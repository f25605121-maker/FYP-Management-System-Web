# FYP System on Railway - Complete Setup Guide

Step-by-step guide to deploy your FYP Management System on Railway.app

---

## Part 1: Prepare Your GitHub Repository

### Step 1.1: Verify repository readiness

Your repository should contain:

```
fyp/
├── app.py                          ✓ Entry point
├── requirements.txt                ✓ Dependencies
├── runtime.txt                     ✓ Python version
├── Procfile                        ✓ Server config
├── .env.example                    ✓ Env template
├── .gitignore                      ✓ Excludes secrets
├── backend/
│   ├── app.py                      ✓ Flask app
│   └── ...
├── frontend/
│   ├── templates/
│   └── static/
└── README.md                       ✓ Documentation
```

### Step 1.2: Ensure .gitignore excludes secrets

**Important: Your .gitignore should have:**

```gitignore
.env
.env.local
*.db
__pycache__/
.venv/
venv/
instance/
*.log
.DS_Store
```

### Step 1.3: Commit and push to GitHub

```bash
cd Desktop/PROJECTS/fyp

# If not a git repo yet:
git init
git add .
git commit -m "Initial commit: FYP system ready for Railway"

# Set up remote (if not done)
# Go to GitHub.com, create new repo, then:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

---

## Part 2: Set Up Railway Project

### Step 2.1: Create Railway account

1. Go to https://railway.app
2. Click "Start for free"
3. Sign in with GitHub (recommended) or Email
4. Grant Railway access to your GitHub

### Step 2.2: Create new project

1. In Railway Dashboard, click "+ New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access GitHub
4. Search and select your FYP repository
5. Click "Deploy Now"

**Railway will:**
- Detect Python app from requirements.txt
- Start build process
- Show build logs in real-time

---

## Part 3: Configure Database

### Step 3.1: Add PostgreSQL service

1. In Railway Project Dashboard
2. Click "+ New Service"
3. Select "Database"
4. Choose "PostgreSQL"
5. Click "Create"

**Railway automatically:**
- Provisions PostgreSQL instance
- Generates secure credentials
- Sets DATABASE_URL environment variable

### Step 3.2: Verify database connection

In Railway Dashboard:
1. Click your app (not the database)
2. Go to "Variables" tab
3. Look for `DATABASE_URL` in environment variables
4. Should show: `postgresql://[user]:[pass]@[host]:[port]/[db]`

---

## Part 4: Configure Environment Variables

### Step 4.1: Access Variables settings

1. Railway Dashboard → Your App
2. Click "Variables" tab
3. You should see `DATABASE_URL` (auto-set by PostgreSQL service)

### Step 4.2: Generate SECRET_KEY

Open Python locally and generate:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Output example: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Step 4.3: Add environment variables

In Railway Variables tab, click "Add" and add:

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `(paste from Step 4.2)` |
| `ALLOWED_ORIGINS` | `https://your-app.up.railway.app` |
| `ADMIN_EMAIL` | `admin@example.com` |
| `ADMIN_PASSWORD` | `StrongPassword123!` |
| `DEBUG` | `False` |

**Optional but recommended:**

| Variable | Value |
|----------|-------|
| `MAIL_SERVER` | `smtp.gmail.com` |
| `MAIL_PORT` | `587` |
| `MAIL_USERNAME` | `your-email@gmail.com` |
| `MAIL_PASSWORD` | `(app-specific password from Gmail)` |

### Step 4.4: Save variables

Variables are saved automatically. Click outside the field or hit Enter.

---

## Part 5: Verify Deployment Files

Railway detects your app type from these files (already prepared):

### Check 1: Procfile

```bash
# From your repo, verify:
cat Procfile
```

Should contain:
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - backend.app:app
```

### Check 2: runtime.txt

```bash
cat runtime.txt
```

Should contain:
```
python-3.11
```

### Check 3: requirements.txt

```bash
grep -E "eventlet|SocketIO|gunicorn" requirements.txt
```

Should show:
```
gunicorn==21.2.0
Flask-SocketIO==5.3.4
eventlet==0.33.3
```

---

## Part 6: Trigger Deployment

### Step 6.1: Manual deployment

If auto-deploy didn't trigger:

1. In Railway Dashboard, click your app
2. Click "Deployments" tab
3. Click "Deploy" button (or right-click, "Redeploy")

Railway starts building your app.

### Step 6.2: Monitor build

Watch the build logs:

```
[Build] Python 3.11 selected
[Build] Building with pip...
[Build] Installing requirements.txt...
[Build] eventlet 0.33.3 - OK
[Build] Flask 3.0.2 - OK
[Build] ... (other packages)
[Build] Build succeeded!
[Deploy] Starting your application...
[Deploy] 2024-01-15 10:30:45 | INFO | Starting application...
[Deploy] 2024-01-15 10:30:46 | ✓ Using eventlet async_mode
[Deploy] 2024-01-15 10:30:47 | Running on http://0.0.0.0:5000
```

### Step 6.3: Wait for "Deployment Success"

Green checkmark means:
- ✓ Build completed
- ✓ App started
- ✓ Ready to serve requests

---

## Part 7: Access Your Application

### Step 7.1: Find your app URL

In Railway Dashboard:
1. Click "Deployments"
2. Look for "Status: Success"
3. Find button with public domain (usually green)
4. Example: `https://fyp-system-abc123.up.railway.app`

### Step 7.2: Test the app

Open in browser:
```
https://your-app.up.railway.app
```

You should see:
- ✓ FYP Login page loads
- ✓ No 502 or 500 errors
- ✓ CSS/images load correctly

---

## Part 8: Verify Core Functionality

### Test 1: Health check

```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test 2: Login

1. Go to app URL
2. Click "Sign Up"
3. Create test account
4. Login

**Verify:**
- ✓ Form submits
- ✓ No database errors
- ✓ Redirected to dashboard

### Test 3: WebSocket connection

1. Open browser (F12)
2. Go to Console tab
3. On dashboard, paste:

```javascript
socket.connected
```

Should return: `true`

If returns `false` or `undefined`:
- Check ALLOWED_ORIGINS (see troubleshooting below)
- Check Railway logs

---

## Part 9: Monitor Your Application

### View Logs

**In Railway Dashboard:**
1. Click your app
2. Go to "Logs" tab
3. See real-time application logs

**Or via CLI:**
```bash
railway logs --follow
```

### Check Metrics

1. Click your app
2. Go to "Metrics" tab
3. Monitor:
   - [ ] CPU usage (should be < 50%)
   - [ ] Memory (should be < 300MB)
   - [ ] Disk I/O
   - [ ] Network

### Set Up Alerts (Optional)

1. Railway Dashboard → Settings
2. Click "Notifications"
3. Enable alerts for crashes/deployments

---

## Part 10: Custom Domain (Optional)

### Add custom domain

1. Railway Dashboard → Settings
2. Click "Custom Domain"
3. Enter your domain: `fyp.yourdomain.com`
4. Add CNAME record to your DNS provider
5. Railway auto-enables SSL

---

## Troubleshooting Deployment Issues

### Issue: "502 Bad Gateway"

**Check logs:**
```bash
railway logs
```

**Common causes:**

1. **Missing eventlet**
   ```
   ERROR: No module named 'eventlet'
   ```
   Fix:
   - Verify requirements.txt has `eventlet==0.33.3`
   - Push to GitHub
   - Redeploy

2. **Wrong worker class**
   ```
   ERROR: eventlet not specified in Procfile
   ```
   Fix:
   - Procfile must have: `--worker-class eventlet -w 1`
   - Push and redeploy

3. **Missing SECRET_KEY**
   ```
   ERROR: SECRET_KEY not set
   ```
   Fix:
   - Go to Variables tab
   - Add SECRET_KEY (see Part 4)
   - Redeploy

### Issue: "WebSocket connection failed"

**Check Railway logs for:**
```
CORS policy violation
```

**Fix:**
1. Go to Variables tab
2. Check ALLOWED_ORIGINS = your domain
3. Format: `https://your-app.up.railway.app`
4. Redeploy

### Issue: "Database connection refused"

**Verify:**
1. PostgreSQL service exists (see Railway dashboard)
2. DATABASE_URL set in Variables
3. Connection string valid

**Test:**
```bash
# Check if you can connect locally
psql postgresql://user:pass@host:port/db
```

### Issue: "Application not responding"

**Likely cause:** High memory/CPU usage

**Check Metrics tab:**
- If memory > 500MB → code has memory leak
- If CPU stuck high → infinite loop or too many queries

**Fix:**
1. Check backend/app.py for N+1 queries
2. Check for unclosed database connections
3. Optimize code
4. Redeploy

---

## Maintenance Tasks

### Daily

1. Check logs for errors
2. Monitor memory/CPU usage
3. Verify dashboard loads

### Weekly

1. Backup database (optional - Railway does this)
2. Review error logs
3. Test critical features

### Monthly

1. Update dependencies (run: `pip list --outdated`)
2. Test disaster recovery (database restore)
3. Review security settings

---

## Restart/Redeploy

### Restart without code changes

1. Railway Dashboard → Your App
2. Click "Deployments"
3. Right-click latest deployment
4. Click "Restart"

### Full redeploy with new code

```bash
# Make changes locally
git add .
git commit -m "Your change"
git push origin main

# Railway auto-deploys on push
# Or manually trigger:
# Railway Dashboard → Deployments → Deploy button
```

---

## Access Database via Terminal

### Using Railway CLI

```bash
# Login
railway login

# Connect to database
railway connect postgres

# Or use psql directly
psql $DATABASE_URL
```

### From Python

```python
from backend.app import app, db

with app.app_context():
    # Query database
    from backend.models import User
    users = db.session.query(User).all()
    for user in users:
        print(user.email)
```

---

## Backup & Restore

### Automatic backups

Railway PostgreSQL automatically backs up.

### Manual backup

```bash
pg_dump $DATABASE_URL > backup.sql
```

### Restore

```bash
psql $DATABASE_URL < backup.sql
```

---

## Security Checklist

- [ ] FLASK_ENV = production
- [ ] SECRET_KEY = strong (32+ bytes)
- [ ] DEBUG = False
- [ ] ALLOWED_ORIGINS = your domain (not *)
- [ ] Database password = secure
- [ ] API keys in environment variables (not code)
- [ ] .env file not in Git
- [ ] SSL/HTTPS enabled (Railway auto-enables)

---

## Performance Optimization

### For better performance:

1. **Upgrade plan** (Railway Dashboard → Settings → Resources)
   - More RAM
   - More CPU cores
   - Auto-scaling (Pro plan)

2. **Optimize code**
   - Fix N+1 queries (see professional review doc)
   - Cache frequently accessed data
   - Use indexes on database

3. **Monitor**
   - Check Metrics tab daily
   - Alert on high memory
   - Set dashboard refresh interval

---

## Success Indicators

Your deployment is successful when:

```
✓ App loads without errors
✓ Health check returns 200
✓ Login works
✓ Dashboard shows data
✓ WebSocket connected (socket.connected = true)
✓ Real-time updates work
✓ No 500 errors in logs
✓ Memory < 300MB
✓ CPU < 50%
✓ Response time < 1 second
```

---

## Next Steps

1. ✓ Deploy to Railway
2. Monitor for 24 hours
3. Gather user feedback
4. Fix any issues
5. Consider:
   - Custom domain
   - Error tracking (Sentry)
   - Performance monitoring
   - Database backups strategy

---

## Help & Support

- **Railway Docs:** https://docs.railway.app
- **Railway Support:** https://railway.app/support
- **GitHub Issues:** Your repo issues tab
- **FYP Docs:** See RAILWAY_DEPLOYMENT_GUIDE.md

---

**🚀 Your FYP system is now live on Railway!**

Monitor it regularly, gather feedback, and iterate. Good luck! 🎉
