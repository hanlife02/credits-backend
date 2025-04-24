"""add default training program

Revision ID: add_default_training_program
Revises: 
Create Date: 2025-04-24 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_default_training_program'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 添加default_training_program_id列到users表
    op.add_column('users', sa.Column('default_training_program_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_users_default_training_program',
        'users', 'training_programs',
        ['default_training_program_id'], ['id']
    )


def downgrade():
    # 删除外键约束
    op.drop_constraint('fk_users_default_training_program', 'users', type_='foreignkey')
    # 删除列
    op.drop_column('users', 'default_training_program_id')
