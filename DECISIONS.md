# Decisions Made & Tradeoffs

## Research & Source Selection

### 1. SAP Fuel & Procurement Data

**Research Finding:**
- SAP exports come in multiple formats: iDoc, flat file CSV, OData API, BAPI
- Most common in enterprise: CSV flat-file exports and OData
- Column headers often in German or English mixed
- Plant codes require lookup tables (plant 1001 might be "Berlin Warehouse")

**Decision: CSV Flat-File Export**

*Why CSV?*
- Most realistic for MVP onboarding (sustainability teams manually export SAP reports)
- No complex SAP authentication (OAuth, JWT, SAP Cloud SDK)
- Can be automated later with scheduled SAP queries, but CSV is the MVP path
- Easier to prototype within 4-day timeline

*What I handle:*
- Quantity extraction from various column names (Menge, Quantity, Qty)
- Unit normalization (L, Litre, gal, Gallon)
- Date parsing (multiple formats)
- Plant code categorization
- Material classification into Scope 1 (fuel) vs Scope 3 (procurement)

*What I ignore:*
- Complex SAP cost center hierarchies
- Batch number tracking (not relevant to emissions)
- Material movement history (only final quantity matters)
- Multi-currency conversions (assume single currency per export)

**Real-world format researched:**
```
Menge,Unit,Datum,Material Code,Description,Plant Code,Amount
1200,L,2024-01-15,FUEL-001,Diesel Fuel,PLANT-01,€1800
950,L,2024-01-20,FUEL-002,Petrol,PLANT-01,€950
```

### 2. Utility Electricity Data

**Research Finding:**
- Utilities expose data via: portal CSV exports, PDF bills, proprietary APIs
- Portal exports are most common (80% of time)
- Meter readings don't align with calendar months (billing cycles offset)
- Multiple tariff types (commercial, industrial, time-of-use)

**Decision: CSV Portal Export**

*Why CSV portal export?*
- Most companies don't have utility API access (requires negotiation)
- PDF parsing adds OCR complexity, fragility (different utility formats)
- CSV export is standard across Enel, E.ON, ENTSO, local utilities
- Still realistic for MVP - facilities teams download monthly

*What I handle:*
- Billing period extraction (start_date, end_date, not month assumption)
- Meter ID categorization
- kWh consumption extraction
- Tariff type classification (Standard, Time-of-Use, Commercial)
- Missing data detection (flag if no dates or consumption)

*What I ignore:*
- Multi-meter aggregation (assume one meter per file)
- Peak vs off-peak breakdown (single kWh figure assumed)
- Power factor or reactive power
- Demand charges
- Real-time API integration (no live meter polling)

**Real-world format researched:**
```
Meter ID,Start Date,End Date,kWh,Tariff Type,Cost
METER-001,2024-01-01,2024-01-31,4500,Commercial,€1200
METER-001,2024-02-01,2024-02-29,4700,Commercial,€1310
```

### 3. Corporate Travel Data

**Research Finding:**
- Travel platforms (Concur, Navan, TravelPerk): different APIs but similar data structure
- Flights: usually have distance, sometimes only airport codes
- Hotels: billed by night, distance = 0 (hotel location = work location or N/A)
- Ground transport: varies (taxi, rental car, public transit)
- Distance not always provided; sometimes only airport codes

**Decision: Navan-style API Export to CSV**

*Why CSV export from travel API?*
- Navan, Concur, TravelPerk all have CSV export (data prep for analysis teams)
- Could integrate APIs, but requires auth per platform (MVP complexity)
- CSV export is realistic path: "export last month's travel"

*What I handle:*
- Trip type classification (Flight, Hotel, Ground)
- Origin/Destination extraction
- Distance lookup from airport codes (DEL → BOM = 1300 km)
- Date parsing
- Cost tracking (for audit trail, not emissions)
- Confidence scoring (high if distance given, medium if estimated)

*What I ignore:*
- Passenger count (assume 1, not group travel)
- Airline tier/class (doesn't affect CO2 much)
- Hotel sustainability rating (out of scope for MVP)
- Vehicle type for ground transport (all treated equally)
- Meal delivery services (out of scope)
- Carbon offset purchases in the platform (separate system)

**Real-world format researched (simplified Navan export):**
```
Type,Origin,Destination,Distance,Date,Cost,Traveler
Flight,DEL,BOM,1300,2024-01-10,₹25000,John Doe
Hotel,BOM,BOM,,2024-01-10,₹6000,John Doe
Ground,BOM,BOM,50,2024-01-10,₹1500,John Doe
```

## Architectural Decisions

### 4. Why 4-Layer Pipeline?

**Decision: Raw → Normalized → Review → Locked**

*Alternatives considered:*
- **Direct import**: CSV → Emission factors → Emissions. **Rejected:** No audit trail, no review, no error recovery.
- **2-layer (raw + final)**: CSV → Emissions. **Rejected:** Can't reprocess if logic changes.
- **3-layer (raw + normalized + emissions)**: CSV → normalized + Emissions calculated. **Rejected:** Separates concerns; should calculate emissions in downstream system (not MVP scope).

*Why 4?* Each layer serves auditors:
1. **Raw** = "What did the system ingest?" (proves data receipt)
2. **Normalized** = "What did we understand?" (shows interpretation)
3. **Review** = "Did anyone check this?" (human validation)
4. **Locked** = "What did we report?" (immutable snapshot for auditors)

### 5. Why Confidence Score Instead of Just "Valid/Invalid"?

**Decision: confidence_score (0.0-1.0) + is_flagged + flag_reason**

*Alternatives:*
- Binary valid/invalid flag. **Rejected:** Loses nuance. 1000 km distance estimated vs known differs in quality.
- Just comment field. **Rejected:** Can't sort/prioritize by data quality.

*Scoring logic:*
- 0.98+ = Data from authoritative source (utility meter, flight booking)
- 0.95 = Normalized without loss (quantity + unit clear)
- 0.85-0.95 = Inference needed (distance estimated from airport codes)
- <0.85 = Significant assumption (activity_date guessed, unit unknown)

Allows analysts to sort by quality. Auditors can see "90% of records are high confidence."

### 6. Multi-Tenancy Design

**Decision: company_id on every record, no database per tenant**

*Alternatives:*
- Separate DB per tenant (Row-Level Security challenge). **Rejected:** Scaling nightmare, backup management.
- Shared DB, row-level security via middleware. **Rejected:** Complexity for MVP; simple company_id filtering works.

*Tradeoff:* All companies' data in one DB. Mitigated by:
- Unique company slugs for URL routing
- Middleware to inject company_id into all queries
- No cross-company data visible in APIs

### 7. No Emission Factors in MVP

**Decision: Store normalized metrics only; don't calculate CO2 yet**

*Why?*
- Emission factors are domain-specific (grid mix varies by country/year)
- Factors change frequently (utilities update quarterly)
- Calculation belongs in separate service (not MVP scope)
- MVP focus: data quality & ingestion, not carbon accounting accuracy

*Example:*
- System stores: "4500 kWh, India grid"
- Downstream system calculates: 4500 kWh × 0.62 kg CO2/kWh = 2790 kg CO2
- If factor updates to 0.58 in next quarter, recalculate without re-ingesting

## What I'd Ask the PM

1. **Scope 3 precision:** Travel distances — do you want to integrate Google Maps API for exact routing, or is airport-code estimation OK for MVP?

2. **Frequency:** Is this a monthly batch process or continuous ingestion? If daily, might need async task queue (Celery).

3. **Audit targets:** Who are the auditors? Are they technical (want API access) or non-technical (need export to Excel)?

4. **Emission factors:** When ready to calculate CO2, should factors live in this system or a separate carbon accounting service?

5. **Data retention:** How long to keep raw records? Audit trail on AuditLog — do auditors need granular edit history or just final approval?

6. **Scope 3 categories:** Are you capturing all procurement data (not just fuel orders)? That's complex - requires supplier mapping.

7. **Multiple uploads per source:** Can the same company upload SAP twice in a month (e.g., mid-month adjustment)? How to handle overlap?

8. **API integrations roadmap:** After MVP CSV uploads, planning to connect to live SAP/Navan APIs? That determines DataSource configuration design.
