"""CI/CD run model for tracking pipeline executions."""

from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSONB


class CICDRun(db.Model):
    """CI/CD run model for tracking pipeline executions."""

    __tablename__ = "ci_cd_runs"

    id = db.Column(db.Integer, primary_key=True)
    commit_hash = db.Column(db.String(40), nullable=False, index=True)
    branch = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Running")  # Running, Success, Failed, Blocked
    sast_results = db.Column(JSONB, nullable=True)  # SonarQube results
    dast_results = db.Column(JSONB, nullable=True)  # OWASP ZAP results
    trivy_results = db.Column(JSONB, nullable=True)  # Trivy scan results
    lint_results = db.Column(JSONB, nullable=True)  # Linting results
    test_results = db.Column(JSONB, nullable=True)  # Test results
    critical_vulnerabilities = db.Column(db.Integer, default=0, nullable=False)
    total_vulnerabilities = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<CICDRun {self.commit_hash[:8]}>"

    def to_dict(self):
        """Convert CI/CD run to dictionary."""
        return {
            "id": self.id,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "status": self.status,
            "sast_results": self.sast_results,
            "dast_results": self.dast_results,
            "trivy_results": self.trivy_results,
            "lint_results": self.lint_results,
            "test_results": self.test_results,
            "critical_vulnerabilities": self.critical_vulnerabilities,
            "total_vulnerabilities": self.total_vulnerabilities,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
