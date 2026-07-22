from backend.brain.knowledge_loader import get_race_rule


def handle(rule_key: str) -> str | None:
    infos = get_race_rule(rule_key)
    if not infos:
        return None

    lines = [f"🚦 {infos['display_name']}"]

    if "meaning" in infos:
        lines.append(f"\n{infos['meaning']}")

    if "driver_action" in infos:
        actions = "\n".join(f"- {a}" for a in infos["driver_action"])
        lines.append(f"\nÀ faire :\n{actions}")

    if "principles" in infos:
        principles = "\n".join(f"- {p}" for p in infos["principles"])
        lines.append(f"\n{principles}")

    if "types" in infos:
        types = "\n".join(f"- {t}" for t in infos["types"])
        lines.append(f"\n{types}")

    return "\n".join(lines)
