"""Add roles column

Revision ID: f2e50a82cf70
Revises: 671e9c4e4082
Create Date: 2025-12-10 22:29:52.530881
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f2e50a82cf70'
down_revision = '671e9c4e4082'
branch_labels = None
depends_on = None


def upgrade():
    # Voeg nieuwe kolom toe
    op.add_column('users', sa.Column('roles', sa.String(length=200)))

    # Verwijder oude kolom als die bestaat
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('role')


def downgrade():
    # Rollback: voeg oude kolom terug toe
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('role', sa.String()))

    # Verwijder kolom roles
    op.drop_column('users', 'roles')
