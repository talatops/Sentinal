"""Increase token_prefix column length.

Revision ID: 005_increase_token_prefix_length
Revises: 004_threat_templates
Create Date: 2025-11-10 13:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005_increase_token_prefix_length'
down_revision = '004_threat_templates'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('api_tokens', 'token_prefix',
                    existing_type=sa.String(length=10),
                    type_=sa.String(length=15),
                    existing_nullable=False)


def downgrade():
    op.alter_column('api_tokens', 'token_prefix',
                    existing_type=sa.String(length=15),
                    type_=sa.String(length=10),
                    existing_nullable=False)

