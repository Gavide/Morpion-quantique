import streamlit as st
import styles
import retour
import interface_game as gui
import visualizer as vis
from page_common import btn, jouer_coup_et_resoudre

def show():
    styles.apply_game_buttons()
    retour.bouton_retour(
        f"N={st.session_state.limite_N} &nbsp;|&nbsp; "
        f"Sat:{'✓' if st.session_state.trigger_sat else '✗'} &nbsp;|&nbsp; "
        f"Cycles:{'✓' if st.session_state.trigger_cyc else '✗'}"
    )

    if st.session_state.winner is not None:
        gui.winner_banner(st.session_state.winner)
        gui.replay_button()
    else:
        gui.turn_indicator(st.session_state.active_player)

    cg, ch = st.columns([2, 1])
    with cg:
        clicked = gui.draw_grid(
            st.session_state.plateau, st.session_state.marques_q,
            st.session_state.limite_N, st.session_state.selection)

        if st.session_state.winner is None:
            if clicked and st.session_state.plateau[clicked[0]][clicked[1]] == 0:
                poids = sum(m[1].count(clicked) for m in st.session_state.marques_q)
                clics = st.session_state.selection.count(clicked)
                if not st.session_state.trigger_sat or (poids + clics) < st.session_state.limite_N:
                    if len(st.session_state.selection) < st.session_state.limite_N:
                        st.session_state.selection.append(clicked)
                        st.rerun()

            nb, lim = len(st.session_state.selection), st.session_state.limite_N
            cv, cr = st.columns(2)
            with cv:
                if st.button(btn(f"VALIDER ({nb}/{lim})", 0), use_container_width=True,
                             type="primary", disabled=(nb < lim)):
                    jouer_coup_et_resoudre(st.session_state.selection,
                        st.session_state.active_player, lim,
                        st.session_state.trigger_sat, st.session_state.trigger_cyc)
            with cr:
                if st.button(btn("RESET", 1), use_container_width=True, disabled=(nb == 0)):
                    st.session_state.selection = []
                    st.rerun()

    with ch:
        vis.display_psi(st.session_state.marques_q)

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)