# FYP System - Local Production Testing Guide

Before deploying to Railway, test the production configuration locally to catch issues early.

---

## Prerequisites

- Python 3.11+ installed
- `requirements.txt` dependencies installed
- Git repository ready
- `.env` file configured (copy from .env.example)

---

## Step 1: Prepare Local Environment

### 1.1 Copy environment template

```bash
cd Desktop/PROJECTS/fyp
cp .env.example .env
```

### 1.2 Edit .env for local testing

**Key changes for local testing:**

```env
FLASK_ENV=production
SECRET_KEY=test-secret-key-min-32-chars-long-for-testing
DEBUG=False
PORT=5000
DATABASE_URL=sqlite:///./fyp.db  # Use SQLite locally (not prod PostgreSQL)
ALLOWED_ORIGINS=http://localhost:5000,http://127.0.0.1:5000
```

### 1.3 Install dependencies

```bash
pip install -r requirements.txt
```

**Verify eventlet installed:**
```bash
python -c "import eventlet; print(f'✓ eventlet {eventlet.__version__}')"
```

---

## Step 2: Verify Production Configuration

### 2.1 Check app.py entry point

```bash
python -c "import app; print('✓ app.py imports successfully')"
```

### 2.2 Check backend app configuration

```bash
python -c "from backend.app import app, socketio; print(f'✓ Flask app initialized'); print(f'✓ SocketIO initialized')"
```

### 2.3 Verify Procfile correctness

```bash
cat Procfile
# Should show:
# web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - backend.app:app
```

---

## Step 3: Start Application in Production Mode

### 3.1 Run via entry point (as Railway will)

```bash
python app.py
```

**Expected output:**
```
[FYP] Starting application...
[FYP] Environment: PRODUCTION
[FYP] Running on Railway: False
[FYP] Listening on 0.0.0.0:5000
[FYP] Debug mode: False
 * Serving Flask app 'app'
 * Running on http://0.0.0.0:5000
```

✓ **Success:** App started without errors

---

## Step 4: Test Application Endpoints

**In another terminal:**

### 4.1 Health check

```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{"status": "healthy"}
```

### 4.2 Home page

```bash
curl http://localhost:5000/
```

**Should return HTML** (not error)

### 4.3 Login page

```bash
curl http://localhost:5000/login
```

**Should return HTML**

---

## Step 5: Test WebSocket Connection

### 5.1 Open browser

Navigate to: `http://localhost:5000`

### 5.2 Open Developer Console (F12)

Click **Console** tab

### 5.3 Check WebSocket connection

Paste this in console:

```javascript
// Check if socket.io is loaded
console.log('Socket.IO version:', io?.version || 'not loaded');

// Attempt connection
socket.on('connect', () => {
    console.log('✓ Connected! Socket ID:', socket.id);
});

socket.on('disconnect', () => {
    console.log('✗ Disconnected');
});

socket.on('error', (error) => {
    console.error('✗ Socket error:', error);
});
```

**Expected:**
- `✓ Connected! Socket ID: [hex-string]` appears
- No error messages
- Dashboard updates show real-time data

### 5.4 Test WebSocket message

```javascript
// In console, after connected
socket.emit('test_event', {message: 'Hello from client'});
```

---

## Step 6: Test Authentication & Features

### 6.1 Create a test account

1. Click "Sign Up"
2. Fill in student details
3. Submit

**Verify:**
- [ ] No errors
- [ ] Redirected to login
- [ ] Can login with new account

### 6.2 Test dashboard

1. Login
2. Go to dashboard
3. Look for real-time updates

**Verify:**
- [ ] Dashboard loads
- [ ] No console errors
- [ ] WebSocket shows connected
- [ ] Data appears correctly

### 6.3 Test project proposal

1. Click "Propose Project"
2. Fill form
3. Submit

**Verify:**
- [ ] No 500 errors
- [ ] Proposal appears in list
- [ ] Real-time notifications show (if configured)

---

## Step 7: Verify Production Settings

### 7.1 Check environment

```bash
# In console after app started
python -c "
import os
print('FLASK_ENV:', os.environ.get('FLASK_ENV'))
print('DEBUG:', os.environ.get('DEBUG'))
print('SECRET_KEY:', 'SET' if os.environ.get('SECRET_KEY') else 'NOT SET')
print('DATABASE_URL:', 'SET' if os.environ.get('DATABASE_URL') else 'NOT SET')
"
```

### 7.2 Verify no debug mode

```bash
# App shouldn't auto-reload on file changes
# Edit a file and verify app doesn't restart
# (Should show no "restarting" messages)
```

### 7.3 Check logging output

Look for these in app logs:

✓ Should see:
```
[FYP] Environment: PRODUCTION
[FYP] Debug mode: False
✓ Using eventlet async_mode for SocketIO
```

✗ Should NOT see:
```
- WARNING: Use a production WSGI server
- Serving Flask app in debug mode
```

---

## Step 8: Performance Testing

### 8.1 Monitor resource usage

While app is running:

```bash
# Check memory usage (Linux/Mac)
ps aux | grep python

# Check on Windows - open Task Manager
# Look for python.exe process
# Memory should be < 200MB for idle
```

### 8.2 Test concurrent connections

```bash
# Open multiple browser tabs to dashboard
# All should show connected
# Memory shouldn't spike significantly
```

### 8.3 Test under load (optional)

```bash
# Simple load test
ab -n 100 -c 10 http://localhost:5000/
```

---

## Step 9: Verify Static Files & Templates

### 9.1 Check CSS/JS loads

1. Inspect page in browser (F12)
2. Go to **Network** tab
3. Refresh page (F5)

**Verify:**
- [ ] CSS files load (status 200)
- [ ] JS files load (status 200)
- [ ] Images load (status 200)
- [ ] No 404 errors

### 9.2 Check template rendering

1. View page source (Ctrl+U)
2. Verify proper HTML

---

## Step 10: Error Handling Tests

### 10.1 Test 404 error

```bash
curl http://localhost:5000/nonexistent
```

**Should return 404 page**, not raw error

### 10.2 Test database error

Stop the database (or disconnect) and try to load dashboard.

**Should show:**
- [ ] Error message (not 500 page dump)
- [ ] Helpful message: "Database connection failed"

### 10.3 Check error logs

App logs should show errors clearly:

```
ERROR: Database connection failed: [specific error]
```

---

## Step 11: Production Readiness Checklist

Before deploying, verify:

```
✓ App starts with FLASK_ENV=production
✓ No warnings about production WSGI server
✓ WebSockets connect successfully
✓ All pages load
✓ Database operations work
✓ File uploads work (if enabled)
✓ Forms submit correctly
✓ No 500 errors in logs
✓ Static files load (CSS/JS/images)
✓ Templates render properly
✓ Error pages show (404, 500)
✓ Email works (if configured)
✓ Authentication works
✓ Real-time updates work
✓ Memory usage < 300MB
```

---

## Step 12: Prepare for Railway Deployment

### 12.1 Commit changes

```bash
git add .
git commit -m "Production testing complete - ready for Railway"
```

### 12.2 Verify git status

```bash
git status
# Should show: "On branch main. Your branch is ahead of 'origin/main' by 1 commit."
```

### 12.3 Push to GitHub

```bash
git push origin main
```

---

## Troubleshooting

### Issue: App won't start

**Error:** `ModuleNotFoundError: No module named 'eventlet'`

**Solution:**
```bash
pip install -r requirements.txt
pip install eventlet==0.33.3
```

### Issue: WebSocket won't connect

**Error:** `WebSocket connection failed`

**Check:**
1. App is running: `curl http://localhost:5000/`
2. WebSocket server is accessible: `curl http://localhost:5000/socket.io/`
3. No firewall blocking port 5000

**Solution:**
```bash
# Check if port 5000 is in use
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill process if needed
kill -9 <PID>  # Get PID from above
```

### Issue: Static files not loading

**Error:** CSS/JS files show 404 in Network tab

**Check:**
1. Files exist in `frontend/static/`
2. Template paths correct: `url_for('static', filename='...')`
3. No hardcoded paths like `/static/`

**Solution:**
```bash
ls -la frontend/static/  # Verify files exist
```

### Issue: Database errors

**Error:** `no such table: user`

**Solution:**
```bash
# Create tables
python -c "from backend.app import app, db; db.create_all()"
```

---

## Next Steps

If all tests pass:

1. ✓ Push to GitHub
2. ✓ Go to Railway.app
3. ✓ Connect your GitHub repo
4. ✓ Configure environment variables
5. ✓ Deploy
6. ✓ Monitor logs

**Deployment is ready!** 🚀
