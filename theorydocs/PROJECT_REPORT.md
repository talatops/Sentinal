# Project Sentinel - Comprehensive Technical Report

## Executive Summary

Project Sentinel is a comprehensive DevSecOps platform that integrates Security-by-Design principles into every stage of the Software Development Lifecycle (SDLC). The platform provides automated threat modeling using STRIDE/DREAD methodologies, security requirements management aligned with OWASP ASVS, and integrated CI/CD security scanning with SAST, DAST, and container scanning capabilities.

---

## 1. Problem Statement

### 1.1 The Challenge

Modern software development faces critical security challenges:

1. **Security as an Afterthought**: Traditional development processes treat security as a bolt-on feature, leading to vulnerabilities discovered late in the development cycle when remediation is costly and time-consuming.

2. **Lack of Integrated Security Tools**: Development teams struggle with fragmented security tools that don't integrate seamlessly into their workflows, creating gaps in security coverage.

3. **Manual Threat Modeling**: Threat modeling is often performed manually, inconsistently, and without proper documentation, making it difficult to track and mitigate security risks systematically.

4. **Disconnected Security Requirements**: Security requirements are often managed separately from functional requirements, leading to misalignment and incomplete security coverage.

5. **Limited CI/CD Security Integration**: Security scanning tools (SAST, DAST, container scanning) operate in isolation, making it difficult to correlate findings and prioritize remediation efforts.

6. **Insufficient Security Visibility**: Development teams lack real-time visibility into security posture, threat trends, and compliance status.

### 1.2 Relevance to Secure Software Design

This problem is directly relevant to secure software design because:

- **Security-by-Design Principle**: Security must be integrated from the requirements phase, not added later. Project Sentinel addresses this by providing threat modeling and security requirements management from the start.

- **Defense in Depth**: The platform implements multiple layers of security controls (authentication, authorization, input validation, security scanning) at different stages of the SDLC.

- **Continuous Security**: Security is not a one-time activity but a continuous process integrated into every stage of development, testing, and deployment.

- **Risk-Based Approach**: The platform enables risk-based prioritization through automated DREAD scoring, helping teams focus on high-risk threats first.

- **Compliance Alignment**: The system aligns with industry standards (OWASP ASVS, GDPR) to ensure compliance and best practices.

### 1.3 Project Objectives

The project objectives are clear, achievable, and measurable:

1. **Automated Threat Modeling**: Provide intelligent STRIDE/DREAD analysis with pattern recognition and automated scoring to reduce manual effort and improve consistency.

2. **Integrated Security Requirements Management**: Enable seamless mapping of security controls to functional requirements with compliance tracking.

3. **CI/CD Security Integration**: Integrate SAST (SonarQube), DAST (OWASP ZAP), and container scanning (Trivy) into CI/CD pipelines with real-time visibility.

4. **Real-Time Security Visibility**: Provide dashboards, analytics, and WebSocket-based real-time updates for security events and scan results.

5. **Developer-Friendly Interface**: Create an intuitive, modern web interface that makes security accessible to developers without requiring deep security expertise.

6. **Scalable Architecture**: Design a microservices-oriented architecture that can scale and integrate with existing development workflows.

---

## 2. Proposed Solution & Architecture

### 2.1 System Overview

Project Sentinel is a full-stack web application consisting of:

- **Frontend**: React-based single-page application providing intuitive UI for threat modeling, requirements management, and CI/CD dashboards
- **Backend**: RESTful API built with Flask providing threat analysis, requirements management, and CI/CD integration services
- **Database**: PostgreSQL database storing users, threats, requirements, and CI/CD run data
- **Security Tools**: Integrated SonarQube (SAST), OWASP ZAP (DAST), and Trivy (container scanning)
- **Infrastructure**: Docker containerization with Nginx reverse proxy for production deployment

### 2.2 High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        GitHub[GitHub Actions]
    end
    
    subgraph "Frontend Layer"
        Nginx[Nginx Reverse Proxy]
        React[React Frontend<br/>Port 80]
    end
    
    subgraph "Backend Layer"
        Flask[Flask API Server<br/>Port 5000]
        WebSocket[WebSocket Server<br/>SocketIO]
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database<br/>Port 5432)]
    end
    
    subgraph "Security Tools"
        SonarQube[SonarQube<br/>SAST - Port 9000]
        ZAP[OWASP ZAP<br/>DAST - Port 8090]
        Trivy[Trivy<br/>Container Scan - Port 8080]
    end
    
    Browser --> Nginx
    GitHub --> Nginx
    Nginx --> React
    Nginx --> Flask
    Flask --> WebSocket
    Flask --> PostgreSQL
    Flask --> SonarQube
    Flask --> ZAP
    Flask --> Trivy
    React --> Flask
    WebSocket --> React
```

### 2.3 Component Architecture

```mermaid
graph LR
    subgraph "Frontend Components"
        Auth[Authentication]
        Threat[Threat Modeling]
        Req[Requirements]
        CICD[CI/CD Dashboard]
        Analytics[Analytics]
    end
    
    subgraph "Backend Services"
        AuthAPI[Auth API]
        ThreatAPI[Threat API]
        ReqAPI[Requirements API]
        CICDAPI[CI/CD API]
        WebSocketAPI[WebSocket API]
    end
    
    subgraph "Core Services"
        Security[Security Utils]
        STRIDE[STRIDE Engine]
        DREAD[DREAD Scorer]
        Scanner[Security Scanner]
    end
    
    subgraph "Data Models"
        User[User Model]
        ThreatModel[Threat Model]
        ReqModel[Requirement Model]
        CICDModel[CI/CD Model]
    end
    
    Auth --> AuthAPI
    Threat --> ThreatAPI
    Req --> ReqAPI
    CICD --> CICDAPI
    
    AuthAPI --> Security
    ThreatAPI --> STRIDE
    ThreatAPI --> DREAD
    CICDAPI --> Scanner
    
    AuthAPI --> User
    ThreatAPI --> ThreatModel
    ReqAPI --> ReqModel
    CICDAPI --> CICDModel
```

### 2.4 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 19, Vite 7 | Modern UI framework with fast build |
| **State Management** | Zustand | Lightweight state management |
| **Styling** | Tailwind CSS | Utility-first CSS framework |
| **Visualization** | ReactFlow, Recharts | Interactive diagrams and charts |
| **Backend** | Flask 3.0, Flask-RESTful | RESTful API framework |
| **Database** | PostgreSQL 15 | Relational database with JSONB support |
| **ORM** | SQLAlchemy | Database abstraction layer |
| **Authentication** | Flask-JWT-Extended | JWT-based authentication |
| **Real-time** | Flask-SocketIO | WebSocket support |
| **Security** | Flask-Talisman, Flask-Limiter | Security headers and rate limiting |
| **Containerization** | Docker, Docker Compose | Container orchestration |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

### 2.5 Database Schema

```mermaid
erDiagram
    User ||--o{ Requirement : creates
    User ||--o{ APIToken : owns
    Threat ||--o{ ThreatVulnerability : has
    Requirement ||--o{ SecurityControl : has
    CICDRun ||--o{ ThreatVulnerability : generates
    
    User {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        string github_id UK
        datetime created_at
        datetime last_login
        boolean is_active
    }
    
    Threat {
        int id PK
        string asset
        text flow
        string trust_boundary
        jsonb stride_categories
        jsonb dread_score
        string risk_level
        text mitigation
        datetime created_at
        datetime updated_at
    }
    
    Requirement {
        int id PK
        string title
        text description
        jsonb security_controls
        int creator_id FK
        datetime created_at
        datetime updated_at
    }
    
    CICDRun {
        int id PK
        string commit_hash
        string branch
        string status
        jsonb sast_results
        jsonb dast_results
        jsonb trivy_results
        int critical_vulnerabilities
        int total_vulnerabilities
        datetime created_at
        datetime completed_at
    }
    
    ThreatVulnerability {
        int id PK
        int threat_id FK
        int cicd_run_id FK
        string vulnerability_type
        string severity
        string status
        text description
        datetime created_at
    }
    
    APIToken {
        int id PK
        int user_id FK
        string token_prefix
        string token_hash
        datetime created_at
        datetime last_used
        boolean is_active
    }
```

---

## 3. Methodology & SDLC Coverage

### 3.1 Development Approach

Project Sentinel follows an **Agile/Iterative development methodology** with Security-by-Design principles integrated at every stage. The development approach emphasizes:

- **Incremental Development**: Features are developed in iterations, allowing for continuous feedback and improvement
- **Test-Driven Development**: Comprehensive test coverage with unit tests, integration tests, and end-to-end tests
- **Continuous Integration**: Automated testing, linting, and security scanning on every commit
- **Documentation-Driven**: Technical documentation, API documentation, and user guides maintained alongside code

### 3.2 Security Activities Integrated at Each SDLC Stage

#### 3.2.1 Requirements Phase

**Security Activities:**

1. **Security Requirements Gathering**
   - System provides structured templates for security requirements
   - OWASP ASVS alignment for compliance tracking
   - One-to-one mapping of security controls to functional requirements

2. **Threat Modeling Initiation**
   - Early threat identification using STRIDE methodology
   - Asset identification and data flow mapping
   - Trust boundary definition

3. **Compliance Requirements**
   - GDPR compliance features (data retention, user rights)
   - OWASP ASVS compliance tracking
   - Security control mapping

**Implementation in Project Sentinel:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant UI as Frontend UI
    participant API as Requirements API
    participant DB as Database
    
    Dev->>UI: Create Security Requirement
    UI->>API: POST /api/requirements
    API->>API: Validate Input (Marshmallow)
    API->>API: Check Authorization (RBAC)
    API->>DB: Store Requirement
    API->>API: Link Security Controls
    DB-->>API: Requirement Created
    API-->>UI: Return Requirement Data
    UI-->>Dev: Display Success
```

**Key Features:**
- `/api/requirements` endpoint for CRUD operations
- Security control validation and mapping
- Compliance dashboard for tracking OWASP ASVS alignment
- Export functionality (CSV/JSON) for audit purposes

#### 3.2.2 Design Phase

**Security Activities:**

1. **Security Architecture Design**
   - Authentication and authorization design (JWT, OAuth)
   - Data encryption and secure storage
   - API security (rate limiting, input validation)

2. **Threat Modeling Refinement**
   - Advanced STRIDE analysis with pattern recognition
   - Automated DREAD scoring for risk assessment
   - Mitigation strategy development

3. **Security Control Design**
   - Input validation schemas
   - Output encoding mechanisms
   - Security headers configuration

**Implementation in Project Sentinel:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant UI as Frontend UI
    participant API as Threat API
    participant STRIDE as STRIDE Engine
    participant DREAD as DREAD Scorer
    participant DB as Database
    
    Dev->>UI: Submit Threat for Analysis
    UI->>API: POST /api/threats/analyze
    API->>API: Validate JWT Token
    API->>STRIDE: Analyze Threat (Pattern Matching)
    STRIDE->>STRIDE: Detect Components
    STRIDE->>STRIDE: Match Threat Patterns
    STRIDE->>STRIDE: Generate STRIDE Categories
    STRIDE-->>API: STRIDE Analysis Results
    API->>DREAD: Calculate DREAD Scores
    DREAD->>DREAD: Pattern-Based Scoring
    DREAD->>DREAD: Risk Level Calculation
    DREAD-->>API: DREAD Scores & Risk Level
    API->>API: Generate Mitigation Recommendations
    API->>DB: Store Threat Analysis
    DB-->>API: Threat Saved
    API-->>UI: Return Complete Analysis
    UI-->>Dev: Display Threat Analysis
```

**Key Features:**
- Advanced pattern recognition with 14 threat patterns
- Component detection (API, database, authentication, etc.)
- Automated DREAD scoring with confidence indicators
- Enhanced mitigation recommendations
- Threat similarity detection for learning

#### 3.2.3 Coding Phase

**Security Activities:**

1. **Secure Coding Practices**
   - Input validation using Marshmallow schemas
   - SQL injection prevention with SQLAlchemy ORM
   - XSS prevention with output encoding
   - Secure password hashing (bcrypt)

2. **Static Analysis (SAST)**
   - SonarQube integration for code quality and security
   - Automated vulnerability detection
   - Code smell identification

3. **Dependency Scanning**
   - Trivy integration for container and dependency scanning
   - Known vulnerability detection
   - License compliance checking

**Implementation in Project Sentinel:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Git as GitHub
    participant CI as CI/CD Pipeline
    participant SonarQube as SonarQube
    participant Trivy as Trivy
    participant API as CI/CD API
    participant DB as Database
    participant WS as WebSocket
    
    Dev->>Git: Push Code
    Git->>CI: Trigger GitHub Actions
    CI->>CI: Run Tests
    CI->>SonarQube: Trigger SAST Scan
    SonarQube->>SonarQube: Analyze Code
    SonarQube-->>CI: SAST Results
    CI->>Trivy: Trigger Container Scan
    Trivy->>Trivy: Scan Dependencies
    Trivy-->>CI: Scan Results
    CI->>API: POST /api/cicd/webhook/sonarqube
    API->>API: Authenticate (API Token)
    API->>DB: Store Scan Results
    API->>WS: Emit Real-Time Update
    WS-->>Dev: Update Dashboard
    API-->>CI: Webhook Acknowledged
```

**Key Features:**
- Automated SAST scanning with SonarQube
- Container and dependency scanning with Trivy
- Webhook integration for GitHub Actions
- Real-time scan result updates via WebSocket
- Vulnerability correlation with threat models

#### 3.2.4 Testing Phase

**Security Activities:**

1. **Security Testing**
   - Dynamic Application Security Testing (DAST) with OWASP ZAP
   - Penetration testing support
   - Vulnerability scanning

2. **Integration Testing**
   - API endpoint testing
   - Authentication and authorization testing
   - Security control validation

3. **Automated Test Suite**
   - Unit tests for security functions
   - Integration tests for API endpoints
   - End-to-end tests for critical flows

**Implementation in Project Sentinel:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant UI as Frontend UI
    participant API as CI/CD API
    participant ZAP as OWASP ZAP
    participant DB as Database
    participant WS as WebSocket
    
    Dev->>UI: Trigger DAST Scan
    UI->>API: POST /api/cicd/scans/zap/trigger
    API->>API: Validate JWT Token
    API->>ZAP: Start ZAP Scan
    ZAP->>ZAP: Perform Security Tests
    ZAP->>ZAP: Identify Vulnerabilities
    ZAP-->>API: DAST Results
    API->>DB: Store Scan Results
    API->>API: Correlate with Threats
    API->>WS: Emit Scan Update
    WS-->>UI: Real-Time Progress
    API-->>UI: Return Scan Results
    UI-->>Dev: Display Vulnerabilities
```

**Key Features:**
- OWASP ZAP integration for DAST scanning
- Automated vulnerability detection
- Real-time scan progress updates
- Vulnerability correlation with threat models
- Comprehensive test coverage (pytest, Jest)

### 3.3 Security Activities Summary by SDLC Stage

| SDLC Stage | Security Activities | Project Sentinel Features |
|------------|---------------------|--------------------------|
| **Requirements** | Security requirements gathering, Threat modeling initiation, Compliance tracking | Requirements API, OWASP ASVS alignment, Threat templates |
| **Design** | Security architecture, Threat modeling refinement, Security control design | STRIDE/DREAD analysis, Pattern recognition, Mitigation recommendations |
| **Coding** | Secure coding practices, SAST, Dependency scanning | SonarQube integration, Trivy scanning, Input validation |
| **Testing** | DAST, Security testing, Vulnerability scanning | OWASP ZAP integration, Automated test suite, Vulnerability correlation |
| **Deployment** | Security scanning in CI/CD, Real-time monitoring | Webhook integration, Real-time dashboards, Security event logging |
| **Maintenance** | Continuous monitoring, Threat updates, Compliance auditing | Analytics dashboard, Threat similarity, Compliance reports |

---

## 4. Data Flow Diagrams

### 4.1 Authentication Flow

```mermaid
flowchart TD
    Start([User Access]) --> Auth{Authenticated?}
    Auth -->|No| Login[Login Page]
    Auth -->|Yes| CheckToken{Token Valid?}
    
    Login --> Input[Enter Credentials]
    Input --> Validate[Validate Input]
    Validate -->|Invalid| Error[Show Error]
    Validate -->|Valid| CheckUser{User Exists?}
    
    CheckUser -->|No| Error
    CheckUser -->|Yes| VerifyPass[Verify Password]
    VerifyPass -->|Invalid| Error
    VerifyPass -->|Valid| GenerateToken[Generate JWT Tokens]
    
    GenerateToken --> StoreToken[Store Tokens]
    StoreToken --> LogEvent[Log Security Event]
    LogEvent --> Dashboard[Dashboard Access]
    
    CheckToken -->|Expired| Refresh{Refresh Token Valid?}
    Refresh -->|Yes| NewToken[Generate New Access Token]
    Refresh -->|No| Login
    NewToken --> Dashboard
    
    CheckToken -->|Valid| Dashboard
    Dashboard --> End([Access Granted])
    Error --> Login
```

### 4.2 Threat Analysis Data Flow

```mermaid
flowchart TD
    Start([User Submits Threat]) --> Input[Input: Asset, Flow, Trust Boundary]
    Input --> Validate[Validate Input Schema]
    Validate -->|Invalid| Error[Return Validation Errors]
    Validate -->|Valid| Auth[Check JWT Authentication]
    
    Auth -->|Unauthorized| Error
    Auth -->|Authorized| STRIDE[STRIDE Engine Analysis]
    
    STRIDE --> DetectComp[Detect Component Types]
    DetectComp --> MatchPattern[Match Threat Patterns]
    MatchPattern --> GenSTRIDE[Generate STRIDE Categories]
    GenSTRIDE --> CalcConf[Calculate Confidence Scores]
    
    CalcConf --> DREAD{DREAD Mode?}
    DREAD -->|Auto| AutoScore[Automated DREAD Scoring]
    DREAD -->|Manual| ManualScore[User-Provided Scores]
    
    AutoScore --> PatternScore[Pattern-Based Scoring]
    PatternScore --> ContextAdj[Context Adjustments]
    ContextAdj --> DREADScores[DREAD Scores]
    
    ManualScore --> ValidateScores[Validate Scores 0-10]
    ValidateScores -->|Invalid| Error
    ValidateScores -->|Valid| DREADScores
    
    DREADScores --> CalcRisk[Calculate Risk Level]
    CalcRisk --> GenMit[Generate Mitigations]
    GenMit --> Enhanced{Enhanced Mitigations?}
    
    Enhanced -->|Yes| EnhancedMit[Enhanced Mitigation Engine]
    Enhanced -->|No| BasicMit[Basic Mitigations]
    
    EnhancedMit --> Store[Store Threat in Database]
    BasicMit --> Store
    
    Store --> Response[Return Analysis Results]
    Response --> End([Threat Analysis Complete])
    Error --> End
```

### 4.3 CI/CD Security Scanning Data Flow

```mermaid
flowchart TD
    Start([Code Push/Manual Trigger]) --> Trigger[Trigger CI/CD Pipeline]
    Trigger --> CreateRun[Create CI/CD Run Record]
    CreateRun --> InitStatus[Set Status: Running]
    
    InitStatus --> Parallel{Parallel Scans}
    
    Parallel --> SAST[SAST: SonarQube]
    Parallel --> DAST[DAST: OWASP ZAP]
    Parallel --> Container[Container: Trivy]
    
    SAST --> SASTScan[Analyze Source Code]
    SASTScan --> SASTResults[SAST Results]
    
    DAST --> DASTScan[Test Running Application]
    DASTScan --> DASTResults[DAST Results]
    
    Container --> TrivyScan[Scan Dependencies/Images]
    TrivyScan --> TrivyResults[Trivy Results]
    
    SASTResults --> Aggregate[Aggregate Results]
    DASTResults --> Aggregate
    TrivyResults --> Aggregate
    
    Aggregate --> CountVuln[Count Vulnerabilities]
    CountVuln --> Critical{Critical Vulns?}
    
    Critical -->|Yes| Blocked[Status: Blocked]
    Critical -->|No| Success[Status: Success]
    
    Blocked --> StoreResults[Store All Results in DB]
    Success --> StoreResults
    
    StoreResults --> WebSocket[Emit WebSocket Update]
    WebSocket --> Dashboard[Update Dashboard]
    Dashboard --> Correlate[Correlate with Threats]
    Correlate --> End([Scan Complete])
```

### 4.4 Requirements Management Data Flow

```mermaid
flowchart TD
    Start([User Creates Requirement]) --> Input[Input: Title, Description]
    Input --> Validate[Validate Input Schema]
    Validate -->|Invalid| Error[Return Validation Errors]
    Validate -->|Valid| Auth[Check JWT Authentication]
    
    Auth -->|Unauthorized| Error
    Auth -->|Authorized| CheckRole{User Role?}
    
    CheckRole -->|Admin| FullAccess[Full Access]
    CheckRole -->|Developer| LimitedAccess[Limited Access]
    
    FullAccess --> CreateReq[Create Requirement]
    LimitedAccess --> CreateReq
    
    CreateReq --> AddControls[Add Security Controls]
    AddControls --> ValidateControls[Validate Controls]
    ValidateControls -->|Invalid| Error
    ValidateControls -->|Valid| MapASVS[Map to OWASP ASVS]
    
    MapASVS --> Store[Store in Database]
    Store --> LinkThreats{Link to Threats?}
    
    LinkThreats -->|Yes| FindThreats[Find Related Threats]
    FindThreats --> CreateLink[Create Threat-Requirement Links]
    LinkThreats -->|No| Response
    
    CreateLink --> Response[Return Requirement Data]
    Response --> UpdateCompliance[Update Compliance Dashboard]
    UpdateCompliance --> End([Requirement Created])
    Error --> End
```

---

## 5. Sequence Diagrams for Normal Flows

### 5.1 User Registration and Login Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthAPI
    participant Security
    participant Database
    participant Logger
    
    User->>Frontend: Enter Registration Details
    Frontend->>AuthAPI: POST /api/auth/register
    AuthAPI->>AuthAPI: Validate Schema (Marshmallow)
    AuthAPI->>Database: Check Username Exists
    Database-->>AuthAPI: User Not Found
    AuthAPI->>Database: Check Email Exists
    Database-->>AuthAPI: Email Not Found
    AuthAPI->>Security: Hash Password (bcrypt)
    Security-->>AuthAPI: Password Hash
    AuthAPI->>Database: Create User Record
    Database-->>AuthAPI: User Created
    AuthAPI->>Logger: Log Security Event
    AuthAPI-->>Frontend: Registration Success
    Frontend-->>User: Show Success Message
    
    User->>Frontend: Enter Login Credentials
    Frontend->>AuthAPI: POST /api/auth/login
    AuthAPI->>AuthAPI: Validate Schema
    AuthAPI->>Database: Find User by Username
    Database-->>AuthAPI: User Found
    AuthAPI->>Security: Verify Password
    Security-->>AuthAPI: Password Valid
    AuthAPI->>AuthAPI: Generate Access Token (JWT)
    AuthAPI->>AuthAPI: Generate Refresh Token (JWT)
    AuthAPI->>Database: Update Last Login
    AuthAPI->>Logger: Log Login Success
    AuthAPI-->>Frontend: Return Tokens + User Data
    Frontend->>Frontend: Store Tokens (LocalStorage)
    Frontend-->>User: Redirect to Dashboard
```

### 5.2 GitHub OAuth Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AuthAPI
    participant GitHub
    participant Database
    participant Logger
    
    User->>Frontend: Click "Login with GitHub"
    Frontend->>GitHub: Redirect to GitHub OAuth
    GitHub->>User: Show Authorization Page
    User->>GitHub: Authorize Application
    GitHub->>Frontend: Redirect with Authorization Code
    Frontend->>AuthAPI: GET /api/auth/github/callback?code=XXX
    AuthAPI->>GitHub: Exchange Code for Access Token
    GitHub-->>AuthAPI: Access Token
    AuthAPI->>GitHub: Get User Info (API)
    GitHub-->>AuthAPI: User Info (username, email, id)
    AuthAPI->>GitHub: Get User Emails (API)
    GitHub-->>AuthAPI: Email List
    AuthAPI->>Database: Check User by GitHub ID
    Database-->>AuthAPI: User Not Found
    AuthAPI->>Database: Check Email Exists
    Database-->>AuthAPI: Email Not Found
    AuthAPI->>Database: Create User (GitHub OAuth)
    Database-->>AuthAPI: User Created
    AuthAPI->>AuthAPI: Generate JWT Tokens
    AuthAPI->>Logger: Log GitHub OAuth Success
    AuthAPI-->>Frontend: Return Tokens + User Data
    Frontend->>Frontend: Store Tokens
    Frontend-->>User: Redirect to Dashboard
```

### 5.3 Threat Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant ThreatAPI
    participant STRIDEEngine
    participant DREADScorer
    participant Database
    participant WebSocket
    
    User->>Frontend: Submit Threat Analysis Request
    Frontend->>Frontend: Validate Form Input
    Frontend->>ThreatAPI: POST /api/threats/analyze<br/>{asset, flow, trust_boundary, auto_score}
    ThreatAPI->>ThreatAPI: Validate JWT Token
    ThreatAPI->>ThreatAPI: Validate Request Schema
    ThreatAPI->>STRIDEEngine: analyze_threat_advanced()
    
    STRIDEEngine->>STRIDEEngine: Detect Component Types
    STRIDEEngine->>STRIDEEngine: Match Threat Patterns
    STRIDEEngine->>STRIDEEngine: Generate STRIDE Categories
    STRIDEEngine->>STRIDEEngine: Calculate Confidence Scores
    STRIDEEngine-->>ThreatAPI: STRIDE Analysis Results
    
    alt Auto-Score Mode
        ThreatAPI->>DREADScorer: suggest_dread_scores()
        DREADScorer->>DREADScorer: Pattern-Based Scoring
        DREADScorer->>DREADScorer: Context Adjustments
        DREADScorer-->>ThreatAPI: Suggested DREAD Scores
    else Manual Score Mode
        ThreatAPI->>ThreatAPI: Use User-Provided Scores
    end
    
    ThreatAPI->>ThreatAPI: Calculate Total DREAD Score
    ThreatAPI->>ThreatAPI: Determine Risk Level
    ThreatAPI->>ThreatAPI: Generate Mitigation Recommendations
    ThreatAPI->>Database: Store Threat Analysis
    Database-->>ThreatAPI: Threat Saved
    ThreatAPI->>WebSocket: Emit Threat Created Event
    ThreatAPI-->>Frontend: Return Complete Analysis
    Frontend->>Frontend: Update UI with Results
    Frontend-->>User: Display Threat Analysis
```

### 5.4 CI/CD Webhook Flow

```mermaid
sequenceDiagram
    participant GitHub
    participant CI as CI/CD Pipeline
    participant SonarQube
    participant WebhookAPI
    participant Database
    participant WebSocket
    participant Frontend
    
    GitHub->>CI: Code Push Event
    CI->>CI: Run Tests
    CI->>SonarQube: Trigger SAST Scan
    SonarQube->>SonarQube: Analyze Code
    SonarQube-->>CI: SAST Results (JSON)
    CI->>WebhookAPI: POST /api/cicd/webhook/sonarqube<br/>{scan_type, results, commit_hash}
    
    WebhookAPI->>WebhookAPI: Authenticate API Token
    WebhookAPI->>WebhookAPI: Validate Webhook Signature
    WebhookAPI->>Database: Find or Create CI/CD Run
    WebhookAPI->>Database: Update Run with SAST Results
    WebhookAPI->>Database: Count Vulnerabilities
    WebhookAPI->>Database: Update Run Status
    Database-->>WebhookAPI: Run Updated
    WebhookAPI->>WebSocket: Emit Scan Update Event
    WebSocket-->>Frontend: Real-Time Update
    Frontend->>Frontend: Update Dashboard
    WebhookAPI-->>CI: Webhook Acknowledged (200 OK)
```

### 5.5 Requirements Creation and Compliance Tracking

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant ReqAPI
    participant Database
    participant Compliance
    
    User->>Frontend: Create Security Requirement
    Frontend->>ReqAPI: POST /api/requirements<br/>{title, description, controls}
    ReqAPI->>ReqAPI: Validate JWT Token
    ReqAPI->>ReqAPI: Validate Request Schema
    ReqAPI->>ReqAPI: Check User Permissions
    ReqAPI->>Database: Create Requirement Record
    Database-->>ReqAPI: Requirement Created
    ReqAPI->>Database: Link Security Controls
    Database-->>ReqAPI: Controls Linked
    ReqAPI->>Compliance: Map to OWASP ASVS
    Compliance->>Compliance: Update Compliance Metrics
    Compliance-->>ReqAPI: Compliance Updated
    ReqAPI->>Database: Store Compliance Data
    ReqAPI-->>Frontend: Return Requirement + Compliance
    Frontend->>Frontend: Update Compliance Dashboard
    Frontend-->>User: Show Requirement Created
```

---

## 6. Security Features Implementation

### 6.1 Authentication & Authorization

**JWT-Based Authentication:**
- Access tokens (30-minute expiry)
- Refresh tokens (7-day expiry)
- Secure token storage
- Token refresh mechanism

**Role-Based Access Control (RBAC):**
- Admin role: Full access to all features
- Developer role: Limited access to threat modeling and requirements

**GitHub OAuth Integration:**
- Secure OAuth 2.0 flow
- User account linking
- Automatic user creation

### 6.2 Input Validation & Sanitization

**Backend (Marshmallow):**
- Schema-based validation
- Type checking
- Length validation
- Email validation
- Custom validators

**Frontend (Zod):**
- Client-side validation
- Form validation
- Type safety

**XSS Prevention:**
- Output encoding
- Content Security Policy (CSP)
- Input sanitization

### 6.3 Security Headers

**Flask-Talisman Configuration:**
- Strict Transport Security (HSTS)
- Content Security Policy
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection

### 6.4 Rate Limiting

**Flask-Limiter:**
- Registration: 5 requests per minute
- Login: 10 requests per minute
- API endpoints: Configurable limits
- IP-based rate limiting

### 6.5 Password Security

**bcrypt Hashing:**
- Secure password hashing
- Salt generation
- Cost factor configuration

### 6.6 API Token Management

**Secure API Tokens:**
- Token prefix storage (first 8 characters)
- Hashed token storage
- Token revocation
- Last used tracking
- Admin-only management

### 6.7 Security Event Logging

**Audit Trail:**
- User registration events
- Login success/failure events
- Security-sensitive operations
- IP address tracking
- Timestamp logging

---

## 7. Integration Points

### 7.1 SonarQube Integration (SAST)

- **Purpose**: Static Application Security Testing
- **Integration Method**: REST API
- **Features**:
  - Automated code analysis
  - Vulnerability detection
  - Code quality metrics
  - Security hotspot identification

### 7.2 OWASP ZAP Integration (DAST)

- **Purpose**: Dynamic Application Security Testing
- **Integration Method**: REST API
- **Features**:
  - Automated security testing
  - Vulnerability scanning
  - Active and passive scanning
  - Report generation

### 7.3 Trivy Integration (Container Scanning)

- **Purpose**: Container and dependency vulnerability scanning
- **Integration Method**: REST API
- **Features**:
  - Container image scanning
  - Dependency vulnerability detection
  - License compliance
  - CVE tracking

### 7.4 GitHub Actions Integration

- **Purpose**: CI/CD pipeline integration
- **Integration Method**: Webhooks
- **Features**:
  - Automated scan triggering
  - Real-time result updates
  - Commit hash tracking
  - Branch-based scanning

---

## 8. Compliance & Standards Alignment

### 8.1 OWASP ASVS Alignment

- Security requirements mapped to OWASP ASVS levels
- Compliance dashboard for tracking
- Security control validation
- Audit trail for compliance

### 8.2 GDPR Compliance

- Data retention policies
- User data access rights
- Data minimization principles
- Secure data storage
- Audit logging

### 8.3 Security Best Practices

- Defense in depth
- Least privilege
- Fail securely
- Secure by default
- Complete mediation

---

## 9. Testing Strategy

### 9.1 Backend Testing

- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication, authorization, input validation
- **Coverage**: Comprehensive test coverage with pytest

### 9.2 Frontend Testing

- **Component Tests**: React component testing
- **Integration Tests**: User flow testing
- **E2E Tests**: Critical path testing

### 9.3 CI/CD Testing

- Automated test execution on every commit
- Linting and code quality checks
- Security scanning integration
- Test coverage reporting

---

## 10. Deployment Architecture

### 10.1 Containerization

- **Docker**: Application containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and load balancing
- **PostgreSQL**: Database container

### 10.2 Production Considerations

- Environment variable configuration
- Secret management
- HTTPS enforcement
- Database backups
- Monitoring and logging

---

## 11. Future Enhancements

1. **Advanced Analytics**: Machine learning for threat prediction
2. **Multi-Tenancy**: Support for multiple organizations
3. **API Rate Limiting**: Advanced rate limiting strategies
4. **Threat Intelligence**: Integration with threat intelligence feeds
5. **Compliance Automation**: Automated compliance reporting
6. **Advanced Visualization**: Enhanced threat modeling diagrams

---

## 12. Conclusion

Project Sentinel successfully addresses the critical need for Security-by-Design in modern software development. By integrating security activities at every stage of the SDLC, the platform provides:

- **Automated Threat Modeling**: Reducing manual effort and improving consistency
- **Integrated Security Requirements**: Ensuring security controls are properly mapped and tracked
- **CI/CD Security Integration**: Providing real-time visibility into security posture
- **Developer-Friendly Interface**: Making security accessible to all team members
- **Compliance Alignment**: Supporting industry standards and regulations

The architecture is scalable, maintainable, and follows security best practices. The comprehensive test coverage and CI/CD integration ensure code quality and security throughout the development lifecycle.

---

## Appendix A: API Endpoints Summary

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/github` - GitHub OAuth initiation
- `GET /api/auth/github/callback` - GitHub OAuth callback
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/profile` - User profile

### Threat Modeling Endpoints
- `POST /api/threats/analyze` - Analyze threat
- `GET /api/threats` - List threats
- `GET /api/threats/{id}` - Get threat details
- `GET /api/threats/analytics` - Threat analytics
- `GET /api/threats/{id}/similar` - Find similar threats

### Requirements Endpoints
- `GET /api/requirements` - List requirements
- `POST /api/requirements` - Create requirement
- `GET /api/requirements/{id}` - Get requirement details
- `GET /api/requirements/compliance` - Compliance dashboard

### CI/CD Endpoints
- `GET /api/cicd/runs` - List CI/CD runs
- `POST /api/cicd/trigger` - Trigger CI/CD run
- `GET /api/cicd/dashboard` - Dashboard statistics
- `POST /api/cicd/webhook/{scan_type}` - Webhook endpoint

---

## Appendix B: Key Configuration Files

- `.docker.env.example` - Environment variable template
- `docker-compose.yml` - Container orchestration
- `backend/.flake8` - Python linting configuration
- `backend/pytest.ini` - Test configuration
- `.github/workflows/ci-cd.yml` - CI/CD pipeline configuration

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: Project Sentinel Development Team
