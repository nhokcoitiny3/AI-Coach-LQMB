"""store sourced hero counter picks"""

from alembic import op
import sqlalchemy as sa

revision = "0005_hero_counters"
down_revision = "0004_hero_images"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("hero_counters", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("hero_id", sa.Uuid(), sa.ForeignKey("heroes.id", ondelete="CASCADE"), nullable=False), sa.Column("source_id", sa.Uuid(), sa.ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False), sa.Column("counter_name", sa.String(100), nullable=False), sa.Column("normalized_counter_name", sa.String(100), nullable=False), sa.Column("source_url", sa.String(500), nullable=False), sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_hero_counters_hero_id", "hero_counters", ["hero_id"])
    op.create_index("ix_hero_counters_source_id", "hero_counters", ["source_id"])
    op.create_index("ix_hero_counters_normalized_counter_name", "hero_counters", ["normalized_counter_name"])
    op.create_index("ix_hero_counters_captured_at", "hero_counters", ["captured_at"])
    op.create_index("ix_counter_source_hero", "hero_counters", ["source_id", "hero_id"])


def downgrade():
    op.drop_table("hero_counters")
