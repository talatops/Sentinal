"""Add threat_templates table and seed initial templates.

Revision ID: 004_threat_templates
Revises: 003_threat_vulnerabilities
Create Date: 2024-01-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '004_threat_templates'
down_revision = '003_threat_vulnerabilities'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'threat_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('asset_type', sa.String(length=100), nullable=True),
        sa.Column('flow_template', sa.Text(), nullable=False),
        sa.Column('trust_boundary_template', sa.String(length=200), nullable=True),
        sa.Column('stride_categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('default_dread_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('default_mitigation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threat_templates_category'), 'threat_templates', ['category'], unique=False)
    
    # Seed initial templates
    from datetime import datetime
    import json
    
    templates = [
        {
            'name': 'SQL Injection in API Endpoint',
            'description': 'User input is directly concatenated into SQL queries without parameterization',
            'category': 'api',
            'asset_type': 'api',
            'flow_template': 'User submits input via POST request to API endpoint. Backend receives input and constructs SQL query by concatenating user input directly into query string. Query is executed against PostgreSQL database without parameterization.',
            'trust_boundary_template': 'External Network to Internal Database',
            'stride_categories': json.dumps(['Tampering', 'Information Disclosure', 'Elevation of Privilege']),
            'default_dread_scores': json.dumps({'damage': 9, 'reproducibility': 8, 'exploitability': 9, 'affected_users': 10, 'discoverability': 7}),
            'default_mitigation': 'Use parameterized queries or prepared statements. Implement input validation and sanitization. Apply principle of least privilege to database user. Enable SQL injection protection in WAF.',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Cross-Site Scripting (XSS) in User-Generated Content',
            'description': 'User input is rendered in HTML without proper sanitization',
            'category': 'web_app',
            'asset_type': 'frontend',
            'flow_template': 'User submits comment or content through web form. Frontend receives input and renders it directly in HTML without sanitization. Malicious JavaScript code executes in victim browser.',
            'trust_boundary_template': 'User Browser to Web Server',
            'stride_categories': json.dumps(['Tampering', 'Information Disclosure']),
            'default_dread_scores': json.dumps({'damage': 6, 'reproducibility': 7, 'exploitability': 6, 'affected_users': 7, 'discoverability': 5}),
            'default_mitigation': 'Implement output encoding (HTML entity encoding, JavaScript encoding). Use Content Security Policy (CSP). Validate and sanitize all user input. Use framework built-in XSS protection.',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Authentication Bypass Vulnerability',
            'description': 'Weak or missing authentication allows unauthorized access',
            'category': 'auth',
            'asset_type': 'authentication',
            'flow_template': 'User attempts to access protected resource. Authentication check is missing or can be bypassed. User gains unauthorized access to protected data or functionality.',
            'trust_boundary_template': 'Unauthenticated to Authenticated Zone',
            'stride_categories': json.dumps(['Spoofing', 'Elevation of Privilege']),
            'default_dread_scores': json.dumps({'damage': 10, 'reproducibility': 8, 'exploitability': 9, 'affected_users': 10, 'discoverability': 6}),
            'default_mitigation': 'Implement strong authentication mechanisms. Use multi-factor authentication (MFA). Enforce session management. Implement proper authorization checks. Use secure password storage (bcrypt, Argon2).',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Insecure Direct Object Reference (IDOR)',
            'description': 'User can access resources by manipulating object identifiers',
            'category': 'api',
            'asset_type': 'api',
            'flow_template': 'User requests resource using predictable ID in URL. Backend does not verify user has permission to access that specific resource. User can access other users data by changing ID.',
            'trust_boundary_template': 'User Session to Resource Access',
            'stride_categories': json.dumps(['Elevation of Privilege', 'Information Disclosure']),
            'default_dread_scores': json.dumps({'damage': 8, 'reproducibility': 9, 'exploitability': 8, 'affected_users': 8, 'discoverability': 7}),
            'default_mitigation': 'Implement proper authorization checks for each resource access. Use indirect object references (map user-facing IDs to internal IDs). Implement access control lists (ACLs). Log all resource access attempts.',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Cross-Site Request Forgery (CSRF)',
            'description': 'State-changing requests can be forged from external sites',
            'category': 'web_app',
            'asset_type': 'frontend',
            'flow_template': 'Attacker creates malicious website that submits form to target application. Victim visits attacker site while authenticated to target. Form submission executes state-changing action without user consent.',
            'trust_boundary_template': 'External Site to Application',
            'stride_categories': json.dumps(['Tampering', 'Repudiation']),
            'default_dread_scores': json.dumps({'damage': 7, 'reproducibility': 8, 'exploitability': 7, 'affected_users': 7, 'discoverability': 6}),
            'default_mitigation': 'Implement CSRF tokens for all state-changing requests. Use SameSite cookie attribute. Verify Origin/Referer headers. Require re-authentication for sensitive operations.',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Session Management Vulnerability',
            'description': 'Weak session tokens or improper session handling',
            'category': 'auth',
            'asset_type': 'authentication',
            'flow_template': 'User authenticates and receives session token. Session token is predictable or not properly invalidated. Attacker can hijack session or perform session fixation attack.',
            'trust_boundary_template': 'Session Storage to Application',
            'stride_categories': json.dumps(['Spoofing', 'Tampering']),
            'default_dread_scores': json.dumps({'damage': 8, 'reproducibility': 7, 'exploitability': 7, 'affected_users': 8, 'discoverability': 6}),
            'default_mitigation': 'Use cryptographically secure random session tokens. Implement proper session expiration. Regenerate session ID after login. Use secure cookie flags (HttpOnly, Secure, SameSite). Implement session timeout.',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Path Traversal Attack',
            'description': 'Unsanitized file paths allow access to arbitrary files',
            'category': 'api',
            'asset_type': 'file_system',
            'flow_template': 'User provides file path in request. Backend reads file without validating path. User can access files outside intended directory using ../ sequences.',
            'trust_boundary_template': 'User Input to File System',
            'stride_categories': json.dumps(['Information Disclosure', 'Tampering']),
            'default_dread_scores': json.dumps({'damage': 7, 'reproducibility': 8, 'exploitability': 7, 'affected_users': 6, 'discoverability': 5}),
            'default_mitigation': 'Validate and sanitize file paths. Use whitelist of allowed directories. Use chroot or similar isolation. Implement proper access controls. Log all file access attempts.',
            'created_at': datetime.utcnow()
        },
        {
            'name': 'Command Injection',
            'description': 'User input is executed as system commands',
            'category': 'api',
            'asset_type': 'backend',
            'flow_template': 'User provides input that is passed to system command. Input is not sanitized. Attacker can execute arbitrary commands on server.',
            'trust_boundary_template': 'User Input to System Shell',
            'stride_categories': json.dumps(['Tampering', 'Elevation of Privilege', 'Denial of Service']),
            'default_dread_scores': json.dumps({'damage': 9, 'reproducibility': 8, 'exploitability': 7, 'affected_users': 8, 'discoverability': 6}),
            'default_mitigation': 'Avoid executing system commands with user input. Use safe APIs instead of shell commands. If necessary, use whitelist validation. Run with least privilege. Implement input validation and sanitization.',
            'created_at': datetime.utcnow()
        }
    ]
    
    # Insert templates
    for template in templates:
        op.execute(
            f"""
            INSERT INTO threat_templates (name, description, category, asset_type, flow_template, trust_boundary_template, stride_categories, default_dread_scores, default_mitigation, created_at)
            VALUES (
                '{template['name'].replace("'", "''")}',
                '{template['description'].replace("'", "''")}',
                '{template['category']}',
                '{template['asset_type']}',
                '{template['flow_template'].replace("'", "''")}',
                '{template['trust_boundary_template']}',
                '{template['stride_categories']}',
                '{template['default_dread_scores']}',
                '{template['default_mitigation'].replace("'", "''")}',
                '{template['created_at'].isoformat()}'
            )
            """
        )


def downgrade():
    op.drop_index(op.f('ix_threat_templates_category'), table_name='threat_templates')
    op.drop_table('threat_templates')

