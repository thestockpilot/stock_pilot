"""add backtest trades, drawdown, profit_factor to marketplace_listings

Revision ID: a2b3c4d5e6f7
Revises: f78f1f226fbd
Create Date: 2026-07-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = 'f78f1f226fbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('marketplace_listings', sa.Column('backtest_trades', sa.Integer(), nullable=True))
    op.add_column('marketplace_listings', sa.Column('backtest_max_drawdown', sa.Numeric(precision=5, scale=4), nullable=True))
    op.add_column('marketplace_listings', sa.Column('backtest_profit_factor', sa.Numeric(precision=5, scale=2), nullable=True))


def downgrade() -> None:
    op.drop_column('marketplace_listings', 'backtest_profit_factor')
    op.drop_column('marketplace_listings', 'backtest_max_drawdown')
    op.drop_column('marketplace_listings', 'backtest_trades')
