"""
Add advanced admin routes to main app.py
Run this to patch the main application with enhanced admin features
"""

import re

def add_admin_routes():
    """Add advanced admin routes to app.py"""
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add import for admin_features
        if 'from admin_features import' not in content:
            import_pattern = r'(from flask import.*?\n)'
            content = re.sub(
                import_pattern,
                r'\1from admin_features import (\n    log_admin_action, admin_required, require_admin_reauth,\n    get_admin_stats, get_audit_logs, create_admin_user,\n    deactivate_user, force_password_reset, export_audit_logs,\n    validate_admin_session, ADMIN_AUDIT_LOG\n)\n',
                content,
                flags=re.DOTALL
            )
        
        # Add admin re-authentication route
        reauth_route = '''
@app.route('/admin/reauth', methods=['GET', 'POST'])
@admin_required
def admin_reauth():
    \"\"\"Admin re-authentication for sensitive operations\"\"\"
    if request.method == 'POST':
        password = request.form.get('password')
        if current_user.check_password(password):
            session['admin_session_start'] = datetime.datetime.now().isoformat()
            log_admin_action("ADMIN_REAUTH_SUCCESS")
            flash("Re-authentication successful.", "success")
            return redirect(request.args.get('next') or url_for('dashboard_admin'))
        else:
            log_admin_action("ADMIN_REAUTH_FAILED", {'ip': request.remote_addr})
            flash("Invalid password. Please try again.", "danger")
    
    return render_template('admin_reauth.html')

'''
        
        # Add admin re-auth route before the first admin route
        if 'admin_reauth' not in content:
            admin_route_pattern = r'(@app\.route\(\"\/dashboard_admin\"\))'
            content = re.sub(admin_route_pattern, reauth_route + r'\1', content)
        
        # Add enhanced admin dashboard route
        enhanced_dashboard = '''
@app.route('/dashboard_admin_enhanced')
@admin_required
def dashboard_admin_enhanced():
    \"\"\"Enhanced admin dashboard with security features\"\"\"
    if not validate_admin_session():
        return redirect(url_for('admin_reauth', next=request.url))
    
    # Set admin session start
    session['admin_session_start'] = datetime.datetime.now().isoformat()
    session['admin_email'] = current_user.email
    
    # Get comprehensive admin stats
    stats = get_admin_stats()
    
    return render_template('dashboard_admin_enhanced.html', 
                         stats=stats, 
                         audit_logs=ADMIN_AUDIT_LOG[-50:])

'''
        
        # Add enhanced dashboard route
        if 'dashboard_admin_enhanced' not in content:
            content += enhanced_dashboard
        
        # Add admin management routes
        admin_management_routes = '''

@app.route('/admin/create_admin', methods=['POST'])
@admin_required
@require_admin_reauth
def create_new_admin():
    \"\"\"Create new admin user with enhanced security\"\"\"
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    password = request.form.get('password')
    
    success, message = create_admin_user(
        email, first_name, last_name, password, 
        created_by=current_user.email
    )
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for('dashboard_admin_enhanced'))

@app.route('/admin/deactivate_user/<int:user_id>', methods=['POST'])
@admin_required
@require_admin_reauth
def deactivate_user_account(user_id):
    \"\"\"Deactivate user account\"\"\"
    success, message = deactivate_user(user_id, deactivated_by=current_user.email)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for('dashboard_admin_enhanced'))

@app.route('/admin/force_password_reset/<int:user_id>', methods=['POST'])
@admin_required
@require_admin_reauth
def force_user_password_reset(user_id):
    \"\"\"Force user to reset password\"\"\"
    success, message = force_password_reset(user_id, forced_by=current_user.email)
    
    if success:
        flash(message, "success")
    else:
        flash(message, "danger")
    
    return redirect(url_for('dashboard_admin_enhanced'))

@app.route('/admin/audit_logs')
@admin_required
def view_audit_logs():
    \"\"\"View admin audit logs\"\"\"
    logs = get_audit_logs(200)
    return render_template('admin_audit_logs.html', audit_logs=logs)

@app.route('/admin/export_logs')
@admin_required
def export_admin_logs():
    \"\"\"Export admin audit logs\"\"\"
    log_data = export_audit_logs()
    response = app.response_class(
        response=log_data,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=admin_audit_logs.json'}
    )
    return response

@app.route('/admin/security_monitoring')
@admin_required
def security_monitoring():
    \"\"\"Security monitoring dashboard\"\"\"
    stats = get_admin_stats()
    return render_template('admin_security.html', stats=stats)

'''
        
        # Add admin management routes
        if 'create_new_admin' not in content:
            content += admin_management_routes
        
        # Enhanced login route with admin logging
        login_pattern = r'(if user and user\.check_password\(password\):.*?login_user\(user, remember=remember\))'
        enhanced_login = r'\1\n            \n            # Log admin login\n            if user.role == "admin":\n                log_admin_action("ADMIN_LOGIN", {\n                    "admin_email": user.email,\n                    "ip": request.remote_addr\n                })'
        
        content = re.sub(login_pattern, enhanced_login, content, flags=re.DOTALL)
        
        # Write the enhanced content
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Advanced admin routes added successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding admin routes: {str(e)}")
        return False

if __name__ == '__main__':
    add_admin_routes()
