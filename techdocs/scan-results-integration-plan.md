# Security Scan Results Integration Plan

## Current State Analysis

### ✅ What We Have:
1. **Backend Infrastructure:**
   - `SecurityScanner` service class (placeholder implementations)
   - CI/CD API endpoints (`/api/cicd/*`)
   - Database model `CICDRun` with JSONB fields for scan results
   - Docker containers running: SonarQube, ZAP, Trivy

2. **Frontend Infrastructure:**
   - Basic Dashboard component
   - CI/CD service for API calls
   - Routing setup

### ❌ What's Missing:
1. **Real API Integrations:**
   - SonarQube API calls (currently returns mock data)
   - OWASP ZAP API calls (currently returns mock data)
   - Trivy API calls (currently returns mock data)

2. **Detailed Results Display:**
   - No dedicated pages for SonarQube results
   - No dedicated pages for ZAP results
   - No dedicated pages for Trivy results
   - Dashboard only shows summary stats

3. **Real-time Updates:**
   - No WebSocket or polling mechanism
   - No live scan progress updates

---

## Implementation Plan

### Phase 1: Real API Integration (Backend)

#### 1.1 SonarQube Integration
**File:** `backend/app/services/security_scanner.py`

**Tasks:**
- [ ] Implement `run_sast_scan()` to call SonarQube API
- [ ] Use SonarQube REST API endpoints:
  - `/api/projects/search` - List projects
  - `/api/issues/search` - Get issues/vulnerabilities
  - `/api/measures/component` - Get metrics (coverage, code smells)
- [ ] Parse and structure results:
  ```python
  {
    'status': 'completed',
    'project_key': 'sentinal',
    'critical': 5,
    'high': 12,
    'medium': 23,
    'low': 8,
    'total': 48,
    'issues': [
      {
        'key': 'issue-key',
        'severity': 'CRITICAL',
        'component': 'file.py',
        'line': 42,
        'message': 'SQL injection vulnerability',
        'rule': 'python:S3649',
        'type': 'VULNERABILITY'
      }
    ],
    'metrics': {
      'coverage': 85.5,
      'code_smells': 23,
      'bugs': 5,
      'vulnerabilities': 48
    }
  }
  ```

#### 1.2 OWASP ZAP Integration
**File:** `backend/app/services/security_scanner.py`

**Tasks:**
- [ ] Implement `run_dast_scan()` to call ZAP API
- [ ] Use ZAP REST API endpoints:
  - `/JSON/spider/action/scan` - Start spider scan
  - `/JSON/ascan/action/scan` - Start active scan
  - `/JSON/core/view/alerts` - Get alerts/vulnerabilities
  - `/JSON/core/view/alertsSummary` - Get summary
- [ ] Implement scan status polling
- [ ] Parse and structure results:
  ```python
  {
    'status': 'completed',
    'target': 'http://localhost',
    'scan_id': 'spider-123',
    'critical': 3,
    'high': 7,
    'medium': 15,
    'low': 12,
    'informational': 5,
    'total': 42,
    'alerts': [
      {
        'id': 'alert-id',
        'name': 'SQL Injection',
        'risk': 'High',
        'confidence': 'Medium',
        'url': 'http://localhost/api/users',
        'param': 'id',
        'attack': "1' OR '1'='1",
        'description': 'SQL injection vulnerability detected',
        'solution': 'Use parameterized queries'
      }
    ],
    'scan_duration': 120  # seconds
  }
  ```

#### 1.3 Trivy Integration
**File:** `backend/app/services/security_scanner.py`

**Tasks:**
- [ ] Implement `run_trivy_scan()` to call Trivy API
- [ ] Use Trivy REST API endpoints:
  - `POST /v1/scan` - Scan container image
  - `GET /v1/scan/{scan_id}` - Get scan results
- [ ] Parse and structure results:
  ```python
  {
    'status': 'completed',
    'image': 'sentinal-backend:latest',
    'scan_id': 'scan-123',
    'critical': 2,
    'high': 8,
    'medium': 15,
    'low': 5,
    'total': 30,
    'vulnerabilities': [
      {
        'vulnerability_id': 'CVE-2024-1234',
        'package': 'openssl',
        'installed_version': '1.1.1',
        'fixed_version': '1.1.2',
        'severity': 'CRITICAL',
        'title': 'OpenSSL vulnerability',
        'description': 'Buffer overflow in OpenSSL',
        'published_date': '2024-01-01',
        'cvss_score': 9.8
      }
    ],
    'os_packages': 150,
    'language_packages': 45
  }
  ```

#### 1.4 Enhanced API Endpoints
**File:** `backend/app/api/cicd.py`

**New Endpoints:**
- [ ] `GET /api/cicd/runs/{run_id}/sast` - Get SonarQube results
- [ ] `GET /api/cicd/runs/{run_id}/dast` - Get ZAP results
- [ ] `GET /api/cicd/runs/{run_id}/trivy` - Get Trivy results
- [ ] `GET /api/cicd/scans/sonarqube/latest` - Get latest SonarQube scan
- [ ] `GET /api/cicd/scans/zap/latest` - Get latest ZAP scan
- [ ] `GET /api/cicd/scans/trivy/latest` - Get latest Trivy scan
- [ ] `POST /api/cicd/scans/sonarqube/trigger` - Trigger SonarQube scan
- [ ] `POST /api/cicd/scans/zap/trigger` - Trigger ZAP scan
- [ ] `POST /api/cicd/scans/trivy/trigger` - Trigger Trivy scan

---

### Phase 2: Frontend Pages & Components

#### 2.1 SonarQube Results Page
**File:** `frontend/src/pages/SonarQubeResults.jsx`

**Features:**
- [ ] Overview cards: Total issues, Critical, High, Medium, Low
- [ ] Code coverage visualization (gauge chart)
- [ ] Issues table with filters:
  - Filter by severity
  - Filter by file/component
  - Filter by rule type
  - Search functionality
- [ ] Issue details modal:
  - File path and line number
  - Issue description
  - Rule information
  - Remediation suggestions
- [ ] Metrics visualization:
  - Code smells trend
  - Coverage trend
  - Technical debt
- [ ] Export functionality (PDF, CSV)

#### 2.2 OWASP ZAP Results Page
**File:** `frontend/src/pages/ZAPResults.jsx`

**Features:**
- [ ] Overview cards: Total alerts, Critical, High, Medium, Low
- [ ] Alert severity distribution (pie chart)
- [ ] Alerts table with filters:
  - Filter by risk level
  - Filter by alert name
  - Filter by URL
  - Search functionality
- [ ] Alert details modal:
  - Full URL and parameters
  - Attack vector
  - Description and solution
  - Evidence/response
- [ ] Scan timeline visualization
- [ ] Affected endpoints list
- [ ] Export functionality (HTML report, JSON)

#### 2.3 Trivy Results Page
**File:** `frontend/src/pages/TrivyResults.jsx`

**Features:**
- [ ] Overview cards: Total vulnerabilities, Critical, High, Medium, Low
- [ ] Vulnerability distribution (bar chart)
- [ ] Vulnerabilities table with filters:
  - Filter by severity
  - Filter by package
  - Filter by CVE ID
  - Search functionality
- [ ] Vulnerability details modal:
  - CVE information
  - Package details
  - Installed vs fixed version
  - CVSS score and vector
  - Description and references
- [ ] Package dependency tree visualization
- [ ] Export functionality (JSON, SARIF)

#### 2.4 Enhanced Dashboard
**File:** `frontend/src/pages/Dashboard.jsx`

**Enhancements:**
- [ ] Add scan results summary cards:
  - SonarQube: Latest scan status, critical issues count
  - ZAP: Latest scan status, high-risk alerts count
  - Trivy: Latest scan status, critical CVEs count
- [ ] Quick links to detailed results pages
- [ ] Recent vulnerabilities feed
- [ ] Scan status indicators (running, completed, failed)
- [ ] Combined vulnerability trend chart

#### 2.5 Scan Details Component
**File:** `frontend/src/components/ScanDetails.jsx`

**Reusable component for:**
- [ ] Displaying scan metadata (start time, duration, status)
- [ ] Progress indicators for running scans
- [ ] Scan configuration display
- [ ] Action buttons (retry, cancel, export)

---

### Phase 3: Real-time Updates

#### 3.1 Backend WebSocket Support
**File:** `backend/app/api/websocket.py` (new)

**Tasks:**
- [ ] Implement WebSocket endpoint using Flask-SocketIO
- [ ] Broadcast scan progress updates
- [ ] Broadcast scan completion events
- [ ] Room-based updates (per scan ID)

#### 3.2 Frontend WebSocket Client
**File:** `frontend/src/services/websocket.js` (new)

**Tasks:**
- [ ] Connect to WebSocket endpoint
- [ ] Subscribe to scan updates
- [ ] Update UI in real-time
- [ ] Handle reconnection logic

#### 3.3 Polling Fallback
**File:** `frontend/src/hooks/useScanPolling.js` (new)

**Tasks:**
- [ ] Poll scan status every 5 seconds for running scans
- [ ] Stop polling when scan completes
- [ ] Handle errors gracefully

---

### Phase 4: Enhanced Features

#### 4.1 Filtering & Search
- [ ] Advanced filters for all result pages
- [ ] Save filter presets
- [ ] Export filtered results

#### 4.2 Comparison & Trends
- [ ] Compare scans over time
- [ ] Vulnerability trend analysis
- [ ] Regression detection

#### 4.3 Notifications
- [ ] Email notifications for critical findings
- [ ] Slack/Teams integration
- [ ] In-app notifications

#### 4.4 Remediation Tracking
- [ ] Mark issues as "In Progress"
- [ ] Mark issues as "Resolved"
- [ ] Add remediation notes
- [ ] Track fix verification

---

## Implementation Priority

### High Priority (MVP):
1. ✅ Real API integrations (SonarQube, ZAP, Trivy)
2. ✅ Basic results pages for each scanner
3. ✅ Enhanced dashboard with scan summaries
4. ✅ Polling for real-time updates

### Medium Priority:
5. ⚠️ WebSocket support for live updates
6. ⚠️ Advanced filtering and search
7. ⚠️ Export functionality

### Low Priority (Future):
8. 📋 Comparison and trend analysis
9. 📋 Notifications integration
10. 📋 Remediation tracking

---

## Technical Stack

### Backend:
- Flask-RESTful for API endpoints
- Requests library for HTTP calls
- Flask-SocketIO for WebSocket support (optional)
- Background tasks (Celery or threading)

### Frontend:
- React components with Framer Motion animations
- Recharts for data visualization
- React Query for data fetching and caching
- Socket.io-client for WebSocket (optional)
- React Router for navigation

---

## API Endpoints Summary

```
GET  /api/cicd/runs                    - List all CI/CD runs
GET  /api/cicd/runs/{id}               - Get run details
GET  /api/cicd/runs/{id}/sast          - Get SonarQube results
GET  /api/cicd/runs/{id}/dast          - Get ZAP results
GET  /api/cicd/runs/{id}/trivy         - Get Trivy results
POST /api/cicd/trigger                 - Trigger new scan
GET  /api/cicd/scans/sonarqube/latest  - Latest SonarQube scan
GET  /api/cicd/scans/zap/latest        - Latest ZAP scan
GET  /api/cicd/scans/trivy/latest      - Latest Trivy scan
POST /api/cicd/scans/sonarqube/trigger - Trigger SonarQube scan
POST /api/cicd/scans/zap/trigger       - Trigger ZAP scan
POST /api/cicd/scans/trivy/trigger     - Trigger Trivy scan
WS   /ws/scan/{scan_id}                - WebSocket for scan updates
```

---

## Database Schema Updates

No changes needed - existing `CICDRun` model with JSONB fields is sufficient.

---

## Testing Strategy

1. **Unit Tests:**
   - Test API integration functions
   - Test result parsing logic
   - Test error handling

2. **Integration Tests:**
   - Test full scan workflow
   - Test API endpoint responses
   - Test database storage

3. **E2E Tests:**
   - Test scan triggering from UI
   - Test results display
   - Test real-time updates

---

## Estimated Timeline

- **Phase 1 (Backend API Integration):** 2-3 days
- **Phase 2 (Frontend Pages):** 3-4 days
- **Phase 3 (Real-time Updates):** 1-2 days
- **Phase 4 (Enhanced Features):** 2-3 days

**Total: 8-12 days for full implementation**

---

## Notes

- Start with SonarQube integration as it's the most straightforward
- ZAP scans can take 5-15 minutes, implement proper async handling
- Trivy scans are fast (seconds), can be synchronous
- Consider rate limiting for API calls
- Cache results to reduce API calls
- Implement proper error handling and retry logic

