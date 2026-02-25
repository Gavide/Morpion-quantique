import streamlit as st
import styles
import retour
import interface_game as gui
import visualizer as vis
from page_common import btn, jouer_coup_et_resoudre, ia_jouer

LIM, SAT, CYC = 2, False, True

def show():
    styles.apply_game_buttons()
    ia_algo = st.session_state.get("ia_algo", "random")
    JH, JIA = 1, -1

    p1n = st.session_state.get('p1_name', 'Joueur')
    retour.bouton_retour(f"IA : <code>{ia_algo}</code> &nbsp;|&nbsp; {p1n} vs Ordinateur")

    if st.session_state.winner is not None:
        gui.winner_banner(st.session_state.winner)
        gui.replay_button()
    else:
        active = st.session_state.active_player
        if active == JH:
            gui.turn_indicator(JH)
        else:
            p2c = st.session_state.get('p2_color', '#FF4B4B')
            st.markdown(
                f"<h3 style='color:{p2c};border-left:5px solid {p2c};padding-left:10px;'>"
                f"Tour : Ordinateur ({ia_algo})</h3>", unsafe_allow_html=True)

    cg, ch = st.columns([2, 1])
    with cg:
        active = st.session_state.active_player

        if active == JIA and st.session_state.winner is None:
            with st.spinner(f"L'IA ({ia_algo}) réfléchit..."):
                c1, c2 = ia_jouer(st.session_state.plateau, st.session_state.marques_q, ia_algo, JIA)
            if c1 is not None:
                jouer_coup_et_resoudre([c1, c2], JIA, LIM, SAT, CYC)
            else:
                st.session_state.winner = 0
                st.rerun()

        clicked = gui.draw_grid(
            st.session_state.plateau, st.session_state.marques_q,
            LIM, st.session_state.selection)

        if active == JH and st.session_state.winner is None:
            if clicked and st.session_state.plateau[clicked[0]][clicked[1]] == 0:
                if len(st.session_state.selection) < LIM:
                    st.session_state.selection.append(clicked)
                    st.rerun()
            nb = len(st.session_state.selection)
            cv, cr = st.columns(2)
            with cv:
                if st.button(btn(f"VALIDER ({nb}/{LIM})", 0), use_container_width=True,
                             type="primary", disabled=(nb < LIM)):
                    jouer_coup_et_resoudre(st.session_state.selection, JH, LIM, SAT, CYC)
            with cr:
                if st.button(btn("RESET", 1), use_container_width=True, disabled=(nb == 0)):
                    st.session_state.selection = []
                    st.rerun()

    with ch:
        vis.display_psi(st.session_state.marques_q)

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)
