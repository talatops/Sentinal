# Project Sentinel - Comprehensive Testing Plan

## Overview

This document provides a complete step-by-step testing plan for Project Sentinel, including setup for ngrok (main app) and Cloudflare Tunnel (SonarQube), secure secret management in GitHub Actions, and comprehensive testing workflows.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Service Configuration](#service-configuration)
4. [Tunnel Setup](#tunnel-setup)
5. [GitHub Secrets Configuration](#github-secrets-configuration)
6. [Testing Workflow](#testing-workflow)
7. [Security Checklist](#security-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Docker & Docker Compose** (latest version)
- **Git** (for version control)
- **ngrok** (for main application tunnel)
- **Cloudflare Tunnel (cloudflared)** (for SonarQube)
- **GitHub Account** (with repository access)
- **curl** (for API testing)
- **jq** (for JSON parsing, optional but recommended)

### Required Accounts

- **ngrok Account** (free tier sufficient): https://dashboard.ngrok.com/signup
- **Cloudflare Account** (free tier sufficient): https://dash.cloudflare.com/sign-up
- **GitHub Account** (with repository admin access)

### Ports Used

| Service | Port | Purpose |
|---------|------|---------|
| Frontend (Nginx) | 80 | Main application (exposed via ngrok) |
| Backend (Flask) | 5000 | API server (proxied through Nginx) |
| SonarQube | 9000 | Code quality analysis (exposed via Cloudflare) |
| Trivy | 8080 | Container scanning (internal) |
| OWASP ZAP | 8090 | Dynamic security testing (internal) |
| PostgreSQL | 5432 | Database (internal only) |

---

## Initial Setup

### Step 1: Clone and Prepare Repository

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd sentinal

# Verify Docker is running
docker --version
docker compose version
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .docker.env.example .docker.env

# Generate secure secrets
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(32))"
```

**Edit `.docker.env`** with the generated values and your configuration:

```bash
# Database Configuration
POSTGRES_DB=sentinal
POSTGRES_USER=sentinal_user
POSTGRES_PASSWORD=<generated_password_above>

# Backend Configuration
FLASK_ENV=production
SECRET_KEY=<generated_secret_key_above>
JWT_SECRET_KEY=<generated_jwt_secret_key_above>

# GitHub OAuth Configuration
# Get from: https://github.com/settings/developers -> OAuth Apps
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_CALLBACK_URL=http://localhost/callback  # Will be updated with ngrok URL

# Security Tools Configuration
TRIVY_API_URL=http://trivy:8080
OWASP_ZAP_API_URL=http://zap:8090
SONARQUBE_URL=http://sonarqube:9000  # Will be updated with Cloudflare URL
SONARQUBE_TOKEN=  # Will be generated after SonarQube setup
SONARQUBE_PROJECT_KEY=sentinal

# Frontend Configuration
VITE_API_URL=http://localhost/api  # Will be updated with ngrok URL

# CORS Configuration
CORS_ORIGINS=http://localhost,http://localhost:80
```

**⚠️ IMPORTANT**: Never commit `.docker.env` to version control!

### Step 3: Start Services Locally

```bash
# Start all services
docker compose --env-file .docker.env up -d --build

# Verify all containers are running
docker compose ps

# Check logs if any service fails
docker compose logs backend
docker compose logs frontend
docker compose logs sonarqube
```

**Expected Output:**
```
NAME                  STATUS
sentinal-postgres     Up (healthy)
sentinal-backend      Up
sentinal-frontend     Up
sentinal-trivy        Up
sentinal-zap          Up
sentinal-sonarqube    Up
```

### Step 4: Wait for Services to Initialize

```bash
# Wait for SonarQube (takes 2-5 minutes)
echo "Waiting for SonarQube to start..."
while ! curl -s http://localhost:9000/api/system/status | grep -q "UP"; do
  echo "SonarQube is starting... (this may take a few minutes)"
  sleep 10
done
echo "✅ SonarQube is ready!"
```

### Step 5: Initialize SonarQube

1. **Access SonarQube Web UI:**
   ```bash
   # Open in browser
   open http://localhost:9000  # macOS
   xdg-open http://localhost:9000  # Linux
   start http://localhost:9000  # Windows
   ```

2. **Login:**
   - Username: `admin`
   - Password: `admin`
   - **You will be forced to change the password on first login**

3. **Generate SonarQube Token:**
   - Click profile icon (top right) → **My Account**
   - Go to **Security** tab
   - Under **Generate Tokens**, enter name: `sentinal-ci`
   - Click **Generate**
   - **⚠️ Copy the token immediately** (you won't see it again)
   - Update `.docker.env`:
     ```bash
     SONARQUBE_TOKEN=<your_generated_token>
     ```

4. **Restart backend to pick up new token:**
   ```bash
   docker compose restart backend
   ```

---

## Tunnel Setup

### Part A: Tunnel Setup for Main Application

**You have two options:**

**Option 1: Use Cloudflare Named Tunnel (Recommended - Stable URL)**
- Uses your custom domain (e.g., `sentinal.jurassiq-dev.org`)
- URL doesn't change on restart
- More reliable for production/testing

**Option 2: Use ngrok (Simpler - URL changes on restart)**
- Quick setup
- URL changes each time you restart
- Good for quick testing

#### Option 1: Cloudflare Named Tunnel for Main App (Recommended)

**This setup uses separate Cloudflare tunnels for the main app and SonarQube:**

1. **Create tunnel for main app:**
   ```bash
   cloudflared tunnel create sentinal
   ```
   
   **Expected Output:**
   ```
   Created tunnel sentinal with id <tunnel-id>
   Tunnel credentials written to /root/.cloudflared/<tunnel-id>.json
   ```

2. **Create config file for sentinal tunnel:**
   ```bash
   cat > ~/.cloudflared/config-sentinal.yml << 'EOF'
   tunnel: <sentinal-tunnel-id>
   credentials-file: /root/.cloudflared/<sentinal-tunnel-id>.json
   
   ingress:
     - hostname: sentinal.jurassiq-dev.org
       service: http://localhost:80
     - service: http_status:404
   EOF
   ```
   Replace `<sentinal-tunnel-id>` with the actual tunnel ID from step 1.

3. **Add DNS route:**
   ```bash
   cloudflared tunnel route dns sentinal sentinal.jurassiq-dev.org
   ```

4. **Start the sentinal tunnel:**
   ```bash
   cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal
   ```
   
   **To run in background:**
   ```bash
   cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal > /tmp/sentinal-tunnel.log 2>&1 &
   ```

5. **Your main app URL will be:**
   ```
   https://sentinal.jurassiq-dev.org
   ```

**Note:** You'll also need to set up a separate tunnel for SonarQube (see Part B below).

---

#### Option 2: ngrok Setup (Alternative)

#### Step 1: Install ngrok

**macOS:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
# Download and install
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

**Windows:**
Download from https://ngrok.com/download and add to PATH

#### Step 2: Authenticate ngrok

```bash
# Sign up at https://dashboard.ngrok.com/signup (if not done)
# Get authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_NGROK_AUTH_TOKEN
```

#### Step 3: Start ngrok Tunnel

```bash
# Start tunnel for port 80 (Nginx - serves both frontend and backend)
ngrok http 80
```

**Expected Output:**
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:80
```

**⚠️ IMPORTANT:** Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

**Note:** The ngrok URL changes each time you restart ngrok (unless using paid plan). Keep this terminal open or run in background.

#### Step 4: Update Configuration with ngrok URL

```bash
# Update .docker.env
GITHUB_CALLBACK_URL=https://abc123.ngrok-free.app/callback
VITE_API_URL=https://abc123.ngrok-free.app/api
CORS_ORIGINS=https://abc123.ngrok-free.app,http://localhost,http://localhost:80

# Restart services to apply changes
docker compose --env-file .docker.env restart backend frontend
```

#### Step 5: Test ngrok Tunnel

```bash
# Test backend health endpoint
curl https://abc123.ngrok-free.app/api/health

# Expected response:
# {"status": "healthy", "service": "sentinal-api"}

# Test frontend
curl -I https://abc123.ngrok-free.app/

# Expected: HTTP/1.1 200 OK
```

**Keep ngrok running** - you'll need it for GitHub Actions webhooks.

---

### Part B: Tunnel Setup for SonarQube

**You have two options:**

**Option 1: Use ngrok (Simplest - Recommended)**
- Since you're already using ngrok for the main app
- Just run another ngrok instance for port 9000
- More reliable than trycloudflare.com

**Option 2: Use Cloudflare Tunnel**
- More complex setup
- Can use your domain if configured

#### Option 1: ngrok for SonarQube (Recommended)

**In a NEW terminal window:**

```bash
# Start ngrok for SonarQube (port 9000)
ngrok http 9000
```

**Expected Output:**
```
Forwarding  https://xyz789.ngrok-free.app -> http://localhost:9000
```

**Copy the HTTPS URL** and use it for `SONARQUBE_URL`

**Advantages:**
- ✅ Same tool you're already using
- ✅ More reliable than trycloudflare.com
- ✅ Works immediately
- ⚠️ URL changes on restart (but that's fine for testing)

---

#### Option 2: Cloudflare Named Tunnel for SonarQube

**This setup uses a separate Cloudflare tunnel for SonarQube:**

#### Step 1: Install Cloudflare Tunnel (cloudflared)

**macOS:**
```bash
brew install cloudflare/cloudflare/cloudflared
```

**Linux:**
```bash
# Download binary
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

**Windows:**
Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

#### Step 2: Login to Cloudflare

```bash
# This will open browser for authentication
cloudflared tunnel login
```

Select your domain (e.g., `jurassiq-dev.org`).

#### Step 3: Create Named Tunnel for SonarQube

```bash
# Create a new tunnel named "sonarqube"
cloudflared tunnel create sonarqube
```

**Expected Output:**
```
Created tunnel sonarqube with id <tunnel-id>
Tunnel credentials written to /root/.cloudflared/<tunnel-id>.json
```

#### Step 4: Create Tunnel Configuration

```bash
# Create config file for sonarqube tunnel
cat > ~/.cloudflared/config-sonarqube.yml << 'EOF'
tunnel: <sonarqube-tunnel-id>
credentials-file: /root/.cloudflared/<sonarqube-tunnel-id>.json

ingress:
  - hostname: sonarqube.jurassiq-dev.org
    service: http://localhost:9000
  - service: http_status:404
EOF
```

Replace `<sonarqube-tunnel-id>` with the actual tunnel ID from step 3.

#### Step 5: Add DNS Route

```bash
# Add DNS route (this creates a CNAME record automatically)
cloudflared tunnel route dns sonarqube sonarqube.jurassiq-dev.org
```

**Expected Output:**
```
Added CNAME sonarqube.jurassiq-dev.org which will route to this tunnel
```

#### Step 6: Start the Tunnel

```bash
# Run the tunnel (keep this terminal open)
cloudflared tunnel --config ~/.cloudflared/config-sonarqube.yml run sonarqube
```

**To run in background:**
```bash
cloudflared tunnel --config ~/.cloudflared/config-sonarqube.yml run sonarqube > /tmp/sonarqube-tunnel.log 2>&1 &
```

**Your SonarQube URL will be:**
```
https://sonarqube.jurassiq-dev.org
```

**Note:** DNS propagation may take 1-2 minutes. Wait before testing.

---

#### Alternative: Use Quick Tunnel (Simpler - URL changes on restart)

**Quick Tunnel is the easiest method:**
- ✅ Shows URL immediately - no configuration needed
- ✅ No DNS setup required
- ✅ Works instantly
- ⚠️ URL changes each time you restart (but that's fine for testing)

**Skip the named tunnel complexity - use this instead:**

#### Step 3: Run Quick Tunnel

```bash
# Run quick tunnel (no setup needed - simplest method!)
# ⚠️ IMPORTANT: Use localhost, NOT the Docker container name!
cloudflared tunnel --url http://localhost:9000
```

**⚠️ CRITICAL:** 
- ✅ **Correct:** `http://localhost:9000` (cloudflared runs on host, connects to localhost)
- ❌ **Wrong:** `http://sonarqube:9000` (this only works inside Docker network)

**Expected Output:**
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it shortly (it may take some time to be reachable) at: |
|  https://abc123-def456-xyz789.cfargotunnel.com                                            |
+--------------------------------------------------------------------------------------------+
```

**⚠️ IMPORTANT:** Copy the Cloudflare tunnel URL immediately (e.g., `https://abc123-def456-xyz789.cfargotunnel.com`)

**Keep this terminal running** - the tunnel needs to stay active.

**Note:** This URL will change each time you restart the tunnel, but that's fine for testing. Just copy the new URL if you restart.

1. **Verify your domain is in Cloudflare:**
   - Go to: https://dash.cloudflare.com
   - Check that `jurassiq-dev.org` is listed in your domains
   - If not, add it to Cloudflare first

2. **Add DNS route for SonarQube:**
   ```bash
   # Add DNS route (this creates a CNAME record automatically)
   cloudflared tunnel route dns add sonarqube.jurassiq-dev.org sonarqube
   ```

   **Expected Output:**
   ```
   Successfully added DNS route sonarqube.jurassiq-dev.org to tunnel sonarqube
   ```

   **⚠️ IMPORTANT:** If you see `10.0.0.0/8` in Routes instead of your hostname, the DNS route wasn't created properly!

3. **Verify the route was created:**
   ```bash
   # List all routes for your tunnel
   cloudflared tunnel route dns list sonarqube
   ```

   **Expected Output:**
   ```
   sonarqube.jurassiq-dev.org
   ```

   **If you see `10.0.0.0/8` instead, the DNS route wasn't added. Try:**
   ```bash
   # Remove any incorrect routes first (if needed)
   cloudflared tunnel route ip delete 10.0.0.0/8 sonarqube
   
   # Add the DNS route again
   cloudflared tunnel route dns add sonarqube.jurassiq-dev.org sonarqube
   ```

4. **Check in Cloudflare Dashboard:**
   - Go to: https://dash.cloudflare.com
   - Select your domain `jurassiq-dev.org`
   - Go to **DNS** → **Records**
   - You should see a CNAME record: `sonarqube` → `b612a4ca-a33b-469f-b383-8fe4c951735f.cfargotunnel.com`
   - Also check: https://one.dash.cloudflare.com → **Access** → **Tunnels** → Click on `sonarqube`
   - The Routes section should show: `sonarqube.jurassiq-dev.org` (NOT `10.0.0.0/8`)
   
   **If Routes shows `10.0.0.0/8`:**
   - This is an internal network route, not a DNS hostname
   - You need to add the DNS route using the command above
   - Or manually create the CNAME record in Cloudflare DNS

5. **Your SonarQube URL will be:**
   ```
   https://sonarqube.jurassiq-dev.org
   ```

**Note:** DNS propagation may take a few minutes. Wait 2-5 minutes after adding the route before testing.

#### Step 7: Start Both Tunnels

**To run both tunnels simultaneously:**

```bash
# Terminal 1: Start sentinal tunnel
cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal

# Terminal 2: Start sonarqube tunnel
cloudflared tunnel --config ~/.cloudflared/config-sonarqube.yml run sonarqube
```

**Or run both in background:**
```bash
# Start sentinal tunnel
cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal > /tmp/sentinal-tunnel.log 2>&1 &

# Start sonarqube tunnel
cloudflared tunnel --config ~/.cloudflared/config-sonarqube.yml run sonarqube > /tmp/sonarqube-tunnel.log 2>&1 &

# Check both are running
cloudflared tunnel list
```

**Expected Output:**
```
ID                                   NAME      CREATED              CONNECTIONS
<sentinal-id>                        sentinal  ...                  2xkhi01, 1xsin02
<sonarqube-id>                       sonarqube ...                  2xkhi01, 1xsin11
```

#### Step 8: Update Configuration

```bash
# Update .docker.env with your Cloudflare tunnel URL
# For named tunnel with custom domain:
SONARQUBE_URL=https://sonarqube.jurassiq-dev.org

# OR if using quick tunnel:
# SONARQUBE_URL=https://abc123-def456-xyz789.cfargotunnel.com

# Restart backend to apply changes
docker compose restart backend
```

#### Step 9: Test Both Tunnels

```bash
# Test main app tunnel
curl https://sentinal.jurassiq-dev.org/api/health

# Expected: {"service":"sentinal-api","status":"healthy"}

# Test SonarQube tunnel
curl https://sonarqube.jurassiq-dev.org/api/system/status

# Expected: {"status":"UP","version":"..."}

# Test in browser
open https://sentinal.jurassiq-dev.org  # macOS
open https://sonarqube.jurassiq-dev.org  # macOS
```

```bash
# Test SonarQube through Cloudflare
# For named tunnel:
curl https://sonarqube.jurassiq-dev.org/api/system/status

# OR for quick tunnel:
# curl https://abc123-def456-xyz789.cfargotunnel.com/api/system/status

# Expected: {"status":"UP","version":"..."}

# Test in browser
open https://sonarqube.jurassiq-dev.org  # macOS
xdg-open https://sonarqube.jurassiq-dev.org  # Linux
start https://sonarqube.jurassiq-dev.org  # Windows
```

**If you get 404 error (connection works but wrong response):**

This means the tunnel is connected but not forwarding correctly. Try:

1. **Verify SonarQube is running locally:**
   ```bash
   curl http://localhost:9000/api/system/status
   ```
   - Should return: `{"status":"UP","version":"..."}`
   - If this fails, SonarQube isn't running - start it: `docker compose up -d sonarqube`

2. **Try accessing root path:**
   ```bash
   # Try the root URL instead
   curl https://follow-assess-inch-scholarships.trycloudflare.com/
   ```
   - This might work if the tunnel is forwarding but path routing is different

3. **Check tunnel is forwarding correctly:**
   - Make sure you're running: `cloudflared tunnel --url http://localhost:9000`
   - NOT: `cloudflared tunnel run sonarqube` (that's for named tunnels)
   - The tunnel should show "Registered tunnel connection" in the output

4. **Restart the tunnel:**
   ```bash
   # Stop current tunnel (Ctrl+C)
   # Wait 10 seconds
   # Start fresh
   cloudflared tunnel --url http://localhost:9000
   ```
   - Copy the new URL and test again

5. **Verify SonarQube is accessible:**
   ```bash
   # Make sure SonarQube responds locally
   curl -v http://localhost:9000/api/system/status
   ```
   - If this doesn't work, the tunnel can't forward to it

**Troubleshooting:**

- **Connection errors:**
  - Wait 1-2 minutes for the tunnel to fully initialize
  - Make sure the tunnel terminal is still running (don't close it)
  - Verify SonarQube is running locally: `curl http://localhost:9000/api/system/status`
  - Check tunnel is active: Look for "Your quick Tunnel has been created!" message

- **URL changed after restart:**
  - Quick tunnel URLs change each time you restart
  - Just copy the new URL from the tunnel output
  - Update `SONARQUBE_URL` in `.docker.env` with the new URL
  - Restart backend: `docker compose restart backend`
  - Update GitHub Secret `SONARQUBE_URL` with the new URL

- **Tunnel not working / Getting 404:**
  - ⚠️ **Most common issue:** Using wrong URL format
  - ✅ **Correct:** `cloudflared tunnel --url http://localhost:9000`
  - ❌ **Wrong:** `cloudflared tunnel --url http://sonarqube:9000` (container name doesn't work from host)
  
  **If tunnel is connected but still getting 404:**
  1. **Wait 1-2 minutes** - Quick tunnels can take time to fully establish
  2. **Verify SonarQube is accessible:** `curl http://localhost:9000/api/system/status` should work
  3. **Check tunnel is still running:** Look for "Registered tunnel connection" in tunnel output
  4. **Try in browser:** Sometimes browser works when curl doesn't
  5. **Check for firewall:** Make sure port 9000 isn't blocked
  6. **Try restarting tunnel:** Stop (Ctrl+C) and restart with `cloudflared tunnel --url http://localhost:9000`
  7. **Alternative:** If trycloudflare.com doesn't work, use your Cloudflare account:
     ```bash
     # Login first
     cloudflared tunnel login
     # Then use quick tunnel (it will use your account)
     cloudflared tunnel --url http://localhost:9000
     ```

**Keep cloudflared running** - you'll need it for SonarQube access from GitHub Actions.

---

## GitHub Secrets Configuration

### Step 1: Access GitHub Repository Settings

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Step 2: Add Required Secrets

Add the following secrets (one at a time):

#### 2.1: Main Application URL

- **Name:** `SENTINAL_API_URL`
- **Value:** 
  - If using Cloudflare: `https://sentinal.jurassiq-dev.org` (your Cloudflare tunnel URL)
  - If using ngrok: `https://abc123.ngrok-free.app` (your ngrok URL)
- **Description:** Main application URL for webhook callbacks

#### 2.2: API Token for Webhooks

- **Name:** `SENTINAL_API_TOKEN`
- **Value:** (Generate from Sentinal dashboard - see Step 3 below)
- **Description:** API token for authenticating webhook requests

#### 2.3: SonarQube URL

- **Name:** `SONARQUBE_URL`
- **Value:** 
  - If using ngrok: `https://xyz789.ngrok-free.app` (your ngrok URL for port 9000)
  - If using Cloudflare named tunnel: `https://sonarqube.jurassiq-dev.org` (your custom domain)
  - If using Cloudflare quick tunnel: `https://abc123-def456-xyz789.cfargotunnel.com` (your quick tunnel URL)
- **Description:** SonarQube server URL for SAST scans
- **Note:** 
  - Named tunnel URL is stable (doesn't change)
  - Quick tunnel URL changes on restart - update the secret with the new URL

#### 2.4: SonarQube Token

- **Name:** `SONARQUBE_TOKEN`
- **Value:** (The token you generated in SonarQube UI)
- **Description:** SonarQube authentication token

#### 2.5: SonarQube Project Key

- **Project key used in CI:** `sentinal`
- The repository root now contains `sonar-project.properties` with the following important fields:
  - `sonar.projectKey=sentinal`
  - `sonar.projectName=Sentinal`
  - `sonar.sources=backend,frontend`
  - `sonar.python.coverage.reportPaths=backend/coverage.xml`
- **What to do:**
  1. In your SonarQube UI (`https://sonarqube.jurassiq-dev.org`), create or confirm a project whose key matches `sentinal`.
  2. Ensure the token stored in `SONARQUBE_TOKEN` has *Execute Analysis* rights on that project.
  3. If you ever rename the project, you MUST update both the SonarQube project key and the `sonar-project.properties` file (otherwise CI will fail with `sonar.projectKey` errors).

This properties file is what the GitHub Actions `sast` job reads, so no additional CLI flags are required—just keep the file in sync with the SonarQube project.

#### 2.6: GitHub OAuth (Optional - if using GitHub OAuth)

- **Name:** `GITHUB_CLIENT_ID`
- **Value:** (Your GitHub OAuth Client ID)

- **Name:** `GITHUB_CLIENT_SECRET`
- **Value:** (Your GitHub OAuth Client Secret)

### Step 3: Generate API Token in Sentinal Dashboard

1. **Access Sentinal Dashboard:**
   ```bash
   # Open in browser
   open https://abc123.ngrok-free.app  # Use your ngrok URL
   ```

2. **Login:**
   - Register a new account or use existing credentials
   - Ensure you have **Admin** role (first user is typically admin)

3. **Create API Token:**
   - Navigate to **API Tokens** page (or **Settings** → **API Tokens`)
   - Click **Create New Token**
   - Enter name: `GitHub Actions CI/CD`
   - Select scopes: `webhook:write` or `webhook:*`
   - Click **Generate**
   - **⚠️ Copy the token immediately** (format: `sent_...`)

4. **Add to GitHub Secrets:**
   - Go back to GitHub repository → Settings → Secrets
   - Add secret: `SENTINAL_API_TOKEN` = `<your_generated_token>`

---

## Testing Workflow

### Phase 1: Local Service Testing

#### Test 1.1: Verify All Services Are Running

```bash
# Check container status
docker compose ps

# Expected: All services should be "Up"
```

#### Test 1.2: Test Backend API

```bash
# Health check
curl http://localhost/api/health

# Expected: {"status": "healthy", "service": "sentinal-api"}

# API root
curl http://localhost/api/

# Expected: API information JSON
```

#### Test 1.3: Test Frontend

```bash
# Open in browser
open http://localhost

# Verify:
# - Frontend loads correctly
# - No console errors
# - Can navigate between pages
```

#### Test 1.4: Test SonarQube

```bash
# Check SonarQube status
curl http://localhost:9000/api/system/status

# Expected: {"status":"UP","version":"..."}

# Open in browser
open http://localhost:9000
```

#### Test 1.5: Test Security Tools

```bash
# Test Trivy
curl http://localhost:8080/health

# Test ZAP
curl http://localhost:8090/JSON/core/view/version/
```

### Phase 2: Tunnel Testing

#### Test 2.1: Test Main App Tunnel

```bash
# If using Cloudflare:
SENTINAL_URL="https://sentinal.jurassiq-dev.org"

# OR if using ngrok:
# SENTINAL_URL="https://abc123.ngrok-free.app"

# Test backend through tunnel
curl $SENTINAL_URL/api/health

# Expected: {"service":"sentinal-api","status":"healthy"}

# Test frontend through tunnel
curl -I $SENTINAL_URL/

# Expected: HTTP/2 200 OK

# Test API endpoint
curl $SENTINAL_URL/api/

# Expected: All should return 200 OK
```

#### Test 2.2: Test SonarQube Tunnel

```bash
# If using ngrok for SonarQube:
SONARQUBE_URL="https://xyz789.ngrok-free.app"  # Your ngrok URL for port 9000

# OR if using Cloudflare named tunnel:
SONARQUBE_URL="https://sonarqube.jurassiq-dev.org"  # Your custom domain

# OR if using Cloudflare quick tunnel:
SONARQUBE_URL="https://abc123-def456-xyz789.cfargotunnel.com"  # Your quick tunnel URL

# Test SonarQube through tunnel
curl $SONARQUBE_URL/api/system/status

# Expected: {"status":"UP","version":"..."}
```

### Phase 3: Authentication Testing

#### Test 3.1: User Registration

```bash
# Register new user
curl -X POST https://abc123.ngrok-free.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Expected: {"message": "User registered successfully", "user": {...}}
```

#### Test 3.2: User Login

```bash
# Login
curl -X POST https://abc123.ngrok-free.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Expected: {"access_token": "...", "refresh_token": "..."}
# Save the access_token for next tests
```

#### Test 3.3: API Token Creation (Admin Only)

```bash
# Create API token (requires admin role)
ACCESS_TOKEN="<your_access_token_from_login>"

curl -X POST https://abc123.ngrok-free.app/api/auth/api-tokens \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "name": "Test Token",
    "scopes": "webhook:write",
    "expires_in_days": 365
  }'

# Expected: {"token": "sent_...", "name": "Test Token", ...}
# Save the token for webhook testing
```

### Phase 4: CI/CD Integration Testing

#### Test 4.1: Manual Webhook Test

```bash
# Test webhook endpoint (replace with your values)
API_TOKEN="<your_api_token>"
NGROK_URL="https://abc123.ngrok-free.app"

# Test SonarQube webhook
curl -X POST $NGROK_URL/api/cicd/webhook/sonarqube \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{
    "commit_hash": "test-commit-123",
    "branch": "main",
    "status": "completed",
    "results": {
      "issues": [],
      "metrics": {
        "bugs": 0,
        "vulnerabilities": 0,
        "code_smells": 0
      }
    }
  }'

# Expected: {"message": "sonarqube results received", "run_id": 1, "status": "Success"}
```

#### Test 4.2: Trigger GitHub Actions Workflow

1. **Make a test commit:**
   ```bash
   # Create a test file
   echo "# Test" > test.md
   git add test.md
   git commit -m "test: Trigger CI/CD pipeline"
   git push origin develop  # or main
   ```

2. **Monitor GitHub Actions:**
   - Go to repository → **Actions** tab
   - Click on the running workflow
   - Watch for:
     - ✅ Linting job completes
     - ✅ Testing job completes
     - ✅ Build job completes
     - ✅ Smoke test job completes
     - ✅ SAST scan (SonarQube) job completes
     - ✅ Container scan (Trivy) job completes
     - ✅ DAST scan (ZAP) job completes

3. **Verify Webhook Calls:**
   - Check GitHub Actions logs for webhook success messages
   - Look for: `✅ Sent results to dashboard` or similar

#### Test 4.3: Verify Results in Dashboard

1. **Access Dashboard:**
   ```bash
   open https://abc123.ngrok-free.app
   ```

2. **Navigate to CI/CD Dashboard:**
   - Login to Sentinal
   - Go to **CI/CD Dashboard** page
   - Verify:
     - New run appears with commit hash
     - SonarQube results are displayed
     - Trivy results are displayed
     - ZAP results are displayed
     - Status is correct (Success/Blocked/Failed)

### Phase 5: Security Scanning Testing

#### Test 5.1: Manual SonarQube Scan

```bash
# Trigger SonarQube scan via API
ACCESS_TOKEN="<your_access_token>"

curl -X POST https://abc123.ngrok-free.app/api/cicd/scans/sonarqube/trigger \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "commit_hash": "manual-test-001",
    "branch": "main"
  }'

# Expected: {"run_id": 2, "results": {...}}
```

#### Test 5.2: Manual Trivy Scan

```bash
curl -X POST https://abc123.ngrok-free.app/api/cicd/scans/trivy/trigger \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "image_name": "sentinal-backend:latest",
    "commit_hash": "manual-test-001"
  }'
```

#### Test 5.3: Manual ZAP Scan

```bash
curl -X POST https://abc123.ngrok-free.app/api/cicd/scans/zap/trigger \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "target_url": "http://localhost",
    "commit_hash": "manual-test-001"
  }'
```

### Phase 6: End-to-End Testing

#### Test 6.1: Complete CI/CD Flow

1. **Make a code change:**
   ```bash
   # Create a test file with intentional issue (for SonarQube to find)
   echo "def unused_function():\n    pass" >> backend/app/test_file.py
   git add backend/app/test_file.py
   git commit -m "test: Add test file for CI/CD"
   git push origin develop
   ```

2. **Monitor Complete Pipeline:**
   - Watch GitHub Actions workflow
   - Verify all jobs complete
   - Check for webhook success messages

3. **Verify in Dashboard:**
   - Check CI/CD Dashboard shows new run
   - Verify scan results are displayed
   - Check vulnerability counts are correct

#### Test 6.2: Test Webhook Failure Handling

```bash
# Test with invalid token
curl -X POST https://abc123.ngrok-free.app/api/cicd/webhook/sonarqube \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer invalid_token" \
  -d '{"commit_hash": "test"}'

# Expected: {"error": "Invalid or expired API token"}, 401
```

#### Test 6.3: Test Rate Limiting

```bash
# Make multiple rapid requests
for i in {1..10}; do
  curl -X POST https://abc123.ngrok-free.app/api/cicd/webhook/sonarqube \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_TOKEN" \
    -d '{"commit_hash": "test-'$i'"}'
  sleep 0.1
done

# Expected: Some requests may be rate-limited (429 status)
```

---

## Security Checklist

### ✅ Pre-Deployment Security Checks

- [ ] All secrets are in GitHub Secrets (not hardcoded)
- [ ] `.docker.env` is in `.gitignore` (verify: `git check-ignore .docker.env`)
- [ ] API tokens have appropriate scopes (least privilege)
- [ ] SonarQube password changed from default
- [ ] Strong passwords generated for all services
- [ ] CORS origins are restricted (not `*` in production)
- [ ] Rate limiting is enabled
- [ ] HTTPS is used for all external URLs (ngrok/Cloudflare)
- [ ] API tokens are rotated regularly
- [ ] Database credentials are strong and unique

### ✅ GitHub Actions Security

- [ ] All secrets are stored in GitHub Secrets
- [ ] No secrets in workflow files (check for hardcoded values)
- [ ] Webhook authentication is working
- [ ] API tokens have expiration dates set
- [ ] Token scopes are minimal (webhook:write only)

### ✅ Network Security

- [ ] ngrok tunnel is using HTTPS
- [ ] Cloudflare tunnel is using HTTPS
- [ ] Internal services are not exposed (PostgreSQL, etc.)
- [ ] Firewall rules are configured (if applicable)

### ✅ Application Security

- [ ] JWT tokens expire correctly
- [ ] Password requirements are enforced
- [ ] SQL injection protection is in place
- [ ] XSS protection headers are set
- [ ] CSRF protection is enabled (if applicable)

---

## Troubleshooting

### Issue: ngrok URL changes on restart

**Solution:**
- Use ngrok paid plan for static URLs, OR
- Update GitHub Secrets each time ngrok restarts, OR
- Use Cloudflare Tunnel for main app (more stable)

### Issue: Cloudflare tunnel not accessible / No hostname shown

**If Routes column shows "--" in Cloudflare dashboard:**

This means your named tunnel has no public URL configured. Solutions:

**Solution 1: Use Quick Tunnel (Easiest)**
```bash
# Stop your named tunnel (Ctrl+C)
# Run quick tunnel instead
cloudflared tunnel --url http://localhost:9000

# This will immediately show you a URL
# Copy the URL and use it for SONARQUBE_URL
```

**Solution 2: Use Quick Tunnel Instead (Simpler)**
```bash
# Stop any named tunnel
# Use quick tunnel instead - much simpler!
cloudflared tunnel --url http://localhost:9000

# Copy the URL that appears
# Update SONARQUBE_URL in .docker.env and GitHub Secrets
```

**Solution 3: Check Tunnel Status**
```bash
# For named tunnels, check tunnel status
cloudflared tunnel info sonarqube

# List all tunnels
cloudflared tunnel list

# Restart tunnel
cloudflared tunnel run sonarqube

# For quick tunnels, restart with URL
cloudflared tunnel --url http://localhost:9000

# Check logs with debug level
cloudflared tunnel run sonarqube --loglevel debug

# Verify local service is accessible
curl http://localhost:9000/api/system/status
```

**Common issues:**
1. **No routes configured** - Use quick tunnel or configure DNS route
2. Tunnel not running - restart it
3. Local service not accessible - check Docker: `docker compose ps sonarqube`
4. URL changed (quick tunnel) - copy new URL from output
5. Named tunnel needs DNS route - configure in Cloudflare dashboard or use quick tunnel

### Issue: GitHub Actions webhook fails with 401

**Solution:**
1. Verify `SENTINAL_API_TOKEN` is correct in GitHub Secrets
2. Check token hasn't expired
3. Verify token has `webhook:write` scope
4. Test token manually:
   ```bash
   curl -X POST https://abc123.ngrok-free.app/api/cicd/webhook/sonarqube \
     -H "Authorization: Bearer $API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"commit_hash": "test"}'
   ```

### Issue: SonarQube scan fails in GitHub Actions

**Solution:**
1. Verify `SONARQUBE_URL` is accessible from internet (test with curl)
2. Check `SONARQUBE_TOKEN` is valid
3. Verify SonarQube project key matches
4. Check SonarQube logs:
   ```bash
   docker compose logs sonarqube
   ```

### Issue: Services not starting

**Solution:**
```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs backend
docker compose logs postgres

# Restart services
docker compose down
docker compose --env-file .docker.env up -d --build

# Check container status
docker compose ps
```

### Issue: Database connection errors

**Solution:**
```bash
# Verify PostgreSQL is healthy
docker compose ps postgres

# Check database logs
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U sentinal_user -d sentinal -c "SELECT 1;"

# Reset database (⚠️ WARNING: Deletes all data)
docker compose down -v
docker compose --env-file .docker.env up -d postgres
sleep 10
docker compose exec backend flask db upgrade
```

### Issue: Frontend can't connect to backend

**Solution:**
1. Verify `VITE_API_URL` is correct in `.docker.env`
2. Check Nginx configuration:
   ```bash
   docker compose exec frontend cat /etc/nginx/nginx.conf
   ```
3. Verify backend is running:
   ```bash
   curl http://localhost/api/health
   ```

---

## Additional Testing Scenarios

### Scenario 1: Multiple Concurrent Scans

```bash
# Trigger multiple scans simultaneously
for i in {1..5}; do
  curl -X POST https://abc123.ngrok-free.app/api/cicd/trigger \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"commit_hash": "concurrent-'$i'", "branch": "main"}' &
done
wait

# Verify all scans complete successfully
```

### Scenario 2: Large Scan Results

```bash
# Test webhook with large payload (simulate many vulnerabilities)
# Create a large JSON payload and test webhook handling
```

### Scenario 3: Network Interruption

1. Stop ngrok tunnel during webhook call
2. Restart ngrok
3. Verify GitHub Actions retries or handles gracefully

### Scenario 4: Service Restart During Scan

```bash
# Start a scan
curl -X POST https://abc123.ngrok-free.app/api/cicd/scans/zap/trigger \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"target_url": "http://localhost"}'

# Restart backend during scan
docker compose restart backend

# Verify scan state is preserved or handled gracefully
```

---

## Maintenance Tasks

### Daily

- [ ] Check Cloudflare tunnels are running (both sentinal and sonarqube)
- [ ] Verify both URLs are accessible:
  - `https://sentinal.jurassiq-dev.org/api/health`
  - `https://sonarqube.jurassiq-dev.org/api/system/status`
- [ ] Monitor GitHub Actions workflow success rate
- [ ] Review security scan results

### Weekly

- [ ] Rotate API tokens (if needed)
- [ ] Review and update secrets
- [ ] Check for service updates
- [ ] Review logs for errors

### Monthly

- [ ] Update dependencies
- [ ] Review security configurations
- [ ] Audit API token usage
- [ ] Review and update documentation

---

## Next Steps

After completing all tests:

1. **Document any issues found** in GitHub Issues
2. **Update configuration** based on test results
3. **Set up monitoring** (optional but recommended)
4. **Configure alerts** for critical failures
5. **Plan for production deployment** (if applicable)

---

## Additional Resources

- [ngrok Documentation](https://ngrok.com/docs)
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Project Sentinel README](./README.md)
- [ngrok Setup Guide](./techdocs/ngrok-setup.md)
- [GitHub Actions Integration](./techdocs/github-actions-integration.md)

---

## Support

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review service logs: `docker compose logs <service-name>`
3. Check GitHub Actions logs for CI/CD issues
4. Open an issue in the repository with:
   - Error messages
   - Steps to reproduce
   - Relevant logs
   - Environment details

---

**Last Updated:** $(date)
**Version:** 1.0
