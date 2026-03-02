import streamlit as st
import time
import styles
import retour
import interface_game as gui
import visualizer as vis
from page_common import ia_jouer, jouer_coup_et_resoudre

LIM, SAT, CYC = 2, False, True
NOMS = {'random':'Random','grover':'Grover','qaoa':'QAOA','minimax_q':'Minimax Q'}

def show():
    styles.apply_game_buttons()
    ia_x    = st.session_state.get("ia_x_algo", "random")
    ia_o    = st.session_state.get("ia_o_algo", "grover")
    vitesse = st.session_state.get("sl_v", 0.5)
    active  = st.session_state.active_player

    retour.bouton_retour(f"{NOMS[ia_x]} (○) vs {NOMS[ia_o]} (✕)")
    vitesse = st.slider("Délai entre coups (s)", 0.0, 3.0, 0.5, 0.1, key="sl_v")

    # ── Bandeau statut ─────────────────────────────────────────
    if st.session_state.winner is not None:
        w = st.session_state.winner
        if   w ==  1: titre, couleur = f"{NOMS[ia_x]} (○) GAGNE !", st.session_state.get('p1_color','#1C83E1')
        elif w == -1: titre, couleur = f"{NOMS[ia_o]} (✕) GAGNE !", st.session_state.get('p2_color','#FF4B4B')
        else:         titre, couleur = "MATCH NUL", "#333"
        st.markdown(
            f'<div style="background:{couleur};padding:20px;border-radius:12px;'
            f'text-align:center;margin-bottom:16px;">'
            f'<h1 style="color:white;margin:0;">{titre}</h1></div>',
            unsafe_allow_html=True)
        if st.button("REJOUER", use_container_width=True, type="primary"):
            keep = ['ia_x_algo','ia_o_algo','p1_color','p2_color','p1_url','p2_url',
                    'p1_name','p2_name','limite_N','trigger_sat','trigger_cyc','page']
            kept = {k: st.session_state[k] for k in keep if k in st.session_state}
            st.session_state.clear()
            st.session_state.update(kept)
            st.session_state.active_player = 1
            st.rerun()
    else:
        p1c   = st.session_state.get('p1_color', '#1C83E1')
        p2c   = st.session_state.get('p2_color', '#FF4B4B')
        color = p1c if active == 1 else p2c
        sym   = "○" if active == 1 else "✕"
        nom   = NOMS[ia_x] if active == 1 else NOMS[ia_o]
        st.markdown(
            f"<h3 style='color:{color};border-left:5px solid {color};padding-left:10px;'>"
            f"Tour : {nom} ({sym})</h3>", unsafe_allow_html=True)

    # ── Grille + historique + circuit ──────────────────────────
    cg, ch = st.columns([2, 1])
    with cg:
        gui.draw_grid(st.session_state.plateau, st.session_state.marques_q, LIM, [])
    with ch:
        vis.display_psi(st.session_state.marques_q)

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)

    # ── Calcul IA APRÈS rendu complet ─────────────────────────
    if st.session_state.winner is None:
        algo = ia_x if active == 1 else ia_o
        nom  = NOMS[ia_x] if active == 1 else NOMS[ia_o]
        sym  = "○" if active == 1 else "✕"
        time.sleep(vitesse)
        with st.spinner(f"{nom} ({sym}) réfléchit..."):
            c1, c2 = ia_jouer(st.session_state.plateau, st.session_state.marques_q,
                              algo, active, limite_N=LIM, trigger_sat=SAT)
        if c1 is not None:
            jouer_coup_et_resoudre([c1, c2], active, LIM, SAT, CYC)
        else:
            st.session_state.winner = 0
            st.rerun()