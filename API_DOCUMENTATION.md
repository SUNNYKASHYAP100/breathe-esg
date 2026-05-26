# Breathe ESG API Documentation

## Base URL
```
Local: http://localhost:8000/api
Production: https://your-backend.railway.app/api
```

---

## Authentication
Currently unauthenticated. For production, implement JWT via DRF:
```python
# Add to settings.py REST_FRAMEWORK
'DEFAULT_AUTHENTICATION_CLASSES': [
    'rest_framework_simplejwt.authentication.JWTAuthentication',
],
```

---

## 📤 Ingestion Endpoints

### Upload CSV File
**Endpoint**: `POST /api/ingestion/jobs/upload/`

**Parameters**:
```json
{
  "company_id": 1,
  "source_type": "SAP_CSV",  // or UTILITY_CSV, TRAVEL_API
  "file": <binary CSV file>
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/ingestion/jobs/upload/ \
  -F "company_id=1" \
  -F "source_type=SAP_CSV" \
  -F "file=@test_sap_data.csv"
```

**Response** (201 Created):
```json
{
  "id": 4,
  "company": 1,
  "data_source": 1,
  "file_name": "test_sap_data.csv",
  "total_rows": 4,
  "status": "completed",
  "created_at": "2026-05-26T16:22:58Z",
  "uploaded_by": null,
  "error_log": []
}
```

**Status Values**:
- `pending`: Waiting to process
- `processing`: Currently parsing CSV
- `completed`: Successfully processed
- `failed`: Error during processing

**Error Response** (400):
```json
{
  "error": "Missing required fields: company_id, source_type, file"
}
```

---

## 👀 Review Endpoints

### List Activity Records
**Endpoint**: `GET /api/review/records/`

**Query Parameters**:
```
?company_id=1              // Required
&status=pending_review     // Optional: pending_review, flagged, approved, locked
&page=1                    // Default: 1
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/review/records/?company_id=1&status=pending_review"
```

**Response** (200 OK):
```json
{
  "count": 16,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "company": 1,
      "source_system": "sap",
      "activity_type": "fuel_combustion",
      "scope": "scope_1",
      "quantity": 500.0,
      "unit": "kWh",
      "activity_date": "2024-02-10",
      "status": "pending_review",
      "confidence_score": 0.95,
      "is_flagged": false,
      "flag_reason": null,
      "notes": "",
      "locked_at": null,
      "created_at": "2026-05-26T10:49:00Z",
      "updated_at": "2026-05-26T10:49:00Z"
    },
    // ... more records
  ]
}
```

**Status Values**:
- `pending_review`: Awaiting analyst approval
- `flagged`: Marked for further investigation
- `approved`: Analyst approved
- `locked`: Locked for audit (immutable)

**Scope Values**:
- `scope_1`: Direct emissions (fuel combustion)
- `scope_2`: Indirect energy (electricity)
- `scope_3`: Value chain (travel, procurement)

---

### Get Record Statistics
**Endpoint**: `GET /api/review/records/statistics/`

**Query Parameters**:
```
?company_id=1    // Required
```

**cURL Example**:
```bash
curl "http://localhost:8000/api/review/records/statistics/?company_id=1"
```

**Response** (200 OK):
```json
{
  "total": 16,
  "pending_review": 16,
  "flagged": 0,
  "approved": 0,
  "locked": 0,
  "by_scope": {
    "scope_1": 4,
    "scope_2": 3,
    "scope_3": 9
  },
  "by_source": {
    "sap": 4,
    "utility": 3,
    "travel": 9
  }
}
```

---

### Get Single Record
**Endpoint**: `GET /api/review/records/{id}/`

**cURL Example**:
```bash
curl "http://localhost:8000/api/review/records/1/"
```

**Response** (200 OK):
```json
{
  "id": 1,
  "company": 1,
  "source_system": "sap",
  "activity_type": "fuel_combustion",
  // ... full record details
  "audit_logs": [
    {
      "id": 1,
      "activity_record": 1,
      "action": "created",
      "previous_value": null,
      "new_value": "500.0 L",
      "user": "admin",
      "timestamp": "2026-05-26T10:49:00Z",
      "notes": "Ingestion from SAP"
    }
  ]
}
```

---

## ✅ Approval Endpoints

### Approve Record
**Endpoint**: `POST /api/review/records/{id}/approve/`

**Request Body**:
```json
{
  "notes": "Verified with plant manager"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/review/records/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes":"Verified with plant manager"}'
```

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "approved",
  "approved_by": "admin",
  "approved_at": "2026-05-26T16:30:00Z",
  "notes": "Verified with plant manager"
  // ... full record details
}
```

**Creates AuditLog Entry**:
```json
{
  "action": "approved",
  "user": "admin",
  "timestamp": "2026-05-26T16:30:00Z",
  "notes": "Verified with plant manager"
}
```

---

### Flag Record
**Endpoint**: `POST /api/review/records/{id}/flag/`

**Request Body**:
```json
{
  "reason": "Value seems unusually high for this period"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/review/records/1/flag/ \
  -H "Content-Type: application/json" \
  -d '{"reason":"Value seems unusually high"}'
```

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "flagged",
  "is_flagged": true,
  "flag_reason": "Value seems unusually high for this period"
  // ... full record details
}
```

---

### Lock Record for Audit
**Endpoint**: `POST /api/review/records/{id}/lock/`

**Request Body**: (empty)
```json
{}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/review/records/1/lock/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response** (200 OK):
```json
{
  "id": 1,
  "status": "locked",
  "locked_at": "2026-05-26T16:35:00Z"
  // ... full record details
}
```

**Note**: Locked records cannot be modified further. Creates audit log entry.

---

## 📊 Tenants Endpoints

### List Companies
**Endpoint**: `GET /api/tenants/companies/`

**Response** (200 OK):
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "TechCorp",
      "slug": "techcorp",
      "created_at": "2026-05-26T10:00:00Z",
      "updated_at": "2026-05-26T10:00:00Z"
    }
  ]
}
```

---

## Error Handling

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error. Check logs."
}
```

---

## Pagination

Default page size: 20 records

**Request**:
```
GET /api/review/records/?company_id=1&page=2
```

**Response**:
```json
{
  "count": 16,
  "next": null,
  "previous": "http://localhost:8000/api/review/records/?company_id=1&page=1",
  "results": [...]
}
```

---

## Filtering

### By Status
```
GET /api/review/records/?company_id=1&status=pending_review
GET /api/review/records/?company_id=1&status=flagged
GET /api/review/records/?company_id=1&status=approved
GET /api/review/records/?company_id=1&status=locked
```

### By Company
```
GET /api/review/records/?company_id=1
```

### Combine Filters
```
GET /api/review/records/?company_id=1&status=approved&page=2
```

---

## API Schema Documentation

**OpenAPI/Swagger UI**:
```
http://localhost:8000/api/docs/
```

**Raw OpenAPI Schema**:
```
http://localhost:8000/api/schema/
```

---

## Example Workflows

### Workflow 1: Upload & Review
```bash
# 1. Upload CSV
curl -X POST http://localhost:8000/api/ingestion/jobs/upload/ \
  -F "company_id=1" \
  -F "source_type=SAP_CSV" \
  -F "file=@test_sap_data.csv"

# 2. Get statistics
curl "http://localhost:8000/api/review/records/statistics/?company_id=1"

# 3. List pending records
curl "http://localhost:8000/api/review/records/?company_id=1&status=pending_review"

# 4. Approve first record
curl -X POST http://localhost:8000/api/review/records/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes":"Approved"}'
```

### Workflow 2: Flag & Review Later
```bash
# 1. Flag suspicious record
curl -X POST http://localhost:8000/api/review/records/5/flag/ \
  -H "Content-Type: application/json" \
  -d '{"reason":"Outlier value"}'

# 2. Get flagged records
curl "http://localhost:8000/api/review/records/?company_id=1&status=flagged"

# 3. Approve after investigation
curl -X POST http://localhost:8000/api/review/records/5/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes":"Investigated - data is correct"}'
```

---

## Rate Limiting

Currently disabled. For production, implement:
```python
# Add to settings.py REST_FRAMEWORK
'DEFAULT_THROTTLE_CLASSES': [
    'rest_framework.throttling.AnonRateThrottle',
    'rest_framework.throttling.UserRateThrottle'
],
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',
    'user': '1000/hour'
}
```

---

## CORS Configuration

**Allowed Origins**:
- `http://localhost:3000` (development)
- `http://localhost:8000` (dev API)
- `*.railway.app` (production)
- `*.vercel.app` (frontend)

**Add more** in backend `.env`:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://example.com
```

---

## Authentication (Future)

Prepare for JWT by installing:
```bash
pip install djangorestframework-simplejwt
```

Then add to URLs:
```python
from rest_framework_simplejwt.views import TokenObtainPairView

path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
```

---

## Testing API with Python

```python
import requests

# Upload
files = {'file': open('test_sap_data.csv', 'rb')}
data = {'company_id': '1', 'source_type': 'SAP_CSV'}
response = requests.post(
    'http://localhost:8000/api/ingestion/jobs/upload/',
    files=files,
    data=data
)
print(response.json())

# List records
response = requests.get(
    'http://localhost:8000/api/review/records/',
    params={'company_id': 1, 'status': 'pending_review'}
)
print(response.json())

# Approve
response = requests.post(
    'http://localhost:8000/api/review/records/1/approve/',
    json={'notes': 'Approved'}
)
print(response.json())
```

---

## Testing API with JavaScript/Node.js

```javascript
import axios from 'axios';

const API = 'http://localhost:8000/api';

// List records
const records = await axios.get(
  `${API}/review/records/?company_id=1&status=pending_review`
);
console.log(records.data.results);

// Approve record
const approve = await axios.post(
  `${API}/review/records/1/approve/`,
  { notes: 'Approved by analyst' }
);
console.log(approve.data);

// Get statistics
const stats = await axios.get(
  `${API}/review/records/statistics/?company_id=1`
);
console.log(stats.data);
```

---

## Deployment API Changes

When deploying to production:

1. **Change base URL** in frontend:
```javascript
// src/Dashboard.jsx
const API_BASE_URL = 'https://your-backend.railway.app/api';
```

2. **Update CORS** in backend settings:
```python
CORS_ALLOWED_ORIGINS = 'https://your-frontend.vercel.app,https://your-backend.railway.app'
```

3. **Add authentication** to all requests:
```javascript
// With JWT token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

---

**Last Updated**: May 26, 2026
**API Version**: 1.0
**Status**: Production Ready ✅
