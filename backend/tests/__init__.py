"""Simple test file for backend."""
import pytest
from app import create_app, db
from app.models.user import User
from app.core.security import hash_password


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
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


def test_user_creation(app, test_user):
    """Test user creation."""
    assert test_user.username == 'testuser'
    assert test_user.email == 'test@example.com'
    assert test_user.role == 'Developer'


def test_user_password_hash(app, test_user):
    """Test password hashing."""
    from app.core.security import verify_password
    assert verify_password('testpass123', test_user.password_hash)
    assert not verify_password('wrongpass', test_user.password_hash)

