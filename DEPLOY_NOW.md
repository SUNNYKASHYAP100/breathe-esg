# 🚀 Deploy Breathe ESG in 20 Minutes

Quick deployment guide to get your platform live on Render.com

---

## ⚡ TL;DR - Quick Steps

### 1. Go to Render.com
- Sign up at [render.com](https://render.com)
- Connect your GitHub account

### 2. Create PostgreSQL Database
```
New → PostgreSQL
Name: breathe-esg-db
Keep other defaults, save connection string
```

### 3. Deploy Backend
```
New → Web Service
Connected repo: breathe-esg
Root Directory: backend
Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
Start Command: gunicorn config.wsgi:application
Environment: Python 3
Add DATABASE_URL from PostgreSQL above
```

### 4. Deploy Frontend
```
New → Web Service
Connected repo: breathe-esg
Root Directory: frontend
Build Command: npm install && npm run build
Start Command: npm run start
Environment: Node
Add REACT_APP_API_URL = https://your-backend-url.onrender.com/api
```

### 5. Update CORS
Go to backend service → Environment
Update: CORS_ALLOWED_ORIGINS = https://your-frontend-url.onrender.com

### 6. Test
Visit your frontend URL and upload a CSV file ✅

---

## 📊 What You Get

| Component | URL |
|-----------|-----|
| Frontend | https://breathe-esg-frontend.onrender.com |
| Backend API | https://breathe-esg-backend.onrender.com/api |
| Admin Panel | https://breathe-esg-backend.onrender.com/admin |
| Database | PostgreSQL on Render (private) |

---

## 🔐 Environment Variables Needed

### Backend
```
DATABASE_URL = postgresql://user:password@host:5432/db
DEBUG = false
ALLOWED_HOSTS = your-backend.onrender.com
SECRET_KEY = (generate new one)
CORS_ALLOWED_ORIGINS = https://your-frontend.onrender.com
```

### Frontend
```
REACT_APP_API_URL = https://your-backend.onrender.com/api
```

---

## ✅ Verification

After deployment:
1. Visit frontend URL
2. Upload test CSV
3. See records in dashboard ✅
4. Approve a record ✅

If all work → **You're live!** 🎉

---

## 📚 Detailed Guides

- Full step-by-step: **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**
- Pre-flight checklist: **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)**
- Troubleshooting: **[RENDER_DEPLOYMENT.md#troubleshooting](RENDER_DEPLOYMENT.md)**

---

## 💾 Database Setup

After backend deploys:

```bash
# Render provides a shell - run this:
python manage.py migrate
python manage.py createsuperuser  # Create admin user
```

---

## 🆘 Common Issues

### "Build Failed"
- Check logs in Render dashboard
- Usually missing dependencies or wrong root directory
- See RENDER_DEPLOYMENT.md for fixes

### "Can't connect to API"
- Check CORS_ALLOWED_ORIGINS is set to your frontend URL
- Check REACT_APP_API_URL is correct
- Verify backend is running (green status)

### "Database migration failed"
- Run manually via Render shell
- See RENDER_DEPLOYMENT.md troubleshooting

---

## 🎯 Next Steps After Deploy

1. ✅ Test all features work
2. ✅ Upload real data
3. ✅ Share the URL with team
4. ✅ Set up monitoring (optional)
5. ✅ Add authentication (optional)

---

## 📞 Support

- Render docs: https://render.com/docs
- Full deployment guide: **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**
- Production checklist: **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)**

---

## ✨ You're Ready!

Follow the steps above and your platform will be live in 20 minutes! 🚀

---

**Last Updated**: May 27, 2026
**Platform**: Render.com
**Status**: Ready to Deploy ✅
