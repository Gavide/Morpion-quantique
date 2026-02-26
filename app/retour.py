import streamlit as st

_KEEP_KEYS = ['p1_name','p2_name','p1_color','p2_color','p1_url','p2_url',
              'ia_algo','ia_joueur_commence','ia_x_algo','ia_o_algo',
              'tournoi_n','limite_N','trigger_sat','trigger_cyc']

def _reset_board():
    kept = {k: st.session_state[k] for k in _KEEP_KEYS if k in st.session_state}
    st.session_state.clear()
    st.session_state.update(kept)
    st.session_state.page = "MENU"

def _reset_board_stay():
    page = st.session_state.get('page', 'MENU')
    kept = {k: st.session_state[k] for k in _KEEP_KEYS if k in st.session_state}
    st.session_state.clear()
    st.session_state.update(kept)
    st.session_state.page = page

def bouton_retour(infos_html: str = "", avec_reset: bool = False):
    if avec_reset:
        col_menu, col_reset, col_info, col_vide = st.columns([1, 1, 3, 3])
    else:
        col_menu, col_info, col_vide = st.columns([1, 3, 4])

    with col_menu:
        if st.button("← MENU", key="__retour__", use_container_width=True):
            _reset_board()
            st.rerun()

    if avec_reset:
        with col_reset:
            if st.button("RESET", key="__reset_plateau__", use_container_width=True):
                _reset_board_stay()
                st.rerun()

    with col_info:
        if infos_html:
            st.markdown(
                f'<div style="font-size:13px;color:#888;padding-top:8px;">{infos_html}</div>',
                unsafe_allow_html=True)

    nb_boutons = 2 if avec_reset else 1
    selectors = ",\n".join([
        f'div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child({i}) div.stButton > button'
        for i in range(1, nb_boutons + 1)
    ])
    st.markdown(f"""
    <style>
    {selectors} {{
        height:36px!important; min-height:36px!important;
        font-size:12px!important; font-weight:700!important;
        letter-spacing:1px!important; text-transform:uppercase!important;
        background:#1e0e35!important;
        border:1px solid #7b3fa0!important;
        color:#c084fc!important;
        border-radius:6px!important;
        box-shadow:none!important;
        transition:background 0.2s,border-color 0.2s,color 0.2s!important;
    }}
    {selectors}:hover {{
        background:#2d1550!important;
        border-color:#a855f7!important;
        color:#e0abff!important;
    }}
    </style>
    """, unsafe_allow_html=True)
    st.divider()