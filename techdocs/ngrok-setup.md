# Setting Up ngrok for Local Development with GitHub Actions

## Overview

When running Project Sentinel locally, GitHub Actions runners cannot access `localhost` URLs. To enable webhook integration between GitHub Actions and your local Sentinal dashboard, you need to expose your local services using ngrok.

## What is ngrok?

ngrok creates a secure tunnel from a public URL to your local machine, allowing external services (like GitHub Actions) to reach your local development environment.

## Setup Instructions

### Step 1: Install ngrok

**macOS:**
```bash
brew install ngrok/ngrok/ngrok
```

**Linux:**
```bash
# Download from https://ngrok.com/download
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

**Windows:**
Download from https://ngrok.com/download and add to PATH

### Step 2: Sign up for ngrok (Free)

1. Go to https://dashboard.ngrok.com/signup
2. Create a free account
3. Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken

### Step 3: Configure ngrok

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Step 4: Expose Sentinal (Frontend + Backend via Nginx)

Start your Sentinal application:
```bash
docker compose --env-file .docker.env up -d
```

In a new terminal, expose port 80 (where Nginx is running):
```bash
ngrok http 80
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:80
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

**Important:** Since Nginx is running on port 80 and acts as a reverse proxy:
- `https://your-ngrok-url.ngrok-free.app/` → Frontend (React app)
- `https://your-ngrok-url.ngrok-free.app/api` → Backend API (proxied to Flask)
- `https://your-ngrok-url.ngrok-free.app/socket.io` → WebSocket connections

So exposing port 80 with ngrok exposes **both** frontend and backend through Nginx!

### Step 5: Expose SonarQube (Optional)

If you want to use local SonarQube with GitHub Actions:

```bash
ngrok http 9000
```

Copy the HTTPS URL for SonarQube.

### Step 6: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

#### Required for Dashboard Webhooks:
- **`SENTINAL_API_URL`**: Your ngrok URL (e.g., `https://abc123.ngrok-free.app`)
- **`SENTINAL_API_TOKEN`**: API token from Sentinal dashboard (Admin → API Tokens)

#### Optional for SonarQube:
- **`SONARQUBE_URL`**: Your SonarQube ngrok URL (e.g., `https://xyz789.ngrok-free.app`)
- **`SONARQUBE_TOKEN`**: SonarQube authentication token

### Step 7: Create API Token in Sentinal

1. Start Sentinal locally
2. Log in as Admin
3. Go to **API Tokens** page
4. Create a new token with appropriate scopes
5. Copy the token and add it to GitHub Secrets as `SENTINAL_API_TOKEN`

## Important Notes

### ngrok Free Tier Limitations:
- **URL changes** on each restart (unless you use a paid plan)
- **Session timeout** after 2 hours of inactivity
- **Connection limits** apply

### For Production:
- Use a static domain or paid ngrok plan
- Or deploy Sentinal to a public server (AWS, Azure, etc.)
- Or use a VPN/tunnel service

### Keeping ngrok Running:

**Option 1: Keep terminal open**
- Just leave the `ngrok http 80` command running

**Option 2: Run in background**
```bash
nohup ngrok http 80 > ngrok.log 2>&1 &
```

**Option 3: Use systemd service (Linux)**
Create `/etc/systemd/system/ngrok-sentinal.service`:
```ini
[Unit]
Description=ngrok tunnel for Sentinal
After=network.target

[Service]
Type=simple
User=your-username
ExecStart=/usr/local/bin/ngrok http 80
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable ngrok-sentinal
sudo systemctl start ngrok-sentinal
```

## Testing the Setup

1. **Test ngrok tunnel (Backend API):**
   ```bash
   curl https://your-ngrok-url.ngrok-free.app/api/health
   ```
   Should return: `{"status": "healthy", "service": "sentinal-api"}`

2. **Test ngrok tunnel (Frontend):**
   ```bash
   curl https://your-ngrok-url.ngrok-free.app/
   ```
   Should return HTML content (the React app)

3. **Test in browser:**
   - Open `https://your-ngrok-url.ngrok-free.app/` in your browser
   - You should see the Sentinal frontend
   - The frontend will automatically use `/api` endpoints through Nginx proxy

4. **Test webhook from GitHub Actions:**
   - Push a commit to trigger the workflow
   - Check GitHub Actions logs for webhook success messages
   - Check Sentinal dashboard for new scan results

## Troubleshooting

### ngrok URL not accessible:
- Make sure Sentinal is running locally (`docker compose ps` to verify)
- Check ngrok is forwarding to correct port (80 for Nginx)
- Verify firewall isn't blocking connections
- Ensure Nginx container is running (it handles both frontend and backend routing)

### Webhook fails with 401:
- Verify `SENTINAL_API_TOKEN` is correct
- Check token hasn't expired
- Ensure token has proper scopes

### Webhook fails with connection error:
- ngrok tunnel may have expired (restart ngrok)
- URL may have changed (update GitHub secret)
- Check ngrok dashboard for connection status

## Alternative Solutions

### 1. Cloudflare Tunnel (Free, Static URL)
```bash
cloudflared tunnel --url http://localhost:80
```

### 2. localtunnel (Free, npm)
```bash
npm install -g localtunnel
lt --port 80
```

### 3. Serveo (SSH-based, Free)
```bash
ssh -R 80:localhost:80 serveo.net
```

## Security Considerations

⚠️ **Important:** When using ngrok for local development:

1. **Don't expose production data** - Use test data only
2. **Use strong API tokens** - Rotate tokens regularly
3. **Monitor ngrok dashboard** - Check for unauthorized access
4. **Use ngrok's IP restrictions** - Limit access to GitHub Actions IPs if possible
5. **Consider ngrok's paid plan** - For static URLs and better security features

## Next Steps

Once ngrok is set up:
1. Update GitHub Secrets with your ngrok URLs
2. Test webhook integration by pushing a commit
3. Verify scan results appear in Sentinal dashboard
4. Consider setting up a static URL for production use

