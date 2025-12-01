# Test Suite Documentation

## Overview

This directory contains comprehensive test suites for Project Sentinel backend API. The tests cover API endpoints, security services, database models, and business logic validation.

## Test Structure

### Test Categories

The test suite is organized into the following categories:

1. **API Endpoint Tests** - Test REST API endpoints and their behavior
2. **Service Tests** - Test business logic and service layer functionality
3. **Model Tests** - Test database models and data validation
4. **Security Tests** - Test authentication, authorization, and security features

## Test Files

### API Endpoint Tests

#### `test_api_auth.py`
Tests authentication and authorization API endpoints.

**Test Coverage:**
- User registration (success, duplicate username, invalid data)
- User login (success, invalid credentials, non-existent user)
- User profile retrieval (authenticated, unauthorized)
- Token refresh mechanism
- Input validation and error handling

**Key Tests:**
- `test_register_user` - Successful user registration
- `test_register_duplicate_username` - Duplicate username prevention
- `test_register_invalid_data` - Input validation
- `test_login_success` - Successful authentication
- `test_login_invalid_credentials` - Invalid password handling
- `test_get_profile` - Authenticated profile access
- `test_get_profile_unauthorized` - Unauthorized access prevention
- `test_refresh_token` - Token refresh functionality

#### `test_api_cicd.py`
Tests CI/CD pipeline and security scanning API endpoints.

**Test Coverage:**
- CI/CD run listing and details
- Triggering CI/CD runs
- Dashboard statistics
- Security scanner integration (mocked)
- Unauthorized access prevention

**Key Tests:**
- `test_get_cicd_runs` - List all CI/CD runs
- `test_get_cicd_run_detail` - Get specific run details
- `test_trigger_cicd_run` - Trigger new CI/CD run with mocked scanners
- `test_get_dashboard` - Dashboard statistics aggregation
- `test_cicd_endpoints_unauthorized` - Authentication requirement

#### `test_api_requirements.py`
Tests security requirements management API endpoints.

**Test Coverage:**
- Requirement CRUD operations
- Security controls validation
- Compliance dashboard (Admin only)
- Role-based access control (RBAC)

**Key Tests:**
- `test_create_requirement` - Create requirement with security controls
- `test_create_requirement_missing_controls` - Validation of required controls
- `test_get_requirements` - List all requirements
- `test_get_requirement_detail` - Get specific requirement
- `test_update_requirement` - Update requirement details
- `test_delete_requirement` - Delete requirement
- `test_get_compliance_dashboard` - Admin-only compliance dashboard
- `test_get_compliance_dashboard_non_admin` - RBAC enforcement

#### `test_api_threat_model.py`
Tests threat modeling and analysis API endpoints.

**Test Coverage:**
- Threat analysis with STRIDE/DREAD
- Auto-scoring and manual scoring modes
- Threat CRUD operations
- Input validation

**Key Tests:**
- `test_analyze_threat_auto_score` - Automated DREAD scoring
- `test_analyze_threat_manual_score` - Manual DREAD score input
- `test_analyze_threat_missing_required_fields` - Input validation
- `test_get_threats` - List all threats
- `test_get_threat_detail` - Get specific threat
- `test_delete_threat` - Delete threat
- `test_analyze_threat_unauthorized` - Authentication requirement

### Service Tests

#### `test_services_stride.py`
Tests STRIDE threat analysis engine.

**Test Coverage:**
- Basic STRIDE category detection
- Advanced pattern matching
- Component type detection
- Mitigation recommendations

**Key Tests:**
- `test_stride_analysis_basic` - Basic threat analysis
- `test_stride_analysis_with_database` - Database-related threats
- `test_stride_analysis_with_authentication` - Authentication threats
- `test_stride_analysis_with_trust_boundary` - Trust boundary analysis
- `test_stride_analysis_advanced` - Advanced pattern matching
- `test_stride_analysis_advanced_with_patterns` - Pattern detection
- `test_get_mitigation_recommendations` - Mitigation suggestions
- `test_get_mitigation_recommendations_low_risk` - Risk-based mitigations

#### `test_services_dread.py`
Tests DREAD risk scoring service.

**Test Coverage:**
- Automated DREAD score suggestions
- User-provided score adjustments
- Risk level calculations
- Confidence scoring
- Score explanations

**Key Tests:**
- `test_suggest_dread_scores` - Basic score suggestions
- `test_suggest_dread_scores_with_user_input` - User score integration
- `test_suggest_dread_scores_high_risk_scenario` - High-risk scenarios
- `test_suggest_dread_scores_low_risk_scenario` - Low-risk scenarios
- `test_dread_score_explanations` - Score explanations
- `test_dread_score_confidence` - Confidence indicators

### Model Tests

#### `test_models.py`
Tests database models and data serialization.

**Test Coverage:**
- User model creation and validation
- Threat model structure
- Requirement model with security controls
- CI/CD run model
- API token model
- Data serialization (to_dict methods)
- Security (password hash not exposed)

**Key Tests:**
- `test_user_model` - User creation and attributes
- `test_user_to_dict` - User serialization (password hash excluded)
- `test_threat_model` - Threat creation and STRIDE/DREAD storage
- `test_requirement_model` - Requirement with security controls
- `test_cicd_run_model` - CI/CD run tracking
- `test_api_token_model` - API token management

### Authentication Tests

#### `test_auth.py`
Tests authentication utilities and security functions.

**Test Coverage:**
- Password hashing and verification
- Input sanitization
- Output encoding
- Security event logging

## Test Fixtures

### `conftest.py`
Provides shared pytest fixtures for all tests.

**Available Fixtures:**

- `app` - Flask application instance (testing configuration)
- `client` - Flask test client for making HTTP requests
- `test_user` - Standard test user (Developer role)
- `admin_user` - Admin test user (Admin role)
- `auth_headers` - JWT authentication headers for test user
- `admin_headers` - JWT authentication headers for admin user
- `db_session` - Database session for direct database operations

**Usage Example:**
```python
def test_example(client, auth_headers, test_user):
    response = client.get('/api/endpoint', headers=auth_headers)
    assert response.status_code == 200
```

## Test Utilities

### `utils.py`
Contains helper functions and mock data generators for tests.

**Functions:**
- Mock scan results generators
- Test data factories
- Common assertion helpers

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test File
```bash
pytest tests/test_api_auth.py
```

### Run Specific Test
```bash
pytest tests/test_api_auth.py::test_login_success
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=term-missing
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Tests Matching Pattern
```bash
pytest -k "auth"  # Run all tests with "auth" in the name
```

## Test Coverage

### Security Testing

The test suite includes security-focused tests:

1. **Authentication Testing:**
   - Password hashing verification
   - JWT token generation and validation
   - Token refresh mechanism
   - Unauthorized access prevention

2. **Authorization Testing:**
   - Role-based access control (RBAC)
   - Admin vs Developer permissions
   - Protected endpoint access

3. **Input Validation Testing:**
   - Schema validation (Marshmallow)
   - SQL injection prevention (ORM usage)
   - XSS prevention (output encoding)
   - Invalid data handling

4. **Error Handling Testing:**
   - Generic error messages (no sensitive info exposure)
   - Proper HTTP status codes
   - Error response structure

### Functional Testing

- **CRUD Operations:** All create, read, update, delete operations tested
- **Edge Cases:** Boundary conditions, missing data, invalid inputs
- **Integration:** API endpoints with database interactions
- **Business Logic:** STRIDE/DREAD calculations, risk assessments

## Test Data Management

- Tests use isolated test database (configured via `TEST_DATABASE_URL`)
- Database is created and dropped for each test run
- Test fixtures provide clean data for each test
- No test data persists between test runs

## Continuous Integration

Tests are automatically run in CI/CD pipeline (GitHub Actions):
- On every push to `main` and `develop` branches
- On pull requests
- With coverage reporting
- With linting checks (flake8, black)

## Best Practices

1. **Isolation:** Each test is independent and doesn't rely on other tests
2. **Fixtures:** Use provided fixtures for common setup
3. **Mocking:** External services (scanners) are mocked to avoid dependencies
4. **Assertions:** Clear, descriptive assertions with meaningful error messages
5. **Naming:** Test names clearly describe what is being tested

## Adding New Tests

When adding new tests:

1. Follow existing naming conventions (`test_<functionality>`)
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies
4. Test both success and failure cases
5. Include edge cases and boundary conditions
6. Add docstrings explaining what the test validates

## Test Statistics

- **Total Test Files:** 9
- **Test Categories:** API endpoints, Services, Models, Authentication
- **Coverage Areas:** Authentication, Authorization, Threat Modeling, Requirements Management, CI/CD Integration

## Notes

- All tests use the `testing` configuration from `app.core.config.TestingConfig`
- Database migrations are handled automatically in test fixtures
- JWT tokens are generated using test secret keys
- External services (SonarQube, ZAP, Trivy) are mocked in tests
