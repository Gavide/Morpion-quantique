import streamlit as st
import quantum_engine as ql
import styles

st.set_page_config(
    page_title="Quantum Tic-Tac-Toe",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

defaults = {
    "page":               "MENU",
    "menu_action":        None,
    "plateau":            [[0]*3 for _ in range(3)],
    "marques_q":          [],
    "qc":                 ql.init_quantum_9q()[2],
    "active_player":      1,
    "selection":          [],
    "winner":             None,
    "history":            [],
    "limite_N":           2,
    "trigger_sat":        False,
    "trigger_cyc":        True,
    "p1_name":            "Joueur 1",
    "p2_name":            "Joueur 2",
    "p1_color":           "#1C83E1",
    "p2_color":           "#FF4B4B",
    "p1_url":             "https://img.icons8.com/color/96/filled-circle.png",
    "p2_url":             "https://img.icons8.com/color/96/close-window.png",
    "ia_algo":            "grover",
    "ia_joueur_commence": True,
    "ia_x_algo":          "grover",
    "ia_o_algo":          "random",
    "tournoi_n":          3,
    "winning_cells":      [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

page = st.session_state.page

# CSS global en premier
styles.apply_base()

# Cache toujours la sidebar — on n'en a plus besoin
st.markdown(
    "<style>"
    "[data-testid='stSidebar']{display:none!important}"
    "[data-testid='stSidebarCollapsedControl']{display:none!important}"
    "</style>",
    unsafe_allow_html=True)

import page_menu         as p_menu
import page_jeu_local    as p_local
import page_jeu_ia       as p_ia
import page_jeu_ia_vs_ia as p_ia2
import page_tournoi      as p_tournoi
import page_infos        as p_infos

if   page == "MENU":         p_menu.show()
elif page == "JEU_LOCAL":    p_local.show()
elif page == "JEU_IA":       p_ia.show()
elif page == "JEU_IA_VS_IA": p_ia2.show()
elif page == "TOURNOI":      p_tournoi.show()
elif page == "INFOS":        p_infos.show()
