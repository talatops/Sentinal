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
10. [Remediation Recommendations](#remediation-recommendations)

---

## Executive Summary

Project Sentinel is a security scanning and CI/CD dashboard application that integrates multiple security tools (SonarQube, Trivy, OWASP ZAP) to provide comprehensive vulnerability scanning and threat modeling capabilities.

**Threat Model Scope:** This document identifies and assesses medium and low severity security threats using the STRIDE methodology and DREAD risk assessment framework.

**Key Findings:**
- **Medium Severity Threats:** 8 identified
- **Low Severity Threats:** 6 identified
- **Overall Risk Level:** **MEDIUM** - System demonstrates good security posture with manageable risks

**Security Posture:** The application implements strong foundational security controls including JWT authentication, SQL injection protection via ORM, API token authentication, and comprehensive security tooling integration.

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
| **T1.1** | Session | Session fixation attacks | **LOW** |
| **T1.2** | OAuth | GitHub OAuth callback validation edge cases | **MEDIUM** |

**Details:**
- **T1.1:** Session fixation attacks are mitigated by JWT tokens, but session management could be enhanced with additional validation.
- **T1.2:** GitHub OAuth callback URL validation is implemented, but edge cases in redirect handling could be further validated.

### Tampering with Data

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T2.1** | File System | Scan result file manipulation | **MEDIUM** |
| **T2.2** | Database | SQL injection (mitigated by SQLAlchemy ORM) | **LOW** |

**Details:**
- **T2.1:** Scan results stored in database could potentially be manipulated if file system access is compromised. Database-level integrity checks provide protection.
- **T2.2:** SQL injection is well-protected by SQLAlchemy ORM, but additional validation on complex queries could provide defense in depth.

### Repudiation

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T3.1** | Audit Logs | Enhanced logging for all user actions | **MEDIUM** |
| **T3.2** | Actions | Non-repudiation for critical actions | **MEDIUM** |
| **T3.3** | Webhooks | Webhook request logging enhancement | **LOW** |

**Details:**
- **T3.1:** Security events are logged, but comprehensive audit trails for all user actions (especially administrative actions) could be enhanced.
- **T3.2:** Non-repudiation mechanisms exist through logging, but could be strengthened with digital signatures for critical operations.
- **T3.3:** Webhook requests are processed, but additional logging of request metadata could improve audit capabilities.

### Information Disclosure

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T4.1** | Error Messages | Verbose error messages in development mode | **MEDIUM** |
| **T4.2** | API | Sensitive data in API responses | **MEDIUM** |
| **T4.3** | Logs | Sensitive information in application logs | **MEDIUM** |

**Details:**
- **T4.1:** Error messages may expose system details in development mode. Production mode should suppress verbose errors, but additional validation ensures no information leakage.
- **T4.2:** API responses are generally well-structured, but some endpoints may return more information than necessary. Response filtering could be enhanced.
- **T4.3:** Application logs may contain sensitive information. Log sanitization is implemented but could be expanded to cover all log outputs.

### Denial of Service

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T5.1** | API | Rate limiting scalability (in-memory storage) | **MEDIUM** |
| **T5.2** | Database | Database connection pool exhaustion | **MEDIUM** |
| **T5.3** | WebSocket | WebSocket connection resource management | **LOW** |

**Details:**
- **T5.1:** Rate limiting is implemented using in-memory storage, which works well for single-instance deployments but may not scale across multiple instances. Distributed rate limiting would improve scalability.
- **T5.2:** Database connection pooling is configured, but connection limits and timeout settings could be optimized to prevent exhaustion under high load.
- **T5.3:** WebSocket connections are managed, but connection limits and cleanup mechanisms could be enhanced for better resource management.

### Elevation of Privilege

| Threat | Component | Description | Severity |
|--------|-----------|-------------|----------|
| **T6.1** | API Tokens | Token scope validation edge cases | **MEDIUM** |
| **T6.2** | Container | Container security hardening opportunities | **MEDIUM** |

**Details:**
- **T6.1:** API token scopes are validated, but edge cases in scope checking could be further hardened to prevent potential privilege escalation.
- **T6.2:** Containers run with appropriate configurations, but additional hardening (non-root users, minimal base images, security scanning) would reduce attack surface.

---

## Risk Assessment (DREAD)

### Medium Severity Threats

#### T3.1: Enhanced Audit Logging
- **Damage:** 5 - Limited impact, affects audit trail quality
- **Reproducibility:** 6 - Easy to test, but requires specific conditions
- **Exploitability:** 4 - Low technical skill required, but limited impact
- **Affected Users:** 5 - Affects audit capabilities
- **Discoverability:** 5 - Moderate difficulty to identify gaps
- **DREAD Score:** 25/50 - **MEDIUM**

#### T3.2: Non-Repudiation Enhancement
- **Damage:** 5 - Affects accountability, not direct security breach
- **Reproducibility:** 5 - Requires specific scenarios
- **Exploitability:** 4 - Low technical skill, limited impact
- **Affected Users:** 4 - Affects specific operations
- **Discoverability:** 5 - Moderate difficulty
- **DREAD Score:** 23/50 - **MEDIUM**

#### T4.1: Verbose Error Messages
- **Damage:** 4 - Information disclosure, limited impact
- **Reproducibility:** 6 - Easy to trigger in development
- **Exploitability:** 5 - Moderate technical skill
- **Affected Users:** 4 - Limited user impact
- **Discoverability:** 6 - Easy to discover in dev mode
- **DREAD Score:** 25/50 - **MEDIUM**

#### T4.2: Sensitive Data in API Responses
- **Damage:** 5 - Potential information disclosure
- **Reproducibility:** 5 - Requires specific API calls
- **Exploitability:** 5 - Moderate technical skill
- **Affected Users:** 5 - Affects API consumers
- **Discoverability:** 5 - Moderate difficulty
- **DREAD Score:** 25/50 - **MEDIUM**

#### T4.3: Sensitive Information in Logs
- **Damage:** 4 - Information disclosure through logs
- **Reproducibility:** 5 - Requires log access
- **Exploitability:** 4 - Low technical skill, requires access
- **Affected Users:** 4 - Limited impact
- **Discoverability:** 5 - Moderate difficulty
- **DREAD Score:** 22/50 - **MEDIUM**

#### T5.1: Rate Limiting Scalability
- **Damage:** 5 - Affects scalability, not direct security
- **Reproducibility:** 6 - Easy to test with multiple instances
- **Exploitability:** 5 - Moderate technical skill
- **Affected Users:** 5 - Affects multi-instance deployments
- **Discoverability:** 6 - Easy to identify
- **DREAD Score:** 27/50 - **MEDIUM**

#### T5.2: Database Connection Pool Exhaustion
- **Damage:** 5 - Service degradation, not complete compromise
- **Reproducibility:** 6 - Easy to test under load
- **Exploitability:** 5 - Moderate technical skill
- **Affected Users:** 5 - Affects all users under load
- **Discoverability:** 6 - Easy to identify
- **DREAD Score:** 27/50 - **MEDIUM**

#### T6.1: Token Scope Validation Edge Cases
- **Damage:** 5 - Potential privilege escalation
- **Reproducibility:** 5 - Requires specific edge cases
- **Exploitability:** 5 - Moderate technical skill
- **Affected Users:** 4 - Limited impact
- **Discoverability:** 5 - Moderate difficulty
- **DREAD Score:** 24/50 - **MEDIUM**

### Low Severity Threats

#### T1.1: Session Fixation
- **Damage:** 3 - Limited impact due to JWT protection
- **Reproducibility:** 4 - Requires specific conditions
- **Exploitability:** 4 - Low technical skill
- **Affected Users:** 3 - Limited user impact
- **Discoverability:** 4 - Moderate difficulty
- **DREAD Score:** 18/50 - **LOW**

#### T1.2: OAuth Callback Edge Cases
- **Damage:** 3 - Limited impact, OAuth is well-protected
- **Reproducibility:** 4 - Requires edge case scenarios
- **Exploitability:** 4 - Low technical skill
- **Affected Users:** 3 - Limited impact
- **Discoverability:** 4 - Moderate difficulty
- **DREAD Score:** 18/50 - **LOW**

#### T2.2: SQL Injection (Defense in Depth)
- **Damage:** 2 - Well-protected by ORM
- **Reproducibility:** 3 - Very difficult due to ORM protection
- **Exploitability:** 3 - Low risk due to existing protection
- **Affected Users:** 2 - Minimal risk
- **Discoverability:** 3 - Difficult to exploit
- **DREAD Score:** 13/50 - **LOW**

#### T3.3: Webhook Request Logging
- **Damage:** 2 - Limited impact on audit trail
- **Reproducibility:** 4 - Easy to test
- **Exploitability:** 2 - Very low impact
- **Affected Users:** 2 - Minimal impact
- **Discoverability:** 4 - Easy to identify
- **DREAD Score:** 14/50 - **LOW**

#### T5.3: WebSocket Connection Management
- **Damage:** 3 - Resource management issue
- **Reproducibility:** 4 - Easy to test with many connections
- **Exploitability:** 3 - Low technical skill
- **Affected Users:** 3 - Limited impact
- **Discoverability:** 4 - Easy to identify
- **DREAD Score:** 17/50 - **LOW**

#### T6.2: Container Security Hardening
- **Damage:** 3 - Reduced attack surface opportunity
- **Reproducibility:** 4 - Easy to assess
- **Exploitability:** 3 - Low risk, containers are reasonably secure
- **Affected Users:** 3 - Limited impact
- **Discoverability:** 4 - Easy to identify
- **DREAD Score:** 17/50 - **LOW**

---

## Threat Scenarios

### Scenario 1: Rate Limiting Scalability Issue

**Scenario:**
1. Application is deployed with multiple backend instances
2. User makes requests across different instances
3. In-memory rate limiting doesn't coordinate between instances
4. User may exceed intended rate limits
5. System may not properly enforce rate limits across instances

**Impact:** Potential for rate limit bypass in multi-instance deployments, affecting fair resource usage

**Likelihood:** MEDIUM (occurs in multi-instance deployments)

**Mitigation:** Implement distributed rate limiting using Redis or similar shared storage

### Scenario 2: Database Connection Pool Exhaustion

**Scenario:**
1. Application experiences high concurrent load
2. Multiple users trigger security scans simultaneously
3. Database connections are not released promptly
4. Connection pool becomes exhausted
5. New requests fail or timeout waiting for database connections

**Impact:** Service degradation, potential timeouts, poor user experience

**Likelihood:** MEDIUM (occurs under high load conditions)

**Mitigation:** Optimize connection pool settings, implement connection timeout, add connection monitoring

### Scenario 3: Verbose Error Information Disclosure

**Scenario:**
1. Application encounters an error in development or misconfigured production
2. Error message includes stack traces or system details
3. Error is returned to user or logged
4. Attacker or user gains information about system internals
5. Information could be used for reconnaissance

**Impact:** Information disclosure, potential reconnaissance for further attacks

**Likelihood:** MEDIUM (more likely in development, less likely in properly configured production)

**Mitigation:** Implement error message sanitization, ensure production mode suppresses verbose errors

### Scenario 4: Enhanced Audit Logging Gap

**Scenario:**
1. User performs administrative action
2. Action is not fully logged with all context
3. Security incident occurs
4. Audit trail is incomplete
5. Investigation is hampered by missing log data

**Impact:** Reduced audit trail quality, potential compliance issues, difficulty in incident investigation

**Likelihood:** MEDIUM (depends on specific actions and logging implementation)

**Mitigation:** Enhance audit logging to capture all user actions with full context

### Scenario 5: API Response Information Disclosure

**Scenario:**
1. API endpoint returns response with more data than necessary
2. Response includes internal IDs, system details, or metadata
3. Attacker analyzes API responses
4. Information is used for reconnaissance or enumeration
5. Potential for information gathering about system structure

**Impact:** Information disclosure, potential reconnaissance

**Likelihood:** MEDIUM (depends on specific endpoints and response structure)

**Mitigation:** Implement response filtering, return only necessary data, review all API endpoints

---

## Mitigation Strategies

### Medium Priority Mitigations

1. **Implement Distributed Rate Limiting**
   - Use Redis for shared rate limiting state
   - Coordinate rate limits across instances
   - Maintain consistent rate limiting behavior
   - Estimated Effort: 6-8 hours

2. **Optimize Database Connection Pooling**
   - Review and optimize connection pool settings
   - Implement connection timeout mechanisms
   - Add connection pool monitoring
   - Estimated Effort: 4-6 hours

3. **Enhance Error Message Handling**
   - Implement error message sanitization
   - Ensure production mode suppresses verbose errors
   - Add error logging without exposing details to users
   - Estimated Effort: 2-4 hours

4. **Improve API Response Filtering**
   - Review all API endpoints for information disclosure
   - Implement response filtering middleware
   - Return only necessary data in responses
   - Estimated Effort: 4-6 hours

5. **Enhance Audit Logging**
   - Implement comprehensive audit logging for all user actions
   - Add context and metadata to log entries
   - Ensure all administrative actions are logged
   - Estimated Effort: 6-8 hours

6. **Strengthen Non-Repudiation**
   - Add digital signatures for critical operations
   - Enhance logging with cryptographic hashes
   - Implement tamper-evident logging
   - Estimated Effort: 8-10 hours

7. **Improve Log Sanitization**
   - Expand log sanitization to cover all log outputs
   - Remove sensitive information from logs
   - Implement log filtering for PII and secrets
   - Estimated Effort: 4-6 hours

8. **Enhance Token Scope Validation**
   - Review and harden scope validation logic
   - Add additional validation for edge cases
   - Implement scope testing
   - Estimated Effort: 4-6 hours

### Low Priority Mitigations

9. **Session Management Enhancement**
   - Add additional session validation
   - Implement session rotation mechanisms
   - Enhance session security
   - Estimated Effort: 2-4 hours

10. **OAuth Callback Validation**
    - Enhance OAuth callback URL validation
    - Add edge case handling
    - Improve redirect security
    - Estimated Effort: 2-4 hours

11. **SQL Injection Defense in Depth**
    - Add additional input validation
    - Implement query parameter validation
    - Add security testing for SQL injection
    - Estimated Effort: 2-4 hours

12. **Webhook Logging Enhancement**
    - Add comprehensive webhook request logging
    - Log request metadata and headers
    - Enhance webhook audit trail
    - Estimated Effort: 2-3 hours

13. **WebSocket Connection Management**
    - Implement connection limits
    - Add connection cleanup mechanisms
    - Enhance WebSocket resource management
    - Estimated Effort: 3-4 hours

14. **Container Security Hardening**
    - Use non-root users in containers
    - Implement minimal base images
    - Add container security scanning
    - Estimated Effort: 4-6 hours

---

## Security Controls

### Current Security Controls

✅ **Implemented:**
- JWT-based authentication
- Password hashing (bcrypt)
- SQL injection protection (SQLAlchemy ORM)
- API token authentication for webhooks
- Basic rate limiting (in-memory)
- Security event logging
- Input sanitization functions
- HTTPS enforcement (in production config)
- Security headers in Nginx
- Role-based access control
- OAuth integration

### Recommended Enhancements

🔄 **Medium Priority:**
- Distributed rate limiting (Redis-based)
- Enhanced audit logging
- Error message sanitization
- API response filtering
- Database connection pool optimization
- Log sanitization expansion
- Token scope validation hardening
- Non-repudiation mechanisms

🔄 **Low Priority:**
- Session management enhancements
- OAuth callback validation improvements
- SQL injection defense in depth
- Webhook logging enhancements
- WebSocket connection management
- Container security hardening

---

## Remediation Recommendations

### Immediate Actions (Medium Priority)

1. **Implement Distributed Rate Limiting** (T5.1)
   - Priority: Medium
   - Effort: 6-8 hours
   - Impact: Improves scalability and consistent rate limiting

2. **Optimize Database Connection Pooling** (T5.2)
   - Priority: Medium
   - Effort: 4-6 hours
   - Impact: Prevents connection exhaustion under load

3. **Enhance Error Message Handling** (T4.1)
   - Priority: Medium
   - Effort: 2-4 hours
   - Impact: Prevents information disclosure

### Short-term Actions (Medium Priority)

4. **Improve API Response Filtering** (T4.2)
   - Priority: Medium
   - Effort: 4-6 hours
   - Impact: Reduces information disclosure

5. **Enhance Audit Logging** (T3.1, T3.2)
   - Priority: Medium
   - Effort: 6-10 hours
   - Impact: Improves audit trail and compliance

6. **Expand Log Sanitization** (T4.3)
   - Priority: Medium
   - Effort: 4-6 hours
   - Impact: Prevents sensitive data in logs

7. **Harden Token Scope Validation** (T6.1)
   - Priority: Medium
   - Effort: 4-6 hours
   - Impact: Prevents privilege escalation

### Long-term Actions (Low Priority)

8. **Session Management Enhancement** (T1.1)
   - Priority: Low
   - Effort: 2-4 hours
   - Impact: Defense in depth

9. **OAuth Callback Validation** (T1.2)
   - Priority: Low
   - Effort: 2-4 hours
   - Impact: Enhanced OAuth security

10. **SQL Injection Defense in Depth** (T2.2)
    - Priority: Low
    - Effort: 2-4 hours
    - Impact: Additional protection layer

11. **Webhook Logging Enhancement** (T3.3)
    - Priority: Low
    - Effort: 2-3 hours
    - Impact: Improved audit trail

12. **WebSocket Connection Management** (T5.3)
    - Priority: Low
    - Effort: 3-4 hours
    - Impact: Better resource management

13. **Container Security Hardening** (T6.2)
    - Priority: Low
    - Effort: 4-6 hours
    - Impact: Reduced attack surface

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
| 2024 | 1.0 | Initial threat model (Medium and Low severity threats) | Security Team |

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

**Document Status:** Active  
**Next Review Date:** Quarterly  
**Owner:** Security Team
