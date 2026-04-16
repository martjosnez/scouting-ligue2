"""
ocr_extractor.py — Extrait les données joueurs depuis une capture Teamworks
en utilisant l'API Claude Vision.

Usage :
    from ingestion.ocr_extractor import extract_from_screenshot
    data = extract_from_screenshot("screenshots/nancy_2025.png", equipe="Nancy", saison="2025/26")
"""
from dotenv import load_dotenv
load_dotenv()
import anthropic
import base64
import json
import re
from pathlib import Path


# ── Prompt calibré sur le format Teamworks observé ──────────────────────────
EXTRACTION_PROMPT = """Tu es un assistant d'extraction de données sportives.
Analyse ce tableau Teamworks et extrait TOUS les joueurs visibles.

Les colonnes présentes sont (dans l'ordre habituel) :
- Name       : nom complet du joueur
- Pos        : poste (C Mid, FullBck, Winger, Strkr, Def Mid, C Def...)
- Role       : rôle tactique (RW, LCB-3, M-DP, ST-1, ST-2, LB, RWB, LW...)
- Age        : âge décimal (ex: 25.7)
- TM Val     : valeur Transfermarkt (ex: "0.6M €" → 0.6)
- Mins       : minutes jouées (entier)
- Proj CPM Total : projection CPM (décimal)
- CPM Total  : contribution par match totale
- CPM Scored : contribution offensive
- CPM Conc.  : contribution défensive (conceded)
- BPM xGS0 Net : box plus/minus net
- GAPM xGS0 Net : goal added per match
- OPV-P Total : overall player value

Retourne UNIQUEMENT un JSON valide, sans texte autour, sans balises markdown.
Format exact :
{
  "equipe": "nom de l'équipe visible dans le filtre ou le titre",
  "saison": "saison visible (ex: 2025/26)",
  "joueurs": [
    {
      "nom": "Prénom Nom",
      "poste": "C Mid",
      "role": "RW",
      "age": 25.7,
      "valeur_m_eur": 0.6,
      "minutes": 2252,
      "proj_cpm_total": 48.0,
      "cpm_total": 29.0,
      "cpm_scored": 27.0,
      "cpm_conc": 44.0,
      "bpm_xgs0_net": 35.0,
      "gapm_xgs0_net": 52.0,
      "opv_p_total": 23.0
    }
  ]
}

Notes importantes :
- Les valeurs colorées en rouge/orange dans le tableau sont des deltas — ignore les petits chiffres colorés à côté des valeurs, garde uniquement la valeur principale.
- Si une valeur est manquante ou illisible, mets null.
- Extrait TOUS les joueurs visibles, même ceux en bas de tableau.
"""


def _encode_image(path: str) -> tuple[str, str]:
    """Encode l'image en base64 et détecte le media type."""
    p = Path(path)
    ext = p.suffix.lower()
    media_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    media_type = media_types.get(ext, "image/png")
    data = base64.standard_b64encode(p.read_bytes()).decode("utf-8")
    return data, media_type


def _clean_json_response(text: str) -> str:
    """Nettoie la réponse si elle contient des balises markdown résiduelles."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

def extract_from_screenshot(
    image_path: str,
    equipe: str | None = None,
    saison: str | None = None,
) -> dict:
    """
    Envoie une capture Teamworks à Claude Vision et retourne les données structurées.

    Args:
        image_path : chemin vers le fichier image (PNG/JPG)
        equipe     : nom de l'équipe (optionnel, sera détecté dans l'image sinon)
        saison     : saison (optionnel, sera détectée dans l'image sinon)

    Returns:
        dict avec clés : equipe, saison, joueurs (liste)

    Raises:
        ValueError  : si la réponse n'est pas du JSON valide
        FileNotFoundError : si le fichier image n'existe pas
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    img_data, media_type = _encode_image(str(image_path))

    # Enrichit le prompt si on connaît déjà l'équipe/saison
    prompt = EXTRACTION_PROMPT
    if equipe:
        prompt += f"\n\nInfo supplémentaire : l'équipe est '{equipe}'."
    if saison:
        prompt += f" La saison est '{saison}'."

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": img_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )

    raw_text = response.content[0].text
    clean_text = _clean_json_response(raw_text)

    try:
        result = json.loads(clean_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Réponse Claude non parseable en JSON.\n"
            f"Erreur : {e}\n"
            f"Réponse brute (200 premiers chars) : {raw_text[:200]}"
        )

    # Normalise les champs optionnels
    result.setdefault("equipe", equipe or "Inconnue")
    result.setdefault("saison", saison or "Inconnue")
    result.setdefault("joueurs", [])

    print(f"✅ {image_path.name} → {len(result['joueurs'])} joueurs extraits")
    return result
