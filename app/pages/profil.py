import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Profil Joueur", layout="wide", page_icon="⚽")

LOGO_URL = "https://raw.githubusercontent.com/martjosnez/scouting-ligue2/main/app/assets/logo_nancy.jpg"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
* { font-family: 'Inter', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #111318; }
[data-testid="stSidebar"] { background: #161920 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebarNav"] { display: none !important; }
.block-container { padding-top: 4rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }
.player-name { font-size: 48px; font-weight: 900; color: #F0F2F5; line-height: 1.1; margin-bottom: 14px; letter-spacing: -1px; }
.badge { display: inline-block; padding: 5px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-right: 6px; margin-bottom: 8px; border: 1px solid; }
.badge-red { background: rgba(232,40,26,0.15); color: #E8281A; border-color: rgba(232,40,26,0.35); }
.badge-gray { background: rgba(255,255,255,0.05); color: #9CA3AF; border-color: rgba(255,255,255,0.1); }
.kpi-card { background: #1C2028; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 20px 24px; text-align: center; }
.kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #6B7280; margin-bottom: 8px; }
.kpi-value { font-size: 38px; font-weight: 900; color: #F0F2F5; line-height: 1; }
.section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #6B7280; margin: 32px 0 18px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.07); }
.bar-wrap { margin-bottom: 14px; }
.bar-meta { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; color: #9CA3AF; }
.bar-track { background: rgba(255,255,255,0.06); border-radius: 4px; height: 6px; overflow: hidden; }
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
    st.markdown("<br>", unsafe_allow_html=True)
    equipes = ["Toutes"] + sorted(joueurs["equipe"].unique().tolist())
    eq = st.selectbox("Equipe", equipes)
    df = joueurs if eq == "Toutes" else joueurs[joueurs["equipe"] == eq]
    postes = ["Tous"] + sorted(df["poste"].dropna().unique().tolist())
    po = st.selectbox("Poste", postes)
    if po != "Tous":
        df = df[df["poste"] == po]
    joueur_sel = st.selectbox("Joueur", df["nom"].tolist())

j = df[df["nom"] == joueur_sel].iloc[0]

st.markdown('<div class="player-name">' + str(j["nom"]) + '</div>', unsafe_allow_html=True)
badges = '<span class="badge badge-red">' + str(j["equipe"]) + '</span>'
badges += '<span class="badge badge-gray">' + str(j["poste"] or "-") + '</span>'
badges += '<span class="badge badge-gray">' + str(j["role"] or "-") + '</span>'
badges += '<span class="badge badge-gray">' + str(j["age"]) + ' ans</span>'
badges += '<span class="badge badge-gray">' + str(j["valeur_m_eur"]) + 'M EUR</span>'
st.markdown(badges, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

mins = int(j["minutes"]) if pd.notna(j["minutes"]) else 0
k1, k2, k3, k4 = st.columns(4)
for col, label, val in [
    (k1, "Minutes", str(mins) + "'"),
    (k2, "CPM Total", str(round(j["cpm_total"])) if pd.notna(j["cpm_total"]) else "-"),
    (k3, "OPV-P", str(round(j["opv_p_total"])) if pd.notna(j["opv_p_total"]) else "-"),
    (k4, "BPM xGS0", str(round(j["bpm_xgs0_net"])) if pd.notna(j["bpm_xgs0_net"]) else "-"),
]:
    col.markdown('<div class="kpi-card"><div class="kpi-label">' + label + '</div><div class="kpi-value">' + val + '</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Analyse detaillee</div>', unsafe_allow_html=True)
col_left, col_right = st.columns([1, 1])
maxs = {m: joueurs[m].max() for m in METRIQUES}

with col_left:
    for m, l in zip(METRIQUES, LABELS):
        val = j[m] if pd.notna(j[m]) else 0
        maxi = maxs[m]
        pct = min(int((val / maxi) * 100), 100) if maxi > 0 else 0
        color = "#14b8a6" if pct >= 50 else "#E8281A"
        html = '<div class="bar-wrap">'
        html += '<div class="bar-meta"><span>' + l + '</span><span style="color:' + color + ';font-weight:600">' + str(round(val)) + '</span></div>'
        html += '<div class="bar-track"><div style="width:' + str(pct) + '%;background:' + color + ';height:6px;border-radius:4px"></div></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

with col_right:
    vals = [j[m] if pd.notna(j[m]) else 0 for m in METRIQUES]
    vn   = [v/maxs[m]*100 if maxs[m] > 0 else 0 for v, m in zip(vals, METRIQUES)]
    fig = go.Figure(go.Scatterpolar(
        r=vn + [vn[0]], theta=LABELS + [LABELS[0]],
        fill="toself",
        fillcolor="rgba(232,40,26,0.1)",
        line=dict(color="#E8281A", width=2),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1C2028",
            radialaxis=dict(visible=True, range=[0,100],
                tickfont=dict(size=9, color="#555"),
                gridcolor="#252830", linecolor="#252830"),
            angularaxis=dict(
                tickfont=dict(size=11, color="#9CA3AF"),
                gridcolor="#252830", linecolor="#252830"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False, height=380,
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
    rows.append({"Metrique": l, "Joueur": round(v,1), "Moyenne poste": round(moy,1), "Ecart": round(diff,1)})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)