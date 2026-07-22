from backend.brain.knowledge_loader import get_circuit


def handle(circuit_key: str) -> str | None:
    """
    Construit la fiche circuit à partir de sa clé canonique
    (déjà résolue par le parser via find_circuit).
    """
    infos = get_circuit(circuit_key)

    if not infos:
        return None

    tips = "\n".join(f"- {tip}" for tip in infos["tips"])

    return (
        f"📍 {infos.get('display_name', circuit_key.title())}\n\n"
        f"Pays : {infos['country']}\n"
        f"Longueur : {infos['length_km']} km\n"
        f"Virages : {infos['corners']}\n\n"
        f"{infos['description']}\n\n"
        f"Conseils :\n{tips}"
    )
