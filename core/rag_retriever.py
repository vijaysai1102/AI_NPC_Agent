import json
from pathlib import Path
from config.settings import CAMPUS_CONTEXT_DIR, RAG_TOP_K

_CONTEXT_FILES = ["events.json", "assignments.json", "rumors.json", "announcements.json", "lore.json"]
_LIST_KEYS = ["events", "assignments", "rumors", "announcements", "lore"]


def _load_all_context() -> list[dict]:
    items = []
    for fname, list_key in zip(_CONTEXT_FILES, _LIST_KEYS):
        path = CAMPUS_CONTEXT_DIR / fname
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items.extend(data.get(list_key, []))
    return items


def retrieve_context(npc_id: str, query: str = "", top_k: int = RAG_TOP_K) -> list[dict]:
    all_items = _load_all_context()
    relevant = [item for item in all_items if npc_id in item.get("npc_relevance", [])]

    if not relevant:
        return []

    query_words = set(query.lower().split()) if query else set()

    def score(item: dict) -> int:
        text = " ".join([
            item.get("title", ""),
            item.get("content", ""),
            item.get("description", "")
        ]).lower()
        keyword_score = sum(1 for w in query_words if len(w) > 3 and w in text)
        # Items with more tag matches to the query score higher
        tag_text = " ".join(item.get("tags", []))
        tag_score = sum(1 for w in query_words if w in tag_text) * 2
        return keyword_score + tag_score

    scored = sorted(relevant, key=score, reverse=True)
    return scored[:top_k]


def format_context(items: list[dict]) -> str:
    if not items:
        return "No specific campus context available right now."
    lines = []
    for item in items:
        title = item.get("title") or item.get("id", "")
        body = item.get("content") or item.get("description", "")
        lines.append(f"• [{title}] {body}")
    return "\n".join(lines)
