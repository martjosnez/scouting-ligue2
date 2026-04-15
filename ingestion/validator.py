"""
validator.py — Valide et nettoie les données extraites par OCR
avant insertion en base.
"""
from __future__ import annotations
from dataclasses import dataclass, field


POSTES_CONNUS = {
    "C Mid", "Def Mid", "C Def", "FullBck", "Winger", "Strkr",
    "Att Mid", "Wng Bck",
}

ROLES_CONNUS = {
    "RW", "LW", "RWB", "LWB", "LB", "RB",
    "M-DP", "M-6", "M-8",
    "LCB-3", "RCB-3", "CB-3", "CB",
    "ST-1", "ST-2", "N.10",
    "AM-DP",
}


@dataclass
class ValidationResult:
    valide: bool = True
    erreurs: list[str] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)
    joueurs_ok: list[dict] = field(default_factory=list)
    joueurs_ko: list[dict] = field(default_factory=list)


def _coerce_float(val, field_name: str, warnings: list) -> float | None:
    """Convertit en float, retourne None si impossible."""
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        warnings.append(f"  '{field_name}' non numérique ({val!r}) → null")
        return None


def _coerce_int(val, field_name: str, warnings: list) -> int | None:
    if val is None:
        return None
    try:
        return int(float(val))
    except (TypeError, ValueError):
        warnings.append(f"  '{field_name}' non entier ({val!r}) → null")
        return None


def validate_joueur(raw: dict) -> tuple[dict | None, list[str], list[str]]:
    """
    Valide un joueur brut issu de l'OCR.

    Returns:
        (joueur_nettoyé_ou_None, erreurs, avertissements)
    """
    errors: list[str] = []
    warnings: list[str] = []

    # ── Champs obligatoires ──────────────────────────────────────────────────
    nom = str(raw.get("nom", "")).strip()
    if not nom:
        errors.append("Nom manquant")
        return None, errors, warnings

    poste = str(raw.get("poste", "")).strip() or None
    if poste and poste not in POSTES_CONNUS:
        warnings.append(f"  Poste inconnu : '{poste}' (accepté quand même)")

    role = str(raw.get("role", "")).strip() or None
    if role and role not in ROLES_CONNUS:
        warnings.append(f"  Rôle inconnu : '{role}' (accepté quand même)")

    age = _coerce_float(raw.get("age"), "age", warnings)
    if age is not None and not (14 <= age <= 45):
        warnings.append(f"  Âge suspect : {age}")

    valeur = _coerce_float(raw.get("valeur_m_eur"), "valeur_m_eur", warnings)
    minutes = _coerce_int(raw.get("minutes"), "minutes", warnings)
    if minutes is not None and minutes < 0:
        warnings.append(f"  Minutes négatives : {minutes} → 0")
        minutes = 0

    # ── Métriques de performance ─────────────────────────────────────────────
    metric_fields = [
        "proj_cpm_total", "cpm_total", "cpm_scored", "cpm_conc",
        "bpm_xgs0_net", "gapm_xgs0_net", "opv_p_total",
    ]
    metrics = {}
    for mf in metric_fields:
        metrics[mf] = _coerce_float(raw.get(mf), mf, warnings)

    # ── Résultat ─────────────────────────────────────────────────────────────
    cleaned = {
        "nom": nom,
        "poste": poste,
        "role": role,
        "age": age,
        "valeur_m_eur": valeur,
        "minutes": minutes,
        **metrics,
    }
    return cleaned, errors, warnings


def validate_extraction(data: dict) -> ValidationResult:
    """
    Valide une extraction complète (résultat de ocr_extractor).

    Args:
        data : dict avec clés equipe, saison, joueurs

    Returns:
        ValidationResult
    """
    result = ValidationResult()

    if not data.get("equipe"):
        result.erreurs.append("Équipe manquante dans l'extraction")
        result.valide = False

    if not data.get("saison"):
        result.avertissements.append("Saison manquante")

    joueurs_raw = data.get("joueurs", [])
    if not joueurs_raw:
        result.erreurs.append("Aucun joueur extrait")
        result.valide = False
        return result

    for i, raw in enumerate(joueurs_raw):
        cleaned, errors, warnings = validate_joueur(raw)

        if errors:
            result.joueurs_ko.append({"index": i, "raw": raw, "erreurs": errors})
            result.avertissements.extend(
                [f"Joueur {i} ignoré : {e}" for e in errors]
            )
        else:
            result.joueurs_ok.append(cleaned)
            if warnings:
                result.avertissements.append(f"Joueur '{cleaned['nom']}':")
                result.avertissements.extend(warnings)

    if not result.joueurs_ok:
        result.erreurs.append("Aucun joueur valide après validation")
        result.valide = False

    return result


def print_report(vr: ValidationResult, equipe: str = "") -> None:
    """Affiche un rapport de validation lisible."""
    titre = f"Rapport validation — {equipe}" if equipe else "Rapport validation"
    print(f"\n{'─'*50}")
    print(titre)
    print(f"{'─'*50}")
    print(f"  Joueurs OK  : {len(vr.joueurs_ok)}")
    print(f"  Joueurs KO  : {len(vr.joueurs_ko)}")

    if vr.erreurs:
        print("\n  ERREURS :")
        for e in vr.erreurs:
            print(f"    ✗ {e}")

    if vr.avertissements:
        print("\n  Avertissements :")
        for w in vr.avertissements:
            print(f"    ⚠ {w}")

    print(f"{'─'*50}\n")
