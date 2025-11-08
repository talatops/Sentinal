"""Threat detector service for auto-creating threats from scan findings."""

from typing import List, Dict, Any, Optional
from app import db
from app.models.threat import Threat
from app.models.threat_vulnerability import ThreatVulnerability
from app.models.cicd import CICDRun
from app.services.stride_dread_engine import STRIDEEngine
from app.services.dread_scorer import DREADScorer
from app.services.threat_patterns import match_threat_patterns


class ThreatDetector:
    """Service for automatically detecting and creating threats from security scan findings."""

    def __init__(self):
        self.stride_engine = STRIDEEngine()
        self.dread_scorer = DREADScorer()

    def detect_threats_from_scan(self, scan_run_id: int) -> List[Dict[str, Any]]:
        """
        Analyze scan results and create/link threats.

        Args:
            scan_run_id: ID of the CI/CD run

        Returns:
            List of created/linked threat information
        """
        scan_run = CICDRun.query.get(scan_run_id)
        if not scan_run:
            return []

        threats_created = []

        # Process SonarQube (SAST) results
        if scan_run.sast_results:
            threats_created.extend(self._process_sonarqube_results(scan_run.sast_results, scan_run_id))

        # Process OWASP ZAP (DAST) results
        if scan_run.dast_results:
            threats_created.extend(self._process_zap_results(scan_run.dast_results, scan_run_id))

        # Process Trivy results
        if scan_run.trivy_results:
            threats_created.extend(self._process_trivy_results(scan_run.trivy_results, scan_run_id))

        return threats_created

    def _process_sonarqube_results(self, sast_results: Dict[str, Any], scan_run_id: int) -> List[Dict[str, Any]]:
        """Process SonarQube SAST results and create/link threats."""
        threats_created = []

        if not isinstance(sast_results, dict):
            return threats_created

        issues = sast_results.get("issues", [])
        if not isinstance(issues, list):
            return threats_created

        for issue in issues:
            # Extract issue details
            rule_key = issue.get("rule", "")
            severity = issue.get("severity", "INFO").lower()
            message = issue.get("message", "")
            component = issue.get("component", "")
            line = issue.get("line")

            # Only process high/critical severity issues
            if severity not in ["critical", "blocker", "major", "high"]:
                continue

            # Create asset and flow description from issue
            asset = component.split(":")[-1] if component else "Unknown Component"
            flow = f"SonarQube detected: {message} in {component}"
            if line:
                flow += f" at line {line}"

            # Check if this matches any threat patterns
            matched_patterns = match_threat_patterns(asset, flow)

            if matched_patterns:
                # Create or link threat
                threat_info = self._create_or_link_threat(
                    asset=asset,
                    flow=flow,
                    vulnerability_type="sonarqube",
                    vulnerability_id=rule_key,
                    scan_run_id=scan_run_id,
                    severity=severity,
                    vulnerability_data=issue,
                )
                if threat_info:
                    threats_created.append(threat_info)

        return threats_created

    def _process_zap_results(self, dast_results: Dict[str, Any], scan_run_id: int) -> List[Dict[str, Any]]:
        """Process OWASP ZAP DAST results and create/link threats."""
        threats_created = []

        if not isinstance(dast_results, dict):
            return threats_created

        alerts = dast_results.get("alerts", [])
        if not isinstance(alerts, list):
            return threats_created

        for alert in alerts:
            # Extract alert details
            alert_id = str(alert.get("pluginId", ""))
            name = alert.get("name", "")
            risk = alert.get("risk", "Informational").lower()
            description = alert.get("description", "")
            url = alert.get("url", "")

            # Only process medium/high/informational risks
            if risk == "informational":
                continue

            # Create asset and flow description
            asset = url.split("/")[2] if url else "Web Application"
            flow = f"ZAP detected: {name} - {description} at {url}"

            # Check if this matches any threat patterns
            matched_patterns = match_threat_patterns(asset, flow)

            if matched_patterns:
                # Create or link threat
                threat_info = self._create_or_link_threat(
                    asset=asset,
                    flow=flow,
                    vulnerability_type="zap",
                    vulnerability_id=alert_id,
                    scan_run_id=scan_run_id,
                    severity=risk,
                    vulnerability_data=alert,
                )
                if threat_info:
                    threats_created.append(threat_info)

        return threats_created

    def _process_trivy_results(self, trivy_results: Dict[str, Any], scan_run_id: int) -> List[Dict[str, Any]]:
        """Process Trivy scan results and create/link threats."""
        threats_created = []

        if not isinstance(trivy_results, dict):
            return threats_created

        # Trivy results structure can vary, handle common formats
        results = trivy_results.get("Results", [])
        if not isinstance(results, list):
            return threats_created

        for result in results:
            vulnerabilities = result.get("Vulnerabilities", [])
            if not isinstance(vulnerabilities, list):
                continue

            target = result.get("Target", "Unknown")

            for vuln in vulnerabilities:
                vuln_id = vuln.get("VulnerabilityID", "")
                severity = vuln.get("Severity", "UNKNOWN").lower()
                title = vuln.get("Title", "")
                description = vuln.get("Description", "")

                # Only process critical/high severity
                if severity not in ["critical", "high"]:
                    continue

                # Create asset and flow description
                asset = target
                flow = f"Trivy detected CVE: {vuln_id} - {title}. {description}"

                # Check if this matches any threat patterns
                matched_patterns = match_threat_patterns(asset, flow)

                if matched_patterns:
                    # Create or link threat
                    threat_info = self._create_or_link_threat(
                        asset=asset,
                        flow=flow,
                        vulnerability_type="trivy",
                        vulnerability_id=vuln_id,
                        scan_run_id=scan_run_id,
                        severity=severity,
                        vulnerability_data=vuln,
                    )
                    if threat_info:
                        threats_created.append(threat_info)

        return threats_created

    def _create_or_link_threat(
        self,
        asset: str,
        flow: str,
        vulnerability_type: str,
        vulnerability_id: str,
        scan_run_id: int,
        severity: str,
        vulnerability_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new threat or link to existing threat.

        Returns:
            Dictionary with threat information, or None if creation failed
        """
        try:
            # Check if vulnerability is already linked
            existing_link = ThreatVulnerability.query.filter_by(
                vulnerability_type=vulnerability_type, vulnerability_id=vulnerability_id
            ).first()

            if existing_link:
                # Update existing link if needed
                if existing_link.status == "resolved":
                    existing_link.status = "linked"  # Re-open if resolved
                existing_link.scan_run_id = scan_run_id
                existing_link.severity = severity
                existing_link.vulnerability_data = vulnerability_data
                db.session.commit()

                return {"action": "linked", "threat_id": existing_link.threat_id, "vulnerability_id": existing_link.id}

            # Use advanced STRIDE analysis
            advanced_analysis = self.stride_engine.analyze_threat_advanced(asset, flow)
            stride_categories = advanced_analysis["stride_categories"]

            # Auto-score DREAD
            dread_suggestions = self.dread_scorer.suggest_dread_scores(asset, flow)
            dread_scores = dread_suggestions["suggested_scores"]

            # Calculate risk level
            total_score = sum(dread_scores.values()) / 5.0
            risk_level = "High" if total_score > 7 else "Medium" if total_score > 4 else "Low"

            # Get mitigation recommendations
            mitigation = self.stride_engine.get_mitigation_recommendations(stride_categories, risk_level)

            # Create new threat
            threat = Threat(
                asset=asset,
                flow=flow,
                stride_categories=stride_categories,
                dread_score=dread_scores,
                risk_level=risk_level,
                mitigation=mitigation,
            )
            db.session.add(threat)
            db.session.flush()  # Get threat ID

            # Link vulnerability to threat
            threat_vuln = ThreatVulnerability(
                threat_id=threat.id,
                vulnerability_type=vulnerability_type,
                vulnerability_id=vulnerability_id,
                scan_run_id=scan_run_id,
                severity=severity,
                status="linked",
                vulnerability_data=vulnerability_data,
            )
            db.session.add(threat_vuln)
            db.session.commit()

            return {"action": "created", "threat_id": threat.id, "vulnerability_id": threat_vuln.id}

        except Exception as e:
            db.session.rollback()
            # Log error but don't fail the entire process
            print(f"Error creating/linking threat: {e}")
            return None
