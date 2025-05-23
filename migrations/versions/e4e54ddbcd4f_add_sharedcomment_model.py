"""add sharedcomment model

Revision ID: e4e54ddbcd4f
Revises: 475f5e213fc3
Create Date: 2025-05-13 16:37:17.513925

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4e54ddbcd4f'
down_revision = '475f5e213fc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shared_comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shared_review_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['shared_review_id'], ['shared_review.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shared_comment')
    # ### end Alembic commands ###
