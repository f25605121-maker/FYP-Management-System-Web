"""
Advanced Admin Features for FYP Management System
Security monitoring, audit logs, and enhanced admin management
"""

import datetime
import json
from functools import wraps
from flask import request, session, flash, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash

# Admin audit log storage (in production, use database)
ADMIN_AUDIT_LOG = []

def log_admin_action(action, details=None, user_id=None):
    """Log admin actions for security auditing"""
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'admin_email': session.get('admin_email', 'unknown'),
        'action': action,
        'details': details or {},
        'ip_address': request.remote_addr,
        'user_agent': str(request.user_agent),
        'user_id': user_id
    }
    ADMIN_AUDIT_LOG.append(log_entry)
    
    # Keep only last 1000 entries
    if len(ADMIN_AUDIT_LOG) > 1000:
        ADMIN_AUDIT_LOG.pop(0)

def admin_required(f):
    """Enhanced admin decorator with logging"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            log_admin_action("UNAUTHORIZED_ACCESS_ATTEMPT", {
                'route': request.endpoint,
                'method': request.method,
                'ip': request.remote_addr
            })
            flash("Access denied. This attempt has been logged.", "danger")
            return redirect(url_for('login'))
        
        # Log admin access
        log_admin_action("ADMIN_PAGE_ACCESS", {
            'route': request.endpoint,
            'method': request.method
        })
        
        return f(*args, **kwargs)
    return decorated_function

def validate_admin_session():
    """Validate admin session for security"""
    if 'admin_session_start' not in session:
        return False
    
    try:
        session_start = datetime.datetime.fromisoformat(session['admin_session_start'])
        # Force admin re-authentication after 30 minutes
        if datetime.datetime.now() - session_start > datetime.timedelta(minutes=30):
            return False
    except:
        return False
    
    return True

def require_admin_reauth(f):
    """Require admin re-authentication for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_admin_session():
            flash("For security, please re-authenticate to access this area.", "warning")
            return redirect(url_for('admin_reauth'))
        return f(*args, **kwargs)
    return decorated_function

def get_admin_stats():
    """Get comprehensive admin statistics"""
    from app import db, User
    
    stats = {
        'total_users': User.query.count(),
        'students': User.query.filter_by(role='student').count(),
        'teachers': User.query.filter_by(role='teacher').count(),
        'supervisors': User.query.filter_by(role='supervisor').count(),
        'admins': User.query.filter_by(role='admin').count(),
        'recent_logins': get_recent_admin_logins(),
        'security_alerts': get_security_alerts(),
        'system_health': get_system_health()
    }
    
    return stats

def get_recent_admin_logins():
    """Get recent admin login attempts"""
    recent_logins = [
        log for log in ADMIN_AUDIT_LOG 
        if log['action'] == 'ADMIN_LOGIN' 
        and datetime.datetime.fromisoformat(log['timestamp']) > datetime.datetime.now() - datetime.timedelta(days=7)
    ]
    return recent_logins[-10:]  # Last 10 logins

def get_security_alerts():
    """Get security alerts for admin dashboard"""
    alerts = []
    
    # Check for failed login attempts
    failed_logins = [
        log for log in ADMIN_AUDIT_LOG 
        if log['action'] == 'FAILED_LOGIN'
        and datetime.datetime.fromisoformat(log['timestamp']) > datetime.datetime.now() - datetime.timedelta(hours=24)
    ]
    
    if len(failed_logins) > 5:
        alerts.append({
            'type': 'warning',
            'message': f"High number of failed login attempts: {len(failed_logins)} in last 24 hours",
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    # Check for unauthorized access attempts
    unauthorized = [
        log for log in ADMIN_AUDIT_LOG 
        if log['action'] == 'UNAUTHORIZED_ACCESS_ATTEMPT'
        and datetime.datetime.fromisoformat(log['timestamp']) > datetime.datetime.now() - datetime.timedelta(hours=24)
    ]
    
    if unauthorized:
        alerts.append({
            'type': 'danger',
            'message': f"Unauthorized access attempts: {len(unauthorized)} in last 24 hours",
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    return alerts

def get_system_health():
    """Get system health metrics"""
    try:
        from app import db
        
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except:
        db_status = 'error'
    
    return {
        'database': db_status,
        'timestamp': datetime.datetime.now().isoformat(),
        'uptime': 'Running'  # In production, calculate actual uptime
    }

def create_admin_user(email, first_name, last_name, password, created_by=None):
    """Create new admin user with proper security"""
    from app import db, User
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(email=email).first()
    if existing_admin:
        return False, "Admin user with this email already exists"
    
    # Validate admin password requirements
    if len(password) < 12:
        return False, "Admin password must be at least 12 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Admin password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Admin password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Admin password must contain at least one digit"
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        return False, "Admin password must contain at least one special character"
    
    # Create admin user
    admin = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role='admin'
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    # Log admin creation
    log_admin_action("ADMIN_CREATED", {
        'new_admin_email': email,
        'created_by': created_by
    })
    
    return True, "Admin user created successfully"

def deactivate_user(user_id, deactivated_by=None):
    """Deactivate a user account"""
    from app import db, User
    
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"
    
    if user.role == 'admin':
        return False, "Cannot deactivate admin accounts"
    
    user.is_active = False
    db.session.commit()
    
    log_admin_action("USER_DEACTIVATED", {
        'deactivated_user_id': user_id,
        'deactivated_user_email': user.email,
        'deactivated_by': deactivated_by
    })
    
    return True, f"User {user.email} has been deactivated"

def force_password_reset(user_id, forced_by=None):
    """Force user to reset password on next login"""
    from app import db, User
    
    user = User.query.get(user_id)
    if not user:
        return False, "User not found"
    
    user.force_password_reset = True
    db.session.commit()
    
    log_admin_action("PASSWORD_RESET_FORCED", {
        'target_user_id': user_id,
        'target_user_email': user.email,
        'forced_by': forced_by
    })
    
    return True, f"Password reset forced for user {user.email}"

def get_audit_logs(limit=100):
    """Get admin audit logs"""
    return ADMIN_AUDIT_LOG[-limit:]

def export_audit_logs():
    """Export audit logs as JSON"""
    return json.dumps(ADMIN_AUDIT_LOG, indent=2, default=str)
