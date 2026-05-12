from core.database import get_connection
from config.settings import STAT_MIN, STAT_MAX

REL_KEYS = ["trust", "friendship", "hostility", "respect"]


def get_relationship(npc_id: str) -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT trust, friendship, hostility, respect, interactions_count FROM relationships WHERE npc_id = ?",
        (npc_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {k: 0 for k in REL_KEYS + ["interactions_count"]}


def update_relationship(npc_id: str, deltas: dict) -> None:
    current = get_relationship(npc_id)
    updates = {}
    for key in REL_KEYS:
        delta = deltas.get(key, 0)
        updates[key] = max(STAT_MIN, min(STAT_MAX, current.get(key, 0) + delta))

    conn = get_connection()
    conn.execute("""
        UPDATE relationships
        SET trust=?, friendship=?, hostility=?, respect=?, updated_at=CURRENT_TIMESTAMP
        WHERE npc_id=?
    """, (updates["trust"], updates["friendship"], updates["hostility"], updates["respect"], npc_id))
    conn.commit()
    conn.close()


def increment_interactions(npc_id: str) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE relationships SET interactions_count = interactions_count + 1, updated_at=CURRENT_TIMESTAMP WHERE npc_id=?",
        (npc_id,)
    )
    conn.commit()
    conn.close()
