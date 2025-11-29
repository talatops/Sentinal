"""Test user model and authentication utilities."""
from app import db
from app.core.security import verify_password


def test_user_creation(app, test_user):
    """Test user creation."""
    with app.app_context():
        # Merge user back into session to access attributes
        user = db.session.merge(test_user)
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'Developer'


def test_user_password_hash(app, test_user):
    """Test password hashing."""
    with app.app_context():
        # Merge user back into session to access attributes
        user = db.session.merge(test_user)
        assert verify_password('testpass123', user.password_hash)
        assert not verify_password('wrongpass', user.password_hash)
