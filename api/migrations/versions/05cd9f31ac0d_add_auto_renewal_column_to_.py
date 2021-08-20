"""add auto_renewal column to UserSubscriptionPreferences

Revision ID: 05cd9f31ac0d
Revises:
Create Date: 2021-08-19 22:16:40.072931

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '05cd9f31ac0d'  # pragma: allowlist secret
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'UserSubscriptionPreferences',
        sa.Column('auto_renew', sa.Boolean(), nullable=False, server_default=False)
    )


def downgrade():
    op.drop_column('UserSubscriptionPreferences', 'auto_renew')
