"""add inherited timestamps to existing counter table"""

from alembic import op
import sqlalchemy as sa

revision = "0006_counter_timestamps"
down_revision = "0005_hero_counters"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("hero_counters", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.add_column("hero_counters", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))


def downgrade():
    op.drop_column("hero_counters", "updated_at")
    op.drop_column("hero_counters", "created_at")
