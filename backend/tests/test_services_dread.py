"""Test DREAD scoring service."""
from app.services.dread_scorer import DREADScorer


def test_suggest_dread_scores():
    """Test DREAD score suggestions."""
    scorer = DREADScorer()
    result = scorer.suggest_dread_scores(
        asset='User Database',
        flow='SQL injection attack on login endpoint',
        trust_boundary=None
    )
    
    assert 'suggested_scores' in result
    assert 'confidence' in result
    assert 'explanations' in result
    
    scores = result['suggested_scores']
    assert 'damage' in scores
    assert 'reproducibility' in scores
    assert 'exploitability' in scores
    assert 'affected_users' in scores
    assert 'discoverability' in scores
    
    # Verify scores are in valid range
    for score in scores.values():
        assert 0 <= score <= 10


def test_suggest_dread_scores_with_user_input():
    """Test DREAD scoring with user-provided partial scores."""
    scorer = DREADScorer()
    user_scores = {'damage': 8, 'reproducibility': 7}
    
    result = scorer.suggest_dread_scores(
        asset='Payment API',
        flow='Credit card data transmission',
        trust_boundary='External Network',
        user_scores=user_scores
    )
    
    assert 'suggested_scores' in result
    # User-provided scores should be respected or adjusted based on context
    scores = result['suggested_scores']
    assert scores['damage'] >= 7  # Should be high for payment data


def test_suggest_dread_scores_high_risk_scenario():
    """Test DREAD scoring for high-risk scenario."""
    scorer = DREADScorer()
    result = scorer.suggest_dread_scores(
        asset='Admin Panel',
        flow='Unauthorized access to admin functions',
        trust_boundary=None
    )
    
    scores = result['suggested_scores']
    # Admin panel attacks should have high scores
    assert scores['damage'] >= 7
    assert scores['exploitability'] >= 5


def test_suggest_dread_scores_low_risk_scenario():
    """Test DREAD scoring for low-risk scenario."""
    scorer = DREADScorer()
    result = scorer.suggest_dread_scores(
        asset='Public Blog',
        flow='User views blog post',
        trust_boundary=None
    )
    
    scores = result['suggested_scores']
    # Public blog viewing should have lower scores
    assert scores['damage'] <= 5


def test_dread_score_explanations():
    """Test that explanations are provided for scores."""
    scorer = DREADScorer()
    result = scorer.suggest_dread_scores(
        asset='Database',
        flow='Data storage and retrieval',
        trust_boundary=None
    )
    
    explanations = result['explanations']
    assert 'damage' in explanations or 'exploitability' in explanations


def test_dread_score_confidence():
    """Test that confidence scores are provided."""
    scorer = DREADScorer()
    result = scorer.suggest_dread_scores(
        asset='API Endpoint',
        flow='REST API call',
        trust_boundary=None
    )
    
    confidence = result['confidence']
    assert isinstance(confidence, dict)
    # Confidence should be between 0 and 1
    for conf_value in confidence.values():
        assert 0 <= conf_value <= 1

