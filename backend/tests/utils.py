"""Test utilities and helper functions."""
import json
from datetime import datetime


def create_test_threat_data(asset='Test Asset', flow='Test flow', auto_score=True):
    """Create test threat analysis data."""
    data = {
        'asset': asset,
        'flow': flow,
        'auto_score': auto_score
    }
    
    if not auto_score:
        data.update({
            'damage': 5,
            'reproducibility': 5,
            'exploitability': 5,
            'affected_users': 5,
            'discoverability': 5
        })
    
    return data


def create_test_requirement_data(title='Test Requirement'):
    """Create test requirement data."""
    return {
        'title': title,
        'description': 'Test description',
        'security_controls': [
            {
                'name': 'Test Control',
                'description': 'Control description',
                'owasp_asvs_level': 'Level 1'
            }
        ],
        'status': 'Draft'
    }


def create_test_user_data(username='testuser', email='test@example.com'):
    """Create test user registration data."""
    return {
        'username': username,
        'email': email,
        'password': 'password123',
        'role': 'Developer'
    }


def create_test_login_data(username='testuser', password='testpass123'):
    """Create test login data."""
    return {
        'username': username,
        'password': password
    }


def mock_scan_results(scan_type='sonarqube'):
    """Create mock scan results."""
    if scan_type == 'sonarqube':
        return {
            'total': 10,
            'critical': 2,
            'high': 3,
            'medium': 3,
            'low': 2,
            'issues': [],
            'metrics': {'coverage': 75.5},
            'quality_gate': {'status': 'PASSED'}
        }
    elif scan_type == 'trivy':
        return {
            'total': 5,
            'critical': 1,
            'high': 2,
            'medium': 1,
            'low': 1,
            'vulnerabilities': []
        }
    elif scan_type == 'zap':
        return {
            'total': 8,
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 2,
            'alerts': []
        }
    return {}


def assert_response_structure(response_data, required_fields):
    """Assert that response contains required fields."""
    for field in required_fields:
        assert field in response_data, f"Missing field: {field}"


def assert_error_response(response_data, error_key='error'):
    """Assert that response is an error response."""
    assert error_key in response_data or 'errors' in response_data

