# api/alembic/script.py.mako
"""projects defaults & not nulls

Revision ID: a1e37dddf901
Revises: 0001
Create Date: 2025-08-10 18:41:13.999748

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1e37dddf901'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # max_proposals
    op.execute("ALTER TABLE projects ALTER COLUMN max_proposals SET DEFAULT 50;")
    op.execute("UPDATE projects SET max_proposals = 50 WHERE max_proposals IS NULL;")
    op.execute("ALTER TABLE projects ALTER COLUMN max_proposals SET NOT NULL;")

    # tags
    op.execute("ALTER TABLE projects ALTER COLUMN tags SET DEFAULT '[]'::jsonb;")
    op.execute("UPDATE projects SET tags = '[]'::jsonb WHERE tags IS NULL;")
    op.execute("ALTER TABLE projects ALTER COLUMN tags SET NOT NULL;")

    # attachments
    op.execute("ALTER TABLE projects ALTER COLUMN attachments SET DEFAULT '[]'::jsonb;")
    op.execute("UPDATE projects SET attachments = '[]'::jsonb WHERE attachments IS NULL;")
    op.execute("ALTER TABLE projects ALTER COLUMN attachments SET NOT NULL;")

    # diğer default'lar da garanti olsun
    op.execute("ALTER TABLE projects ALTER COLUMN is_featured SET DEFAULT false;")
    op.execute("ALTER TABLE projects ALTER COLUMN allows_proposals SET DEFAULT true;")
    op.execute("ALTER TABLE projects ALTER COLUMN currency SET DEFAULT 'USD';")
    op.execute("ALTER TABLE projects ALTER COLUMN view_count SET DEFAULT 0;")
    op.execute("ALTER TABLE projects ALTER COLUMN proposal_count SET DEFAULT 0;")
    op.execute("ALTER TABLE projects ALTER COLUMN status SET DEFAULT 'open';")
    op.execute("ALTER TABLE projects ALTER COLUMN budget_type SET DEFAULT 'fixed';")

def downgrade():
    pass