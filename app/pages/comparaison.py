import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Comparaison", layout="wide", page_icon="⚽")

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
.player-box { background: #1C2028; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 18px 22px; }
.player-box-name { font-size: 20px; font-weight: 700; color: #F0F2F5; margin-bottom: 4px; }
.player-box-sub { font-size: 12px; color: #6B7280; }
.vs-label { font-size: 22px; font-weight: 900; color: #E8281A; text-align: center; padding-top: 22px; }
.section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #6B7280; margin: 32px 0 18px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.07); }
.kpi-card { background: #1C2028; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px; text-align: center; }
.kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #6B7280; margin-bottom: 8px; }
.kpi-value { font-size: 30px; font-weight: 900; color: #F0F2F5; line-height: 1; }
.kpi-value-a { font-size: 30px; font-weight: 900; color: #E8281A; line-height: 1; }
.kpi-value-b { font-size: 30px; font-weight: 900; color: #14b8a6; line-height: 1; }
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
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("Base de donnees vide.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
joueurs = pd.read_sql("""
    SELECT j.nom, j.poste, j.age, e.nom as equipe,
           s.minutes, s.proj_cpm_total,
           s.cpm_total, s.cpm_scored, s.cpm_conc,
           s.bpm_xgs0_net, s.gapm_xgs0_net, s.opv_p_total
    FROM joueurs j
    JOIN equipes e ON j.equipe_id = e.id
    JOIN stats_match s ON s.joueur_id = j.id
""", conn)
conn.close()

if joueurs.empty:
    st.warning("Aucun joueur en base.")
    st.stop()

METRIQUES = ["proj_cpm_total","cpm_total","cpm_scored","cpm_conc","bpm_xgs0_net","gapm_xgs0_net","opv_p_total"]
LABELS    = ["Proj CPM","CPM Total","CPM Scored","CPM Conc.","BPM xGS0","GAPM xGS0","OPV-P"]
METRIQUES_RADAR = ["cpm_total","cpm_scored","cpm_conc","bpm_xgs0_net","gapm_xgs0_net","opv_p_total"]
LABELS_RADAR    = ["CPM Total","CPM Scored","CPM Conc.","BPM xGS0","GAPM xGS0","OPV-P"]

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

st.markdown('<div class="page-title">Comparaison</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Face a face entre deux joueurs</div>', unsafe_allow_html=True)

col1, mid, col2 = st.columns([10, 1, 10])
with col1:
    joueur1 = st.selectbox("Joueur A", joueurs["nom"].tolist(), key="j1")
with mid:
    st.markdown('<div class="vs-label">VS</div>', unsafe_allow_html=True)
with col2:
    joueur2 = st.selectbox("Joueur B", joueurs["nom"].tolist(),
                           index=1 if len(joueurs) > 1 else 0, key="j2")

j1 = joueurs[joueurs["nom"] == joueur1].iloc[0]
j2 = joueurs[joueurs["nom"] == joueur2].iloc[0]

c1, _, c2 = st.columns([10, 1, 10])
with c1:
    st.markdown('<div class="player-box"><div class="player-box-name">' + str(j1["nom"]) + '</div><div class="player-box-sub">' + str(j1["equipe"]) + ' · ' + str(j1["poste"] or "-") + ' · ' + str(j1["age"]) + ' ans</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="player-box"><div class="player-box-name">' + str(j2["nom"]) + '</div><div class="player-box-sub">' + str(j2["equipe"]) + ' · ' + str(j2["poste"] or "-") + ' · ' + str(j2["age"]) + ' ans</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Proj CPM Total</div>', unsafe_allow_html=True)
kc1, kc2 = st.columns(2)
proj1 = str(round(j1["proj_cpm_total"])) if pd.notna(j1["proj_cpm_total"]) else "-"
proj2 = str(round(j2["proj_cpm_total"])) if pd.notna(j2["proj_cpm_total"]) else "-"
with kc1:
    st.markdown('<div class="kpi-card"><div class="kpi-label">' + str(j1["nom"]) + '</div><div class="kpi-value-a">' + proj1 + '</div></div>', unsafe_allow_html=True)
with kc2:
    st.markdown('<div class="kpi-card"><div class="kpi-label">' + str(j2["nom"]) + '</div><div class="kpi-value-b">' + proj2 + '</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Radar comparatif</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=[j1[m] if pd.notna(j1[m]) else 0 for m in METRIQUES_RADAR] + [j1[METRIQUES_RADAR[0]]],
    theta=LABELS_RADAR + [LABELS_RADAR[0]],
    fill="toself", name=joueur1,
    fillcolor="rgba(232,40,26,0.1)",
    line=dict(color="#E8281A", width=2),
))
fig.add_trace(go.Scatterpolar(
    r=[j2[m] if pd.notna(j2[m]) else 0 for m in METRIQUES_RADAR] + [j2[METRIQUES_RADAR[0]]],
    theta=LABELS_RADAR + [LABELS_RADAR[0]],
    fill="toself", name=joueur2,
    fillcolor="rgba(20,184,166,0.1)",
    line=dict(color="#14b8a6", width=2),
))
fig.update_layout(
    polar=dict(
        bgcolor="#1C2028",
        radialaxis=dict(visible=True,
            tickfont=dict(size=9, color="#555"),
            gridcolor="#252830", linecolor="#252830"),
        angularaxis=dict(
            tickfont=dict(size=11, color="#9CA3AF"),
            gridcolor="#252830", linecolor="#252830"),
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(font=dict(color="#9CA3AF", size=12), bgcolor="rgba(0,0,0,0)"),
    height=440, margin=dict(l=60,r=60,t=30,b=30),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-title">Barres comparatives</div>', unsafe_allow_html=True)
maxs = {m: joueurs[m].max() for m in METRIQUES}

for m, l in zip(METRIQUES, LABELS):
    va = j1[m] if pd.notna(j1[m]) else 0
    vb = j2[m] if pd.notna(j2[m]) else 0
    maxi = maxs[m]
    pa = int(va/maxi*100) if maxi > 0 else 0
    pb = int(vb/maxi*100) if maxi > 0 else 0
    html = '<div style="display:grid;grid-template-columns:1fr 80px 1fr;gap:8px;align-items:center;margin-bottom:14px">'
    html += '<div><div style="font-size:13px;font-weight:600;color:#F0F2F5;text-align:right;margin-bottom:4px">' + str(round(va)) + '</div><div style="display:flex;justify-content:flex-end"><div style="width:' + str(pa) + '%;height:6px;background:#E8281A;border-radius:3px"></div></div></div>'
    html += '<div style="text-align:center;font-size:10px;color:#6B7280;text-transform:uppercase;letter-spacing:.5px;font-weight:600">' + l + '</div>'
    html += '<div><div style="font-size:13px;font-weight:600;color:#F0F2F5;margin-bottom:4px">' + str(round(vb)) + '</div><div style="width:' + str(pb) + '%;height:6px;background:#14b8a6;border-radius:3px"></div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)