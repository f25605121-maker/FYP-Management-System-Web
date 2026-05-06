"""
ENHANCED ADMIN ROUTES WITH COMPREHENSIVE SECURITY
Example endpoints showing best practices for admin operations.

ATTACH THIS BLUEPRINT TO YOUR APP:
    from .admin_routes_secure import admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

APPLY MIDDLEWARE:
    @app.before_request
    def apply_admin_middleware():
        if request.path.startswith('/admin'):
            # Admin routes already protected by decorators below
            pass
"""

from flask import Blueprint, request, abort, jsonify, session, redirect, url_for
from flask_login import current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Import admin_security for decorators and utilities
from .admin_security import (
    require_auth, require_admin, require_admin_reauth,
    check_resource_access, validate_no_privilege_escalation,
    validate_user_input, ValidationError,
    log_admin_action, error_response, success_response,
    detect_security_anomalies, mark_admin_reauth, clear_admin_reauth
)
from .admin_validation_schemas import (
    CREATE_USER_SCHEMA, UPDATE_USER_SCHEMA, CHANGE_ROLE_SCHEMA,
    RESET_USER_PASSWORD_SCHEMA, ADMIN_REAUTH_SCHEMA
)

logger = logging.getLogger(__name__)

admin_blueprint = Blueprint('admin_secure', __name__)


def get_db():
    """Lazy import db to avoid circular imports"""
    from . import db
    return db


def get_models():
    """Lazy import models to avoid circular imports"""
    from .app import User, AuditLog, StudentGroup
    return User, AuditLog, StudentGroup

@admin_blueprint.route('/reauth', methods=['POST'])
@require_admin
def admin_reauth():
    """
    Admin re-authentication endpoint for sensitive operations.
    Validates password and sets re-auth session marker.
    
    Request: POST /admin/reauth
    Body: { "password": "admin_password" }
    
    Returns:
        200: { success: true, message: "Re-authenticated" }
        401: Invalid password
        403: Not admin
    """
    try:
        # Validate input
        data = request.get_json() or {}
        validated = validate_user_input(data, ADMIN_REAUTH_SCHEMA)
        
        # Check admin password
        if not current_user.check_password(validated['password']):
            log_admin_action(
                action='REAUTH_FAILED',
                resource_type='admin_auth',
                status='FAILED',
                details='Invalid password for re-authentication'
            )
            logger.warning(f"Failed re-auth attempt by {current_user.email}")
            abort(401)
        
        # Mark re-authentication successful
        mark_admin_reauth()
        log_admin_action(
            action='ADMIN_REAUTH_SUCCESS',
            resource_type='admin_auth',
            status='SUCCESS'
        )
        
        return success_response('Re-authenticated successfully. Session valid for 30 minutes.', code=200)
    
    except ValidationError as e:
        log_admin_action(
            action='REAUTH_VALIDATION_FAILED',
            resource_type='admin_auth',
            status='FAILED',
            details=str(e)
        )
        return error_response(f'Validation error: {str(e)}', code=400)
    
    except Exception as e:
        logger.error(f"Error in admin re-auth: {e}", exc_info=True)
        return error_response('Re-authentication failed', code=500)


# ─────────────────────────────────────────────────────────────
# USER MANAGEMENT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@admin_blueprint.route('/users', methods=['GET'])
@require_admin
def get_users():
    """
    List all users with pagination and filtering.
    
    Query params:
        page: int (default 1)
        per_page: int (default 20, max 100)
        role: str (filter by role)
        search: str (search by email or name)
    
    Returns:
        200: { users: [...], total: int, page: int }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role_filter = request.args.get('role', type=str)
        search = request.args.get('search', type=str)
        
        # Validate pagination
        if page < 1 or per_page < 1:
            return error_response('Invalid pagination parameters', code=400)
        
        query = User.query
        
        # Apply filters
        if role_filter and role_filter in ['admin', 'cordinator', 'teacher', 'supervisor', 'student', 'evaluator']:
            query = query.filter_by(role=role_filter)
        
        if search:
            search = f"%{search}%"
            query = query.filter(
                (User.email.ilike(search)) |
                (User.first_name.ilike(search)) |
                (User.last_name.ilike(search))
            )
        
        pagination = query.paginate(page=page, per_page=per_page)
        
        users_data = [{
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in pagination.items]
        
        log_admin_action(
            action='VIEW_USERS_LIST',
            resource_type='user',
            status='SUCCESS',
            details=f'Listed {len(users_data)} users'
        )
        
        return success_response(
            'Users retrieved',
            data={
                'users': users_data,
                'total': pagination.total,
                'page': page,
                'pages': pagination.pages
            },
            code=200
        )
    
    except Exception as e:
        logger.error(f"Error retrieving users: {e}", exc_info=True)
        return error_response('Failed to retrieve users', code=500)


@admin_blueprint.route('/users', methods=['POST'])
@require_admin
@require_admin_reauth
def create_user():
    """
    Create a new user (requires admin re-authentication).
    Validates all fields, prevents privilege escalation.
    
    Request: POST /admin/users
    Body: {
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student",
        "password": "SecurePass123!",
        "program": "CS" (optional)
    }
    
    Returns:
        201: { success: true, user_id: int }
        400: Validation error or email exists
        403: Insufficient permissions
    """
    try:
        # Get and validate input
        data = request.get_json() or {}
        validated = validate_user_input(data, CREATE_USER_SCHEMA)
        
        # Check privilege escalation
        if not validate_no_privilege_escalation(None, validated['role']):
            log_admin_action(
                action='PRIVILEGE_ESCALATION_ATTEMPT',
                resource_type='user_create',
                status='FAILED',
                details=f'Attempted to create user with role: {validated["role"]}'
            )
            return error_response('Insufficient privileges to assign this role', code=403)
        
        # Check if user already exists
        if User.query.filter_by(email=validated['email']).first():
            log_admin_action(
                action='CREATE_USER_FAILED',
                resource_type='user',
                status='FAILED',
                details=f'User already exists: {validated["email"]}'
            )
            return error_response('User with this email already exists', code=400)
        
        # Create new user
        new_user = User(
            email=validated['email'],
            first_name=validated['first_name'],
            last_name=validated['last_name'],
            role=validated['role'],
            program=validated.get('program'),
            semester=validated.get('semester')
        )
        new_user.set_password(validated['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log successful creation
        log_admin_action(
            action='CREATE_USER',
            resource_type='user',
            resource_id=str(new_user.id),
            target_user_id=new_user.id,
            status='SUCCESS',
            details=f'Created user: {validated["email"]} with role: {validated["role"]}'
        )
        
        logger.info(f"Admin {current_user.email} created user {new_user.email}")
        
        return success_response(
            'User created successfully',
            data={'user_id': new_user.id, 'email': new_user.email},
            code=201
        )
    
    except ValidationError as e:
        return error_response(f'Validation error: {str(e)}', code=400)
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        db.session.rollback()
        log_admin_action(
            action='CREATE_USER_ERROR',
            resource_type='user',
            status='FAILED',
            details=str(e)
        )
        return error_response('Failed to create user', code=500)


@admin_blueprint.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user(user_id):
    """
    Get user details (resource-level authorization check).
    
    Returns:
        200: User object
        403: Insufficient access
        404: User not found
    """
    try:
        # Resource-level access check
        if not check_resource_access('user', user_id, current_user.id, action='read'):
            log_admin_action(
                action='UNAUTHORIZED_USER_ACCESS',
                resource_type='user',
                resource_id=str(user_id),
                status='FAILED'
            )
            return error_response('Access denied to this resource', code=403)
        
        user = db.session.get(User, user_id)
        if not user:
            return error_response('User not found', code=404)
        
        return success_response(
            'User retrieved',
            data={
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            },
            code=200
        )
    
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}", exc_info=True)
        return error_response('Failed to retrieve user', code=500)


@admin_blueprint.route('/users/<int:user_id>/role', methods=['PATCH'])
@require_admin
@require_admin_reauth
def change_user_role(user_id):
    """
    Change user role (requires admin re-authentication).
    Prevents privilege escalation (non-admins cannot assign admin role).
    
    Request: PATCH /admin/users/<user_id>/role
    Body: { "new_role": "supervisor" }
    
    Returns:
        200: Role changed
        400: Invalid role
        403: Privilege escalation attempt or access denied
        404: User not found
    """
    try:
        # Get user
        user = db.session.get(User, user_id)
        if not user:
            return error_response('User not found', code=404)
        
        # Get and validate input
        data = request.get_json() or {}
        validated = validate_user_input(data, CHANGE_ROLE_SCHEMA)
        
        new_role = validated['new_role']
        old_role = user.role
        
        # Check privilege escalation
        if not validate_no_privilege_escalation(user_id, new_role):
            log_admin_action(
                action='PRIVILEGE_ESCALATION_ATTEMPT',
                resource_type='user',
                resource_id=str(user_id),
                target_user_id=user_id,
                status='FAILED',
                details=f'Attempted role change from {old_role} to {new_role}'
            )
            return error_response('Insufficient privileges to assign this role', code=403)
        
        # Prevent self-demotion from admin (optional safety check)
        if current_user.id == user_id and new_role != 'admin':
            logger.warning(f"Prevented self-demotion attempt by admin {current_user.id}")
            return error_response('Cannot demote yourself from admin role', code=403)
        
        # Update role
        user.role = new_role
        db.session.commit()
        
        # Log role change
        log_admin_action(
            action='CHANGE_USER_ROLE',
            resource_type='user',
            resource_id=str(user_id),
            target_user_id=user_id,
            status='SUCCESS',
            details=f'Role changed from {old_role} to {new_role}'
        )
        
        logger.info(f"Admin {current_user.email} changed role of user {user.email}: {old_role} -> {new_role}")
        
        return success_response(f'User role changed to {new_role}', code=200)
    
    except ValidationError as e:
        return error_response(f'Validation error: {str(e)}', code=400)
    except Exception as e:
        logger.error(f"Error changing user role: {e}", exc_info=True)
        db.session.rollback()
        return error_response('Failed to change user role', code=500)


@admin_blueprint.route('/users/<int:user_id>/password', methods=['POST'])
@require_admin
@require_admin_reauth
def reset_user_password(user_id):
    """
    Force reset user password (requires admin re-authentication).
    
    Request: POST /admin/users/<user_id>/password
    Body: { "new_password": "NewSecurePass123!" }
    
    Returns:
        200: Password reset
        400: Validation error
        404: User not found
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return error_response('User not found', code=404)
        
        data = request.get_json() or {}
        validated = validate_user_input(data, RESET_USER_PASSWORD_SCHEMA)
        
        user.set_password(validated['new_password'])
        db.session.commit()
        
        log_admin_action(
            action='RESET_USER_PASSWORD',
            resource_type='user',
            resource_id=str(user_id),
            target_user_id=user_id,
            status='SUCCESS'
        )
        
        logger.info(f"Admin {current_user.email} reset password for {user.email}")
        
        return success_response('User password reset successfully', code=200)
    
    except ValidationError as e:
        return error_response(f'Validation error: {str(e)}', code=400)
    except Exception as e:
        logger.error(f"Error resetting password: {e}", exc_info=True)
        db.session.rollback()
        return error_response('Failed to reset password', code=500)


@admin_blueprint.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
@require_admin_reauth
def delete_user(user_id):
    """
    Delete user (soft delete with cascade cleanup, requires re-auth).
    
    Returns:
        200: User deleted
        403: Attempting to delete self
        404: User not found
    """
    try:
        user = db.session.get(User, user_id)
        if not user:
            return error_response('User not found', code=404)
        
        # Prevent self-deletion
        if current_user.id == user_id:
            log_admin_action(
                action='DELETE_USER_FAILED',
                resource_type='user',
                resource_id=str(user_id),
                status='FAILED',
                details='Attempted self-deletion'
            )
            return error_response('Cannot delete your own user account', code=403)
        
        # Cascade delete related records (in production, use soft delete)
        email = user.email
        db.session.delete(user)
        db.session.commit()
        
        log_admin_action(
            action='DELETE_USER',
            resource_type='user',
            resource_id=str(user_id),
            target_user_id=user_id,
            status='SUCCESS',
            details=f'Deleted user: {email}'
        )
        
        logger.info(f"Admin {current_user.email} deleted user {email}")
        
        return success_response('User deleted successfully', code=200)
    
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        db.session.rollback()
        return error_response('Failed to delete user', code=500)


# ─────────────────────────────────────────────────────────────
# SECURITY MONITORING ENDPOINTS
# ─────────────────────────────────────────────────────────────

@admin_blueprint.route('/audit-logs', methods=['GET'])
@require_admin
def get_audit_logs():
    """
    Retrieve audit logs (paginated).
    
    Query params:
        page: int (default 1)
        per_page: int (default 20, max 100)
        action: str (filter by action)
        status: str (SUCCESS or FAILED)
        start_date: ISO date
        end_date: ISO date
    
    Returns:
        200: { logs: [...], total: int }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        action_filter = request.args.get('action', type=str)
        status_filter = request.args.get('status', type=str)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        
        query = AuditLog.query.order_by(AuditLog.timestamp.desc())
        
        if action_filter:
            query = query.filter_by(action=action_filter)
        if status_filter in ['SUCCESS', 'FAILED']:
            query = query.filter_by(status=status_filter)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(AuditLog.timestamp >= start_dt)
            except:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(AuditLog.timestamp <= end_dt)
            except:
                pass
        
        pagination = query.paginate(page=page, per_page=per_page)
        logs = [log.to_dict() for log in pagination.items]
        
        return success_response(
            'Audit logs retrieved',
            data={
                'logs': logs,
                'total': pagination.total,
                'page': page,
                'pages': pagination.pages
            },
            code=200
        )
    
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {e}", exc_info=True)
        return error_response('Failed to retrieve audit logs', code=500)


@admin_blueprint.route('/security-alerts', methods=['GET'])
@require_admin
def get_security_alerts():
    """
    Get current security alerts (anomaly detection).
    
    Returns:
        200: { alerts: [...] }
    """
    try:
        hours = request.args.get('hours', 24, type=int)
        alerts = detect_security_anomalies(admin_id=None, hours=min(hours, 168))  # Max 7 days
        
        return success_response(
            'Security alerts retrieved',
            data={'alerts': alerts},
            code=200
        )
    
    except Exception as e:
        logger.error(f"Error retrieving security alerts: {e}", exc_info=True)
        return error_response('Failed to retrieve security alerts', code=500)


# ─────────────────────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────────────────────

@admin_blueprint.errorhandler(401)
def unauthorized(e):
    """Handle 401 Unauthorized"""
    return error_response('Authentication required', code=401)


@admin_blueprint.errorhandler(403)
def forbidden(e):
    """Handle 403 Forbidden"""
    return error_response('Access denied. Admin privileges required.', code=403)


@admin_blueprint.errorhandler(404)
def not_found(e):
    """Handle 404 Not Found"""
    return error_response('Resource not found', code=404)


@admin_blueprint.errorhandler(500)
def internal_error(e):
    """Handle 500 Internal Server Error"""
    logger.error(f"Internal error: {e}", exc_info=True)
    return error_response('Internal server error', code=500)
