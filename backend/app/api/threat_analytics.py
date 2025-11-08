"""Threat analytics API endpoints."""
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from app.core.security import jwt_required
from app import db
from app.models.threat import Threat
from app.models.threat_vulnerability import ThreatVulnerability
from sqlalchemy import func
from datetime import datetime, timedelta


class ThreatAnalytics(Resource):
    """Threat analytics endpoint."""
    
    @jwt_required()
    def get(self):
        """Get threat analytics and statistics."""
        # Total threats
        total_threats = Threat.query.count()
        
        # Threats by risk level
        risk_level_stats = db.session.query(
            Threat.risk_level,
            func.count(Threat.id).label('count')
        ).group_by(Threat.risk_level).all()
        
        risk_levels = {level: count for level, count in risk_level_stats}
        
        # STRIDE category distribution
        stride_stats = {}
        threats = Threat.query.all()
        for threat in threats:
            categories = threat.stride_categories or []
            for category in categories:
                stride_stats[category] = stride_stats.get(category, 0) + 1
        
        # Most common assets
        asset_stats = db.session.query(
            Threat.asset,
            func.count(Threat.id).label('count')
        ).group_by(Threat.asset).order_by(func.count(Threat.id).desc()).limit(10).all()
        
        most_vulnerable_assets = [{'asset': asset, 'count': count} for asset, count in asset_stats]
        
        # Threats with vulnerabilities vs theoretical
        threats_with_vulns = db.session.query(func.count(func.distinct(ThreatVulnerability.threat_id))).scalar() or 0
        theoretical_threats = total_threats - threats_with_vulns
        
        # Average DREAD scores
        avg_dread = db.session.query(
            func.avg(func.cast(Threat.dread_score['damage'], db.Integer)).label('avg_damage'),
            func.avg(func.cast(Threat.dread_score['reproducibility'], db.Integer)).label('avg_reproducibility'),
            func.avg(func.cast(Threat.dread_score['exploitability'], db.Integer)).label('avg_exploitability'),
            func.avg(func.cast(Threat.dread_score['affected_users'], db.Integer)).label('avg_affected_users'),
            func.avg(func.cast(Threat.dread_score['discoverability'], db.Integer)).label('avg_discoverability'),
        ).first()
        
        avg_scores = {
            'damage': round(float(avg_dread.avg_damage or 0), 2),
            'reproducibility': round(float(avg_dread.avg_reproducibility or 0), 2),
            'exploitability': round(float(avg_dread.avg_exploitability or 0), 2),
            'affected_users': round(float(avg_dread.avg_affected_users or 0), 2),
            'discoverability': round(float(avg_dread.avg_discoverability or 0), 2),
        }
        
        # Threat trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_threats = Threat.query.filter(Threat.created_at >= thirty_days_ago).all()
        
        # Group by date
        threat_trends = {}
        for threat in recent_threats:
            date_key = threat.created_at.date().isoformat()
            threat_trends[date_key] = threat_trends.get(date_key, 0) + 1
        
        # Vulnerability statistics
        vuln_stats = db.session.query(
            ThreatVulnerability.vulnerability_type,
            func.count(ThreatVulnerability.id).label('count')
        ).group_by(ThreatVulnerability.vulnerability_type).all()
        
        vulnerability_types = {vtype: count for vtype, count in vuln_stats}
        
        # Resolution rate
        resolved_vulns = ThreatVulnerability.query.filter_by(status='resolved').count()
        total_vulns = ThreatVulnerability.query.count()
        resolution_rate = (resolved_vulns / total_vulns * 100) if total_vulns > 0 else 0
        
        return {
            'summary': {
                'total_threats': total_threats,
                'threats_with_vulnerabilities': threats_with_vulns,
                'theoretical_threats': theoretical_threats,
                'resolution_rate': round(resolution_rate, 2)
            },
            'risk_levels': risk_levels,
            'stride_distribution': stride_stats,
            'most_vulnerable_assets': most_vulnerable_assets,
            'average_dread_scores': avg_scores,
            'threat_trends': threat_trends,
            'vulnerability_types': vulnerability_types
        }, 200

