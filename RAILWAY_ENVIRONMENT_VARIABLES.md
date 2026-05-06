# Railway Environment Variables - Complete Reference

Detailed guide to every environment variable used by the FYP system on Railway.

---

## How to Set Variables in Railway

### Method 1: Railway Dashboard (Easiest)

1. Go to https://railway.app
2. Click your project
3. Click "Variables" tab
4. Click "+ New Variable"
5. Enter Name and Value
6. Press Enter

### Method 2: Railway CLI

```bash
# Set variable
railway variables set FLASK_ENV production

# View all variables
railway variables

# Connect with psql to see DATABASE_URL
echo $DATABASE_URL
```

---

## Required Variables

Must be set before app works in production.

### FLASK_ENV
**Purpose:** Enables production mode

**Value:** `production`

**Where it's used:**
- `app.py`: Disables debug mode
- `backend/app.py`: Disables verbose logging
- Error handling: Shows minimal error info

```bash
# Example
FLASK_ENV=production
```

### SECRET_KEY
**Purpose:** Encrypts session cookies and CSRF tokens

**Value:** Random 32-byte hex string

**Generate:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Example output:**
```
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

**Copy entire output to Railway:**
```bash
SECRET_KEY=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

**Where it's used:**
- Session encryption (user login)
- CSRF token generation
- Form validation

### DATABASE_URL
**Purpose:** PostgreSQL database connection string

**Automatic:** Railway sets this automatically when you add PostgreSQL service

**Format:**
```
postgresql://username:password@hostname:port/database
```

**Example:**
```
postgresql://postgres:secretpass123@db.example.com:5432/railway
```

**DO NOT:**
- ✗ Create manually (Railway creates it)
- ✗ Share this URL publicly
- ✗ Commit to Git

**Where it's used:**
- `backend/app.py`: Database connection
- SQLAlchemy ORM: Table creation and queries
- All database operations

---

## Highly Recommended Variables

Should always be set in production.

### ALLOWED_ORIGINS
**Purpose:** CORS configuration for WebSockets

**Value:** Your Railway domain

**Format:**
```
https://your-app.up.railway.app
```

**For multiple domains:**
```
https://your-app.up.railway.app,https://your-custom-domain.com
```

**Important:**
- Must include `https://` (not `http://`)
- No trailing slash
- Exact match required

**Where it's used:**
- `backend/app.py`: SocketIO initialization
- WebSocket connection validation
- CORS headers

**What if not set:**
- Default: `*` (all origins allowed)
- ✗ Security risk: allows anyone to connect
- ✓ Set this!

### DEBUG
**Purpose:** Disables debug mode

**Value:** `False`

**Where it's used:**
- `app.py`: Disables reloader
- `backend/app.py`: Disables debug toolbar
- Error handling: Shows minimal info to users

**What if not set:**
- Flask defaults to debug=False when FLASK_ENV=production
- But explicitly setting this is safest

---

## Admin User Variables

Used to create initial admin account (optional).

### ADMIN_EMAIL
**Purpose:** Email for admin account

**Value:** `admin@yourdomain.com`

**Example:**
```
ADMIN_EMAIL=admin@example.com
```

**Where it's used:**
- `backend/scripts/create_admin.py`: Admin creation script
- First-time setup initialization

### ADMIN_PASSWORD
**Purpose:** Initial admin password

**Value:** Strong password (change after first login!)

**Example:**
```
ADMIN_PASSWORD=SecurePassword123!Min12Chars
```

**IMPORTANT:**
- Change this password after first login
- Should be 12+ characters
- Include uppercase, lowercase, numbers, special chars
- Don't reuse this password elsewhere

**Where it's used:**
- Admin account creation
- Initial login

**Security:**
- ✓ Will be in Railway variables (encrypted at rest)
- ✓ Change immediately after first login
- ✗ Don't use simple passwords

---

## Email Configuration Variables

Required for password reset, notifications (optional but recommended).

### MAIL_SERVER
**Purpose:** SMTP server address

**Value:** Your email provider's SMTP server

**Common values:**
```
smtp.gmail.com       # Gmail
smtp.sendgrid.net    # SendGrid
smtp.mailgun.org     # Mailgun
smtp.office365.com   # Office 365
```

**Example:**
```
MAIL_SERVER=smtp.gmail.com
```

### MAIL_PORT
**Purpose:** SMTP port number

**Value:** 
- `587` (TLS - recommended)
- `465` (SSL)
- `25` (unencrypted - not recommended)

**Example:**
```
MAIL_PORT=587
```

### MAIL_USE_TLS
**Purpose:** Enable TLS encryption

**Value:** `True` or `False`

**Recommended:**
```
MAIL_USE_TLS=True
```

### MAIL_USERNAME
**Purpose:** Email account for sending

**Value:** Your email address

**Example:**
```
MAIL_USERNAME=no-reply@example.com
```

### MAIL_PASSWORD
**Purpose:** Email account password

**Value:** App-specific password (not your regular password!)

**For Gmail:**
1. Enable 2-factor authentication
2. Go to Google Account → Security
3. Create "App Password" for this application
4. Use generated password here

**Example (don't use real):**
```
MAIL_PASSWORD=abcd efgh ijkl mnop
```

### MAIL_DEFAULT_SENDER
**Purpose:** "From:" address for emails

**Value:** Email address or "Name <email@domain>"

**Example:**
```
MAIL_DEFAULT_SENDER=noreply@fyp-system.com
MAIL_DEFAULT_SENDER=FYP System <noreply@example.com>
```

**Where these are used:**
- `backend/app.py`: Flask-Mail configuration
- Password reset emails
- Notification emails
- All outgoing emails

---

## Google OAuth Variables

For Google Sign-In feature (optional).

### GOOGLE_CLIENT_ID
**Purpose:** Google OAuth application ID

**Get from:**
1. https://console.cloud.google.com
2. Create new project
3. APIs & Services → Credentials
4. Create OAuth 2.0 Client ID
5. Copy Client ID

**Value:** Long alphanumeric string

**Example:**
```
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
```

### GOOGLE_CLIENT_SECRET
**Purpose:** Google OAuth application secret

**Get from:** Same process as GOOGLE_CLIENT_ID

**IMPORTANT:**
- ✓ Keep secret (already in Railway variables - encrypted)
- ✗ Never commit to Git
- ✗ Never share

**Example (don't use real):**
```
GOOGLE_CLIENT_SECRET=GOCSPX-abc123def456
```

**Authorized Redirect URI (in Google Console):**
Add both:
```
https://your-app.up.railway.app/authorize
https://your-app.up.railway.app/google/callback
```

---

## File Upload Variables

Configure file upload restrictions.

### MAX_UPLOAD_SIZE
**Purpose:** Maximum file upload size in bytes

**Value:** Size in bytes
- `16777216` = 16 MB (default, recommended)
- `33554432` = 32 MB
- `5242880` = 5 MB (restrictive)

**Example:**
```
MAX_UPLOAD_SIZE=16777216
```

**Where it's used:**
- File upload handler
- Form validation
- User feedback

### UPLOAD_FOLDER
**Purpose:** Directory to store uploaded files

**Value:** Path (usually `/tmp/uploads` on Railway)

**Example:**
```
UPLOAD_FOLDER=/tmp/uploads
```

**Note:**
- Railway provides `/tmp` for temporary storage
- Files deleted after app restart
- For permanent storage, use Railway PostgreSQL or external service

---

## Logging Variables

Control application logging level.

### LOG_LEVEL
**Purpose:** Minimum severity of logged messages

**Values:**
- `DEBUG` - Most verbose (development only)
- `INFO` - Important events (default)
- `WARNING` - Warnings and errors
- `ERROR` - Errors only
- `CRITICAL` - Critical errors only

**Production value:**
```
LOG_LEVEL=INFO
```

**Development value:**
```
LOG_LEVEL=DEBUG
```

**Where it's used:**
- Application logging output
- Railway logs visibility

---

## Railway Auto-Set Variables

These are set automatically by Railway (don't modify).

### DATABASE_URL
- Auto-set when PostgreSQL service added
- Format: `postgresql://...`

### RAILWAY_ENVIRONMENT_NAME
- Value: `production`
- Indicates running on Railway

### RAILWAY_ENVIRONMENT_ID
- Unique Railway environment ID
- Auto-set by Railway

### RAILWAY_PUBLIC_DOMAIN
- Your app's public URL
- Example: `your-app.up.railway.app`
- Auto-set by Railway

---

## Optional but Useful Variables

### PORT
**Purpose:** Server port

**Default:** 5000

**On Railway:** Auto-set (don't modify)

**Local testing:**
```
PORT=8000
```

### TIMEZONE
**Purpose:** Application timezone

**Example:**
```
TIMEZONE=UTC
TIMEZONE=Asia/Karachi
TIMEZONE=America/New_York
```

---

## Configuration Template

Copy this to Railway as a reference:

```
# Flask Core
FLASK_ENV=production
SECRET_KEY=(generate using: python -c "import secrets; print(secrets.token_hex(32))")
DEBUG=False

# Server
PORT=(auto-set by Railway)
ALLOWED_ORIGINS=https://your-app.up.railway.app

# Database
DATABASE_URL=(auto-set by Railway)

# Admin User (optional, for setup)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=ChangeThis123!

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=(app-specific password)
MAIL_DEFAULT_SENDER=noreply@fyp-system.com

# Google OAuth (optional)
GOOGLE_CLIENT_ID=(from Google Console)
GOOGLE_CLIENT_SECRET=(from Google Console)

# File Upload
MAX_UPLOAD_SIZE=16777216
UPLOAD_FOLDER=/tmp/uploads

# Logging
LOG_LEVEL=INFO
```

---

## Validation Checklist

Before deploying:

```
✓ FLASK_ENV=production
✓ SECRET_KEY=set (32+ bytes)
✓ DATABASE_URL=present (auto or manual)
✓ ALLOWED_ORIGINS=set to your domain
✓ DEBUG=False (or not set; defaults correctly)
✓ MAIL variables=optional but recommended
✓ GOOGLE variables=optional if not using OAuth
✓ File upload variables=optional
✓ LOG_LEVEL=INFO
```

---

## Updating Variables

### To update a variable:

1. Railway Dashboard → Variables tab
2. Click the variable name
3. Edit value
4. Press Enter

**Note:** App auto-reloads when variables change (usually)

### If app doesn't pick up change:

1. Go to Deployments tab
2. Click "Redeploy"
3. Wait for deployment to complete

---

## Security Best Practices

- ✓ All variables stored securely (Railway encrypts at rest)
- ✓ Only visible to you in dashboard
- ✓ Can rotate SECRET_KEY anytime (users need to re-login)
- ✓ Can rotate database password (requires update)
- ✓ Use strong, unique secrets
- ✓ Never share variable values
- ✗ Don't commit .env files to Git
- ✗ Don't hardcode secrets in code
- ✗ Don't use simple/default passwords

---

## Troubleshooting

### Variable not being read

**Check:**
1. Exact spelling matches code
2. Value is set (not empty)
3. Deployed after setting (might need redeploy)

**Fix:**
```bash
# Verify in logs
railway logs | grep "Variable"

# Redeploy
git push origin main
```

### App crashes after changing variable

**Likely cause:**
- Invalid value format
- Missing required variable
- Typo in variable name

**Fix:**
1. Check Railway logs for error
2. Revert the change
3. Try again with correct value
4. Redeploy

### DATABASE_URL not working

**Check:**
1. PostgreSQL service exists
2. DATABASE_URL variable visible
3. Connection string format correct

**Fix:**
```bash
# Test connection locally
psql $DATABASE_URL

# If works locally but not on Railway, redeploy
git push origin main
```

---

## Next Steps

1. ✓ Generate SECRET_KEY
2. ✓ Set FLASK_ENV=production
3. ✓ Add PostgreSQL service (auto-sets DATABASE_URL)
4. ✓ Set ALLOWED_ORIGINS to your domain
5. ✓ Configure email (optional but recommended)
6. ✓ Deploy and test

**All set!** Your FYP system is ready for Railway production deployment. 🚀
