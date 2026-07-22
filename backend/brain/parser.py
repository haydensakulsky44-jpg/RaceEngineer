"""
Analyse un message utilisateur et en extrait :
- les intentions détectées (setup, telemetry, orientation, greeting,
  priority_advice, race_rules, driver_prep, telemetry_topic)
- les entités reconnues (voiture, circuit, diagnostic sous-virage/survirage,
  type de virage, règle de course, sujet de préparation pilote, sujet de
  télémétrie) via le knowledge_loader (matching par alias/mots-clés, basé
  sur les JSON de backend/knowledge/, donc rien n'est codé en dur ici)
"""

from backend.brain.knowledge_loader import (
    find_car,
    find_circuit,
    find_corner_type,
    find_driver_prep_topic,
    find_handling_diagnostic,
    find_race_rule,
    find_telemetry_topic,
)
from backend.brain.modules.orientation import mentions_pathway_topic

GREETING_WORDS = ["bonjour", "salut", "hello", "coucou"]
SETUP_WORDS = ["setup", "réglage", "reglage", "régler", "regler"]
TELEMETRY_WORDS = ["telemetrie", "télémétrie", "telemetry", "data", "analyse ma"]
ORIENTATION_WORDS = [
    "licence", "license", "permis", "coût", "cout", "prix", "budget",
    "comment débuter", "comment commencer", "fédération", "federation",
    "réglementation", "reglementation", "catégorie", "categorie",
    "filière", "filiere", "carrière", "carriere",
]
PRIORITY_WORDS = [
    "par où commencer", "par ou commencer", "priorité", "priorite",
    "quoi régler en premier", "quoi regler en premier", "commencer par quoi",
    "gagner du temps",
]


def parse_message(message: str) -> dict:
    message_lower = message.lower()

    intent = {
        "setup": any(word in message_lower for word in SETUP_WORDS),
        "telemetry": any(word in message_lower for word in TELEMETRY_WORDS),
        "orientation": any(word in message_lower for word in ORIENTATION_WORDS)
        or mentions_pathway_topic(message_lower),
        "greeting": any(word in message_lower for word in GREETING_WORDS),
        "priority_advice": any(word in message_lower for word in PRIORITY_WORDS),
        "circuit": find_circuit(message_lower),
        "car": find_car(message_lower),
        "handling_diagnostic": find_handling_diagnostic(message_lower),
        "corner_type": find_corner_type(message_lower),
        "race_rule": find_race_rule(message_lower),
        "driver_prep_topic": find_driver_prep_topic(message_lower),
        "telemetry_topic": find_telemetry_topic(message_lower),
    }

    return intent
