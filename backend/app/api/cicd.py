"""CI/CD API endpoints."""

from flask import request
from flask_restful import Resource
from app.core.security import jwt_required
from app import db
from app.models.cicd import CICDRun
from app.services.security_scanner import SecurityScanner
from app.core.webhook_auth import webhook_auth_required
from app.api.websocket import emit_scan_update, emit_dashboard_update
from datetime import datetime


class CICDRunList(Resource):
    """CI/CD runs list endpoint."""

    @jwt_required()
    def get(self):
        """Get all CI/CD runs."""
        limit = request.args.get("limit", 50, type=int)
        runs = CICDRun.query.order_by(CICDRun.created_at.desc()).limit(limit).all()
        return {"runs": [run.to_dict() for run in runs]}, 200


class CICDRunDetail(Resource):
    """CI/CD run detail endpoint."""

    @jwt_required()
    def get(self, run_id):
        """Get CI/CD run details."""
        run = CICDRun.query.get_or_404(run_id)
        return {"run": run.to_dict()}, 200


class CICDTrigger(Resource):
    """Trigger CI/CD pipeline."""

    @jwt_required()
    def post(self):
        """Trigger a new CI/CD run."""
        data = request.json or {}
        commit_hash = data.get("commit_hash", "manual")
        branch = data.get("branch", "main")

        # Create new run
        run = CICDRun(commit_hash=commit_hash, branch=branch, status="Running")
        db.session.add(run)
        db.session.commit()

        # Start security scans asynchronously (in production, use Celery)
        scanner = SecurityScanner()

        try:
            # Run SAST (SonarQube)
            sast_results = scanner.run_sast_scan(commit_hash)
            run.sast_results = sast_results

            # Run Trivy scan
            trivy_results = scanner.run_trivy_scan()
            run.trivy_results = trivy_results

            # Run DAST (OWASP ZAP)
            dast_results = scanner.run_dast_scan()
            run.dast_results = dast_results

            # Calculate vulnerabilities
            critical_vulns = 0
            total_vulns = 0

            if trivy_results:
                critical_vulns += trivy_results.get("critical", 0)
                total_vulns += trivy_results.get("total", 0)

            if sast_results:
                critical_vulns += sast_results.get("critical", 0)
                total_vulns += sast_results.get("total", 0)

            if dast_results:
                critical_vulns += dast_results.get("critical", 0)
                total_vulns += dast_results.get("total", 0)

            run.critical_vulnerabilities = critical_vulns
            run.total_vulnerabilities = total_vulns

            # Determine status
            if critical_vulns > 0:
                run.status = "Blocked"
            else:
                run.status = "Success"

            run.completed_at = datetime.utcnow()

        except Exception:
            run.status = "Failed"
            run.completed_at = datetime.utcnow()

        db.session.commit()

        return {"run": run.to_dict()}, 201


class CICDDashboard(Resource):
    """CI/CD dashboard endpoint."""

    @jwt_required()
    def get(self):
        """Get dashboard statistics."""
        total_runs = CICDRun.query.count()
        successful_runs = CICDRun.query.filter_by(status="Success").count()
        failed_runs = CICDRun.query.filter_by(status="Failed").count()
        blocked_runs = CICDRun.query.filter_by(status="Blocked").count()

        success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

        # Recent runs
        recent_runs = CICDRun.query.order_by(CICDRun.created_at.desc()).limit(10).all()

        # Vulnerability trends (last 30 runs)
        recent_vulns = CICDRun.query.order_by(CICDRun.created_at.desc()).limit(30).all()
        vuln_trend = [
            {
                "date": run.created_at.isoformat() if run.created_at else None,
                "critical": run.critical_vulnerabilities,
                "total": run.total_vulnerabilities,
            }
            for run in recent_vulns
        ]

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "blocked_runs": blocked_runs,
            "success_rate": round(success_rate, 2),
            "recent_runs": [run.to_dict() for run in recent_runs],
            "vulnerability_trend": vuln_trend,
        }, 200


class CICDWebhook(Resource):
    """Webhook endpoint for receiving CI/CD scan results from GitHub Actions."""

    @webhook_auth_required
    def post(self, scan_type):
        """Receive scan results from GitHub Actions.

        Args:
            scan_type: Type of scan (sonarqube, zap, trivy, lint, test)
        """
        data = request.json or {}

        # Get run info from webhook payload
        commit_hash = data.get("commit_hash") or data.get("sha") or "unknown"
        branch = data.get("branch") or data.get("ref", "main").replace("refs/heads/", "")
        run_id = data.get("run_id")

        # Find or create CI/CD run
        if run_id:
            run = CICDRun.query.get(run_id)
        else:
            # Try to find by commit hash
            run = CICDRun.query.filter_by(commit_hash=commit_hash).order_by(CICDRun.created_at.desc()).first()

        if not run:
            # Create new run
            run = CICDRun(commit_hash=commit_hash, branch=branch, status="Running")
            db.session.add(run)
            db.session.commit()
            emit_dashboard_update("new_run", run.to_dict())

        # Process scan results based on type
        scan_results = data.get("results", {})
        status = data.get("status", "completed")

        try:
            if scan_type == "sonarqube":
                run.sast_results = scan_results
                emit_scan_update(run.id, "sast_progress", {"status": status, "results": scan_results})

            elif scan_type == "zap":
                run.dast_results = scan_results
                emit_scan_update(run.id, "dast_progress", {"status": status, "results": scan_results})

            elif scan_type == "trivy":
                run.trivy_results = scan_results
                emit_scan_update(run.id, "trivy_progress", {"status": status, "results": scan_results})

            elif scan_type == "lint":
                run.lint_results = scan_results
                emit_scan_update(run.id, "lint_progress", {"status": status, "results": scan_results})

            elif scan_type == "test":
                run.test_results = scan_results
                emit_scan_update(run.id, "test_progress", {"status": status, "results": scan_results})

            # Recalculate vulnerabilities
            critical_vulns = 0
            total_vulns = 0

            if run.trivy_results:
                critical_vulns += run.trivy_results.get("critical", 0)
                total_vulns += run.trivy_results.get("total", 0)

            if run.sast_results:
                critical_vulns += run.sast_results.get("critical", 0)
                total_vulns += run.sast_results.get("total", 0)

            if run.dast_results:
                critical_vulns += run.dast_results.get("critical", 0)
                total_vulns += run.dast_results.get("total", 0)

            run.critical_vulnerabilities = critical_vulns
            run.total_vulnerabilities = total_vulns

            # Update status if all scans are complete
            if status == "completed":
                # Check if all scans are done
                all_done = (
                    (run.sast_results is not None or scan_type == "sonarqube")
                    and (run.dast_results is not None or scan_type == "zap")
                    and (run.trivy_results is not None or scan_type == "trivy")
                )

                if all_done:
                    if critical_vulns > 0:
                        run.status = "Blocked"
                    else:
                        run.status = "Success"
                    run.completed_at = datetime.utcnow()

                    emit_scan_update(run.id, "completed", run.to_dict())
                    emit_dashboard_update("scan_completed", run.to_dict())

            db.session.commit()

            return {"message": f"{scan_type} results received", "run_id": run.id, "status": run.status}, 200

        except Exception as e:
            run.status = "Failed"
            run.completed_at = datetime.utcnow()
            db.session.commit()

            emit_scan_update(run.id, "failed", {"error": str(e)})

            return {"error": "Failed to process scan results", "message": str(e)}, 500


class CICDRunSAST(Resource):
    """Get detailed SonarQube results for a run."""

    @jwt_required()
    def get(self, run_id):
        """Get SonarQube results with filtering and pagination."""
        run = CICDRun.query.get_or_404(run_id)

        if not run.sast_results:
            return {"error": "No SonarQube results available"}, 404

        results = run.sast_results.copy()
        issues = results.get("issues", [])

        # Apply filters
        severity_filter = request.args.getlist("severity")
        type_filter = request.args.getlist("type")
        status_filter = request.args.getlist("status")
        component_filter = request.args.get("component")
        rule_filter = request.args.get("rule")
        search = request.args.get("search", "").lower()

        filtered_issues = issues

        if severity_filter:
            filtered_issues = [i for i in filtered_issues if i.get("severity") in severity_filter]
        if type_filter:
            filtered_issues = [i for i in filtered_issues if i.get("type") in type_filter]
        if status_filter:
            filtered_issues = [i for i in filtered_issues if i.get("status") in status_filter]
        if component_filter:
            filtered_issues = [i for i in filtered_issues if component_filter in i.get("component", "")]
        if rule_filter:
            filtered_issues = [i for i in filtered_issues if rule_filter in i.get("rule", "")]
        if search:
            filtered_issues = [
                i
                for i in filtered_issues
                if (
                    search in i.get("message", "").lower()
                    or search in i.get("component", "").lower()
                    or search in i.get("rule", "").lower()
                )
            ]

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        start = (page - 1) * per_page
        end = start + per_page

        paginated_issues = filtered_issues[start:end]

        results["issues"] = paginated_issues
        results["pagination"] = {
            "page": page,
            "per_page": per_page,
            "total": len(filtered_issues),
            "pages": (len(filtered_issues) + per_page - 1) // per_page,
        }

        return {"results": results}, 200


class CICDRunDAST(Resource):
    """Get detailed ZAP results for a run."""

    @jwt_required()
    def get(self, run_id):
        """Get ZAP results with filtering and pagination."""
        run = CICDRun.query.get_or_404(run_id)

        if not run.dast_results:
            return {"error": "No ZAP results available"}, 404

        results = run.dast_results.copy()
        alerts = results.get("alerts", [])

        # Apply filters
        risk_filter = request.args.getlist("risk")
        confidence_filter = request.args.getlist("confidence")
        alert_name_filter = request.args.get("alert_name")
        url_filter = request.args.get("url")
        cwe_filter = request.args.get("cwe")
        search = request.args.get("search", "").lower()

        filtered_alerts = alerts

        if risk_filter:
            filtered_alerts = [a for a in filtered_alerts if a.get("risk") in risk_filter]
        if confidence_filter:
            filtered_alerts = [a for a in filtered_alerts if a.get("confidence") in confidence_filter]
        if alert_name_filter:
            filtered_alerts = [a for a in filtered_alerts if alert_name_filter in a.get("name", "")]
        if url_filter:
            filtered_alerts = [a for a in filtered_alerts if url_filter in a.get("url", "")]
        if cwe_filter:
            filtered_alerts = [a for a in filtered_alerts if cwe_filter == str(a.get("cweid", ""))]
        if search:
            filtered_alerts = [
                a
                for a in filtered_alerts
                if (
                    search in a.get("name", "").lower()
                    or search in a.get("url", "").lower()
                    or search in a.get("description", "").lower()
                )
            ]

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        start = (page - 1) * per_page
        end = start + per_page

        paginated_alerts = filtered_alerts[start:end]

        results["alerts"] = paginated_alerts
        results["pagination"] = {
            "page": page,
            "per_page": per_page,
            "total": len(filtered_alerts),
            "pages": (len(filtered_alerts) + per_page - 1) // per_page,
        }

        return {"results": results}, 200


class CICDRunTrivy(Resource):
    """Get detailed Trivy results for a run."""

    @jwt_required()
    def get(self, run_id):
        """Get Trivy results with filtering and pagination."""
        run = CICDRun.query.get_or_404(run_id)

        if not run.trivy_results:
            return {"error": "No Trivy results available"}, 404

        results = run.trivy_results.copy()
        vulnerabilities = results.get("vulnerabilities", [])

        # Apply filters
        severity_filter = request.args.getlist("severity")
        package_filter = request.args.get("package")
        cve_filter = request.args.get("cve")
        package_type_filter = request.args.get("package_type")
        cvss_min = request.args.get("cvss_min", type=float)
        search = request.args.get("search", "").lower()

        filtered_vulns = vulnerabilities

        if severity_filter:
            filtered_vulns = [v for v in filtered_vulns if v.get("severity") in severity_filter]
        if package_filter:
            filtered_vulns = [v for v in filtered_vulns if package_filter in v.get("pkg_name", "")]
        if cve_filter:
            filtered_vulns = [v for v in filtered_vulns if cve_filter in v.get("vulnerability_id", "")]
        if package_type_filter:
            filtered_vulns = [v for v in filtered_vulns if v.get("package_type") == package_type_filter]
        if cvss_min is not None:
            filtered_vulns = [
                v
                for v in filtered_vulns
                if (
                    v.get("cvss", {}).get("v3", {}).get("score", 0) >= cvss_min
                    or v.get("cvss", {}).get("v2", {}).get("score", 0) >= cvss_min
                )
            ]
        if search:
            filtered_vulns = [
                v
                for v in filtered_vulns
                if (
                    search in v.get("vulnerability_id", "").lower()
                    or search in v.get("pkg_name", "").lower()
                    or search in v.get("description", "").lower()
                )
            ]

        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        start = (page - 1) * per_page
        end = start + per_page

        paginated_vulns = filtered_vulns[start:end]

        results["vulnerabilities"] = paginated_vulns
        results["pagination"] = {
            "page": page,
            "per_page": per_page,
            "total": len(filtered_vulns),
            "pages": (len(filtered_vulns) + per_page - 1) // per_page,
        }

        return {"results": results}, 200


class LatestSonarQubeScan(Resource):
    """Get latest SonarQube scan results."""

    @jwt_required()
    def get(self):
        """Get latest SonarQube scan with all issues."""
        run = CICDRun.query.filter(CICDRun.sast_results.isnot(None)).order_by(CICDRun.created_at.desc()).first()

        if not run:
            return {"run": None, "sast_results": None, "message": "No SonarQube scans found"}, 200

        return {"run": run.to_dict(), "sast_results": run.sast_results}, 200


class LatestZAPScan(Resource):
    """Get latest ZAP scan results."""

    @jwt_required()
    def get(self):
        """Get latest ZAP scan with all alerts."""
        run = CICDRun.query.filter(CICDRun.dast_results.isnot(None)).order_by(CICDRun.created_at.desc()).first()

        if not run:
            return {"run": None, "dast_results": None, "message": "No ZAP scans found"}, 200

        return {"run": run.to_dict(), "dast_results": run.dast_results}, 200


class LatestTrivyScan(Resource):
    """Get latest Trivy scan results."""

    @jwt_required()
    def get(self):
        """Get latest Trivy scan with all vulnerabilities."""
        run = CICDRun.query.filter(CICDRun.trivy_results.isnot(None)).order_by(CICDRun.created_at.desc()).first()

        if not run:
            return {"run": None, "trivy_results": None, "message": "No Trivy scans found"}, 200

        return {"run": run.to_dict(), "trivy_results": run.trivy_results}, 200


class TriggerSonarQubeScan(Resource):
    """Trigger SonarQube scan."""

    @jwt_required()
    def post(self):
        """Trigger a new SonarQube scan."""
        data = request.json or {}
        commit_hash = data.get("commit_hash", "manual")
        project_key = data.get("project_key")

        scanner = SecurityScanner()
        results = scanner.run_sast_scan(commit_hash, project_key)

        # Create or update run
        run = CICDRun.query.filter_by(commit_hash=commit_hash).order_by(CICDRun.created_at.desc()).first()
        if not run:
            run = CICDRun(commit_hash=commit_hash, branch=data.get("branch", "main"), status="Running")
            db.session.add(run)

        run.sast_results = results
        if results.get("status") == "completed":
            run.status = "Success" if results.get("critical", 0) == 0 else "Blocked"
            run.completed_at = datetime.utcnow()

        db.session.commit()

        emit_scan_update(run.id, "sast_progress", results)
        emit_dashboard_update("scan_completed", run.to_dict())

        return {"run_id": run.id, "results": results}, 201


class TriggerZAPScan(Resource):
    """Trigger ZAP scan (async)."""

    @jwt_required()
    def post(self):
        """Trigger a new ZAP scan."""
        data = request.json or {}
        target_url = data.get("target_url", "http://localhost")

        scanner = SecurityScanner()
        results = scanner.run_dast_scan(target_url)

        # Create run
        run = CICDRun(
            commit_hash=data.get("commit_hash", "manual"), branch=data.get("branch", "main"), status="Running"
        )
        db.session.add(run)
        db.session.commit()

        # Store initial scan state
        run.dast_results = results
        db.session.commit()

        emit_scan_update(run.id, "dast_progress", results)

        return {
            "run_id": run.id,
            "scan_id": results.get("active_scan_id"),
            "status": results.get("status"),
            "results": results,
        }, 201


class TriggerTrivyScan(Resource):
    """Trigger Trivy scan."""

    @jwt_required()
    def post(self):
        """Trigger a new Trivy scan."""
        data = request.json or {}
        image_name = data.get("image_name", "sentinal-backend:latest")

        scanner = SecurityScanner()
        results = scanner.run_trivy_scan(image_name)

        # Create or update run
        commit_hash_val = data.get("commit_hash", "manual")
        run = CICDRun.query.filter_by(commit_hash=commit_hash_val).order_by(CICDRun.created_at.desc()).first()
        if not run:
            run = CICDRun(
                commit_hash=data.get("commit_hash", "manual"), branch=data.get("branch", "main"), status="Running"
            )
            db.session.add(run)

        run.trivy_results = results
        if results.get("status") == "completed":
            run.status = "Success" if results.get("critical", 0) == 0 else "Blocked"
            run.completed_at = datetime.utcnow()

        db.session.commit()

        emit_scan_update(run.id, "trivy_progress", results)
        emit_dashboard_update("scan_completed", run.to_dict())

        return {"run_id": run.id, "results": results}, 201


class ScanStatus(Resource):
    """Get scan status."""

    @jwt_required()
    def get(self, scan_type, scan_id):
        """Get scan status by scan ID."""
        scanner = SecurityScanner()

        if scan_type == "zap":
            results = scanner.run_dast_scan(scan_id=scan_id)
            return {
                "status": results.get("status"),
                "progress": results.get("active_scan_progress", 0),
                "results": results,
            }, 200
        else:
            return {"error": "Status checking not supported for this scan type"}, 400
