"""Add threat_vulnerabilities table for linking threats to scan findings.

Revision ID: 003_threat_vulnerabilities
Revises: 002_add_api_tokens
Create Date: 2024-01-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '003_threat_vulnerabilities'
down_revision = '002_add_api_tokens'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'threat_vulnerabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('threat_id', sa.Integer(), nullable=False),
        sa.Column('vulnerability_type', sa.String(length=50), nullable=False),
        sa.Column('vulnerability_id', sa.String(length=200), nullable=False),
        sa.Column('scan_run_id', sa.Integer(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='linked'),
        sa.Column('vulnerability_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['threat_id'], ['threats.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['scan_run_id'], ['ci_cd_runs.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('threat_id', 'vulnerability_type', 'vulnerability_id', name='uq_threat_vuln')
    )
    op.create_index(op.f('ix_threat_vulnerabilities_threat_id'), 'threat_vulnerabilities', ['threat_id'], unique=False)
    op.create_index(op.f('ix_threat_vulnerabilities_vulnerability_type'), 'threat_vulnerabilities', ['vulnerability_type'], unique=False)
    op.create_index(op.f('ix_threat_vulnerabilities_status'), 'threat_vulnerabilities', ['status'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_threat_vulnerabilities_status'), table_name='threat_vulnerabilities')
    op.drop_index(op.f('ix_threat_vulnerabilities_vulnerability_type'), table_name='threat_vulnerabilities')
    op.drop_index(op.f('ix_threat_vulnerabilities_threat_id'), table_name='threat_vulnerabilities')
    op.drop_table('threat_vulnerabilities')

