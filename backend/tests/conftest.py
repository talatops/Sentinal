"""Pytest configuration and shared fixtures."""
import pytest
import os
from app import create_app, db
from app.models.user import User
from app.core.security import hash_password
from flask_jwt_extended import create_access_token


@pytest.fixture(scope='function')
def app():
    """Create test application."""
    # Use TEST_DATABASE_URL if available, otherwise use default
    test_db_url = os.environ.get(
        'TEST_DATABASE_URL',
        os.environ.get('DATABASE_URL', 'postgresql://test_user:test_pass@localhost/test_sentinal')
    )
    os.environ['TEST_DATABASE_URL'] = test_db_url
    
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=hash_password('testpass123'),
            role='Developer'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(app):
    """Create admin user."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            password_hash=hash_password('adminpass123'),
            role='Admin'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(app, test_user):
    """Create JWT auth headers for test user."""
    with app.app_context():
        access_token = create_access_token(identity=test_user.id)
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def admin_headers(app, admin_user):
    """Create JWT auth headers for admin user."""
    with app.app_context():
        access_token = create_access_token(identity=admin_user.id)
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def db_session(app):
    """Get database session."""
    with app.app_context():
        yield db.session
        db.session.rollback()

