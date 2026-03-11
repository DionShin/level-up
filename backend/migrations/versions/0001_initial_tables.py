"""initial tables

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # stats
    op.create_table(
        'stats',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.Column('icon', sa.String(length=10), nullable=False),
        sa.Column('color', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_stats_user_id', 'stats', ['user_id'])

    # categories
    op.create_table(
        'categories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('stat_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('icon', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['stat_id'], ['stats.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_categories_user_id', 'categories', ['user_id'])

    # routines
    op.create_table(
        'routines',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('category_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('frequency', sa.String(length=20), nullable=False, server_default='daily'),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('notification_time', sa.String(length=5), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_forked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('original_routine_id', sa.String(), nullable=True),
        sa.Column('original_author', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_routines_user_id', 'routines', ['user_id'])

    # routine_logs
    op.create_table(
        'routine_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('routine_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['routine_id'], ['routines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_routine_logs_routine_id', 'routine_logs', ['routine_id'])
    op.create_index('ix_routine_logs_user_id', 'routine_logs', ['user_id'])
    op.create_index('ix_routine_logs_log_date', 'routine_logs', ['log_date'])

    # growth_history
    op.create_table(
        'growth_history',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('routine_id', sa.String(), nullable=True),
        sa.Column('event_type', sa.String(length=30), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['routine_id'], ['routines.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_growth_history_user_id', 'growth_history', ['user_id'])

    # push_subscriptions
    op.create_table(
        'push_subscriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('keys', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('endpoint'),
    )
    op.create_index('ix_push_subscriptions_user_id', 'push_subscriptions', ['user_id'])

    # community_routines
    op.create_table(
        'community_routines',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('author_user_id', sa.String(), nullable=False),
        sa.Column('author_name', sa.String(length=50), nullable=False),
        sa.Column('author_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('stat_id', sa.String(length=30), nullable=False),
        sa.Column('category_name', sa.String(length=50), nullable=False),
        sa.Column('routine_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('days_of_week', sa.JSON(), nullable=True),
        sa.Column('notification_time', sa.String(length=5), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('fork_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('like_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_community_routines_author_user_id', 'community_routines', ['author_user_id'])


def downgrade() -> None:
    op.drop_table('community_routines')
    op.drop_table('push_subscriptions')
    op.drop_table('growth_history')
    op.drop_table('routine_logs')
    op.drop_table('routines')
    op.drop_table('categories')
    op.drop_table('stats')
