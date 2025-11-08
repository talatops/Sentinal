"""Requirements management API endpoints."""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from app.core.security import jwt_required
from marshmallow import Schema, fields, ValidationError, validate
from app import db
from app.models.requirement import Requirement, SecurityControl
from app.core.security import admin_required
import csv
import io


class RequirementSchema(Schema):
    """Schema for requirement."""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=5000))
    security_controls = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))
    status = fields.Str(validate=validate.OneOf(['Draft', 'Review', 'Approved', 'Implemented']))
    owasp_asvs_level = fields.Str(validate=validate.OneOf(['Level 1', 'Level 2', 'Level 3']))


class RequirementList(Resource):
    """Requirements list endpoint."""
    
    @jwt_required()
    def get(self):
        """Get all requirements."""
        requirements = Requirement.query.order_by(Requirement.created_at.desc()).all()
        return {'requirements': [req.to_dict() for req in requirements]}, 200
    
    @jwt_required()
    def post(self):
        """Create a new requirement."""
        schema = RequirementSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            return {'errors': err.messages}, 400
        
        # Ensure at least one security control
        if not data.get('security_controls'):
            return {'error': 'At least one security control is required'}, 400
        
        user_id = get_jwt_identity()
        
        # Create requirement
        requirement = Requirement(
            title=data['title'],
            description=data.get('description'),
            security_controls=[ctrl.get('id') or ctrl.get('name') for ctrl in data['security_controls']],
            created_by=user_id,
            status=data.get('status', 'Draft'),
            owasp_asvs_level=data.get('owasp_asvs_level')
        )
        
        db.session.add(requirement)
        db.session.flush()
        
        # Create security controls
        for ctrl_data in data['security_controls']:
            control = SecurityControl(
                name=ctrl_data.get('name', ''),
                description=ctrl_data.get('description'),
                owasp_asvs_level=ctrl_data.get('owasp_asvs_level'),
                requirement_id=requirement.id
            )
            db.session.add(control)
        
        db.session.commit()
        
        return {'requirement': requirement.to_dict()}, 201


class RequirementDetail(Resource):
    """Requirement detail endpoint."""
    
    @jwt_required()
    def get(self, req_id):
        """Get requirement details."""
        requirement = Requirement.query.get_or_404(req_id)
        return {'requirement': requirement.to_dict()}, 200
    
    @jwt_required()
    def put(self, req_id):
        """Update requirement."""
        requirement = Requirement.query.get_or_404(req_id)
        user_id = get_jwt_identity()
        
        # Check permissions
        if requirement.created_by != user_id:
            from app.models.user import User
            user = User.query.get(user_id)
            if user.role != 'Admin':
                return {'error': 'Insufficient permissions'}, 403
        
        data = request.json
        if 'title' in data:
            requirement.title = data['title']
        if 'description' in data:
            requirement.description = data['description']
        if 'status' in data:
            requirement.status = data['status']
        if 'owasp_asvs_level' in data:
            requirement.owasp_asvs_level = data['owasp_asvs_level']
        
        db.session.commit()
        return {'requirement': requirement.to_dict()}, 200
    
    @jwt_required()
    def delete(self, req_id):
        """Delete requirement."""
        requirement = Requirement.query.get_or_404(req_id)
        user_id = get_jwt_identity()
        
        # Check permissions
        if requirement.created_by != user_id:
            from app.models.user import User
            user = User.query.get(user_id)
            if user.role != 'Admin':
                return {'error': 'Insufficient permissions'}, 403
        
        db.session.delete(requirement)
        db.session.commit()
        return {'message': 'Requirement deleted successfully'}, 200


class SecurityControlList(Resource):
    """Security controls for a requirement."""
    
    @jwt_required()
    def get(self, req_id):
        """Get security controls for a requirement."""
        requirement = Requirement.query.get_or_404(req_id)
        controls = SecurityControl.query.filter_by(requirement_id=req_id).all()
        return {'controls': [ctrl.to_dict() for ctrl in controls]}, 200
    
    @jwt_required()
    def post(self, req_id):
        """Add security control to requirement."""
        requirement = Requirement.query.get_or_404(req_id)
        
        data = request.json
        control = SecurityControl(
            name=data.get('name', ''),
            description=data.get('description'),
            owasp_asvs_level=data.get('owasp_asvs_level'),
            requirement_id=req_id
        )
        
        db.session.add(control)
        db.session.commit()
        
        return {'control': control.to_dict()}, 201


class RequirementExport(Resource):
    """Export requirements."""
    
    @jwt_required()
    def get(self):
        """Export requirements as CSV or JSON."""
        format_type = request.args.get('format', 'json')
        requirements = Requirement.query.all()
        
        if format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Title', 'Description', 'Status', 'OWASP ASVS Level', 'Security Controls', 'Created At'])
            
            for req in requirements:
                controls = ', '.join([ctrl.name for ctrl in req.controls])
                writer.writerow([
                    req.id,
                    req.title,
                    req.description or '',
                    req.status,
                    req.owasp_asvs_level or '',
                    controls,
                    req.created_at.isoformat() if req.created_at else ''
                ])
            
            return jsonify({
                'data': output.getvalue(),
                'format': 'csv'
            })
        else:
            return {'requirements': [req.to_dict() for req in requirements]}, 200


class ComplianceDashboard(Resource):
    """Compliance dashboard endpoint."""
    
    @admin_required
    def get(self):
        """Get compliance dashboard data."""
        requirements = Requirement.query.all()
        
        total_requirements = len(requirements)
        requirements_with_controls = sum(1 for req in requirements if req.controls.count() > 0)
        compliance_rate = (requirements_with_controls / total_requirements * 100) if total_requirements > 0 else 0
        
        # OWASP ASVS level distribution
        level_distribution = {
            'Level 1': sum(1 for req in requirements if req.owasp_asvs_level == 'Level 1'),
            'Level 2': sum(1 for req in requirements if req.owasp_asvs_level == 'Level 2'),
            'Level 3': sum(1 for req in requirements if req.owasp_asvs_level == 'Level 3'),
            'Not Specified': sum(1 for req in requirements if not req.owasp_asvs_level)
        }
        
        # Status distribution
        status_distribution = {}
        for req in requirements:
            status_distribution[req.status] = status_distribution.get(req.status, 0) + 1
        
        return {
            'total_requirements': total_requirements,
            'requirements_with_controls': requirements_with_controls,
            'compliance_rate': round(compliance_rate, 2),
            'owasp_asvs_distribution': level_distribution,
            'status_distribution': status_distribution
        }, 200

