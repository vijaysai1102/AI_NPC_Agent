import streamlit as st


def render_npc_card(npc: dict) -> None:
    st.markdown(f"## {npc['emoji']} {npc['name']}")
    st.caption(npc["role"])
    st.divider()

    st.markdown("**Personality**")
    trait_html = " ".join(
        f'<span style="background:#1e3a5f;color:#7dd3fc;padding:2px 8px;border-radius:12px;font-size:0.75rem">{t}</span>'
        for t in npc.get("traits", [])
    )
    st.markdown(trait_html, unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f"**Goal:** {npc.get('goal', '')}")
    st.markdown(f"**Fear:** {npc.get('fear', '')}")
    st.divider()
