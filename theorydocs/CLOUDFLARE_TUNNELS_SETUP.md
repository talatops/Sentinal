# Cloudflare Tunnels Setup - Two Separate Tunnels

## Overview

This document describes the setup for two separate Cloudflare named tunnels:
1. **Sentinal Tunnel** - Main dashboard application (`https://sentinal.jurassiq-dev.org`)
2. **SonarQube Tunnel** - SonarQube service (`https://sonarqube.jurassiq-dev.org`)

## Current Setup

### Tunnel 1: Sentinal (Main Dashboard)

- **Tunnel Name:** `sentinal`
- **Tunnel ID:** `b7c01a86-75f5-4bb4-8fa5-09de346b074f`
- **Config File:** `~/.cloudflared/config-sentinal.yml`
- **URL:** `https://sentinal.jurassiq-dev.org`
- **Local Service:** `http://localhost:80`

### Tunnel 2: SonarQube

- **Tunnel Name:** `sonarqube`
- **Tunnel ID:** `3dc56c8c-a0d6-4785-a0e2-f05ab1c21600`
- **Config File:** `~/.cloudflared/config-sonarqube.yml`
- **URL:** `https://sonarqube.jurassiq-dev.org`
- **Local Service:** `http://localhost:9000`

## Configuration Files

### Sentinal Tunnel Config (`~/.cloudflared/config-sentinal.yml`)

```yaml
tunnel: b7c01a86-75f5-4bb4-8fa5-09de346b074f
credentials-file: /root/.cloudflared/b7c01a86-75f5-4bb4-8fa5-09de346b074f.json

ingress:
  - hostname: sentinal.jurassiq-dev.org
    service: http://localhost:80
  - service: http_status:404
```

### SonarQube Tunnel Config (`~/.cloudflared/config-sonarqube.yml`)

```yaml
tunnel: 3dc56c8c-a0d6-4785-a0e2-f05ab1c21600
credentials-file: /root/.cloudflared/3dc56c8c-a0d6-4785-a0e2-f05ab1c21600.json

ingress:
  - hostname: sonarqube.jurassiq-dev.org
    service: http://localhost:9000
  - service: http_status:404
```

## Starting the Tunnels

### Start Both Tunnels in Background

```bash
# Start sentinal tunnel
cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal > /tmp/sentinal-tunnel.log 2>&1 &

# Start sonarqube tunnel
cloudflared tunnel --config ~/.cloudflared/config-sonarqube.yml run sonarqube > /tmp/sonarqube-tunnel.log 2>&1 &
```

### Start Both Tunnels in Separate Terminals

```bash
# Terminal 1: Sentinal tunnel
cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal

# Terminal 2: SonarQube tunnel
cloudflared tunnel --config ~/.cloudflared/config-sonarqube.yml run sonarqube
```

## Verifying Tunnels

### Check Tunnel Status

```bash
# List all tunnels
cloudflared tunnel list

# Check specific tunnel info
cloudflared tunnel info sentinal
cloudflared tunnel info sonarqube
```

### Test URLs

```bash
# Test Sentinal tunnel
curl https://sentinal.jurassiq-dev.org/api/health
# Expected: {"service":"sentinal-api","status":"healthy"}

# Test SonarQube tunnel
curl https://sonarqube.jurassiq-dev.org/api/system/status
# Expected: {"status":"UP","version":"..."}
```

### Check Running Processes

```bash
# Check if tunnels are running
ps aux | grep "cloudflared.*config" | grep -v grep

# Check tunnel logs
tail -f /tmp/sentinal-tunnel.log
tail -f /tmp/sonarqube-tunnel.log
```

## Stopping Tunnels

```bash
# Stop all tunnels
pkill -f "cloudflared tunnel"

# Stop specific tunnel
pkill -f "cloudflared.*sentinal"
pkill -f "cloudflared.*sonarqube"
```

## Troubleshooting

### Tunnel Not Working

1. **Check if tunnel is running:**
   ```bash
   ps aux | grep cloudflared | grep -v grep
   ```

2. **Check tunnel logs:**
   ```bash
   tail -50 /tmp/sentinal-tunnel.log
   tail -50 /tmp/sonarqube-tunnel.log
   ```

3. **Verify local services are accessible:**
   ```bash
   curl http://localhost/api/health
   curl http://localhost:9000/api/system/status
   ```

4. **Restart tunnel:**
   ```bash
   # Stop and restart
   pkill -f "cloudflared.*sentinal"
   cloudflared tunnel --config ~/.cloudflared/config-sentinal.yml run sentinal > /tmp/sentinal-tunnel.log 2>&1 &
   ```

### DNS Issues

**⚠️ IMPORTANT:** The DNS route for `sentinal.jurassiq-dev.org` must point to the correct tunnel!

If you get 404 errors or the tunnel doesn't work, verify DNS records in Cloudflare dashboard:

1. Go to: https://dash.cloudflare.com
2. Select domain: `jurassiq-dev.org`
3. Go to **DNS** → **Records**
4. Find the CNAME record for `sentinal`
5. **Verify/Update** the target to: `b7c01a86-75f5-4bb4-8fa5-09de346b074f.cfargotunnel.com`
   - If it points to `3dc56c8c-a0d6-4785-a0e2-f05ab1c21600.cfargotunnel.com` (sonarqube tunnel), **update it!**
6. Verify CNAME record for `sonarqube`:
   - Should be: `3dc56c8c-a0d6-4785-a0e2-f05ab1c21600.cfargotunnel.com`

**To check current routing:**
```bash
cloudflared tunnel route dns list sentinal
cloudflared tunnel route dns list sonarqube
```

**Expected output:**
- `sentinal.jurassiq-dev.org` → tunnel `b7c01a86-75f5-4bb4-8fa5-09de346b074f` (sentinal)
- `sonarqube.jurassiq-dev.org` → tunnel `3dc56c8c-a0d6-4785-a0e2-f05ab1c21600` (sonarqube)

## Quick Status Check Script

```bash
#!/bin/bash
echo "=== Cloudflare Tunnel Status ==="
echo ""
echo "Active Tunnels:"
cloudflared tunnel list
echo ""
echo "Testing URLs:"
echo -n "Sentinal: "
curl -s --max-time 5 https://sentinal.jurassiq-dev.org/api/health | head -1 || echo "FAILED"
echo -n "SonarQube: "
curl -s --max-time 5 https://sonarqube.jurassiq-dev.org/api/system/status | head -1 || echo "FAILED"
```

Save as `check-tunnels.sh` and run: `bash check-tunnels.sh`
