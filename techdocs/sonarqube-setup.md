# SonarQube Setup Guide

## Default Credentials

When SonarQube starts for the first time, it uses **default credentials**:

- **Username**: `admin`
- **Password**: `admin`

**IMPORTANT**: On first login, SonarQube will force you to change the password.

## Getting Your SonarQube Token

### Option 1: From Local Container (Recommended for Development)

1. **Access SonarQube Web UI**:
   - URL: http://localhost:9000
   - Login with: `admin` / `admin` (or your changed password)

2. **Generate Token**:
   - Click on your profile icon (top right)
   - Go to **My Account** → **Security**
   - Under **Generate Tokens**, enter a token name (e.g., "sentinal-ci")
   - Click **Generate**
   - **Copy the token immediately** (you won't be able to see it again)

3. **Add to .docker.env**:
   ```bash
   SONARQUBE_TOKEN=your_generated_token_here
   ```

### Option 2: From SonarCloud (If Using Cloud Service)

If you're using SonarCloud (sonarcloud.io) instead of local SonarQube:

1. Go to https://sonarcloud.io
2. Login with GitHub
3. Go to **My Account** → **Security**
4. Generate a token
5. Use SonarCloud URL in `.docker.env`:
   ```bash
   SONARQUBE_URL=https://sonarcloud.io
   SONARQUBE_TOKEN=your_sonarcloud_token
   ```

## Which One to Use?

- **Local Container (SonarQube)**: Use for development/testing
  - URL: http://localhost:9000
  - Token from local container
  
- **SonarCloud**: Use for production/CI/CD
  - URL: https://sonarcloud.io
  - Token from SonarCloud website

## Current Setup

Your docker-compose.yml is configured to use **local SonarQube container**.

To use SonarCloud instead, update `.docker.env`:
```bash
SONARQUBE_URL=https://sonarcloud.io
SONARQUBE_TOKEN=your_sonarcloud_token
```

## Accessing SonarQube

- **Web UI**: http://localhost:9000
- **Default Login**: admin / admin
- **After first login**: You'll be prompted to change password

## Troubleshooting

If SonarQube is not accessible:
1. Check if container is running: `docker compose ps sonarqube`
2. Check logs: `docker compose logs sonarqube`
3. Wait a few minutes - SonarQube takes time to start up
4. Check port 9000 is not blocked

