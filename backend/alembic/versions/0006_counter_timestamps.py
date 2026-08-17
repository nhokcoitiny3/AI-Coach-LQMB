"""add inherited timestamps to existing counter table"""

revision = "0006_counter_timestamps"
down_revision = "0005_hero_counters"
branch_labels = None
depends_on = None


def upgrade():
    # Revision 0005 already creates these inherited timestamp columns.
    # Keep this revision as a no-op so fresh databases can reach head.
    pass


def downgrade():
    pass
