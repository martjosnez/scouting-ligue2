import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"

st.set_page_config(page_title="Comparaison", layout="wide")
st.title("⚖️ Comparaison de joueurs")

if not DB_PATH.exists():
    st.warning("Base de données vide. Lance d'abord l'ingestion.")
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

METRIQUES = ["cpm_total", "cpm_scored", "cpm_conc",
             "bpm_xgs0_net", "gapm_xgs0_net", "opv_p_total"]
LABELS = ["CPM Total", "CPM Scored", "CPM Conc.",
          "BPM xGS0", "GAPM xGS0", "OPV-P"]

col1, col2 = st.columns(2)
with col1:
    joueur1 = st.selectbox("Joueur A", joueurs["nom"].tolist(), key="j1")
with col2:
    joueur2 = st.selectbox("Joueur B", joueurs["nom"].tolist(),
                           index=1 if len(joueurs) > 1 else 0, key="j2")

j1 = joueurs[joueurs["nom"] == joueur1].iloc[0]
j2 = joueurs[joueurs["nom"] == joueur2].iloc[0]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=[j1[m] for m in METRIQUES],
    theta=LABELS, fill="toself", name=joueur1
))
fig.add_trace(go.Scatterpolar(
    r=[j2[m] for m in METRIQUES],
    theta=LABELS, fill="toself", name=joueur2
))
fig.update_layout(polar=dict(radialaxis=dict(visible=True)),
                  showlegend=True, height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Comparaison détaillée")
comp = pd.DataFrame({
    "Métrique": LABELS,
    joueur1: [j1[m] for m in METRIQUES],
    joueur2: [j2[m] for m in METRIQUES],
})
comp["Meilleur"] = comp.apply(
    lambda r: joueur1 if r[joueur1] > r[joueur2] else joueur2, axis=1
)
st.dataframe(comp, use_container_width=True, hide_index=True)