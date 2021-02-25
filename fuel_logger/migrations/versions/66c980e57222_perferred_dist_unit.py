"""perferred_dist_unit

Revision ID: 66c980e57222
Revises: 94b733c58c61
Create Date: 2020-04-16 22:12:17.236717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "66c980e57222"
down_revision = "94b733c58c61"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("vehicle", sa.Column("odo_unit", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("vehicle", "odo_unit")
    # ### end Alembic commands ###