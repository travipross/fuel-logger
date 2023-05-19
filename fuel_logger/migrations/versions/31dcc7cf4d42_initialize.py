"""initialize

Revision ID: 31dcc7cf4d42
Revises:
Create Date: 2020-03-29 17:14:41.313496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "31dcc7cf4d42"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "vehicle",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("make", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "fillup",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("odometer_km", sa.Integer(), nullable=False),
        sa.Column("fuel_amt_l", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fillup_timestamp"), "fillup", ["timestamp"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_fillup_timestamp"), table_name="fillup")
    op.drop_table("fillup")
    op.drop_table("vehicle")
    op.drop_table("user")
    # ### end Alembic commands ###
