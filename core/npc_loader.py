import json
from functools import lru_cache
from config.settings import NPCS_PATH


@lru_cache(maxsize=1)
def _load_raw() -> dict:
    with open(NPCS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_npcs() -> list[dict]:
    return _load_raw()["npcs"]


def load_npc(npc_id: str) -> dict:
    for npc in load_all_npcs():
        if npc["id"] == npc_id:
            return npc
    raise ValueError(f"Unknown NPC id: {npc_id}")
