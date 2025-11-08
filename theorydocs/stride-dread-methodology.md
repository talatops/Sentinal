# STRIDE/DREAD Methodology Guide

## Overview

STRIDE and DREAD are threat modeling methodologies used to identify and assess security threats in software systems. Project Sentinel implements an **advanced, intelligent version** of these methodologies with pattern recognition, automated scoring, and vulnerability correlation.

## STRIDE

STRIDE is an acronym representing six categories of threats:

### 1. Spoofing
**Definition**: Impersonating another user or system component.

**Examples**:
- Fake login pages
- IP address spoofing
- Email spoofing
- Session hijacking
- Authentication bypass

**Mitigation**:
- Strong authentication mechanisms
- Certificate-based authentication
- Multi-factor authentication (MFA)
- Secure session management
- Account lockout policies

**Detection in Project Sentinel**:
- Pattern: `authentication_bypass`, `session_management`
- Components: Authentication systems, login forms
- Keywords: "auth", "login", "credential", "password", "token", "session"

### 2. Tampering
**Definition**: Unauthorized modification of data or code.

**Examples**:
- Data manipulation in transit
- SQL injection
- Code injection
- Configuration file modification
- Command injection

**Mitigation**:
- Cryptographic signatures
- Input validation and sanitization
- Parameterized queries
- Code signing
- Integrity checks

**Detection in Project Sentinel**:
- Pattern: `sql_injection`, `command_injection`, `path_traversal`
- Components: APIs, databases, file systems
- Keywords: "sql", "query", "command", "execute", "file", "path"

### 3. Repudiation
**Definition**: Denying that an action occurred.

**Examples**:
- User denies making a transaction
- System denies receiving a request
- Log tampering
- Missing audit trails

**Mitigation**:
- Comprehensive audit logging
- Digital signatures
- Non-repudiation mechanisms
- Timestamping
- Immutable logs

**Detection in Project Sentinel**:
- Pattern: `csrf`
- Components: Logging systems, transaction systems
- Keywords: "log", "audit", "record", "transaction", "signature"

### 4. Information Disclosure
**Definition**: Unauthorized access to sensitive information.

**Examples**:
- Data leaks
- Unauthorized database access
- Information exposure in error messages
- Path traversal attacks
- XXE attacks

**Mitigation**:
- Encryption (at rest and in transit)
- Access controls
- Least privilege principle
- Data masking
- Secure error handling

**Detection in Project Sentinel**:
- Pattern: `sql_injection`, `xss`, `path_traversal`, `xxe`, `sensitive_data_exposure`
- Components: Databases, APIs, file systems
- Keywords: "database", "file", "read", "access", "expose", "leak"

### 5. Denial of Service (DoS)
**Definition**: Preventing legitimate users from accessing services.

**Examples**:
- Resource exhaustion
- Network flooding
- Application crashes
- DDoS attacks
- Slowloris attacks

**Mitigation**:
- Rate limiting
- Resource quotas
- Load balancing
- Redundancy
- DDoS protection

**Detection in Project Sentinel**:
- Pattern: `dos`, `ssrf`
- Components: APIs, networks, backends
- Keywords: "dos", "denial", "resource", "exhaustion", "flood", "limit"

### 6. Elevation of Privilege
**Definition**: Gaining unauthorized access to higher privileges.

**Examples**:
- Privilege escalation exploits
- Bypassing authorization checks
- Admin account compromise
- IDOR vulnerabilities
- Broken access control

**Mitigation**:
- Principle of least privilege
- Role-based access control (RBAC)
- Regular security audits
- Privilege separation
- Authorization checks

**Detection in Project Sentinel**:
- Pattern: `authentication_bypass`, `idor`, `broken_access_control`
- Components: Authorization systems, APIs, admin panels
- Keywords: "authorization", "privilege", "admin", "access", "bypass", "elevation"

## DREAD

DREAD is a risk assessment model that quantifies threats:

### Components

1. **Damage** (0-10)
   - How severe would an attack be?
   - Impact on business, users, data
   - **Automated Scoring**: Based on threat pattern, asset criticality, component type

2. **Reproducibility** (0-10)
   - How easy is it to reproduce the attack?
   - Can it be triggered reliably?
   - **Automated Scoring**: Based on pattern characteristics, attack complexity

3. **Exploitability** (0-10)
   - How easy is it to launch the attack?
   - Technical skills required
   - **Automated Scoring**: Based on pattern exploitability, tool availability

4. **Affected Users** (0-10)
   - How many users would be impacted?
   - Percentage of user base
   - **Automated Scoring**: Based on component type, system exposure

5. **Discoverability** (0-10)
   - How easy is it to discover the vulnerability?
   - Public knowledge, documentation
   - **Automated Scoring**: Based on external exposure, pattern visibility

### Risk Calculation

```
DREAD Score = (Damage + Reproducibility + Exploitability + Affected Users + Discoverability) / 5
```

### Risk Levels

- **High**: Score > 7
  - Immediate action required
  - Critical security issue
  - Potential for significant damage
  - Red badge in UI

- **Medium**: Score 4-7
  - Address in next sprint
  - Moderate security concern
  - Requires attention
  - Yellow badge in UI

- **Low**: Score < 4
  - Monitor and address in maintenance
  - Low priority
  - Minimal impact
  - Green badge in UI

## Using STRIDE/DREAD in Project Sentinel

### Threat Analysis Process

1. **Identify Assets**
   - What are you protecting?
   - Databases, APIs, user data, etc.
   - System automatically detects component types

2. **Map Data Flows**
   - How does data move through the system?
   - Identify trust boundaries
   - Describe the flow in detail for better pattern matching

3. **Apply STRIDE (Automatic)**
   - System uses advanced pattern matching
   - Detects threat patterns from description
   - Identifies STRIDE categories with confidence scores
   - Shows matched patterns and component types

4. **Calculate DREAD (Automated or Manual)**
   - **Automated Mode**: System suggests scores based on patterns
   - **Manual Mode**: User provides scores (0-10 for each dimension)
   - System calculates total risk score automatically
   - Shows confidence levels for automated suggestions

5. **Prioritize Mitigations**
   - System provides prioritized, contextual recommendations
   - Address High risks first
   - Plan Medium risks
   - Monitor Low risks
   - Link to actual vulnerabilities for confirmed threats

### Example Analysis

**Asset**: User Authentication System

**Data Flow**: User → Login Form → Authentication Service → Database

**Advanced STRIDE Analysis**:
- **Component Detection**: `['frontend', 'api', 'authentication', 'database']`
- **Pattern Matching**: 
  - `authentication_bypass` (confidence: 0.85)
  - `session_management` (confidence: 0.8)
- **STRIDE Threats**:
  - Spoofing (confidence: 0.85) - Authentication component
  - Tampering (confidence: 0.7) - Database component
  - Information Disclosure (confidence: 0.7) - Database component
  - Denial of Service (confidence: 0.6) - Database component
  - Elevation of Privilege (confidence: 0.85) - Authentication bypass pattern

**Automated DREAD Scoring**:
- Damage: 9 (90% confidence) - Authentication compromise affects all users
- Reproducibility: 8 (85% confidence) - Easy to reproduce login attacks
- Exploitability: 6 (75% confidence) - Moderate skill required
- Affected Users: 10 (95% confidence) - All users affected
- Discoverability: 7 (80% confidence) - Well-known attack vectors

**Total Score**: (9+8+6+10+7)/5 = 8.0 → **High Risk**

**Enhanced Mitigation**:
- **High Priority**:
  - "CRITICAL: Implement strong authentication mechanisms immediately" (Effectiveness: 10/10)
  - "Enable multi-factor authentication (MFA) for all users" (Effectiveness: 9/10)
  - "Use secure password storage (bcrypt, Argon2)" (Effectiveness: 8/10)
- **Medium Priority**:
  - "Implement account lockout after failed login attempts" (Effectiveness: 7/10)
  - "Use secure session management with proper expiration" (Effectiveness: 8/10)
- **Risk-Level Action**:
  - "URGENT: Address immediately. Schedule security review and penetration testing."

## Advanced Features in Project Sentinel

### 1. Threat Pattern Library

14 pre-defined patterns covering OWASP Top 10 and common vulnerabilities:
- SQL Injection
- Cross-Site Scripting (XSS)
- Authentication Bypass
- IDOR
- CSRF
- Session Management Issues
- Path Traversal
- Command Injection
- XXE
- Insecure Deserialization
- SSRF
- Broken Access Control
- Sensitive Data Exposure
- Denial of Service

### 2. Vulnerability Correlation

Link theoretical threats to actual vulnerabilities:
- **SonarQube (SAST)**: Static analysis findings
- **OWASP ZAP (DAST)**: Dynamic analysis alerts
- **Trivy**: Container vulnerability scans

Benefits:
- Distinguish confirmed vs. theoretical threats
- Prioritize threats with actual exploits
- Track resolution status
- Visual correlation matrix

### 3. Threat Similarity Detection

Find similar threats using:
- Text similarity
- STRIDE category overlap
- DREAD score similarity
- Asset type matching

Helps learn from past threats and improve analysis.

### 4. Threat Templates

8 pre-built templates for common scenarios:
- SQL Injection in API Endpoint
- Cross-Site Scripting (XSS)
- Authentication Bypass
- IDOR
- CSRF
- Session Management
- Path Traversal
- Command Injection

### 5. Visualization

- **Threat Diagrams**: Interactive data flow visualization (ReactFlow)
- **Threat Matrix**: STRIDE vs Asset heatmap
- **Vulnerability Correlation**: Visual threat-vulnerability relationships

### 6. Analytics

- Threat statistics and trends
- Risk level distribution
- STRIDE category distribution
- Most vulnerable assets
- Average DREAD scores
- Threat resolution rates

## Best Practices

1. **Regular Reviews**
   - Conduct threat modeling sessions
   - Update as system evolves
   - Include security team
   - Use threat templates for common scenarios

2. **Documentation**
   - Document all threats
   - Track mitigations
   - Review periodically
   - Link to vulnerabilities

3. **Integration**
   - Integrate into SDLC
   - Include in code reviews
   - Automated threat detection from scans
   - Real-time vulnerability correlation

4. **Training**
   - Educate development team
   - Share threat intelligence
   - Learn from incidents
   - Use threat similarity to learn from past threats

5. **Use Advanced Features**
   - Enable auto-scoring for faster analysis
   - Review confidence scores
   - Use threat templates
   - Link vulnerabilities to threats
   - Explore similar threats

## References

- Microsoft STRIDE Model
- OWASP Threat Modeling
- OWASP Top 10
- NIST Cybersecurity Framework
- DREAD Risk Assessment Model

## Implementation Details

Project Sentinel implements STRIDE/DREAD with:
- **Advanced Pattern Recognition**: 14 threat patterns with regex matching
- **Component Detection**: Automatic component type identification
- **Automated DREAD Scoring**: Pattern-based suggestions with confidence
- **Enhanced Mitigations**: Contextual, prioritized recommendations
- **Vulnerability Correlation**: Link threats to scan findings
- **Threat Similarity**: Find similar threats for learning
- **Threat Templates**: Pre-built templates for common scenarios
- **Visualization**: Interactive diagrams and matrices
- **Analytics**: Comprehensive threat statistics

See `theorydocs/how-stride-dread-works.md` for detailed implementation guide.
