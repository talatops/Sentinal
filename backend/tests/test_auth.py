"""Test user model and authentication utilities."""
from app.core.security import verify_password


def test_user_creation(app, test_user):
    """Test user creation."""
    assert test_user.username == 'testuser'
    assert test_user.email == 'test@example.com'
    assert test_user.role == 'Developer'


def test_user_password_hash(app, test_user):
    """Test password hashing."""
    assert verify_password('testpass123', test_user.password_hash)
    assert not verify_password('wrongpass', test_user.password_hash)
