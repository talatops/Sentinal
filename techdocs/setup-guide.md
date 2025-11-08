# Project Sentinel - Setup Guide

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (for local development)

## Quick Start with Docker

1. **Clone the repository**
```bash
git clone <repository-url>
cd sentinal
```

2. **Configure environment variables**
```bash
cp .docker.env .docker.env.local
# Edit .docker.env.local with your values
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Initialize database**
```bash
docker-compose exec backend flask db upgrade
```

5. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost/api
- SonarQube: http://localhost:9000
- Trivy: http://localhost:8080
- OWASP ZAP: http://localhost:8080

## Local Development Setup

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
export POSTGRES_DB=sentinal
export POSTGRES_USER=sentinal_user
export POSTGRES_PASSWORD=your_password
export SECRET_KEY=your_secret_key
export JWT_SECRET_KEY=your_jwt_secret
```

5. **Run database migrations**
```bash
flask db upgrade
```

6. **Start development server**
```bash
python run.py
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Set environment variables**
```bash
export VITE_API_URL=http://localhost:5000/api
```

4. **Start development server**
```bash
npm run dev
```

## Database Setup

### Using Docker PostgreSQL

The docker-compose.yml includes a PostgreSQL service. No additional setup needed.

### Using Local PostgreSQL

1. **Create database**
```sql
CREATE DATABASE sentinal;
CREATE USER sentinal_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sentinal TO sentinal_user;
```

2. **Update connection string**
```bash
export DATABASE_URL=postgresql://sentinal_user:your_password@localhost:5432/sentinal
```

3. **Run migrations**
```bash
cd backend
flask db upgrade
```

## GitHub OAuth Setup

1. **Create GitHub OAuth App**
   - Go to GitHub Settings → Developer Settings → OAuth Apps
   - Click "New OAuth App"
   - Set Authorization callback URL: `http://localhost/callback`
   - Copy Client ID and Client Secret

2. **Update .docker.env**
```bash
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
GITHUB_CALLBACK_URL=http://localhost/callback
```

## Security Tools Configuration

### SonarQube

1. **Access SonarQube**
   - URL: http://localhost:9000
   - Default credentials: admin/admin

2. **Generate token**
   - Go to My Account → Security → Generate Token
   - Copy token to .docker.env

### Trivy

Trivy runs automatically in Docker. No additional configuration needed.

### OWASP ZAP

OWASP ZAP runs automatically in Docker. API is available at http://localhost:8080

## Creating Admin User

1. **Register via API**
```bash
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_password",
    "role": "Admin"
  }'
```

2. **Or via database**
```sql
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@example.com', '<bcrypt_hash>', 'Admin');
```

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running: `docker-compose ps postgres`
- Verify credentials in .docker.env
- Check network connectivity

### Port Conflicts
- Change ports in docker-compose.yml
- Update .docker.env accordingly

### Frontend Not Loading
- Check Nginx logs: `docker-compose logs nginx`
- Verify frontend build: `docker-compose logs frontend`
- Check API connectivity

### Backend Errors
- Check logs: `docker-compose logs backend`
- Verify database migrations: `docker-compose exec backend flask db current`
- Check environment variables

## Production Deployment

1. **Update .docker.env with production values**
2. **Set strong secrets**
3. **Configure HTTPS**
4. **Update CORS_ORIGINS**
5. **Set up backup strategy**
6. **Configure monitoring**

## Next Steps

- Review [Architecture Documentation](./architecture.md)
- Check [API Documentation](./api-documentation.md)
- Read [Deployment Guide](./deployment.md)

