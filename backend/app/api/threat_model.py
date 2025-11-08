"""Threat modeling API endpoints."""
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from app.core.security import jwt_required
from marshmallow import Schema, fields, ValidationError, validate
from app import db
from app.models.threat import Threat
from app.models.threat_vulnerability import ThreatVulnerability
from app.services.stride_dread_engine import STRIDEEngine
from app.services.dread_scorer import DREADScorer
from app.services.threat_similarity import ThreatSimilarityService


class ThreatAnalyzeSchema(Schema):
    """Schema for threat analysis."""
    asset = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    flow = fields.Str(required=True)
    trust_boundary = fields.Str(validate=validate.Length(max=200), allow_none=True)
    auto_score = fields.Bool(missing=False)
    damage = fields.Int(validate=validate.Range(min=0, max=10), allow_none=True)
    reproducibility = fields.Int(validate=validate.Range(min=0, max=10), allow_none=True)
    exploitability = fields.Int(validate=validate.Range(min=0, max=10), allow_none=True)
    affected_users = fields.Int(validate=validate.Range(min=0, max=10), allow_none=True)
    discoverability = fields.Int(validate=validate.Range(min=0, max=10), allow_none=True)


class ThreatAnalyze(Resource):
    """Threat analysis endpoint."""
    
    @jwt_required()
    def post(self):
        """Analyze a threat using STRIDE/DREAD."""
        schema = ThreatAnalyzeSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        auto_score = data.get('auto_score', False)
        
        # Use advanced STRIDE engine to analyze
        engine = STRIDEEngine()
        advanced_analysis = engine.analyze_threat_advanced(
            data['asset'],
            data['flow'],
            data.get('trust_boundary')
        )
        stride_categories = advanced_analysis['stride_categories']
        
        # Handle DREAD scoring
        dread_scorer = DREADScorer()
        user_scores = None
        
        if not auto_score:
            # Manual scoring - validate all scores are provided
            if not all(data.get(key) is not None for key in ['damage', 'reproducibility', 'exploitability', 'affected_users', 'discoverability']):
                return {'errors': {'dread_scores': 'All DREAD scores are required when auto_score is false'}}, 400
            
            dread_scores = {
                'damage': data['damage'],
                'reproducibility': data['reproducibility'],
                'exploitability': data['exploitability'],
                'affected_users': data['affected_users'],
                'discoverability': data['discoverability']
            }
            dread_suggestions = None
        else:
            # Auto-scoring - get suggestions
            user_scores = {}
            if data.get('damage') is not None:
                user_scores['damage'] = data['damage']
            if data.get('reproducibility') is not None:
                user_scores['reproducibility'] = data['reproducibility']
            if data.get('exploitability') is not None:
                user_scores['exploitability'] = data['exploitability']
            if data.get('affected_users') is not None:
                user_scores['affected_users'] = data['affected_users']
            if data.get('discoverability') is not None:
                user_scores['discoverability'] = data['discoverability']
            
            dread_suggestions = dread_scorer.suggest_dread_scores(
                data['asset'],
                data['flow'],
                data.get('trust_boundary'),
                user_scores if user_scores else None
            )
            dread_scores = dread_suggestions['suggested_scores']
        
        # Calculate total score and risk level
        total_score = sum(dread_scores.values()) / 5.0
        risk_level = 'High' if total_score > 7 else 'Medium' if total_score > 4 else 'Low'
        
        # Get mitigation recommendations
        mitigation = engine.get_mitigation_recommendations(stride_categories, risk_level)
        
        # Try to get enhanced mitigations if available
        enhanced_mitigations = None
        try:
            from app.services.enhanced_mitigations import EnhancedMitigationEngine
            enhanced_engine = EnhancedMitigationEngine()
            enhanced_mitigations = enhanced_engine.get_mitigations(
                stride_categories,
                risk_level,
                advanced_analysis.get('primary_pattern'),
                None,
                advanced_analysis.get('component_types', [])
            )
        except ImportError:
            pass
        
        # Create threat record
        threat = Threat(
            asset=data['asset'],
            flow=data['flow'],
            trust_boundary=data.get('trust_boundary'),
            stride_categories=stride_categories,
            dread_score=dread_scores,
            risk_level=risk_level,
            mitigation=mitigation
        )
        
        db.session.add(threat)
        db.session.commit()
        
        response = {
            'threat': threat.to_dict(),
            'analysis': {
                'stride_categories': stride_categories,
                'stride_confidence': advanced_analysis.get('stride_confidence', {}),
                'component_types': advanced_analysis.get('component_types', []),
                'matched_patterns': advanced_analysis.get('matched_patterns', []),
                'primary_pattern': advanced_analysis.get('primary_pattern'),
                'pattern_confidence': advanced_analysis.get('pattern_confidence', 0.0),
                'dread_score': total_score,
                'risk_level': risk_level,
                'mitigation': mitigation
            }
        }
        
        # Include DREAD suggestions if auto-scoring was used
        if auto_score and dread_suggestions:
            response['analysis']['dread_suggestions'] = {
                'suggested_scores': dread_suggestions['suggested_scores'],
                'confidence': dread_suggestions['confidence'],
                'explanations': dread_suggestions['explanations']
            }
        
        # Include enhanced mitigations if available
        if enhanced_mitigations:
            response['analysis']['enhanced_mitigations'] = enhanced_mitigations
        
        return response, 201


class ThreatList(Resource):
    """List all threats."""
    
    @jwt_required()
    def get(self):
        """Get all threats."""
        threats = Threat.query.order_by(Threat.created_at.desc()).all()
        return {'threats': [threat.to_dict() for threat in threats]}, 200


class ThreatDetail(Resource):
    """Threat detail endpoint."""
    
    @jwt_required()
    def get(self, threat_id):
        """Get threat details."""
        threat = Threat.query.get_or_404(threat_id)
        return {'threat': threat.to_dict()}, 200
    
    @jwt_required()
    def put(self, threat_id):
        """Update threat."""
        threat = Threat.query.get_or_404(threat_id)
        
        data = request.json
        if 'mitigation' in data:
            threat.mitigation = data['mitigation']
        if 'risk_level' in data:
            threat.risk_level = data['risk_level']
        
        db.session.commit()
        return {'threat': threat.to_dict()}, 200
    
    @jwt_required()
    def delete(self, threat_id):
        """Delete threat."""
        threat = Threat.query.get_or_404(threat_id)
        db.session.delete(threat)
        db.session.commit()
        return {'message': 'Threat deleted successfully'}, 200


class ThreatVulnerabilities(Resource):
    """Get vulnerabilities linked to a threat."""
    
    @jwt_required()
    def get(self, threat_id):
        """Get all vulnerabilities linked to a threat."""
        threat = Threat.query.get_or_404(threat_id)
        vulnerabilities = ThreatVulnerability.query.filter_by(threat_id=threat_id).all()
        return {
            'threat_id': threat_id,
            'vulnerabilities': [v.to_dict() for v in vulnerabilities]
        }, 200


class LinkVulnerability(Resource):
    """Link a vulnerability to a threat."""
    
    @jwt_required()
    def post(self, threat_id):
        """Link a vulnerability to a threat."""
        threat = Threat.query.get_or_404(threat_id)
        
        data = request.json
        vulnerability_type = data.get('vulnerability_type')
        vulnerability_id = data.get('vulnerability_id')
        scan_run_id = data.get('scan_run_id')
        severity = data.get('severity')
        vulnerability_data = data.get('vulnerability_data')
        
        if not vulnerability_type or not vulnerability_id:
            return {'error': 'vulnerability_type and vulnerability_id are required'}, 400
        
        # Check if link already exists
        existing = ThreatVulnerability.query.filter_by(
            threat_id=threat_id,
            vulnerability_type=vulnerability_type,
            vulnerability_id=vulnerability_id
        ).first()
        
        if existing:
            return {'error': 'Vulnerability already linked to this threat'}, 400
        
        # Create link
        threat_vuln = ThreatVulnerability(
            threat_id=threat_id,
            vulnerability_type=vulnerability_type,
            vulnerability_id=vulnerability_id,
            scan_run_id=scan_run_id,
            severity=severity,
            vulnerability_data=vulnerability_data,
            status='linked'
        )
        
        db.session.add(threat_vuln)
        db.session.commit()
        
        return {'vulnerability': threat_vuln.to_dict()}, 201


class ThreatsWithVulnerabilities(Resource):
    """Get threats that have linked vulnerabilities."""
    
    @jwt_required()
    def get(self):
        """Get all threats with linked vulnerabilities."""
        # Get threats that have at least one vulnerability
        threats = Threat.query.join(ThreatVulnerability).distinct().all()
        
        result = []
        for threat in threats:
            threat_dict = threat.to_dict()
            vulnerabilities = ThreatVulnerability.query.filter_by(threat_id=threat.id).all()
            threat_dict['vulnerabilities'] = [v.to_dict() for v in vulnerabilities]
            threat_dict['vulnerability_count'] = len(vulnerabilities)
            result.append(threat_dict)
        
        return {'threats': result}, 200


class UpdateVulnerabilityStatus(Resource):
    """Update vulnerability status."""
    
    @jwt_required()
    def put(self, vulnerability_id):
        """Update vulnerability status."""
        threat_vuln = ThreatVulnerability.query.get_or_404(vulnerability_id)
        
        data = request.json
        status = data.get('status')
        
        if status not in ['linked', 'resolved', 'false_positive']:
            return {'error': 'Invalid status. Must be: linked, resolved, or false_positive'}, 400
        
        threat_vuln.status = status
        db.session.commit()
        
        return {'vulnerability': threat_vuln.to_dict()}, 200


class ThreatSimilar(Resource):
    """Get similar threats."""
    
    @jwt_required()
    def get(self, threat_id):
        """Get threats similar to the specified threat."""
        similarity_service = ThreatSimilarityService()
        similar_threats = similarity_service.find_similar_threats(threat_id, limit=5)
        return {'similar_threats': similar_threats}, 200

