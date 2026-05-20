"""initial

Revision ID: 50d90fb2e3e6
Revises: 
Create Date: 2026-05-19 22:22:31.008485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '50d90fb2e3e6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'vacancies',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hh_id', sa.String(50), nullable=False, unique=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('company', sa.String(200), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('salary_from', sa.Integer(), nullable=True),
        sa.Column('salary_to', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(10), nullable=True),
        sa.Column('salary_from_byn', sa.Integer(), nullable=True),
        sa.Column('salary_to_byn', sa.Integer(), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('employment', sa.String(100), nullable=True),
        sa.Column('schedule', sa.String(200), nullable=True),
        sa.Column('contract_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )

    op.create_table(
        'vacancy_skills',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('vacancy_hh_id', sa.String(50), nullable=False),
        sa.Column('skill_name', sa.String(100), nullable=False),
        sa.UniqueConstraint('vacancy_hh_id', 'skill_name'),
    )


def downgrade() -> None:
    op.drop_table('vacancy_skills')
    op.drop_table('vacancies')