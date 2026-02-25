import streamlit as st
import retour

def show():
    retour.bouton_retour()
    st.markdown("<h1 class='center-text'>DOCUMENTS DU PROJET</h1>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["ENONCE", "RAPPORT FINAL", "PARTICIPATION"])
    with t1:
        st.info("Placez ici l'énoncé de votre projet de Morpion Quantique.")
    with t2:
        st.success("Insérez ici votre rapport technique et vos conclusions.")
    with t3:
        st.markdown("#### Membres du projet")
        st.write("Ajoutez ici les noms des participants, leurs rôles et contributions.")