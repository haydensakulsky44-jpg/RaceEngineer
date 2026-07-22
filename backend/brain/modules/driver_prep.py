from backend.brain.knowledge_loader import get_driver_prep_topic


def handle(topic_key: str) -> str | None:
    infos = get_driver_prep_topic(topic_key)
    if not infos:
        return None

    tips = "\n".join(f"- {tip}" for tip in infos["tips"])

    return f"💪 {infos['display_name']}\n\n{tips}"
