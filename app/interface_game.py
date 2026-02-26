import streamlit as st

def _case_bloquee(case, selection, marques_q, limite_N, trigger_sat, plateau):
    """Même logique que _can_click mais sans dépendance Streamlit."""
    if plateau[case[0]][case[1]] != 0:
        return True
    poids_existant = sum(m[1].count(case) for m in marques_q)
    clics_dans_sel = selection.count(case)
    if trigger_sat:
        return poids_existant + clics_dans_sel + 1 > limite_N
    est_dernier_clic = (len(selection) == limite_N - 1)
    if not est_dernier_clic:
        return False
    cases_du_tour = selection + [case]
    if len(set(cases_du_tour)) == 1:
        total = poids_existant + len(cases_du_tour)
        if total > limite_N:
            return True
    return False


def draw_grid(plateau, marques_q, limite_N, selection):
    p1_url   = st.session_state.get('p1_url',   "https://img.icons8.com/color/96/filled-circle.png")
    p2_url   = st.session_state.get('p2_url',   "https://img.icons8.com/color/96/close-window.png")
    p1_color = st.session_state.get('p1_color', "#1C83E1")
    p2_color = st.session_state.get('p2_color', "#FF4B4B")
    active   = st.session_state.get('active_player', 1)
    pcol     = p1_color if active == 1 else p2_color
    winning  = st.session_state.get('winning_cells', [])
    winner   = st.session_state.get('winner', None)
    win_col  = (p1_color if winner == 1 else p2_color) if winner else None

    # CSS grille : boutons petits, fond sombre, texte visible
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        height:22px!important; min-height:22px!important;
        font-size:10px!important; font-weight:500!important;
        padding:0 4px!important; line-height:1!important;
        background:#1a1a1a!important;
        border:1px solid rgba(255,255,255,0.18)!important;
        color:rgba(210,210,210,0.85)!important;
        border-radius:3px!important;
        letter-spacing:0!important; text-transform:none!important;
        box-shadow:none!important;
        transition:background 0.15s,color 0.15s!important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:hover {
        background:#2a2a2a!important;
        color:#fff!important;
        border-color:rgba(255,255,255,0.4)!important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button:disabled {
        opacity:0.18!important; cursor:default!important;
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    clicked = None

    for idx in range(9):
        i, j = idx // 3, idx % 3
        case = (i, j)
        with cols[j]:
            val = plateau[i][j]
            mici = [m for m in marques_q if case in m[1]]
            cx = sum(m[1].count(case) for m in mici if m[0] ==  1)
            co = sum(m[1].count(case) for m in mici if m[0] == -1)
            tp = cx + co

            trigger_sat = st.session_state.get('trigger_sat', False)
            bloquee = _case_bloquee(case, selection, marques_q, limite_N, trigger_sat, plateau)

            if val != 0:
                ox, oo = (1, 0) if val == 1 else (0, 1)
            else:
                ox = cx / limite_N if limite_N else 0
                oo = co / limite_N if limite_N else 0

            sel_n = selection.count(case)

            # Bordure : gagnante > sélectionnée > bloquée > normale
            if case in winning and win_col:
                border = f"3px solid {win_col}"
                glow   = f"box-shadow:0 0 16px {win_col},0 0 32px {win_col}80;"
            elif sel_n > 0:
                border = f"2px solid {pcol}"
                glow   = ""
            elif bloquee and val == 0:
                border = "1px solid #550000"
                glow   = ""
            else:
                border = "1px solid #333"
                glow   = ""

            badge = (
                f'<div style="position:absolute;top:2px;left:2px;'
                f'background:{pcol};color:#fff;font-size:10px;'
                f'padding:1px 4px;border-radius:3px;z-index:5;">{sel_n}×</div>'
            ) if sel_n > 0 else ""

            # Overlay rouge sur les cases bloquées (saturation)
            blocked_overlay = (
                f'<div style="position:absolute;inset:0;border-radius:8px;'
                f'background:rgba(180,0,0,0.18);z-index:3;'
                f'display:flex;align-items:center;justify-content:center;">'
                f'<span style="color:#ff4444;font-size:18px;font-weight:900;opacity:0.7;">✕</span>'
                f'</div>'
            ) if bloquee and val == 0 else ""

            bg = "rgba(40,0,0,0.35)" if bloquee and val == 0 else "rgba(255,255,255,0.02)"

            st.markdown(
                f'<div style="position:relative;width:100%;height:100px;'
                f'border:{border};border-radius:8px;{glow}'
                f'background:{bg};'
                f'display:flex;justify-content:center;align-items:center;">'
                f'{badge}'
                f'{blocked_overlay}'
                f'<img src="{p1_url}" style="position:absolute;width:58px;opacity:{ox};">'
                f'<img src="{p2_url}" style="position:absolute;width:58px;opacity:{oo};">'
                f'<div style="position:absolute;bottom:3px;right:6px;'
                f'font-size:10px;color:#666;">{tp}/{limite_N}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if st.button(f"{i},{j}", key=f"g_{idx}", disabled=(val != 0 or bloquee), use_container_width=True):
                clicked = case

    return clicked


def turn_indicator(player):
    name  = st.session_state.get('p1_name', 'Joueur 1') if player == 1 else st.session_state.get('p2_name', 'Joueur 2')
    color = st.session_state.get('p1_color', '#1C83E1') if player == 1 else st.session_state.get('p2_color', '#FF4B4B')
    st.markdown(
        f"<h3 style='color:{color};border-left:5px solid {color};padding-left:10px;margin-top:4px;'>"
        f"Tour : {name}</h3>", unsafe_allow_html=True)


def winner_banner(winner):
    p1n = st.session_state.get('p1_name', 'Joueur 1')
    p2n = st.session_state.get('p2_name', 'Joueur 2')
    p1c = st.session_state.get('p1_color', '#1C83E1')
    p2c = st.session_state.get('p2_color', '#FF4B4B')
    if winner == 0:
        color, title, sub = "#222", "MATCH NUL", "Égalité parfaite."
    else:
        color = p1c if winner == 1 else p2c
        name  = p1n if winner == 1 else p2n
        title, sub = f"VICTOIRE : {name}", "Félicitations !"
        st.balloons()
    st.markdown(
        f'<div style="background:{color};padding:20px;border-radius:12px;'
        f'text-align:center;margin-bottom:16px;">'
        f'<h1 style="color:white;margin:0;">{title}</h1>'
        f'<p style="color:white;opacity:0.75;margin:4px 0 0;">{sub}</p></div>',
        unsafe_allow_html=True)


def replay_button():
    if st.button("NOUVELLE PARTIE", use_container_width=True, type="primary"):
        keep = ['p1_name', 'p2_name', 'p1_color', 'p2_color', 'p1_url', 'p2_url',
                'ia_algo', 'ia_joueur_commence', 'ia_x_algo', 'ia_o_algo', 'tournoi_n']
        kept = {k: st.session_state[k] for k in keep if k in st.session_state}
        st.session_state.clear()
        st.session_state.update(kept)
        st.rerun()