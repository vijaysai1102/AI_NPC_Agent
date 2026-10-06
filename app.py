import streamlit as st
from core.database import init_db
from core.npc_loader import load_all_npcs, load_npc
from core.memory_manager import get_recent_memories, save_memory, save_chat_message, load_chat_history
from core.emotion_engine import get_emotions, update_emotions
from core.relationship_engine import get_relationship, update_relationship, increment_interactions
from core.rag_retriever import retrieve_context
from ai.gemini_client import generate_response, QuotaExceededError, ModelNotFoundError
from ai.prompt_builder import build_prompt
from ai.opening_message import generate_opening
from ui.npc_card import render_npc_card
from ui.meters import render_meters, render_memory_timeline
from config.settings import MEMORY_CONTEXT_COUNT, RAG_TOP_K, GROQ_API_KEY
import json, re

def _safe_text(content: str) -> str:
    """Extract reply text from content that may be a raw JSON string."""
    if not content.strip().startswith("{"):
        return content
    try:
        cleaned = re.sub(r"//[^\n\"]*", "", content)
        cleaned = re.sub(r":\s*\+(\d)", r": \1", cleaned)
        data = json.loads(cleaned.strip())
        return data.get("reply", content)
    except Exception:
        return content

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Living Campus",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}
/* NPC button hover */
.stButton > button {
    border-radius: 10px;
    transition: all 0.2s;
}
/* Chat messages */
[data-testid="stChatMessage"] {
    border-radius: 12px;
    margin-bottom: 4px;
}
/* Remove default padding on main block */
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────

init_db()

# ── Session state ─────────────────────────────────────────────────────────────

if "active_npc" not in st.session_state:
    st.session_state.active_npc = None
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}
if "opening_sent" not in st.session_state:
    st.session_state.opening_sent = set()

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("# 🎓 Living Campus")
    st.caption("Westbrook University — AI NPC World")
    st.divider()

    if not GROQ_API_KEY:
        st.error("⚠️ No GROQ_API_KEY found.\nAdd GROQ_API_KEY to your `.env` file.\nGet a free key at https://console.groq.com")
        st.stop()

    npcs = load_all_npcs()

    st.markdown("### Who do you want to talk to?")
    for npc in npcs:
        is_active = npc["id"] == st.session_state.active_npc
        label = f"{npc['emoji']}  {npc['name']}\n\n*{npc['role']}*"
        if st.button(
            label,
            key=f"btn_{npc['id']}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            if st.session_state.active_npc != npc["id"]:
                st.session_state.active_npc = npc["id"]
                st.rerun()

    st.divider()
    st.caption("💾 Memories persist across sessions")
    st.caption("🎭 Emotions and relationships evolve over time")

    # Reset button
    if st.session_state.active_npc:
        with st.expander("⚙️ Options"):
            if st.button("🔄 Reset this NPC's state", use_container_width=True):
                from core.npc_loader import load_npc as _load_npc
                from core.emotion_engine import reset_emotions
                npc_data = _load_npc(st.session_state.active_npc)
                reset_emotions(st.session_state.active_npc, npc_data["initial_mood"])
                if st.session_state.active_npc in st.session_state.chat_histories:
                    del st.session_state.chat_histories[st.session_state.active_npc]
                if st.session_state.active_npc in st.session_state.opening_sent:
                    st.session_state.opening_sent.discard(st.session_state.active_npc)
                st.rerun()

# ── Welcome screen ────────────────────────────────────────────────────────────

if not st.session_state.active_npc:
    st.markdown("# Welcome to Westbrook University 🎓")
    st.markdown("*A Living Campus powered by AI*")
    st.divider()

    st.markdown("### Meet the people on campus")
    cols = st.columns(3)
    for col, npc in zip(cols, npcs):
        with col:
            st.markdown(f"### {npc['emoji']} {npc['name']}")
            st.caption(npc["role"])
            st.markdown(" ".join(
                f"`{t}`" for t in npc.get("traits", [])
            ))
            st.markdown(f"_{npc.get('goal', '')}_")
            if st.button(f"Talk to {npc['name'].split()[0]}", key=f"welcome_{npc['id']}", use_container_width=True):
                st.session_state.active_npc = npc["id"]
                st.rerun()

    st.divider()
    st.markdown(
        "**How it works:** Each NPC remembers your conversations, tracks emotions, "
        "and develops a relationship with you over time. Talk to them — they're watching."
    )
    st.stop()

# ── Main chat area ────────────────────────────────────────────────────────────

npc_id = st.session_state.active_npc
npc = load_npc(npc_id)

col_chat, col_info = st.columns([3, 1])

# ── Right panel: NPC card + meters ───────────────────────────────────────────

with col_info:
    emotions = get_emotions(npc_id)
    relationship = get_relationship(npc_id)
    memories_for_timeline = get_recent_memories(npc_id, n=20)
    render_npc_card(npc)
    render_meters(emotions, relationship)
    render_memory_timeline(memories_for_timeline)

# ── Left panel: Chat ──────────────────────────────────────────────────────────

with col_chat:
    st.markdown(f"## Talking to {npc['emoji']} {npc['name']}")
    st.divider()

    if npc_id not in st.session_state.chat_histories:
        # Load persisted chat history from SQLite on first load
        persisted = load_chat_history(npc_id, limit=50)
        st.session_state.chat_histories[npc_id] = persisted
        if persisted:
            # Already have history — mark opening as sent so we don't re-generate
            st.session_state.opening_sent.add(npc_id)

    # Generate opening message on first ever visit to this NPC
    if npc_id not in st.session_state.opening_sent:
        try:
            with st.spinner(f"💭 {npc['name']} is thinking..."):
                opening = generate_opening(npc_id)
            st.session_state.chat_histories[npc_id] = [{"role": "npc", "content": opening}]
            st.session_state.opening_sent.add(npc_id)
            save_chat_message(npc_id, "npc", opening)
        except (QuotaExceededError, ModelNotFoundError) as e:
            st.error(f"**API Error**\n\n{e}")
            st.stop()

    # Render conversation history
    history = st.session_state.chat_histories[npc_id]
    for msg in history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(_safe_text(msg["content"]))
        else:
            with st.chat_message("assistant", avatar=npc["emoji"]):
                st.write(_safe_text(msg["content"]))

    # Chat input
    user_input = st.chat_input(f"Message {npc['name']}...")

    if user_input:
        # Show user message immediately and persist
        history.append({"role": "user", "content": user_input})
        save_chat_message(npc_id, "user", user_input)
        with st.chat_message("user"):
            st.write(user_input)

        # Load context and generate response
        emotions = get_emotions(npc_id)
        relationship = get_relationship(npc_id)
        memories = get_recent_memories(npc_id, MEMORY_CONTEXT_COUNT)
        rag_context = retrieve_context(npc_id, user_input, top_k=RAG_TOP_K)

        prompt = build_prompt(
            npc=npc,
            emotions=emotions,
            relationship=relationship,
            memories=memories,
            rag_context=rag_context,
            chat_history=history[:-1],  # exclude the message we just appended
            user_message=user_input
        )

        with st.chat_message("assistant", avatar=npc["emoji"]):
            try:
                with st.spinner(""):
                    result = generate_response(prompt)
                reply = result.get("reply", "...")
                st.write(reply)
            except (QuotaExceededError, ModelNotFoundError) as e:
                st.error(f"**API Error**\n\n{e}")
                history.pop()  # remove the user message we added
                st.stop()

        # Update state
        emotion_delta = result.get("emotion_delta", {})
        memory_note = result.get("memory_note", "")

        if emotion_delta:
            update_emotions(npc_id, emotion_delta)

        increment_interactions(npc_id)

        # Passive relationship drift: interactions build slight trust over time
        if relationship.get("interactions_count", 0) % 5 == 0:
            update_relationship(npc_id, {"trust": 2, "respect": 1})

        if memory_note:
            save_memory(npc_id, memory_note, importance=5, tags="")

        history.append({"role": "npc", "content": reply})
        save_chat_message(npc_id, "npc", reply)
        st.rerun()
