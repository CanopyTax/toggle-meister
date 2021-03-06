"""add soft delete feature table

Revision ID: af4279aa1f64
Revises: fa2cd0ecc30f
Create Date: 2019-05-13 11:47:29.388502

"""

# revision identifiers, used by Alembic.
revision = 'af4279aa1f64'
down_revision = 'fa2cd0ecc30f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    # ### commands auto generated by Alembic ###
    op.create_table('deleted_features',
                    sa.Column('name', sa.String(length=50), nullable=False),
                    sa.Column('deleted_on', postgresql.TIMESTAMP(), nullable=True),
                    sa.Column('deleted_by', sa.String(), nullable=True),
                    sa.ForeignKeyConstraint(['deleted_by'], ['employees.username'], ),
                    sa.PrimaryKeyConstraint('name'),
                    sa.UniqueConstraint('name')
                    )
    op.drop_constraint('toggles_feature_fkey', 'toggles', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic ###
    op.create_foreign_key('toggles_feature_fkey', 'toggles', 'features', ['feature'], ['name'])
    op.drop_table('deleted_features')
    # ### end Alembic commands ###
