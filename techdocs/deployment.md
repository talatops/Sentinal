# Project Sentinel - Deployment Guide

## Deployment Options

### Docker Compose (Recommended)

Best for single-server deployments.

1. **Prepare server**
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

2. **Clone repository**
```bash
git clone <repository-url>
cd sentinal
```

3. **Configure environment**
```bash
cp .docker.env .docker.env.production
# Edit with production values
```

4. **Deploy**
```bash
docker-compose -f docker-compose.yml --env-file .docker.env.production up -d
```

5. **Initialize database**
```bash
docker-compose exec backend flask db upgrade
```

### Kubernetes

For scalable, production deployments.

1. **Create Kubernetes manifests**
2. **Deploy PostgreSQL**
3. **Deploy backend**
4. **Deploy frontend**
5. **Configure ingress**

### Cloud Platforms

#### Railway
1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push

#### Heroku
1. Create Procfile
2. Set environment variables
3. Deploy via Git

## Environment Configuration

### Required Variables

```bash
# Database
POSTGRES_DB=sentinal
POSTGRES_USER=sentinal_user
POSTGRES_PASSWORD=<strong_password>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Backend
SECRET_KEY=<32_char_minimum>
JWT_SECRET_KEY=<32_char_minimum>
FLASK_ENV=production

# GitHub OAuth
GITHUB_CLIENT_ID=<your_client_id>
GITHUB_CLIENT_SECRET=<your_client_secret>
GITHUB_CALLBACK_URL=<production_url>/callback

# Security Tools
SONARQUBE_TOKEN=<your_token>
```

### Security Best Practices

1. **Use strong passwords**
   - Minimum 32 characters for secrets
   - Unique passwords for each environment

2. **Enable HTTPS**
   - Configure SSL certificates
   - Update GITHUB_CALLBACK_URL to HTTPS
   - Set FLASK_TLS=true

3. **Restrict CORS**
   - Set CORS_ORIGINS to specific domains
   - Remove wildcard (*) in production

4. **Database Security**
   - Use separate read/write users
   - Enable SSL connections
   - Regular backups

## Monitoring

### Health Checks

All services include health checks:
- Backend: `/api/health`
- Database: PostgreSQL health check
- Frontend: Nginx status

### Logging

- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs postgres`

### Metrics

Consider integrating:
- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking

## Backup Strategy

### Database Backups

```bash
# Manual backup
docker-compose exec postgres pg_dump -U sentinal_user sentinal > backup.sql

# Automated backup (cron)
0 2 * * * docker-compose exec -T postgres pg_dump -U sentinal_user sentinal > /backups/sentinal_$(date +\%Y\%m\%d).sql
```

### Volume Backups

```bash
# Backup volumes
docker run --rm -v sentinal_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Scaling

### Horizontal Scaling

1. **Backend**
   - Run multiple backend instances
   - Use load balancer
   - Share session storage

2. **Frontend**
   - Use CDN for static assets
   - Multiple Nginx instances

3. **Database**
   - Read replicas for read operations
   - Connection pooling

### Vertical Scaling

- Increase container resources
- Optimize database queries
- Add caching layer (Redis)

## Maintenance

### Updates

1. **Pull latest code**
```bash
git pull origin main
```

2. **Rebuild containers**
```bash
docker-compose build
docker-compose up -d
```

3. **Run migrations**
```bash
docker-compose exec backend flask db upgrade
```

### Rollback

1. **Revert code**
```bash
git checkout <previous_commit>
```

2. **Rebuild and restart**
```bash
docker-compose build
docker-compose up -d
```

3. **Rollback database** (if needed)
```bash
docker-compose exec backend flask db downgrade
```

## Security Updates

1. **Update dependencies regularly**
```bash
# Backend
pip list --outdated
pip install --upgrade <package>

# Frontend
npm outdated
npm update
```

2. **Scan for vulnerabilities**
```bash
# Backend
bandit -r app/

# Containers
trivy image sentinal-backend:latest
```

3. **Update base images**
- Regularly update Docker base images
- Monitor security advisories

## Disaster Recovery

1. **Regular backups**
2. **Test restore procedures**
3. **Document recovery steps**
4. **Maintain off-site backups**

## Performance Optimization

1. **Database indexing**
2. **Query optimization**
3. **Caching strategies**
4. **CDN for static assets**
5. **Compression (gzip)**

