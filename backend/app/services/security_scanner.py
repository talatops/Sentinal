"""Security scanner service for integrating with Trivy, OWASP ZAP, and SonarQube."""
import requests
import time
from typing import Dict, Any, Optional
from flask import current_app
from datetime import datetime


class SecurityScanner:
    """Service for running security scans."""

    def __init__(self):
        """Initialize scanner with configuration."""
        self.trivy_url = current_app.config.get('TRIVY_API_URL', 'http://trivy:8080')
        self.zap_url = current_app.config.get('OWASP_ZAP_API_URL', 'http://zap:8090')
        self.sonarqube_url = current_app.config.get('SONARQUBE_URL', 'http://sonarqube:9000')
        self.sonarqube_token = current_app.config.get('SONARQUBE_TOKEN', '')
        self.sonarqube_project_key = current_app.config.get('SONARQUBE_PROJECT_KEY', 'sentinal')

    def run_sast_scan(self, commit_hash: str, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Run SAST scan using SonarQube.

        Args:
            commit_hash: Git commit hash
            project_key: SonarQube project key (optional, uses config default)

        Returns:
            Dictionary with complete scan results including all issues
        """
        try:
            project_key = project_key or self.sonarqube_project_key

            # Get all issues with pagination
            all_issues = []
            page = 1
            page_size = 500

            while True:
                response = requests.get(
                    f'{self.sonarqube_url}/api/issues/search',
                    params={
                        'componentKeys': project_key,
                        'p': page,
                        'ps': page_size,
                        'resolved': 'false'
                    },
                    auth=(self.sonarqube_token, ''),
                    timeout=30
                )

                if response.status_code != 200:
                    current_app.logger.error(f'SonarQube API error: {response.status_code} - {response.text}')
                    break

                data = response.json()
                issues = data.get('issues', [])
                all_issues.extend(issues)

                # Check if more pages
                paging = data.get('paging', {})
                if paging.get('pageIndex', 0) * paging.get('pageSize', 0) >= paging.get('total', 0):
                    break

                page += 1

            # Get metrics
            metrics_response = requests.get(
                f'{self.sonarqube_url}/api/measures/component',
                params={
                    'component': project_key,
                    'metricKeys': (
                        'coverage,bugs,vulnerabilities,code_smells,security_hotspots,'
                        'technical_debt,duplicated_lines_density,ncloc,files'
                    )
                },
                auth=(self.sonarqube_token, ''),
                timeout=30
            )

            metrics = {}
            if metrics_response.status_code == 200:
                metrics_data = metrics_response.json()
                component = metrics_data.get('component', {})
                for measure in component.get('measures', []):
                    metric_key = measure.get('metric')
                    value = measure.get('value')
                    if value:
                        # Parse value based on metric type
                        if metric_key in ['coverage', 'duplicated_lines_density']:
                            metrics[metric_key] = float(value)
                        elif metric_key == 'technical_debt':
                            metrics[metric_key] = self._parse_technical_debt(value)
                        else:
                            metrics[metric_key] = int(value)

            # Get quality gate status
            quality_gate_response = requests.get(
                f'{self.sonarqube_url}/api/qualitygates/project_status',
                params={'projectKey': project_key},
                auth=(self.sonarqube_token, ''),
                timeout=30
            )

            quality_gate = {'status': 'UNKNOWN'}
            if quality_gate_response.status_code == 200:
                qg_data = quality_gate_response.json()
                quality_gate = {
                    'status': qg_data.get('projectStatus', {}).get('status', 'UNKNOWN'),
                    'conditions': qg_data.get('projectStatus', {}).get('conditions', [])
                }

            # Count issues by severity
            severity_counts = {'CRITICAL': 0, 'BLOCKER': 0, 'MAJOR': 0, 'MINOR': 0, 'INFO': 0}
            for issue in all_issues:
                severity = issue.get('severity', 'INFO')
                if severity in severity_counts:
                    severity_counts[severity] += 1

            # Parse issues with full details
            parsed_issues = []
            for issue in all_issues:
                parsed_issue = {
                    'key': issue.get('key'),
                    'severity': issue.get('severity'),
                    'type': issue.get('type'),
                    'component': issue.get('component'),
                    'line': issue.get('line'),
                    'message': issue.get('message'),
                    'rule': issue.get('rule'),
                    'status': issue.get('status'),
                    'author': issue.get('author'),
                    'creation_date': issue.get('creationDate'),
                    'update_date': issue.get('updateDate'),
                    'text_range': issue.get('textRange'),
                    'flows': issue.get('flows', []),
                    'tags': issue.get('tags', [])
                }

                # Get rule details if available
                if issue.get('rule'):
                    try:
                        rule_response = requests.get(
                            f'{self.sonarqube_url}/api/rules/show',
                            params={'key': issue.get('rule')},
                            auth=(self.sonarqube_token, ''),
                            timeout=10
                        )
                        if rule_response.status_code == 200:
                            rule_data = rule_response.json().get('rule', {})
                            parsed_issue['rule_name'] = rule_data.get('name')
                            parsed_issue['rule_description'] = rule_data.get('htmlDesc') or rule_data.get('mdDesc', '')
                            parsed_issue['effort'] = rule_data.get('debtRemFn', {}).get('coeff', '')
                    except Exception as e:
                        current_app.logger.warning(f'Failed to get rule details: {e}')

                parsed_issues.append(parsed_issue)

            # Map severity to standard levels
            critical = severity_counts.get('CRITICAL', 0) + severity_counts.get('BLOCKER', 0)
            high = severity_counts.get('MAJOR', 0)
            medium = severity_counts.get('MINOR', 0)
            low = severity_counts.get('INFO', 0)

            return {
                'status': 'completed',
                'project_key': project_key,
                'scan_timestamp': datetime.utcnow().isoformat(),
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low,
                'info': low,
                'total': len(all_issues),
                'issues': parsed_issues,
                'metrics': metrics,
                'quality_gate': quality_gate
            }
        except Exception as e:
            current_app.logger.error(f'SonarQube scan failed: {str(e)}')
            return {
                'status': 'failed',
                'error': str(e),
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'total': 0,
                'issues': []
            }

    def run_trivy_scan(self, image_name: str = 'sentinal-backend:latest') -> Dict[str, Any]:
        """
        Run Trivy container scan.

        Args:
            image_name: Docker image name to scan

        Returns:
            Dictionary with complete vulnerability data
        """
        try:
            # Trivy server API - submit scan
            scan_response = requests.post(
                f'{self.trivy_url}/v1/scan',
                json={'image': image_name},
                timeout=300  # 5 minutes timeout
            )

            if scan_response.status_code != 200:
                current_app.logger.error(f'Trivy scan submission failed: {scan_response.status_code}')
                return {
                    'status': 'failed',
                    'error': f'Scan submission failed: {scan_response.status_code}',
                    'critical': 0,
                    'total': 0
                }

            scan_data = scan_response.json()
            scan_id = scan_data.get('scan_id')

            if not scan_id:
                # If no scan_id, try direct scan (older API)
                return self._trivy_direct_scan(image_name)

            # Poll for results
            max_attempts = 60
            attempt = 0
            while attempt < max_attempts:
                result_response = requests.get(
                    f'{self.trivy_url}/v1/scan/{scan_id}',
                    timeout=30
                )

                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get('status') == 'completed':
                        return self._parse_trivy_results(result_data, image_name)
                    elif result_data.get('status') == 'failed':
                        return {
                            'status': 'failed',
                            'error': result_data.get('error', 'Scan failed'),
                            'critical': 0,
                            'total': 0
                        }

                time.sleep(2)
                attempt += 1

            return {
                'status': 'failed',
                'error': 'Scan timeout',
                'critical': 0,
                'total': 0
            }

        except Exception as e:
            current_app.logger.error(f'Trivy scan failed: {str(e)}')
            return {
                'status': 'failed',
                'error': str(e),
                'critical': 0,
                'total': 0
            }

    def _trivy_direct_scan(self, image_name: str) -> Dict[str, Any]:
        """Fallback direct scan for Trivy."""
        try:
            # Try JSON format endpoint
            response = requests.get(
                f'{self.trivy_url}/v1/images/{image_name}',
                params={'format': 'json'},
                timeout=300
            )

            if response.status_code == 200:
                return self._parse_trivy_results(response.json(), image_name)

            return {
                'status': 'failed',
                'error': 'Trivy API not available',
                'critical': 0,
                'total': 0
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'critical': 0,
                'total': 0
            }

    def _parse_trivy_results(self, data: Dict[str, Any], image_name: str) -> Dict[str, Any]:
        """Parse Trivy scan results."""
        vulnerabilities = []
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}

        # Parse results structure
        results = data.get('Results', [])
        os_packages = {'total': 0, 'vulnerable': 0}
        language_packages = {}

        for result in results:
            result_type = result.get('Type', '')

            if result_type == 'os':
                packages = result.get('Packages', [])
                os_packages['total'] = len(packages)

                for vuln in result.get('Vulnerabilities', []):
                    severity = vuln.get('Severity', 'UNKNOWN')
                    if severity in severity_counts:
                        severity_counts[severity] += 1

                    parsed_vuln = {
                        'vulnerability_id': vuln.get('VulnerabilityID'),
                        'pkg_name': vuln.get('PkgName'),
                        'pkg_path': vuln.get('PkgPath'),
                        'installed_version': vuln.get('InstalledVersion'),
                        'fixed_version': vuln.get('FixedVersion'),
                        'severity': severity,
                        'title': vuln.get('Title'),
                        'description': vuln.get('Description'),
                        'published_date': vuln.get('PublishedDate'),
                        'last_modified_date': vuln.get('LastModifiedDate'),
                        'cvss': vuln.get('CVSS', {}),
                        'cwe_ids': vuln.get('CweIDs', []),
                        'references': vuln.get('References', []),
                        'layer': vuln.get('Layer', {}),
                        'primary_url': vuln.get('PrimaryURL'),
                        'class': 'os-pkgs',
                        'package_type': result.get('Class', '')
                    }
                    vulnerabilities.append(parsed_vuln)
                    os_packages['vulnerable'] += 1

            elif result_type in ['python', 'node', 'go', 'java']:
                if result_type not in language_packages:
                    language_packages[result_type] = {'total': 0, 'vulnerable': 0}

                packages = result.get('Packages', [])
                language_packages[result_type]['total'] = len(packages)

                for vuln in result.get('Vulnerabilities', []):
                    severity = vuln.get('Severity', 'UNKNOWN')
                    if severity in severity_counts:
                        severity_counts[severity] += 1

                    parsed_vuln = {
                        'vulnerability_id': vuln.get('VulnerabilityID'),
                        'pkg_name': vuln.get('PkgName'),
                        'pkg_path': vuln.get('PkgPath'),
                        'installed_version': vuln.get('InstalledVersion'),
                        'fixed_version': vuln.get('FixedVersion'),
                        'severity': severity,
                        'title': vuln.get('Title'),
                        'description': vuln.get('Description'),
                        'published_date': vuln.get('PublishedDate'),
                        'last_modified_date': vuln.get('LastModifiedDate'),
                        'cvss': vuln.get('CVSS', {}),
                        'cwe_ids': vuln.get('CweIDs', []),
                        'references': vuln.get('References', []),
                        'primary_url': vuln.get('PrimaryURL'),
                        'class': 'lang-pkgs',
                        'package_type': result_type
                    }
                    vulnerabilities.append(parsed_vuln)
                    language_packages[result_type]['vulnerable'] += 1

        metadata = data.get('Metadata', {})

        return {
            'status': 'completed',
            'image': image_name,
            'scan_timestamp': datetime.utcnow().isoformat(),
            'critical': severity_counts.get('CRITICAL', 0),
            'high': severity_counts.get('HIGH', 0),
            'medium': severity_counts.get('MEDIUM', 0),
            'low': severity_counts.get('LOW', 0),
            'unknown': severity_counts.get('UNKNOWN', 0),
            'total': len(vulnerabilities),
            'vulnerabilities': vulnerabilities,
            'os_packages': os_packages,
            'language_packages': language_packages,
            'metadata': {
                'image_id': metadata.get('ImageID'),
                'digest': metadata.get('Digest'),
                'repo_tags': metadata.get('RepoTags', []),
                'repo_digests': metadata.get('RepoDigests', [])
            }
        }

    def run_dast_scan(self, target_url: str = 'http://localhost', scan_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run DAST scan using OWASP ZAP.

        Args:
            target_url: URL to scan
            scan_id: Optional scan ID for status checking

        Returns:
            Dictionary with complete alert data
        """
        try:
            # If scan_id provided, check status
            if scan_id:
                return self._get_zap_scan_status(scan_id, target_url)

            # Start spider scan
            spider_response = requests.get(
                f'{self.zap_url}/JSON/spider/action/scan',
                params={'url': target_url},
                timeout=30
            )

            if spider_response.status_code != 200:
                current_app.logger.error(f'ZAP spider scan failed: {spider_response.status_code}')
                return {
                    'status': 'failed',
                    'error': 'Spider scan failed',
                    'critical': 0,
                    'total': 0
                }

            spider_data = spider_response.json()
            spider_scan_id = spider_data.get('scan')

            # Wait for spider to complete
            spider_complete = False
            max_wait = 300  # 5 minutes
            waited = 0

            while not spider_complete and waited < max_wait:
                status_response = requests.get(
                    f'{self.zap_url}/JSON/spider/view/status',
                    params={'scanId': spider_scan_id},
                    timeout=10
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    progress = int(status_data.get('status', 0))
                    if progress >= 100:
                        spider_complete = True
                        break

                time.sleep(2)
                waited += 2

            # Start active scan
            active_response = requests.get(
                f'{self.zap_url}/JSON/ascan/action/scan',
                params={'url': target_url},
                timeout=30
            )

            if active_response.status_code != 200:
                return {
                    'status': 'running',
                    'target': target_url,
                    'spider_scan_id': spider_scan_id,
                    'spider_complete': spider_complete,
                    'message': 'Active scan failed to start'
                }

            active_data = active_response.json()
            active_scan_id = active_data.get('scan')

            # Get spider results
            spider_results_response = requests.get(
                f'{self.zap_url}/JSON/spider/view/results',
                params={'scanId': spider_scan_id},
                timeout=10
            )

            urls_found = 0
            if spider_results_response.status_code == 200:
                spider_results = spider_results_response.json()
                urls_found = len(spider_results.get('results', []))

            # Return running status with scan IDs
            return {
                'status': 'running',
                'target': target_url,
                'spider_scan_id': spider_scan_id,
                'active_scan_id': active_scan_id,
                'spider_complete': spider_complete,
                'spider_results': {'urls_found': urls_found},
                'scan_start': datetime.utcnow().isoformat()
            }

        except Exception as e:
            current_app.logger.error(f'ZAP scan failed: {str(e)}')
            return {
                'status': 'failed',
                'error': str(e),
                'critical': 0,
                'total': 0
            }

    def _get_zap_scan_status(self, scan_id: str, target_url: str) -> Dict[str, Any]:
        """Get ZAP scan status and results."""
        try:
            # Check active scan status
            status_response = requests.get(
                f'{self.zap_url}/JSON/ascan/view/status',
                params={'scanId': scan_id},
                timeout=10
            )

            progress = 0
            if status_response.status_code == 200:
                status_data = status_response.json()
                progress = int(status_data.get('status', 0))

            if progress < 100:
                return {
                    'status': 'running',
                    'target': target_url,
                    'active_scan_id': scan_id,
                    'active_scan_progress': progress
                }

            # Scan complete, get alerts
            alerts_response = requests.get(
                f'{self.zap_url}/JSON/core/view/alerts',
                params={'baseurl': target_url},
                timeout=30
            )

            if alerts_response.status_code != 200:
                return {
                    'status': 'completed',
                    'target': target_url,
                    'critical': 0,
                    'total': 0,
                    'alerts': []
                }

            alerts_data = alerts_response.json()
            alerts = alerts_data.get('alerts', [])

            # Parse alerts
            parsed_alerts = []
            severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0, 'Informational': 0}

            for alert in alerts:
                risk = alert.get('risk', 'Informational')
                if risk in severity_counts:
                    severity_counts[risk] += 1

                parsed_alert = {
                    'id': alert.get('pluginId'),
                    'name': alert.get('name'),
                    'risk': risk,
                    'confidence': alert.get('confidence'),
                    'cweid': alert.get('cweid'),
                    'wascid': alert.get('wascid'),
                    'url': alert.get('url'),
                    'method': alert.get('method'),
                    'param': alert.get('param'),
                    'attack': alert.get('attack'),
                    'evidence': alert.get('evidence'),
                    'description': alert.get('description'),
                    'solution': alert.get('solution'),
                    'reference': alert.get('reference'),
                    'other': alert.get('other'),
                    'alert': alert.get('alert'),
                    'messageId': alert.get('messageId'),
                    'pluginId': alert.get('pluginId'),
                    'sourceid': alert.get('sourceid')
                }
                parsed_alerts.append(parsed_alert)

            return {
                'status': 'completed',
                'target': target_url,
                'active_scan_id': scan_id,
                'scan_start': datetime.utcnow().isoformat(),  # Should be stored from start
                'scan_end': datetime.utcnow().isoformat(),
                'critical': severity_counts.get('Critical', 0),
                'high': severity_counts.get('High', 0),
                'medium': severity_counts.get('Medium', 0),
                'low': severity_counts.get('Low', 0),
                'informational': severity_counts.get('Informational', 0),
                'total': len(alerts),
                'alerts': parsed_alerts,
                'spider_results': {'urls_found': 0, 'urls_scanned': 0},
                'active_scan_progress': 100
            }

        except Exception as e:
            current_app.logger.error(f'ZAP status check failed: {str(e)}')
            return {
                'status': 'failed',
                'error': str(e),
                'critical': 0,
                'total': 0
            }

    def _parse_technical_debt(self, value: str) -> str:
        """Parse technical debt value."""
        # SonarQube returns technical debt in minutes
        try:
            minutes = int(value)
            hours = minutes // 60
            mins = minutes % 60
            if hours > 0:
                return f'{hours}h {mins}min'
            return f'{mins}min'
        except Exception:
            return value
