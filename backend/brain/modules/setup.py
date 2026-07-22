from backend.brain.knowledge_loader import get_handling_diagnostic, load_setup_basics


def setup() -> str:
    """Message générique quand on n'a ni voiture ni circuit ni symptôme précis."""
    return "Indique le jeu, la voiture et le circuit pour un setup, ou décris le comportement de la voiture (ex: 'elle sous-vire en entrée de virage')."


def diagnostic_response(diagnostic_key: str) -> str | None:
    """Construit une réponse de diagnostic sous-virage/survirage à partir de la clé détectée."""
    infos = get_handling_diagnostic(diagnostic_key)
    if not infos:
        return None

    causes = "\n".join(f"- {c}" for c in infos["likely_causes"])
    adjustments = "\n".join(f"- {a}" for a in infos["adjustments"])

    return (
        f"🔧 {infos['display_name']}\n\n"
        f"Causes probables :\n{causes}\n\n"
        f"Pistes de réglage :\n{adjustments}"
    )


def priority_advice() -> str:
    """Renvoie l'ordre de priorité conseillé pour travailler les réglages."""
    basics = load_setup_basics()
    order = basics.get("optimization_priority_order", [])
    note = basics.get("optimization_priority_note", "")

    lines = []
    for i, key in enumerate(order, start=1):
        infos = basics.get(key, {})
        display = infos.get("display_name", key)
        role = infos.get("role", "")
        lines.append(f"{i}. {display} — {role}")

    return (
        "🎯 Par où commencer pour gagner du temps rapidement :\n\n"
        + "\n".join(lines)
        + (f"\n\n{note}" if note else "")
    )
