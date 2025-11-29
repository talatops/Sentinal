"""Test CI/CD API endpoints."""
import json
from unittest.mock import patch, MagicMock
from app.models.cicd import CICDRun


def test_get_cicd_runs(client, auth_headers, test_user, app):
    """Test getting CI/CD runs."""
    # Create a test run
    with app.app_context():
        from app import db
        run = CICDRun(
            commit_hash='abc123',
            branch='main',
            status='Success'
        )
        db.session.add(run)
        db.session.commit()
    
    response = client.get('/api/cicd/runs', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'runs' in data
    assert isinstance(data['runs'], list)


def test_get_cicd_run_detail(client, auth_headers, test_user, app):
    """Test getting CI/CD run details."""
    # Create a test run
    with app.app_context():
        from app import db
        run = CICDRun(
            commit_hash='abc123',
            branch='main',
            status='Success'
        )
        db.session.add(run)
        db.session.commit()
        run_id = run.id
    
    response = client.get(f'/api/cicd/runs/{run_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'run' in data
    assert data['run']['commit_hash'] == 'abc123'


@patch('app.services.security_scanner.SecurityScanner')
def test_trigger_cicd_run(mock_scanner, client, auth_headers):
    """Test triggering a CI/CD run."""
    # Mock scanner responses
    mock_instance = MagicMock()
    mock_instance.run_sast_scan.return_value = {'total': 0, 'critical': 0}
    mock_instance.run_trivy_scan.return_value = {'total': 0, 'critical': 0}
    mock_instance.run_dast_scan.return_value = {'total': 0, 'critical': 0}
    mock_scanner.return_value = mock_instance
    
    response = client.post(
        '/api/cicd/trigger',
        data=json.dumps({
            'commit_hash': 'test123',
            'branch': 'main'
        }),
        content_type='application/json',
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'run' in data


def test_get_dashboard(client, auth_headers, test_user, app):
    """Test getting dashboard data."""
    # Create test runs
    with app.app_context():
        from app import db
        run1 = CICDRun(commit_hash='abc123', branch='main', status='Success')
        run2 = CICDRun(commit_hash='def456', branch='main', status='Failed')
        db.session.add(run1)
        db.session.add(run2)
        db.session.commit()
    
    response = client.get('/api/cicd/dashboard', headers=auth_headers)
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_runs' in data
    assert 'successful_runs' in data
    assert 'failed_runs' in data


def test_cicd_endpoints_unauthorized(client):
    """Test CI/CD endpoints without authentication."""
    response = client.get('/api/cicd/runs')
    assert response.status_code == 401
    
    response = client.post('/api/cicd/trigger', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 401

