from core.database import get_connection
from config.settings import STAT_MIN, STAT_MAX

EMOTION_KEYS = ["happy", "angry", "suspicious", "stressed", "excited", "annoyed"]


def get_emotions(npc_id: str) -> dict:
    conn = get_connection()
    row = conn.execute(
        "SELECT happy, angry, suspicious, stressed, excited, annoyed FROM emotions WHERE npc_id = ?",
        (npc_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {k: 0 for k in EMOTION_KEYS}


def update_emotions(npc_id: str, deltas: dict) -> None:
    current = get_emotions(npc_id)
    updates = {}
    for key in EMOTION_KEYS:
        delta = deltas.get(key, 0)
        updates[key] = max(STAT_MIN, min(STAT_MAX, current.get(key, 0) + delta))

    conn = get_connection()
    conn.execute("""
        UPDATE emotions
        SET happy=?, angry=?, suspicious=?, stressed=?, excited=?, annoyed=?, updated_at=CURRENT_TIMESTAMP
        WHERE npc_id=?
    """, (
        updates["happy"], updates["angry"], updates["suspicious"],
        updates["stressed"], updates["excited"], updates["annoyed"],
        npc_id
    ))
    conn.commit()
    conn.close()


def reset_emotions(npc_id: str, mood: dict) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE emotions
        SET happy=?, angry=?, suspicious=?, stressed=?, excited=?, annoyed=?, updated_at=CURRENT_TIMESTAMP
        WHERE npc_id=?
    """, (
        mood.get("happy", 50), mood.get("angry", 0), mood.get("suspicious", 0),
        mood.get("stressed", 30), mood.get("excited", 40), mood.get("annoyed", 0),
        npc_id
    ))
    conn.commit()
    conn.close()
