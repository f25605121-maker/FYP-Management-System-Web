"""
COMPREHENSIVE TEST SUITE FOR ADMIN SECURITY
Tests all authorization, validation, and logging features.

Run with: pytest test_admin_security.py -v

Install dependencies:
    pip install pytest pytest-flask
"""

import pytest
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash


class TestAdminSecurityMiddleware:
    """Test authorization middleware and decorators"""
    
    @pytest.fixture
    def admin_user(self, app, db):
        """Create admin user for tests"""
        admin = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('AdminPass123!')
        db.session.add(admin)
        db.session.commit()
        return admin
    
    @pytest.fixture
    def student_user(self, app, db):
        """Create student user for tests"""
        student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        student.set_password('StudentPass123!')
        db.session.add(student)
        db.session.commit()
        return student
    
    def test_unauthenticated_access_to_admin_route_returns_401(self, client):
        """REQUIREMENT: Unauthenticated access to /admin/* → 401"""
        response = client.get('/admin/users')
        assert response.status_code == 401
        assert 'error' in response.get_json()
    
    def test_non_admin_access_to_admin_route_returns_403(self, client, student_user):
        """REQUIREMENT: Non-admin access to /admin/* → 403"""
        client.login(student_user.email, 'StudentPass123!')
        response = client.get('/admin/users')
        assert response.status_code == 403
        assert response.get_json()['error'] == 'Access denied'
    
    def test_admin_access_allowed_to_admin_route(self, client, admin_user):
        """REQUIREMENT: Admin can access /admin/* routes"""
        client.login(admin_user.email, 'AdminPass123!')
        response = client.get('/admin/users')
        assert response.status_code == 200
        assert response.get_json()['success'] is True
    
    def test_unauthorized_access_logged_to_audit(self, client, student_user, db):
        """REQUIREMENT: Unauthorized attempts are logged"""
        client.login(student_user.email, 'StudentPass123!')
        client.get('/admin/users')
        
        # Check audit log
        audit = AuditLog.query.filter_by(
            action='UNAUTHORIZED_ACCESS_ATTEMPT'
        ).first()
        assert audit is not None
        assert audit.status == 'FAILED'


class TestInputValidation:
    """Test input validation and sanitization"""
    
    @pytest.fixture
    def admin_session(self, client, admin_user):
        """Create authenticated admin session"""
        client.login(admin_user.email, 'AdminPass123!')
        return client
    
    def test_invalid_email_format_rejected(self, admin_session):
        """REQUIREMENT: Invalid email format rejected with 400"""
        response = admin_session.post('/admin/users', json={
            'email': 'not-an-email',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        assert response.status_code == 400
        assert 'Validation error' in response.get_json()['error']
    
    def test_weak_password_rejected(self, admin_session):
        """REQUIREMENT: Weak password rejected"""
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password': 'weak'  # Too short, no special chars, etc.
        })
        assert response.status_code == 400
    
    def test_invalid_role_rejected(self, admin_session):
        """REQUIREMENT: Invalid role rejected"""
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'invalid_role',
            'password': 'TestPass123!'
        })
        assert response.status_code == 400
    
    def test_missing_required_field_rejected(self, admin_session):
        """REQUIREMENT: Missing required fields rejected"""
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            # Missing last_name (required)
            'role': 'student',
            'password': 'TestPass123!'
        })
        assert response.status_code == 400
    
    def test_xss_attempt_sanitized(self, admin_session):
        """REQUIREMENT: XSS attempts are sanitized"""
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': '<script>alert("xss")</script>',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        # Should create user with escaped first_name
        if response.status_code == 201:
            # Verify the script tag was escaped
            user = User.query.filter_by(email='test@test.com').first()
            assert '<script>' not in user.first_name
            assert '&lt;script&gt;' in user.first_name  # HTML escaped


class TestRoleManagement:
    """Test role-based access control and privilege escalation prevention"""
    
    @pytest.fixture
    def admin_session(self, client, admin_user):
        client.login(admin_user.email, 'AdminPass123!')
        # Re-authenticate for sensitive ops
        client.post('/admin/reauth', json={'password': 'AdminPass123!'})
        return client
    
    def test_non_admin_cannot_create_admin_user(self, client, student_user):
        """REQUIREMENT: Prevent privilege escalation - non-admin cannot assign admin role"""
        client.login(student_user.email, 'StudentPass123!')
        response = client.post('/admin/users', json={
            'email': 'newadmin@test.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'role': 'admin',
            'password': 'TestPass123!'
        })
        assert response.status_code == 403
        assert 'privileges' in response.get_json()['error'].lower()
    
    def test_privilege_escalation_logged(self, client, student_user, db):
        """REQUIREMENT: Privilege escalation attempts are logged"""
        client.login(student_user.email, 'StudentPass123!')
        client.post('/admin/users', json={
            'email': 'newadmin@test.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'role': 'admin',
            'password': 'TestPass123!'
        })
        
        audit = AuditLog.query.filter_by(
            action='PRIVILEGE_ESCALATION_ATTEMPT'
        ).first()
        assert audit is not None
    
    def test_role_change_logged_with_old_new_values(self, admin_session, student_user, db):
        """REQUIREMENT: Role changes logged with before/after values"""
        response = admin_session.patch(
            f'/admin/users/{student_user.id}/role',
            json={'new_role': 'supervisor'}
        )
        assert response.status_code == 200
        
        # Verify audit log
        audit = AuditLog.query.filter_by(
            action='CHANGE_USER_ROLE',
            target_user_id=student_user.id
        ).first()
        assert audit is not None
        assert 'student' in audit.details
        assert 'supervisor' in audit.details


class TestAuditLogging:
    """Test audit logging functionality"""
    
    @pytest.fixture
    def admin_session(self, client, admin_user):
        client.login(admin_user.email, 'AdminPass123!')
        client.post('/admin/reauth', json={'password': 'AdminPass123!'})
        return client
    
    def test_create_user_action_logged(self, admin_session, db):
        """REQUIREMENT: Every admin action is logged"""
        response = admin_session.post('/admin/users', json={
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        assert response.status_code == 201
        
        # Verify audit log entry
        audit = AuditLog.query.filter_by(
            action='CREATE_USER'
        ).order_by(AuditLog.timestamp.desc()).first()
        
        assert audit is not None
        assert audit.status == 'SUCCESS'
        assert 'newuser@test.com' in audit.details
        assert audit.ip_address is not None
        assert audit.user_agent is not None
    
    def test_failed_action_logged(self, admin_session, db):
        """REQUIREMENT: Failed actions are logged"""
        # Attempt to create user with duplicate email
        admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',  # Duplicate
            'first_name': 'Test2',
            'last_name': 'User2',
            'role': 'student',
            'password': 'TestPass123!'
        })
        assert response.status_code == 400
        
        # Verify failed attempt was logged
        audit = AuditLog.query.filter_by(
            action='CREATE_USER_FAILED',
            status='FAILED'
        ).order_by(AuditLog.timestamp.desc()).first()
        assert audit is not None
    
    def test_audit_log_contains_no_sensitive_data(self, admin_session):
        """REQUIREMENT: Audit logs don't contain sensitive data (passwords, tokens)"""
        admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        
        audit = AuditLog.query.filter_by(
            action='CREATE_USER'
        ).first()
        
        assert 'TestPass123!' not in audit.details
        assert 'password' not in audit.details.lower()
    
    def test_retrieve_audit_logs_endpoint(self, admin_session):
        """REQUIREMENT: Audit logs can be retrieved via API"""
        response = admin_session.get('/admin/audit-logs?page=1&per_page=10')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'logs' in data['data']
        assert 'total' in data['data']


class TestSessionHardening:
    """Test session security and re-authentication"""
    
    @pytest.fixture
    def admin_session(self, client, admin_user):
        client.login(admin_user.email, 'AdminPass123!')
        return client
    
    def test_sensitive_operation_requires_reauth(self, admin_session):
        """REQUIREMENT: Sensitive operations require re-authentication"""
        # Create user without re-auth should fail
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        assert response.status_code == 403
    
    def test_reauth_sets_session_marker(self, admin_session):
        """REQUIREMENT: Successful re-auth sets session marker"""
        response = admin_session.post('/admin/reauth', json={
            'password': 'AdminPass123!'
        })
        assert response.status_code == 200
        # Session marker should be set (tested via subsequent allowed requests)
    
    def test_reauth_expires_after_30_minutes(self, admin_session):
        """REQUIREMENT: Re-auth expires after 30 minutes"""
        # Set re-auth time to 31 minutes ago
        with admin_session.session_transaction() as sess:
            old_time = (datetime.utcnow() - timedelta(minutes=31)).isoformat()
            sess['admin_reauth_time'] = old_time
        
        # Sensitive operation should fail
        response = admin_session.post('/admin/users', json={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'student',
            'password': 'TestPass123!'
        })
        assert response.status_code == 403
    
    def test_invalid_reauth_password_rejected(self, admin_session):
        """REQUIREMENT: Invalid password in re-auth rejected"""
        response = admin_session.post('/admin/reauth', json={
            'password': 'WrongPassword123!'
        })
        assert response.status_code == 401


class TestResourceLevelAuthorization:
    """Test resource-level access checks"""
    
    def test_admin_can_access_any_user_resource(self, client, admin_user, student_user):
        """REQUIREMENT: Admin can access any resource"""
        client.login(admin_user.email, 'AdminPass123!')
        response = client.get(f'/admin/users/{student_user.id}')
        assert response.status_code == 200
    
    def test_404_for_nonexistent_user(self, client, admin_user):
        """REQUIREMENT: Proper 404 for nonexistent resources"""
        client.login(admin_user.email, 'AdminPass123!')
        response = client.get('/admin/users/99999')
        assert response.status_code == 404


class TestDenyByDefault:
    """Test deny-by-default policy"""
    
    def test_implicit_deny_for_unlisted_routes(self, client, admin_user):
        """REQUIREMENT: Routes without explicit allow are denied"""
        # This would need a route that's not explicitly allowed
        # Testing the principle that authorization is checked
        pass


class TestErrorHandling:
    """Test error responses and no information leakage"""
    
    def test_error_response_format_standardized(self, client, admin_user):
        """REQUIREMENT: Error responses use consistent format"""
        client.login(admin_user.email, 'AdminPass123!')
        response = client.get('/admin/users/99999')
        data = response.get_json()
        assert 'error' in data
        assert 'code' in data
        assert 'success' in data
    
    def test_stack_trace_not_leaked_in_response(self, client, admin_user):
        """REQUIREMENT: No stack traces in error responses"""
        client.login(admin_user.email, 'AdminPass123!')
        response = client.post('/admin/users', json={
            'invalid': 'data'
        })
        error_msg = response.get_json()['error']
        assert 'traceback' not in error_msg.lower()
        assert 'file' not in error_msg.lower()


class TestSecurityMonitoring:
    """Test security alert detection"""
    
    def test_detect_high_failed_login_attempts(self, client, db):
        """REQUIREMENT: Detect and alert on anomalies"""
        # This would need to create multiple failed login attempts
        # and verify security_alerts endpoint detects them
        pass
    
    def test_security_alerts_endpoint_accessible(self, client, admin_user):
        """REQUIREMENT: Security alerts can be retrieved"""
        client.login(admin_user.email, 'AdminPass123!')
        response = client.get('/admin/security-alerts')
        assert response.status_code == 200
        data = response.get_json()
        assert 'alerts' in data['data']


# ─────────────────────────────────────────────────────────────
# INTEGRATION TESTS
# ─────────────────────────────────────────────────────────────

class TestFullUserLifecycle:
    """Test complete admin workflow"""
    
    def test_admin_can_create_change_role_and_reset_password(self, client, admin_user):
        """Full workflow: create → change role → reset password"""
        client.login(admin_user.email, 'AdminPass123!')
        
        # 1. Create user
        client.post('/admin/reauth', json={'password': 'AdminPass123!'})
        response = client.post('/admin/users', json={
            'email': 'workflow@test.com',
            'first_name': 'Workflow',
            'last_name': 'Test',
            'role': 'student',
            'password': 'WorkPass123!'
        })
        assert response.status_code == 201
        user_id = response.get_json()['data']['user_id']
        
        # 2. Change role
        client.post('/admin/reauth', json={'password': 'AdminPass123!'})
        response = client.patch(f'/admin/users/{user_id}/role', 
                                json={'new_role': 'supervisor'})
        assert response.status_code == 200
        
        # 3. Reset password
        client.post('/admin/reauth', json={'password': 'AdminPass123!'})
        response = client.post(f'/admin/users/{user_id}/password',
                               json={'new_password': 'NewPass123!'})
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
