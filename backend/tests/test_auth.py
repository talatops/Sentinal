"""Test configuration."""
import pytest
import os

@pytest.fixture(scope='session')
def test_config():
    """Test configuration."""
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.environ.get('TEST_DATABASE_URL', 'postgresql://test_user:test_pass@localhost/test_sentinal'),
    }

