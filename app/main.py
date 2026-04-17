import streamlit as st
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "scouting_prod.db"

st.set_page_config(
    page_title="Scouting Ligue 2",
    page_icon="⚽",
    layout="wide"
)

LOGO_URL = "https://raw.githubusercontent.com/martjosnez/scouting-ligue2/main/app/assets/logo_nancy.jpg"

st.markdown("""
<style>
@import url('https://fonts.cdnfonts.com/css/raleway-5');
* { font-family: 'Raleway', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #0A0C10; }
[data-testid="stSidebar"] { background: #0F1218 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding-top: 3rem !important; max-width: 1200px; }
.hero-eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 4px; text-transform: uppercase; color: #E8281A; margin-bottom: 12px; }
.hero-title { font-size: 80px; font-weight: 900; color: #F0F2F5; line-height: 1; letter-spacing: -2px; margin-bottom: 10px; white-space: nowrap; }
.hero-title span { color: #E8281A; }
.hero-desc { font-size: 14px; color: #6B7280; margin-bottom: 36px; }
.kpi-row { display: flex; gap: 12px; margin-bottom: 44px; }
.kpi-box { background: #141720; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 28px; min-width: 140px; }
.kpi-box-val { font-size: 36px; font-weight: 900; color: #E8281A; line-height: 1; }
.kpi-box-lbl { font-size: 11px; font-weight: 700; color: #4B5563; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px; }
.sidebar-logo { text-align: center; padding: 20px 12px 24px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 16px; }
.sidebar-logo img { width: 100px; border-radius: 10px; margin-bottom: 12px; }
.sidebar-club { font-size: 14px; font-weight: 800; color: #F0F2F5; }
.sidebar-season { font-size: 10px; color: #4B5563; text-transform: uppercase; letter-spacing: 2px; margin-top: 3px; }
.nav-link { display: flex; align-items: center; gap: 12px; padding: 11px 14px; border-radius: 8px; color: #9CA3AF; font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.nav-link-icon { font-size: 18px; }

div[data-testid="stButton"] button {
    background: #141720 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    color: #F0F2F5 !important;
    font-size: 18px !important;
    font-weight: 800 !important;
    padding: 48px 24px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    line-height: 1.6 !important;
}
div[data-testid="stButton"] button:hover {
    border-color: rgba(232,40,26,0.6) !important;
    background: rgba(232,40,26,0.08) !important;
    color: #E8281A !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <img src="{LOGO_URL}" onerror="this.style.display='none'">
        <div class="sidebar-club">AS Nancy Lorraine</div>
        <div class="sidebar-season">Saison 2025 / 26</div>
    </div>
    <div class="nav-link"><span class="nav-link-icon">🏠</span> Accueil</div>
    <div class="nav-link"><span class="nav-link-icon">👤</span> Profil joueur</div>
    <div class="nav-link"><span class="nav-link-icon">⚖️</span> Comparaison</div>
    <div class="nav-link"><span class="nav-link-icon">📋</span> Shortlist</div>
    """, unsafe_allow_html=True)

conn = sqlite3.connect(DB_PATH) if DB_PATH.exists() else None
nb_joueurs = 0
nb_clubs = 0
if conn:
    try:
        nb_joueurs = conn.execute("SELECT COUNT(*) FROM joueurs").fetchone()[0]
        nb_clubs = conn.execute("SELECT COUNT(*) FROM equipes").fetchone()[0]
        conn.close()
    except:
        pass

st.markdown("""
<div class="hero-eyebrow">Tableau de bord</div>
<div class="hero-title">SCOUTING <span>LIGUE 2</span></div>
<div class="hero-desc">Analyse de performance · Saison 2025 / 26</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-box"><div class="kpi-box-val">{nb_clubs}</div><div class="kpi-box-lbl">Clubs</div></div>
    <div class="kpi-box"><div class="kpi-box-val">{nb_joueurs}</div><div class="kpi-box-lbl">Joueurs</div></div>
    <div class="kpi-box"><div class="kpi-box-val">25/26</div><div class="kpi-box-lbl">Saison</div></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👤\n\nProfil joueur\nAnalyse individuelle", key="btn_profil", use_container_width=True):
        st.switch_page("pages/profil.py")

with col2:
    if st.button("⚖️\n\nComparaison\nFace a face", key="btn_comp", use_container_width=True):
        st.switch_page("pages/comparaison.py")

with col3:
    if st.button("📋\n\nShortlist\nCibles de recrutement", key="btn_short", use_container_width=True):
        st.switch_page("pages/shortlist.py")