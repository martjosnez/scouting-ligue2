import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Profil Joueur", layout="wide", page_icon="⚽")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');
[data-testid="stAppViewContainer"] { background: #0D0F12; }
[data-testid="stSidebar"] { background: #141720 !important; border-right: 1px solid rgba(255,255,255,0.07); }
.block-container { padding-top: 2rem; }
.player-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 52px; letter-spacing: 3px;
    color: #F0F2F5; line-height: 1; margin-bottom: 12px;
}
.badge {
    display: inline-block;
    padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-family: 'DM Sans', sans-serif;
    margin-right: 6px; margin-bottom: 6px;
    border: 1px solid;
}
.badge-red { background: rgba(232,40,26,0.15); color: #E8281A; border-color: rgba(232,40,26,0.4); }
.badge-gray { background: rgba(255,255,255,0.05); color: #9CA3AF; border-color: rgba(255,255,255,0.1); }
.kpi-card {
    background: #141720; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 16px 20px; text-align: center;
}
.kpi-label { font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #6B7280; margin-bottom: 6px; }
.kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 36px; color: #F0F2F5; line-height: 1; }
.section-title {
    font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
    color: #6B7280; margin: 28px 0 16px; padding-bottom: 8px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.bar-wrap { margin-bottom: 12px; }
.bar-meta { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; color: #9CA3AF; }
.bar-track { background: rgba(255,255,255,0.06); border-radius: 3px; height: 5px; overflow: hidden; }
[data-testid="stSelectbox"] label, [data-testid="stSelectbox"] div {
    color: #9CA3AF !important; font-family: 'DM Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("Base de données vide.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
joueurs = pd.read_sql("""
    SELECT j.id, j.nom, j.poste, j.role, j.age, j.valeur_m_eur,
           e.nom as equipe, s.minutes,
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

METRIQUES = ["cpm_total","cpm_scored","cpm_conc","bpm_xgs0_net","gapm_xgs0_net","opv_p_total"]
LABELS    = ["CPM Total","CPM Scored","CPM Conc.","BPM xGS0","GAPM xGS0","OPV-P"]

with st.sidebar:
    st.markdown("### 🔴 Scouting L2")
    st.markdown("---")
    equipes = ["Toutes"] + sorted(joueurs["equipe"].unique().tolist())
    eq = st.selectbox("Équipe", equipes)
    df = joueurs if eq == "Toutes" else joueurs[joueurs["equipe"] == eq]
    postes = ["Tous"] + sorted(df["poste"].dropna().unique().tolist())
    po = st.selectbox("Poste", postes)
    if po != "Tous":
        df = df[df["poste"] == po]
    joueur_sel = st.selectbox("Joueur", df["nom"].tolist())

j = df[df["nom"] == joueur_sel].iloc[0]

st.markdown(f'<div class="player-name">{j["nom"]}</div>', unsafe_allow_html=True)
st.markdown(f"""
<span class="badge badge-red">{j['equipe']}</span>
<span class="badge badge-gray">{j['poste'] or '—'}</span>
<span class="badge badge-gray">{j['role'] or '—'}</span>
<span class="badge badge-gray">{j['age']} ans</span>
<span class="badge badge-gray">{j['valeur_m_eur']}M €</span>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

mins = int(j['minutes']) if pd.notna(j['minutes']) else 0
k1, k2, k3, k4 = st.columns(4)
for col, label, val in [
    (k1, "Minutes", f"{mins}'"),
    (k2, "CPM Total", f"{j['cpm_total']:.0f}" if pd.notna(j['cpm_total']) else "—"),
    (k3, "OPV-P", f"{j['opv_p_total']:.0f}" if pd.notna(j['opv_p_total']) else "—"),
    (k4, "BPM xGS0", f"{j['bpm_xgs0_net']:.0f}" if pd.notna(j['bpm_xgs0_net']) else "—"),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{val}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Analyse détaillée</div>', unsafe_allow_html=True)
col_left, col_right = st.columns([1, 1])

maxs = {m: joueurs[m].max() for m in METRIQUES}

with col_left:
    for m, l in zip(METRIQUES, LABELS):
        val = j[m] if pd.notna(j[m]) else 0
        maxi = maxs[m]
        pct = min(int((val / maxi) * 100), 100) if maxi > 0 else 0
        color = "#E8281A" if pct < 50 else "#14b8a6"
        st.markdown(f"""
        <div class="bar-wrap">
          <div class="bar-meta"><span>{l}</span><span style="color:{color};font-weight:500">{val:.0f}</span></div>
          <div class="