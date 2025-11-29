# 🛡️ Project Sentinel — Secure-by-Design DevSecOps Framework

A comprehensive DevSecOps platform integrating Security-by-Design principles into every stage of the Software Development Lifecycle (SDLC). Project Sentinel provides automated threat modeling, security requirements management, and CI/CD pipeline security scanning.

## 📑 Table of Contents

- [Repository Structure](#-repository-structure)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Code Quality](#-code-quality)
- [Security Features](#-security-features)
- [API Endpoints](#-api-endpoints)
- [Technology Stack](#️-technology-stack)
- [Advanced Threat Modeling Features](#-advanced-threat-modeling-features)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Support](#-support)

## 📦 Repository Structure

This is a **monorepo** containing both backend and frontend applications:

### Backend (`/backend`)
- **Purpose**: RESTful API server providing threat modeling, requirements management, and CI/CD integration services
- **Technology**: Python 3.11, Flask 3.0, PostgreSQL 15
- **Key Features**: JWT authentication, WebSocket support, security scanning integrations (SonarQube, ZAP, Trivy)

### Frontend (`/frontend`)
- **Purpose**: Modern web application providing an intuitive UI for threat modeling, requirements management, and CI/CD dashboard
- **Technology**: React 19, Vite 7, Tailwind CSS
- **Key Features**: Real-time updates, interactive visualizations, cybersecurity-themed design

## ✨ Features

### 🔐 Advanced Threat Modeling Toolkit
- **Intelligent STRIDE Analysis**: Advanced pattern recognition with 14 threat patterns
- **Automated DREAD Scoring**: AI-powered risk assessment with confidence indicators
- **Component Detection**: Automatic identification of system components
- **Threat Templates**: 8 pre-built templates for common scenarios
- **Vulnerability Correlation**: Link threats to actual scan findings (SonarQube, ZAP, Trivy)
- **Threat Similarity Detection**: Find similar threats for learning and improvement
- **Visual Analytics**: Interactive diagrams, threat matrices, and analytics dashboard

### 📋 Secure Requirements Management Portal
- Create, read, update, delete security requirements
- Enforce one-to-one mapping of security controls to functional requirements
- Admin dashboard for compliance auditing (OWASP ASVS)
- Export security mappings (CSV/JSON)
- Link requirements to threats and vulnerabilities

### 🚀 Security-by-Design CI/CD Pipeline
- **SAST**: SonarQube integration for static analysis
- **DAST**: OWASP ZAP integration for dynamic analysis
- **Container Scanning**: Trivy integration for vulnerability detection
- Real-time scan results dashboard
- Webhook integration for GitHub Actions
- API token authentication for webhooks

### 🔑 Authentication & Authorization
- JWT-based authentication
- GitHub OAuth integration
- Role-based access control (Admin/Developer)
- API token management (Admin only)
- Secure token refresh mechanism

## 🏗️ Architecture

### Frontend (React + Vite)
- **Framework**: React 19 with Vite 7
- **State Management**: Zustand
- **Routing**: React Router v6
- **Styling**: Tailwind CSS (Cybersecurity theme)
- **Visualization**: ReactFlow, Recharts
- **Animations**: Framer Motion
- **Validation**: Zod

### Backend (Python + Flask)
- **Framework**: Flask 3.0 with Flask-RESTful
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: Flask-JWT-Extended
- **Real-time**: Flask-SocketIO (WebSockets)
- **Security**: Flask-Limiter, Flask-Talisman

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **Database**: PostgreSQL
- **Security Tools**: SonarQube, OWASP ZAP, Trivy

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd sentinal
```

2. **Configure environment variables**
```bash
cp .docker.env.example .docker.env
# Edit .docker.env with your configuration
```

3. **Start the application**
```bash
docker compose --env-file .docker.env up -d --build
```

4. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost/api
- SonarQube: http://localhost:9000
- OWASP ZAP: http://localhost:8090
- Trivy: http://localhost:8080

### Default Credentials
- **SonarQube**: admin/admin (change on first login)
- **PostgreSQL**: Configured in `.docker.env`

## 📚 Documentation

### Theory Documentation
- [`theorydocs/stride-dread-methodology.md`](theorydocs/stride-dread-methodology.md) - Complete STRIDE/DREAD guide
- [`theorydocs/how-stride-dread-works.md`](theorydocs/how-stride-dread-works.md) - Implementation details

### Technical Documentation
- [`backend/README.md`](backend/README.md) - Backend API documentation
- [`frontend/README.md`](frontend/README.md) - Frontend documentation
- [`techdocs/`](techdocs/) - Architecture diagrams, API docs, setup guides
- [`techdocs/ngrok-setup.md`](techdocs/ngrok-setup.md) - ngrok setup for local development with GitHub Actions

## 🔧 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python run.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
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

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🔍 Code Quality

### Backend Code Quality Checks

Run linting and formatting checks for Python code:

```bash
# Check code style with flake8
cd backend
flake8 app/

# Check code formatting with black
cd backend
black --check app/
```

**Note**: Configuration files (`.flake8` and `pyproject.toml`) are automatically used by these tools. The CI/CD pipeline runs these checks automatically on every commit.

## 🔒 Security Features

- **Input Validation**: Marshmallow schemas, Zod validation
- **SQL Injection Prevention**: Parameterized queries, SQLAlchemy ORM
- **XSS Prevention**: Output encoding, Content Security Policy
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Rate Limiting**: Flask-Limiter for API protection
- **Secrets Management**: Environment variables, secure storage
- **HTTPS**: HSTS headers, secure cookies
- **GDPR Compliance**: Data retention policies, user data management

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/github` - GitHub OAuth initiation
- `GET /api/auth/github/callback` - GitHub OAuth callback
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/profile` - Get user profile

### Threat Modeling
- `POST /api/threats/analyze` - Analyze threat (with auto-scoring)
- `GET /api/threats` - List all threats
- `GET /api/threats/{id}` - Get threat details
- `PUT /api/threats/{id}` - Update threat
- `DELETE /api/threats/{id}` - Delete threat
- `GET /api/threats/analytics` - Threat statistics
- `GET /api/threats/{id}/similar` - Find similar threats
- `GET /api/threats/{id}/vulnerabilities` - Get linked vulnerabilities
- `POST /api/threats/{id}/link-vulnerability` - Link vulnerability to threat
- `GET /api/threats/templates` - List threat templates
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

## 🛠️ Technology Stack

| Category | Technology |
|----------|-----------|
| Frontend Framework | React 19, Vite 7 |
| Backend Framework | Flask 3.0, Flask-RESTful |
| Database | PostgreSQL 15 |
| State Management | Zustand |
| Styling | Tailwind CSS |
| Visualization | ReactFlow, Recharts |
| Authentication | JWT, GitHub OAuth |
| Security Scanning | SonarQube, OWASP ZAP, Trivy |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Testing | PyTest, Jest |
| Linting | ESLint, Prettier, flake8, bandit, black, mypy |

## 📈 Advanced Threat Modeling Features

### Pattern Recognition
- 14 pre-defined threat patterns covering OWASP Top 10
- Regex-based pattern matching
- Confidence scoring for each pattern
- Component-aware detection

### Automated DREAD Scoring
- Pattern-based score suggestions
- Context-aware adjustments
- Confidence indicators
- Manual override capability
- Explanations for each score

### Enhanced Mitigations
- Pattern-specific recommendations
- Component-specific mitigations
- Risk-level prioritized actions
- Effectiveness ratings
- Difficulty indicators

### Visualization
- **Threat Diagrams**: Interactive data flow visualization
- **Threat Matrix**: STRIDE vs Asset heatmap
- **Vulnerability Correlation**: Visual threat-vulnerability relationships
- **Analytics Dashboard**: Comprehensive threat statistics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OWASP for security guidelines and methodologies
- Microsoft for STRIDE threat modeling framework
- All open-source contributors and libraries used in this project

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Project Sentinel** - Building secure software, one threat at a time 🛡️


<!-- Updated by saad -->


<!-- Updated by saad -->
