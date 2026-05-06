"""
Patch to add session security to the main app.py
Run this script to apply session security patches
"""

import re

def apply_session_security_patch():
    """Apply session security patches to app.py"""
    
    app_file_path = 'app.py'
    
    try:
        with open(app_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add import for session_security at the top
        if 'from session_security import' not in content:
            # Find the imports section and add our import
            import_pattern = r'(from flask import.*?\n)'
            if re.search(import_pattern, content, re.DOTALL):
                content = re.sub(
                    import_pattern,
                    r'\1from session_security import configure_session_security, secure_login_user, validate_session\n',
                    content,
                    flags=re.DOTALL
                )
        
        # Add session security configuration after existing session config
        session_config_pattern = r"(app\.config\['SESSION_COOKIE_SAMESITE'\] = 'Lax'\n)"
        if 'PERMANENT_SESSION_LIFETIME' not in content:
            replacement = r"""\1
# Session timeout and security settings
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)  # 1 hour session timeout
app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Reset timeout on activity
app.config['SESSION_COOKIE_NAME'] = 'fyp_session'  # Custom session cookie name

# Configure session security
configure_session_security(app)
"""
            content = re.sub(session_config_pattern, replacement, content)
        
        # Modify the login function to use secure login
        login_function_pattern = r'(login_user\(user, remember=remember\))'
        if 'secure_login_user' not in content:
            content = re.sub(
                login_function_pattern,
                'secure_login_user(user, remember=False)',  # Force no remember for security
                content
            )
        
        # Add session validation decorator
        session_validation_code = '''
# Session validation decorator
def require_valid_session(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not validate_session():
            logout_user()
            flash('Your session has expired. Please login again.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

'''
        
        # Add the validation decorator before the first route
        if 'require_valid_session' not in content:
            route_pattern = r'(@app\.route.*?\n)'
            first_route = re.search(route_pattern, content)
            if first_route:
                content = content[:first_route.start()] + session_validation_code + content[first_route.start():]
        
        # Write the patched content back
        with open(app_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Session security patches applied successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error applying patches: {str(e)}")
        return False

if __name__ == '__main__':
    apply_session_security_patch()
