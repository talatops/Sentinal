"""Test threat modeling API endpoints."""
import json
from app.models.threat import Threat


def test_analyze_threat_auto_score(client, auth_headers):
    """Test threat analysis with auto-scoring."""
    response = client.post(
        '/api/threats/analyze',
        data=json.dumps({
            'asset': 'User Database',
            'flow': 'User submits login credentials via POST request. Backend queries PostgreSQL database to verify credentials.',
            'trust_boundary': 'Internal Network',
            'auto_score': True
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'threat' in data
    assert 'analysis' in data
    assert 'stride_categories' in data['analysis']
    assert 'dread_score' in data['analysis']
    assert 'risk_level' in data['analysis']
    assert 'mitigation' in data['analysis']


def test_analyze_threat_manual_score(client, auth_headers):
    """Test threat analysis with manual DREAD scoring."""
    response = client.post(
        '/api/threats/analyze',
        data=json.dumps({
            'asset': 'Payment API',
            'flow': 'User submits payment information through API endpoint',
            'auto_score': False,
            'damage': 9,
            'reproducibility': 8,
            'exploitability': 7,
            'affected_users': 10,
            'discoverability': 6
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'threat' in data
    assert 'analysis' in data
    assert data['analysis']['dread_score'] == 8.0  # (9+8+7+10+6)/5


def test_analyze_threat_missing_required_fields(client, auth_headers):
    """Test threat analysis with missing required fields."""
    response = client.post(
        '/api/threats/analyze',
        data=json.dumps({
            'asset': 'Test Asset'
            # Missing 'flow' field
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'errors' in data


def test_get_threats(client, auth_headers, test_user, app):
    """Test getting all threats."""
    # Create a test threat
    with app.app_context():
        threat = Threat(
            asset='Test Asset',
            flow='Test flow description',
            stride_categories=['Tampering', 'Information Disclosure'],
            dread_score={'damage': 5, 'reproducibility': 5, 'exploitability': 5, 'affected_users': 5, 'discoverability': 5},
            risk_level='Medium'
        )
        from app import db
        db.session.add(threat)
        db.session.commit()
    
    response = client.get('/api/threats', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'threats' in data
    assert isinstance(data['threats'], list)


def test_get_threat_detail(client, auth_headers, test_user, app):
    """Test getting threat details."""
    # Create a test threat
    with app.app_context():
        threat = Threat(
            asset='Test Asset',
            flow='Test flow description',
            stride_categories=['Tampering'],
            dread_score={'damage': 5, 'reproducibility': 5, 'exploitability': 5, 'affected_users': 5, 'discoverability': 5},
            risk_level='Medium'
        )
        from app import db
        db.session.add(threat)
        db.session.commit()
        threat_id = threat.id
    
    response = client.get(f'/api/threats/{threat_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'threat' in data
    assert data['threat']['asset'] == 'Test Asset'


def test_get_threat_not_found(client, auth_headers):
    """Test getting non-existent threat."""
    response = client.get('/api/threats/99999', headers=auth_headers)
    
    assert response.status_code == 404


def test_delete_threat(client, auth_headers, test_user, app):
    """Test deleting a threat."""
    # Create a test threat
    with app.app_context():
        threat = Threat(
            asset='Test Asset',
            flow='Test flow description',
            stride_categories=['Tampering'],
            dread_score={'damage': 5, 'reproducibility': 5, 'exploitability': 5, 'affected_users': 5, 'discoverability': 5},
            risk_level='Medium'
        )
        from app import db
        db.session.add(threat)
        db.session.commit()
        threat_id = threat.id
    
    response = client.delete(f'/api/threats/{threat_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data


def test_analyze_threat_unauthorized(client):
    """Test threat analysis without authentication."""
    response = client.post(
        '/api/threats/analyze',
        data=json.dumps({
            'asset': 'Test Asset',
            'flow': 'Test flow',
            'auto_score': True
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 401

