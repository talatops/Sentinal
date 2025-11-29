"""Test STRIDE analysis engine."""
from app.services.stride_dread_engine import STRIDEEngine


def test_stride_analysis_basic():
    """Test basic STRIDE analysis."""
    engine = STRIDEEngine()
    categories = engine.analyze_threat(
        asset='User Database',
        flow='User submits login credentials via POST request'
    )
    
    assert isinstance(categories, list)
    assert len(categories) > 0
    assert 'Spoofing' in categories or 'Elevation of Privilege' in categories


def test_stride_analysis_with_database():
    """Test STRIDE analysis with database keywords."""
    engine = STRIDEEngine()
    categories = engine.analyze_threat(
        asset='Database',
        flow='User data is stored in PostgreSQL database'
    )
    
    assert 'Tampering' in categories
    assert 'Information Disclosure' in categories
    assert 'Denial of Service' in categories


def test_stride_analysis_with_authentication():
    """Test STRIDE analysis with authentication keywords."""
    engine = STRIDEEngine()
    categories = engine.analyze_threat(
        asset='Auth Service',
        flow='User authenticates using username and password'
    )
    
    assert 'Spoofing' in categories
    assert 'Elevation of Privilege' in categories


def test_stride_analysis_with_trust_boundary():
    """Test STRIDE analysis with trust boundary."""
    engine = STRIDEEngine()
    categories = engine.analyze_threat(
        asset='API Gateway',
        flow='Data crosses network boundary',
        trust_boundary='DMZ'
    )
    
    assert 'Tampering' in categories
    assert 'Information Disclosure' in categories


def test_stride_analysis_advanced():
    """Test advanced STRIDE analysis with pattern matching."""
    engine = STRIDEEngine()
    result = engine.analyze_threat_advanced(
        asset='Payment API',
        flow='User submits payment information through HTTPS API endpoint',
        trust_boundary='External Network'
    )
    
    assert 'stride_categories' in result
    assert isinstance(result['stride_categories'], list)
    assert len(result['stride_categories']) > 0


def test_stride_analysis_advanced_with_patterns():
    """Test advanced analysis returns pattern information."""
    engine = STRIDEEngine()
    result = engine.analyze_threat_advanced(
        asset='User Database',
        flow='SQL injection attack on login endpoint',
        trust_boundary=None
    )
    
    assert 'stride_categories' in result
    assert 'matched_patterns' in result or 'component_types' in result


def test_get_mitigation_recommendations():
    """Test getting mitigation recommendations."""
    engine = STRIDEEngine()
    categories = ['Spoofing', 'Tampering', 'Information Disclosure']
    mitigation = engine.get_mitigation_recommendations(categories, 'High')
    
    assert isinstance(mitigation, str)
    assert len(mitigation) > 0


def test_get_mitigation_recommendations_low_risk():
    """Test mitigation recommendations for low risk."""
    engine = STRIDEEngine()
    categories = ['Information Disclosure']
    mitigation = engine.get_mitigation_recommendations(categories, 'Low')
    
    assert isinstance(mitigation, str)

