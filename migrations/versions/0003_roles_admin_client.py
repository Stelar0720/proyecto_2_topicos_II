"""Restringe los roles efectivos a admin/client sin perder referencias."""
from alembic import op

revision = "0003_roles_admin_client"
down_revision = "0002_demo_client_schedule"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("PRAGMA foreign_keys=OFF")
    op.execute("CREATE TABLE staff_new (id VARCHAR(36) PRIMARY KEY, username VARCHAR(80) NOT NULL UNIQUE, password_hash VARCHAR(256) NOT NULL, role VARCHAR(12) NOT NULL CHECK (role IN ('admin','client')), active BOOLEAN NOT NULL, created_at DATETIME NOT NULL)")
    op.execute("INSERT INTO staff_new SELECT id, username, password_hash, CASE WHEN role='client' THEN 'client' ELSE 'admin' END, active, created_at FROM staff")
    op.execute("DROP TABLE staff")
    op.execute("ALTER TABLE staff_new RENAME TO staff")
    op.execute("PRAGMA foreign_keys=ON")


def downgrade():
    pass
