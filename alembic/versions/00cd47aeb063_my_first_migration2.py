"""my first migration2

Revision ID: 00cd47aeb063
Revises: 5eb9b7b4aa93
Create Date: 2022-08-19 09:18:20.276622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00cd47aeb063'
down_revision = '5eb9b7b4aa93'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transmission',
    sa.Column('transmission_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('transmission_configuration', sa.Enum('config_80', 'config_80_encoder', 'config_105', 'config_105_break', 'config_105_encoder', 'config_105_break_encoder', name='transmissionconfiguration'), nullable=True),
    sa.Column('finished_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('transmission_id')
    )
    op.create_table('assembly_step',
    sa.Column('assembly_step_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('assembly_step_order', sa.Enum('step_1', 'step_2', 'step_3', name='assemblystep'), nullable=True),
    sa.Column('transmission_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['transmission_id'], ['transmission.transmission_id'], ),
    sa.PrimaryKeyConstraint('assembly_step_id')
    )
    op.drop_table('book_publisher')
    op.drop_table('author_publisher')
    op.drop_table('book')
    op.drop_table('publisher')
    op.drop_table('author')
    op.drop_table('mynewtable')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mynewtable',
    sa.Column('my_id', sa.INTEGER(), nullable=False),
    sa.Column('my_text', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('my_id')
    )
    op.create_table('author',
    sa.Column('author_id', sa.INTEGER(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(), nullable=True),
    sa.Column('last_name', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('author_id')
    )
    op.create_table('publisher',
    sa.Column('publisher_id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('publisher_id')
    )
    op.create_table('book',
    sa.Column('book_id', sa.INTEGER(), nullable=False),
    sa.Column('author_id', sa.INTEGER(), nullable=True),
    sa.Column('title', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.author_id'], ),
    sa.PrimaryKeyConstraint('book_id')
    )
    op.create_table('author_publisher',
    sa.Column('author_id', sa.INTEGER(), nullable=True),
    sa.Column('publisher_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['author.author_id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.publisher_id'], )
    )
    op.create_table('book_publisher',
    sa.Column('book_id', sa.INTEGER(), nullable=True),
    sa.Column('publisher_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.book_id'], ),
    sa.ForeignKeyConstraint(['publisher_id'], ['publisher.publisher_id'], )
    )
    op.drop_table('assembly_step')
    op.drop_table('transmission')
    # ### end Alembic commands ###