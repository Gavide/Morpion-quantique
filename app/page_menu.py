import streamlit as st
import styles
from page_common import btn

IA_OPTIONS = {
    "Aleatoire":          "random",
    "Grover Heuristique": "grover",
    "QAOA + Grover":      "qaoa",
    "Minimax Quantique":  "minimax_q",
}
IA_DESC = {
    "random":    "Choisit deux cases au hasard.",
    "grover":    "Grover + heuristique quantique.",
    "qaoa":      "QAOA évalue les cases, Grover sélectionne.",
    "minimax_q": "Minimax alpha-bêta adapté aux paires quantiques.",
}

def _desc(texte):
    st.markdown(
        f'<p style="color:#666;font-size:13px;margin:-8px 0 14px 0;letter-spacing:0.5px;">{texte}</p>',
        unsafe_allow_html=True)

def show():
    st.markdown("""
    <style>
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] div.stButton > button,
    [data-testid="stMain"] [data-testid="stVerticalBlock"] div.stButton > button {
        background: #1e0e35 !important;
        border: 2px solid #7b3fa0 !important;
        color: #c084fc !important;
        height: 56px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        transition: background 0.2s, border-color 0.2s, color 0.2s, box-shadow 0.2s !important;
    }
    [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] div.stButton > button:hover,
    [data-testid="stMain"] [data-testid="stVerticalBlock"] div.stButton > button:hover {
        background: #2d1550 !important;
        border-color: #a855f7 !important;
        color: #e0abff !important;
        box-shadow: 0 0 14px rgba(168,85,247,0.35) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="main-header">QUANTUM<br>TIC-TAC-TOE</h1>', unsafe_allow_html=True)

    _, col, _ = st.columns([0.3, 2, 0.3])
    with col:
        st.markdown("<div style='margin-bottom:50px'></div>", unsafe_allow_html=True)
        action = st.session_state.get("menu_action")

        if st.button(btn("MULTIJOUEUR LOCAL", 0), use_container_width=True, key="m_local"):
            st.session_state.menu_action = None if action == "LOCAL" else "LOCAL"; st.rerun()
        if st.button(btn("ORDINATEUR", 1), use_container_width=True, key="m_ia"):
            st.session_state.menu_action = None if action == "IA" else "IA"; st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button(btn("INFORMATIONS", 2), use_container_width=True, key="m_infos"):
                st.session_state.menu_action = None if action == "INFOS" else "INFOS"; st.rerun()
        with c2:
            if st.button(btn("PERSONNALISATION", 3), use_container_width=True, key="m_perso"):
                st.session_state.menu_action = None if action == "PERSO" else "PERSO"; st.rerun()

        styles.apply_menu_button_styles(action)

        if action:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                if action == "LOCAL":    _panel_local()
                elif action == "IA":     _panel_ia()
                elif action == "INFOS":  _panel_infos()
                elif action == "PERSO":  _panel_perso()


def _panel_local():
    st.subheader("Multijoueur local")
    _desc("Deux joueurs s'affrontent sur le même écran. Choisissez le seuil d'effondrement et les règles de résolution.")
    st.session_state.limite_N    = st.slider("SEUIL (N)", 1, 9, st.session_state.limite_N)
    c1, c2 = st.columns(2)
    st.session_state.trigger_sat = c1.toggle("SATURATION", value=st.session_state.trigger_sat)
    st.session_state.trigger_cyc = c2.toggle("CYCLES",     value=st.session_state.trigger_cyc)
    if st.button(btn("JOUER", 0), type="primary", use_container_width=True):
        st.session_state.page = "JEU_LOCAL"; st.rerun()


def _panel_ia():
    st.subheader("Jouer contre l'IA")
    _desc("Affrontez un algorithme quantique. Choisissez qui commence et la stratégie de l'adversaire.")
    qui = st.radio("Qui commence ?", ["Joueur", "Ordinateur"], horizontal=True, key="r_qui")
    st.session_state.ia_joueur_commence = (qui == "Joueur")
    lbl = st.selectbox("Algorithme IA", list(IA_OPTIONS.keys()), key="sel_ia")
    st.session_state.ia_algo = IA_OPTIONS[lbl]
    st.info(IA_DESC[IA_OPTIONS[lbl]])
    if st.button(btn("JOUER CONTRE L'IA", 0), type="primary", use_container_width=True):
        # Initialiser active_player selon qui commence
        st.session_state.active_player = 1 if st.session_state.ia_joueur_commence else -1
        st.session_state.page = "JEU_IA"; st.rerun()

    st.divider()
    st.subheader("IA vs IA")
    _desc("Regardez deux algorithmes s'affronter en temps réel. Réglez le délai entre chaque coup.")
    cx, co = st.columns(2)
    with cx:
        lx = st.selectbox("IA X", list(IA_OPTIONS.keys()), key="sel_iax")
        st.session_state.ia_x_algo = IA_OPTIONS[lx]
    with co:
        lo = st.selectbox("IA O", list(IA_OPTIONS.keys()), index=1, key="sel_iao")
        st.session_state.ia_o_algo = IA_OPTIONS[lo]
    if st.button(btn("LANCER IA vs IA", 2), use_container_width=True):
        st.session_state.page = "JEU_IA_VS_IA"; st.rerun()

    st.divider()
    st.subheader("Tournoi ELO")
    _desc("Les 4 IAs s'affrontent en round-robin. Un classement ELO est calculé à l'issue de tous les matchs.")
    st.session_state.tournoi_n = st.slider("Parties / match", 1, 20, st.session_state.get("tournoi_n", 3), key="sl_tn")
    if st.button(btn("LANCER LE TOURNOI", 0), use_container_width=True):
        st.session_state.page = "TOURNOI"; st.rerun()


def _panel_infos():
    st.subheader("Documents du projet")
    _desc("Accédez à l'énoncé du projet et au rapport final. Consultez la liste des participants.")
    if st.button(btn("CONSULTER", 2), use_container_width=True):
        st.session_state.page = "INFOS"; st.rerun()


def _panel_perso():
    st.subheader("Personnalisation")
    _desc("Changez le nom, la couleur et l'icône de chaque joueur.")
    _skin(1); _skin(2)


def _skin(n):
    p = f"p{n}"
    st.markdown(f"#### JOUEUR {n}")
    ca, cb = st.columns([3, 1])
    with ca:
        st.session_state[f'{p}_name'] = st.text_input(
            f"Pseudo {n}", st.session_state[f'{p}_name'], key=f"n_{p}", label_visibility="collapsed")
    with cb:
        st.session_state[f'{p}_color'] = st.color_picker(
            "Couleur", st.session_state[f'{p}_color'], key=f"cp_{p}", label_visibility="collapsed")
    ci, cu = st.columns([1, 4])
    with ci: st.image(st.session_state[f'{p}_url'], width=45)
    with cu:
        st.session_state[f'{p}_url'] = st.text_input(
            "URL", st.session_state[f'{p}_url'], key=f"u_{p}", label_visibility="collapsed")
    st.divider()