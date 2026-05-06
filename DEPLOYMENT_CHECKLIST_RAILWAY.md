# FYP System - Production Deployment Checklist

Complete this before deploying to Railway.

---

## ✅ Backend Configuration

- [ ] `app.py` - Entry point configured correctly
  - [ ] Uses `socketio.run()` instead of `app.run()`
  - [ ] Reads PORT from `os.environ.get('PORT')`
  - [ ] Host is `0.0.0.0`
  - [ ] `use_reloader=False` for production

- [ ] `backend/app.py` - Flask app properly configured
  - [ ] SocketIO async mode configured (eventlet/gevent)
  - [ ] CORS_allowed_origins from environment variable
  - [ ] DATABASE_URL from environment
  - [ ] SECRET_KEY from environment (not hardcoded)
  - [ ] Debug mode disabled in production

---

## ✅ Deployment Files

- [ ] `Procfile` - Correct syntax
  - [ ] Uses `gunicorn --worker-class eventlet`
  - [ ] Uses PORT environment variable
  - [ ] Timeout set to 120 seconds
  - [ ] No hardcoded worker count (let Railway manage)

- [ ] `runtime.txt` - Python version
  - [ ] Version: `python-3.11` (not python-3.11.0)
  - [ ] Python 3.11+ confirmed compatible

- [ ] `requirements.txt` - All dependencies
  - [ ] eventlet >= 0.33.3 (for WebSockets)
  - [ ] python-socketio >= 5.9.0
  - [ ] gunicorn >= 21.2.0
  - [ ] Flask-SocketIO >= 5.3.4
  - [ ] Flask-CORS >= 4.0.0
  - [ ] All other dependencies present
  - [ ] No duplicate entries
  - [ ] Versions pinned (==, not >=)

- [ ] `.env.example` - Created
  - [ ] Template for all environment variables
  - [ ] Instructions for each variable
  - [ ] Safe default values

- [ ] `.gitignore` - Database files excluded
  - [ ] `*.db` (SQLite database)
  - [ ] `.env` (local secrets)
  - [ ] `__pycache__/`
  - [ ] `.venv/`
  - [ ] `logs/`

---

## ✅ Environment Variables

- [ ] FLASK_ENV = production
- [ ] SECRET_KEY = Set (32+ byte random string)
- [ ] DATABASE_URL = PostgreSQL URL (not SQLite)
- [ ] ALLOWED_ORIGINS = Your Railway domain
- [ ] PORT = (Will be set by Railway)
- [ ] Optional email variables configured

**Generate SECRET_KEY:**
```python
import secrets
secrets.token_hex(32)  # Copy this value to Railway
```

---

## ✅ Database Setup

- [ ] PostgreSQL database created (not SQLite)
- [ ] DATABASE_URL connection string tested locally
- [ ] Tables exist (migrations run if needed)
- [ ] Admin user exists

**For Railway:**
- [ ] Add PostgreSQL service
- [ ] Railway auto-fills DATABASE_URL
- [ ] Verify connection: `psql $DATABASE_URL`

---

## ✅ Frontend Configuration

- [ ] Templates use correct paths
  - [ ] `url_for()` used for all links
  - [ ] Static files in `frontend/static/`
  - [ ] Templates in `frontend/templates/`

- [ ] Static files
  - [ ] CSS/JS files referenced with `url_for('static', filename='...')`
  - [ ] No absolute paths
  - [ ] Images have correct paths

- [ ] WebSocket client (if using real-time updates)
  - [ ] Socket.IO client library included
  - [ ] Correct server URL (not localhost)
  - [ ] Reconnection logic present

---

## ✅ Security

- [ ] SECRET_KEY is secure (not default)
- [ ] DEBUG = False
- [ ] FLASK_ENV = production
- [ ] No hardcoded credentials in code
- [ ] CORS restricted to known domains
- [ ] HTTPS enabled (Railway auto-enables)
- [ ] Database password secure
- [ ] API keys in environment variables

---

## ✅ WebSocket Configuration

- [ ] `eventlet` installed (in requirements.txt)
- [ ] Procfile uses `--worker-class eventlet`
- [ ] SocketIO configured with proper async_mode
- [ ] CORS allows your domain
- [ ] Ping interval set (default: 30s)
- [ ] No "hardcoded localhost" in WebSocket URL

**Test:**
```javascript
// In browser console on /dashboard
socket.connected    // Should be true
socket.id          // Should show socket ID
socket.io.engine.readyState  // Should be 3 (connected)
```

---

## ✅ Logging & Monitoring

- [ ] Logging configured for production
- [ ] Error handlers in place
- [ ] No sensitive data in logs
- [ ] Log level set appropriately

**For Railway:**
- [ ] Logs viewable in Railway dashboard
- [ ] Error tracking (optional: Sentry)
- [ ] Performance monitoring (optional)

---

## ✅ Git & Repository

- [ ] Code pushed to GitHub
- [ ] `.gitignore` prevents secrets
- [ ] No `.env` file in repository
- [ ] Procfile in repository root
- [ ] runtime.txt in repository root
- [ ] requirements.txt in repository root

```bash
# Verify before pushing:
git status  # Only tracked files should appear
git log     # Commits present
```

---

## ✅ Local Testing

- [ ] App runs locally: `python app.py`
- [ ] No import errors
- [ ] Database connects (set DATABASE_URL locally or use SQLite)
- [ ] WebSockets work in browser console
- [ ] All pages load
- [ ] Forms submit correctly
- [ ] No 500 errors in logs

---

## ✅ Railway Setup

- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] PostgreSQL service added
- [ ] Environment variables configured
- [ ] Deploy key added to GitHub (if private repo)

---

## ✅ Deployment

- [ ] All checks above completed
- [ ] Commit final changes: `git add . && git commit -m "Production ready"`
- [ ] Push to main: `git push origin main`
- [ ] Watch Railway dashboard for deploy
- [ ] Verify "Deployment Success" status
- [ ] App accessible at Railway URL

---

## ✅ Post-Deployment Verification

**After deployment:**

- [ ] App loads: `https://your-app.up.railway.app`
- [ ] Health check passes: `https://your-app.up.railway.app/health`
- [ ] Login page works
- [ ] Can create account
- [ ] Dashboard loads
- [ ] WebSocket connects (check browser console)
- [ ] Real-time updates work
- [ ] No 500 errors in Railway logs
- [ ] No WebSocket connection errors

**Test WebSocket:**
```javascript
// Paste in browser console on dashboard
console.log('Connected:', socket.connected);
console.log('Socket ID:', socket.id);
socket.emit('test', {msg: 'Hello'});
```

---

## ✅ Troubleshooting

If deployment fails:

1. **Check Railway Logs:**
   ```
   Railway Dashboard → Your App → Logs
   ```

2. **Common Issues:**
   - [ ] eventlet not installed → Add to requirements.txt
   - [ ] SECRET_KEY not set → Set in Railway variables
   - [ ] DATABASE_URL invalid → Verify PostgreSQL connection
   - [ ] 502 Bad Gateway → Check app logs for crashes
   - [ ] WebSocket fails → Check ALLOWED_ORIGINS, Procfile

3. **Re-deploy:**
   ```bash
   git commit --allow-empty -m "Redeploy"
   git push origin main
   ```

---

## ✅ Performance & Optimization

After going live:

- [ ] Monitor error rate (should be 0%)
- [ ] Check memory usage (should be < 500MB)
- [ ] Monitor CPU usage
- [ ] Test dashboard load time (should be < 2s)
- [ ] Verify WebSocket latency (should be < 100ms)

---

## ✅ Maintenance

- [ ] Set up automatic backups
- [ ] Monitor error logs daily (first week)
- [ ] Test database restore process
- [ ] Document deployment steps
- [ ] Set up CI/CD if using multiple environments

---

## 🎯 Final Checklist Before Production

```
System Ready for Production?

□ All checks above = ✓ Yes
□ App deployed = ✓ Yes  
□ WebSockets working = ✓ Yes
□ Database connected = ✓ Yes
□ No errors in logs = ✓ Yes
□ Performance acceptable = ✓ Yes

APPROVAL: _________________ Date: _________
```

---

**Status:** ✅ Ready for deployment when all items checked

**Help:** Refer to RAILWAY_DEPLOYMENT_GUIDE.md for detailed setup instructions
