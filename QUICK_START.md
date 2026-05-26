# Breathe ESG - Quick Start Guide

## 🚀 Start the Platform in 30 Seconds

### Terminal 1: Backend
```bash
cd "d:\Breathe ESG\backend"
..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```
✅ Backend runs at http://localhost:8000

### Terminal 2: Frontend
```bash
cd "d:\Breathe ESG\frontend"
npm start
```
✅ Frontend runs at http://localhost:3000

### Then
Open browser to **http://localhost:3000** and start uploading data!

---

## 📤 Upload Data (3 Options)

### Option 1: SAP Fuel Data
1. Keep dropdown as "SAP Export (CSV)"
2. Click "Choose File" → select `test_sap_data.csv`
3. Click "Upload File"
4. ✅ See success message with Job ID

### Option 2: Utility Electricity Data
1. Change dropdown to "Utility Portal Export (CSV)"
2. Click "Choose File" → select `test_utility_data.csv`
3. Click "Upload File"
4. ✅ New electricity records appear in dashboard

### Option 3: Travel Data
1. Change dropdown to "Travel Data (CSV)"
2. Click "Choose File" → select `test_travel_data.csv`
3. Click "Upload File"
4. ✅ New travel records appear in dashboard

---

## 👀 View Records in Dashboard

1. Scroll down to see **Activity Records** table
2. Left sidebar shows **Statistics**:
   - Total Records count
   - Pending Review count
   - Flagged count
   - Approved count
   - Locked count

3. Use **Filter Buttons** to view by status:
   - ✅ Pending Review (default)
   - 🚩 Flagged
   - ✓ Approved
   - 🔒 Locked

---

## ✅ Approve Records

1. Find a record in the table
2. Scroll right and click **"View"** button
3. Modal opens with full record details
4. Click **"Approve"** button
5. ✅ Record locked for audit (status → Approved)

---

## 🚩 Flag Records for Review

1. Open record detail modal (click "View")
2. Click **"Flag for Review"** button
3. Enter reason when prompted (e.g., "Value seems high")
4. ✅ Record flagged (status → Flagged)

---

## 🔒 Lock Records for Audit

1. Open record detail modal (click "View")
2. Click **"Lock for Audit"** button
3. ✅ Record locked (status → Locked)
4. ⚠️ Cannot be modified after locking

---

## 📊 Dashboard Explained

**Statistics Card (Top Left):**
- Shows count of records by status
- Updates in real-time after uploads

**Filter Buttons (Left Sidebar):**
- Click to filter table by approval status
- Active button highlighted in blue

**Activity Records Table (Main):**
- Shows all filtered records
- Columns: Date, Type, Scope, Quantity, Source, Status, Action

**Scope Badges:**
- 🔴 scope_1 = Fuel combustion (Direct)
- 🟢 scope_2 = Electricity (Indirect)
- 🟡 scope_3 = Travel (Value Chain)

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `test_sap_data.csv` | 4 fuel records for testing |
| `test_utility_data.csv` | 4 electricity records for testing |
| `test_travel_data.csv` | 4 travel records for testing |

---

## ⚙️ Expected CSV Formats

### SAP Export
```
Plant,Menge,Unit,Date,Description
Plant01,500,L,2024-02-10,Diesel fuel
Plant02,300,L,2024-02-11,Gasoline
```

### Utility Portal
```
Meter ID,Start Date,End Date,Consumption,Unit
METER001,2024-02-01,2024-02-29,5000,kWh
METER002,2024-02-01,2024-02-29,3200,kWh
```

### Travel Data
```
Employee,From Airport,To Airport,Distance,Date
John Doe,LAX,JFK,2475,2024-02-05
Jane Smith,LHR,CDG,215,2024-02-08
```

---

## 🔧 Troubleshooting

### Issue: "Cannot connect to backend"
**Solution**: Check Django server running on terminal 1
```bash
# Terminal 1 should show:
Starting development server at http://0.0.0.0:8000/
```

### Issue: "Upload button disabled"
**Solution**: Select a CSV file first
1. Click "Choose File"
2. Select any .csv file
3. Upload button becomes enabled

### Issue: "Dashboard shows 'Loading...'"
**Solution**: Wait 3-5 seconds for API response
- Backend processes CSV in background
- Dashboard auto-refreshes after upload

### Issue: "Port 3000 already in use"
**Solution**: Kill existing process
```bash
# PowerShell
lsof -i :3000 | grep node | awk '{print $2}' | xargs kill -9
```

---

## 📖 Learn More

| Document | Learn About |
|----------|-------------|
| `MODEL.md` | Database schema and relationships |
| `DECISIONS.md` | Why we chose SAP/Utility/Travel sources |
| `SOURCES.md` | Real-world data format research |
| `DEPLOYMENT.md` | Deploy to Railway/Render/Vercel |
| `COMPLETION_SUMMARY.md` | Full feature list and architecture |

---

## 🎯 Common Tasks

### Count all records
Look at "TOTAL RECORDS" in Statistics card (top left)

### Find fuel records only
Filter by Status → Look for "fuel_combustion" in Type column

### View approval workflow
1. Select any record and click "View"
2. Three buttons available:
   - Approve (green)
   - Flag for Review (orange)
   - Lock for Audit (blue)

### Check what's been approved
Click "Approved" filter button to see all approved records

### See recent uploads
Scroll table by date (most recent at top)

---

## 💾 Database Info

**Current Records**: 16 total
- SAP (Scope 1): 4 fuel records
- Utility (Scope 2): 3 electricity records
- Travel (Scope 3): 9 flight/ground/hotel records

**Status**: All records in "Pending Review"
- Ready to be approved by analyst
- Can be flagged for further investigation
- Can be locked for final audit

---

## 🌍 Production Deployment

Ready to deploy? See `DEPLOYMENT.md` for:
- Railway backend deployment
- Vercel frontend deployment
- PostgreSQL setup
- Environment variables
- SSL/HTTPS configuration

---

## ✨ Key Features

✅ **Multi-source ingestion** (SAP, Utility, Travel)
✅ **Automatic normalization** (scope categorization, unit conversion)
✅ **Analyst review dashboard** (approve/flag/lock workflows)
✅ **Complete audit trail** (who, what, when, why)
✅ **Real-time statistics** (status distribution, by scope/source)
✅ **Production-ready** (error handling, logging, migrations)

---

## 🆘 Need Help?

1. **Upload failing?** → Check CSV format matches expected structure
2. **No records showing?** → Scroll down to Activity Records section
3. **API errors?** → Ensure backend terminal shows "Starting development server"
4. **Styling issues?** → Hard refresh browser (Ctrl+Shift+R)

---

**Let's review ESG data! 🌱**
