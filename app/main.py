import streamlit as st
import sqlite3
import base64
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "database" / "scouting_prod.db"

st.set_page_config(
    page_title="Scouting Ligue 2",
    page_icon="⚽",
    layout="wide"
)

def get_logo_base64():
    logo_path = Path(__file__).parent / "assets" / "logo_nancy.jpg"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

st.markdown("""
<style>
@import url('https://fonts.cdnfonts.com/css/raleway-5');
* { font-family: 'Raleway', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #0A0C10; }
[data-testid="stSidebar"] { background: #0F1218 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] a { color: #9CA3AF !important; font-size: 14px !important; }
[data-testid="stSidebarNav"] a:hover { color: #F0F2F5 !important; }
.block-container { padding-top: 3rem !important; max-width: 1100px; }
.hero { margin-bottom: 40px; }
.hero-eyebrow { font-size: 11px; font-weight: 700; letter-spacing: 4px; text-transform: uppercase; color: #E8281A; margin-bottom: 10px; }
.hero-title { font-size: 72px; font-weight: 900; color: #F0F2F5; line-height: 0.95; letter-spacing: -2px; margin-bottom: 16px; }
.hero-title span { color: #E8281A; }
.hero-desc { font-size: 15px; color: #6B7280; font-weight: 400; letter-spacing: 0.5px; }
.kpi-row { display: flex; gap: 12px; margin-bottom: 48px; }
.kpi-box { background: #141720; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 16px 24px; min-width: 130px; }
.kpi-box-val { font-size: 34px; font-weight: 800; color: #E8281A; line-height: 1; }
.kpi-box-lbl { font-size: 11px; font-weight: 600; color: #4B5563; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 5px; }
.nav-box { background: #141720; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 28px 24px; text-align: center; }
.nav-box-icon { font-size: 36px; margin-bottom: 14px; display: block; }
.nav-box-title { font-size: 17px; font-weight: 700; color: #F0F2F5; margin-bottom: 6px; }
.nav-box-desc { font-size: 12px; color: #6B7280; font-weight: 400; }
div[data-testid="stButton"] button { background: transparent !important; border: none !important; padding: 0 !important; height: auto !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    logo_b64 = get_logo_base64()
    if logo_b64:
        st.markdown(f"""
        <div style="text-align:center;padding:16px 0 20px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:8px">
            <img src="data:image/jpeg;base64,{logo_b64}" style="width:90px;border-radius:8px;margin-bottom:10px">
            <div style="font-size:13px;font-weight:800;color:#F0F2F5;letter-spacing:1px">AS Nancy Lorraine</div>
            <div style="font-size:10px;color:#4B5563;text-transform:uppercase;letter-spacing:2px;margin-top:2px">Saison 2025/26</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:16px 0 20px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:8px">
            <div style="font-size:22px;margin-bottom:6px">⚽</div>
            <div style="font-size:13px;font-weight:800;color:#F0F2F5;letter-spacing:1px">AS Nancy Lorraine</div>
            <div style="font-size:10px;color:#4B5563;text-transform:uppercase;letter-spacing:2px;margin-top:2px">Saison 2025/26</div>
        </div>
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
<div class="hero">
    <div class="hero-eyebrow">Tableau de bord</div>
    <div class="hero-title">SCOUTING<br><span>LIGUE 2</span></div>
    <div class="hero-desc">Analyse de performance · Saison 2025 / 26</div>
</div>
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
    <div class="nav-box">
        <span class="nav-box-icon">👤</span>
        <div class="nav-box-title">Profil joueur</div>
        <div class="nav-box-desc">Analyse individuelle complète</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder", key="btn_profil", use_container_width=True):
        st.switch_page("pages/profil.py")

with col2:
    st.markdown("""
    <div class="nav-box">
        <span class="nav-box-icon">⚖️</span>
        <div class="nav-box-title">Comparaison</div>
        <div class="nav-box-desc">Face a face entre deux joueurs</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder", key="btn_comp", use_container_width=True):
        st.switch_page("pages/comparaison.py")

with col3:
    st.markdown("""
    <div class="nav-box">
        <span class="nav-box-icon">📋</span>
        <div class="nav-box-title">Shortlist</div>
        <div class="nav-box-desc">Cibles de recrutement</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Acceder", key="btn_short", use_container_width=True):
        st.switch_page("pages/shortlist.py")