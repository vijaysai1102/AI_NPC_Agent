from core.database import get_connection


def save_memory(npc_id: str, content: str, importance: int = 5, tags: str = "") -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO memories (npc_id, content, importance, tags) VALUES (?, ?, ?, ?)",
        (npc_id, content, importance, tags)
    )
    conn.commit()
    conn.close()


def get_recent_memories(npc_id: str, n: int = 5) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT content, importance, created_at FROM memories WHERE npc_id = ? ORDER BY created_at DESC LIMIT ?",
        (npc_id, n)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_memories_by_tags(npc_id: str, tags: list[str], limit: int = 5) -> list[dict]:
    if not tags:
        return get_recent_memories(npc_id, limit)
    conn = get_connection()
    tag_filters = " OR ".join(["tags LIKE ?" for _ in tags])
    params = [npc_id] + [f"%{t}%" for t in tags] + [limit]
    rows = conn.execute(
        f"SELECT content, importance, created_at FROM memories WHERE npc_id = ? AND ({tag_filters}) ORDER BY importance DESC LIMIT ?",
        params
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def format_memories(memories: list[dict]) -> str:
    if not memories:
        return "No prior interactions on record."
    return "\n".join(f"- {m['content']}" for m in memories)


# ── Chat history persistence ───────────────────────────────────────────────────

def save_chat_message(npc_id: str, role: str, message: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_history (npc_id, role, message) VALUES (?, ?, ?)",
        (npc_id, role, message)
    )
    conn.commit()
    conn.close()


def load_chat_history(npc_id: str, limit: int = 50) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, message FROM chat_history WHERE npc_id = ? ORDER BY created_at ASC LIMIT ?",
        (npc_id, limit)
    ).fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["message"]} for r in rows]
