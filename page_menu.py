import streamlit as st
import styles
from page_common import btn

IA_OPTIONS = {
    "Aleatoire":         "random",
    "Grover Heuristique":"grover",
    "QAOA + Grover":     "qaoa",
    "Minimax Quantique": "minimax_q",
}
IA_DESC = {
    "random":    "Choisit deux cases au hasard.",
    "grover":    "Grover + heuristique quantique.",
    "qaoa":      "QAOA évalue les cases, Grover sélectionne.",
    "minimax_q": "Minimax alpha-bêta adapté aux paires quantiques.",
}

def show():
    styles.apply_base()
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
    st.subheader("OPTIONS MULTIJOUEUR")
    st.session_state.limite_N    = st.slider("SEUIL (N)", 1, 9, st.session_state.limite_N)
    c1, c2 = st.columns(2)
    st.session_state.trigger_sat = c1.toggle("SATURATION", value=st.session_state.trigger_sat)
    st.session_state.trigger_cyc = c2.toggle("CYCLES",     value=st.session_state.trigger_cyc)
    if st.button(btn("JOUER", 0), type="primary", use_container_width=True):
        st.session_state.page = "JEU_LOCAL"; st.rerun()


def _panel_ia():
    st.subheader("OPTIONS ORDINATEUR")
    qui = st.radio("Qui commence ?", ["Joueur (X)", "Ordinateur (O)"], horizontal=True, key="r_qui")
    st.session_state.ia_joueur_commence = (qui == "Joueur (X)")
    lbl = st.selectbox("Algorithme IA", list(IA_OPTIONS.keys()), key="sel_ia")
    st.session_state.ia_algo = IA_OPTIONS[lbl]
    st.info(IA_DESC[IA_OPTIONS[lbl]])
    st.caption("2 cases / tour · Cycles activés")
    if st.button(btn("JOUER CONTRE L'IA", 0), type="primary", use_container_width=True):
        st.session_state.page = "JEU_IA"; st.rerun()

    st.divider()
    st.subheader("IA vs IA")
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
    st.caption("Round-robin entre les 4 IAs.")
    st.session_state.tournoi_n = st.slider("Parties / match (N)", 1, 20, st.session_state.get("tournoi_n", 3), key="sl_tn")
    if st.button(btn("LANCER LE TOURNOI", 0), use_container_width=True):
        st.session_state.page = "TOURNOI"; st.rerun()


def _panel_infos():
    st.subheader("DOCUMENTS DU PROJET")
    if st.button(btn("CONSULTER", 2), use_container_width=True):
        st.session_state.page = "INFOS"; st.rerun()


def _panel_perso():
    st.subheader("PERSONNALISATION")
    _skin(1); _skin(2)


def _skin(n):
    p = f"p{n}"
    st.markdown(f"#### JOUEUR {n}")
    ca, cb = st.columns([3,1])
    with ca:
        st.session_state[f'{p}_name'] = st.text_input(
            f"Pseudo {n}", st.session_state[f'{p}_name'], key=f"n_{p}", label_visibility="collapsed")
    with cb:
        st.session_state[f'{p}_color'] = st.color_picker(
            "Couleur", st.session_state[f'{p}_color'], key=f"cp_{p}", label_visibility="collapsed")
    ci, cu = st.columns([1,4])
    with ci: st.image(st.session_state[f'{p}_url'], width=45)
    with cu:
        st.session_state[f'{p}_url'] = st.text_input(
            "URL", st.session_state[f'{p}_url'], key=f"u_{p}", label_visibility="collapsed")
    st.divider()