# Scouting Ligue 2 — MVP

Application interne de scouting basée sur les captures Teamworks.
Pipeline : OCR (Claude Vision) → SQLite → Streamlit

---

## Installation

```bash
git clone <ton-repo>
cd scouting-ligue2
pip install -r requirements.txt
```

Configure ta clé API Anthropic :
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# ou crée un fichier .env avec : ANTHROPIC_API_KEY=sk-ant-...
```

---

## Étape 1 — Ingestion des captures

1. Place tes captures Teamworks dans `data/screenshots/`
2. Lance le pipeline :

```bash
# Test sans écriture en base (recommandé en premier)
python run_ingestion.py --dry-run

# Ingestion réelle
python run_ingestion.py

# Fichier unique
python run_ingestion.py --file data/screenshots/nancy_j12.png
```

---

## Étape 2 — Lancer l'application

```bash
streamlit run app/main.py
```

---

## Structure du projet

```
scouting-ligue2/
├── data/
│   └── screenshots/        ← Dépose tes captures ici
├── database/
│   ├── schema.sql
│   ├── init_db.py
│   └── scouting.db         ← Généré automatiquement
├── ingestion/
│   ├── ocr_extractor.py    ← OCR via Claude Vision
│   ├── validator.py        ← Nettoyage des données
│   └── db_loader.py        ← Insertion SQLite
├── app/
│   ├── main.py
│   └── pages/
│       ├── profil.py
│       ├── comparaison.py
│       └── shortlist.py
├── run_ingestion.py        ← Point d'entrée batch
└── requirements.txt
```

---

## Métriques Teamworks supportées

| Colonne        | Description                        |
|----------------|------------------------------------|
| Mins           | Minutes jouées                     |
| Proj CPM Total | Projection CPM saison              |
| CPM Total      | Contribution Per Match totale      |
| CPM Scored     | Contribution offensive             |
| CPM Conc.      | Contribution défensive             |
| BPM xGS0 Net   | Box Plus/Minus net                 |
| GAPM xGS0 Net  | Goal Added Per Match               |
| OPV-P Total    | Overall Player Value               |
