import streamlit as st

st.set_page_config(
    page_title="Scouting Ligue 2",
    page_icon="⚽",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

[data-testid="stAppViewContainer"] {
    background: #0D0F12;
}
[data-testid="stSidebar"] {
    background: #141720 !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
.block-container { padding-top: 2rem; }

.dash-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 52px;
    letter-spacing: 3px;
    color: #F0F2F5;
    line-height: 1;
    margin-bottom: 4px;
}
.dash-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: #6B7280;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 32px;
}
.nav-card {
    background: #141720;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 28px 24px;
    text-align: center;
    cursor: pointer;
    transition: all .2s;
}
.nav-card:hover {
    border-color: rgba(232,40,26,0.5);
    background: rgba(232,40,26,0.08);
}
.nav-icon {
    font-size: 32px;
    margin-bottom: 12px;
}
.nav-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 20px;
    letter-spacing: 2px;
    color: #F0F2F5;
}
.nav-desc {
    font-size: 12px;
    color: #6B7280;
    margin-top: 4px;
}
.stat-strip {
    display: flex;
    gap: 16px;
    margin-top: 32px;
}
.stat-pill {
    background: #141720;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 12px 20px;
    font-family: 'DM Sans', sans-serif;
}
.stat-pill-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    color: #E8281A;
    line-height: 1;
}
.stat-pill-lbl {
    font-size: 11px;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="stButton"] button {
    background: #141720 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: #F0F2F5 !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 2rem 1rem !important;
    font-size: 15px !important;
    transition: all .2s !important;
}
div[data-testid="stButton"] button:hover {
    border-color: rgba(232,40,26,0.5) !important;
    background: rgba(232,40,26,0.08) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="dash-title">Scouting Ligue 2</div>', unsafe_allow_html=True)
st.markdown('<div class="dash-sub">Saison 2025 / 26 · Tableau de bord</div>', unsafe_allow_html=True)

st.markdown("""
<div class="stat-strip">
  <div class="stat-pill"><div class="stat-pill-val">10</div><div class="stat-pill-lbl">Clubs indexés</div></div>
  <div class="stat-pill"><div class="stat-pill-val">247+</div><div class="stat-pill-lbl">Joueurs</div></div>
  <div class="stat-pill"><div class="stat-pill-val">2025/26</div><div class="stat-pill-lbl">Saison</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("👤  Profil joueur\n\nAnalyse individuelle complète", use_container_width=True):
        st.switch_page("pages/profil.py")
with col2:
    if st.button("⚖️  Comparaison\n\nFace à face entre deux joueurs", use_container_width=True):
        st.switch_page("pages/comparaison.py")
with col3:
    if st.button("📋  Shortlist\n\nCibles de recrutement", use_container_width=True):
        st.switch_page("pages/shortlist.py")