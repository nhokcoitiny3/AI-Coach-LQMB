"""preserve multi-source catalog provenance"""

from alembic import op
import sqlalchemy as sa

revision = "0003_catalog_provenance"
down_revision = "0002_datafeed"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hero_catalog_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("hero_id", sa.Uuid(), sa.ForeignKey("heroes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", sa.Uuid(), sa.ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("source_role", sa.String(100), nullable=False, server_default="unknown"),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("region", sa.String(30), nullable=False),
        sa.Column("patch_version", sa.String(50), nullable=True),
        sa.Column("aliases", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("hero_id", "source_id", name="uq_hero_catalog_source"),
    )
    op.create_index("ix_hero_catalog_sources_hero_id", "hero_catalog_sources", ["hero_id"])
    op.create_index("ix_hero_catalog_sources_source_id", "hero_catalog_sources", ["source_id"])
    op.execute("DELETE FROM heroes WHERE normalized_name IN ('gameplay', 'tuongskin')")


def downgrade():
    op.drop_table("hero_catalog_sources")
