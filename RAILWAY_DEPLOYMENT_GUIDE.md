# FYP Management System - Railway Deployment Guide

## Step 1: Prepare Local Environment

```bash
# Clone or cd to your project
cd Desktop/PROJECTS/fyp

# Install dependencies
pip install -r requirements.txt

# Test locally
python app.py
# Should see: "Running on 0.0.0.0:5000"
```

## Step 2: Prepare Git Repository

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Prepare for Railway deployment"

# Push to GitHub/GitLab
git remote add origin https://github.com/YOUR-REPO.git
git push -u origin main
```

## Step 3: Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Authorize Railway to access your GitHub
5. Select your FYP repository

## Step 4: Configure Environment Variables

In Railway Dashboard → Your Project → Variables:

```
FLASK_ENV=production
SECRET_KEY=(Generate with: python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=(Your PostgreSQL URL)
ALLOWED_ORIGINS=https://your-app.up.railway.app
```

## Step 5: Add PostgreSQL Database

In Railway Dashboard:
1. Click "+ New Service"
2. Select "Database"
3. Choose "PostgreSQL"
4. Let Railway auto-fill DATABASE_URL

## Step 6: Deploy

Railway auto-deploys when you push to GitHub:

```bash
git push origin main
```

Watch deployment in Railway Dashboard:
- Build logs appear automatically
- Deployment shows progress
- Look for "✓ Deployment completed" message

## Step 7: Access Your App

Once deployed:
- Main URL: `https://your-app.up.railway.app`
- Health check: `https://your-app.up.railway.app/health`
- Dashboard: `https://your-app.up.railway.app/dashboard`

## Step 8: Verify WebSockets

Test WebSocket connection:
1. Open browser console (F12)
2. Go to dashboard
3. You should see: "Connected to real-time updates"
4. No errors in console

If not working, see "Troubleshooting WebSockets" below.

---

## Environment Variables Reference

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| FLASK_ENV | Yes | production | Enables production mode |
| SECRET_KEY | Yes | (32-char hex) | Session encryption |
| DATABASE_URL | Yes | postgresql://... | Database connection |
| PORT | Auto | 5000 | Server port (Railway sets this) |
| ALLOWED_ORIGINS | No | https://myapp.up.railway.app | CORS for WebSockets |

---

## Troubleshooting WebSockets

### Issue: "WebSocket connection failed"

**Check 1: Is it connecting?**
```bash
# In browser console on dashboard page
socket.connected  # Should be true
socket.id         # Should show socket ID
```

**Check 2: Check Railway logs**
```
# In Railway Dashboard → Logs
# Look for errors like:
# - "eventlet not installed"
# - "Connection refused"
# - "CORS origin not allowed"
```

**Solution:**
1. Ensure eventlet is in requirements.txt ✓
2. Set ALLOWED_ORIGINS env var to your domain ✓
3. Check Procfile uses `--worker-class eventlet` ✓

### Issue: "Dashboard not updating"

**Reason:** Real-time updates broken

**Solution:**
1. Refresh page
2. Check browser console for errors
3. Verify database is connected: `DATABASE_URL` is set
4. Check logs for database connection errors

### Issue: "502 Bad Gateway"

**Reason:** Application crashed

**Solutions:**
1. Check Railway Logs for crash details
2. Verify SECRET_KEY is set
3. Verify DATABASE_URL is correct
4. Ensure Python 3.11+ is in runtime.txt

---

## Performance Optimization

### For Railway with WebSockets:

**Procfile** (Current - Optimal):
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 backend.app:app
```

- `-w 1`: Single worker (eventlet handles concurrency)
- `eventlet`: Best for WebSockets
- `--timeout 120`: 2-minute timeout for long-running tasks

### If hitting limits:

Add more memory/CPU in Railway settings:
- Go to Settings → Resources
- Increase RAM or CPU as needed
- Auto-scaling available on Pro plan

---

## Monitoring Your Deployment

### Key Metrics to Watch:

1. **Build Time**: Should be < 5 minutes
2. **Deployment Success**: Green checkmark
3. **Memory Usage**: Should be < 500MB
4. **Error Rate**: Should be 0%

### View Logs:

```bash
# Real-time logs in Railway Dashboard
# Or use Railway CLI:

railway logs --follow
```

### Debug WebSocket Issues:

```bash
# Check if socket.io is accessible
curl https://your-app.up.railway.app/socket.io/
```

Should return HTML or socket.io data (not 404 or 500 error)

---

## Database Management

### First Time Setup:

1. Create admin user
2. Run migrations
3. Seed initial data

**Steps in Railway:**

1. Go to Deploy → Redeploy → Advanced Settings
2. Add pre-deploy command:
   ```
   python backend/scripts/create_admin.py
   ```

### Backup Database:

Railway PostgreSQL automatically backs up, but you can:

1. Export data from Railway Postgres
2. Use pg_dump:
   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```

---

## Security Checklist

Before going live:

- [ ] FLASK_ENV=production
- [ ] SECRET_KEY is strong (32 bytes)
- [ ] DATABASE_URL is secure
- [ ] ALLOWED_ORIGINS matches your domain
- [ ] Debug mode disabled
- [ ] SSL/HTTPS enabled (Railway auto-enables)
- [ ] Firewall rules configured
- [ ] Database credentials are secret

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| 502 Bad Gateway | App crashed | Check logs, verify env vars |
| WebSocket timeout | eventlet not installed | Ensure eventlet in requirements.txt |
| 404 on /socket.io | Bad Procfile | Use `gunicorn --worker-class eventlet` |
| Slow dashboard | N+1 queries | See PROFESSIONAL_SYSTEM_REVIEW.md |
| Static files not loading | Wrong path | Check template_folder & static_folder |

---

## Next Steps

1. ✓ Deployment ready
2. Monitor application for 24 hours
3. Set up error tracking (optional: Sentry)
4. Configure domain name (optional)
5. Implement CI/CD pipeline (optional)
6. Set up backups (Railway handles this)

---

**Deployment is complete! Your app is now live on Railway with WebSocket support.** 🚀
