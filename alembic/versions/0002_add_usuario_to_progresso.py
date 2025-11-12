"""Obsolete migration placeholder.

This file was replaced by 0002_add_responsavel_to_progresso.py. Keeping this
placeholder avoids accidental duplicate-revision conflicts in environments
where the old filename may have been referenced. Do not apply this file.
"""

# This migration is intentionally left as a no-op placeholder.
revision = '0002_obsolete_do_not_apply'
down_revision = '0001'

def upgrade() -> None:
    # no-op
    return

def downgrade() -> None:
    # no-op
    return
