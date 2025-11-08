# Threat Modeling Test Examples

This file contains example requests to test the threat modeling functionality using STRIDE/DREAD methodology.

## Prerequisites

1. **Get an access token** (login first):
```bash
# Login to get token
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'

# Save the access_token from the response
export TOKEN="your_access_token_here"
```

## Example 1: High-Risk SQL Injection Threat

**Scenario**: User authentication endpoint vulnerable to SQL injection

```bash
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "User Authentication API Endpoint",
    "flow": "User submits login credentials via POST request. Backend queries PostgreSQL database using string concatenation without parameterized queries. Attacker injects malicious SQL payload in username field.",
    "trust_boundary": "Public Internet -> Application Server -> Database",
    "damage": 9,
    "reproducibility": 8,
    "exploitability": 9,
    "affected_users": 10,
    "discoverability": 7
  }'
```

**Expected Result**: 
- STRIDE Categories: ["Spoofing", "Tampering", "Information Disclosure"]
- Risk Level: High (DREAD score ~8.6)
- Mitigation: Should recommend parameterized queries, input validation, WAF

---

## Example 2: Medium-Risk XSS Threat

**Scenario**: User-generated content displayed without sanitization

```bash
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "User Comments Feature",
    "flow": "User submits comment through web form. Comment is stored in database and displayed to other users without HTML sanitization. Attacker injects JavaScript payload that executes in victims browsers.",
    "trust_boundary": "User Browser -> Web Server -> Database -> Other Users Browsers",
    "damage": 6,
    "reproducibility": 7,
    "exploitability": 6,
    "affected_users": 7,
    "discoverability": 5
  }'
```

**Expected Result**:
- STRIDE Categories: ["Tampering", "Information Disclosure"]
- Risk Level: Medium (DREAD score ~6.2)
- Mitigation: Should recommend output encoding, Content Security Policy, input sanitization

---

## Example 3: Low-Risk Information Disclosure

**Scenario**: Verbose error messages leak system information

```bash
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "Error Handling System",
    "flow": "Application throws unhandled exception. Error handler returns detailed stack trace including file paths, database connection strings, and internal IP addresses to client.",
    "trust_boundary": "Application Server -> Client Browser",
    "damage": 3,
    "reproducibility": 4,
    "exploitability": 3,
    "affected_users": 2,
    "discoverability": 4
  }'
```

**Expected Result**:
- STRIDE Categories: ["Information Disclosure"]
- Risk Level: Low (DREAD score ~3.2)
- Mitigation: Should recommend generic error messages, proper logging, error sanitization

---

## Example 4: High-Risk Authentication Bypass

**Scenario**: Weak session management allows privilege escalation

```bash
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "Session Management System",
    "flow": "Application uses predictable session tokens based on username and timestamp. No session invalidation on logout. Attacker can guess or hijack sessions to gain unauthorized access to user accounts.",
    "trust_boundary": "Client Browser -> Application Server -> Protected Resources",
    "damage": 10,
    "reproducibility": 9,
    "exploitability": 8,
    "affected_users": 9,
    "discoverability": 6
  }'
```

**Expected Result**:
- STRIDE Categories: ["Spoofing", "Elevation of Privilege"]
- Risk Level: High (DREAD score ~8.4)
- Mitigation: Should recommend secure random session tokens, HTTPS-only cookies, proper session invalidation

---

## Example 5: Medium-Risk API Rate Limiting Bypass

**Scenario**: Missing rate limiting allows brute force attacks

```bash
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "Password Reset API",
    "flow": "Password reset endpoint accepts email addresses without rate limiting. Attacker can enumerate valid email addresses and flood users with reset emails, causing denial of service.",
    "trust_boundary": "Public Internet -> API Gateway -> Email Service",
    "damage": 5,
    "reproducibility": 8,
    "exploitability": 7,
    "affected_users": 6,
    "discoverability": 4
  }'
```

**Expected Result**:
- STRIDE Categories: ["Denial of Service", "Information Disclosure"]
- Risk Level: Medium (DREAD score ~6.0)
- Mitigation: Should recommend rate limiting, CAPTCHA, email throttling

---

## Example 6: High-Risk Insecure Direct Object Reference

**Scenario**: API endpoints expose internal IDs without authorization checks

```bash
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "User Profile API",
    "flow": "API endpoint /api/users/{id} returns user data based solely on ID parameter without checking if requester has permission. Attacker can enumerate user IDs to access any user profile data including PII.",
    "trust_boundary": "Authenticated User -> API Server -> Database",
    "damage": 8,
    "reproducibility": 9,
    "exploitability": 8,
    "affected_users": 8,
    "discoverability": 5
  }'
```

**Expected Result**:
- STRIDE Categories: ["Tampering", "Information Disclosure", "Elevation of Privilege"]
- Risk Level: High (DREAD score ~7.6)
- Mitigation: Should recommend authorization checks, indirect object references, access control lists

---

## Testing via Frontend

1. Navigate to `http://localhost/threats` in your browser
2. Fill in the threat modeling form with any of the examples above
3. Submit and view the STRIDE/DREAD analysis results

## Testing via API (Complete Workflow)

```bash
# 1. Login
RESPONSE=$(curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 2. Analyze a threat
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "User Authentication API Endpoint",
    "flow": "User submits login credentials via POST request. Backend queries PostgreSQL database using string concatenation without parameterized queries.",
    "trust_boundary": "Public Internet -> Application Server -> Database",
    "damage": 9,
    "reproducibility": 8,
    "exploitability": 9,
    "affected_users": 10,
    "discoverability": 7
  }' | jq '.'

# 3. List all threats
curl -X GET http://localhost/api/threats \
  -H "Authorization: Bearer $TOKEN" | jq '.'

# 4. Get specific threat details (replace {id} with actual threat ID)
curl -X GET http://localhost/api/threats/1 \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

## DREAD Scoring Guide

- **Damage** (0-10): How bad would an attack be?
  - 0-3: Minimal impact (annoyance)
  - 4-6: Moderate impact (data loss, service disruption)
  - 7-10: Severe impact (complete system compromise, data breach)

- **Reproducibility** (0-10): How easy is it to reproduce the attack?
  - 0-3: Very difficult, requires specific conditions
  - 4-6: Moderate difficulty, some conditions needed
  - 7-10: Very easy, can be reproduced reliably

- **Exploitability** (0-10): How much effort is required to exploit?
  - 0-3: Requires expert knowledge, custom tools
  - 4-6: Moderate skill level required
  - 7-10: Script kiddie level, publicly available tools

- **Affected Users** (0-10): How many users would be affected?
  - 0-3: Single user or small group
  - 4-6: Moderate user base
  - 7-10: All users or critical systems

- **Discoverability** (0-10): How easy is it to discover the vulnerability?
  - 0-3: Very difficult to discover
  - 4-6: Moderate difficulty, requires some investigation
  - 7-10: Obvious, visible in normal use

## STRIDE Categories

- **S**poofing: Impersonating someone or something else
- **T**ampering: Modifying data or code
- **R**epudiation: Denying having performed an action
- **I**nformation Disclosure: Exposing information to unauthorized parties
- **D**enial of Service: Making a service unavailable
- **E**levation of Privilege: Gaining unauthorized access or capabilities

