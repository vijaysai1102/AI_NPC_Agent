from core.npc_loader import load_npc
from core.emotion_engine import get_emotions
from core.relationship_engine import get_relationship
from core.memory_manager import get_recent_memories
from core.rag_retriever import retrieve_context
from ai.gemini_client import generate_response
from ai.prompt_builder import build_opening_prompt
from config.settings import MEMORY_CONTEXT_COUNT, RAG_TOP_K


def generate_opening(npc_id: str) -> str:
    npc = load_npc(npc_id)
    emotions = get_emotions(npc_id)
    relationship = get_relationship(npc_id)
    memories = get_recent_memories(npc_id, MEMORY_CONTEXT_COUNT)
    rag_context = retrieve_context(npc_id, query="", top_k=RAG_TOP_K)

    prompt = build_opening_prompt(npc, emotions, relationship, memories, rag_context)
    result = generate_response(prompt)
    return result.get("reply", f"Hey. What do you want?")
