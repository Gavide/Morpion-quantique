import streamlit as st

_TITRE = ('font-size:10px;text-transform:uppercase;letter-spacing:2px;'
          'color:#444;font-weight:600;')

def display_psi(marques_q):
    """Historique des coups — barré si effondré, avec coups classiques."""
    p1c = st.session_state.get('p1_color', '#1C83E1')
    p2c = st.session_state.get('p2_color', '#FF4B4B')
    history = st.session_state.get('history', [])

    st.markdown(f'<div style="margin-bottom:4px;"><span style="{_TITRE}">Historique des coups</span></div>',
                unsafe_allow_html=True)

    if not history:
        st.markdown(
            '<div style="font-family:monospace;color:#555;font-size:12px;'
            'padding:6px 10px;border-left:3px solid #222;margin-bottom:8px;">'
            'Aucun coup joué</div>', unsafe_allow_html=True)
        return

    lignes = []
    for entry in reversed(history):
        color  = p1c if entry['joueur'] == 1 else p2c
        sym    = entry['sym']
        nom    = entry['nom']
        cases  = entry['cases']
        barre  = entry.get('barre', False)
        effondrees = entry.get('effondrement', [])

        cases_str = " + ".join([f"({c[0]},{c[1]})" for c in cases])

        # Indicateur d'effondrement
        if effondrees:
            eff_str = " → <span style='color:#f5a623;'>⚡ " + \
                      ", ".join([f"({c[0]},{c[1]})" for c in effondrees]) + \
                      " collapsé</span>"
        else:
            eff_str = ""

        # Style barré si effondré
        style_texte = "text-decoration:line-through;opacity:0.45;" if barre else ""

        lignes.append(
            f'<div style="font-family:monospace;font-size:12px;line-height:1.8;{style_texte}">'
            f'<span style="color:#555;font-size:10px;">#{entry["num"]}</span> '
            f'<span style="color:{color};font-weight:700;">{sym} {nom}</span>'
            f'<span style="color:#666;"> → {cases_str}</span>'
            f'{eff_str}'
            f'</div>'
        )

    st.markdown(
        '<div style="background:rgba(255,255,255,0.03);border-left:3px solid #2a2a2a;'
        'border-radius:0 6px 6px 0;padding:8px 14px;margin-bottom:8px;">'
        + "".join(lignes) + '</div>',
        unsafe_allow_html=True)


def display_hardware_registry(plateau, marques_q):
    from quantum_engine import init_quantum_9q, jouer_coup_quantum_multi

    st.markdown(f'<div style="margin-bottom:4px;margin-top:12px;"><span style="{_TITRE}">Gate Sequence — Circuit Quantique</span></div>',
                unsafe_allow_html=True)

    if not marques_q:
        st.markdown(
            '<div style="font-family:monospace;color:#555;font-size:12px;'
            'padding:6px 10px;border-left:3px solid #222;">Circuit vide</div>',
            unsafe_allow_html=True)
        return

    try:
        _, _, qc = init_quantum_9q()
        mq_tmp = []
        for joueur, cases, num in marques_q:
            jouer_coup_quantum_multi(plateau, mq_tmp, qc, joueur, cases)

        circuit_str = str(qc.draw(output='text', fold=-1))

        st.markdown(
            '<style>[data-testid="stCode"] pre {'
            'background:#ffffff!important;color:#111!important;'
            'border:1px solid #ddd!important;border-radius:6px!important;'
            'font-family:"Courier New",monospace!important;}'
            '[data-testid="stCode"]{background:#ffffff!important;}</style>',
            unsafe_allow_html=True)
        st.code(circuit_str, language=None)

    except Exception as e:
        st.markdown(f'<div style="color:#e88;font-size:12px;">Circuit non disponible : {e}</div>',
                    unsafe_allow_html=True)
