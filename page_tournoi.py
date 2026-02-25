import streamlit as st
import pandas as pd
import styles
import retour
import quantum_engine as ql

NOMS = {'random':'Random','grover':'Grover','qaoa':'QAOA','minimax_q':'Minimax Q'}
COLS = {'random':'#95a5a6','grover':'#3498db','qaoa':'#9b59b6','minimax_q':'#e74c3c'}

def show():
    ias = list(NOMS.keys())
    n_parties = st.session_state.get("tournoi_n", 3)

    retour.bouton_retour(f"{n_parties} parties/match · 4 IAs · 6 matchs")

    st.markdown("<h2>Tournoi ELO — Quantum Tic-Tac-Toe</h2>", unsafe_allow_html=True)

    prog   = st.progress(0, text="Démarrage...")
    cl, cr = st.columns(2)
    with cl:
        st.subheader("Matchs")
        log_ph = st.empty()
    with cr:
        st.subheader("Classement live")
        rank_ph = st.empty()

    log_lines = []

    def on_match(match_num, total, ia1, ia2, elo_snap, stats_snap):
        prog.progress(match_num / total, text=f"Match {match_num}/{total}")
        log_lines.append(
            f"**{NOMS[ia1]}** vs **{NOMS[ia2]}** — "
            f"{elo_snap[ia1]:.0f} / {elo_snap[ia2]:.0f} ELO")
        log_ph.markdown("\n\n".join(log_lines[-5:]))
        cl_live = sorted(ias, key=lambda x: elo_snap[x], reverse=True)
        rank_ph.table(pd.DataFrame([{
            "Rang": f"#{r+1}", "IA": NOMS[ia],
            "ELO": f"{elo_snap[ia]:.0f}",
            "V": stats_snap[ia]['V'], "N": stats_snap[ia]['N'], "D": stats_snap[ia]['D']
        } for r, ia in enumerate(cl_live)]))

    with st.spinner("Tournoi en cours..."):
        elo, stats, classement, hist_elo = ql.tournoi_round_robin_elo(n_parties, on_match)

    prog.progress(1.0, text="Terminé !")
    log_ph.empty()
    rank_ph.empty()

    st.divider()
    st.subheader("Classement Final")
    st.table(pd.DataFrame([{
        "Rang": f"#{r+1}", "IA": NOMS[ia],
        "ELO": f"{elo[ia]:.0f}",
        "V": stats[ia]['V'], "N": stats[ia]['N'], "D": stats[ia]['D']
    } for r, ia in enumerate(classement)]))

    st.subheader("Evolution ELO")
    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        for ia in ias:
            fig.add_trace(go.Scatter(y=hist_elo[ia], name=NOMS[ia],
                line=dict(color=COLS[ia], width=2), mode='lines'))
        fig.add_hline(y=1000, line_dash="dash", line_color="gray", opacity=0.4)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.3)',
            font_color='white', height=320,
            xaxis_title="Parties", yaxis_title="ELO",
            legend=dict(bgcolor='rgba(0,0,0,0.4)'),
            margin=dict(t=10, b=40))
        fig.update_xaxes(gridcolor='rgba(255,255,255,0.08)')
        fig.update_yaxes(gridcolor='rgba(255,255,255,0.08)')
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        import io
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor('#111'); ax.set_facecolor('#111')
            for ia in ias:
                ax.plot(hist_elo[ia], label=NOMS[ia], color=COLS[ia], linewidth=2)
            ax.axhline(1000, color='gray', linestyle='--', alpha=0.5)
            ax.tick_params(colors='white')
            ax.legend()
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', facecolor='#111')
            st.image(buf)
        except Exception:
            st.info("Installez plotly ou matplotlib pour le graphique.")