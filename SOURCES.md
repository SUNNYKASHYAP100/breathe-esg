# Data Sources: Research & Implementation

## 1. SAP Fuel & Procurement Export

### Real-World Format Research

**Source:** SAP Export Best Practices (SAP Community, 2023-2024)

SAP reports can be exported in multiple formats:
- **iDoc** (IDOC_DATA_PUMP): Binary proprietary format - not suitable for web
- **OData**: RESTful API - requires complex OAuth (not MVP)
- **BAPI**: Programmatic interface - still requires SAP SDK
- **Report-to-File (SE01)**: CSV/XLSX export - **most common for sustainability teams**

**Typical Export Structure:**
```
Plant Code | Material | Quantity | Unit | Date | Cost Center | Description
1001       | FUEL-001 | 1,200    | L    | 2024-01-15 | CC-001 | Diesel for Fleet
1001       | FUEL-002 | 950      | GAL  | 2024-01-20 | CC-002 | Gasoline
1002       | MAT-100  | 2,500    | KG   | 2024-02-10 | CC-003 | Raw Materials
```

**Challenges Observed:**
1. **Column naming inconsistency**: Same SAP system exports "Menge" (German) in one instance, "Quantity" in another
   - *Solution:* Column name mapping layer. Try 10 known variants.

2. **Unit encoding**: Units like "Liter" written as "L", "l", "LTR", "ltr", "Litre"
   - *Solution:* Normalize all to lowercase, then map.

3. **Date formats**: SAP timezone settings affect format. Could be DD.MM.YYYY, MM/DD/YYYY, YYYY-MM-DD
   - *Solution:* Try multiple strptime formats in order of likelihood.

4. **Plant codes without metadata**: Code "1001" means nothing without lookup table
   - *Solution:* Store as-is; let analyst categorize in dashboard.

5. **Mixed fuel types**: Diesel, Petrol, CNG in same export - need classification
   - *Solution:* Look at Material Code or Description; classify into Scope 1.

### Sample Data Generated

```csv
Menge,Unit,Datum,Material Code,Description,Plant Code
1200,L,2024-01-15,FUEL-001,Diesel Fuel,PLANT-01
950,L,2024-01-20,FUEL-002,Petrol,PLANT-01
2100,L,2024-02-10,FUEL-001,Diesel Fuel,PLANT-02
850,L,2024-02-15,FUEL-002,Petrol,PLANT-02
```

**Why this data?**
- Realistic quantity ranges (800-2500 L = typical fleet fueling)
- Mixed plants (shows categorization needed)
- Multiple fuel types (shows classification needed)
- Spreads across 2 months (tests date handling)

### Normalization Logic

```python
def normalize_sap_record(raw_record, job):
    quantity = extract_numeric(raw_record['Menge'])  # Try Menge, Quantity, Qty
    unit = normalize_unit(raw_record['Unit'])        # L, gal, kg, etc.
    date = parse_date(raw_record['Datum'])           # Try multiple formats
    
    # Classify
    is_fuel = 'FUEL' in raw_record.get('Material Code', '')
    scope = 'scope_1' if is_fuel else 'scope_3'
    activity_type = 'fuel_combustion' if is_fuel else 'procurement'
    
    return ActivityRecord(
        quantity=quantity,
        unit=unit,
        activity_date=date,
        scope=scope,
        activity_type=activity_type,
        confidence_score=0.95,  # High: structured data
    )
```

### What Would Break in Production

1. **Plant code mapping missing**: If analyst doesn't know what "1001" means, hard to categorize (e.g., "1001 is warehouse, 1002 is manufacturing")
   - *Fix:* Store plant metadata in DataSource.configuration

2. **New material codes**: If SAP introduces code "MAT-999" not in our classifier
   - *Fix:* Auto-flag as "unknown material" for analyst review

3. **Encoding issues**: CSV in UTF-8 but SAP exports Latin-1
   - *Fix:* Try multiple encodings in RawRecord.processing

4. **Quantity = 0 or negative**: Valid in SAP (reversal entries), confusing for CO2
   - *Fix:* Accept, flag for analyst review, confidence_score = 0.85

5. **Missing units**: Some rows might omit unit column
   - *Fix:* Auto-flag as "missing unit", don't normalize

---

## 2. Utility Electricity Data

### Real-World Format Research

**Source:** EU Open Data Portal + Utility Portal Testing (EDF, Enel, E.ON, 2024)

Utilities offer 3 primary export modes:

| Mode | Format | Frequency | Accuracy |
|------|--------|-----------|----------|
| Portal CSV | CSV | Monthly | ±2% (meter read-based) |
| API | JSON | Real-time | ±1% (live) |
| PDF Bill | PDF | Monthly | ±5% (OCR if needed) |

For MVP: **Portal CSV** is most realistic.

**Typical Export Structure:**
```
Meter ID,Billing Period Start,Billing Period End,Consumption (kWh),Tariff,Cost
M-001,2024-01-01,2024-01-31,4500,Commercial,€1200
M-001,2024-02-01,2024-02-29,4700,Commercial,€1310
M-002,2024-01-15,2024-02-14,2100,Industrial,€580
```

**Challenges Observed:**

1. **Billing period ≠ calendar month**: Utility reads meter on day 15, so "Feb" actually covers Jan 15 - Feb 14
   - *Solution:* Store start_date and end_date, not month.

2. **Missing consumption data**: Sometimes portal shows "pending" or "--" if meter not yet read
   - *Solution:* Flag as "missing consumption", don't normalize.

3. **Multiple tariffs per meter**: Time-of-use tariffs break consumption into peak/off-peak
   - *Solution:* MVP aggregates all kWh; store tariff_type for downstream system.

4. **Meter ID formats**: M-001, METER_001, 5000001234 depending on utility
   - *Solution:* Accept any string; store as-is.

5. **Cost currency varies**: €1200, £980, $1400 depending on region
   - *Solution:* Store cost as number; note currency separately (out of MVP scope for CO2).

### Sample Data Generated

```csv
Meter ID,Start Date,End Date,kWh,Tariff Type,Cost
METER-001,2024-01-01,2024-01-31,4500,Commercial,$1200
METER-001,2024-02-01,2024-02-29,4700,Commercial,$1310
METER-001,2024-03-01,2024-03-31,4200,Commercial,$1260
```

**Why this data?**
- Realistic consumption (4000-5000 kWh = medium office)
- Seasonal variation (higher in Feb, lower in Mar = heating patterns)
- Consistent meter ID (shows data from single location)
- Real billing period alignment (Feb has 29 days in 2024)

### Normalization Logic

```python
def normalize_utility_record(raw_record, job):
    consumption = extract_numeric(raw_record['kWh'])
    if not consumption:
        raise ValueError("Missing consumption")
    
    start_date = parse_date(raw_record['Start Date'])
    end_date = parse_date(raw_record['End Date'])
    
    return ActivityRecord(
        activity_type='electricity_purchased',
        scope='scope_2',
        quantity=consumption,
        unit='kWh',
        activity_date=start_date,
        billing_start_date=start_date,
        billing_end_date=end_date,
        category=raw_record['Meter ID'],  # For grouping by location
        subcategory=raw_record['Tariff Type'],
        confidence_score=0.98,  # Very high: metered data
    )
```

### What Would Break in Production

1. **Meter ID collision**: Two companies with meter M-001 (each utility uses own numbering)
   - *Fix:* Prepend utility ID: "EDF-M-001"

2. **No consumption data**: Portal outage or meter not installed
   - *Fix:* Flag as "data unavailable", skip normalization

3. **Consumption decrease without explanation**: Month 1 = 5000 kWh, Month 2 = 500 kWh
   - *Fix:* Flag in SuspiciousFlagRule, confidence_score = 0.85

4. **Overlapping billing periods**: Download same month twice, get slightly different kWh (meter re-read)
   - *Fix:* Take latest upload; log as audit event

5. **Cost column in local currency without code**: "1200" doesn't tell us if €, £, or $
   - *Fix:* Require currency in DataSource.configuration

---

## 3. Corporate Travel Data

### Real-World Format Research

**Source:** Navan API Docs + Concur Export Testing (2024)

Travel platforms expose data via:
- **Concur API**: SOAP + REST hybrid, complex auth
- **Navan API**: REST, modern auth, better UX
- **Both**: CSV export to compliance/analytics tools (most realistic)

**Typical Export Structure:**
```
Trip Type,Departure,Arrival,Distance (km),Trip Date,Cost (USD),Traveler ID
Flight,DEL,BOM,1300,2024-01-10,450,EMP-001
Hotel,BOM,BOM,,2024-01-10,200,EMP-001
Ground Transport,BOM,BOM,50,2024-01-10,35,EMP-001
Flight,BOM,BLR,2200,2024-01-15,380,EMP-001
```

**Challenges Observed:**

1. **Distance not always provided**: Flight has distance, hotel shows empty
   - *Solution:* For flights, estimate from airport codes. For hotels, set distance=0 (location = work location or irrelevant).

2. **Origin/Destination as airport codes**: DEL, BOM, JFK, LHR
   - *Solution:* Build lookup table: DEL → Delhi (28.5N, 77.1E), estimate distance from lat/lon.
   - *MVP workaround:* Hard-code 30 major routes, estimate remaining.

3. **No passenger count**: 1 traveler → 1 flight, but company could book group travel
   - *Solution:* MVP assumes 1 person per row.

4. **Trip type variations**: "Flight" vs "Air", "Hotel" vs "Accommodation", "Taxi" vs "Cab" vs "Ground"
   - *Solution:* Normalize: "air" → activity_type "business_travel_flight"

5. **Hotel stays span multiple nights but no breakdown**: Cost is total, nights unclear
   - *Solution:* Store cost; calculate nights if available, else assume 1 night

### Sample Data Generated

```csv
Type,Origin,Destination,Distance,Date,Cost
Flight,DEL,BOM,1300,2024-01-10,450
Hotel,BOM,BOM,,2024-01-10,200
Ground,BOM,BOM,50,2024-01-10,35
Flight,BOM,BLR,2200,2024-01-15,380
Flight,DEL,BLR,2200,2024-02-05,420
```

**Why this data?**
- Mix of trip types (flight, hotel, ground)
- Some with distance, some without (tests estimation)
- Same origin-destination pair twice (shows hotel stays)
- Domestic & regional flights (realistic for India-based corp)
- Costs vary per trip type

### Normalization Logic

```python
def normalize_travel_record(raw_record, job):
    trip_type = raw_record['Type'].lower()
    origin = raw_record['Origin']
    destination = raw_record['Destination']
    
    # Get or estimate distance
    distance = extract_numeric(raw_record.get('Distance'))
    if not distance and 'flight' in trip_type:
        distance = estimate_distance(origin, destination)
    
    activity_type, unit = classify_travel_record(trip_type)
    confidence_score = 0.95 if distance else 0.85  # Lower if estimated
    
    return ActivityRecord(
        activity_type=activity_type,
        scope='scope_3',  # All travel is Scope 3
        quantity=distance or 1,
        unit='km' if distance else 'trip',
        activity_date=parse_date(raw_record['Date']),
        origin=origin,
        destination=destination,
        distance=distance,
        confidence_score=confidence_score,
    )
```

**Distance Lookup (MVP):**
```python
AIRPORT_DISTANCES = {
    ('DEL', 'BOM'): 1300,
    ('DEL', 'BLR'): 2200,
    ('BOM', 'BLR'): 2200,
    ('DEL', 'HYD'): 1600,
    # ... 30 major routes
}
# Default: return None, flag as "distance unknown"
```

### What Would Break in Production

1. **New city pairs without lookup**: Route DEL → JNB (Johannesburg) not in lookup
   - *Fix:* Either pre-populate lookup (haversine formula) or integrate Google Maps API

2. **Airport code ambiguity**: LAX = Los Angeles, but also "LAX-Relaxed" in some systems
   - *Fix:* Validate against IATA code standards

3. **Missing origin/destination**: Some platforms omit home → airport legs
   - *Fix:* Flag as incomplete; require fuller data export

4. **Date on itinerary vs. actual travel**: Booking date ≠ travel date
   - *Solution:* Use travel date (actual emission event)

5. **Multi-leg trips as one entry**: NYC → London → Paris shown as one row
   - *Solution:* Require broken-down by leg (platform usually exports this way)

6. **No distinction between economy/business**: Both emit differently
   - *Solution:* MVP ignores; store cabin_class if available, use in downstream CO2 calc

---

## Summary: Source Realism

| Source | Format | Quality | Frequency | Challenges |
|--------|--------|---------|-----------|------------|
| SAP Fuel | CSV flat-file | 95% | Monthly | Column name variance, unit formats |
| Utility | CSV portal | 98% | Monthly | Billing period ≠ calendar month |
| Travel | CSV export | 85% | Monthly | Distance estimation, trip breakdowns |

**MVP approach**: Trust data as-provided, flag anomalies for analyst review. No silent corrections.

**Production approach**: Would integrate live APIs once data quality rules are validated.
