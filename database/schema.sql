-- ============================================================
-- Scouting Ligue 2 — Schéma SQLite
-- Calibré sur le format Teamworks (captures d'écran)
-- ============================================================

CREATE TABLE IF NOT EXISTS equipes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nom         TEXT NOT NULL UNIQUE,
    saison      TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS joueurs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nom             TEXT NOT NULL,
    equipe_id       INTEGER REFERENCES equipes(id),
    poste           TEXT,   -- Pos : C Mid, FullBck, Winger, Strkr, Def Mid...
    role            TEXT,   -- Role : RW, LCB-3, M-DP, ST-1...
    age             REAL,
    valeur_m_eur    REAL,   -- TM Val en millions €
    created_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(nom, equipe_id)
);

CREATE TABLE IF NOT EXISTS stats_match (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    joueur_id       INTEGER NOT NULL REFERENCES joueurs(id),
    source_fichier  TEXT,           -- nom du fichier screenshot source
    saison          TEXT,
    minutes         INTEGER,
    proj_cpm_total  REAL,
    cpm_total       REAL,
    cpm_scored      REAL,
    cpm_conc        REAL,           -- CPM Conceded
    bpm_xgs0_net    REAL,           -- Box Plus/Minus xGS0
    gapm_xgs0_net   REAL,           -- Goal Added Per Match xGS0
    opv_p_total     REAL,           -- Overall Player Value
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS shortlist (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    joueur_id       INTEGER NOT NULL REFERENCES joueurs(id),
    added_by        TEXT DEFAULT 'scout',
    priorite        INTEGER DEFAULT 2, -- 1=haute 2=moyenne 3=basse
    note            TEXT,
    statut          TEXT DEFAULT 'suivi', -- suivi | contacté | écarté
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ingestion_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fichier         TEXT NOT NULL,
    statut          TEXT,   -- success | error | pending
    nb_joueurs      INTEGER DEFAULT 0,
    erreur          TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- Index pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_joueurs_poste ON joueurs(poste);
CREATE INDEX IF NOT EXISTS idx_stats_joueur  ON stats_match(joueur_id);
CREATE INDEX IF NOT EXISTS idx_shortlist_statut ON shortlist(statut);
