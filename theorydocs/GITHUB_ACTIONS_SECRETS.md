# GitHub Actions Secrets Configuration Guide

This document lists all the secrets you need to configure in your GitHub repository for the CI/CD pipeline to work properly.

## How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

**⚠️ IMPORTANT:** 
- Secret names are case-sensitive
- Secret names must NOT start with `GITHUB_` (GitHub reserved prefix)
- Once added, secret values cannot be viewed again (only updated or deleted)

---

## Required Secrets

### 1. SENTINAL_API_URL

**Required:** ✅ **YES** (for dashboard webhook integration)

**Description:** The public URL of your Sentinal dashboard application. This is used by GitHub Actions to send scan results (SonarQube, Trivy, ZAP) back to your dashboard.

**Used in Jobs:**
- `sast` (SonarQube scan)
- `container-scan` (Trivy scan)
- `dast` (OWASP ZAP scan)

**Value Format:**
- If using **Cloudflare Tunnel**: `https://sentinal.jurassiq-dev.org`
- If using **ngrok**: `https://abc123.ngrok-free.app` (your ngrok URL)

**How to Get:**
1. **If using Cloudflare Tunnel:**
   - Your URL is: `https://sentinal.jurassiq-dev.org`
   - Verify it's working: `curl https://sentinal.jurassiq-dev.org/api/health`

2. **If using ngrok:**
   - Start ngrok: `ngrok http 80`
   - Copy the HTTPS URL from ngrok output
   - Example: `https://precontributive-tribally-dione.ngrok-free.dev`

**Example Value:**
```
https://sentinal.jurassiq-dev.org
```

**⚠️ Note:** 
- URL must be accessible from the internet (GitHub Actions runners need to reach it)
- Must use `https://` (not `http://`)
- No trailing slash

---

### 2. SENTINAL_API_TOKEN

**Required:** ✅ **YES** (for dashboard webhook authentication)

**Description:** API token for authenticating webhook requests from GitHub Actions to your Sentinal dashboard. This token must have `webhook:write` scope.

**Used in Jobs:**
- `sast` (SonarQube scan)
- `container-scan` (Trivy scan)
- `dast` (OWASP ZAP scan)

**Value Format:**
- Token format: `sent_...` (starts with `sent_`)
- Example: `sent_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

**How to Get:**
1. **Access Sentinal Dashboard:**
   - Open: `https://sentinal.jurassiq-dev.org` (or your ngrok URL)
   - Login with your admin account

2. **Create API Token:**
   - Navigate to **API Tokens** page (or **Settings** → **API Tokens**)
   - Click **Create New Token**
   - Enter name: `GitHub Actions CI/CD`
   - Select scopes: `webhook:write` (or `webhook:*` for full access)
   - Set expiration (optional, recommended: 365 days)
   - Click **Generate**

3. **⚠️ Copy the token immediately** - you won't be able to see it again!

**Example Value:**
```
sent_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

**⚠️ Security Notes:**
- Keep this token secret - never commit it to code
- Rotate tokens regularly (every 90-365 days)
- Use minimal scopes (`webhook:write` only, not `webhook:*`)

---

### 3. SONARQUBE_URL

**Required:** ⚠️ **OPTIONAL** (SAST scan will be skipped if not set)

**Description:** The public URL of your SonarQube server. This is used by GitHub Actions to perform Static Application Security Testing (SAST) scans.

**Used in Jobs:**
- `sast` (SonarQube scan)

**Value Format:**
- If using **Cloudflare Named Tunnel**: `https://sonarqube.jurassiq-dev.org`
- If using **Cloudflare Quick Tunnel**: `https://abc123-def456-xyz789.cfargotunnel.com`
- If using **ngrok**: `https://xyz789.ngrok-free.app` (your ngrok URL for port 9000)

**How to Get:**
1. **If using Cloudflare Named Tunnel:**
   - Your URL is: `https://sonarqube.jurassiq-dev.org`
   - Verify it's working: `curl https://sonarqube.jurassiq-dev.org/api/system/status`

2. **If using Cloudflare Quick Tunnel:**
   - Run: `cloudflared tunnel --url http://localhost:9000`
   - Copy the URL from the output
   - ⚠️ URL changes each time you restart the tunnel

3. **If using ngrok:**
   - In a separate terminal: `ngrok http 9000`
   - Copy the HTTPS URL from ngrok output

**Example Value:**
```
https://sonarqube.jurassiq-dev.org
```

**⚠️ Note:**
- URL must be accessible from the internet (GitHub Actions runners need to reach it)
- Must use `https://` (not `http://`)
- If not set, SAST scan will be skipped (workflow will continue)

---

### 4. SONARQUBE_TOKEN

**Required:** ⚠️ **OPTIONAL** (SAST scan will be skipped if not set)

**Description:** Authentication token for SonarQube. This token is used by GitHub Actions to authenticate with your SonarQube server for SAST scans.

**Used in Jobs:**
- `sast` (SonarQube scan)

**Value Format:**
- Token format: `sqa_...` (starts with `sqa_`)
- Example: `sqa_85babafd06293b7f9eaf75583a78d9941176a1a8`

**How to Get:**
1. **Access SonarQube:**
   - Open: `http://localhost:9000` (local) or `https://sonarqube.jurassiq-dev.org` (via tunnel)
   - Login with username: `admin` and password: `admin` (change on first login)

2. **Generate Token:**
   - Click profile icon (top right) → **My Account**
   - Go to **Security** tab
   - Under **Generate Tokens**, enter name: `sentinal-ci` or `github-actions`
   - Click **Generate**

3. **⚠️ Copy the token immediately** - you won't be able to see it again!

**Example Value:**
```
sqa_85babafd06293b7f9eaf75583a78d9941176a1a8
```

**⚠️ Note:**
- If not set, SAST scan will be skipped (workflow will continue)
- Token must have permissions to analyze projects

---

## Optional Secrets

### 5. GITHUB_CLIENT_ID (Optional)

**Required:** ❌ **NO** (only if using GitHub OAuth in your application)

**Description:** GitHub OAuth Client ID for user authentication. Only needed if your application uses GitHub OAuth for login.

**Used in Jobs:**
- None (used by application, not CI/CD)

**How to Get:**
1. Go to: https://github.com/settings/developers
2. Click **OAuth Apps** → **New OAuth App**
3. Fill in:
   - Application name: `sentinal`
   - Homepage URL: `https://sentinal.jurassiq-dev.org`
   - Authorization callback URL: `https://sentinal.jurassiq-dev.org/callback`
4. Click **Register application**
5. Copy the **Client ID**

**Note:** This is typically stored in `.docker.env`, not GitHub Secrets, unless you need it in CI/CD.

---

### 6. GITHUB_CLIENT_SECRET (Optional)

**Required:** ❌ **NO** (only if using GitHub OAuth in your application)

**Description:** GitHub OAuth Client Secret. Only needed if your application uses GitHub OAuth for login.

**How to Get:**
1. Go to: https://github.com/settings/developers
2. Click on your OAuth App
3. Click **Generate a new client secret**
4. **⚠️ Copy the secret immediately** - you won't be able to see it again!

**Note:** This is typically stored in `.docker.env`, not GitHub Secrets, unless you need it in CI/CD.

---

## Secret Checklist

Use this checklist to ensure all required secrets are configured:

### Required for Basic CI/CD (Linting, Testing, Build)
- [ ] None required - these jobs run without secrets

### Required for Dashboard Integration
- [ ] `SENTINAL_API_URL` - Your dashboard public URL
- [ ] `SENTINAL_API_TOKEN` - API token with `webhook:write` scope

### Required for SAST Scanning (SonarQube)
- [ ] `SONARQUBE_URL` - SonarQube server public URL
- [ ] `SONARQUBE_TOKEN` - SonarQube authentication token

### Optional (for GitHub OAuth)
- [ ] `GITHUB_CLIENT_ID` - Only if using GitHub OAuth
- [ ] `GITHUB_CLIENT_SECRET` - Only if using GitHub OAuth

---

## Quick Setup Summary

### Minimum Required Secrets (for full CI/CD with dashboard):

1. **SENTINAL_API_URL**
   - Value: `https://sentinal.jurassiq-dev.org` (or your ngrok URL)
   - Purpose: Dashboard webhook endpoint

2. **SENTINAL_API_TOKEN**
   - Value: Generate from Sentinal dashboard → API Tokens
   - Purpose: Authenticate webhook requests

3. **SONARQUBE_URL** (Optional but recommended)
   - Value: `https://sonarqube.jurassiq-dev.org` (or your tunnel URL)
   - Purpose: SAST scanning

4. **SONARQUBE_TOKEN** (Optional but recommended)
   - Value: Generate from SonarQube UI
   - Purpose: Authenticate with SonarQube

---

## Verification Steps

After adding all secrets, verify they're working:

### 1. Test SENTINAL_API_URL
```bash
# From your local machine or any internet-connected device
curl https://sentinal.jurassiq-dev.org/api/health
# Expected: {"service":"sentinal-api","status":"healthy"}
```

### 2. Test SENTINAL_API_TOKEN
```bash
# Test webhook endpoint with your token
curl -X POST https://sentinal.jurassiq-dev.org/api/cicd/webhook/sonarqube \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SENTINAL_API_TOKEN" \
  -d '{"commit_hash": "test", "branch": "main", "status": "completed", "results": {}}'
# Expected: {"message": "sonarqube results received", ...}
```

### 3. Test SONARQUBE_URL
```bash
# Test SonarQube is accessible
curl https://sonarqube.jurassiq-dev.org/api/system/status
# Expected: {"status":"UP","version":"..."}
```

### 4. Test SONARQUBE_TOKEN
```bash
# Test SonarQube authentication (requires valid token)
curl -u YOUR_SONARQUBE_TOKEN: https://sonarqube.jurassiq-dev.org/api/authentication/validate
# Expected: {"valid":true}
```

---

## Troubleshooting

### Secret Not Working

1. **Check secret name is correct:**
   - Names are case-sensitive
   - Must match exactly: `SENTINAL_API_URL` (not `sentinal_api_url`)

2. **Verify secret value:**
   - No extra spaces or newlines
   - Complete URL (including `https://`)
   - Token is complete (not truncated)

3. **Check secret is accessible:**
   - URLs must be reachable from internet
   - Test with `curl` from outside your network

4. **Verify token permissions:**
   - `SENTINAL_API_TOKEN` must have `webhook:write` scope
   - `SONARQUBE_TOKEN` must be valid and not expired

### Workflow Skipping Steps

If you see messages like:
- `⚠️ SonarQube secrets not configured. Skipping SAST scan.`
- `⚠️ Sentinal Dashboard webhook not configured. Results won't be sent to dashboard.`

This means the corresponding secrets are missing. Add them to enable those features.

---

## Current Configuration Status

Based on your setup:

✅ **SENTINAL_API_URL**: Should be `https://sentinal.jurassiq-dev.org`
✅ **SENTINAL_API_TOKEN**: Generate from dashboard
✅ **SONARQUBE_URL**: Should be `https://sonarqube.jurassiq-dev.org`
✅ **SONARQUBE_TOKEN**: Generate from SonarQube UI

---

## Security Best Practices

1. **Rotate tokens regularly:**
   - API tokens: Every 90-365 days
   - SonarQube tokens: Every 90-365 days

2. **Use minimal scopes:**
   - `webhook:write` only (not `webhook:*`)
   - Don't grant unnecessary permissions

3. **Monitor token usage:**
   - Check dashboard logs for webhook activity
   - Revoke unused tokens

4. **Never commit secrets:**
   - Secrets should only be in GitHub Secrets
   - Never in code, config files, or commit messages

---

## Reference: Which Jobs Use Which Secrets

| Job Name | Secrets Used | Required? |
|----------|-------------|-----------|
| `lint` | None | - |
| `test` | None | - |
| `build` | None | - |
| `smoke-test` | None | - |
| `sast` | `SONARQUBE_URL`, `SONARQUBE_TOKEN`, `SENTINAL_API_URL`, `SENTINAL_API_TOKEN` | Optional (skips if missing) |
| `container-scan` | `SENTINAL_API_URL`, `SENTINAL_API_TOKEN` | Optional (skips webhook if missing) |
| `dast` | `SENTINAL_API_URL`, `SENTINAL_API_TOKEN` | Optional (skips webhook if missing) |
| `deployment-gate` | None | - |
| `deploy` | None | - |

---

## Example: Adding Secrets via GitHub CLI (Alternative Method)

If you prefer using GitHub CLI:

```bash
# Install GitHub CLI first: https://cli.github.com/

# Add SENTINAL_API_URL
gh secret set SENTINAL_API_URL --body "https://sentinal.jurassiq-dev.org"

# Add SENTINAL_API_TOKEN
gh secret set SENTINAL_API_TOKEN --body "sent_abc123..."

# Add SONARQUBE_URL
gh secret set SONARQUBE_URL --body "https://sonarqube.jurassiq-dev.org"

# Add SONARQUBE_TOKEN
gh secret set SONARQUBE_TOKEN --body "sqa_85babafd..."
```

---

## Next Steps

After adding all secrets:

1. **Trigger a test workflow:**
   ```bash
   git commit --allow-empty -m "test: Verify GitHub Actions secrets"
   git push origin develop
   ```

2. **Monitor the workflow:**
   - Go to repository → **Actions** tab
   - Check if all jobs complete successfully
   - Verify webhook calls are being made

3. **Check dashboard:**
   - Login to Sentinal dashboard
   - Go to **CI/CD Dashboard**
   - Verify scan results are appearing

---

**Last Updated:** 2025-11-30
**Version:** 1.0
