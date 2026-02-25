import streamlit as st
import time
import styles
import retour
import interface_game as gui
import visualizer as vis
import quantum_engine as ql
from page_common import verifier_fin, ia_jouer

LIM, SAT, CYC = 2, False, True
NOMS = {'random':'Random','grover':'Grover','qaoa':'QAOA','minimax_q':'Minimax Q'}

def show():
    styles.apply_game_buttons()
    ia_x = st.session_state.get("ia_x_algo", "random")
    ia_o = st.session_state.get("ia_o_algo", "grover")
    vitesse = st.session_state.get("_vitesse", 0.5)
    active  = st.session_state.active_player

    retour.bouton_retour(f"{NOMS[ia_x]} (X) vs {NOMS[ia_o]} (O)")

    # Contrôle vitesse dans la page
    vitesse = st.slider("Délai entre coups (s)", 0.0, 3.0, 0.5, 0.1, key="sl_v")

    if st.session_state.winner is not None:
        w = st.session_state.winner
        if   w ==  1: titre, couleur = f"{NOMS[ia_x]} (X) GAGNE !", "#1C83E1"
        elif w == -1: titre, couleur = f"{NOMS[ia_o]} (O) GAGNE !", "#FF4B4B"
        else:         titre, couleur = "MATCH NUL", "#333"
        st.markdown(
            f'<div style="background:{couleur};padding:20px;border-radius:12px;'
            f'text-align:center;margin-bottom:16px;">'
            f'<h1 style="color:white;margin:0;">{titre}</h1></div>',
            unsafe_allow_html=True)
        if st.button("REJOUER", use_container_width=True, type="primary"):
            keep = ['ia_x_algo','ia_o_algo','p1_color','p2_color','p1_url','p2_url']
            kept = {k: st.session_state[k] for k in keep if k in st.session_state}
            st.session_state.clear()
            st.session_state.update(kept)
            st.rerun()
    else:
        p1c = st.session_state.get('p1_color', '#1C83E1')
        p2c = st.session_state.get('p2_color', '#FF4B4B')
        color = p1c if active == 1 else p2c
        label = f"Tour : {NOMS[ia_x]} (X)" if active == 1 else f"Tour : {NOMS[ia_o]} (O)"
        st.markdown(
            f"<h3 style='color:{color};border-left:5px solid {color};padding-left:10px;'>"
            f"{label}</h3>", unsafe_allow_html=True)

    cg, ch = st.columns([2, 1])
    with cg:
        gui.draw_grid(st.session_state.plateau, st.session_state.marques_q, LIM, [])

        if st.session_state.winner is None:
            algo = ia_x if active == 1 else ia_o
            time.sleep(vitesse)
            with st.spinner(f"`{algo}` réfléchit..."):
                c1, c2 = ia_jouer(st.session_state.plateau, st.session_state.marques_q, algo, active)
            if c1 is not None:
                st.session_state.plateau, st.session_state.marques_q = ql.jouer_coup_quantum_multi(
                    st.session_state.plateau, st.session_state.marques_q,
                    st.session_state.qc, active, [c1, c2])
                st.session_state.plateau, st.session_state.marques_q, st.session_state.qc = \
                    ql.resoudre_par_saturation(st.session_state.plateau, st.session_state.marques_q,
                        st.session_state.qc, LIM, SAT, CYC)
                nom = f"{NOMS[ia_x]} (X)" if active == 1 else f"{NOMS[ia_o]} (O)"
                st.session_state.history.append({
                    "Tour": len(st.session_state.history) + 1,
                    "IA":   nom,
                    "Coup": f"({c1[0]},{c1[1]}) - ({c2[0]},{c2[1]})"})
                verifier_fin()
                st.session_state.active_player *= -1
            else:
                st.session_state.winner = 0
            st.rerun()

    with ch:
        vis.display_psi(st.session_state.marques_q)

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)
