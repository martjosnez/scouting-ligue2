import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path("database/scouting.db")

st.set_page_config(page_title="Shortlist", layout="wide")
st.title("📋 Shortlist — Cibles de scouting")

if not DB_PATH.exists():
    st.warning("Base de données vide. Lance d'abord l'ingestion.")
    st.stop()

conn = sqlite3.connect(DB_PATH)

joueurs = pd.read_sql("""
    SELECT j.id, j.nom, j.poste, j.age, e.nom as equipe,
           s.cpm_total, s.opv_p_total, s.minutes
    FROM joueurs j
    JOIN equipes e ON j.equipe_id = e.id
    JOIN stats_match s ON s.joueur_id = j.id
""", conn)

shortlist = pd.read_sql("""
    SELECT sl.id, j.nom, j.poste, e.nom as equipe,
           sl.priorite, sl.statut, sl.note, sl.added_by
    FROM shortlist sl
    JOIN joueurs j ON sl.joueur_id = j.id
    JOIN equipes e ON j.equipe_id = e.id
    ORDER BY sl.priorite, sl.created_at DESC
""", conn)

st.subheader("Ajouter un joueur à la shortlist")
col1, col2, col3 = st.columns(3)
with col1:
    joueur_sel = st.selectbox("Joueur", joueurs["nom"].tolist())
with col2:
    priorite = st.selectbox("Priorité", [1, 2, 3],
                            format_func=lambda x: {1:"Haute",2:"Moyenne",3:"Basse"}[x])
with col3:
    statut = st.selectbox("Statut", ["suivi", "contacté", "écarté"])

note = st.text_area("Note scout", placeholder="Points forts, points faibles...")
scout = st.text_input("Ton nom", value="Scout")

if st.button("Ajouter à la shortlist", type="primary"):
    joueur_id = int(joueurs[joueurs["nom"] == joueur_sel]["id"].iloc[0])
    existing = pd.read_sql(
        f"SELECT id FROM shortlist WHERE joueur_id = {joueur_id}", conn
    )
    if not existing.empty:
        st.warning(f"{joueur_sel} est déjà dans la shortlist !")
    else:
        conn.execute("""
            INSERT INTO shortlist (joueur_id, priorite, statut, note, added_by)
            VALUES (?, ?, ?, ?, ?)
        """, (joueur_id, priorite, statut, note, scout))
        conn.commit()
        st.success(f"{joueur_sel} ajouté à la shortlist !")
        st.rerun()

st.markdown("---")
st.subheader(f"Shortlist actuelle — {len(shortlist)} joueurs")

if shortlist.empty:
    st.info("Shortlist vide. Ajoute des joueurs ci-dessus.")
else:
    COULEURS = {1: "🔴", 2: "🟡", 3: "🟢"}
    for _, row in shortlist.iterrows():
        with st.expander(
            f"{COULEURS[row['priorite']]} {row['nom']} — {row['equipe']} — {row['statut']}"
        ):
            c1, c2, c3 = st.columns(3)
            c1.write(f"Poste : {row['poste']}")
            c2.write(f"Statut : {row['statut']}")
            c3.write(f"Scout : {row['added_by']}")
            if row["note"]:
                st.write(f"Note : {row['note']}")
            if st.button("Retirer de la shortlist", key=f"del_{row['id']}"):
                conn.execute("DELETE FROM shortlist WHERE id = ?", (row["id"],))
                conn.commit()
                st.rerun()

conn.close()