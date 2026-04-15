"""
db_loader.py — Insère les données validées dans la base SQLite.
Gère les doublons (upsert) et logge chaque ingestion.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "database" / "scouting.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _get_or_create_equipe(conn: sqlite3.Connection, nom: str, saison: str) -> int:
    row = conn.execute(
        "SELECT id FROM equipes WHERE nom = ? AND saison = ?", (nom, saison)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO equipes (nom, saison) VALUES (?, ?)", (nom, saison)
    )
    return cur.lastrowid


def _upsert_joueur(conn: sqlite3.Connection, j: dict, equipe_id: int) -> int:
    """Insère ou met à jour un joueur. Retourne son id."""
    row = conn.execute(
        "SELECT id FROM joueurs WHERE nom = ? AND equipe_id = ?",
        (j["nom"], equipe_id),
    ).fetchone()

    if row:
        conn.execute(
            """UPDATE joueurs SET poste=?, role=?, age=?, valeur_m_eur=?
               WHERE id=?""",
            (j["poste"], j["role"], j["age"], j["valeur_m_eur"], row["id"]),
        )
        return row["id"]
    else:
        cur = conn.execute(
            """INSERT INTO joueurs (nom, equipe_id, poste, role, age, valeur_m_eur)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (j["nom"], equipe_id, j["poste"], j["role"], j["age"], j["valeur_m_eur"]),
        )
        return cur.lastrowid


def insert_extraction(
    data: dict,
    joueurs_valides: list[dict],
    source_fichier: str,
) -> int:
    """
    Insère une extraction complète en base.

    Args:
        data            : dict brut (equipe, saison)
        joueurs_valides : liste de joueurs nettoyés par le validator
        source_fichier  : nom du fichier screenshot source

    Returns:
        Nombre de joueurs insérés/mis à jour
    """
    equipe_nom = data.get("equipe", "Inconnue")
    saison = data.get("saison", "Inconnue")

    with get_connection() as conn:
        equipe_id = _get_or_create_equipe(conn, equipe_nom, saison)
        nb_inseres = 0

        for j in joueurs_valides:
            joueur_id = _upsert_joueur(conn, j, equipe_id)

            # Vérifie si des stats pour cette source existent déjà
            existing = conn.execute(
                "SELECT id FROM stats_match WHERE joueur_id=? AND source_fichier=?",
                (joueur_id, source_fichier),
            ).fetchone()

            if existing:
                conn.execute(
                    """UPDATE stats_match SET
                        minutes=?, proj_cpm_total=?, cpm_total=?, cpm_scored=?,
                        cpm_conc=?, bpm_xgs0_net=?, gapm_xgs0_net=?, opv_p_total=?,
                        saison=?
                       WHERE id=?""",
                    (
                        j["minutes"], j["proj_cpm_total"], j["cpm_total"],
                        j["cpm_scored"], j["cpm_conc"], j["bpm_xgs0_net"],
                        j["gapm_xgs0_net"], j["opv_p_total"], saison,
                        existing["id"],
                    ),
                )
            else:
                conn.execute(
                    """INSERT INTO stats_match
                        (joueur_id, source_fichier, saison, minutes,
                         proj_cpm_total, cpm_total, cpm_scored, cpm_conc,
                         bpm_xgs0_net, gapm_xgs0_net, opv_p_total)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        joueur_id, source_fichier, saison, j["minutes"],
                        j["proj_cpm_total"], j["cpm_total"], j["cpm_scored"],
                        j["cpm_conc"], j["bpm_xgs0_net"], j["gapm_xgs0_net"],
                        j["opv_p_total"],
                    ),
                )
            nb_inseres += 1

        # Log d'ingestion
        conn.execute(
            """INSERT INTO ingestion_log (fichier, statut, nb_joueurs)
               VALUES (?, 'success', ?)""",
            (source_fichier, nb_inseres),
        )
        conn.commit()

    return nb_inseres


def log_error(source_fichier: str, erreur: str) -> None:
    """Enregistre une erreur d'ingestion dans le log."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO ingestion_log (fichier, statut, erreur)
               VALUES (?, 'error', ?)""",
            (source_fichier, erreur),
        )
        conn.commit()
