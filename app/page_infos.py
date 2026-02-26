import streamlit as st
import retour
import base64
from pathlib import Path

def _afficher_pdf(nom_fichier: str):
    """Affiche un PDF inline si le fichier existe, sinon message d'erreur."""
    chemin = Path(nom_fichier)
    if not chemin.exists():
        st.warning(f"Fichier `{nom_fichier}` introuvable. Placez-le dans le même dossier que `app.py`.")
        return
    data = base64.b64encode(chemin.read_bytes()).decode("utf-8")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{data}" '
        f'width="100%" height="800px" style="border:none;border-radius:6px;"></iframe>',
        unsafe_allow_html=True,
    )

def show():
    retour.bouton_retour()
    st.markdown("<h1 style='text-align:center;'>DOCUMENTS DU PROJET</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["ENONCE", "RAPPORT FINAL", "PARTICIPATION"])
    with t1:
        _afficher_pdf("enonce.pdf")
    with t2:
        _afficher_pdf("rapport.pdf")
    with t3:
        st.markdown("#### Membres du projet")
        st.write("Thomas BELLEVILLE, Valentine GASNIER, Eva TAVARES, David WANG")
        st.markdown("#### Professeur")
        st.write("M. Breuil")
