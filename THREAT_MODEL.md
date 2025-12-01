# Threat Model for Project Sentinel

**Document Version:** 1.0  
**Date:** 2024  
**Project:** Sentinel - Security Scanning & CI/CD Dashboard  
**Methodology:** STRIDE + DREAD

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Diagram](#architecture-diagram)
4. [Data Flow Analysis](#data-flow-analysis)
5. [Threat Identification (STRIDE)](#threat-identification-stride)
6. [Risk Assessment (DREAD)](#risk-assessment-dread)
7. [Threat Scenarios](#threat-scenarios)
8. [Mitigation Strategies](#mitigation-strategies)
9. [Security Controls](#security-controls)
10. [Remediation Priority](#remediation-priority)

---

## Executive Summary

Project Sentinel is a security scanning and CI/CD dashboard application that integrates multiple security tools (SonarQube, Trivy, OWASP ZAP) to provide comprehensive vulnerability scanning and threat modeling capabilities.

**Key Security Concerns:**
- **Critical:** Hardcoded secrets in `.docker.env` file (exposed in repository)
- **High:** Weak CORS configuration allowing wildcard origins
- **High:** Insufficient input validation on webhook endpoints
- **Medium:** Missing rate limiting on critical endpoints
- **Medium:** Insecure default configuration values
- **Medium:** WebSocket connections without proper authentication
- **Low:** Information disclosure through error messages

**Overall Risk Level:** **HIGH** - Multiple critical and high-severity vulnerabilities identified.

---

## System Overview

### Components

1. **Frontend (React + Vite)**
   - Served via Nginx
   - Port 80 (HTTP)
   - WebSocket connections for real-time updates

2. **Backend (Flask + SQLAlchemy)**
   - RESTful API
   - JWT authentication
   - PostgreSQL database
   - WebSocket server (Socket.IO)

3. **Security Tools**
   - SonarQube (SAST)
   - Trivy (Container scanning)
   - OWASP ZAP (DAST)

4. **Infrastructure**
   - Docker Compose orchestration
   - PostgreSQL database
   - Nginx reverse proxy

### Technology Stack

- **Backend:** Python 3.11, Flask, SQLAlchemy, Flask-JWT-Extended
- **Frontend:** React, Vite, TailwindCSS
- **Database:** PostgreSQL 15
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet Users                         │
└───────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                           │
│  - Frontend static files                                     │
│  - API proxy (/api → backend:5000)                          │
│  - WebSocket proxy (/socket.io → backend:5000)             │
└───────────────────────────┬───────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                      │
        ▼                                      ▼
┌──────────────────────┐          ┌──────────────────────┐
│   Frontend Container │          │   Backend Container   │
│   (React + Vite)     │          │   (Flask API)        │
└──────────────────────┘          └──────────┬───────────┘
                                              │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
                    ▼                        ▼                        ▼
        ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
        │   PostgreSQL      │    │   SonarQube      │    │   Trivy          │
        │   Database        │    │   (SAST)         │    │   (Container)    │
        └──────────────────┘    └──────────────────┘    └──────────────────┘
                                                              │
                                                              ▼
                                                    ┌──────────────────┐
                                                    │   OWASP ZAP      │
                                                    │   (DAST)         │
                                                    └──────────────────┘
```

---

## Data Flow Analysis

### Critical Data Flows

1. **User Authentication Flow**
   ```
   User → Frontend → Nginx → Backend → PostgreSQL
   (Credentials, JWT tokens)
   ```

2. **Webhook Data Flow**
   ```
   GitHub Actions → Internet → Nginx → Backend → PostgreSQL
   (Scan results, API tokens)
   ```

3. **Security Scan Flow**
   ```
   User → Backend → Security Tools (SonarQube/Trivy/ZAP) → Backend → PostgreSQL
   (Scan requests, vulnerability data)
   ```

4. **Real-time Updates Flow**
   ```
   Backend → WebSocket → Frontend
   (Scan progress, vulnerability alerts)
   ```

---

## Threat Identification (STRIDE)

### Spoofing Identity

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T1.1** | Authentication | JWT token theft via XSS | **HIGH** |
| **T1.2** | Webhook | API token reuse/brute force | **MEDIUM** |
| **T1.3** | OAuth | GitHub OAuth callback manipulation | **MEDIUM** |
| **T1.4** | Session | Session fixation attacks | **LOW** |

**Details:**
- **T1.1:** JWT tokens stored in localStorage are vulnerable to XSS attacks. If an attacker injects malicious JavaScript, they can steal tokens.
- **T1.2:** API tokens for webhooks use SHA-256 hashing, but weak token generation or storage could allow brute force.
- **T1.3:** GitHub OAuth callback URL validation may be insufficient, allowing redirect attacks.

### Tampering with Data

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T2.1** | API | Webhook payload tampering | **HIGH** |
| **T2.2** | Database | SQL injection (mitigated by SQLAlchemy ORM) | **LOW** |
| **T2.3** | File System | Scan result manipulation | **MEDIUM** |
| **T2.4** | Configuration | Environment variable tampering | **CRITICAL** |

**Details:**
- **T2.1:** Webhook endpoints accept JSON payloads. Without proper validation, attackers could inject malicious scan results.
- **T2.4:** `.docker.env` file contains hardcoded secrets (database passwords, JWT secrets, API tokens) that are committed to the repository.

### Repudiation

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T3.1** | Audit Logs | Insufficient logging of security events | **MEDIUM** |
| **T3.2** | Actions | Missing non-repudiation for critical actions | **MEDIUM** |
| **T3.3** | Webhooks | No webhook request logging | **LOW** |

**Details:**
- **T3.1:** Security events are logged, but comprehensive audit trails for all user actions may be missing.

### Information Disclosure

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T4.1** | Secrets | Hardcoded secrets in `.docker.env` | **CRITICAL** |
| **T4.2** | Error Messages | Verbose error messages exposing system details | **MEDIUM** |
| **T4.3** | API | Sensitive data in API responses | **MEDIUM** |
| **T4.4** | Logs | Sensitive information in application logs | **MEDIUM** |
| **T4.5** | CORS | Wildcard CORS configuration | **HIGH** |

**Details:**
- **T4.1:** `.docker.env` file contains:
  - Database password: `Kp9mN2xR7vQ4wY8zL5jH3cF6bT1sA0dG`
  - SECRET_KEY: `_GMEkHWaQ07OA4ppszLjxMA-bw5ah9nDAMrnUTHuA6M`
  - JWT_SECRET_KEY: `6_-1ToaEgkB2AgrFDcbB_8f9S3wJ45CVpR3Fh0c9t6Q`
  - GitHub OAuth secrets
  - SonarQube token
- **T4.5:** CORS configuration allows wildcard (`*`) in development, which could be misconfigured in production.

### Denial of Service

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T5.1** | API | Rate limiting insufficient or missing | **MEDIUM** |
| **T5.2** | Database | Database connection exhaustion | **MEDIUM** |
| **T5.3** | Security Tools | Resource exhaustion from scan requests | **HIGH** |
| **T5.4** | WebSocket | WebSocket connection flooding | **LOW** |

**Details:**
- **T5.1:** Rate limiting is configured but uses in-memory storage (`memory://`), which doesn't work across multiple instances.
- **T5.3:** Security scan endpoints can be triggered repeatedly, exhausting resources on SonarQube, Trivy, or ZAP services.

### Elevation of Privilege

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T6.1** | Authorization | Insufficient role-based access control | **HIGH** |
| **T6.2** | API Tokens | Token scope escalation | **MEDIUM** |
| **T6.3** | Database | SQL injection leading to privilege escalation | **LOW** |
| **T6.4** | Container | Container escape vulnerabilities | **MEDIUM** |

**Details:**
- **T6.1:** Role-based access control exists but may not be consistently applied across all endpoints.
- **T6.2:** API token scopes are checked, but improper validation could allow privilege escalation.

---

## Risk Assessment (DREAD)

### Critical Threats

#### T4.1: Hardcoded Secrets in Repository
- **Damage:** 10 - Complete system compromise
- **Reproducibility:** 10 - Anyone with repository access
- **Exploitability:** 10 - No technical skill required
- **Affected Users:** 10 - All users and data
- **Discoverability:** 10 - Visible in repository
- **DREAD Score:** 50/50 - **CRITICAL**

#### T4.5: Weak CORS Configuration
- **Damage:** 8 - Data theft, XSS attacks
- **Reproducibility:** 9 - Easy to exploit
- **Exploitability:** 8 - Moderate technical skill
- **Affected Users:** 9 - All users
- **Discoverability:** 7 - Requires testing
- **DREAD Score:** 41/50 - **HIGH**

#### T2.1: Webhook Payload Tampering
- **Damage:** 9 - False vulnerability reports, data corruption
- **Reproducibility:** 8 - Requires API token
- **Exploitability:** 7 - Moderate technical skill
- **Affected Users:** 8 - All scan results
- **Discoverability:** 6 - Requires token access
- **DREAD Score:** 38/50 - **HIGH**

#### T1.1: JWT Token Theft via XSS
- **Damage:** 9 - Account takeover
- **Reproducibility:** 7 - Requires XSS vulnerability
- **Exploitability:** 8 - Advanced technical skill
- **Affected Users:** 8 - Affected users
- **Discoverability:** 6 - Requires vulnerability discovery
- **DREAD Score:** 38/50 - **HIGH**

### High Threats

#### T5.3: Resource Exhaustion from Scan Requests
- **Damage:** 7 - Service unavailability
- **Reproducibility:** 9 - Easy to trigger
- **Exploitability:** 6 - Basic technical skill
- **Affected Users:** 8 - All users
- **Discoverability:** 7 - Easy to discover
- **DREAD Score:** 37/50 - **HIGH**

#### T6.1: Insufficient RBAC
- **Damage:** 8 - Unauthorized access
- **Reproducibility:** 7 - Requires authentication
- **Exploitability:** 6 - Moderate technical skill
- **Affected Users:** 7 - Affected users
- **Discoverability:** 6 - Requires testing
- **DREAD Score:** 34/50 - **HIGH**

---

## Threat Scenarios

### Scenario 1: Secret Exposure Attack

**Attack Path:**
1. Attacker gains access to repository (public repo, compromised account, insider threat)
2. Attacker reads `.docker.env` file containing all secrets
3. Attacker uses database password to access PostgreSQL
4. Attacker extracts all user data, API tokens, and scan results
5. Attacker uses JWT_SECRET_KEY to forge authentication tokens
6. Attacker gains full system access

**Impact:** Complete system compromise, data breach, service disruption

**Likelihood:** HIGH (if repository is public or compromised)

### Scenario 2: CORS-Based XSS Attack

**Attack Path:**
1. Attacker creates malicious website
2. Website makes cross-origin request to Sentinel API
3. Due to weak CORS configuration, request is allowed
4. Attacker injects malicious JavaScript via API response
5. User's browser executes malicious script
6. Attacker steals JWT token from localStorage
7. Attacker uses token to access user's account

**Impact:** Account takeover, data theft, unauthorized actions

**Likelihood:** MEDIUM (requires XSS vulnerability in frontend)

### Scenario 3: Webhook Payload Injection

**Attack Path:**
1. Attacker compromises GitHub Actions workflow or API token
2. Attacker sends malicious webhook payload with injected scan results
3. Backend processes payload without sufficient validation
4. Malicious data is stored in database
5. Dashboard displays false vulnerability information
6. Users make incorrect security decisions based on false data

**Impact:** False security reporting, incorrect risk assessment, potential security gaps

**Likelihood:** MEDIUM (requires token compromise)

### Scenario 4: Denial of Service via Scan Requests

**Attack Path:**
1. Attacker authenticates with valid credentials
2. Attacker triggers multiple concurrent security scans
3. SonarQube/Trivy/ZAP services become overwhelmed
4. Legitimate scan requests fail or timeout
5. System becomes unavailable for other users

**Impact:** Service unavailability, delayed security scans, user frustration

**Likelihood:** MEDIUM (requires authentication but easy to execute)

---

## Mitigation Strategies

### Immediate Actions (Critical)

1. **Remove Hardcoded Secrets**
   - Move `.docker.env` to `.gitignore`
   - Use environment variables or secret management (HashiCorp Vault, AWS Secrets Manager)
   - Rotate all exposed secrets immediately
   - Implement secret scanning in CI/CD pipeline

2. **Fix CORS Configuration**
   - Remove wildcard (`*`) from CORS_ORIGINS
   - Explicitly list allowed origins
   - Implement proper CORS headers in production

3. **Implement Input Validation**
   - Validate all webhook payloads using JSON schemas
   - Sanitize all user inputs
   - Implement request size limits

### Short-term Actions (High Priority)

4. **Enhance Authentication Security**
   - Move JWT tokens from localStorage to httpOnly cookies
   - Implement token rotation
   - Add CSRF protection

5. **Implement Rate Limiting**
   - Use Redis for distributed rate limiting
   - Apply rate limits to all endpoints
   - Implement progressive rate limiting (stricter for authenticated users)

6. **Strengthen RBAC**
   - Audit all endpoints for proper authorization checks
   - Implement principle of least privilege
   - Add role-based access control tests

7. **Resource Protection**
   - Implement scan request queuing
   - Add concurrent scan limits per user
   - Implement timeout mechanisms for long-running scans

### Medium-term Actions

8. **Enhanced Logging and Monitoring**
   - Implement comprehensive audit logging
   - Add security event monitoring
   - Set up alerting for suspicious activities

9. **Security Headers**
   - Implement Content Security Policy (CSP)
   - Add HSTS headers
   - Implement X-Frame-Options, X-Content-Type-Options

10. **Database Security**
    - Implement connection pooling limits
    - Use read-only database users where possible
    - Encrypt sensitive data at rest

11. **Container Security**
    - Use non-root users in containers
    - Implement container image scanning
    - Use minimal base images

---

## Security Controls

### Current Security Controls

✅ **Implemented:**
- JWT-based authentication
- Password hashing (bcrypt)
- SQL injection protection (SQLAlchemy ORM)
- API token authentication for webhooks
- Basic rate limiting
- Security event logging
- Input sanitization functions
- HTTPS enforcement (in production config)
- Security headers in Nginx

❌ **Missing or Weak:**
- Secret management system
- Strong CORS configuration
- Comprehensive input validation
- Distributed rate limiting
- CSRF protection
- JWT token storage security
- Comprehensive audit logging
- Resource limits on scans
- Container security hardening

### Recommended Security Controls

1. **Secrets Management**
   - Use HashiCorp Vault or AWS Secrets Manager
   - Implement secret rotation
   - Use environment variables in production

2. **Network Security**
   - Implement WAF (Web Application Firewall)
   - Use VPN for internal service communication
   - Implement network segmentation

3. **Application Security**
   - Implement Content Security Policy (CSP)
   - Add Subresource Integrity (SRI) for external resources
   - Implement secure cookie flags

4. **Monitoring and Alerting**
   - Implement SIEM (Security Information and Event Management)
   - Set up intrusion detection
   - Implement anomaly detection

---

## Remediation Priority

### Priority 1 (Critical - Immediate)

1. **Remove and Rotate Hardcoded Secrets** (T4.1)
   - Estimated Effort: 2-4 hours
   - Impact: Prevents complete system compromise

2. **Fix CORS Configuration** (T4.5)
   - Estimated Effort: 1-2 hours
   - Impact: Prevents XSS and CSRF attacks

### Priority 2 (High - Within 1 Week)

3. **Implement Webhook Input Validation** (T2.1)
   - Estimated Effort: 4-8 hours
   - Impact: Prevents data tampering

4. **Secure JWT Token Storage** (T1.1)
   - Estimated Effort: 4-6 hours
   - Impact: Prevents token theft

5. **Implement Distributed Rate Limiting** (T5.1)
   - Estimated Effort: 6-8 hours
   - Impact: Prevents DoS attacks

6. **Add Scan Request Limits** (T5.3)
   - Estimated Effort: 4-6 hours
   - Impact: Prevents resource exhaustion

### Priority 3 (Medium - Within 1 Month)

7. **Strengthen RBAC** (T6.1)
   - Estimated Effort: 8-12 hours
   - Impact: Prevents privilege escalation

8. **Enhanced Audit Logging** (T3.1)
   - Estimated Effort: 6-8 hours
   - Impact: Improves security monitoring

9. **Implement Security Headers** (T4.2)
   - Estimated Effort: 2-4 hours
   - Impact: Reduces information disclosure

### Priority 4 (Low - Ongoing)

10. **Container Security Hardening** (T6.4)
    - Estimated Effort: 4-6 hours
    - Impact: Reduces attack surface

11. **Comprehensive Security Testing**
    - Estimated Effort: Ongoing
    - Impact: Continuous security improvement

---

## Threat Model Maintenance

### Review Schedule

- **Quarterly:** Full threat model review
- **After Major Changes:** Threat model update
- **After Security Incidents:** Threat model reassessment
- **Annually:** Comprehensive security audit

### Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024 | 1.0 | Initial threat model | Security Team |

---

## Appendix

### References

- OWASP Top 10 (2021)
- OWASP ASVS (Application Security Verification Standard)
- STRIDE Threat Modeling Methodology
- DREAD Risk Assessment Model

### Tools Used

- SonarQube (SAST)
- Trivy (Container Scanning)
- OWASP ZAP (DAST)
- Bandit (Python Security Linter)

### Related Documents

- `TESTING_PLAN.md` - Security testing procedures
- `theorydocs/security-principles.md` - Security principles
- `theorydocs/stride-dread-methodology.md` - Threat modeling methodology

---

**Document Status:** Draft  
**Next Review Date:** Quarterly  
**Owner:** Security Team

