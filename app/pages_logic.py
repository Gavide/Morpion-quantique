import streamlit as st
import pandas as pd
import quantum_engine as ql
import interface_game as gui
import visualizer as vis
import styles

# ─── Noms des IA disponibles pour le mode Ordinateur ───
IA_OPTIONS = {
    "🎲 Aléatoire":          "random",
    "⚛️ Grover Heuristique": "grover",
    "🌀 QAOA + Grover":      "qaoa",
    "🧠 Minimax Quantique":  "minimax_q",
}

def get_button_label(text, index):
    sign = "○" if index % 2 == 0 else "✕"
    return f"{sign}   {text}   {sign}"

# ════════════════════════════════════════════════════════════
# MENU PRINCIPAL
# ════════════════════════════════════════════════════════════

def show_menu():
    styles.apply_main_style()
    st.markdown('<h1 class="main-header">QUANTUM<br>TIC-TAC-TOE</h1>', unsafe_allow_html=True)

    _, col_center, _ = st.columns([0.3, 2, 0.3])
    with col_center:
        st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
        action = st.session_state.get("menu_action")

        if st.button(get_button_label("MULTIJOUEUR LOCAL", 0), use_container_width=True, key="btn_local"):
            st.session_state.menu_action = None if action == "LOCAL" else "LOCAL"
            st.rerun()

        if st.button(get_button_label("ORDINATEUR", 1), use_container_width=True, key="btn_ia"):
            st.session_state.menu_action = None if action == "IA" else "IA"
            st.rerun()

        col_inf, col_perso = st.columns(2)
        with col_inf:
            if st.button(get_button_label("INFORMATIONS", 2), use_container_width=True, key="btn_infos"):
                st.session_state.menu_action = None if action == "INFOS" else "INFOS"
                st.rerun()
        with col_perso:
            if st.button(get_button_label("PERSONNALISATION", 3), use_container_width=True, key="btn_perso"):
                st.session_state.menu_action = None if action == "PERSO" else "PERSO"
                st.rerun()

        styles.apply_button_styles(action)

        if action:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):

                # ── MULTIJOUEUR LOCAL ──
                if action == "LOCAL":
                    st.subheader("OPTIONS MULTIJOUEUR")
                    st.session_state.limite_N = st.slider(
                        "SEUIL DE SATURATION (N)", 1, 9, st.session_state.limite_N
                    )
                    c1, c2 = st.columns(2)
                    st.session_state.trigger_sat = c1.toggle("SATURATION", value=st.session_state.trigger_sat)
                    st.session_state.trigger_cyc = c2.toggle("CYCLES",     value=st.session_state.trigger_cyc)
                    if st.button(get_button_label("JOUER", 0), type="primary", use_container_width=True):
                        st.session_state.page = "JEU_LOCAL"
                        st.rerun()

                # ── ORDINATEUR ──
                elif action == "IA":
                    st.subheader("OPTIONS ORDINATEUR")

                    # Choix de qui commence
                    qui_commence = st.radio(
                        "Qui commence ?",
                        ["Joueur (X)", "Ordinateur (O)"],
                        horizontal=True,
                        key="radio_qui_commence"
                    )
                    st.session_state.ia_joueur_commence = (qui_commence == "Joueur (X)")

                    # Choix de l'IA
                    ia_label = st.selectbox(
                        "Algorithme IA",
                        list(IA_OPTIONS.keys()),
                        key="sel_ia_algo"
                    )
                    st.session_state.ia_algo = IA_OPTIONS[ia_label]

                    # Description de chaque IA
                    descriptions = {
                        "random":    "Choisit deux cases au hasard parmi les cases libres.",
                        "grover":    "Utilise une heuristique quantique + algorithme de Grover pour sélectionner la meilleure paire.",
                        "qaoa":      "QAOA évalue l'importance stratégique de chaque case, puis Grover sélectionne la meilleure paire.",
                        "minimax_q": "Minimax alpha-bêta adapté au jeu quantique : explore les paires de cases sur 2 niveaux.",
                    }
                    st.info(descriptions[IA_OPTIONS[ia_label]])

                    st.caption("2 cases / tour · Cycles activés")

                    if st.button(get_button_label("JOUER CONTRE L'IA", 0), type="primary", use_container_width=True):
                        st.session_state.page = "JEU_IA"
                        st.rerun()

                    st.divider()
                    st.subheader("IA vs IA")
                    c_x, c_o = st.columns(2)
                    with c_x:
                        ia_x_label = st.selectbox("IA X (joueur 1)", list(IA_OPTIONS.keys()), key="sel_ia_x")
                        st.session_state.ia_x_algo = IA_OPTIONS[ia_x_label]
                    with c_o:
                        ia_o_label = st.selectbox("IA O (joueur 2)", list(IA_OPTIONS.keys()), index=1, key="sel_ia_o")
                        st.session_state.ia_o_algo = IA_OPTIONS[ia_o_label]
                    if st.button(get_button_label("LANCER IA vs IA", 2), use_container_width=True):
                        st.session_state.page = "JEU_IA_VS_IA"
                        st.rerun()

                    st.divider()
                    st.subheader("Tournoi ELO")
                    st.caption("Round-robin entre les 4 IAs. Plus N est grand, plus les résultats sont fiables (et longs).")
                    st.session_state.tournoi_n = st.slider(
                        "Parties par match (N)", 1, 20,
                        st.session_state.get("tournoi_n", 3), 1,
                        key="sl_tournoi_n"
                    )
                    if st.button(get_button_label("LANCER LE TOURNOI", 0), use_container_width=True):
                        st.session_state.page = "TOURNOI"
                        st.rerun()

                # ── INFORMATIONS ──
                elif action == "INFOS":
                    st.subheader("DOCUMENTS DU PROJET")
                    st.write("Projet de Morpion Quantique utilisant Qiskit.")
                    if st.button(get_button_label("CONSULTER LE RAPPORT", 2), use_container_width=True):
                        st.session_state.page = "INFOS"
                        st.rerun()

                # ── PERSONNALISATION ──
                elif action == "PERSO":
                    st.subheader("PERSONNALISATION DES SKINS")
                    draw_compact_skin(1)
                    draw_compact_skin(2)


def draw_compact_skin(p_num):
    p = f"p{p_num}"
    st.markdown(f"#### JOUEUR {p_num}")
    c_n, c_c = st.columns([3, 1])
    with c_n:
        st.session_state[f'{p}_name'] = st.text_input(
            f"Pseudo J{p_num}", st.session_state[f'{p}_name'],
            key=f"n_{p}", label_visibility="collapsed"
        )
    with c_c:
        st.session_state[f'{p}_color'] = st.color_picker(
            "Couleur", st.session_state[f'{p}_color'],
            key=f"cp_{p}", label_visibility="collapsed"
        )
    c_img, c_url = st.columns([1, 4])
    with c_img:
        st.image(st.session_state[f'{p}_url'], width=45)
    with c_url:
        st.session_state[f'{p}_url'] = st.text_input(
            "URL Icon", st.session_state[f'{p}_url'],
            key=f"u_{p}", label_visibility="collapsed"
        )
    st.divider()


# ════════════════════════════════════════════════════════════
# JEU LOCAL (2 joueurs humains)
# ════════════════════════════════════════════════════════════

def show_game_local():
    styles.apply_main_style()
    with st.sidebar:
        if st.button(get_button_label("RETOUR AU MENU", 1), use_container_width=True, key="btn_retour"):
            st.session_state.page = "MENU"
            st.rerun()
        st.divider()
        st.write(f"PARAMÈTRES : N={st.session_state.limite_N}")
        st.write(f"SATURATION : {'✓' if st.session_state.trigger_sat else '✗'}")
        st.write(f"CYCLES : {'✓' if st.session_state.trigger_cyc else '✗'}")

    if st.session_state.winner is not None:
        gui.display_winner(st.session_state.winner)
        gui.show_replay_button()
    else:
        vis.display_psi(st.session_state.marques_q)
        gui.display_turn_indicator(st.session_state.active_player)

    col_game, col_hist = st.columns([2, 1])
    with col_game:
        case_clicked = gui.draw_grid_superposed(
            st.session_state.plateau, st.session_state.marques_q,
            st.session_state.limite_N, st.session_state.selection
        )
        if st.session_state.winner is None:
            _handle_click_local(case_clicked)
            _handle_validate_reset()

    with col_hist:
        st.subheader("HISTORIQUE")
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history).iloc[::-1])

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)


def _handle_click_local(case_clicked):
    if case_clicked and st.session_state.plateau[case_clicked[0]][case_clicked[1]] == 0:
        poids = sum(m[1].count(case_clicked) for m in st.session_state.marques_q)
        clics = st.session_state.selection.count(case_clicked)
        if not st.session_state.trigger_sat or (poids + clics) < st.session_state.limite_N:
            if len(st.session_state.selection) < st.session_state.limite_N:
                st.session_state.selection.append(case_clicked)
                st.rerun()


def _handle_validate_reset():
    nb, lim = len(st.session_state.selection), st.session_state.limite_N
    cv, cr = st.columns(2)
    with cv:
        if st.button(
            get_button_label(f"VALIDER ({nb}/{lim})", 0),
            use_container_width=True, type="primary", disabled=(nb < lim)
        ):
            _jouer_coup_et_resoudre(
                st.session_state.selection,
                st.session_state.active_player,
                st.session_state.limite_N,
                st.session_state.trigger_sat,
                st.session_state.trigger_cyc,
            )
    with cr:
        if st.button(get_button_label("RESET", 1), use_container_width=True, disabled=(nb == 0)):
            st.session_state.selection = []
            st.rerun()


def _jouer_coup_et_resoudre(selection, joueur, limite_N, trigger_sat, trigger_cyc):
    """Joue le coup, résout, met à jour l'historique et vérifie la victoire."""
    st.session_state.plateau, st.session_state.marques_q = ql.jouer_coup_quantum_multi(
        st.session_state.plateau, st.session_state.marques_q, st.session_state.qc,
        joueur, selection
    )
    st.session_state.plateau, st.session_state.marques_q, st.session_state.qc = ql.resoudre_par_saturation(
        st.session_state.plateau, st.session_state.marques_q, st.session_state.qc,
        limite_N, trigger_sat, trigger_cyc
    )
    mouv = " - ".join([f"({c[0]},{c[1]})" for c in selection])
    nom  = st.session_state.p1_name if joueur == 1 else st.session_state.p2_name
    st.session_state.history.append({
        "Tour": len(st.session_state.history) + 1, "Joueur": nom, "Liaisons": mouv
    })
    _verifier_et_finir()
    st.session_state.active_player *= -1
    st.session_state.selection = []
    st.rerun()


def _verifier_et_finir():
    wx = ql.verifier_victoire(st.session_state.plateau, 1)
    wo = ql.verifier_victoire(st.session_state.plateau, -1)
    if wx and wo:   st.session_state.winner = 0
    elif wx:        st.session_state.winner = 1
    elif wo:        st.session_state.winner = -1
    elif all(c != 0 for r in st.session_state.plateau for c in r):
        st.session_state.winner = 0


# ════════════════════════════════════════════════════════════
# JEU CONTRE L'IA
# ════════════════════════════════════════════════════════════

def show_game_ia():
    styles.apply_main_style()

    ia_algo         = st.session_state.get("ia_algo", "random")
    joueur_humain   = 1   # Le joueur humain joue toujours X (1)
    joueur_ia       = -1  # L'IA joue toujours O (-1)
    limite_N        = 2   # Mode IA : toujours 2 cases par coup
    trigger_sat     = False
    trigger_cyc     = True

    with st.sidebar:
        if st.button(get_button_label("RETOUR AU MENU", 1), use_container_width=True, key="btn_retour"):
            st.session_state.page = "MENU"
            st.rerun()
        st.divider()
        st.markdown(f"**Mode :** Joueur vs IA")
        st.markdown(f"**IA :** `{ia_algo}`")
        st.markdown("**Règles :** 2 cases / tour, cycles activés")
        st.divider()
        # Affiche qui est qui
        p1_name = st.session_state.get('p1_name', 'Joueur')
        st.markdown(f"🟦 **{p1_name}** → X")
        st.markdown(f"🔴 **Ordinateur** → O")

    if st.session_state.winner is not None:
        gui.display_winner(st.session_state.winner)
        gui.show_replay_button()
    else:
        vis.display_psi(st.session_state.marques_q)
        active = st.session_state.active_player
        if active == joueur_humain:
            gui.display_turn_indicator(joueur_humain)
        else:
            p2_color = st.session_state.get('p2_color', '#FF4B4B')
            st.markdown(
                f"<h3 style='color:{p2_color};border-left:5px solid {p2_color};padding-left:10px;'>"
                f"Tour : Ordinateur ({ia_algo})</h3>",
                unsafe_allow_html=True
            )

    col_game, col_hist = st.columns([2, 1])
    with col_game:
        active = st.session_state.active_player

        # ── Tour de l'IA ──
        if active == joueur_ia and st.session_state.winner is None:
            with st.spinner(f"L'IA ({ia_algo}) réfléchit..."):
                c1, c2 = _ia_jouer(
                    st.session_state.plateau, st.session_state.marques_q, ia_algo, joueur_ia
                )
            if c1 is not None:
                _jouer_coup_et_resoudre(
                    [c1, c2], joueur_ia, limite_N, trigger_sat, trigger_cyc
                )
            else:
                st.warning("L'IA n'a pas pu jouer (plus de cases disponibles).")
                st.session_state.winner = 0

        # ── Tour du joueur humain ──
        case_clicked = gui.draw_grid_superposed(
            st.session_state.plateau, st.session_state.marques_q,
            limite_N, st.session_state.selection
        )
        if active == joueur_humain and st.session_state.winner is None:
            if case_clicked and st.session_state.plateau[case_clicked[0]][case_clicked[1]] == 0:
                if len(st.session_state.selection) < limite_N:
                    st.session_state.selection.append(case_clicked)
                    st.rerun()

            nb = len(st.session_state.selection)
            cv, cr = st.columns(2)
            with cv:
                if st.button(
                    get_button_label(f"VALIDER ({nb}/{limite_N})", 0),
                    use_container_width=True, type="primary", disabled=(nb < limite_N)
                ):
                    _jouer_coup_et_resoudre(
                        st.session_state.selection, joueur_humain,
                        limite_N, trigger_sat, trigger_cyc
                    )
            with cr:
                if st.button(get_button_label("RESET", 1), use_container_width=True, disabled=(nb == 0)):
                    st.session_state.selection = []
                    st.rerun()

    with col_hist:
        st.subheader("HISTORIQUE")
        if st.session_state.history:
            st.table(pd.DataFrame(st.session_state.history).iloc[::-1])

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)


def _ia_jouer(plateau, marques_q, ia_algo, joueur_ia):
    """Délègue le choix de coup à l'algorithme IA sélectionné."""
    if ia_algo == "random":
        return ql.choisir_coup_random(plateau, marques_q)
    elif ia_algo == "grover":
        return ql.choisir_coup_ia_grover(plateau, marques_q, joueur_ia=joueur_ia, mode='heuristique_optimal')
    elif ia_algo == "qaoa":
        return ql.choisir_coup_ia_grover(plateau, marques_q, joueur_ia=joueur_ia, mode='qaoa')
    elif ia_algo == "minimax_q":
        return ql.choisir_coup_minimax_quantum(plateau, marques_q, joueur=joueur_ia, profondeur=2)
    else:
        return ql.choisir_coup_random(plateau, marques_q)


# ════════════════════════════════════════════════════════════
# JEU IA vs IA — les deux IA jouent en direct
# ════════════════════════════════════════════════════════════

def show_game_ia_vs_ia():
    styles.apply_main_style()

    ia_x = st.session_state.get("ia_x_algo", "random")
    ia_o = st.session_state.get("ia_o_algo", "grover")
    limite_N    = 2
    trigger_sat = False
    trigger_cyc = True

    with st.sidebar:
        if st.button(get_button_label("RETOUR AU MENU", 1), use_container_width=True, key="btn_retour"):
            st.session_state.page = "MENU"
            st.rerun()
        st.divider()
        st.markdown("**Mode :** IA vs IA")
        st.markdown(f"🟦 X → `{ia_x}`")
        st.markdown(f"🔴 O → `{ia_o}`")
        st.markdown("**Règles :** 2 cases / tour, cycles activés")
        st.divider()
        # Vitesse
        vitesse = st.slider("Délai entre coups (s)", 0.0, 3.0, 0.5, 0.1, key="sl_vitesse")

    # ── En-tête ──
    active = st.session_state.active_player

    if st.session_state.winner is not None:
        # Résultat final — on remplace les noms par les algos
        w = st.session_state.winner
        if w == 1:
            titre = f"🏆 {ia_x.upper()} (X) GAGNE !"
            couleur = "#1C83E1"
        elif w == -1:
            titre = f"🏆 {ia_o.upper()} (O) GAGNE !"
            couleur = "#FF4B4B"
        else:
            titre = "🤝 MATCH NUL"
            couleur = "#444"
        st.markdown(
            f'<div style="background:{couleur};padding:20px;border-radius:15px;'
            f'text-align:center;margin-bottom:20px;">'
            f'<h1 style="color:white;margin:0;">{titre}</h1></div>',
            unsafe_allow_html=True
        )
        # Replay
        if st.button("🔄 REJOUER", use_container_width=True, type="primary"):
            keys_to_keep = ['ia_x_algo','ia_o_algo','p1_color','p2_color','p1_url','p2_url']
            kept = {k: st.session_state[k] for k in keys_to_keep if k in st.session_state}
            st.session_state.clear()
            st.session_state.update(kept)
            st.rerun()

    else:
        vis.display_psi(st.session_state.marques_q)

        # Indicateur de tour (style coloré par algo)
        p1_color = st.session_state.get('p1_color', '#1C83E1')
        p2_color = st.session_state.get('p2_color', '#FF4B4B')
        if active == 1:
            color, label = p1_color, f"Tour : {ia_x.upper()} (X)"
        else:
            color, label = p2_color, f"Tour : {ia_o.upper()} (O)"
        st.markdown(
            f"<h3 style='color:{color};border-left:5px solid {color};padding-left:10px;'>"
            f"{label}</h3>",
            unsafe_allow_html=True
        )

    col_game, col_hist = st.columns([2, 1])
    with col_game:
        # Grille (désactivée — lecture seule)
        gui.draw_grid_superposed(
            st.session_state.plateau, st.session_state.marques_q,
            limite_N, []   # Pas de sélection possible
        )

        # Joue automatiquement le prochain coup
        if st.session_state.winner is None:
            algo_actif = ia_x if active == 1 else ia_o

            import time
            time.sleep(vitesse)

            with st.spinner(f"`{algo_actif}` réfléchit..."):
                c1, c2 = _ia_jouer(
                    st.session_state.plateau, st.session_state.marques_q,
                    algo_actif, active
                )

            if c1 is not None:
                st.session_state.plateau, st.session_state.marques_q = ql.jouer_coup_quantum_multi(
                    st.session_state.plateau, st.session_state.marques_q, st.session_state.qc,
                    active, [c1, c2]
                )
                st.session_state.plateau, st.session_state.marques_q, st.session_state.qc = ql.resoudre_par_saturation(
                    st.session_state.plateau, st.session_state.marques_q, st.session_state.qc,
                    limite_N, trigger_sat, trigger_cyc
                )
                nom = f"{ia_x} (X)" if active == 1 else f"{ia_o} (O)"
                mouv = f"({c1[0]},{c1[1]}) - ({c2[0]},{c2[1]})"
                st.session_state.history.append({
                    "Tour": len(st.session_state.history) + 1,
                    "IA":   nom,
                    "Coup": mouv,
                })
                _verifier_et_finir()
                st.session_state.active_player *= -1
            else:
                st.session_state.winner = 0

            st.rerun()

    with col_hist:
        st.subheader("HISTORIQUE")
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history).iloc[::-1]
            st.table(df)

    st.divider()
    vis.display_hardware_registry(st.session_state.plateau, st.session_state.marques_q)


# ════════════════════════════════════════════════════════════
# PAGE INFOS
# ════════════════════════════════════════════════════════════

def show_infos():
    styles.apply_main_style()
    if st.button(get_button_label("RETOUR AU MENU", 1)):
        st.session_state.page = "MENU"
        st.rerun()
    st.markdown("<h1 class='center-text'>DOCUMENTS DU PROJET</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["ENONCE", "RAPPORT FINAL", "PARTICIPATION"])
    with t1:
        st.info("Placez ici l'énoncé de votre projet de Morpion Quantique.")
    with t2:
        st.success("Insérez ici votre rapport technique et vos conclusions.")
    with t3:
        st.markdown("#### Membres du projet")
        st.write("Ajoutez ici les noms des participants, leurs rôles et contributions.")


# ════════════════════════════════════════════════════════════
# PAGE TOURNOI ELO
# ════════════════════════════════════════════════════════════

def show_tournoi():
    styles.apply_main_style()

    with st.sidebar:
        if st.button(get_button_label("RETOUR AU MENU", 1), use_container_width=True, key="btn_retour"):
            st.session_state.page = "MENU"
            st.rerun()
        st.divider()
        n_parties = st.session_state.get("tournoi_n", 3)
        st.markdown(f"**Parties / match :** {n_parties}")
        st.markdown("**4 IAs :** Random · Grover · QAOA · Minimax Q")
        st.markdown("**6 matchs** au total (round-robin)")

    st.markdown("<h2>Tournoi ELO — Quantum Tic-Tac-Toe</h2>", unsafe_allow_html=True)

    noms = {
        'random':    'Random',
        'grover':    'Grover',
        'qaoa':      'QAOA',
        'minimax_q': 'Minimax Q',
    }
    ias = list(noms.keys())
    n_parties = st.session_state.get("tournoi_n", 3)

    # ── Zones d'affichage ──────────────────────────────────
    prog_bar    = st.progress(0, text="En attente...")
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Matchs en cours")
        log_area = st.empty()

    with col_right:
        st.subheader("Classement ELO live")
        rank_area = st.empty()

    # ── Lancement ─────────────────────────────────────────
    log_lines = []
    n_matchs  = len(ias) * (len(ias) - 1) // 2

    def on_progression(match_num, total, ia1, ia2, elo_snapshot, stats_snapshot):
        pct = match_num / total
        prog_bar.progress(pct, text=f"Match {match_num}/{total} terminé")

        score_ia1 = f"{elo_snapshot[ia1]:.0f}"
        score_ia2 = f"{elo_snapshot[ia2]:.0f}"
        s1 = stats_snapshot[ia1]
        s2 = stats_snapshot[ia2]
        log_lines.append(
            f"**{noms[ia1]}** vs **{noms[ia2]}** — "
            f"ELO : {score_ia1} / {score_ia2} — "
            f"{s1['V']}V {s1['N']}N {s1['D']}D · {s2['V']}V {s2['N']}N {s2['D']}D"
        )
        log_area.markdown("\n\n".join(log_lines[-6:]))

        # Classement live
        classement_live = sorted(ias, key=lambda ia: elo_snapshot[ia], reverse=True)
        rows = []
        for rang, ia in enumerate(classement_live, 1):
            s = stats_snapshot[ia]
            rows.append({
                "Rang": f"#{rang}",
                "IA":   noms[ia],
                "ELO":  f"{elo_snapshot[ia]:.0f}",
                "V":    s['V'],
                "N":    s['N'],
                "D":    s['D'],
            })
        rank_area.table(pd.DataFrame(rows))

    with st.spinner("Tournoi en cours... (peut prendre plusieurs minutes selon N et les algos)"):
        elo, stats, classement, historique_elo = ql.tournoi_round_robin_elo(
            n_parties, callback_progression=on_progression
        )

    # Tournoi terminé — remplacer le live par le résultat final propre
    prog_bar.progress(1.0, text="Tournoi terminé !")
    log_area.empty()
    rank_area.empty()

    # ── Résultats finaux ───────────────────────────────────
    st.divider()
    st.subheader("Classement Final")

    rows_final = []
    for rang, ia in enumerate(classement, 1):
        s = stats[ia]
        rows_final.append({
            "Rang":  f"#{rang}",
            "IA":    noms[ia],
            "ELO":   f"{elo[ia]:.0f}",
            "V":     s['V'],
            "N":     s['N'],
            "D":     s['D'],
        })
    st.table(pd.DataFrame(rows_final))

    # ── Graphique évolution ELO ────────────────────────────
    st.subheader("Evolution ELO")
    try:
        import plotly.graph_objects as go
        couleurs = {'random': '#95a5a6', 'grover': '#3498db', 'qaoa': '#9b59b6', 'minimax_q': '#e74c3c'}
        fig = go.Figure()
        for ia in ias:
            fig.add_trace(go.Scatter(
                y=historique_elo[ia], name=noms[ia],
                line=dict(color=couleurs[ia], width=2),
                mode='lines'
            ))
        fig.add_hline(y=1000, line_dash="dash", line_color="gray", opacity=0.5, annotation_text="ELO initial")
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.3)',
            font_color='white', xaxis_title="Parties jouées", yaxis_title="ELO",
            legend=dict(bgcolor='rgba(0,0,0,0.5)'),
            height=350, margin=dict(t=20, b=40)
        )
        fig.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        import io
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#111')
            ax.set_facecolor('#111')
            cols_mpl = {'random':'#95a5a6','grover':'#3498db','qaoa':'#9b59b6','minimax_q':'#e74c3c'}
            for ia in ias:
                ax.plot(historique_elo[ia], label=noms[ia], color=cols_mpl[ia], linewidth=2)
            ax.axhline(1000, color='gray', linestyle='--', alpha=0.5)
            ax.set_xlabel('Parties jouées', color='white')
            ax.set_ylabel('ELO', color='white')
            ax.tick_params(colors='white')
            ax.legend()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', facecolor='#111')
            st.image(buf)
        except Exception:
            st.info("Graphique non disponible (installez plotly ou matplotlib).")