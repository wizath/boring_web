"""init

Revision ID: d56f6a253711
Revises: 
Create Date: 2023-02-16 13:54:29.364484

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'd56f6a253711'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('userrefreshtoken',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('jti', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('blacklisted_at', sa.DateTime(), nullable=True),
    sa.Column('blacklisted', sa.Boolean(), nullable=False),
    sa.Column('ip_address', sqlmodel.sql.sqltypes.AutoString(length=39), nullable=False),
    sa.Column('user_agent', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userrefreshtoken')
    op.drop_table('user')
    # ### end Alembic commands ###
