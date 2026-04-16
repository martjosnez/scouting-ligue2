import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scouting_prod.db"
st.set_page_config(page_title="Shortlist", layout="wide", page_icon="⚽")

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
.add-section {
    background: #141720; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 20px 24px; margin-bottom: 24px;
}
.add-title { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #6B7280; margin-bottom: 16px; }
.section-title {
    font-size: 10px; text-transform: uppercase; letter-spacing: 2px;
    color: #6B7280; margin: 8px 0 16px;
    padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.07);
}
.short-item {
    background: #141720; border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px; padding: 14px 18px;
    display: flex; align-items: center; gap: 14px;
    margin-bottom: 8px; transition: border-color .15s;
}
.short-item:hover { border-color: rgba(232,40,26,0.4); }
.prio-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.short-name { font-size: 14px; font-weight: 500; color: #F0F2F5; }
.short-meta { font-size: 12px; color: #6B7280; margin-top: 2px; }
.status-badge {
    font-size: 11px; padding: 3px 10px; border-radius: 20px; border: 1px solid;
}
.status-suivi { background: rgba(20,184,166,.1); color: #14b8a6; border-color: rgba(20,184,166,.3); }
.status-cible { background: rgba(232,40,26,.1); color: #E8281A; border-color: rgba(232,40,26,.3); }
.status-contacte { background: rgba(245,158,11,.1); color: #f59e0b; border-color: rgba(245,158,11,.3); }
.status-ecarte { background: rgba(107,114,128,.1); color: #6B7280; border-color: rgba(107,114,128,.3); }
div[data-testid="stButton"] button {
    background: #E8281A !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

if not DB_PATH.exists():
    st.warning("Base de données vide.")
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

st.markdown('<div class="page-title">Shortlist</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Cibles de recrutement</div>', unsafe_allow_html=True)

st.markdown('<div class="add-title">Ajouter un joueur</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
with col1:
    joueur_sel = st.selectbox("Joueur", joueurs["nom"].tolist(), label_visibility="collapsed")
with col2:
    priorite = st.selectbox("Priorité", [1, 2, 3],
        format_func=lambda x: {1:"🔴 Haute", 2:"🟡 Moyenne", 3:"⚪ Basse"}[x],
        label_visibility="collapsed")
with col3:
    statut = st.selectbox("Statut", ["suivi", "cible", "contacté", "écarté"],
        label_visibility="collapsed")
with col4:
    ajouter = st.button("+ Ajouter", use_container_width=True)

note = st.text_area("Note scout", placeholder="Points forts, points faibles...",
    label_visibility="collapsed")
scout = st.text_input("Ton nom", value="Scout", label_visibility="collapsed")

if ajouter:
    joueur_id = int(joueurs[joueurs["nom"] == joueur_sel]["id"].iloc[0])
    existing = pd.read_sql(f"SELECT id FROM shortlist WHERE joueur_id = {joueur_id}", conn)
    if not existing.empty:
        st.warning(f"{joueur_sel} est déjà dans la shortlist !")
    else:
        conn.execute("""
            INSERT INTO shortlist (joueur_id, priorite, statut, note, added_by)
            VALUES (?, ?, ?, ?, ?)
        """, (joueur_id, priorite, statut, note, scout))
        conn.commit()
        st.success(f"✓ {joueur_sel} ajouté !")
        st.rerun()

shortlist = load_shortlist()

st.markdown(f'<div class="section-title">Shortlist actuelle — {len(shortlist)} joueurs</div>',
    unsafe_allow_html=True)

PRIO_COLOR = {1: "#E8281A", 2: "#f59e0b", 3: "#6B7280"}
STATUS_CLASS = {"suivi": "status-suivi", "cible": "status-cible",
                "contacté": "status-contacte", "écarté": "status-ecarte"}

if shortlist.empty:
    st.markdown("""
    <div style="background:#141720;border:1px solid rgba(255,255,255,0.07);
    border-radius:10px;padding:20px;text-align:center;color:#6B7280;font-size:13px;">
    Shortlist vide — ajoute des joueurs ci-dessus
    </div>""", unsafe_allow_html=True)
else:
    for _, row in shortlist.iterrows():
        color = PRIO_COLOR.get(row['priorite'], "#6B7280")
        sc = STATUS_CLASS.get(row['statut'], "status-suivi")
        note_html = f'<div style="font-size:12px;color:#6B7280;font-style:italic;flex:1">{row["note"]}</div>' if row["note"] else '<div style="flex:1"></div>'
        st.markdown(f"""