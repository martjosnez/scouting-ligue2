"""
run_ingestion.py — Lance le pipeline complet sur un dossier de captures.

Usage :
    python run_ingestion.py                          # traite data/screenshots/
    python run_ingestion.py --folder mon_dossier/    # dossier custom
    python run_ingestion.py --file une_capture.png   # fichier unique
    python run_ingestion.py --dry-run                # test sans écriture en base
"""
import argparse
import sys
from pathlib import Path

# Ajoute la racine du projet au path
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.ocr_extractor import extract_from_screenshot
from ingestion.validator import validate_extraction, print_report
from ingestion.db_loader import insert_extraction, log_error
from database.init_db import init_db, DB_PATH

SCREENSHOTS_DIR = Path("data/screenshots")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def process_file(image_path: Path, dry_run: bool = False) -> bool:
    """
    Traite une image : OCR → validation → insertion.
    Retourne True si succès.
    """
    print(f"\n{'='*55}")
    print(f"  Traitement : {image_path.name}")
    print(f"{'='*55}")

    # 1. Extraction OCR
    try:
        data = extract_from_screenshot(str(image_path))
    except Exception as e:
        print(f"  ✗ Erreur OCR : {e}")
        if not dry_run:
            log_error(image_path.name, str(e))
        return False

    # 2. Validation
    vr = validate_extraction(data)
    print_report(vr, equipe=data.get("equipe", "?"))

    if not vr.valide or not vr.joueurs_ok:
        print(f"  ✗ Extraction invalide, fichier ignoré.")
        if not dry_run:
            log_error(image_path.name, " | ".join(vr.erreurs))
        return False

    # 3. Insertion
    if dry_run:
        print(f"  [DRY RUN] {len(vr.joueurs_ok)} joueurs prêts à insérer (pas d'écriture)")
        return True

    try:
        nb = insert_extraction(data, vr.joueurs_ok, source_fichier=image_path.name)
        print(f"  ✅ {nb} joueurs insérés/mis à jour en base")
        return True
    except Exception as e:
        print(f"  ✗ Erreur insertion : {e}")
        log_error(image_path.name, str(e))
        return False


def main():
    parser = argparse.ArgumentParser(description="Pipeline ingestion scouting Ligue 2")
    parser.add_argument("--folder", type=str, default=None)
    parser.add_argument("--file",   type=str, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Init base si elle n'existe pas
    if not DB_PATH.exists():
        print("📦 Initialisation de la base SQLite...")
        init_db()

    # Collecte des fichiers à traiter
    if args.file:
        files = [Path(args.file)]
    elif args.folder:
        folder = Path(args.folder)
        files = [f for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]
    else:
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        files = [f for f in SCREENSHOTS_DIR.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]

    if not files:
        print(f"⚠ Aucune image trouvée dans {SCREENSHOTS_DIR}")
        print("  → Place tes captures PNG/JPG dans data/screenshots/")
        return

    print(f"\n🔍 {len(files)} image(s) à traiter {'[DRY RUN]' if args.dry_run else ''}")

    ok, ko = 0, 0
    for f in sorted(files):
        if process_file(f, dry_run=args.dry_run):
            ok += 1
        else:
            ko += 1

    print(f"\n{'='*55}")
    print(f"  RÉSUMÉ : {ok} succès / {ko} échecs / {ok+ko} total")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    main()
