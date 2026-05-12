import streamlit as st

_EMOTION_META = {
    "happy":      ("😊", "#22c55e"),
    "angry":      ("😠", "#ef4444"),
    "suspicious": ("🤨", "#eab308"),
    "stressed":   ("😰", "#f97316"),
    "excited":    ("🤩", "#3b82f6"),
    "annoyed":    ("😒", "#a855f7"),
}

_REL_META = {
    "trust":      ("🤝", "#06b6d4"),
    "friendship": ("💛", "#facc15"),
    "hostility":  ("⚔️",  "#f43f5e"),
    "respect":    ("🎖️",  "#8b5cf6"),
}


def _bar(label: str, emoji: str, value: int, color: str) -> None:
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;margin-bottom:2px">'
        f'<span style="font-size:0.8rem">{emoji} {label.capitalize()}</span>'
        f'<span style="font-size:0.8rem;color:{color}">{value}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    filled = int((value / 100) * 20)
    bar = "█" * filled + "░" * (20 - filled)
    st.markdown(
        f'<div style="font-family:monospace;font-size:0.7rem;color:{color};margin-bottom:8px">{bar}</div>',
        unsafe_allow_html=True
    )


def render_meters(emotions: dict, relationship: dict) -> None:
    st.markdown("**Emotional State**")
    for key, (emoji, color) in _EMOTION_META.items():
        val = emotions.get(key, 0)
        _bar(key, emoji, val, color)

    st.divider()
    st.markdown("**Relationship**")
    for key, (emoji, color) in _REL_META.items():
        val = relationship.get(key, 0)
        _bar(key, emoji, val, color)

    interactions = relationship.get("interactions_count", 0)
    st.caption(f"Total interactions: {interactions}")


def render_memory_timeline(memories: list[dict]) -> None:
    st.divider()
    with st.expander("🧠 Memory Timeline", expanded=False):
        if not memories:
            st.caption("No memories yet. Start talking!")
            return
        for m in reversed(memories):  # oldest first
            ts = m.get("created_at", "")
            # Trim timestamp to readable format
            if "T" in ts:
                ts = ts.replace("T", " ")[:16]
            elif " " in ts:
                ts = ts[:16]
            importance = m.get("importance", 5)
            star = "⭐" if importance >= 7 else "📝"
            st.markdown(
                f'<div style="border-left:2px solid #334155;padding:4px 8px;margin-bottom:6px">'
                f'<div style="font-size:0.7rem;color:#64748b">{star} {ts}</div>'
                f'<div style="font-size:0.82rem">{m["content"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
