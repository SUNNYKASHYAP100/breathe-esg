# Data Model & Architecture

## Overview

The Breathe ESG ingestion system is built on a **4-layer normalized pipeline**:

1. **Raw Ingestion** - Store original data as-is
2. **Normalization** - Transform to standard schema
3. **Review & Validation** - Analyst approval workflow
4. **Locked Records** - Audit-ready snapshot

This design prioritizes **traceability** and **immutability** over convenience.

## Core Models

### Multi-Tenancy

**Company**
- `id` (UUID)
- `name` (String, unique)
- `slug` (String, unique, for URL routing)
- `description` (Text)
- `created_at`, `updated_at`

**CompanyUser**
- `company_id` (FK to Company)
- `user_id` (FK to Django User)
- `role` (admin | analyst | uploader | viewer)
- Unique constraint: (company, user)

*Why:* Enterprise clients often have 10-50 analysts. Role-based access controls which records they can see/approve.

### Ingestion Models

**DataSource**
- `company_id` (FK)
- `source_type` (sap_fuel | sap_procurement | utility_electricity | travel_flights | travel_hotels | travel_ground)
- `name` (String)
- `configuration` (JSONField - stores API keys, column mappings, etc.)

*Why:* Each company may have multiple SAP plants, multiple utility providers, multiple travel platforms. Need to track source separately from imported data.

**IngestionJob**
- `company_id` (FK)
- `data_source_id` (FK)
- `uploaded_by` (FK to User)
- `status` (pending | processing | completed | failed)
- `file_name` (String)
- `file_path` (String)
- `total_rows`, `processed_rows`, `failed_rows` (Int)
- `error_log` (JSONField - array of {row, error})
- `created_at`, `updated_at`

*Why:* Track batch upload progress. Crucial for understanding data quality - if 50% of rows fail, we need to know immediately.

**RawRecord**
- `ingestion_job_id` (FK)
- `company_id` (FK for easy filtering)
- `source_type` (String, denormalized for perf)
- `raw_data` (JSONField - the actual CSV row)
- `row_number` (Int)
- `processing_status` (pending | normalized | failed)
- `error_message` (Text, blank if normalized)

*Why:* Never overwrite original data. If normalization fails or we need to re-run parsing logic, we always have the original. Crucial for audit.

### Normalization Models

**ActivityRecord** - THE CENTRAL MODEL
- `company_id` (FK)
- `raw_record_id` (OneToOne, optional - some records created manually)
- `ingestion_job_id` (FK - which batch)
- `source_system` (sap | utility | travel - string)

**Emission Metrics**
- `activity_type` (fuel_combustion | electricity_purchased | business_travel_flight | business_travel_hotel | business_travel_ground | procurement)
- `scope` (scope_1 | scope_2 | scope_3)
- `quantity` (Decimal(15,4))
- `unit` (L | gal | kWh | kg | km | night | trip)
- `activity_date` (Date)
- `billing_start_date`, `billing_end_date` (Date, optional - for utilities)

**Categorization**
- `category` (String - SAP plant code, meter ID, travel type)
- `subcategory` (String - SAP material type, utility tariff, hotel chain)
- `origin`, `destination`, `distance` (String, String, Decimal - for travel)

**Data Quality**
- `confidence_score` (Decimal(0-1))
  - 0.95+ = High (strong source, complete data)
  - 0.85-0.95 = Medium (some inference needed, e.g., distance estimation)
  - <0.85 = Low (significant inference, e.g., activity_date guessed)
- `is_flagged` (Boolean)
- `flag_reason` (String - why analyst flagged)

**Audit Trail**
- `status` (pending_review | flagged | approved | locked)
- `approved_by` (FK to User, null if not approved)
- `approved_at` (DateTime, null if not approved)
- `notes` (Text)
- `original_data` (JSONField - stores the normalized field mapping from raw)

*Why this dense structure:*
- Original data, normalized metrics, audit trail, approval status all in one record = single source of truth
- No joins needed for analyst dashboard - fast queries on large tables
- confidence_score drives review prioritization (low confidence → must review)
- `locked` status makes audit-ready snapshots immutable

**AuditLog** - APPEND-ONLY LOG
- `activity_record_id` (FK)
- `action` (created | updated | flagged | approved | locked)
- `user_id` (FK to User who made change)
- `changes` (JSONField - {field: [old_value, new_value]})
- `notes` (Text)
- `created_at` (auto_now_add)

*Why:* Every action immutably logged. When auditors ask "who approved this and when", we have the answer. Append-only prevents tampering.

**SuspiciousFlagRule** - AUTO-FLAGGING RULES
- `company_id` (FK)
- `activity_type` (String)
- `field_name` (String - e.g., "quantity")
- `condition` (gt | lt | eq | missing)
- `threshold` (Decimal)
- `enabled` (Boolean)

*Examples:*
- activity_type = fuel_combustion, field = quantity, condition = gt, threshold = 5000L → "unusually high fuel usage"
- activity_type = electricity_purchased, field = quantity, condition = lt, threshold = 10kWh → "suspiciously low"

Allows non-technical PMs to define anomaly rules.

### Review Models

**ReviewQueue** - PRIORITY QUEUE FOR ANALYSTS
- `company_id` (FK)
- `activity_record_id` (OneToOne)
- `priority` (low | medium | high)
  - high = flagged by rules or analyst
  - medium = low confidence_score
  - low = default
- `reason` (String - why in queue)

*Why:* Analysts see most critical work first. If we auto-flag 10k records, they need guidance on what to tackle.

**ReviewSession** - BATCH REVIEW TRACKING
- `company_id` (FK)
- `analyst` (FK to User)
- `status` (open | in_progress | completed)
- `records_to_review`, `records_approved`, `records_rejected`, `records_flagged` (Int counters)
- `notes` (Text)
- `created_at`, `completed_at`

*Why:* Audit trail - "analyst X reviewed 500 records on May 26, approved 450, flagged 50". Useful for compliance reports.

## Data Flow

```
CSV Upload
    ↓
RawRecord (JSON blob in DB)
    ↓ [Normalization Service]
ActivityRecord (normalized fields)
    ↓ [Auto-flag check]
ReviewQueue (if flagged or low confidence)
    ↓ [Analyst reviews]
Approval/Flag decision
    ↓ [If approved]
Status = "locked"
    ↓
Audit-ready export
```

## Unit Normalization

All metrics stored in standard units:
- **Energy**: kWh (converts from J, MWh, etc.)
- **Volume**: L (converts from gal, m³, etc.)
- **Distance**: km (converts from miles)
- **Mass**: kg (converts from lbs, tonnes)

Conversion happens in `apps.normalization.services.normalize_unit()`. Stores original unit for transparency.

## Key Design Decisions

### Why no carbon calculations?
**Answer:** Scope of this MVP is ingestion & review, not emissions accounting. Carbon factor selection is domain-specific (source? region? year?). Separates concerns: data quality from calculation quality.

### Why store original_data on ActivityRecord?
**Answer:** Traceability. If an analyst changes quantity from 1000 to 1200, we need to know what we started with. Append-only AuditLog isn't enough - need the mapped values too.

### Why not use polymorphic models for different record types?
**Answer:** Multi-table inheritance adds query complexity. Single ActivityRecord table with `activity_type` and `scope` enums is simpler to query for analysts ("show me all Scope 1 records this month").

### Why JSONField for raw_data and original_data?
**Answer:** Data from SAP, utilities, and travel platforms varies wildly. JSONField gives flexibility. Could parse into structured fields, but then lose data on mismatches.

### Why denormalize company_id and source_type on RawRecord?
**Answer:** Query performance. Analysts filter by company and source. Avoids JOINs on huge tables.

## Audit Requirements Met

- ✅ **Immutability**: RawRecord and locked ActivityRecord never change
- ✅ **Traceability**: AuditLog captures who did what and when
- ✅ **Source tracking**: ingestion_job_id and source_system on every record
- ✅ **Approval workflow**: status field + approved_by + approved_at
- ✅ **Data quality metrics**: confidence_score and flag_reason
- ✅ **Multi-tenant isolation**: company_id on all models
