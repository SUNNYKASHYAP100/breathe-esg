# 🚀 Breathe ESG - Commands & Terminal Guide

## Quick Start Commands

### PowerShell Terminal 1: Backend
```powershell
# Navigate to backend
cd "d:\Breathe ESG\backend"

# Start server (venv activates automatically)
..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

**Expected Output**:
```
System check identified no issues (0 silenced).
May 26, 2026 - 16:22:58
Django version 6.0.5, using settings 'config.settings'
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

### PowerShell Terminal 2: Frontend
```powershell
# Navigate to frontend
cd "d:\Breathe ESG\frontend"

# Start React development server
npm start
```

**Expected Output**:
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

---

## Common Django Commands

### Create Virtual Environment
```bash
python -m venv venv
```

### Activate Virtual Environment
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# Or in backend folder:
..\venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Database Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Or Both at Once
```bash
python manage.py migrate --run-syncdb
```

### Generate Sample Data
```bash
python manage.py generate_sample_data
```

### Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow prompts: 
# Username: admin
# Email: admin@breatheesg.com
# Password: (create secure password)
```

### Access Django Admin
```
http://localhost:8000/admin/
```

### Run Tests
```bash
python manage.py test
```

### Check Django Configuration
```bash
python manage.py check
```

### View API Schema
```bash
# OpenAPI/Swagger
http://localhost:8000/api/docs/

# Raw schema
http://localhost:8000/api/schema/
```

---

## Common npm Commands

### Install Dependencies
```bash
cd frontend
npm install
```

### Install Specific Package
```bash
npm install axios
npm install tailwindcss
```

### Start Development Server
```bash
npm start
```

### Build for Production
```bash
npm run build
```

### Run Tests
```bash
npm test
```

### Eject Configuration (⚠️ irreversible)
```bash
npm run eject
```

### Fix Vulnerabilities
```bash
npm audit fix
```

### Check for Vulnerabilities
```bash
npm audit
```

### Update npm
```bash
npm install -g npm@latest
```

---

## File Management

### List Directory Contents
```powershell
# List files in current directory
ls
# or
dir

# List with details
ls -l
# or
Get-ChildItem -Force
```

### Navigate Directories
```powershell
# Go to Breathe ESG
cd "d:\Breathe ESG"

# Go to parent directory
cd ..

# Show current path
pwd
# or
Get-Location
```

### View File Contents
```powershell
# Simple view
type filename.txt

# With syntax highlighting (PowerShell)
Get-Content filename.txt

# First 20 lines
Get-Content filename.txt -TotalCount 20
```

### Create File
```powershell
# Create empty file
New-Item -Path filename.txt -ItemType File

# Create with content
@"
Content here
" | Out-File filename.txt
```

### Delete File/Folder
```powershell
# Delete file
Remove-Item filename.txt

# Delete folder (recursive)
Remove-Item foldername -Recurse -Force
```

---

## Database Commands

### View SQLite Database
```bash
# Use sqlite3 CLI
sqlite3 db.sqlite3

# Common queries:
.tables                    # Show all tables
.schema CompanyUser        # Show table structure
SELECT * FROM tenants_company;  # Query data
```

### Backup Database
```powershell
# Copy entire db
Copy-Item db.sqlite3 db.sqlite3.backup
```

### Reset Database (WARNING: Deletes all data)
```bash
# Delete database file
rm db.sqlite3

# Recreate with migrations
python manage.py migrate --run-syncdb

# Regenerate sample data
python manage.py generate_sample_data
```

---

## Testing Endpoints

### Using PowerShell
```powershell
# Simple GET request
$response = Invoke-WebRequest -Uri 'http://localhost:8000/api/review/records/?company_id=1' -UseBasicParsing
$response.Content | ConvertFrom-Json

# POST request with JSON
$body = @{notes="Test"} | ConvertTo-Json
Invoke-WebRequest -Uri 'http://localhost:8000/api/review/records/1/approve/' `
  -Method Post `
  -Body $body `
  -ContentType 'application/json' `
  -UseBasicParsing
```

### Using curl (if installed)
```bash
# List records
curl -s "http://localhost:8000/api/review/records/?company_id=1" | ConvertFrom-Json

# Upload file
curl -X POST http://localhost:8000/api/ingestion/jobs/upload/ \
  -F "company_id=1" \
  -F "source_type=SAP_CSV" \
  -F "file=@test_sap_data.csv"

# Approve record
curl -X POST http://localhost:8000/api/review/records/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes":"Approved"}'
```

### Using Python
```python
import requests

# List records
response = requests.get(
    'http://localhost:8000/api/review/records/',
    params={'company_id': 1}
)
print(response.json())

# Upload file
with open('test_sap_data.csv', 'rb') as f:
    files = {'file': f}
    data = {'company_id': '1', 'source_type': 'SAP_CSV'}
    response = requests.post(
        'http://localhost:8000/api/ingestion/jobs/upload/',
        files=files,
        data=data
    )
print(response.json())
```

---

## Debugging

### View Django Logs
```bash
# Logs print to terminal running Django
# Look for lines like:
# GET /api/review/records/ HTTP/1.1" 200

# For more detail, add logging to settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### View React Logs
```powershell
# In browser, open Developer Tools
# F12 or Ctrl+Shift+I

# Go to Console tab to see:
# - Errors (red)
# - Warnings (yellow)
# - Logs (blue)
# - Network requests (Network tab)
```

### Check Port Availability
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process on port (replace PID with number from above)
taskkill /PID 12345 /F
```

### View Python Version
```bash
python --version
# or
python -c "import sys; print(sys.version)"
```

### View Node/npm Version
```bash
node --version
npm --version
```

---

## Environment Variables

### Create .env File (Backend)
```bash
# File: d:\Breathe ESG\backend\.env

SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
CELERY_BROKER_URL=redis://localhost:6379/0
```

### Create .env File (Frontend)
```bash
# File: d:\Breathe ESG\frontend\.env

REACT_APP_API_BASE_URL=http://localhost:8000/api
```

### Read Environment Variables (Python)
```python
from decouple import config

secret = config('SECRET_KEY')
debug = config('DEBUG', cast=bool)
database = config('DATABASE_URL')
```

---

## Git Commands (If Using Git)

### Initialize Repository
```bash
git init
```

### Add Files
```bash
git add .
git add filename.txt
```

### Commit Changes
```bash
git commit -m "Add upload feature"
```

### Check Status
```bash
git status
```

### View Commit History
```bash
git log --oneline
```

---

## Docker Commands (Future Deployment)

### Build Docker Image
```bash
docker build -t breathe-esg:latest .
```

### Run Docker Container
```bash
docker run -p 8000:8000 breathe-esg:latest
```

### Docker Compose
```bash
docker-compose up
```

---

## Process Management

### List Running Processes
```powershell
# All processes
Get-Process

# Filter by name
Get-Process python
Get-Process node

# Task manager
taskmgr
```

### Kill Process
```powershell
# By PID
taskkill /PID 12345 /F

# By name
taskkill /IM python.exe /F
taskkill /IM node.exe /F
```

### Stop Servers
```powershell
# In Django terminal: CTRL+BREAK
# In React terminal: CTRL+C

# Or kill processes
taskkill /IM python.exe /F
taskkill /IM node.exe /F
```

---

## Helpful Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Stop running process |
| `Ctrl+Break` | Stop Django server (alternate) |
| `↑ Arrow` | Previous command |
| `↓ Arrow` | Next command |
| `Tab` | Auto-complete path/command |
| `Ctrl+L` | Clear terminal |
| `Clear-Host` | Clear terminal (PowerShell) |
| `cls` | Clear terminal (CMD) |

---

## Terminal Sessions

### Keep Terminal Running in Background
```powershell
# Start Django in new session (Windows)
Start-Process powershell -ArgumentList {
    cd "d:\Breathe ESG\backend"
    ..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
}
```

### Terminal Multiplexing
```bash
# Using tmux (Linux/Mac only)
tmux new-session -d -s backend
tmux send-keys -t backend "cd ~/breathe-esg/backend && python manage.py runserver" Enter
```

---

## Troubleshooting Commands

### Check Django Health
```bash
python manage.py check
```

### Test Database Connection
```bash
python manage.py dbshell
# Type: .quit to exit
```

### Verify API Endpoint
```powershell
# Test backend accessibility
Test-NetConnection -ComputerName localhost -Port 8000

# Test frontend accessibility
Test-NetConnection -ComputerName localhost -Port 3000
```

### Force Kill Stubborn Processes
```powershell
# Find and kill by port
$process = Get-NetTCPConnection -LocalPort 8000 | Get-Process
Stop-Process -InputObject $process -Force
```

### View System Resources
```powershell
# CPU and Memory usage
Get-Process python | Select-Object Name, CPU, Memory

# Disk space
Get-PSDrive

# Network connections
Get-NetTCPConnection -State Listen
```

---

## Performance Monitoring

### Monitor Django
```bash
# Use django-silk (install first)
pip install django-silk

# Add to INSTALLED_APPS
# Access at: http://localhost:8000/silk/

# Basic timing
python -m cProfile manage.py runserver
```

### Monitor Frontend
```bash
# React DevTools
# Chrome extension for React debugging

# Performance profiling in browser
# F12 → Performance tab → Record
```

---

## Installation Verification

### Verify All Dependencies
```bash
# Check Django
python -c "import django; print(django.VERSION)"

# Check DRF
python -c "import rest_framework; print(rest_framework.VERSION)"

# Check React
npm list react

# Check Node modules
npm list --depth=0
```

---

## Useful Aliases (PowerShell)

Create in `$PROFILE`:
```powershell
# Backend
Set-Alias be 'cd "d:\Breathe ESG\backend"'
Set-Alias fe 'cd "d:\Breathe ESG\frontend"'

# Commands
Set-Alias runbe 'python manage.py runserver 0.0.0.0:8000'
Set-Alias runfe 'npm start'

# Then use:
be              # Jump to backend
runbe           # Start Django
fe              # Jump to frontend
runfe           # Start React
```

---

## One-Liner Quick Starts

```powershell
# Start everything in one line
cd "d:\Breathe ESG\backend"; Start-Process powershell -ArgumentList '-NoExit', '-Command', '..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000'; cd "d:\Breathe ESG\frontend"; npm start

# Or use separate terminals and paste these:
# Terminal 1:
cd "d:\Breathe ESG\backend" && ..\venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000

# Terminal 2:
cd "d:\Breathe ESG\frontend" && npm start

# Terminal 3 (optional - for testing):
cd "d:\Breathe ESG"
```

---

## Advanced: Development Workflow

### Full Reset & Restart
```bash
# Stop all servers (Ctrl+C in terminals)

# Backend reset
cd backend
rm db.sqlite3
python manage.py migrate --run-syncdb
python manage.py generate_sample_data
python manage.py runserver 0.0.0.0:8000

# Frontend reset
cd frontend
rm -r node_modules
npm install
npm start
```

---

**Last Updated**: May 26, 2026
**Platform**: Windows PowerShell
**Status**: Ready for Production ✅
