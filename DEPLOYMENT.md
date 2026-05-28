# Breathe ESG - ESG Data Ingestion and Review Platform

## Setup & Deployment

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py generate_sample_data  # Optional: seed with sample data
python manage.py createsuperuser  # Create admin user
python manage.py runserver
```

API available at: http://localhost:8000
Swagger docs: http://localhost:8000/api/docs/

**Frontend:**
```bash
cd frontend
npm install
npm start
```

Dashboard available at: http://localhost:3000

### Deployment to Railway

**Backend:**
1. Create `railway.json` (already provided)
2. Set environment variables:
   ```
   SECRET_KEY=<generate-strong-key>
   DATABASE_URL=postgresql://<user>:<pass>@<host>/<db>
   ALLOWED_HOSTS=yourdomain.railway.app
   DEBUG=False
   ```
3. Deploy:
   ```bash
   railway link
   railway up
   ```

**Frontend (Vercel recommended):**
1. Push to GitHub
2. Link repo to Vercel
3. Set env var: `REACT_APP_API_ttps://your-backend.railway.app/api`
4. Deploy

### Database

**Local development:** SQLite (db.sqlite3)
**Production:** PostgreSQL (Railway provides)

### API Endpoints

- **Companies**: `GET/POST /api/tenants/companies/`
- **Data Sources**: `GET/POST /api/ingestion/sources/`
- **Upload**: `POST /api/ingestion/jobs/upload/`
- **Activity Records**: `GET /api/review/records/`
- **Approve Record**: `POST /api/review/records/{id}/approve/`
- **Flag Record**: `POST /api/review/records/{id}/flag/`
- **Statistics**: `GET /api/review/records/statistics/?company_id=1`

All endpoints require `company_id` parameter for multi-tenancy.

### Sample Data

Generate sample data with:
```bash
python manage.py generate_sample_data
```

Creates:
- 1 test company (Acme Corp)
- 1 test user (analyst)
- 3 data sources (SAP Fuel, Utility, Travel)
- 12 sample records across all sources

### Authentication

MVP uses basic Django user authentication. Add JWT/OAuth in Phase 2.

### Troubleshooting

**CORS errors:**
- Ensure frontend `REACT_APP_API_URL`tches backend URL
- Check CORS_ALLOWED_ORIGINS in settings.py

**Database errors:**
- Run `python manage.py migrate --run-syncdb`
- For PostgreSQL, ensure psycopg2 is installed

**Port conflicts:**
- Backend: `python manage.py runserver 8001` (change port)
- Frontend: `PORT=3001 npm start`

### Next Steps

1. Connect live SAP/Navan/Utility APIs (DataSource configuration)
2. Add emission factor calculations
3. Implement JWT authentication
4. Build data export to audit systems
5. Add ML-based anomaly detection
