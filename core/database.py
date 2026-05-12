import sqlite3
import json
from pathlib import Path
from config.settings import DB_PATH, NPCS_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            npc_id      TEXT NOT NULL,
            content     TEXT NOT NULL,
            importance  INTEGER DEFAULT 5,
            tags        TEXT DEFAULT '',
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_memories_npc
            ON memories(npc_id, created_at DESC);

        CREATE TABLE IF NOT EXISTS emotions (
            npc_id      TEXT PRIMARY KEY,
            happy       INTEGER DEFAULT 50,
            angry       INTEGER DEFAULT 0,
            suspicious  INTEGER DEFAULT 0,
            stressed    INTEGER DEFAULT 30,
            excited     INTEGER DEFAULT 40,
            annoyed     INTEGER DEFAULT 0,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS relationships (
            npc_id              TEXT PRIMARY KEY,
            trust               INTEGER DEFAULT 50,
            friendship          INTEGER DEFAULT 30,
            hostility           INTEGER DEFAULT 0,
            respect             INTEGER DEFAULT 30,
            interactions_count  INTEGER DEFAULT 0,
            updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            npc_id      TEXT NOT NULL,
            role        TEXT NOT NULL,
            message     TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_chat_npc
            ON chat_history(npc_id, created_at DESC);
    """)

    # Seed default emotion and relationship rows for each NPC
    with open(NPCS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for npc in data["npcs"]:
        mood = npc["initial_mood"]
        cursor.execute("""
            INSERT OR IGNORE INTO emotions (npc_id, happy, angry, suspicious, stressed, excited, annoyed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            npc["id"],
            mood["happy"], mood["angry"], mood["suspicious"],
            mood["stressed"], mood["excited"], mood["annoyed"]
        ))
        cursor.execute("""
            INSERT OR IGNORE INTO relationships (npc_id)
            VALUES (?)
        """, (npc["id"],))

    conn.commit()
    conn.close()
