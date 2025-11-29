"""Test requirements management API endpoints."""
import json
from app.models.requirement import Requirement


def test_create_requirement(client, auth_headers):
    """Test creating a requirement."""
    response = client.post(
        '/api/requirements',
        data=json.dumps({
            'title': 'Secure Authentication',
            'description': 'Implement secure authentication mechanism',
            'security_controls': [
                {
                    'name': 'MFA',
                    'description': 'Multi-factor authentication',
                    'owasp_asvs_level': 'Level 2'
                }
            ],
            'status': 'Draft',
            'owasp_asvs_level': 'Level 2'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'requirement' in data
    assert data['requirement']['title'] == 'Secure Authentication'


def test_create_requirement_missing_controls(client, auth_headers):
    """Test creating requirement without security controls."""
    response = client.post(
        '/api/requirements',
        data=json.dumps({
            'title': 'Test Requirement',
            'description': 'Test description',
            'security_controls': []
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_get_requirements(client, auth_headers, test_user, app):
    """Test getting all requirements."""
    # Create a test requirement
    with app.app_context():
        from app import db
        requirement = Requirement(
            title='Test Requirement',
            description='Test description',
            security_controls=['MFA'],
            created_by=test_user.id,
            status='Draft'
        )
        db.session.add(requirement)
        db.session.commit()
    
    response = client.get('/api/requirements', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'requirements' in data
    assert isinstance(data['requirements'], list)


def test_get_requirement_detail(client, auth_headers, test_user, app):
    """Test getting requirement details."""
    # Create a test requirement
    with app.app_context():
        from app import db
        requirement = Requirement(
            title='Test Requirement',
            description='Test description',
            security_controls=['MFA'],
            created_by=test_user.id,
            status='Draft'
        )
        db.session.add(requirement)
        db.session.commit()
        req_id = requirement.id
    
    response = client.get(f'/api/requirements/{req_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'requirement' in data
    assert data['requirement']['title'] == 'Test Requirement'


def test_update_requirement(client, auth_headers, test_user, app):
    """Test updating a requirement."""
    # Create a test requirement
    with app.app_context():
        from app import db
        requirement = Requirement(
            title='Test Requirement',
            description='Test description',
            security_controls=['MFA'],
            created_by=test_user.id,
            status='Draft'
        )
        db.session.add(requirement)
        db.session.commit()
        req_id = requirement.id
    
    response = client.put(
        f'/api/requirements/{req_id}',
        data=json.dumps({
            'title': 'Updated Requirement',
            'status': 'Approved'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'requirement' in data
    assert data['requirement']['title'] == 'Updated Requirement'


def test_delete_requirement(client, auth_headers, test_user, app):
    """Test deleting a requirement."""
    # Create a test requirement
    with app.app_context():
        from app import db
        requirement = Requirement(
            title='Test Requirement',
            description='Test description',
            security_controls=['MFA'],
            created_by=test_user.id,
            status='Draft'
        )
        db.session.add(requirement)
        db.session.commit()
        req_id = requirement.id
    
    response = client.delete(f'/api/requirements/{req_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data


def test_get_compliance_dashboard(client, admin_headers, test_user, app):
    """Test getting compliance dashboard (Admin only)."""
    # Create test requirements
    with app.app_context():
        from app import db
        req1 = Requirement(
            title='Req 1',
            security_controls=['Control 1'],
            created_by=test_user.id
        )
        req2 = Requirement(
            title='Req 2',
            security_controls=['Control 2'],
            created_by=test_user.id
        )
        db.session.add(req1)
        db.session.add(req2)
        db.session.commit()
    
    response = client.get('/api/requirements/compliance', headers=admin_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_requirements' in data
    assert 'compliance_rate' in data


def test_get_compliance_dashboard_non_admin(client, auth_headers):
    """Test compliance dashboard access for non-admin."""
    response = client.get('/api/requirements/compliance', headers=auth_headers)
    
    assert response.status_code == 403

