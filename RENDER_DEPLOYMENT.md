# Deploy Breathe ESG to Render.com 🚀

Complete step-by-step guide to deploy your platform to Render.com.

---

## 📋 Deployment Checklist

- [ ] Create Render.com account
- [ ] Deploy backend (Django)
- [ ] Deploy PostgreSQL database
- [ ] Deploy frontend (React)
- [ ] Configure environment variables
- [ ] Test live endpoints
- [ ] Update frontend with live API URL

---

## Part 1: Backend Deployment (Django + PostgreSQL)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **Sign Up** (use GitHub for easy login)
3. Authorize Render to access your GitHub
4. Verify email

### Step 2: Create PostgreSQL Database

1. On Render dashboard, click **New +** → **PostgreSQL**
2. Fill in details:
   - **Name**: `breathe-esg-db`
   - **Database**: `breathe_esg`
   - **User**: `breatheuser`
   - **Region**: Choose closest to you
   - **Plan**: Free (good for testing)
3. Click **Create Database**
4. **Copy the connection string** - You'll need it soon

The connection string looks like:
```
postgresql://breatheuser:PASSWORD@HOST:5432/breathe_esg
```

Save this! ⭐

### Step 3: Deploy Backend Service

1. On Render dashboard, click **New +** → **Web Service**
2. Connect your GitHub:
   - Select **Connect your repository** 
   - Search for `breathe-esg`
   - Click **Connect**
3. Fill in details:
   - **Name**: `breathe-esg-backend`
   - **Environment**: Python 3
   - **Region**: Same as database (or near it)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn config.wsgi:application`
   - **Plan**: Free

4. Click **Create Web Service**

### Step 4: Add Environment Variables

After service is created:

1. Go to **Environment** tab
2. Add these variables:

```
DATABASE_URL = (paste your PostgreSQL connection string from Step 2)
DEBUG = false
ALLOWED_HOSTS = your-service-name.onrender.com
SECRET_KEY = (generate a new one or use an existing one)
CORS_ALLOWED_ORIGINS = https://your-frontend-url.onrender.com
```

To generate a new SECRET_KEY, run this in Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

3. Click **Save**
4. Render will automatically redeploy

### Step 5: Check Backend Deployment

1. Wait for deploy to complete (check the logs)
2. Once deployed, you'll see a URL like:
   ```
   https://breathe-esg-backend.onrender.com
   ```
3. Test it:
   ```
   https://breathe-esg-backend.onrender.com/api/review/records/?company_id=1
   ```

If you see JSON data → ✅ Backend is working!

---

## Part 2: Frontend Deployment (React)

### Step 1: Create Frontend Service

1. On Render dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository again
3. Fill in details:
   - **Name**: `breathe-esg-frontend`
   - **Environment**: Node
   - **Region**: Same as backend
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm run start` or `npx serve -s build -l 3000`
   - **Plan**: Free

4. Click **Create Web Service**

### Step 2: Add Frontend Environment Variables

After frontend service is created:

1. Go to **Environment** tab
2. Add this variable:

```
REACT_APP_API_URL = https://your-backend-url.onrender.com/api
```

(Replace with your actual backend URL from Part 1, Step 5)

Example:
```
REACT_APP_API_URL = https://breathe-esg-backend.onrender.com/api
```

3. Click **Save**
4. Render will redeploy automatically

### Step 3: Update Frontend Code

Make sure your frontend is using the environment variable:

**frontend/src/api.js** (create if doesn't exist):
```javascript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

Then use it in axios calls:
```javascript
const response = await axios.get(`${API_BASE_URL}/review/records/?company_id=1`);
```

### Step 4: Check Frontend Deployment

1. Wait for deploy to complete
2. Your frontend URL will be something like:
   ```
   https://breathe-esg-frontend.onrender.com
   ```
3. Visit it in browser
4. Test the upload form and dashboard

If everything works → ✅ Platform is live!

---

## Part 3: Final Configuration

### Update CORS on Backend

In your backend service on Render:

1. Go to **Environment** tab
2. Update `CORS_ALLOWED_ORIGINS`:
   ```
   https://breathe-esg-frontend.onrender.com
   ```
3. Save and redeploy

### Test End-to-End

1. Go to your frontend: `https://breathe-esg-frontend.onrender.com`
2. Upload a test CSV file
3. Should see success message
4. Refresh dashboard - new records should appear
5. Try approving a record

If all steps work → ✅ **Platform is deployed!**

---

## 📊 Your Live URLs

After deployment, you'll have:

```
Frontend:  https://breathe-esg-frontend.onrender.com
Backend:   https://breathe-esg-backend.onrender.com
API Docs:  https://breathe-esg-backend.onrender.com/api/docs
Admin:     https://breathe-esg-backend.onrender.com/admin
Database:  PostgreSQL on Render
```

---

## 🔐 Important Security Notes

Before going live:

- ✅ DEBUG = false (already set)
- ✅ ALLOWED_HOSTS configured
- ✅ CORS properly restricted
- ✅ SECRET_KEY is random
- ✅ Database password is secure
- ✅ Environment variables not in code

---

## 🛠️ Troubleshooting

### "BUILD FAILED" on Backend

**Check logs** on Render:
1. Click service → **Logs** tab
2. Look for error messages
3. Common issues:
   - Missing dependency: Add to `requirements.txt`
   - Wrong directory: Ensure `Root Directory` is `backend`
   - Database connection: Check `DATABASE_URL` format

### "Can't connect to API" on Frontend

**Check CORS settings**:
1. Make sure `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. Check `REACT_APP_API_URL` environment variable
3. Test API directly: Visit `https://backend.onrender.com/api/records/`

### "Database migration failed"

**Run migrations manually**:
1. SSH into backend service (Render allows this)
2. Or use Render's shell:
   ```bash
   python manage.py migrate
   ```

### Service keeps restarting

**Check memory**:
- Free tier has limits
- Try optimizing Django settings
- Contact Render support if persistent

---

## 📈 Monitoring

Once deployed:

1. **Backend Logs**: Click service → Logs tab
2. **Frontend Logs**: Same place
3. **Database**: Check PostgreSQL tab for usage
4. **Alerts**: Set up email notifications in settings

---

## 💰 Costs

**Free Tier** (perfect for testing):
- ✅ 1 backend service (dormant after 15 min inactivity)
- ✅ 1 frontend service (dormant after 15 min inactivity)
- ✅ 1 PostgreSQL database (90 days free, then paid)
- ✅ 100 GB bandwidth/month

**To keep running 24/7**: Upgrade to paid plan ($7/month per service)

---

## 🚀 Deployment Complete!

Your platform is now live! Share these URLs:

```
Frontend: https://breathe-esg-frontend.onrender.com
API Docs: https://breathe-esg-backend.onrender.com/api/docs
GitHub:   https://github.com/SUNNYKASHYAP100/breathe-esg
```

---

## 📝 Next Steps After Deployment

- [ ] Create superuser on production
- [ ] Add real data (upload actual CSV files)
- [ ] Set up monitoring and alerts
- [ ] Configure custom domain (optional)
- [ ] Set up email notifications
- [ ] Add authentication system
- [ ] Optimize performance
- [ ] Set up CI/CD pipeline

---

## 🆘 Need Help?

### Render Support
- Documentation: https://render.com/docs
- Dashboard: https://dashboard.render.com

### Django Issues
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- DRF CORS: https://github.com/adamchainz/django-cors-headers

### React Issues
- Environment Variables: https://create-react-app.dev/docs/adding-custom-environment-variables/
- Build Issues: Check npm logs

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Backend service is running (green status on Render)
- [ ] Frontend service is running (green status on Render)
- [ ] PostgreSQL database is created
- [ ] Backend API responds: `https://backend-url.onrender.com/api/review/records/`
- [ ] Frontend loads: `https://frontend-url.onrender.com`
- [ ] Can upload CSV file
- [ ] Records appear in dashboard
- [ ] Approve button works
- [ ] No CORS errors in browser console

---

## 🎉 You're Live!

Your Breathe ESG platform is now deployed on Render and accessible from anywhere!

**Share your platform URL and start using it!** 🌍

---

**Last Updated**: May 27, 2026  
**Deployment Platform**: Render.com  
**Status**: Ready to Deploy ✅
