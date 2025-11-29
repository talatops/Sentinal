"""Test database models."""
from app import db
from app.models.user import User
from app.models.threat import Threat
from app.models.requirement import Requirement
from app.models.cicd import CICDRun
from app.models.api_token import APIToken
from app.core.security import hash_password


def test_user_model(app, db_session):
    """Test User model."""
    user = User(
        username='modeltest',
        email='modeltest@example.com',
        password_hash=hash_password('password123'),
        role='Developer'
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.username == 'modeltest'
    assert user.email == 'modeltest@example.com'
    assert user.role == 'Developer'
    assert user.is_active is True
    assert user.created_at is not None


def test_user_to_dict(app, test_user):
    """Test User to_dict method."""
    with app.app_context():
        # Merge user back into session to access attributes
        user = db.session.merge(test_user)
        user_dict = user.to_dict()
        
        assert 'id' in user_dict
        assert 'username' in user_dict
        assert 'email' in user_dict
        assert 'role' in user_dict
        assert 'password_hash' not in user_dict  # Should not expose password


def test_threat_model(app, db_session):
    """Test Threat model."""
    threat = Threat(
        asset='Test Asset',
        flow='Test flow description',
        stride_categories=['Tampering', 'Information Disclosure'],
        dread_score={
            'damage': 5,
            'reproducibility': 5,
            'exploitability': 5,
            'affected_users': 5,
            'discoverability': 5
        },
        risk_level='Medium',
        mitigation='Test mitigation'
    )
    db_session.add(threat)
    db_session.commit()
    
    assert threat.id is not None
    assert threat.asset == 'Test Asset'
    assert threat.risk_level == 'Medium'
    assert len(threat.stride_categories) == 2


def test_threat_to_dict(app, db_session):
    """Test Threat to_dict method."""
    threat = Threat(
        asset='Test Asset',
        flow='Test flow',
        stride_categories=['Tampering'],
        dread_score={'damage': 5, 'reproducibility': 5, 'exploitability': 5, 'affected_users': 5, 'discoverability': 5},
        risk_level='Low'
    )
    db_session.add(threat)
    db_session.commit()
    
    threat_dict = threat.to_dict()
    assert 'id' in threat_dict
    assert 'asset' in threat_dict
    assert 'risk_level' in threat_dict


def test_requirement_model(app, db_session, test_user):
    """Test Requirement model."""
    with app.app_context():
        # Merge user back into session to access ID
        user = db.session.merge(test_user)
        requirement = Requirement(
            title='Test Requirement',
            description='Test description',
            security_controls=['MFA', 'Encryption'],
            created_by=user.id,
            status='Draft'
        )
        db_session.add(requirement)
        db_session.commit()
        
        assert requirement.id is not None
        assert requirement.title == 'Test Requirement'
        assert requirement.status == 'Draft'
        assert len(requirement.security_controls) == 2


def test_requirement_to_dict(app, db_session, test_user):
    """Test Requirement to_dict method."""
    with app.app_context():
        # Merge user back into session to access ID
        user = db.session.merge(test_user)
        requirement = Requirement(
            title='Test Requirement',
            security_controls=['MFA'],
            created_by=user.id
        )
        db_session.add(requirement)
        db_session.commit()
        
        req_dict = requirement.to_dict()
        assert 'id' in req_dict
        assert 'title' in req_dict
        assert 'status' in req_dict


def test_cicd_run_model(app, db_session):
    """Test CICDRun model."""
    run = CICDRun(
        commit_hash='abc123',
        branch='main',
        status='Success',
        total_vulnerabilities=5,
        critical_vulnerabilities=1
    )
    db_session.add(run)
    db_session.commit()
    
    assert run.id is not None
    assert run.commit_hash == 'abc123'
    assert run.status == 'Success'
    assert run.total_vulnerabilities == 5


def test_cicd_run_to_dict(app, db_session):
    """Test CICDRun to_dict method."""
    run = CICDRun(
        commit_hash='def456',
        branch='develop',
        status='Running'
    )
    db_session.add(run)
    db_session.commit()
    
    run_dict = run.to_dict()
    assert 'id' in run_dict
    assert 'commit_hash' in run_dict
    assert 'status' in run_dict


def test_api_token_model(app, db_session, admin_user):
    """Test APIToken model."""
    with app.app_context():
        # Merge user back into session to access ID
        user = db.session.merge(admin_user)
        token = APIToken(
            name='Test Token',
            token_hash='hashed_token_value',
            token_prefix='sent_abc123',
            created_by=user.id,
            scopes=['webhook:write']
        )
        db_session.add(token)
        db_session.commit()
        
        assert token.id is not None
        assert token.name == 'Test Token'
        assert token.is_active is True
        assert 'webhook:write' in token.scopes


def test_api_token_to_dict(app, db_session, admin_user):
    """Test APIToken to_dict method."""
    with app.app_context():
        # Merge user back into session to access ID
        user = db.session.merge(admin_user)
        token = APIToken(
            name='Test Token',
            token_hash='hashed_token',
            token_prefix='sent_test',
            created_by=user.id
        )
        db_session.add(token)
        db_session.commit()
        
        token_dict = token.to_dict()
        assert 'id' in token_dict
        assert 'name' in token_dict
        assert 'token_hash' not in token_dict  # Should not expose hash
        assert 'is_active' in token_dict

