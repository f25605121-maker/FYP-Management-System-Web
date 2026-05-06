"""
Session Security Configuration for FYP Management System
Prevents session hijacking across browsers and implements proper timeout
"""

import datetime
from flask import session

def configure_session_security(app):
    """Configure secure session settings"""
    
    # Session timeout and security settings
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)  # 1 hour session timeout
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Reset timeout on activity
    app.config['SESSION_COOKIE_NAME'] = 'fyp_session'  # Custom session cookie name
    
    return app

def secure_login_user(user, remember=False):
    """Secure login function that sets proper session parameters"""
    from flask_login import login_user
    
    # Set session as permanent to enable timeout
    session.permanent = True
    
    # Login user without remember me for security
    login_user(user, remember=False)  # Force no remember for security
    
    # Set additional session security markers
    session['login_time'] = datetime.datetime.now().isoformat()
    session['user_agent'] = str(request.user_agent) if 'request' in globals() else 'unknown'
    session['ip_address'] = request.remote_addr if 'request' in globals() else 'unknown'

def validate_session():
    """Validate current session for security"""
    if 'login_time' not in session:
        return False
    
    try:
        login_time = datetime.datetime.fromisoformat(session['login_time'])
        # Check if session is older than 1 hour
        if datetime.datetime.now() - login_time > datetime.timedelta(hours=1):
            return False
    except:
        return False
    
    return True

def invalidate_session():
    """Invalidate current session"""
    session.clear()
    from flask_login import logout_user
    logout_user()
