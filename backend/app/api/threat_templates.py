"""Threat template API endpoints."""

from flask import request
from flask_restful import Resource
from app.core.security import jwt_required
from app import db
from app.models.threat_template import ThreatTemplate
from app.models.threat import Threat
from app.services.stride_dread_engine import STRIDEEngine
from app.services.dread_scorer import DREADScorer


class ThreatTemplateList(Resource):
    """List threat templates."""

    @jwt_required()
    def get(self):
        """Get all threat templates."""
        category = request.args.get("category")
        query = ThreatTemplate.query

        if category:
            query = query.filter_by(category=category)

        templates = query.order_by(ThreatTemplate.name).all()
        return {"templates": [t.to_dict() for t in templates]}, 200


class ThreatTemplateDetail(Resource):
    """Get threat template details."""

    @jwt_required()
    def get(self, template_id):
        """Get threat template details."""
        template = ThreatTemplate.query.get_or_404(template_id)
        return {"template": template.to_dict()}, 200


class CreateThreatFromTemplate(Resource):
    """Create a threat from a template."""

    @jwt_required()
    def post(self, template_id):
        """Create a threat from a template."""
        template = ThreatTemplate.query.get_or_404(template_id)
        data = request.json or {}

        # Use template values, allow overrides
        asset = data.get("asset") or template.asset_type or "Unknown Asset"
        flow = data.get("flow") or template.flow_template
        trust_boundary = data.get("trust_boundary") or template.trust_boundary_template

        # Use advanced STRIDE analysis
        engine = STRIDEEngine()
        advanced_analysis = engine.analyze_threat_advanced(asset, flow, trust_boundary)
        stride_categories = advanced_analysis["stride_categories"]

        # Use template DREAD scores or auto-score
        dread_scorer = DREADScorer()
        if template.default_dread_scores:
            dread_scores = template.default_dread_scores
        else:
            dread_suggestions = dread_scorer.suggest_dread_scores(asset, flow, trust_boundary)
            dread_scores = dread_suggestions["suggested_scores"]

        # Calculate risk level
        total_score = sum(dread_scores.values()) / 5.0
        risk_level = "High" if total_score > 7 else "Medium" if total_score > 4 else "Low"

        # Get mitigations
        mitigation = template.default_mitigation or engine.get_mitigation_recommendations(stride_categories, risk_level)

        # Create threat
        threat = Threat(
            asset=asset,
            flow=flow,
            trust_boundary=trust_boundary,
            stride_categories=stride_categories,
            dread_score=dread_scores,
            risk_level=risk_level,
            mitigation=mitigation,
        )

        db.session.add(threat)
        db.session.commit()

        return {
            "threat": threat.to_dict(),
            "analysis": {
                "stride_categories": stride_categories,
                "dread_score": total_score,
                "risk_level": risk_level,
                "mitigation": mitigation,
            },
        }, 201
