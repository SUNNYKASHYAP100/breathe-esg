# Tradeoffs: What I Deliberately Did Not Build

## 1. No Direct SAP/Utility/Travel API Integration

**What would be needed:**
- SAP OData client (OAuth + BAPI knowledge)
- Utility API SDK (differs per provider: Enel has different auth than E.ON)
- Navan/Concur API clients (polling frequency, pagination, error handling)
- Continuous reconciliation logic (what if API is down for a day?)

**Why I skipped it:**
- 4-day timeline constraint
- CSV export is realistic MVP path; APIs are "Phase 2"
- Companies typically start with manual exports anyway
- Adds 2+ days of implementation per source
- Integration testing requires real accounts (SAP sandbox is complex)

**Trade:** Analysts do CSV exports manually once/month vs. automatic daily pulls
**Value retained:** Same normalization logic; trivial to add API sources later (just modify DataSource config)

**Debt:** DataSource.configuration field is designed for this - store API credentials, polling schedule, field mappings. Easy to implement later.

---

## 2. No OCR for PDF Utility Bills

**What would be needed:**
- Tesseract or Amazon Textract integration
- PDF structure detection (find table of meter readings)
- Parsing logic per utility (different PDF layouts)
- Validation of OCR accuracy (OCR errors propagate to emissions)

**Why I skipped it:**
- OCR is fragile (5-10% error rate on scanned documents)
- Utilities offer CSV export (better source)
- One PDF per utility × 50 utilities × 12 months = 600 files to test
- If OCR fails, analyst still needs manual fallback

**Trade:** Requires facilities team to use portal CSV export vs. automated PDF parsing
**Value retained:** Dashboard flags missing data, so if CSV is skipped, visible immediately

**Debt:** Could add OCR as data_source type later without changing core models

---

## 3. No Real-Time Ingestion / Event Streaming

**What would be needed:**
- Kafka or Redis Pub/Sub
- Celery task queue for async normalization
- WebSocket updates on dashboard ("3 new records flagged")
- Batch status polling vs. push notifications

**Why I skipped it:**
- MVP is batch processing (files uploaded once/month)
- Not needed until 100k+ records/day volumes
- Adds complexity: distributed task management, failure retries, dead-letter queues
- Synchronous request-response is fine for 4-day sprint

**Trade:** Upload feels slower (wait for response) vs. instant async notification
**Value retained:** IngestionJob status model supports async later; just wire Celery when needed

**Debt:** Job status enum (pending/processing/completed/failed) is designed for this

---

## 4. No Advanced Anomaly Detection ML

**What would be needed:**
- ML model training (isolation forest or autoencoders for outlier detection)
- Feature engineering (historical consumption patterns, seasonal adjustments)
- Threshold tuning per company
- Model retraining as data grows

**Why I skipped it:**
- Rule-based flagging is transparent and debuggable (PM can define rules)
- ML adds black-box unpredictability (why flagged? "the model said so")
- MVP needs manual analyst approval anyway (no full automation)
- 4-day timeline precludes training set collection

**Trade:** Simple rule-based flags (quantity > 5000L) vs. intelligent pattern detection
**Value retained:** SuspiciousFlagRule model allows rule definition; can plug in ML scoring later

**Example rule that works well:**
- Fuel usage 2x historical average → Flag
- Electricity usage drops 50% without explanation → Flag
- Flight distance > 20k km (likely data error) → Flag

---

## Summary

| Feature | Skipped | Why | Phase 2 Priority |
|---------|---------|-----|------------------|
| Live SAP/Navan APIs | Yes | CSV export MVP | High - automates upload |
| PDF bill OCR | Yes | CSV export available | Low - adds fragility |
| Real-time streaming | Yes | Batch processing sufficient | Medium - needed >100k records |
| ML anomaly detection | Yes | Rules-based is transparent | Low - rules work well for MVP |
| Carbon calculation | Yes | Upstream system job | High - business critical |
| Multi-company data export | Yes | Focus on ingestion | Medium - needed for dashboards |
| Role-based UI (hide sensitive data) | Yes | All analysts see all records | High - compliance |
| Multi-language support | Yes | English only MVP | Low - nice-to-have |

**Net result:** Sharp, focused MVP with honest tradeoffs. Each skipped feature adds 1-2 days; cutting them enables 4-day delivery of core value (data quality & review).
