"""Flask application initialization."""

from flask import Flask, jsonify
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler

# Fix eventlet DNS resolution - patch after eventlet imports
# We'll patch the DNS resolver in run.py after socketio is initialized

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")


def create_app(config_name="production"):
    """Application factory pattern."""
    app = Flask(__name__)

    # Load configuration
    if config_name == "development":
        app.config.from_object("app.core.config.DevelopmentConfig")
    elif config_name == "testing":
        app.config.from_object("app.core.config.TestingConfig")
    else:
        app.config.from_object("app.core.config.ProductionConfig")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization header is missing"}), 401

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token is not fresh"}), 401

    # Security headers
    Talisman(
        app,
        force_https=False,  # Set to True in production with HTTPS
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,
        content_security_policy={
            "default-src": "'self'",
            "script-src": "'self' 'unsafe-inline'",
            "style-src": "'self' 'unsafe-inline'",
        },
    )

    # Rate limiting
    limiter.init_app(app)

    # Configure logging
    if not app.debug:
        file_handler = RotatingFileHandler("logs/sentinal.log", maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Sentinal startup")

    # Health check route
    @app.route("/api/health")
    def health():
        return {"status": "healthy", "service": "sentinal-api"}, 200

    # Root API route
    @app.route("/api")
    def api_root():
        return {
            "message": "Project Sentinel API",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth",
                "threats": "/api/threats",
                "requirements": "/api/requirements",
                "cicd": "/api/cicd",
            },
        }, 200

    # Register blueprints/API routes
    from app.api import auth, threat_model, requirements, cicd, api_tokens
    from app.api.websocket import register_websocket_handlers
    from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError
    from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

    @app.errorhandler(NoAuthorizationError)
    @app.errorhandler(JWTDecodeError)
    @app.errorhandler(ExpiredSignatureError)
    @app.errorhandler(InvalidTokenError)
    def handle_jwt_error(e):
        """Handle JWT exceptions and return proper 401 responses."""
        error_message = str(e)
        if "Missing Authorization Header" in error_message or "Authorization header is missing" in error_message:
            return jsonify({"error": "Authorization header is missing"}), 401
        elif "expired" in error_message.lower() or isinstance(e, ExpiredSignatureError):
            return jsonify({"error": "Token has expired"}), 401
        elif "invalid" in error_message.lower() or isinstance(e, (JWTDecodeError, InvalidTokenError)):
            return jsonify({"error": "Invalid token"}), 401
        else:
            return jsonify({"error": "Authentication required"}), 401

    api = Api(app, prefix="/api")

    # Authentication routes
    api.add_resource(auth.Register, "/auth/register")
    api.add_resource(auth.Login, "/auth/login")
    api.add_resource(auth.GitHubAuth, "/auth/github")
    api.add_resource(auth.GitHubCallback, "/auth/github/callback")
    api.add_resource(auth.RefreshToken, "/auth/refresh")
    api.add_resource(auth.Logout, "/auth/logout")
    api.add_resource(auth.UserProfile, "/auth/profile")

    # API Token management routes
    api.add_resource(api_tokens.CreateAPIToken, "/auth/api-tokens")
    api.add_resource(api_tokens.ListAPITokens, "/auth/api-tokens")
    api.add_resource(api_tokens.RevokeAPIToken, "/auth/api-tokens/<int:token_id>/revoke")

    # Threat modeling routes
    api.add_resource(threat_model.ThreatAnalyze, "/threats/analyze")
    api.add_resource(threat_model.ThreatList, "/threats")
    api.add_resource(threat_model.ThreatDetail, "/threats/<int:threat_id>")
    api.add_resource(threat_model.ThreatVulnerabilities, "/threats/<int:threat_id>/vulnerabilities")
    api.add_resource(threat_model.LinkVulnerability, "/threats/<int:threat_id>/link-vulnerability")
    api.add_resource(threat_model.ThreatsWithVulnerabilities, "/threats/with-vulnerabilities")
    api.add_resource(threat_model.UpdateVulnerabilityStatus, "/threats/vulnerabilities/<int:vulnerability_id>/status")
    api.add_resource(threat_model.ThreatSimilar, "/threats/<int:threat_id>/similar")

    # Threat analytics routes
    from app.api import threat_analytics

    api.add_resource(threat_analytics.ThreatAnalytics, "/threats/analytics")

    # Threat template routes
    from app.api import threat_templates

    api.add_resource(threat_templates.ThreatTemplateList, "/threats/templates")
    api.add_resource(threat_templates.ThreatTemplateDetail, "/threats/templates/<int:template_id>")
    api.add_resource(threat_templates.CreateThreatFromTemplate, "/threats/templates/<int:template_id>/create-threat")

    # Requirements routes
    api.add_resource(requirements.RequirementList, "/requirements")
    api.add_resource(requirements.RequirementDetail, "/requirements/<int:req_id>")
    api.add_resource(requirements.SecurityControlList, "/requirements/<int:req_id>/controls")
    api.add_resource(requirements.RequirementExport, "/requirements/export")
    api.add_resource(requirements.ComplianceDashboard, "/requirements/compliance")

    # CI/CD routes
    api.add_resource(cicd.CICDRunList, "/cicd/runs")
    api.add_resource(cicd.CICDRunDetail, "/cicd/runs/<int:run_id>")
    api.add_resource(cicd.CICDTrigger, "/cicd/trigger")
    api.add_resource(cicd.CICDDashboard, "/cicd/dashboard")

    # Detailed scan results endpoints
    api.add_resource(cicd.CICDRunSAST, "/cicd/runs/<int:run_id>/sast")
    api.add_resource(cicd.CICDRunDAST, "/cicd/runs/<int:run_id>/dast")
    api.add_resource(cicd.CICDRunTrivy, "/cicd/runs/<int:run_id>/trivy")

    # Latest scan endpoints
    api.add_resource(cicd.LatestSonarQubeScan, "/cicd/scans/sonarqube/latest")
    api.add_resource(cicd.LatestZAPScan, "/cicd/scans/zap/latest")
    api.add_resource(cicd.LatestTrivyScan, "/cicd/scans/trivy/latest")

    # Trigger scan endpoints
    api.add_resource(cicd.TriggerSonarQubeScan, "/cicd/scans/sonarqube/trigger")
    api.add_resource(cicd.TriggerZAPScan, "/cicd/scans/zap/trigger")
    api.add_resource(cicd.TriggerTrivyScan, "/cicd/scans/trivy/trigger")

    # Scan status endpoint
    api.add_resource(cicd.ScanStatus, "/cicd/scans/<scan_type>/status/<scan_id>")

    # Webhook routes (no JWT, uses API token)
    api.add_resource(cicd.CICDWebhook, "/cicd/webhook/<scan_type>")

    # Register WebSocket handlers
    register_websocket_handlers(socketio)

    return app
