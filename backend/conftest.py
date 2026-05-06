"""
Pytest configuration and fixtures for admin security tests.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app import app, db, User, AuditLog


@pytest.fixture
def app_instance():
    """Create and configure a test Flask app instance."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app_instance):
    """Create a test client."""
    return app_instance.test_client()


@pytest.fixture
def db_fixture(app_instance):
    """Provide database for tests."""
    with app_instance.app_context():
        yield db


@pytest.fixture
def admin_user(app_instance, db_fixture):
    """Create a test admin user."""
    with app_instance.app_context():
        admin = User(
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('AdminPass123!')
        db_fixture.session.add(admin)
        db_fixture.session.commit()
        return admin


@pytest.fixture
def student_user(app_instance, db_fixture):
    """Create a test student user."""
    with app_instance.app_context():
        student = User(
            email='student@test.com',
            first_name='Student',
            last_name='User',
            role='student'
        )
        student.set_password('StudentPass123!')
        db_fixture.session.add(student)
        db_fixture.session.commit()
        return student


@pytest.fixture
def supervisor_user(app_instance, db_fixture):
    """Create a test supervisor user."""
    with app_instance.app_context():
        supervisor = User(
            email='supervisor@test.com',
            first_name='Supervisor',
            last_name='User',
            role='supervisor'
        )
        supervisor.set_password('SupervisorPass123!')
        db_fixture.session.add(supervisor)
        db_fixture.session.commit()
        return supervisor
