# README

# Breathe ESG - Enterprise ESG Data Ingestion & Review Platform

**A working prototype for ingesting, normalizing, and reviewing emission data from multiple sources.**

## What This Is

An MVP Django REST + React application that:

1. **Ingests** fuel/procurement data (SAP), electricity (utility portals), business travel (Navan/Concur)
2. **Normalizes** data into standard emission activity records
3. **Flags** suspicious data via configurable rules
4. **Reviews** records through an analyst dashboard
5. **Locks** approved records for audit compliance

## Why This Approach

- **4-layer pipeline**: Raw → Normalized → Review → Locked (immutable for auditors)
- **CSV sources over APIs**: More realistic for onboarding enterprise clients who export manually
- **Analyst-first UX**: Dashboard for non-technical sustainability teams
- **Audit trail**: Every change logged; approved records locked
- **Multi-tenancy**: Multiple companies, isolated data
- **Scope classification**: Automatically categorizes into Scope 1/2/3

## Tech Stack

**Backend**: Django 6, Django REST Framework, PostgreSQL (SQLite for dev)
**Frontend**: React 18, Axios, CSS3
**Deployment**: Railway (backend), Vercel (frontend)

## Quick Start

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py generate_sample_data
python manage.py createsuperuser
python manage.py runserver

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

Backend: http://localhost:8000
Frontend: http://localhost:3000
Swagger API docs: http://localhost:8000/api/docs/

## Sample Data

Run `python manage.py generate_sample_data` to seed:
- 4 SAP fuel records (1200-2100 L, various dates)
- 3 utility electricity records (4500-4700 kWh, monthly)
- 5 corporate travel records (flights, hotels, ground transport)

## Key Models

**Company** → **IngestionJob** → **RawRecord** → **ActivityRecord**
- RawRecord: original CSV row (never modified)
- ActivityRecord: normalized metrics + approval status
- AuditLog: append-only change history

## API Examples

**View activity records pending review:**
```bash
curl http://localhost:8000/api/review/records/?company_id=1&status=pending_review
```

**Approve a record:**
```bash
curl -X POST http://localhost:8000/api/review/records/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes": "Looks good"}'
```

**Flag suspicious data:**
```bash
curl -X POST http://localhost:8000/api/review/records/1/flag/ \
  -H "Content-Type: application/json" \
  -d '{"reason": "Unusually high fuel consumption"}'
```

**Get statistics:**
```bash
curl http://localhost:8000/api/review/records/statistics/?company_id=1
```

## Documentation

- **MODEL.md** - Data model & schema design
- **DECISIONS.md** - Research & architectural choices
- **SOURCES.md** - Data source formats & normalization logic
- **TRADEOFFS.md** - What I didn't build & why
- **DEPLOYMENT.md** - Production deployment instructions

## Limitations (Intentional)

This MVP deliberately does NOT include:

1. **Live API integration** - Uses CSV exports, can add APIs later
2. **Carbon calculation** - Stores normalized metrics only
3. **Real-time updates** - Batch ingestion (monthly files)
4. **OCR for PDFs** - CSV export is more reliable
5. **ML anomaly detection** - Rule-based flagging works well

See **TRADEOFFS.md** for justification.

## Deployment

**Railway (backend):**
```bash
railway link
railway up
```

**Vercel (frontend):**
- Push to GitHub
- Connect repo to Vercel
- Set `REACT_APP_API_BASE_URL` env var

See **DEPLOYMENT.md** for full instructions.

## Files

```
backend/
  ├── config/              # Django settings
  ├── apps/
  │   ├── tenants/        # Multi-tenancy (Company, CompanyUser)
  │   ├── ingestion/      # Upload & RawRecord storage
  │   ├── normalization/  # Parsing & ActivityRecord creation
  │   └── review/         # Analyst dashboard & approval workflow
  ├── manage.py
  └── requirements.txt

frontend/
  ├── src/
  │   ├── Dashboard.jsx   # Main analyst UI
  │   ├── Dashboard.css
  │   ├── App.js
  │   └── index.js
  ├── package.json
  └── .env

MODEL.md              # Data model documentation
DECISIONS.md          # Why I made certain choices
SOURCES.md            # Data source research & formats
TRADEOFFS.md          # What I didn't build
DEPLOYMENT.md         # How to deploy
```

## Next Steps

1. **Connect Navan API** - Replace CSV upload with live travel data pull
2. **Emission factors** - Add carbon calculation service
3. **JWT auth** - Replace Django auth for production
4. **Data export** - Output approved records to auditor systems
5. **ML anomaly detection** - Upgrade from rule-based flagging

## For Auditors

- All records immutable once locked (`status = 'locked'`)
- AuditLog captures every change with user & timestamp
- Original data preserved (never overwritten)
- Multi-tenancy enforced at DB layer
- Confidence scores indicate data quality
- Source tracking: know where every record came from

---

Built in 4 days. Questions? See documentation files.
