# Project Sentinel - Backend

## Overview
Flask-based REST API backend for Project Sentinel DevSecOps framework with advanced threat modeling capabilities.

## Technology Stack
- Python 3.11
- Flask 3.0
- Flask-RESTful
- SQLAlchemy (PostgreSQL)
- Flask-JWT-Extended
- Flask-SocketIO (WebSockets)
- Alembic (migrations)
- Marshmallow (validation)

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Docker (optional)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (use .docker.env):
```bash
export POSTGRES_DB=sentinal
export POSTGRES_USER=sentinal_user
export POSTGRES_PASSWORD=your_password
export SECRET_KEY=your_secret_key
export JWT_SECRET_KEY=your_jwt_secret
export GITHUB_CLIENT_ID=your_github_client_id
export GITHUB_CLIENT_SECRET=your_github_client_secret
```

4. Initialize database:
```bash
flask db upgrade
```

5. Run application:
```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/github` - GitHub OAuth initiation
- `GET /api/auth/github/callback` - GitHub OAuth callback
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/profile` - Get user profile

### Threat Modeling (Advanced)
- `POST /api/threats/analyze` - Analyze threat with advanced STRIDE/DREAD
  - Supports `auto_score` parameter for automated DREAD scoring
  - Returns pattern matches, component types, confidence scores
- `GET /api/threats` - List all threats
- `GET /api/threats/{id}` - Get threat details
- `PUT /api/threats/{id}` - Update threat
- `DELETE /api/threats/{id}` - Delete threat
- `GET /api/threats/analytics` - Threat statistics and trends
- `GET /api/threats/{id}/similar` - Find similar threats
- `GET /api/threats/{id}/vulnerabilities` - Get linked vulnerabilities
- `POST /api/threats/{id}/link-vulnerability` - Link vulnerability to threat
- `GET /api/threats/with-vulnerabilities` - Get threats with linked vulnerabilities
- `PUT /api/threats/vulnerabilities/{id}/status` - Update vulnerability status
- `GET /api/threats/templates` - List threat templates
- `GET /api/threats/templates/{id}` - Get threat template details
- `POST /api/threats/templates` - Create threat template (Admin)
- `PUT /api/threats/templates/{id}` - Update threat template (Admin)
- `DELETE /api/threats/templates/{id}` - Delete threat template (Admin)
- `POST /api/threats/templates/{id}/create-threat` - Create threat from template

### Requirements Management
- `GET /api/requirements` - List all requirements
- `POST /api/requirements` - Create requirement
- `GET /api/requirements/{id}` - Get requirement details
- `PUT /api/requirements/{id}` - Update requirement
- `DELETE /api/requirements/{id}` - Delete requirement
- `GET /api/requirements/{id}/controls` - Get security controls
- `POST /api/requirements/{id}/controls` - Add security control
- `GET /api/requirements/export` - Export requirements
- `GET /api/requirements/compliance` - Compliance dashboard (Admin only)

### CI/CD Dashboard
- `GET /api/cicd/runs` - List CI/CD runs
- `GET /api/cicd/runs/{id}` - Get run details
- `POST /api/cicd/trigger` - Trigger CI/CD run
- `GET /api/cicd/dashboard` - Dashboard statistics
- `GET /api/cicd/scans/sonarqube/latest` - Latest SonarQube scan
- `GET /api/cicd/scans/zap/latest` - Latest ZAP scan
- `GET /api/cicd/scans/trivy/latest` - Latest Trivy scan

### API Tokens (Admin Only)
- `POST /api/auth/api-tokens` - Create API token
- `GET /api/auth/api-tokens` - List API tokens
- `POST /api/auth/api-tokens/{id}/revoke` - Revoke API token

## Advanced Features

### Threat Pattern Recognition
- 14 pre-defined threat patterns (SQL Injection, XSS, Authentication Bypass, etc.)
- Regex-based pattern matching
- Component type detection
- Confidence scoring

### Automated DREAD Scoring
- Pattern-based score suggestions
- Context-aware adjustments
- Confidence indicators
- Manual override support

### Vulnerability Correlation
- Link threats to SonarQube findings
- Link threats to OWASP ZAP alerts
- Link threats to Trivy scan results
- Status tracking (linked, resolved, false_positive)

### Threat Similarity Detection
- Text similarity using TF-IDF
- STRIDE category overlap
- DREAD score similarity
- Asset type matching

### Threat Templates
- 8 pre-built templates
- Create custom templates
- Create threats from templates

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black app/
flake8 app/
bandit -r app/
mypy app/
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## Database Schema

### Core Tables
- `users` - User accounts with roles
- `requirements` - Security requirements
- `security_controls` - Security controls linked to requirements
- `threats` - Threat records with STRIDE/DREAD analysis
- `threat_vulnerabilities` - Links between threats and vulnerabilities
- `threat_templates` - Pre-built threat templates
- `ci_cd_runs` - CI/CD pipeline runs
- `api_tokens` - API tokens for webhook authentication

## Security Features

- JWT-based authentication with refresh tokens
- Role-based access control (Admin/Developer)
- Input validation with Marshmallow schemas
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (Flask-Limiter)
- CORS protection
- Secure password hashing (bcrypt)
- API token authentication for webhooks

## Docker

Build and run with Docker:
```bash
docker build -t sentinal-backend .
docker run -p 5000:5000 --env-file .docker.env sentinal-backend
```

Or use docker-compose from project root:
```bash
docker compose --env-file .docker.env up -d backend
```

## WebSocket Support

Real-time updates via Flask-SocketIO:
- Scan status updates
- Dashboard refresh notifications
- Threat analysis progress

## Environment Variables

See `.docker.env.example` for all required environment variables.

## API Documentation

API documentation is available at `/api/docs` (if Swagger is configured) or see `techdocs/api-documentation.md`.
