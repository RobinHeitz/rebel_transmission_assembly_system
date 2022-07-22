"""Adding a new model

Revision ID: 5eb9b7b4aa93
Revises: 5d8fb50d646f
Create Date: 2022-07-22 11:28:52.696447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5eb9b7b4aa93'
down_revision = '5d8fb50d646f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mynewtable',
    sa.Column('my_id', sa.Integer(), nullable=False),
    sa.Column('my_text', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('my_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mynewtable')
    # ### end Alembic commands ###
