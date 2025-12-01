# Threat Mapping Examples for Project Sentinel

This document provides comprehensive threat mapping examples specific to the Project Sentinel DevSecOps Framework architecture. These examples can be used directly in the threat modeling interface.

## Table of Contents
1. [Authentication & Authorization Threats](#authentication--authorization-threats)
2. [API Endpoint Threats](#api-endpoint-threats)
3. [Database & Data Storage Threats](#database--data-storage-threats)
4. [CI/CD Pipeline Threats](#cicd-pipeline-threats)
5. [Frontend & Client-Side Threats](#frontend--client-side-threats)
6. [Security Scanning Integration Threats](#security-scanning-integration-threats)
7. [WebSocket & Real-Time Communication Threats](#websocket--real-time-communication-threats)
8. [Docker & Container Threats](#docker--container-threats)

---

## Authentication & Authorization Threats

### Example 1: JWT Token Theft via XSS
**Asset**: JWT Authentication System  
**Data Flow**: User logs in → Frontend receives JWT token → Token stored in localStorage → XSS attack steals token → Attacker uses token to access API  
**Trust Boundary**: User Browser → Frontend React App → Backend Flask API → PostgreSQL Database

**DREAD Scores** (Manual):
- Damage: 9
- Reproducibility: 7
- Exploitability: 8
- Affected Users: 8
- Discoverability: 6

**Expected STRIDE Categories**: Spoofing, Information Disclosure, Elevation of Privilege

**Mitigation Recommendations**:
- Store JWT tokens in httpOnly cookies instead of localStorage
- Implement Content Security Policy (CSP) headers
- Use short-lived access tokens with refresh token rotation
- Enable XSS protection in React (sanitize user inputs)

---

### Example 2: Weak Password Policy in User Registration
**Asset**: User Registration API Endpoint  
**Data Flow**: User submits registration form → Frontend sends credentials via POST → Backend validates and stores password hash → Weak password policy allows simple passwords → Attacker brute forces accounts  
**Trust Boundary**: Public Internet → Nginx Proxy → Flask API → PostgreSQL Database

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Spoofing, Elevation of Privilege

**Mitigation Recommendations**:
- Enforce strong password policy (min 12 chars, complexity requirements)
- Implement password strength meter
- Add rate limiting on registration endpoint
- Use bcrypt or Argon2 for password hashing

---

### Example 3: Session Fixation Attack
**Asset**: Session Management System  
**Data Flow**: User authenticates → Backend creates session token → Token not regenerated after login → Attacker who obtained token before login gains access → Session remains valid  
**Trust Boundary**: Client Browser → Flask API → Session Store

**DREAD Scores** (Manual):
- Damage: 7
- Reproducibility: 6
- Exploitability: 5
- Affected Users: 6
- Discoverability: 4

**Expected STRIDE Categories**: Spoofing, Elevation of Privilege

**Mitigation Recommendations**:
- Regenerate session tokens after successful authentication
- Implement secure session management with proper expiration
- Use secure, random session identifiers
- Invalidate old sessions on password change

---

## API Endpoint Threats

### Example 4: SQL Injection in Threat Analysis Endpoint
**Asset**: Threat Modeling API (`/api/threats/analyze`)  
**Data Flow**: User submits threat analysis → Backend processes threat description → SQL query constructed using string concatenation → Attacker injects malicious SQL payload in flow field → Database compromised  
**Trust Boundary**: Authenticated User → Flask API → PostgreSQL Database

**DREAD Scores** (Manual):
- Damage: 10
- Reproducibility: 9
- Exploitability: 9
- Affected Users: 10
- Discoverability: 5

**Expected STRIDE Categories**: Tampering, Information Disclosure, Denial of Service, Elevation of Privilege

**Mitigation Recommendations**:
- Use parameterized queries (SQLAlchemy ORM)
- Implement input validation and sanitization
- Apply least privilege database user permissions
- Enable SQL injection detection in WAF

---

### Example 5: Insecure Direct Object Reference (IDOR) in Threat Details
**Asset**: Threat Detail API (`/api/threats/{id}`)  
**Data Flow**: User requests threat details → API endpoint `/api/threats/{id}` returns threat data → No authorization check verifies requester owns threat → Attacker enumerates threat IDs → Accesses all threat data including sensitive information  
**Trust Boundary**: Authenticated User → Flask API → PostgreSQL Database

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Information Disclosure, Elevation of Privilege

**Mitigation Recommendations**:
- Implement authorization checks before returning threat data
- Use indirect object references (UUIDs instead of sequential IDs)
- Add access control lists (ACLs) for threat resources
- Log all access attempts for audit

---

### Example 6: Mass Assignment in Requirements API
**Asset**: Requirements Update API (`/api/requirements/{id}`)  
**Data Flow**: User updates requirement → Frontend sends JSON payload → Backend directly assigns all fields from request → Attacker includes unauthorized fields (e.g., `created_by`, `status`) → Unauthorized data modification  
**Trust Boundary**: Authenticated User → Flask API → PostgreSQL Database

**DREAD Scores** (Manual):
- Damage: 6
- Reproducibility: 8
- Exploitability: 7
- Affected Users: 5
- Discoverability: 6

**Expected STRIDE Categories**: Tampering, Elevation of Privilege

**Mitigation Recommendations**:
- Use explicit field allowlists in update operations
- Implement schema validation (Marshmallow)
- Separate DTOs for create/update operations
- Add role-based field restrictions

---

## Database & Data Storage Threats

### Example 7: Unencrypted Sensitive Data at Rest
**Asset**: PostgreSQL Database  
**Data Flow**: Application stores user data → Data written to PostgreSQL → Database files stored on disk without encryption → Attacker gains physical/database access → Reads all sensitive data including passwords, API tokens, PII  
**Trust Boundary**: Application Server → PostgreSQL Database → Disk Storage

**DREAD Scores** (Manual):
- Damage: 9
- Reproducibility: 5
- Exploitability: 4
- Affected Users: 10
- Discoverability: 3

**Expected STRIDE Categories**: Information Disclosure

**Mitigation Recommendations**:
- Enable PostgreSQL Transparent Data Encryption (TDE)
- Encrypt sensitive columns at application level
- Use encrypted filesystem for database storage
- Implement field-level encryption for PII
- Regular security audits of database access

---

### Example 8: Database Connection String Exposure
**Asset**: Database Configuration  
**Data Flow**: Application reads database connection string from environment variables → Connection string logged in error messages → Error message returned to client → Attacker extracts database credentials → Direct database access  
**Trust Boundary**: Application Server → Error Handler → Client Browser

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Information Disclosure

**Mitigation Recommendations**:
- Never log sensitive configuration in error messages
- Use generic error messages for clients
- Store credentials in secure secret management (Vault, AWS Secrets Manager)
- Implement proper error handling and sanitization
- Use connection pooling with encrypted connections

---

## CI/CD Pipeline Threats

### Example 9: GitHub Actions Secret Exposure
**Asset**: CI/CD Pipeline Secrets  
**Data Flow**: GitHub Actions workflow runs → Secrets accessed via `${{ secrets.API_TOKEN }}` → Secret accidentally logged in workflow output → Attacker views workflow logs → Extracts API tokens and credentials → Unauthorized access to systems  
**Trust Boundary**: GitHub Actions Runner → Workflow Logs → Public/Private Repository

**DREAD Scores** (Manual):
- Damage: 8
- Reproducibility: 7
- Exploitability: 6
- Affected Users: 7
- Discoverability: 8

**Expected STRIDE Categories**: Information Disclosure, Spoofing, Elevation of Privilege

**Mitigation Recommendations**:
- Never echo secrets in workflow logs
- Use secret masking in GitHub Actions
- Implement least privilege for CI/CD tokens
- Rotate secrets regularly
- Audit workflow access permissions
- Use OIDC for cloud provider authentication

---

### Example 10: Malicious Code Injection in CI/CD Pipeline
**Asset**: CI/CD Pipeline Execution  
**Data Flow**: Developer commits code → GitHub webhook triggers CI/CD pipeline → Pipeline executes build and security scans → Attacker injects malicious code in dependency → Pipeline executes malicious code → System compromise  
**Trust Boundary**: GitHub Repository → CI/CD Pipeline → Build Environment → Production

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Tampering, Elevation of Privilege, Denial of Service

**Mitigation Recommendations**:
- Use dependency scanning (Trivy, Snyk)
- Implement code signing and verification
- Use pinned dependency versions
- Run pipelines in isolated containers
- Implement approval workflows for production deployments
- Scan container images before deployment

---

### Example 11: SonarQube Integration Token Theft
**Asset**: SonarQube API Integration  
**Data Flow**: Backend connects to SonarQube API → Uses API token stored in environment → Token logged or exposed in error → Attacker obtains token → Accesses SonarQube API → Modifies scan results or accesses sensitive code analysis data  
**Trust Boundary**: Flask Backend → SonarQube API (Port 9000)

**DREAD Scores** (Manual):
- Damage: 6
- Reproducibility: 5
- Exploitability: 4
- Affected Users: 4
- Discoverability: 3

**Expected STRIDE Categories**: Spoofing, Information Disclosure, Tampering

**Mitigation Recommendations**:
- Store SonarQube tokens in secure secret management
- Use least privilege tokens (read-only when possible)
- Implement token rotation policy
- Monitor API access logs
- Use IP whitelisting for SonarQube access

---

## Frontend & Client-Side Threats

### Example 12: Cross-Site Scripting (XSS) in Threat Description Display
**Asset**: Threat Modeling Frontend  
**Data Flow**: User creates threat with malicious script in description → Threat stored in database → Frontend displays threat description without sanitization → Malicious script executes in other users' browsers → Session theft or data exfiltration  
**Trust Boundary**: User Input → React Frontend → User Browser → Other Users' Browsers

**DREAD Scores** (Manual):
- Damage: 7
- Reproducibility: 8
- Exploitability: 7
- Affected Users: 8
- Discoverability: 6

**Expected STRIDE Categories**: Tampering, Information Disclosure, Spoofing

**Mitigation Recommendations**:
- Sanitize all user inputs before display
- Use React's built-in XSS protection (auto-escaping)
- Implement Content Security Policy (CSP) headers
- Use DOMPurify for HTML sanitization
- Encode output properly (HTML entity encoding)

---

### Example 13: Insecure API Token Storage in Frontend
**Asset**: API Token Management Frontend  
**Data Flow**: Admin creates API token → Token displayed in frontend → Token stored in React state or localStorage → Token accessible via browser DevTools → Attacker with physical access steals token → Unauthorized API access  
**Trust Boundary**: Admin User → React Frontend → Browser Storage → Attacker

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Information Disclosure, Spoofing, Elevation of Privilege

**Mitigation Recommendations**:
- Never display full API tokens in UI (show masked version)
- Store tokens server-side only
- Implement token expiration and rotation
- Use secure token generation (cryptographically random)
- Add audit logging for token access

---

## Security Scanning Integration Threats

### Example 14: OWASP ZAP False Positive Injection
**Asset**: OWASP ZAP Integration  
**Data Flow**: CI/CD pipeline triggers ZAP scan → ZAP scans application → ZAP identifies false positive vulnerability → Results stored in database → Threat modeling system links false positive to threat → Development team wastes time on non-issue  
**Trust Boundary**: CI/CD Pipeline → OWASP ZAP (Port 8090) → Flask Backend → PostgreSQL

**DREAD Scores** (Manual):
- Damage: 2
- Reproducibility: 9
- Exploitability: 1
- Affected Users: 3
- Discoverability: 8

**Expected STRIDE Categories**: Information Disclosure (false positive)

**Mitigation Recommendations**:
- Implement false positive detection and filtering
- Manual review process for scan results
- Tune ZAP scan policies to reduce false positives
- Link scan results to threat models for context
- Implement confidence scoring for vulnerabilities

---

### Example 15: Trivy Container Scan Bypass
**Asset**: Container Security Scanning  
**Data Flow**: Docker image built → Trivy scans image for vulnerabilities → Scan runs in CI/CD → Attacker introduces vulnerability in base image → Trivy scan misses vulnerability → Vulnerable container deployed to production → System compromise  
**Trust Boundary**: CI/CD Pipeline → Trivy Scanner → Container Registry → Production Environment

**DREAD Scores** (Manual):
- Damage: 8
- Reproducibility: 4
- Exploitability: 5
- Affected Users: 7
- Discoverability: 3

**Expected STRIDE Categories**: Tampering, Elevation of Privilege, Information Disclosure

**Mitigation Recommendations**:
- Use trusted base images only
- Implement multi-stage scanning (build-time and runtime)
- Enforce scan result gates in CI/CD
- Regularly update Trivy vulnerability database
- Use image signing and verification
- Implement runtime security monitoring

---

## WebSocket & Real-Time Communication Threats

### Example 16: WebSocket Authentication Bypass
**Asset**: WebSocket Server (SocketIO)  
**Data Flow**: Client connects to WebSocket → WebSocket connection established without proper authentication → Real-time updates sent to unauthenticated clients → Sensitive CI/CD scan results leaked → Information disclosure  
**Trust Boundary**: Client Browser → WebSocket Server → Real-Time Updates

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Spoofing, Information Disclosure, Elevation of Privilege

**Mitigation Recommendations**:
- Authenticate WebSocket connections using JWT tokens
- Implement authorization checks for WebSocket events
- Use secure WebSocket (WSS) in production
- Validate message origins and permissions
- Implement rate limiting on WebSocket connections

---

### Example 17: WebSocket Message Injection
**Asset**: WebSocket Message Handler  
**Data Flow**: Client sends WebSocket message → Backend processes message without validation → Malicious payload in message → Backend executes or stores malicious data → System compromise or data corruption  
**Trust Boundary**: Client Browser → WebSocket Server → Backend Processing → Database

**DREAD Scores** (Manual):
- Damage: 7
- Reproducibility: 8
- Exploitability: 7
- Affected Users: 6
- Discoverability: 5

**Expected STRIDE Categories**: Tampering, Information Disclosure, Denial of Service

**Mitigation Recommendations**:
- Validate all WebSocket message payloads
- Implement message schema validation
- Use input sanitization for WebSocket messages
- Implement message size limits
- Add authentication and authorization checks

---

## Docker & Container Threats

### Example 18: Container Escape via Privileged Mode
**Asset**: Docker Container Configuration  
**Data Flow**: Application runs in Docker container → Container started with `--privileged` flag → Container has excessive permissions → Attacker gains access to container → Escapes to host system → Full system compromise  
**Trust Boundary**: Docker Container → Host System → Other Containers

**DREAD Scores** (Manual):
- Damage: 10
- Reproducibility: 6
- Exploitability: 5
- Affected Users: 9
- Discoverability: 4

**Expected STRIDE Categories**: Elevation of Privilege, Tampering, Information Disclosure

**Mitigation Recommendations**:
- Never run containers in privileged mode
- Use read-only root filesystems when possible
- Implement least privilege container users
- Use Docker security profiles (AppArmor, SELinux)
- Limit container capabilities
- Implement container runtime security monitoring

---

### Example 19: Insecure Docker Image Registry
**Asset**: Docker Image Registry  
**Data Flow**: Developer builds Docker image → Image pushed to registry → Registry lacks authentication → Public access to registry → Attacker pulls images → Extracts secrets or reverse engineers application → System compromise  
**Trust Boundary**: Build Environment → Docker Registry → Public Internet

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Information Disclosure, Tampering, Spoofing

**Mitigation Recommendations**:
- Implement authentication for Docker registry
- Use private registries for production images
- Sign and verify container images
- Implement access controls and RBAC
- Scan images before pushing to registry
- Use encrypted connections (HTTPS) for registry

---

### Example 20: Docker Compose Network Exposure
**Asset**: Docker Compose Network Configuration  
**Data Flow**: Services defined in docker-compose.yml → Services communicate via Docker network → Network misconfigured exposes services → Attacker on same network accesses internal services → Bypasses firewall rules → Unauthorized access  
**Trust Boundary**: Docker Network → Internal Services → External Network

**DREAD Scores** (Manual):
- Damage: 6
- Reproducibility: 5
- Exploitability: 4
- Affected Users: 5
- Discoverability: 3

**Expected STRIDE Categories**: Information Disclosure, Spoofing, Elevation of Privilege

**Mitigation Recommendations**:
- Use isolated Docker networks
- Implement network segmentation
- Use firewall rules within Docker networks
- Limit service-to-service communication
- Use Docker secrets for sensitive data
- Implement network policies

---

## Nginx & Reverse Proxy Threats

### Example 21: Nginx Configuration Injection
**Asset**: Nginx Reverse Proxy Configuration  
**Data Flow**: Nginx serves as reverse proxy → Configuration file contains user-controlled variables → Attacker injects malicious configuration → Nginx executes malicious config → Request routing manipulation or system compromise  
**Trust Boundary**: Public Internet → Nginx Proxy → Backend Services

**DREAD Scores** (Manual):
- Damage: 7
- Reproducibility: 4
- Exploitability: 3
- Affected Users: 6
- Discoverability: 2

**Expected STRIDE Categories**: Tampering, Denial of Service, Elevation of Privilege

**Mitigation Recommendations**:
- Validate all Nginx configuration inputs
- Use static configuration files
- Implement configuration file integrity checks
- Run Nginx with least privileges
- Regularly audit Nginx configurations
- Use configuration management tools

---

### Example 22: Missing Security Headers in Nginx
**Asset**: Nginx HTTP Headers Configuration  
**Data Flow**: Client requests resource → Nginx serves response → Security headers (CSP, HSTS, X-Frame-Options) missing → Browser vulnerable to XSS, clickjacking, MITM attacks → User data compromised  
**Trust Boundary**: Client Browser → Nginx Proxy → Backend Services

**DREAD Scores** (Auto-scoring enabled):
- Enable automatic DREAD scoring

**Expected STRIDE Categories**: Information Disclosure, Spoofing, Tampering

**Mitigation Recommendations**:
- Implement Content Security Policy (CSP) headers
- Enable HTTP Strict Transport Security (HSTS)
- Set X-Frame-Options to prevent clickjacking
- Implement X-Content-Type-Options: nosniff
- Add Referrer-Policy headers
- Use security header scanning tools

---

## How to Use These Examples

### Via Frontend UI:
1. Navigate to the Threat Modeling page
2. Fill in the form with any example above:
   - **Asset**: Copy from example
   - **Data Flow**: Copy from example
   - **Trust Boundary**: Copy from example (if provided)
   - **DREAD Scores**: Either enable auto-scoring or enter manual scores
3. Click "Analyze Threat"
4. Review the STRIDE categories and mitigation recommendations

### Via API:
```bash
# First, get authentication token
TOKEN=$(curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' \
  | jq -r '.access_token')

# Example: Analyze SQL Injection threat
curl -X POST http://localhost/api/threats/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "Threat Modeling API",
    "flow": "User submits threat analysis. Backend processes threat description. SQL query constructed using string concatenation. Attacker injects malicious SQL payload in flow field. Database compromised.",
    "trust_boundary": "Authenticated User -> Flask API -> PostgreSQL Database",
    "auto_score": false,
    "damage": 10,
    "reproducibility": 9,
    "exploitability": 9,
    "affected_users": 10,
    "discoverability": 5
  }' | jq '.'
```

---

## Best Practices for Threat Mapping

1. **Be Specific**: Provide detailed data flows to help pattern matching
2. **Include Trust Boundaries**: Clearly define where trust changes
3. **Use Auto-Scoring First**: Let the system suggest DREAD scores, then adjust if needed
4. **Link to Vulnerabilities**: After creating threats, link them to actual scan findings
5. **Review Similar Threats**: Use the similarity feature to learn from past analyses
6. **Update Regularly**: Re-analyze threats as the system evolves
7. **Document Mitigations**: Track which mitigations have been implemented

---

## Additional Resources

- [STRIDE/DREAD Methodology Guide](../theorydocs/stride-dread-methodology.md)
- [How STRIDE/DREAD Works](../theorydocs/how-stride-dread-works.md)
- [Threat Modeling Test Examples](../tests/test-threat-modeling-examples.md)
- [Project Architecture](../techdocs/architecture.md)

