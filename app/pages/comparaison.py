import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Comparaison", layout="wide", page_icon="⚽")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');
[data-testid="stAppViewContainer"] { background: #0D0F12; }
[data-testid="stSidebar"] { background: #141720 !important; border-right: 1px solid rgba(255,255,255,0.07); }
.block-container { padding-top: 2rem; }
.page-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 52px; letter-spacing: 3px;
    color: #F0F2F5; line-height: 1; margin-bottom: 4px;
}
.page-sub { font-size: 12px; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 28px; }
.player-box {
    background: #141720; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 16px 20px;
}
.player-box-name { font-family: 'Bebas Neue', sans-serif; font-size: 22px; color: #F0F2F5; letter-spacing: 1px; }
.player-box-sub { font-size: 12px; color: #6B7280; margin-top: 2px; }
.vs-label {
    font-family: 'Bebas Neue', sans-serif; font-size: 24px;
    color: #E8281A; text-align: center; padding-top: 18px;
}
.section-title {
    font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
    color: #6B7280; margin: 28px 0 16px;
    padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.07);
}
.comp-row { display: grid; grid-template-columns: 1fr 100px 1fr; gap: 8px; align-items: center; margin-bottom: 14px; }
.comp-val-a { font-size: 14px; font-weight: 500; color: #F0F2F5; text-align: right; margin-bottom: 4px; }
.comp-val-b { font-size: 14px; font-weight: 500; color: #F0F2F5; margin-bottom: 4px; }
.comp-metric { text-align: center; font-size: 10px; color: #6B7280; text-transform: uppercase; letter-spacing: .5px; }
.bar-a { display: flex; justify-content: flex-end; }
.bar-b { display: flex; justify-content: flex-start; }
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("Base de données vide.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
joueurs = pd.read_sql("""
    SELECT j.nom, j.poste, j.age, e.nom as equipe,
           s.minutes, s.cpm_total, s.cpm_scored, s.cpm_conc,
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

st.markdown('<div class="page-title">Comparaison</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Face à face entre deux joueurs</div>', unsafe_allow_html=True)

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
    st.markdown(f"""
    <div class="player-box">
      <div class="player-box-name">{j1['nom']}</div>
      <div class="player-box-sub">{j1['equipe']} · {j1['poste'] or '—'} · {j1['age']} ans</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="player-box">
      <div class="player-box-name">{j2['nom']}</div>
      <div class="player-box-sub">{j2['equipe']} · {j2['poste'] or '—'} · {j2['age']} ans</div>
    </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Radar comparatif</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=[j1[m] if pd.notna(j1[m]) else 0 for m in METRIQUES] + [j1[METRIQUES[0]]],
    theta=LABELS + [LABELS[0]],
    fill="toself", name=joueur1,
    fillcolor="rgba(232,40,26,0.12)",
    line=dict(color="#E8281A", width=2),
))
fig.add_trace(go.Scatterpolar(
    r=[j2[m] if pd.notna(j2[m]) else 0 for m in METRIQUES] + [j2[METRIQUES[0]]],
    theta=LABELS + [LABELS[0]],
    fill="toself", name=joueur2,
    fillcolor="rgba(20,184,166,0.12)",
    line=dict(color="#14b8a6", width=2),
))
fig.update_layout(
    polar=dict(
        bgcolor="#141720",
        radialaxis=dict(visible=True, tickfont=dict(size=9, color="#555"),
            gridcolor="#1C2030", linecolor="#1C2030"),
        angularaxis=dict(tickfont=dict(size=11, color="#9CA3AF"),
            gridcolor="#1C2030", linecolor="#1C2030"),
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(font=dict(color="#9CA3AF", size=12), bgcolor="rgba(0,0,0,0)"),
    height=420, margin=dict(l=60,r=60,t=30,b=30),
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
    st.markdown(f"""
    <div class="comp-row">
      <div>
        <div class="comp-val-a">{va:.0f}</div>
        <div class="bar-a"><div style="width:{pa}%;height:5px;background:#E8281A;border-radius:3px"></div></div>
      </div>
      <div class="comp-metric">{l}</div>
      <div>
        <div class="comp-val-b">{vb:.0f}</div>
        <div class="bar-b"><div style="width:{pb}%;height:5px;background:#14b8a6;border-radius:3px"></div></div>
      </div>
    </div>""", unsafe_allow_html=True)