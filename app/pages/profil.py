import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Profil Joueur", layout="wide", page_icon="⚽")

st.markdown("""
<style>
.player-header {
    background: linear-gradient(135deg, #1A1D26 0%, #0E1117 100%);
    border: 1px solid #00D4AA33;
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
}
.player-name {
    font-size: 36px;
    font-weight: 800;
    color: #FAFAFA;
    margin: 0 0 8px 0;
}
.player-tag {
    display: inline-block;
    background: #00D4AA22;
    border: 1px solid #00D4AA55;
    color: #00D4AA;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
}
.metric-card {
    background: #1A1D26;
    border: 1px solid #ffffff11;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.metric-label {
    font-size: 11px;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #FAFAFA;
}
.section-title {
    font-size: 16px;
    font-weight: 600;
    color: #00D4AA;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 24px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #00D4AA33;
}
.jauge-wrap { margin-bottom: 14px; }
.jauge-label {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 5px;
    color: #aaa;
}
.jauge-bar {
    background: #ffffff11;
    border-radius: 6px;
    height: 8px;
    overflow: hidden;
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

def couleur(val, maxi):
    if pd.isna(val) or maxi == 0: return "#555"
    p = val / maxi
    if p >= 0.75: return "#00D4AA"
    if p >= 0.45: return "#F0A500"
    return "#FF6B6B"

def jauge(label, val, maxi):
    if pd.isna(val): val = 0
    pct = min(int((val / maxi) * 100), 100) if maxi > 0 else 0
    c = couleur(val, maxi)
    st.markdown(f"""
    <div class="jauge-wrap">
      <div class="jauge-label">
        <span>{label}</span><span style="color:{c};font-weight:600">{val:.0f}</span>
      </div>
      <div class="jauge-bar">
        <div style="width:{pct}%;background:{c};height:8px;border-radius:6px"></div>
      </div>
    </div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Scouting Ligue 2")
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

st.markdown(f"""
<div class="player-header">
  <div class="player-name">{j['nom']}</div>
  <span class="player-tag">{j['equipe']}</span>
  <span class="player-tag">{j['poste'] or '—'}</span>
  <span class="player-tag">{j['role'] or '—'}</span>
  <span class="player-tag">{j['age']} ans</span>
  <span class="player-tag">{j['valeur_m_eur']}M €</span>
</div>
""", unsafe_allow_html=True)

mins = int(j['minutes']) if pd.notna(j['minutes']) else 0
k1,k2,k3,k4 = st.columns(4)
for col, label, val in [
    (k1, "Minutes", f"{mins}'"),
    (k2, "CPM Total", f"{j['cpm_total']:.0f}" if pd.notna(j['cpm_total']) else "—"),
    (k3, "OPV-P", f"{j['opv_p_total']:.0f}" if pd.notna(j['opv_p_total']) else "—"),
    (k4, "BPM xGS0", f"{j['bpm_xgs0_net']:.0f}" if pd.notna(j['bpm_xgs0_net']) else "—"),
]:
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{val}</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Analyse détaillée</div>', unsafe_allow_html=True)
col_left, col_right = st.columns([1, 1])

with col_left:
    maxs = {m: joueurs[m].max() for m in METRIQUES}
    for m, l in zip(METRIQUES, LABELS):
        jauge(l, j[m], maxs[m])

with col_right:
    vals = [j[m] if pd.notna(j[m]) else 0 for m in METRIQUES]
    maxi = [joueurs[m].max() for m in METRIQUES]
    vn   = [v/mx*100 if mx > 0 else 0 for v, mx in zip(vals, maxi)]
    fig = go.Figure(go.Scatterpolar(
        r=vn + [vn[0]], theta=LABELS + [LABELS[0]],
        fill="toself",
        fillcolor="rgba(0,212,170,0.15)",
        line=dict(color="#00D4AA", width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1A1D26",
            radialaxis=dict(
                visible=True, range=[0,100],
                tickfont=dict(size=9, color="#666"),
                gridcolor="#333344",
                linecolor="#333344"),
            angularaxis=dict(
                tickfont=dict(size=11, color="#aaa"),
                gridcolor="#333344",
                linecolor="#333344"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, height=360,
        margin=dict(l=50,r=50,t=30,b=30),
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-title">Vs moyenne du poste</div>', unsafe_allow_html=True)
meme_poste = joueurs[joueurs["poste"] == j["poste"]] if j["poste"] else joueurs
rows = []
for m, l in zip(METRIQUES, LABELS):
    v   = j[m] if pd.notna(j[m]) else 0
    moy = meme_poste[m].mean()
    diff = v - moy
    rows.append({"Métrique": l, "Joueur": round(v,1),
                 "Moyenne poste": round(moy,1), "Écart": round(diff,1)})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)