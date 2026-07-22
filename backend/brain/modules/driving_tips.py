from backend.brain.knowledge_loader import get_corner_type


def handle(corner_key: str) -> str | None:
    infos = get_corner_type(corner_key)
    if not infos:
        return None

    tips = "\n".join(f"- {tip}" for tip in infos["tips"])

    return f"🏎️ {infos['display_name']}\n\nConseils :\n{tips}"
