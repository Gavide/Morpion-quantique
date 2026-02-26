import streamlit as st
import styles
import retour
import interface_game as gui
import visualizer as vis
from page_common import btn, jouer_coup_et_resoudre


def _can_click(case, selection, marques_q, limite_N, trigger_sat):
    """
    Peut-on ajouter `case` à la sélection ?

    Saturation ON  : total existant + ce qu'on a déjà sélectionné + 1 <= N.

    Saturation OFF : on ne peut pas concentrer TOUTES les marques du tour
                     sur une seule case si ça dépasserait N.
                     La vérification se fait seulement quand c'est le DERNIER
                     clic du tour (len(selection) == limite_N - 1), car avant
                     ça, le joueur peut encore placer ses autres marques ailleurs.
    """
    if st.session_state.plateau[case[0]][case[1]] != 0:
        return False  # case déjà effondrée (classique)

    poids_existant = sum(m[1].count(case) for m in marques_q)
    clics_dans_sel = selection.count(case)

    if trigger_sat:
        # Strict : jamais dépasser N
        return poids_existant + clics_dans_sel + 1 <= limite_N

    # Saturation OFF :
    # On ne vérifie la règle que sur le DERNIER clic du tour.
    # Avant ça, le joueur a encore des coups à placer — il peut toujours
    # mettre le suivant ailleurs.
    est_dernier_clic = (len(selection) == limite_N - 1)
    if not est_dernier_clic:
        return True  # pas encore le dernier → toujours OK

    # Dernier clic : si TOUTES les marques du tour finissent sur `case`
    # et que ça dépasse N → interdit.
    cases_du_tour = selection + [case]
    toutes_sur_meme_case = (len(set(cases_du_tour)) == 1)

    if toutes_sur_meme_case:
        total = poids_existant + len(cases_du_tour)
        if total > limite_N:
            return False

    return True


def show():
    styles.apply_game_buttons()
    retour.bouton_retour(
        f"N={st.session_state.limite_N} &nbsp;|&nbsp; "
        f"Sat:{'✓' if st.session_state.trigger_sat else '✗'} &nbsp;|&nbsp; "
        f"Cycles:{'✓' if st.session_state.trigger_cyc else '✗'}",
        avec_reset=True
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
            if clicked:
                if (len(st.session_state.selection) < st.session_state.limite_N and
                        _can_click(clicked, st.session_state.selection,
                                   st.session_state.marques_q,
                                   st.session_state.limite_N,
                                   st.session_state.trigger_sat)):
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