import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Recherche", layout="wide", page_icon="⚽")

LOGO_URL = "https://raw.githubusercontent.com/martjosnez/scouting-ligue2/main/app/assets/logo_nancy.jpg"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
* { font-family: 'Inter', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #111318; }
[data-testid="stSidebar"] { background: #161920 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding-top: 4rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }
.page-title { font-size: 48px; font-weight: 900; color: #F0F2F5; line-height: 1.1; margin-bottom: 6px; letter-spacing: -1px; }
.page-sub { font-size: 13px; color: #6B7280; margin-bottom: 32px; text-transform: uppercase; letter-spacing: 1.5px; }
.result-count { font-size: 13px; color: #6B7280; margin-bottom: 16px; }
.result-count span { color: #E8281A; font-weight: 700; }
.filter-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #6B7280; margin-bottom: 8px; margin-top: 16px; }
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
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("Base de donnees vide.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
joueurs = pd.read_sql("""
    SELECT j.nom, j.poste, j.role, j.age, j.valeur_m_eur,
           e.nom as equipe, s.minutes,
           s.proj_cpm_total, s.cpm_total, s.cpm_scored, s.cpm_conc,
           s.bpm_xgs0_net, s.gapm_xgs0_net, s.opv_p_total
    FROM joueurs j
    JOIN equipes e ON j.equipe_id = e.id
    JOIN stats_match s ON s.joueur_id = j.id
""", conn)
conn.close()

if joueurs.empty:
    st.warning("Aucun joueur en base.")
    st.stop()

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
    if st.button("🔍  Recherche", use_container_width=True, key="nav_recherche"):
        st.switch_page("pages/recherche.py")

    st.markdown("---")

    st.markdown('<div class="filter-title">Equipes</div>', unsafe_allow_html=True)
    equipes_list = sorted(joueurs["equipe"].unique().tolist())
    equipes_sel = st.multiselect("Equipes", equipes_list, default=equipes_list, label_visibility="collapsed")

    st.markdown('<div class="filter-title">Postes</div>', unsafe_allow_html=True)
    postes_list = sorted(joueurs["poste"].dropna().unique().tolist())
    postes_sel = st.multiselect("Postes", postes_list, default=postes_list, label_visibility="collapsed")

    st.markdown('<div class="filter-title">Age</div>', unsafe_allow_html=True)
    age_min = float(joueurs["age"].min())
    age_max = float(joueurs["age"].max())
    age_range = st.slider("Age", age_min, age_max, (age_min, age_max), step=0.5, label_visibility="collapsed")

    st.markdown('<div class="filter-title">Minutes minimum</div>', unsafe_allow_html=True)
    mins_min = int(joueurs["minutes"].min())
    mins_max = int(joueurs["minutes"].max())
    mins_seuil = st.slider("Minutes", mins_min, mins_max, mins_min, step=100, label_visibility="collapsed")

    st.markdown('<div class="filter-title">Valeur TM max (M EUR)</div>', unsafe_allow_html=True)
    val_max = float(joueurs["valeur_m_eur"].max())
    val_seuil = st.slider("Valeur", 0.0, val_max, val_max, step=0.1, label_visibility="collapsed")

    st.markdown('<div class="filter-title">Trier par</div>', unsafe_allow_html=True)
    tri_options = {
        "Proj CPM Total": "proj_cpm_total",
        "CPM Total": "cpm_total",
        "OPV-P": "opv_p_total",
        "BPM xGS0": "bpm_xgs0_net",
        "GAPM xGS0": "gapm_xgs0_net",
        "Minutes": "minutes",
        "Age": "age",
        "Valeur TM": "valeur_m_eur",
    }
    tri_label = st.selectbox("Trier par", list(tri_options.keys()), label_visibility="collapsed")
    tri_col = tri_options[tri_label]

df = joueurs.copy()
if equipes_sel:
    df = df[df["equipe"].isin(equipes_sel)]
if postes_sel:
    df = df[df["poste"].isin(postes_sel)]
df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
df = df[df["minutes"] >= mins_seuil]
df = df[df["valeur_m_eur"] <= val_seuil]
df = df.sort_values(tri_col, ascending=False)

st.markdown('<div class="page-title">Recherche</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Filtres & classement des joueurs</div>', unsafe_allow_html=True)
st.markdown('<div class="result-count"><span>' + str(len(df)) + '</span> joueurs trouvés sur ' + str(len(joueurs)) + '</div>', unsafe_allow_html=True)

df_display = df[[
    "nom", "equipe", "poste", "role", "age", "valeur_m_eur",
    "minutes", "proj_cpm_total", "cpm_total", "cpm_scored",
    "cpm_conc", "bpm_xgs0_net", "gapm_xgs0_net", "opv_p_total"
]].copy()

df_display.columns = [
    "Nom", "Equipe", "Poste", "Role", "Age", "Valeur (M)",
    "Minutes", "Proj CPM", "CPM Total", "CPM Scored",
    "CPM Conc.", "BPM xGS0", "GAPM xGS0", "OPV-P"
]

for col in ["Proj CPM","CPM Total","CPM Scored","CPM Conc.","BPM xGS0","GAPM xGS0","OPV-P"]:
    df_display[col] = df_display[col].apply(lambda x: round(x) if pd.notna(x) else "-")

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    height=600,
    column_config={
        "Proj CPM": st.column_config.NumberColumn("Proj CPM", help="Projection CPM Total"),
        "CPM Total": st.column_config.NumberColumn("CPM Total"),
        "OPV-P": st.column_config.NumberColumn("OPV-P"),
        "BPM xGS0": st.column_config.NumberColumn("BPM xGS0"),
        "Valeur (M)": st.column_config.NumberColumn("Valeur (M)", format="%.1f M"),
        "Age": st.column_config.NumberColumn("Age", format="%.1f"),
    }
)