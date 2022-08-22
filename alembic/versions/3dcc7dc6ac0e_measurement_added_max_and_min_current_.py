"""Measurement added max and min_current property

Revision ID: 3dcc7dc6ac0e
Revises: 0b1e1c58bfe4
Create Date: 2022-08-22 16:17:27.594361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3dcc7dc6ac0e'
down_revision = '0b1e1c58bfe4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('measurement', sa.Column('max_current', sa.Float(), nullable=True))
    op.add_column('measurement', sa.Column('min_current', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('measurement', 'min_current')
    op.drop_column('measurement', 'max_current')
    # ### end Alembic commands ###
