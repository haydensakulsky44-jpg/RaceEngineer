"""
Charge les bases de connaissances (circuits, voitures, réglementation
multi-discipline, diagnostics de setup, conseils de trajectoire, règles de
course, préparation pilote, bases télémétrie, ...) depuis les fichiers JSON
de backend/knowledge/, et fournit des fonctions de matching par alias pour
le parser.

Les fichiers sont chargés une seule fois puis mis en cache. Pour recharger
à chaud (ex: après une édition manuelle du JSON en dev), voir reload_all().
"""

import json
from pathlib import Path

KNOWLEDGE_ROOT = Path(__file__).parent.parent / "knowledge"

CIRCUITS_PATH = KNOWLEDGE_ROOT / "circuits" / "circuits.json"
CARS_PATH = KNOWLEDGE_ROOT / "cars" / "cars.json"
HANDLING_DIAGNOSTICS_PATH = KNOWLEDGE_ROOT / "setup_guides" / "handling_diagnostics.json"
SETUP_BASICS_PATH = KNOWLEDGE_ROOT / "setup_guides" / "setup_basics.json"
CORNER_TYPES_PATH = KNOWLEDGE_ROOT / "driving_tips" / "corner_types.json"
RACE_RULES_PATH = KNOWLEDGE_ROOT / "race_rules" / "flags_and_penalties.json"
DRIVER_PREP_PATH = KNOWLEDGE_ROOT / "driver_prep" / "physical_mental.json"
TELEMETRY_BASICS_PATH = KNOWLEDGE_ROOT / "telemetry_basics" / "telemetry_basics.json"

REGULATIONS_PATHS = {
    "circuit": KNOWLEDGE_ROOT / "regulations" / "circuit_racing.json",
    "karting": KNOWLEDGE_ROOT / "regulations" / "karting.json",
    "rallye": KNOWLEDGE_ROOT / "regulations" / "rallye.json",
}

_cache = {
    "circuits": None,
    "cars": None,
    "handling_diagnostics": None,
    "setup_basics": None,
    "corner_types": None,
    "race_rules": None,
    "driver_prep": None,
    "telemetry_basics": None,
    "regulations": {},
}


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_circuits() -> dict:
    if _cache["circuits"] is None:
        _cache["circuits"] = _load_json(CIRCUITS_PATH)
    return _cache["circuits"]


def load_cars() -> dict:
    if _cache["cars"] is None:
        _cache["cars"] = _load_json(CARS_PATH)
    return _cache["cars"]


def load_handling_diagnostics() -> dict:
    if _cache["handling_diagnostics"] is None:
        _cache["handling_diagnostics"] = _load_json(HANDLING_DIAGNOSTICS_PATH)
    return _cache["handling_diagnostics"]


def load_setup_basics() -> dict:
    if _cache["setup_basics"] is None:
        _cache["setup_basics"] = _load_json(SETUP_BASICS_PATH)
    return _cache["setup_basics"]


def load_corner_types() -> dict:
    if _cache["corner_types"] is None:
        _cache["corner_types"] = _load_json(CORNER_TYPES_PATH)
    return _cache["corner_types"]


def load_race_rules() -> dict:
    if _cache["race_rules"] is None:
        _cache["race_rules"] = _load_json(RACE_RULES_PATH)
    return _cache["race_rules"]


def load_driver_prep() -> dict:
    if _cache["driver_prep"] is None:
        _cache["driver_prep"] = _load_json(DRIVER_PREP_PATH)
    return _cache["driver_prep"]


def load_telemetry_basics() -> dict:
    if _cache["telemetry_basics"] is None:
        _cache["telemetry_basics"] = _load_json(TELEMETRY_BASICS_PATH)
    return _cache["telemetry_basics"]


def load_regulations(discipline_key: str) -> dict:
    if discipline_key not in _cache["regulations"]:
        path = REGULATIONS_PATHS.get(discipline_key)
        _cache["regulations"][discipline_key] = _load_json(path) if path else {}
    return _cache["regulations"][discipline_key]


def load_all_regulations() -> dict:
    return {key: load_regulations(key) for key in REGULATIONS_PATHS}


def reload_all():
    """Force le rechargement de tous les JSON depuis le disque (utile en dev)."""
    for key in _cache:
        _cache[key] = {} if key == "regulations" else None


def _build_alias_index(entries: dict) -> list[tuple[str, str]]:
    """
    Construit une liste (alias, clé_canonique) triée par longueur d'alias
    décroissante, pour matcher en priorité l'alias le plus spécifique
    (ex: "488 gt3" avant "488").
    Ignore les clés commençant par "_" (métadonnées, ex: "_meta").
    """
    index = []
    for key, infos in entries.items():
        if key.startswith("_"):
            continue
        for alias in infos.get("aliases", [key]):
            index.append((alias.lower(), key))
    index.sort(key=lambda pair: len(pair[0]), reverse=True)
    return index


def find_circuit(message: str) -> str | None:
    message = message.lower()
    for alias, key in _build_alias_index(load_circuits()):
        if alias in message:
            return key
    return None


def find_car(message: str) -> str | None:
    message = message.lower()
    for alias, key in _build_alias_index(load_cars()):
        if alias in message:
            return key
    return None


def find_corner_type(message: str) -> str | None:
    message = message.lower()
    for alias, key in _build_alias_index(load_corner_types()):
        if alias in message:
            return key
    return None


def find_race_rule(message: str) -> str | None:
    message = message.lower()
    for alias, key in _build_alias_index(load_race_rules()):
        if alias in message:
            return key
    return None


def find_driver_prep_topic(message: str) -> str | None:
    message = message.lower()
    for alias, key in _build_alias_index(load_driver_prep()):
        if alias in message:
            return key
    return None


def find_telemetry_topic(message: str) -> str | None:
    message = message.lower()
    for alias, key in _build_alias_index(load_telemetry_basics()):
        if alias in message:
            return key
    return None


def find_discipline(message: str) -> str | None:
    """Détecte quelle discipline (circuit/karting/rallye) est mentionnée."""
    message = message.lower()
    index = []
    for discipline_key, path in REGULATIONS_PATHS.items():
        data = load_regulations(discipline_key)
        aliases = data.get("discipline", {}).get("aliases", [])
        for alias in aliases:
            index.append((alias.lower(), discipline_key))
    index.sort(key=lambda pair: len(pair[0]), reverse=True)
    for alias, key in index:
        if alias in message:
            return key
    return None


def find_pathway_step(message: str) -> tuple[str, str] | None:
    """Détecte une étape précise de filière (ex: 'gt4', 'kz', 'wrc'), toutes
    disciplines confondues, et retourne (discipline_key, step_key)."""
    message = message.lower()
    index = []
    for discipline_key in REGULATIONS_PATHS:
        data = load_regulations(discipline_key)
        for step in data.get("pathway", []):
            for kw in step.get("keywords", []):
                index.append((kw.lower(), discipline_key, step["key"]))
    index.sort(key=lambda triple: len(triple[0]), reverse=True)
    for kw, discipline_key, step_key in index:
        if kw in message:
            return (discipline_key, step_key)
    return None


def get_pathway_step(discipline_key: str, step_key: str) -> dict | None:
    data = load_regulations(discipline_key)
    for step in data.get("pathway", []):
        if step["key"] == step_key:
            return step
    return None


# Mots-clés associés à chaque diagnostic de comportement (sous-virage/survirage).
# Séparé des aliases JSON car ce sont des symptômes exprimés en langage
# naturel plutôt que des noms propres.
_HANDLING_KEYWORDS = {
    "understeer_entry": ["sous-vire en entrée", "sous vire en entrée", "pousse en entrée", "tout droit en entrée"],
    "understeer_mid": ["sous-vire au milieu", "sous vire au milieu", "pousse au milieu"],
    "understeer_exit": ["sous-vire en sortie", "sous vire en sortie", "ne se replace pas"],
    "oversteer_entry": ["survire en entrée", "arrière décroche au freinage", "décroche au freinage"],
    "oversteer_mid": ["survire au milieu", "glisse au milieu", "arrière glisse"],
    "oversteer_exit": ["survire en sortie", "décroche à l'accélération", "perte de traction", "patine en sortie"],
    # formes génériques (sans précision de phase) -> on retombe sur le "mid" par défaut
    "understeer_mid_generic": ["sous-vire", "sous vire", "sousvire", "understeer"],
    "oversteer_mid_generic": ["survire", "surviré", "oversteer"],
}


def find_handling_diagnostic(message: str) -> str | None:
    """
    Retourne la clé canonique du diagnostic sous-virage/survirage détecté,
    en priorisant les formulations précises (avec phase) sur les génériques.
    """
    message = message.lower()

    precise_keys = [k for k in _HANDLING_KEYWORDS if not k.endswith("_generic")]
    for key in precise_keys:
        if any(kw in message for kw in _HANDLING_KEYWORDS[key]):
            return key

    if any(kw in message for kw in _HANDLING_KEYWORDS["understeer_mid_generic"]):
        return "understeer_mid"
    if any(kw in message for kw in _HANDLING_KEYWORDS["oversteer_mid_generic"]):
        return "oversteer_mid"

    return None


def get_circuit(key: str) -> dict | None:
    return load_circuits().get(key)


def get_car(key: str) -> dict | None:
    return load_cars().get(key)


def get_handling_diagnostic(key: str) -> dict | None:
    return load_handling_diagnostics().get(key)


def get_corner_type(key: str) -> dict | None:
    return load_corner_types().get(key)


def get_race_rule(key: str) -> dict | None:
    return load_race_rules().get(key)


def get_driver_prep_topic(key: str) -> dict | None:
    return load_driver_prep().get(key)


def get_telemetry_topic(key: str) -> dict | None:
    return load_telemetry_basics().get(key)
