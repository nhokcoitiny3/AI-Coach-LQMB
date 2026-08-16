"""add versioned multi-source datafeed"""

from alembic import op
import sqlalchemy as sa

revision = "0002_datafeed"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("heroes", sa.Column("normalized_name", sa.String(100), nullable=True))
    op.add_column("heroes", sa.Column("aliases", sa.JSON(), nullable=False, server_default="[]"))
    op.add_column("heroes", sa.Column("region", sa.String(30), nullable=False, server_default="unknown"))
    op.add_column("heroes", sa.Column("catalog_patch", sa.String(50), nullable=True))
    op.add_column("heroes", sa.Column("source_url", sa.String(500), nullable=True))
    op.add_column("heroes", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_heroes_normalized_name", "heroes", ["normalized_name"], unique=True)
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(60), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("region", sa.String(30), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_data_sources_key", "data_sources", ["key"])
    op.create_table(
        "data_feed_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("records_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_written", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_data_feed_runs_source_id", "data_feed_runs", ["source_id"])
    op.create_index("ix_data_feed_runs_status", "data_feed_runs", ["status"])
    op.create_table(
        "hero_meta_snapshots",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("hero_id", sa.Uuid(), sa.ForeignKey("heroes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("region", sa.String(30), nullable=False),
        sa.Column("patch_version", sa.String(50), nullable=True),
        sa.Column("tier", sa.String(10), nullable=True),
        sa.Column("pick_rate", sa.Float(), nullable=True),
        sa.Column("ban_rate", sa.Float(), nullable=True),
        sa.Column("win_rate", sa.Float(), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_hero_meta_snapshots_hero_id", "hero_meta_snapshots", ["hero_id"])
    op.create_index("ix_hero_meta_snapshots_source_id", "hero_meta_snapshots", ["source_id"])
    op.create_index("ix_hero_meta_snapshots_captured_at", "hero_meta_snapshots", ["captured_at"])
    op.create_index("ix_meta_source_hero_capture", "hero_meta_snapshots", ["source_id", "hero_id", "captured_at"])


def downgrade():
    op.drop_table("hero_meta_snapshots")
    op.drop_table("data_feed_runs")
    op.drop_table("data_sources")
    op.drop_index("ix_heroes_normalized_name", table_name="heroes")
    op.drop_column("heroes", "last_seen_at")
    op.drop_column("heroes", "source_url")
    op.drop_column("heroes", "catalog_patch")
    op.drop_column("heroes", "region")
    op.drop_column("heroes", "aliases")
    op.drop_column("heroes", "normalized_name")
