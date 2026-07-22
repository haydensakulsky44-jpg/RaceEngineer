from backend.brain.knowledge_loader import get_telemetry_topic


def telemetry() -> str:
    """Message générique quand aucun sujet précis n'est identifié."""
    return (
        "Je pourrai bientôt analyser directement tes fichiers de télémétrie. "
        "En attendant, je peux déjà t'expliquer comment lire une trace de vitesse, "
        "de freinage, d'accélérateur, ou le delta time — demande-moi par exemple "
        "'comment lire la télémétrie' ou 'c'est quoi le delta time'."
    )


def topic_response(topic_key: str) -> str | None:
    infos = get_telemetry_topic(topic_key)
    if not infos:
        return None

    lines = [f"📊 {infos['display_name']}"]
    if "explanation" in infos:
        lines.append(f"\n{infos['explanation']}")

    if "what_to_look_for" in infos:
        points = "\n".join(f"- {p}" for p in infos["what_to_look_for"])
        lines.append(f"\nCe qu'il faut regarder :\n{points}")

    if "steps" in infos:
        steps = "\n".join(f"{i}. {s}" for i, s in enumerate(infos["steps"], start=1))
        lines.append(f"\n{steps}")

    return "\n".join(lines)
