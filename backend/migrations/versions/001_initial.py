"""Initial database migration."""
"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=80), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('github_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("role IN ('Admin', 'Developer')", name='check_role')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_github_id'), 'users', ['github_id'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create requirements table
    op.create_table(
        'requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('security_controls', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('owasp_asvs_level', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create security_controls table
    op.create_table(
        'security_controls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owasp_asvs_level', sa.String(length=20), nullable=True),
        sa.Column('requirement_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['requirement_id'], ['requirements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create threats table
    op.create_table(
        'threats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset', sa.String(length=200), nullable=False),
        sa.Column('flow', sa.Text(), nullable=False),
        sa.Column('trust_boundary', sa.String(length=200), nullable=True),
        sa.Column('stride_categories', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('dread_score', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('mitigation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_threats_created_at'), 'threats', ['created_at'], unique=False)
    
    # Create ci_cd_runs table
    op.create_table(
        'ci_cd_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('commit_hash', sa.String(length=40), nullable=False),
        sa.Column('branch', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('sast_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dast_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('trivy_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('lint_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('test_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('critical_vulnerabilities', sa.Integer(), nullable=False),
        sa.Column('total_vulnerabilities', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ci_cd_runs_commit_hash'), 'ci_cd_runs', ['commit_hash'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ci_cd_runs_commit_hash'), table_name='ci_cd_runs')
    op.drop_table('ci_cd_runs')
    op.drop_index(op.f('ix_threats_created_at'), table_name='threats')
    op.drop_table('threats')
    op.drop_table('security_controls')
    op.drop_table('requirements')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_github_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

