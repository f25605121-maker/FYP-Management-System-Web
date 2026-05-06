# FYP System - WebSocket Production Troubleshooting Guide

Real-time WebSocket functionality is critical for live dashboard updates and notifications. This guide helps diagnose and fix WebSocket issues in production.

---

## Quick Diagnosis

### Is WebSocket working?

**In browser console on dashboard:**

```javascript
// Test 1: Is socket.io loaded?
console.log(typeof io);  // Should print: "object"

// Test 2: Is socket connected?
console.log(socket.connected);  // Should print: true

// Test 3: What's the socket ID?
console.log(socket.id);  // Should print: hex-string like "abc123def456"

// Test 4: Check connection state
console.log(socket.io.engine.readyState);  
// 0 = OPENING, 1 = OPEN, 2 = CLOSING, 3 = CLOSED
// Should be 1 (OPEN) or 3 (CLOSED waiting for reconnect)
```

**Results:**
- ✓ All tests pass → WebSocket working
- ✗ Any test fails → See troubleshooting sections below

---

## Issue 1: "WebSocket connection refused"

### Error Message
```
WebSocket connection to 'wss://your-app.up.railway.app/socket.io/' failed: Error in connection establishment
```

### Causes & Solutions

**1.1 Server not running or crashed**

Check:
```bash
# In Railway dashboard
# Go to: Logs tab
# Look for: crash messages or 502 errors
```

Solution:
- [ ] Verify Procfile uses eventlet: `--worker-class eventlet`
- [ ] Check SECRET_KEY is set
- [ ] Check DATABASE_URL is valid
- [ ] Restart deployment: GitHub push triggers redeploy

**1.2 Wrong domain/port**

Check WebSocket URL in browser console:
```javascript
console.log(socket.io.uri);
```

Solution:
- [ ] If shows `http://localhost:5000`, WebSocket client using wrong URL
- [ ] Should be `https://your-app.up.railway.app` (auto-detected from window.location)
- [ ] Check template: WebSocket URL should NOT be hardcoded

**1.3 Firewall/Network blocking**

Check network tab (F12 → Network):
- [ ] Look for `socket.io` requests
- [ ] Should show status 101 (Switching Protocols) or 200 (polling fallback)
- [ ] If shows ERR_NAME_NOT_RESOLVED → DNS issue
- [ ] If times out → Firewall blocking

Solution:
- [ ] Contact Railway support for firewall rules
- [ ] Verify ALLOWED_ORIGINS doesn't block your domain

**1.4 CORS misconfiguration**

Check Railway logs:
```
ERROR: CORS policy: The value of the 'Access-Control-Allow-Origin' header is...
```

Solution in backend/app.py:
```python
# Current (wrong):
socketio = SocketIO(app, cors_allowed_origins="*")

# Should be:
socketio = SocketIO(app, cors_allowed_origins=[
    os.environ.get('FRONTEND_URL', 'http://localhost:5000')
])
```

Set in Railway variables:
```
FRONTEND_URL=https://your-app.up.railway.app
```

---

## Issue 2: "Connect timeout"

### Error Message
```
Socket.IO error: Error: connect timeout
```

### Causes & Solutions

**2.1 Server too slow to respond**

Check:
- [ ] Dashboard performance (check N+1 queries)
- [ ] Database query time
- [ ] Memory usage

Solution:
- [ ] Check Railway resource limits
- [ ] Optimize database queries
- [ ] Increase timeout in client code:

```javascript
// frontend/static/js/realtime-updates.js
const socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5,
    transports: ['websocket', 'polling'],
    upgrade: true,
    timeout: 60000  // 60 second timeout (increase if needed)
});
```

**2.2 Eventlet not installed**

Check Railway logs:
```
ERROR: eventlet module not found
```

Solution:
- [ ] Verify in requirements.txt: `eventlet==0.33.3`
- [ ] Verify Procfile: `--worker-class eventlet`
- [ ] Redeploy: `git push origin main`

**2.3 Multiple workers with eventlet**

Error in logs:
```
WARNING: Multiple workers with eventlet; WebSocket may fail
```

Solution:
- [ ] Change Procfile from: `--workers 2` or `-w 2`
- [ ] To: `-w 1` (single worker only)
- [ ] Procfile should be:
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT --timeout 120 backend.app:app
```

---

## Issue 3: "Connection drops frequently"

### Error Message
```javascript
socket.on('disconnect', (reason) => {
    console.log('Disconnected:', reason);
    // Shows: "transport close", "server namespace disconnect", etc.
});
```

### Causes & Solutions

**3.1 Ping/pong timeout**

Normal behavior: Socket.IO sends pings every 30s, expects pong within 60s

If disconnecting frequently:
- [ ] Network is unstable
- [ ] Server under heavy load
- [ ] Firewall dropping idle connections

Solution in backend/app.py:
```python
socketio = SocketIO(app,
    ping_interval=30,    # Send ping every 30s
    ping_timeout=60,     # Wait 60s for response
    # Increase these for unreliable networks:
    ping_interval=60,    # Every 60s
    ping_timeout=120,    # Wait 120s
)
```

Then redeploy.

**3.2 Server memory leak**

If disconnects increase over time:

Check Railway dashboard:
- [ ] Memory usage climbing → memory leak
- [ ] Look for unreleased database connections

Solution:
- [ ] Check backend/app.py for:
  - [ ] Unclosed database connections
  - [ ] Event handlers not cleaning up
  - [ ] Memory accumulation

**3.3 Session/token expiration**

If disconnects after ~24 hours:

Check:
```python
# backend/app.py
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
```

Solution:
- [ ] Increase session lifetime if needed
- [ ] Or implement refresh token logic

**3.4 Browser tab inactive**

Browsers suspend timers on inactive tabs.

Solution: Add to frontend code:
```javascript
// Keep connection alive when tab inactive
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Tab hidden - WebSocket may pause');
    } else {
        console.log('Tab visible - reconnecting...');
        socket.connect();
    }
});
```

---

## Issue 4: "Real-time updates not working"

### Symptoms
- Dashboard loads
- WebSocket connected (console shows `socket.connected = true`)
- But data doesn't update in real-time
- Manual refresh needed to see changes

### Diagnosis

```javascript
// In browser console
socket.on('update_notification', (data) => {
    console.log('Received update:', data);
});

// Or test with custom event
socket.emit('test_event', {msg: 'hello'});
socket.on('test_response', (data) => {
    console.log('Received response:', data);
});
```

### Solutions

**4.1 Event not being emitted**

Check backend code for event broadcast:

```python
# backend/app.py - should have something like:
@socketio.on('connect')
def handle_connect():
    emit('notification', {'msg': 'User connected'})  # This sends to client

# Emit to all clients:
socketio.emit('notification', {'msg': 'Update'})

# Emit to specific room:
socketio.emit('notification', {'msg': 'Update'}, room=room_id)
```

If events not in code → add them

**4.2 Event not reaching client**

Check browser console (Network tab):

1. Look for WebSocket frame data
2. Should show incoming messages like:
   ```
   {"type": "message", "data": [...]}
   ```

If not showing:
- [ ] Event name mismatch (frontend expecting 'update_notification' but backend emitting 'notification')
- [ ] Event filtered by CORS
- [ ] Room/namespace mismatch

**4.3 JavaScript error in event handler**

Check console for errors when data arrives.

Example problem:
```javascript
// Frontend listening but error in handler
socket.on('update_notification', (data) => {
    console.log(data.nonexistent.property);  // ERROR! undefined.property
    // Handler breaks, stops receiving updates
});
```

Solution:
```javascript
socket.on('update_notification', (data) => {
    if (data && data.message) {
        console.log(data.message);
    }
});
```

**4.4 Database connection broken**

If no events being emitted from backend:

Check Railway logs:
```
ERROR: Database connection failed
ERROR: No attribute 'query'
```

Solution:
- [ ] Verify DATABASE_URL in Railway variables
- [ ] Test: `psql $DATABASE_URL` (verify connection)
- [ ] Restart app: GitHub push

---

## Issue 5: "Memory usage high / app crashes"

### Symptoms
- WebSocket working initially
- After hours: memory climbing
- Eventually: app crashes or becomes slow

### Diagnosis

Check Railway Metrics:
1. Go to Railway Dashboard
2. Click your app
3. Go to Metrics tab
4. Check Memory graph over time

If memory climbing → memory leak

### Solutions

**5.1 Unclosed database connections**

```python
# Problem:
def handle_event():
    db.session.query(User).all()  # Not closed!

# Solution:
def handle_event():
    try:
        users = db.session.query(User).all()
        return users
    finally:
        db.session.close()  # Always close
```

**5.2 Socket event listener accumulation**

```javascript
// Problem: registering multiple listeners
for (let i = 0; i < 100; i++) {
    socket.on('update', (data) => { /* ... */ });  // 100 listeners!
}

// Solution: register once or use off()
socket.off('update');  // Remove old listener
socket.on('update', (data) => { /* ... */ });  # Then register once
```

**5.3 Memory limit reached**

Check Railway settings:
- [ ] Current plan memory limit
- [ ] If consistently high: upgrade plan
- [ ] Or optimize code to use less memory

---

## Issue 6: "502 Bad Gateway"

### After WebSocket changes

Procfile wrong:
```
# Wrong (standard gunicorn):
web: gunicorn backend.app:app

# Correct (eventlet worker):
web: gunicorn --worker-class eventlet -w 1 backend.app:app
```

Solution:
1. Fix Procfile
2. Git push to redeploy
3. Wait 2-3 minutes

---

## Debugging Commands

### Check WebSocket is accessible

```bash
# From terminal:
curl -i https://your-app.up.railway.app/socket.io/

# Should return:
# HTTP/2 200 or 426 (Upgrade Required)
# NOT 404 or 502
```

### View Railway logs real-time

```bash
# If Railway CLI installed:
railway logs --follow

# Or use dashboard:
# Railway → Your App → Logs tab
```

### Test from local

```bash
# Set up local to match production
export FLASK_ENV=production
export ALLOWED_ORIGINS=http://localhost:5000
python app.py

# In browser:
# http://localhost:5000
# F12 → Console
# Check: socket.connected
```

---

## Performance Monitoring

### Monitor WebSocket health

```javascript
// Add to frontend code
setInterval(() => {
    console.log({
        connected: socket.connected,
        socketId: socket.id,
        latency: socket.io.engine.transport.latencyBound || 'N/A',
        transport: socket.io.engine.transport.name
    });
}, 30000);  // Every 30 seconds
```

### Check latency

```javascript
// Measure roundtrip time
const start = Date.now();
socket.emit('ping', {}, () => {
    const latency = Date.now() - start;
    console.log(`Latency: ${latency}ms`);
});
```

---

## WebSocket Fallback (Polling)

If WebSocket fails, Socket.IO falls back to HTTP polling.

Polling is less efficient but ensures connection.

Check transport:
```javascript
console.log(socket.io.engine.transport.name);
// "websocket" = good
// "polling" = fallback (slower)
```

This is OK temporarily, but investigate why WebSocket isn't working.

---

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `ECONNREFUSED` | Server not running | Check Railway logs, redeploy |
| `ETIMEDOUT` | Server too slow | Optimize code, increase timeout |
| `ENOTFOUND` | DNS error | Wrong domain in ALLOWED_ORIGINS |
| `CORS policy` | Domain mismatch | Set ALLOWED_ORIGINS correctly |
| `socket.emit is not a function` | Socket not loaded | Ensure socket.io client loaded |
| `Cannot read property of undefined` | Event data structure wrong | Add null checks in handler |

---

## Final Checklist

WebSocket production ready when:

- [ ] Procfile uses `--worker-class eventlet -w 1`
- [ ] requirements.txt has eventlet==0.33.3
- [ ] ALLOWED_ORIGINS set to your domain
- [ ] ping_interval and ping_timeout configured
- [ ] No console errors on dashboard
- [ ] `socket.connected === true` in console
- [ ] Real-time updates appear instantly
- [ ] No 502 errors in logs
- [ ] Memory stable (not climbing)
- [ ] Latency < 100ms

---

**WebSocket troubleshooting complete!** 🚀

For more help, check Railway logs or contact support.
