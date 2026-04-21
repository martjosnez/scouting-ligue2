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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
* { font-family: 'Inter', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #111318; }
[data-testid="stSidebar"] { background: #161920 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding-top: 5rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }

.hero-eyebrow { font-size: 12px; font-weight: 700; letter-spacing: 4px; text-transform: uppercase; color: #E8281A; margin-bottom: 14px; }
.hero-title { font-size: 80px; font-weight: 900; color: #F0F2F5; line-height: 1; letter-spacing: -3px; margin-bottom: 14px; }
.hero-title span { color: #E8281A; }
.hero-desc { font-size: 15px; color: #6B7280; margin-bottom: 48px; letter-spacing: 0.5px; }

.kpi-row { display: flex; gap: 14px; margin-bottom: 52px; }
.kpi-box { background: #1C2028; border: 1px solid rgba(255,255,255,0.07); border-radius: 14px; padding: 20px 32px; min-width: 150px; }
.kpi-box-val { font-size: 40px; font-weight: 900; color: #E8281A; line-height: 1; }
.kpi-box-lbl { font-size: 11px; font-weight: 700; color: #4B5563; text-transform: uppercase; letter-spacing: 2px; margin-top: 6px; }

.sidebar-logo { text-align: center; padding: 20px 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 12px; }
.sidebar-logo img { width: 90px; border-radius: 10px; margin-bottom: 10px; }
.sidebar-club { font-size: 15px; font-weight: 700; color: #F0F2F5; }
.sidebar-season { font-size: 11px; color: #4B5563; text-transform: uppercase; letter-spacing: 2px; margin-top: 3px; }

div[data-testid="stButton"] button {
    background: transparent !important; border: none !important;
    color: #9CA3AF !important; font-size: 15px !important;
    font-weight: 500 !important; text-align: left !important;
    padding: 10px 14px !important; border-radius: 8px !important;
    width: 100% !important;
}
div[data-testid="stButton"] button:hover {
    background: rgba(255,255,255,0.05) !important;
    color: #F0F2F5 !important;
}

.nav-card {
    background: #1C2028; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 36px 28px; text-align: center;
    transition: all 0.2s;
}
.nav-card:hover { border-color: rgba(232,40,26,0.5); background: rgba(232,40,26,0.06); }
.nav-card-icon { font-size: 40px; margin-bottom: 16px; display: block; }
.nav-card-title { font-size: 20px; font-weight: 800; color: #F0F2F5; margin-bottom: 8px; }
.nav-card-desc { font-size: 13px; color: #6B7280; font-weight: 400; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <img src="{LOGO_URL}" onerror="this.style.display='none'">
        <div class="sidebar-club">AS Nancy Lorraine</div>
        <div class="sidebar-season">Saison 2025 / 26</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏠  Accueil", use_container_width=True, key="nav_home"):
        st.switch_page("main.py")
    if st.button("👤  Profil joueur", use_container_width=True, key="nav_profil"):
        st.switch_page("pages/profil.py")
    if st.button("⚖️  Comparaison", use_container_width=True, key="nav_comp"):
        st.switch_page("pages/comparaison.py")
    if st.button("📋  Shortlist", use_container_width=True, key="nav_short"):
        st.switch_page("pages/shortlist.py")

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
    st.markdown("""
    <div class="nav-card">
        <span class="nav-card-icon">👤</span>
        <div class="nav-card-title">Profil joueur</div>
        <div class="nav-card-desc">Analyse individuelle complete</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder →", key="btn_profil", use_container_width=True):
        st.switch_page("pages/profil.py")

with col2:
    st.markdown("""
    <div class="nav-card">
        <span class="nav-card-icon">⚖️</span>
        <div class="nav-card-title">Comparaison</div>
        <div class="nav-card-desc">Face a face entre deux joueurs</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder →", key="btn_comp", use_container_width=True):
        st.switch_page("pages/comparaison.py")

with col3:
    st.markdown("""
    <div class="nav-card">
        <span class="nav-card-icon">📋</span>
        <div class="nav-card-title">Shortlist</div>
        <div class="nav-card-desc">Cibles de recrutement</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder →", key="btn_short", use_container_width=True):
        st.switch_page("pages/shortlist.py")