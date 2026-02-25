import streamlit as st

def bouton_retour(infos_html: str = ""):
    col_btn, col_info, col_vide = st.columns([1, 3, 4])
    with col_btn:
        if st.button("← MENU", key="__retour__", use_container_width=True):
            st.session_state.page = "MENU"
            st.rerun()
    with col_info:
        if infos_html:
            st.markdown(
                f'<div style="font-size:13px;color:#888;padding-top:8px;">{infos_html}</div>',
                unsafe_allow_html=True)

    # Bouton retour : violet/mauve — ne confond pas avec les couleurs joueurs
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:first-of-type
        > div:first-child div.stButton > button {
        height:36px!important; min-height:36px!important;
        font-size:12px!important; font-weight:700!important;
        letter-spacing:1px!important; text-transform:uppercase!important;
        background:#1e0e35!important;
        border:1px solid #7b3fa0!important;
        color:#c084fc!important;
        border-radius:6px!important;
        box-shadow:none!important;
        transition:background 0.2s,border-color 0.2s,color 0.2s!important;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type
        > div:first-child div.stButton > button:hover {
        background:#2d1550!important;
        border-color:#a855f7!important;
        color:#e0abff!important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.divider()