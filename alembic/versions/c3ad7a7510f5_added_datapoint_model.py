"""Added DataPoint model

Revision ID: c3ad7a7510f5
Revises: 37347a272d33
Create Date: 2022-08-19 11:04:56.273838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3ad7a7510f5'
down_revision = '37347a272d33'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('datapoint',
    sa.Column('datapoint_id', sa.Integer(), nullable=False),
    sa.Column('current', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.Integer(), nullable=True),
    sa.Column('measurement_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['measurement_id'], ['measurement.measurement_id'], ),
    sa.PrimaryKeyConstraint('datapoint_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('datapoint')
    # ### end Alembic commands ###
