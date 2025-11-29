# Project Sentinel - Slide Content

## Slide 1: Core Concept - Security-by-Design Framework

### Title: Project Sentinel - Secure-by-Design DevSecOps Framework

**Key Concepts:**
- **Integrated Security**: Security embedded in every SDLC stage
- **Automated Threat Modeling**: STRIDE/DREAD methodology with pattern recognition
- **Requirements-Driven Security**: Enforced security controls mapping
- **Continuous Security Scanning**: SAST, DAST, and container scanning in CI/CD
- **Threat-Vulnerability Correlation**: Links theoretical threats to actual scan findings

**Core Philosophy:**
- Shift-left security: Identify threats before deployment
- Security requirements as first-class citizens
- Automated risk assessment with confidence indicators
- Real-time security visibility across the pipeline

---

## Slide 2: Threat Modeling Workflow - STRIDE/DREAD Analysis

### Title: Intelligent Threat Modeling with Automated Analysis

**Workflow Overview:**
1. **Input**: Developer describes asset, data flow, and trust boundaries
2. **STRIDE Analysis**: Pattern matching engine identifies threat categories
3. **DREAD Scoring**: Automated risk assessment with pattern-based suggestions
4. **Risk Calculation**: Automatic risk level assignment (High/Medium/Low)
5. **Mitigation Recommendations**: Context-aware security controls

**Key Features:**
- **14 Threat Patterns**: Pre-defined patterns covering OWASP Top 10
- **Component Detection**: Automatic identification of system components
- **Confidence Scoring**: Pattern matching with confidence indicators
- **Enhanced Mitigations**: Priority-ranked, component-specific recommendations

**Sequence Diagram:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant UI as Frontend UI
    participant API as Backend API
    participant STRIDE as STRIDE Engine
    participant Pattern as Pattern Matcher
    participant DREAD as DREAD Scorer
    participant DB as Database

    Dev->>UI: Submit Threat (Asset, Flow, Trust Boundary)
    UI->>API: POST /api/threats/analyze
    API->>STRIDE: analyze_threat_advanced()
    STRIDE->>Pattern: match_threat_patterns()
    Pattern-->>STRIDE: Matched Patterns + Confidence
    STRIDE->>STRIDE: detect_component_type()
    STRIDE-->>API: STRIDE Categories + Patterns + Components
    
    API->>DREAD: suggest_dread_scores()
    DREAD->>Pattern: get_suggested_dread_from_patterns()
    Pattern-->>DREAD: Suggested Scores + Confidence
    DREAD-->>API: DREAD Scores + Explanations
    
    API->>API: Calculate Risk Level
    API->>API: Get Mitigation Recommendations
    API->>DB: Save Threat Record
    DB-->>API: Threat Saved
    API-->>UI: Analysis Result (STRIDE, DREAD, Risk, Mitigations)
    UI-->>Dev: Display Results Modal
```

---

## Slide 3: Requirements Management Workflow

### Title: Security Requirements with Enforced Controls

**Workflow Overview:**
1. **Requirement Creation**: Define functional requirement with security controls
2. **Control Mapping**: One-to-one mapping of security controls to requirements
3. **OWASP ASVS Alignment**: Link controls to OWASP ASVS levels
4. **Compliance Tracking**: Admin dashboard for compliance auditing
5. **Export & Reporting**: Export requirements as CSV/JSON for audits

**Key Features:**
- **Enforced Controls**: Every requirement must have at least one security control
- **OWASP ASVS Integration**: Level 1, 2, 3 compliance tracking
- **Compliance Dashboard**: Real-time compliance rate calculation
- **Audit Trail**: Complete history of requirement changes

**Sequence Diagram:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant UI as Frontend UI
    participant API as Backend API
    participant DB as Database
    participant Admin as Admin Dashboard

    Dev->>UI: Create Requirement + Security Controls
    UI->>API: POST /api/requirements
    API->>API: Validate (Zod Schema)
    API->>DB: Save Requirement + Controls
    DB-->>API: Requirement Created
    
    Admin->>UI: View Compliance Dashboard
    UI->>API: GET /api/requirements/compliance
    API->>DB: Query Requirements + Controls
    DB-->>API: Compliance Data
    API->>API: Calculate Compliance Rate
    API-->>UI: Compliance Metrics
    UI-->>Admin: Display Dashboard
    
    Dev->>UI: Export Requirements
    UI->>API: GET /api/requirements/export?format=json
    API->>DB: Fetch All Requirements
    DB-->>API: Requirements Data
    API-->>UI: JSON/CSV Export
```

---

## Slide 4: CI/CD Security Scanning Workflow

### Title: Continuous Security Scanning in CI/CD Pipeline

**Workflow Overview:**
1. **Code Push**: Developer pushes code to repository
2. **GitHub Actions Trigger**: CI/CD pipeline automatically starts
3. **Parallel Security Scans**: SAST (SonarQube), DAST (ZAP), Container (Trivy)
4. **Results Aggregation**: Backend receives scan results via webhooks
5. **Deployment Gate**: Blocks deployment if critical vulnerabilities found
6. **Real-time Dashboard**: WebSocket updates show scan progress

**Key Features:**
- **Multi-Tool Integration**: SonarQube, OWASP ZAP, Trivy
- **Webhook Authentication**: API token-based secure webhooks
- **Automatic Threat Detection**: Scan findings auto-create threat records
- **Deployment Gates**: Configurable blocking rules based on severity

**Sequence Diagram:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub Actions
    participant SQ as SonarQube
    participant ZAP as OWASP ZAP
    participant Trivy as Trivy
    participant API as Backend API
    participant WS as WebSocket
    participant UI as Dashboard
    participant Detector as Threat Detector

    Dev->>GH: Push Code
    GH->>SQ: Run SAST Scan
    GH->>ZAP: Run DAST Scan
    GH->>Trivy: Run Container Scan
    
    SQ-->>GH: SAST Results
    ZAP-->>GH: DAST Results
    Trivy-->>GH: Trivy Results
    
    GH->>API: POST /api/cicd/webhook/sonarqube (with token)
    GH->>API: POST /api/cicd/webhook/zap (with token)
    GH->>API: POST /api/cicd/webhook/trivy (with token)
    
    API->>API: Authenticate Webhook (API Token)
    API->>API: Store Scan Results
    API->>Detector: detect_threats_from_scan()
    Detector->>Detector: Process SAST/DAST/Trivy Results
    Detector->>Detector: Create/Link Threats
    Detector-->>API: Threats Created
    
    API->>WS: emit_scan_update()
    WS->>UI: Real-time Update
    UI->>UI: Update Dashboard
    
    API->>API: Check Deployment Gate
    alt Critical Vulnerabilities Found
        API-->>GH: Block Deployment
    else No Critical Issues
        API-->>GH: Allow Deployment
    end
```

---

## Slide 5: Threat-Vulnerability Correlation

### Title: Bridging Theory and Reality - Threat-Vulnerability Correlation

**Workflow Overview:**
1. **Threat Modeling**: Create theoretical threats via STRIDE/DREAD
2. **Security Scanning**: CI/CD scans discover actual vulnerabilities
3. **Automatic Correlation**: Threat Detector service links scan findings to threats
4. **Visual Matrix**: Threat-Vulnerability correlation matrix visualization
5. **Risk Prioritization**: Focus on threats with confirmed vulnerabilities

**Key Features:**
- **Automatic Linking**: Pattern-based matching of scan findings to threats
- **Bidirectional View**: View threats with vulnerabilities or vulnerabilities with threats
- **Risk Assessment**: Distinguish theoretical vs. confirmed threats
- **Mitigation Tracking**: Track which threats have been addressed

**Sequence Diagram:**

```mermaid
sequenceDiagram
    participant Threat as Threat Model
    participant Scan as Security Scan
    participant Detector as Threat Detector
    participant Pattern as Pattern Matcher
    participant DB as Database
    participant UI as Correlation Matrix

    Threat->>DB: Save Threat (STRIDE/DREAD)
    Scan->>DB: Save Scan Results (SonarQube/ZAP/Trivy)
    
    Scan->>Detector: detect_threats_from_scan(scan_id)
    Detector->>Detector: Extract Issues from Scan
    Detector->>Pattern: match_threat_patterns(issue)
    Pattern-->>Detector: Matched Threat Patterns
    
    Detector->>DB: Query Existing Threats
    DB-->>Detector: Potential Matching Threats
    Detector->>Detector: Calculate Similarity Score
    Detector->>DB: Create ThreatVulnerability Link
    
    UI->>DB: GET /api/threats/with-vulnerabilities
    DB-->>UI: Threats + Linked Vulnerabilities
    UI->>UI: Render Correlation Matrix
    
    UI->>UI: Filter (All/With Vulns/Without Vulns)
    UI->>UI: Display Threat Details + Vulnerabilities
```

---

## Slide 6: Real-time Dashboard & WebSocket Architecture

### Title: Real-time Security Visibility

**Workflow Overview:**
1. **WebSocket Connection**: Frontend establishes persistent connection
2. **Event Subscription**: Client subscribes to dashboard updates
3. **Scan Progress**: Real-time updates during security scans
4. **Result Notifications**: Instant notifications when scans complete
5. **Dashboard Refresh**: Automatic UI updates without page reload

**Key Features:**
- **Flask-SocketIO**: WebSocket server for real-time communication
- **Event-Driven Updates**: Scan progress, completion, and error events
- **Multi-Client Support**: Multiple users see updates simultaneously
- **Automatic Reconnection**: Handles connection drops gracefully

**Sequence Diagram:**

```mermaid
sequenceDiagram
    participant UI1 as User 1 Dashboard
    participant UI2 as User 2 Dashboard
    participant WS as WebSocket Server
    participant API as Backend API
    participant Scanner as Security Scanner
    participant DB as Database

    UI1->>WS: Connect & Subscribe
    UI2->>WS: Connect & Subscribe
    WS-->>UI1: Connected
    WS-->>UI2: Connected
    
    API->>Scanner: Trigger Security Scan
    Scanner->>Scanner: Run SAST Scan (Progress: 0%)
    Scanner->>WS: emit('scan_update', {progress: 10%})
    WS->>UI1: Scan Progress Update
    WS->>UI2: Scan Progress Update
    
    Scanner->>Scanner: Run SAST Scan (Progress: 50%)
    Scanner->>WS: emit('scan_update', {progress: 50%})
    WS->>UI1: Scan Progress Update
    WS->>UI2: Scan Progress Update
    
    Scanner->>DB: Save Scan Results
    Scanner->>WS: emit('scan_completed', {results})
    WS->>UI1: Scan Completed Event
    WS->>UI2: Scan Completed Event
    
    UI1->>API: GET /api/cicd/dashboard
    UI2->>API: GET /api/cicd/dashboard
    API->>DB: Query Dashboard Stats
    DB-->>API: Dashboard Data
    API-->>UI1: Updated Dashboard
    API-->>UI2: Updated Dashboard
```

---

## Slide 7: System Architecture & Data Flow

### Title: Microservices Architecture with Security Integration

**Architecture Overview:**
- **Frontend**: React SPA with real-time WebSocket client
- **Backend**: Flask RESTful API with WebSocket server
- **Database**: PostgreSQL with JSONB for flexible data storage
- **Security Tools**: SonarQube, OWASP ZAP, Trivy (containerized)
- **Reverse Proxy**: Nginx routing frontend and API requests

**Data Flow:**
1. User interactions → Frontend → Backend API
2. Backend processes → Database persistence
3. Security scans → External tools → Webhook callbacks
4. Real-time updates → WebSocket → Frontend UI

**Key Design Patterns:**
- **Service Layer**: Business logic separated from API endpoints
- **Pattern Matching**: Reusable threat pattern library
- **Event-Driven**: WebSocket events for real-time updates
- **Webhook Authentication**: API token-based security

**Architecture Diagram:**

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React UI]
        WSClient[WebSocket Client]
    end
    
    subgraph "API Gateway"
        Nginx[Nginx Reverse Proxy]
    end
    
    subgraph "Backend Services"
        API[Flask REST API]
        WSServer[WebSocket Server]
        STRIDE[STRIDE Engine]
        DREAD[DREAD Scorer]
        Detector[Threat Detector]
        Scanner[Security Scanner]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL)]
    end
    
    subgraph "Security Tools"
        SQ[SonarQube]
        ZAP[OWASP ZAP]
        Trivy[Trivy]
    end
    
    subgraph "External"
        GitHub[GitHub Actions]
    end
    
    UI --> Nginx
    WSClient --> WSServer
    Nginx --> API
    Nginx --> UI
    
    API --> STRIDE
    API --> DREAD
    API --> Detector
    API --> Scanner
    API --> DB
    
    Scanner --> SQ
    Scanner --> ZAP
    Scanner --> Trivy
    
    GitHub --> API
    SQ --> API
    ZAP --> API
    Trivy --> API
    
    WSServer --> UI
    Detector --> DB
```

---

## Slide 8: Key Innovations & Value Proposition

### Title: What Makes Project Sentinel Unique

**Key Innovations:**

1. **Intelligent Pattern Recognition**
   - 14 pre-defined threat patterns
   - Regex-based matching with confidence scores
   - Component-aware threat detection
   - Automatic STRIDE category assignment

2. **Automated DREAD Scoring**
   - Pattern-based score suggestions
   - Context-aware adjustments
   - Confidence indicators for each score
   - Manual override capability

3. **Threat-Vulnerability Bridge**
   - Automatic linking of scan findings to threats
   - Distinguishes theoretical vs. confirmed threats
   - Visual correlation matrix
   - Risk prioritization based on real findings

4. **Requirements-Driven Security**
   - Enforced security controls mapping
   - OWASP ASVS compliance tracking
   - Audit-ready exports
   - Compliance dashboard

5. **Real-time Security Visibility**
   - WebSocket-based live updates
   - Scan progress tracking
   - Instant result notifications
   - Multi-user synchronized views

**Value Proposition:**
- **Shift-Left Security**: Identify threats before deployment
- **Automated Risk Assessment**: Reduce manual effort in threat modeling
- **Continuous Security**: Integrated scanning in CI/CD pipeline
- **Compliance Ready**: OWASP ASVS alignment and audit trails
- **Developer-Friendly**: Intuitive UI with real-time feedback

**Impact:**
- Faster threat identification
- Reduced security debt
- Improved compliance posture
- Better risk prioritization
- Enhanced developer security awareness

---
