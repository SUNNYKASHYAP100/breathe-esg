# Deployment Architecture

## 📦 Production Deployment Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET (HTTPS)                         │
└─────────────────────────────────────────────────────────────────┘
                  │                                  │
                  │                                  │
        ┌─────────▼────────────┐          ┌─────────▼────────────┐
        │  REACT FRONTEND      │          │   DJANGO BACKEND     │
        │  https://front..     │          │   https://api...     │
        │  onrender.com        │          │   onrender.com       │
        │                      │          │                      │
        │ ✓ Node.js            │          │ ✓ Python 3           │
        │ ✓ npm run build      │──────────│ ✓ Gunicorn WSGI      │
        │ ✓ Serve static       │  CORS    │ ✓ DRF API            │
        │                      │  config  │ ✓ Admin Panel        │
        └──────────────────────┘          └──────────┬───────────┘
                                                      │
                                    ┌─────────────────▼──────────────┐
                                    │   PostgreSQL Database           │
                                    │                                 │
                                    │ ✓ 10 tables                     │
                                    │ ✓ Multi-tenant (by company_id)  │
                                    │ ✓ Relationships intact          │
                                    │ ✓ Audit trail                   │
                                    │ ✓ Full backups                  │
                                    └─────────────────────────────────┘
```

---

## 🌐 Traffic Flow

### 1. User visits frontend
```
User Browser → Render CDN → React App (index.html, CSS, JS)
               ↓
        Frontend loads
        Shows upload form & dashboard
```

### 2. User uploads CSV
```
React Component → POST /api/ingestion/jobs/upload/
                 ↓
           (CORS check)
                 ↓
          Django Backend
                 ↓
          Parse CSV, normalize data
                 ↓
          Write to PostgreSQL
                 ↓
          Return success JSON
                 ↓
        Update React dashboard
```

### 3. User approves record
```
React Component → POST /api/review/records/{id}/approve/
                 ↓
           (CORS check)
                 ↓
          Django Backend
                 ↓
          Update status in DB
          Create audit entry
                 ↓
          Return updated record
                 ↓
        Dashboard refreshes
```

---

## 🔐 Security Architecture

```
┌──────────────────────────────────────┐
│      HTTPS/TLS Encryption            │
│  (Automatic via Render)              │
└────────────┬─────────────────────────┘
             │
      ┌──────▼──────┐
      │  Frontend    │
      │              │
      │ - XSS protect│
      │ - No secrets │
      │ - env vars   │
      └──────┬───────┘
             │ CORS check
      ┌──────▼──────┐
      │  Backend     │
      │              │
      │ - CSRF token │
      │ - ORM (SQLi) │
      │ - Auth check │
      └──────┬───────┘
             │
      ┌──────▼──────┐
      │  PostgreSQL  │
      │              │
      │ - SSL conn   │
      │ - Strong pwd │
      │ - Firewall   │
      └──────────────┘
```

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAW CSV FILE                              │
│                                                              │
│  SAP:      Fuel_L, Vehicle, Date                            │
│  Utility:  kWh, Building, Period                            │
│  Travel:   Distance, Airport_Codes, Employee               │
└────────────────────┬────────────────────────────────────────┘
                     │ Upload via form
     ┌───────────────▼─────────────────┐
     │  INGESTION LAYER                │
     │  ✓ Validate CSV format          │
     │  ✓ Store as RawRecord (raw)     │
     │  ✓ Create IngestionJob (track)  │
     └────────────────┬────────────────┘
                      │
     ┌────────────────▼──────────────┐
     │  NORMALIZATION LAYER          │
     │  ✓ Parse SAP → ActivityRecord │
     │  ✓ Parse Utility → Record     │
     │  ✓ Parse Travel → Record      │
     │  ✓ Unit conversion            │
     │  ✓ Scope categorization       │
     └────────────────┬──────────────┘
                      │
     ┌────────────────▼──────────────┐
     │  REVIEW LAYER                 │
     │  ✓ Records in "pending"       │
     │  ✓ Analyst reviews            │
     │  ✓ Approve/Flag/Lock action   │
     │  ✓ Audit trail created        │
     └────────────────┬──────────────┘
                      │
     ┌────────────────▼──────────────┐
     │  APPROVAL STATE               │
     │  ✓ Status: approved/locked    │
     │  ✓ Immutable (cannot change)  │
     │  ✓ Ready for reporting        │
     └───────────────────────────────┘
```

---

## 🗄️ Database Architecture

```
TENANTS App
├── Company
│   ├── id (PK)
│   ├── name
│   └── industry
└── CompanyUser
    ├── id (PK)
    ├── company_id (FK)
    ├── user_id (FK)
    └── role

INGESTION App
├── DataSource
│   ├── id (PK)
│   ├── company_id (FK)
│   ├── source_type
│   └── name
├── IngestionJob
│   ├── id (PK)
│   ├── data_source_id (FK)
│   ├── status
│   └── created_at
└── RawRecord
    ├── id (PK)
    ├── ingestion_job_id (FK)
    ├── raw_data (JSON)
    └── created_at

NORMALIZATION App
├── ActivityRecord
│   ├── id (PK)
│   ├── company_id (FK)
│   ├── record_type
│   ├── quantity
│   ├── unit
│   ├── scope
│   └── created_at
└── AuditLog
    ├── id (PK)
    ├── activity_id (FK)
    ├── action
    ├── old_value
    ├── new_value
    └── timestamp

REVIEW App
├── ReviewSession
│   ├── id (PK)
│   ├── user_id (FK)
│   ├── company_id (FK)
│   └── created_at
├── ReviewQueue
│   ├── id (PK)
│   ├── review_session_id (FK)
│   ├── activity_record_id (FK)
│   └── position
└── SuspiciousFlagRule
    ├── id (PK)
    ├── company_id (FK)
    ├── rule_name
    └── threshold
```

---

## 🔄 API Architecture

```
BASE URL: https://breathe-esg-backend.onrender.com/api

ENDPOINTS:

Ingestion
├── POST   /ingestion/jobs/upload/
│          Accept: multipart/form-data
│          Return: {"job_id": 123, "status": "success"}
└── GET    /ingestion/jobs/

Review
├── GET    /review/records/
│          Query params: company_id, status, page
│          Return: [{"id": 1, "status": "pending", ...}]
├── GET    /review/records/statistics/
│          Return: {"total": 16, "pending": 10, ...}
├── POST   /review/records/{id}/approve/
│          Return: {"status": "approved"}
├── POST   /review/records/{id}/flag/
│          Return: {"status": "flagged"}
└── POST   /review/records/{id}/lock/
           Return: {"status": "locked"}

Tenants
└── GET    /tenants/companies/
           Return: [{"id": 1, "name": "TechCorp"}]

Schema
└── GET    /schema/
           OpenAPI specification
```

---

## 🚀 Deployment Services

### Frontend (React)
```
Platform: Render.com
Runtime: Node.js
Region: US East (or your choice)
Build: npm install && npm run build
Start: npm run start
Scale: Auto (free tier pauses after 15 min inactivity)
```

### Backend (Django)
```
Platform: Render.com
Runtime: Python 3
Region: US East (same as frontend)
Build: pip install -r requirements.txt && python manage.py migrate
Start: gunicorn config.wsgi:application
Scale: Auto (free tier pauses after 15 min inactivity)
Workers: Auto-detected
```

### Database (PostgreSQL)
```
Platform: Render.com
Engine: PostgreSQL 12+
Size: 1 GB RAM (free tier)
Backup: Daily automated backups
Retention: 7 days
Restore: Point-in-time recovery available
```

---

## 📈 Scaling Path

### Phase 1: MVP (Current)
- Single backend instance
- Single frontend instance
- Shared PostgreSQL
- <100 users

### Phase 2: Growth (Optional)
- 2-3 backend instances (behind load balancer)
- CDN for frontend assets
- Database read replicas
- <1000 users

### Phase 3: Enterprise
- Auto-scaling groups
- Multi-region deployment
- Read/write database split
- Caching layer (Redis)
- 10,000+ users

---

## 🔍 Monitoring & Observability

```
┌─────────────────────────────────────────┐
│         Render Dashboard                 │
│  - Service status (green/red)            │
│  - CPU usage                             │
│  - Memory usage                          │
│  - Network I/O                           │
│  - Deployment history                    │
│  - Logs (stdout/stderr)                  │
│  - Error tracking                        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│       Application Monitoring              │
│  - API response times                    │
│  - Error rates                           │
│  - Database query performance            │
│  - User actions logging                  │
│  - Audit trail                           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        Browser Monitoring                 │
│  - Console errors                        │
│  - Network requests                      │
│  - User interactions                     │
│  - Performance metrics                   │
└─────────────────────────────────────────┘
```

---

## 🔑 Environment Variables

### Backend (.env)
```
DEBUG=False
ALLOWED_HOSTS=breathe-esg-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://breathe-esg-frontend.onrender.com
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-random-secret-key
```

### Frontend (.env or build-time)
```
REACT_APP_API_URL=https://breathe-esg-backend.onrender.com/api
```

---

## ✅ Pre-Launch Checklist

- [ ] Database created and connected
- [ ] Backend deployed and running (green status)
- [ ] Frontend deployed and running (green status)
- [ ] Migrations applied to production database
- [ ] Superuser created
- [ ] API endpoints responding (200 status)
- [ ] Frontend loads and connects to backend
- [ ] Upload form works
- [ ] Dashboard displays records
- [ ] CORS configured correctly
- [ ] No console errors in browser
- [ ] Logs reviewed, no errors

---

## 🎯 Success Metrics

After deployment:
- ✅ Frontend loads in <3 seconds
- ✅ API responds in <500ms
- ✅ CSV upload completes in <5 seconds
- ✅ Dashboard updates in real-time
- ✅ Zero CORS errors
- ✅ 99% uptime
- ✅ All features working

---

## 📞 Support & Resources

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **React Build**: https://create-react-app.dev/docs/deployment/
- **PostgreSQL**: https://www.postgresql.org/docs/

---

**Last Updated**: May 27, 2026  
**Architecture**: Render.com  
**Status**: Ready for Production ✅
