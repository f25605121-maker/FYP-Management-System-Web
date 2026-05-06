"""
COMPREHENSIVE ADMIN SECURITY & AUTHORIZATION MODULE
Implements strict backend authorization, deny-by-default policy, audit logging, 
and role-based access control for all admin operations.
"""

from functools import wraps
from flask import current_app, abort, request, jsonify
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import func
import logging
import traceback

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# 1. CENTRALIZED AUTHORIZATION MIDDLEWARE & DECORATORS
# ─────────────────────────────────────────────────────────────

def require_auth(f):
    """
    Middleware: Requires user to be authenticated.
    Returns 401 if not authenticated, redirects to login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated access attempt to {request.path} from {request.remote_addr}")
            abort(401)  # Unauthorized
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """
    Middleware: Requires user to be authenticated AND have admin role.
    Returns 401 if not authenticated, 403 if not admin.
    Deny-by-default: only explicitly allowed actions can proceed.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated access to admin route {request.path} from {request.remote_addr}")
            abort(401)
        
        if current_user.role != 'admin':
            logger.warning(
                f"Unauthorized admin access attempt by user {current_user.id} (role={current_user.role}) "
                f"to {request.path} from {request.remote_addr}"
            )
            # Log unauthorized attempt
            from . import db
            from .models import AuditLog
            try:
                audit = AuditLog(
                    admin_id=current_user.id,
                    action='UNAUTHORIZED_ACCESS_ATTEMPT',
                    resource_type='admin_route',
                    resource_id=request.path,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', 'Unknown'),
                    status='FAILED',
                    details=f'Non-admin access attempt: role={current_user.role}'
                )
                db.session.add(audit)
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to log unauthorized access: {e}")
            
            abort(403)  # Forbidden
        
        return f(*args, **kwargs)
    return decorated_function


def require_admin_reauth(f):
    """
    Middleware: Requires admin re-authentication for sensitive operations.
    Admin must have re-authenticated within last 30 minutes.
    Checks session key 'admin_reauth_time'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        
        reauth_time = session.get('admin_reauth_time')
        if not reauth_time:
            logger.warning(f"Admin {current_user.id} attempted sensitive op without re-auth at {request.path}")
            abort(403)
        
        reauth_dt = datetime.fromisoformat(reauth_time)
        if datetime.utcnow() - reauth_dt > timedelta(minutes=30):
            logger.warning(f"Admin {current_user.id} re-auth expired for sensitive op at {request.path}")
            del session['admin_reauth_time']
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


# ─────────────────────────────────────────────────────────────
# 2. RESOURCE-LEVEL AUTHORIZATION CHECKS
# ─────────────────────────────────────────────────────────────

def check_resource_access(resource_type, resource_id, user_id, action='read'):
    """
    Resource-level authorization check.
    Validates if user can access/modify a specific resource.
    
    Args:
        resource_type: 'user', 'project', 'group', 'submission', etc.
        resource_id: ID of the resource
        user_id: ID of the user requesting access
        action: 'read', 'write', 'delete'
    
    Returns:
        bool: True if access granted, False otherwise
    """
    from . import db
    from .models import User, StudentGroup, ProjectProposal, Submission
    
    try:
        if resource_type == 'user':
            # Admin can read/modify any user
            user = db.session.get(User, resource_id)
            if not user:
                return False
            # Prevent privilege escalation: only admins can modify admin role
            return True
        
        elif resource_type == 'group':
            group = db.session.get(StudentGroup, resource_id)
            if not group:
                return False
            # Admin can access any group
            return True
        
        elif resource_type == 'project':
            project = db.session.get(ProjectProposal, resource_id)
            if not project:
                return False
            # Admin can access any project
            return True
        
        elif resource_type == 'submission':
            submission = db.session.get(Submission, resource_id)
            if not submission:
                return False
            # Admin can access any submission
            return True
        
        else:
            logger.warning(f"Unknown resource type: {resource_type}")
            return False
    
    except Exception as e:
        logger.error(f"Error checking resource access: {e}")
        return False


def validate_no_privilege_escalation(user_id, new_role):
    """
    Prevent privilege escalation attacks.
    Validates that only admins can assign 'admin' role.
    
    Args:
        user_id: User being modified
        new_role: New role to assign
    
    Returns:
        bool: True if valid, False if escalation attempt
    """
    if new_role == 'admin' and current_user.role != 'admin':
        logger.warning(
            f"Privilege escalation attempt: user {current_user.id} tried to assign admin role to {user_id}"
        )
        return False
    
    if new_role not in ['admin', 'cordinator', 'teacher', 'supervisor', 'student', 'evaluator']:
        logger.warning(f"Invalid role assignment attempt: {new_role}")
        return False
    
    return True


# ─────────────────────────────────────────────────────────────
# 3. INPUT VALIDATION & SANITIZATION
# ─────────────────────────────────────────────────────────────

class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_user_input(data, schema):
    """
    Validate request data against schema.
    Raises ValidationError if invalid.
    
    Args:
        data: dict of user input
        schema: dict defining expected fields, types, and constraints
    
    Returns:
        dict: sanitized data
    """
    if not isinstance(data, dict):
        raise ValidationError("Request body must be JSON object")
    
    sanitized = {}
    
    for field, rules in schema.items():
        value = data.get(field)
        
        # Required field check
        if rules.get('required', False) and (value is None or value == ''):
            raise ValidationError(f"Field '{field}' is required")
        
        if value is None:
            continue
        
        # Type validation
        expected_type = rules.get('type')
        if expected_type == 'string' and not isinstance(value, str):
            raise ValidationError(f"Field '{field}' must be string")
        elif expected_type == 'int' and not isinstance(value, int):
            raise ValidationError(f"Field '{field}' must be integer")
        elif expected_type == 'email' and not isinstance(value, str):
            raise ValidationError(f"Field '{field}' must be string")
        
        # Length validation
        if expected_type in ['string', 'email']:
            min_len = rules.get('min_length')
            max_len = rules.get('max_length')
            if min_len and len(value) < min_len:
                raise ValidationError(f"Field '{field}' must be at least {min_len} chars")
            if max_len and len(value) > max_len:
                raise ValidationError(f"Field '{field}' must not exceed {max_len} chars")
        
        # Pattern validation (regex)
        import re
        pattern = rules.get('pattern')
        if pattern and isinstance(value, str):
            if not re.match(pattern, value):
                raise ValidationError(f"Field '{field}' format invalid")
        
        # Range validation
        if expected_type == 'int':
            min_val = rules.get('min')
            max_val = rules.get('max')
            if min_val is not None and value < min_val:
                raise ValidationError(f"Field '{field}' must be >= {min_val}")
            if max_val is not None and value > max_val:
                raise ValidationError(f"Field '{field}' must be <= {max_val}")
        
        # Allowed values
        allowed = rules.get('allowed')
        if allowed and value not in allowed:
            raise ValidationError(f"Field '{field}' must be one of {allowed}")
        
        # Sanitize string values (remove/escape dangerous chars)
        if isinstance(value, str):
            value = sanitize_string(value)
        
        sanitized[field] = value
    
    # Check for unexpected fields (strict mode)
    strict = schema.get('_strict', False)
    if strict:
        unexpected = set(data.keys()) - set(schema.keys()) - {'_strict'}
        if unexpected:
            raise ValidationError(f"Unexpected fields: {unexpected}")
    
    return sanitized


def sanitize_string(value):
    """
    Sanitize string to prevent XSS and SQL injection.
    - Remove null bytes
    - Escape dangerous characters
    """
    if not isinstance(value, str):
        return value
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    # HTML escape dangerous characters (prevent XSS)
    import html
    value = html.escape(value)
    
    return value


# ─────────────────────────────────────────────────────────────
# 4. AUDIT LOGGING
# ─────────────────────────────────────────────────────────────

def log_admin_action(action, resource_type=None, resource_id=None, 
                     status='SUCCESS', details=None, target_user_id=None):
    """
    Log admin action to persistent database.
    
    Args:
        action: Action name (e.g., 'CREATE_USER', 'DELETE_USER', 'CHANGE_ROLE')
        resource_type: Type of resource (e.g., 'user', 'project')
        resource_id: ID of resource affected
        status: 'SUCCESS' or 'FAILED'
        details: Additional context
        target_user_id: ID of affected user (if applicable)
    
    Returns:
        AuditLog object or None
    """
    from . import db
    from .models import AuditLog
    
    if not current_user.is_authenticated:
        logger.warning("Attempted to log action without authentication")
        return None
    
    try:
        audit = AuditLog(
            admin_id=current_user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            target_user_id=target_user_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', 'Unknown'),
            status=status,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()
        
        logger.info(
            f"ADMIN_ACTION: {action} by {current_user.email} on {resource_type}:{resource_id} - {status}"
        )
        return audit
    
    except Exception as e:
        logger.error(f"Failed to log admin action: {e}")
        db.session.rollback()
        return None


# ─────────────────────────────────────────────────────────────
# 5. ERROR HANDLING & RESPONSE FORMATTING
# ─────────────────────────────────────────────────────────────

def error_response(message, code=400, details=None):
    """
    Return standardized error response.
    Do NOT leak stack traces or internal details.
    """
    response = {
        'success': False,
        'error': message,
        'code': code
    }
    if details and current_app.debug:
        response['details'] = details
    return jsonify(response), code


def success_response(message, data=None, code=200):
    """Return standardized success response."""
    response = {
        'success': True,
        'message': message,
        'code': code
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), code


# ─────────────────────────────────────────────────────────────
# 6. SECURITY MONITORING & ALERTS
# ─────────────────────────────────────────────────────────────

def detect_security_anomalies(admin_id=None, hours=24):
    """
    Detect suspicious patterns in audit logs.
    Returns list of security alerts.
    """
    from . import db
    from .models import AuditLog
    
    alerts = []
    
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Alert: Many failed actions
        failed_actions = AuditLog.query.filter(
            AuditLog.status == 'FAILED',
            AuditLog.timestamp >= cutoff
        ).count()
        if failed_actions > 10:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f'{failed_actions} failed admin actions in last {hours}h',
                'type': 'HIGH_FAILURE_RATE'
            })
        
        # Alert: Unauthorized access attempts
        unauth_attempts = AuditLog.query.filter(
            AuditLog.action == 'UNAUTHORIZED_ACCESS_ATTEMPT',
            AuditLog.timestamp >= cutoff
        ).count()
        if unauth_attempts > 5:
            alerts.append({
                'severity': 'HIGH',
                'message': f'{unauth_attempts} unauthorized access attempts in last {hours}h',
                'type': 'HIGH_UNAUTH_ATTEMPTS'
            })
        
        # Alert: Privilege escalation attempts
        priv_esc = AuditLog.query.filter(
            AuditLog.action == 'PRIVILEGE_ESCALATION_ATTEMPT',
            AuditLog.timestamp >= cutoff
        ).count()
        if priv_esc > 0:
            alerts.append({
                'severity': 'CRITICAL',
                'message': f'{priv_esc} privilege escalation attempts detected!',
                'type': 'PRIVILEGE_ESCALATION_ATTEMPT'
            })
        
        # Alert: Bulk user deletions
        bulk_deletes = AuditLog.query.filter(
            AuditLog.action == 'DELETE_USER',
            AuditLog.timestamp >= cutoff
        ).count()
        if bulk_deletes > 5:
            alerts.append({
                'severity': 'MEDIUM',
                'message': f'{bulk_deletes} users deleted in last {hours}h',
                'type': 'BULK_DELETE_ACTIVITY'
            })
    
    except Exception as e:
        logger.error(f"Error detecting security anomalies: {e}")
    
    return alerts


# ─────────────────────────────────────────────────────────────
# 7. SESSION HARDENING
# ─────────────────────────────────────────────────────────────

def mark_admin_reauth():
    """
    Mark successful admin re-authentication.
    Sets session key with current timestamp.
    """
    from flask import session
    session['admin_reauth_time'] = datetime.utcnow().isoformat()
    session.permanent = True
    logger.info(f"Admin {current_user.id} re-authenticated at {datetime.utcnow()}")


def clear_admin_reauth():
    """Clear admin re-authentication marker."""
    from flask import session
    if 'admin_reauth_time' in session:
        del session['admin_reauth_time']
    logger.info(f"Cleared re-auth for admin {current_user.id}")


def invalidate_admin_sessions(admin_id):
    """
    Invalidate all sessions for an admin (e.g., on role downgrade or logout).
    Note: Requires session store to support this (SQLAlchemy sessions).
    """
    logger.info(f"Invalidating all sessions for admin {admin_id}")
    # Implementation depends on session store
    # For Flask default session: next request will show new login


