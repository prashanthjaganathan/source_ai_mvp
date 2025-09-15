"""ensure uid on users; original_key on photos (rename file_path)

Revision ID: 9a63515141f6
Revises: 
Create Date: 2025-09-14 18:14:26.236151

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '9a63515141f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _col_exists(table, column):
    """Check if a column exists in a table"""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns(table)}
    return column in cols


def upgrade() -> None:
    # UUID extension (safe if already present)
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # users.uid
    if not _col_exists("users", "uid"):
        op.add_column(
            "users",
            sa.Column("uid", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        )
        # unique index/constraint
        op.create_index("ix_users_uid", "users", ["uid"], unique=True)

    # photos.original_key  (rename from file_path if needed)
    has_original = _col_exists("photos", "original_key")
    has_file_path = _col_exists("photos", "file_path")

    if not has_original and has_file_path:
        # add new column, copy, drop old
        op.add_column("photos", sa.Column("original_key", sa.String(500), nullable=True))
        op.execute("UPDATE photos SET original_key = file_path WHERE original_key IS NULL;")
        # Make it NOT NULL only if every row has a value
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM photos WHERE original_key IS NULL) THEN
                    ALTER TABLE photos ALTER COLUMN original_key SET NOT NULL;
                END IF;
            END $$;
        """)
        op.drop_column("photos", "file_path")
    elif not has_original and not has_file_path:
        # table exists but neither column: create original_key nullable (you can enforce later)
        op.add_column("photos", sa.Column("original_key", sa.String(500), nullable=True))

    # photos.uid
    if not _col_exists("photos", "uid"):
        op.add_column(
            "photos",
            sa.Column("uid", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        )
        op.create_index("ix_photos_uid", "photos", ["uid"], unique=True)


def downgrade() -> None:
    # Keep it simple: no-op
    pass
