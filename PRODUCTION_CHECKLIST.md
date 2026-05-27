# Production Deployment Checklist ✅

Complete checklist before deploying Breathe ESG to production.

---

## 🔐 Security Checks

### Environment Variables
- [ ] `DEBUG = False` (NOT True)
- [ ] `SECRET_KEY` is random and unique
- [ ] `ALLOWED_HOSTS` includes production domain
- [ ] `CORS_ALLOWED_ORIGINS` restricted to your domain
- [ ] Database credentials are strong
- [ ] No secrets in code or .env files

### Database
- [ ] Using PostgreSQL (not SQLite)
- [ ] Database is backed up
- [ ] PostgreSQL password is strong (12+ chars, mixed case)
- [ ] Database user has limited permissions
- [ ] SSL connection to database enabled

### API Security
- [ ] CSRF protection enabled
- [ ] CORS properly configured
- [ ] Rate limiting considered
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)

### Frontend Security
- [ ] HTTPS enforced (automatic on Render/Vercel)
- [ ] No sensitive data in localStorage
- [ ] API calls use environment variables
- [ ] No API keys exposed in code
- [ ] XSS protection via React

---

## 🛠️ Code Quality

### Backend
- [ ] All imports working
- [ ] No console.log or print() statements (except logging)
- [ ] No hardcoded URLs or credentials
- [ ] Proper error handling everywhere
- [ ] Logging configured for production

### Frontend
- [ ] No console.error or console.warn in production builds
- [ ] All API calls handle errors
- [ ] Environment variables properly set
- [ ] No localhost references
- [ ] CSS/images optimized

### Database
- [ ] All migrations applied
- [ ] Database schema correct
- [ ] Foreign key relationships intact
- [ ] Indexes created on frequently queried fields
- [ ] No unused tables or fields

---

## 📋 Configuration

### Django Settings
- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` updated
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `STATIC_ROOT` configured
- [ ] `STATIC_URL` works on CDN/cloud storage
- [ ] `LOGGING` configured for production

### React Configuration
- [ ] `REACT_APP_API_URL` set to production backend
- [ ] `.env.production` created (if needed)
- [ ] Build optimizations enabled
- [ ] Service worker considered for offline support
- [ ] `PUBLIC_URL` correct for deployment

### Server Configuration
- [ ] Gunicorn/WSGI configured
- [ ] Worker count appropriate for server size
- [ ] Timeouts set correctly
- [ ] Health checks enabled
- [ ] Auto-restart on failure enabled

---

## 🗄️ Database

### Pre-Deployment
- [ ] Database created on cloud provider
- [ ] Migrations written for schema
- [ ] Test data removed (or marked as test)
- [ ] Backup taken before migration
- [ ] Connection string verified
- [ ] Network access configured (whitelist IPs if needed)

### Post-Deployment
- [ ] Run migrations on production: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Load initial data if needed: `python manage.py loaddata fixture.json`
- [ ] Verify tables created: `python manage.py shell` → `from apps.ingestion.models import IngestionJob; print(IngestionJob.objects.count())`

---

## 🚀 Deployment Platform

### Render.com Setup
- [ ] Account created
- [ ] PostgreSQL database provisioned
- [ ] Backend service created and deployed
- [ ] Frontend service created and deployed
- [ ] Environment variables set on both services
- [ ] Logs accessible and checked
- [ ] Auto-deploy from GitHub configured

### Domain & DNS (Optional)
- [ ] Custom domain purchased (if desired)
- [ ] DNS records updated to point to Render
- [ ] SSL certificate auto-generated
- [ ] Redirects working (http → https)

---

## ✅ Testing

### API Endpoints
- [ ] GET `/api/review/records/` returns 200
- [ ] GET `/api/review/records/statistics/` returns stats
- [ ] POST `/api/ingestion/jobs/upload/` accepts file
- [ ] POST `/api/review/records/{id}/approve/` works
- [ ] POST `/api/review/records/{id}/flag/` works
- [ ] Pagination works on list endpoints
- [ ] Filtering works (status, company_id)

### Frontend
- [ ] App loads at production URL
- [ ] Dashboard displays records
- [ ] Upload form loads and submits
- [ ] Can filter records by status
- [ ] Can approve/flag records
- [ ] Success messages appear
- [ ] Error messages appear for failures
- [ ] Mobile responsive

### CORS
- [ ] No CORS errors in browser console
- [ ] API calls succeed from frontend
- [ ] Preflight requests work
- [ ] Authentication headers pass through

### Database
- [ ] Superuser can login to admin
- [ ] Records display in admin
- [ ] Migrations ran successfully
- [ ] No foreign key errors
- [ ] Permissions working correctly

---

## 📊 Monitoring & Logs

### Logging Setup
- [ ] Backend logs captured (Render dashboard)
- [ ] Frontend errors tracked (browser console or service)
- [ ] Database connection logged
- [ ] Error alerts configured
- [ ] Performance metrics captured

### Health Checks
- [ ] Endpoint health check configured
- [ ] Service auto-restart on failure enabled
- [ ] Database connectivity monitored
- [ ] Uptime monitoring setup (Uptime Robot recommended)
- [ ] Alert emails configured

### Backups
- [ ] PostgreSQL backups enabled (Render does this)
- [ ] Backup retention set (7+ days minimum)
- [ ] Test restore procedure
- [ ] Backup location verified

---

## 📱 Communication

### Before Launch
- [ ] Documentation updated with live URLs
- [ ] README points to production
- [ ] API docs updated with production endpoints
- [ ] Deployment guide shared with team
- [ ] Login credentials shared securely

### After Launch
- [ ] Status page created or shared
- [ ] Support contact information provided
- [ ] Issue tracking system set up (GitHub Issues)
- [ ] User feedback mechanism established
- [ ] Maintenance window communication plan ready

---

## 🔄 Rollback Plan

- [ ] Previous version tagged in Git
- [ ] Database backup taken before deployment
- [ ] Rollback procedure documented
- [ ] Team knows how to execute rollback
- [ ] Communication template ready

---

## 📈 Performance

### Backend Performance
- [ ] Gunicorn workers optimized for server size
- [ ] Database connection pooling configured
- [ ] Caching considered for slow queries
- [ ] API response times acceptable (<500ms)
- [ ] Database queries optimized (no N+1 queries)

### Frontend Performance
- [ ] Bundle size reasonable (<200KB gzipped)
- [ ] Images optimized and lazy-loaded
- [ ] CSS minified
- [ ] JavaScript minified and split
- [ ] Load time acceptable (<3 seconds)

### Database Performance
- [ ] Indexes created on frequently filtered columns
- [ ] Query performance acceptable
- [ ] Connection pool sized correctly
- [ ] Database statistics updated
- [ ] Slow query log monitored

---

## 🎓 Documentation

- [ ] Deployment guide written (RENDER_DEPLOYMENT.md)
- [ ] API documentation updated
- [ ] Architecture documented (MODEL.md)
- [ ] Troubleshooting guide created
- [ ] Runbook for common operations
- [ ] Team training completed

---

## ✨ Final Checks

- [ ] Code review completed
- [ ] Tests pass locally
- [ ] No console errors or warnings
- [ ] No hardcoded localhost references
- [ ] No sensitive data in logs
- [ ] Commit history clean
- [ ] Git tags created for release
- [ ] Release notes written

---

## 🎉 Go-Live

After all checks pass:

- [ ] Deploy to staging first (test environment)
- [ ] Run smoke tests on staging
- [ ] Get stakeholder approval
- [ ] Deploy to production
- [ ] Monitor logs for 24 hours
- [ ] Verify all features working
- [ ] Announce launch to users

---

## 📞 Support Contacts

- **Render Support**: support@render.com
- **Django Docs**: docs.djangoproject.com
- **React Docs**: react.dev
- **PostgreSQL Docs**: postgresql.org/docs

---

## 🚨 Emergency Contacts

- **Team Lead**: [Contact Info]
- **DevOps**: [Contact Info]
- **Database Admin**: [Contact Info]
- **Incident Response**: [Contact Info]

---

## ✅ Deployment Status

**Pre-Deployment**: ⏳ IN PROGRESS
**Staging Approval**: ⏳ PENDING
**Production Deployment**: ⏳ READY

---

**Checklist Completed By**: [Name]  
**Date**: [Date]  
**Time**: [Time]  
**Sign-off**: _______________

---

**Last Updated**: May 27, 2026  
**Platform**: Render.com  
**Next Review**: After first production deployment
