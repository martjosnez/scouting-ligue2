import streamlit as st

st.set_page_config(
    page_title="Scouting Ligue 2",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Scouting Ligue 2")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤 Profil joueur", use_container_width=True):
        st.switch_page("pages/profil.py")

with col2:
    if st.button("⚖️ Comparaison", use_container_width=True):
        st.switch_page("pages/comparaison.py")

with col3:
    if st.button("📋 Shortlist", use_container_width=True):
        st.switch_page("pages/shortlist.py")

st.info("Base de données : en attente d'ingestion des captures Teamworks")