"""store crawled hero portrait URLs"""

from alembic import op
import sqlalchemy as sa

revision = "0004_hero_images"
down_revision = "0003_catalog_provenance"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("heroes", sa.Column("image_url", sa.String(1000), nullable=True))


def downgrade():
    op.drop_column("heroes", "image_url")
