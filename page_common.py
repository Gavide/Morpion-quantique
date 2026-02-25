"""Utilitaires partagés entre toutes les pages."""
import streamlit as st
import quantum_engine as ql

def btn(text, index):
    sign = "○" if index % 2 == 0 else "✕"
    return f"{sign}   {text}   {sign}"

def _snapshot_plateau():
    """Copie du plateau avant coup."""
    return [row[:] for row in st.session_state.plateau]

def jouer_coup_et_resoudre(selection, joueur, limite_N, trigger_sat, trigger_cyc):
    plateau_avant = _snapshot_plateau()
    marques_avant = list(st.session_state.marques_q)
    num_coup = len(st.session_state.history) + 1

    st.session_state.plateau, st.session_state.marques_q = ql.jouer_coup_quantum_multi(
        st.session_state.plateau, st.session_state.marques_q,
        st.session_state.qc, joueur, selection
    )

    plateau_apres_coup = _snapshot_plateau()
    marques_apres_coup = list(st.session_state.marques_q)

    st.session_state.plateau, st.session_state.marques_q, st.session_state.qc = \
        ql.resoudre_par_saturation(
            st.session_state.plateau, st.session_state.marques_q,
            st.session_state.qc, limite_N, trigger_sat, trigger_cyc
        )

    # Déterminer si des cases ont été effondrées
    effondrement = (st.session_state.marques_q != marques_apres_coup or
                    st.session_state.plateau != plateau_apres_coup)

    # Enregistrer le coup (même si classique, même si effondrement)
    nom = st.session_state.p1_name if joueur == 1 else st.session_state.p2_name
    sym = "○" if joueur == 1 else "✕"
    cases_str = " + ".join([f"({c[0]},{c[1]})" for c in selection])

    # Détecter les cases qui ont été classifiées (effondrées)
    effondrees = []
    for i in range(3):
        for j in range(3):
            if plateau_avant[i][j] == 0 and st.session_state.plateau[i][j] != 0:
                effondrees.append((i, j))

    st.session_state.history.append({
        "num":         num_coup,
        "joueur":      joueur,
        "nom":         nom,
        "sym":         sym,
        "cases":       list(selection),
        "effondrement": effondrees,  # cases qui ont collapsé ce tour
        "barre":       False,        # sera True si ce coup est effondré plus tard
    })

    # Marquer les coups précédents dont les cases ont collapsé
    for entry in st.session_state.history[:-1]:
        if not entry["barre"]:
            for c in entry["cases"]:
                if c in effondrees:
                    entry["barre"] = True
                    break

    verifier_fin()
    st.session_state.active_player *= -1
    st.session_state.selection = []
    st.rerun()

def verifier_fin():
    wx = ql.verifier_victoire(st.session_state.plateau, 1)
    wo = ql.verifier_victoire(st.session_state.plateau, -1)
    if wx and wo:
        st.session_state.winner = 0
        st.session_state.winning_cells = []
    elif wx:
        st.session_state.winner = 1
        st.session_state.winning_cells = ql.cases_gagnantes(st.session_state.plateau, 1)
    elif wo:
        st.session_state.winner = -1
        st.session_state.winning_cells = ql.cases_gagnantes(st.session_state.plateau, -1)
    elif all(c != 0 for r in st.session_state.plateau for c in r):
        st.session_state.winner = 0
        st.session_state.winning_cells = []

def ia_jouer(plateau, marques_q, ia_algo, joueur_ia):
    if ia_algo == "random":
        return ql.choisir_coup_random(plateau, marques_q)
    elif ia_algo == "grover":
        return ql.choisir_coup_ia_grover(plateau, marques_q, joueur_ia=joueur_ia, mode='heuristique_optimal')
    elif ia_algo == "qaoa":
        return ql.choisir_coup_ia_grover(plateau, marques_q, joueur_ia=joueur_ia, mode='qaoa')
    elif ia_algo == "minimax_q":
        return ql.choisir_coup_minimax_quantum(plateau, marques_q, joueur=joueur_ia, profondeur=2)
    return ql.choisir_coup_random(plateau, marques_q)