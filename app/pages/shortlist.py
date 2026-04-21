import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Shortlist", layout="wide", page_icon="⚽")

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
.add-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #6B7280; margin-bottom: 14px; }
.section-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #6B7280; margin: 32px 0 18px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.07); }
.short-item { background: #1C2028; border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; padding: 16px 20px; display: flex; align-items: center; gap: 14px; margin-bottom: 10px; }
.prio-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.short-name { font-size: 15px; font-weight: 700; color: #F0F2F5; }
.short-meta { font-size: 12px; color: #6B7280; margin-top: 3px; }
.status-badge { font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 20px; border: 1px solid; }
.status-suivi { background: rgba(20,184,166,.1); color: #14b8a6; border-color: rgba(20,184,166,.3); }
.status-cible { background: rgba(232,40,26,.1); color: #E8281A; border-color: rgba(232,40,26,.3); }
.status-contacte { background: rgba(245,158,11,.1); color: #f59e0b; border-color: rgba(245,158,11,.3); }
.status-ecarte { background: rgba(107,114,128,.1); color: #6B7280; border-color: rgba(107,114,128,.3); }
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
button[kind="primary"] {
    background: #E8281A !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; padding: 10px 20px !important;
}
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("Base de donnees vide.")
    st.stop()

conn = sqlite3.connect(DB_PATH)

joueurs = pd.read_sql("""
    SELECT j.id, j.nom, j.poste, j.age, e.nom as equipe,
           s.cpm_total, s.opv_p_total, s.minutes
    FROM joueurs j
    JOIN equipes e ON j.equipe_id = e.id
    JOIN stats_match s ON s.joueur_id = j.id
""", conn)

def load_shortlist():
    return pd.read_sql("""
        SELECT sl.id, j.nom, j.poste, e.nom as equipe,
               sl.priorite, sl.statut, sl.note, sl.added_by
        FROM shortlist sl
        JOIN joueurs j ON sl.joueur_id = j.id
        JOIN equipes e ON j.equipe_id = e.id
        ORDER BY sl.priorite, sl.created_at DESC
    """, conn)

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

st.markdown('<div class="page-title">Shortlist</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Cibles de recrutement</div>', unsafe_allow_html=True)

st.markdown('<div class="add-title">Ajouter un joueur</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    joueur_sel = st.selectbox("Joueur", joueurs["nom"].tolist(), label_visibility="collapsed")
with col2:
    priorite = st.selectbox("Priorite", [1, 2, 3],
        format_func=lambda x: {1: "Haute", 2: "Moyenne", 3: "Basse"}[x],
        label_visibility="collapsed")
with col3:
    statut = st.selectbox("Statut", ["suivi", "cible", "contacte", "ecarte"],
        label_visibility="collapsed")
with col4:
    ajouter = st.button("+ Ajouter", use_container_width=True, key="btn_ajouter")

note = st.text_area("Note scout", placeholder="Points forts, points faibles...", label_visibility="collapsed")
scout = st.text_input("Ton nom", value="Scout", label_visibility="collapsed")

if ajouter:
    joueur_id = int(joueurs[joueurs["nom"] == joueur_sel]["id"].iloc[0])
    existing = pd.read_sql(f"SELECT id FROM shortlist WHERE joueur_id = {joueur_id}", conn)
    if not existing.empty:
        st.warning(joueur_sel + " est deja dans la shortlist !")
    else:
        conn.execute(
            "INSERT INTO shortlist (joueur_id, priorite, statut, note, added_by) VALUES (?, ?, ?, ?, ?)",
            (joueur_id, priorite, statut, note, scout)
        )
        conn.commit()
        st.success(joueur_sel + " ajoute !")
        st.rerun()

shortlist = load_shortlist()

st.markdown('<div class="section-title">Shortlist actuelle — ' + str(len(shortlist)) + ' joueurs</div>', unsafe_allow_html=True)

PRIO_COLOR = {1: "#E8281A", 2: "#f59e0b", 3: "#6B7280"}
STATUS_CLASS = {"suivi": "status-suivi", "cible": "status-cible", "contacte": "status-contacte", "ecarte": "status-ecarte"}

if shortlist.empty:
    st.markdown('<div style="background:#1C2028;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:24px;text-align:center;color:#6B7280;font-size:14px;">Shortlist vide — ajoute des joueurs ci-dessus</div>', unsafe_allow_html=True)
else:
    for _, row in shortlist.iterrows():
        color = PRIO_COLOR.get(row["priorite"], "#6B7280")
        sc = STATUS_CLASS.get(row["statut"], "status-suivi")
        note_txt = str(row["note"]) if row["note"] else ""
        html = '<div class="short-item">'
        html += '<div class="prio-dot" style="background:' + color + '"></div>'
        html += '<div style="flex:1"><div class="short-name">' + str(row["nom"]) + '</div>'
        html += '<div class="short-meta">' + str(row["equipe"]) + ' · ' + str(row["poste"] or "") + '</div></div>'
        if note_txt:
            html += '<div style="font-size:12px;color:#6B7280;font-style:italic;flex:1;max-width:300px">' + note_txt + '</div>'
        html += '<span class="status-badge ' + sc + '">' + str(row["statut"]) + '</span>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
        if st.button("Retirer", key="del_" + str(row["id"])):
            conn.execute("DELETE FROM shortlist WHERE id = ?", (row["id"],))
            conn.commit()
            st.rerun()

conn.close()