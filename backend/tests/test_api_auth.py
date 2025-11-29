"""Test authentication API endpoints."""
import json
from app.models.user import User


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'role': 'Developer'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert 'user' in data
    assert data['user']['username'] == 'newuser'


def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username."""
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'already exists' in data['error'].lower()


def test_register_invalid_data(client):
    """Test registration with invalid data."""
    response = client.post(
        '/api/auth/register',
        data=json.dumps({
            'username': 'ab',  # Too short
            'email': 'invalid-email',
            'password': 'short'  # Too short
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'errors' in data


def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'testpass123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert 'user' in data
    assert data['user']['username'] == 'testuser'


def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'wrongpassword'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'nonexistent',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'error' in data


def test_get_profile(client, auth_headers):
    """Test getting user profile."""
    response = client.get(
        '/api/auth/profile',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'user' in data
    assert data['user']['username'] == 'testuser'


def test_get_profile_unauthorized(client):
    """Test getting profile without authentication."""
    response = client.get('/api/auth/profile')
    
    assert response.status_code == 401


def test_refresh_token(client, test_user):
    """Test token refresh."""
    # First login to get refresh token
    login_response = client.post(
        '/api/auth/login',
        data=json.dumps({
            'username': 'testuser',
            'password': 'testpass123'
        }),
        content_type='application/json'
    )
    
    login_data = json.loads(login_response.data)
    refresh_token = login_data['refresh_token']
    
    # Refresh the token
    response = client.post(
        '/api/auth/refresh',
        headers={'Authorization': f'Bearer {refresh_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

