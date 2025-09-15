"""rename_frequency_seconds_to_hours

Revision ID: bec89700c4be
Revises: 8f0988bc7020
Create Date: 2025-09-14 20:32:55.134378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bec89700c4be'
down_revision: Union[str, None] = '8f0988bc7020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename frequency_seconds to frequency_hours
    op.alter_column('photo_schedules', 'frequency_seconds', new_column_name='frequency_hours')


def downgrade() -> None:
    # Rename frequency_hours back to frequency_seconds
    op.alter_column('photo_schedules', 'frequency_hours', new_column_name='frequency_seconds')
