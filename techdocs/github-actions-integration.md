# GitHub Actions CI/CD Integration with Dashboard

## Current State

### What Happens Now:
1. **Developer pushes code** → GitHub Actions triggers
2. **GitHub Actions runs scans:**
   - SonarQube scan runs → Results go to SonarQube server only
   - Trivy scan runs → Results uploaded to GitHub Security tab only
   - ZAP scan runs → Results stored in GitHub Actions logs only
3. **Dashboard:** Shows nothing (no connection)

### The Problem:
- GitHub Actions scans run independently
- Results are NOT sent to Project Sentinel dashboard
- Dashboard only shows results from manual triggers via backend API
- Two separate systems that don't communicate

---

## How It Should Work

### Option 1: GitHub Actions → Backend API (Recommended)

**Flow:**
```
1. Developer pushes code
   ↓
2. GitHub Actions triggers CI/CD pipeline
   ↓
3. Each scan job completes:
   - SonarQube scan → Parse results → POST to /api/cicd/webhook/sonarqube
   - Trivy scan → Parse results → POST to /api/cicd/webhook/trivy
   - ZAP scan → Parse results → POST to /api/cicd/webhook/zap
   ↓
4. Backend stores results in database
   ↓
5. Dashboard automatically shows new results
```

**Implementation Steps:**

1. **Create Webhook Endpoints in Backend:**
   ```python
   # backend/app/api/cicd.py
   
   class CICDWebhook(Resource):
       """Webhook endpoint for CI/CD results."""
       
       def post(self, scan_type):  # scan_type: sonarqube, trivy, zap
           """Receive scan results from GitHub Actions."""
           data = request.json
           commit_hash = data.get('commit_hash')
           branch = data.get('branch', 'main')
           results = data.get('results')
           
           # Create or update CI/CD run
           run = CICDRun.query.filter_by(
               commit_hash=commit_hash,
               branch=branch
           ).first()
           
           if not run:
               run = CICDRun(
                   commit_hash=commit_hash,
                   branch=branch,
                   status='Running'
               )
               db.session.add(run)
           
           # Store results based on scan type
           if scan_type == 'sonarqube':
               run.sast_results = results
           elif scan_type == 'trivy':
               run.trivy_results = results
           elif scan_type == 'zap':
               run.dast_results = results
           
           db.session.commit()
           return {'status': 'success'}, 200
   ```

2. **Update GitHub Actions Workflow:**
   ```yaml
   # .github/workflows/ci-cd.yml
   
   sast:
     name: SAST Scan (SonarQube)
     runs-on: ubuntu-latest
     needs: [build]
     steps:
       - uses: actions/checkout@v4
       
       - name: SonarQube Scan
         uses: sonarsource/sonarqube-scan-action@master
         env:
           SONAR_TOKEN: ${{ secrets.SONARQUBE_TOKEN }}
           SONAR_HOST_URL: ${{ secrets.SONARQUBE_URL }}
         continue-on-error: true
       
       - name: Get SonarQube Results
         id: sonarqube-results
         run: |
           # Fetch results from SonarQube API
           RESULTS=$(curl -s -u ${{ secrets.SONARQUBE_TOKEN }}: \
             "${{ secrets.SONARQUBE_URL }}/api/issues/search?componentKeys=sentinal" | jq '.')
           echo "results<<EOF" >> $GITHUB_OUTPUT
           echo "$RESULTS" >> $GITHUB_OUTPUT
           echo "EOF" >> $GITHUB_OUTPUT
       
       - name: Send Results to Dashboard
         run: |
           curl -X POST "${{ secrets.SENTINAL_API_URL }}/api/cicd/webhook/sonarqube" \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer ${{ secrets.SENTINAL_API_TOKEN }}" \
             -d '{
               "commit_hash": "${{ github.sha }}",
               "branch": "${{ github.ref_name }}",
               "results": ${{ steps.sonarqube-results.outputs.results }}
             }'
   ```

### Option 2: Backend Polls Scanners Directly

**Flow:**
```
1. Developer pushes code
   ↓
2. GitHub Actions triggers CI/CD pipeline
   ↓
3. Scans complete → Results stored in SonarQube/ZAP/Trivy servers
   ↓
4. Backend periodically polls scanners:
   - Checks SonarQube for new issues
   - Checks Trivy for new scans
   - Checks ZAP for completed scans
   ↓
5. Backend stores results in database
   ↓
6. Dashboard shows results
```

**Pros:** No changes needed to GitHub Actions
**Cons:** Delayed updates, requires polling logic, may miss some scans

### Option 3: Hybrid Approach (Best)

**Flow:**
```
1. Developer pushes code
   ↓
2. GitHub Actions triggers CI/CD pipeline
   ↓
3. GitHub Actions calls backend webhook: POST /api/cicd/webhook/trigger
   ↓
4. Backend creates CI/CD run record
   ↓
5. GitHub Actions runs scans:
   - SonarQube → Sends results to webhook
   - Trivy → Sends results to webhook
   - ZAP → Sends results to webhook
   ↓
6. Backend stores all results
   ↓
7. Dashboard shows complete results
```

---

## Recommended Implementation

### Step 1: Create Webhook Endpoints

**File:** `backend/app/api/cicd.py`

Add new endpoints:
- `POST /api/cicd/webhook/sonarqube` - Receive SonarQube results
- `POST /api/cicd/webhook/trivy` - Receive Trivy results
- `POST /api/cicd/webhook/zap` - Receive ZAP results
- `POST /api/cicd/webhook/trigger` - Notify scan started

### Step 2: Update GitHub Actions Workflow

**File:** `.github/workflows/ci-cd.yml`

Add steps after each scan to:
1. Parse scan results
2. Format as JSON
3. POST to backend webhook endpoint
4. Include commit hash, branch, and results

### Step 3: Add Authentication

- Use API token authentication for webhooks
- Store token in GitHub Secrets: `SENTINAL_API_TOKEN`
- Store API URL in GitHub Secrets: `SENTINAL_API_URL`

---

## Detailed Workflow Example

### SonarQube Integration:

```yaml
sast:
  name: SAST Scan (SonarQube)
  runs-on: ubuntu-latest
  needs: [build]
  steps:
    - uses: actions/checkout@v4
    
    - name: SonarQube Scan
      uses: sonarsource/sonarqube-scan-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONARQUBE_TOKEN }}
        SONAR_HOST_URL: ${{ secrets.SONARQUBE_URL }}
      continue-on-error: true
    
    - name: Fetch SonarQube Issues
      id: fetch-issues
      run: |
        # Get all issues
        ISSUES=$(curl -s -u ${{ secrets.SONARQUBE_TOKEN }}: \
          "${{ secrets.SONARQUBE_URL }}/api/issues/search?componentKeys=sentinal&ps=500" | jq '.issues')
        
        # Get metrics
        METRICS=$(curl -s -u ${{ secrets.SONARQUBE_TOKEN }}: \
          "${{ secrets.SONARQUBE_URL }}/api/measures/component?component=sentinal&metricKeys=coverage,bugs,vulnerabilities,code_smells" | jq '.component.measures')
        
        # Combine results
        echo "results<<EOF" >> $GITHUB_OUTPUT
        jq -n --argjson issues "$ISSUES" --argjson metrics "$METRICS" \
          '{issues: $issues, metrics: $metrics}' >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT
    
    - name: Send to Dashboard
      run: |
        curl -X POST "${{ secrets.SENTINAL_API_URL }}/api/cicd/webhook/sonarqube" \
          -H "Content-Type: application/json" \
          -H "X-API-Token: ${{ secrets.SENTINAL_API_TOKEN }}" \
          -d '{
            "commit_hash": "${{ github.sha }}",
            "branch": "${{ github.ref_name }}",
            "workflow_run_id": "${{ github.run_id }}",
            "results": ${{ steps.fetch-issues.outputs.results }}
          }'
```

### Trivy Integration:

```yaml
container-scan:
  name: Container Scan (Trivy)
  runs-on: ubuntu-latest
  needs: [build]
  steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'image'
        image-ref: 'sentinal-backend:latest'
        format: 'json'
        output: 'trivy-results.json'
      continue-on-error: true
    
    - name: Send to Dashboard
      run: |
        curl -X POST "${{ secrets.SENTINAL_API_URL }}/api/cicd/webhook/trivy" \
          -H "Content-Type: application/json" \
          -H "X-API-Token: ${{ secrets.SENTINAL_API_TOKEN }}" \
          -d "{
            \"commit_hash\": \"${{ github.sha }}\",
            \"branch\": \"${{ github.ref_name }}\",
            \"workflow_run_id\": \"${{ github.run_id }}\",
            \"results\": $(cat trivy-results.json)
          }"
```

### ZAP Integration:

```yaml
dast:
  name: DAST Scan (OWASP ZAP)
  runs-on: ubuntu-latest
  needs: [build]
  steps:
    - uses: actions/checkout@v4
    
    - name: ZAP Baseline Scan
      uses: zaproxy/action-baseline@v0.10.0
      with:
        target: 'http://localhost'
        format: json
        output: zap-results.json
      continue-on-error: true
    
    - name: Send to Dashboard
      run: |
        curl -X POST "${{ secrets.SENTINAL_API_URL }}/api/cicd/webhook/zap" \
          -H "Content-Type: application/json" \
          -H "X-API-Token: ${{ secrets.SENTINAL_API_TOKEN }}" \
          -d "{
            \"commit_hash\": \"${{ github.sha }}\",
            \"branch\": \"${{ github.ref_name }}\",
            \"workflow_run_id\": \"${{ github.run_id }}\",
            \"results\": $(cat zap-results.json)
          }"
```

---

## Backend Webhook Implementation

### Webhook Endpoint Structure:

```python
# backend/app/api/cicd.py

class CICDWebhook(Resource):
    """Webhook endpoint for receiving CI/CD scan results."""
    
    def post(self, scan_type):
        """
        Receive scan results from GitHub Actions.
        
        scan_type: 'sonarqube', 'trivy', 'zap'
        """
        # Verify API token
        api_token = request.headers.get('X-API-Token')
        if not self._verify_token(api_token):
            return {'error': 'Invalid API token'}, 401
        
        data = request.json
        commit_hash = data.get('commit_hash')
        branch = data.get('branch', 'main')
        workflow_run_id = data.get('workflow_run_id')
        results = data.get('results', {})
        
        # Find or create CI/CD run
        run = CICDRun.query.filter_by(
            commit_hash=commit_hash,
            branch=branch
        ).first()
        
        if not run:
            run = CICDRun(
                commit_hash=commit_hash,
                branch=branch,
                status='Running',
                workflow_run_id=workflow_run_id
            )
            db.session.add(run)
        
        # Store results based on scan type
        if scan_type == 'sonarqube':
            run.sast_results = self._parse_sonarqube_results(results)
        elif scan_type == 'trivy':
            run.trivy_results = self._parse_trivy_results(results)
        elif scan_type == 'zap':
            run.dast_results = self._parse_zap_results(results)
        
        # Update vulnerability counts
        self._update_vulnerability_counts(run)
        
        # Update status
        if run.sast_results and run.trivy_results and run.dast_results:
            run.status = 'Blocked' if run.critical_vulnerabilities > 0 else 'Success'
            run.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return {'status': 'success', 'run_id': run.id}, 200
```

---

## Summary

### Current State:
- ❌ GitHub Actions runs scans independently
- ❌ Results don't appear in dashboard
- ❌ No connection between GitHub Actions and dashboard

### After Implementation:
- ✅ GitHub Actions sends results to backend after each scan
- ✅ Backend stores results in database
- ✅ Dashboard automatically displays results
- ✅ Real-time updates when scans complete
- ✅ Complete scan history visible in dashboard

### Required Changes:
1. **Backend:** Add webhook endpoints (`/api/cicd/webhook/*`)
2. **GitHub Actions:** Add steps to send results to webhooks
3. **GitHub Secrets:** Add `SENTINAL_API_URL` and `SENTINAL_API_TOKEN`
4. **Backend Config:** Add webhook token validation

### Benefits:
- Single source of truth (dashboard)
- Complete scan history
- Real-time visibility
- Unified view of all security scans
- Better tracking and reporting

