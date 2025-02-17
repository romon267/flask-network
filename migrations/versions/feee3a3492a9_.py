"""empty message

Revision ID: feee3a3492a9
Revises: f7d921398532
Create Date: 2021-01-12 12:45:30.489861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'feee3a3492a9'
down_revision = 'f7d921398532'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('is_edited', sa.Boolean(), nullable=True))
    op.add_column('post', sa.Column('is_edited', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'is_edited')
    op.drop_column('comment', 'is_edited')
    # ### end Alembic commands ###
