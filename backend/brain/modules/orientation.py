from backend.brain.knowledge_loader import (
    find_discipline,
    find_pathway_step,
    load_all_regulations,
    load_regulations,
)


def mentions_pathway_topic(message: str) -> bool:
    """Utilisé par le parser pour déclencher l'intention orientation
    quand une discipline ou une catégorie précise (gt3, kz, wrc...) est citée."""
    message = message.lower()
    return find_discipline(message) is not None or find_pathway_step(message) is not None


def _format_step(discipline_key: str, step: dict) -> str:
    discipline = load_regulations(discipline_key).get("discipline", {})
    discipline_name = discipline.get("display_name", discipline_key.title())

    prereqs = "\n".join(f"- {p}" for p in step["prerequisites"])
    budget_min, budget_max = step["estimated_annual_budget_eur"]

    return (
        f"🏁 {step['display_name']} ({discipline_name})\n\n"
        f"{step['description']}\n\n"
        f"Âge minimum indicatif : {step['typical_age_min']} ans\n"
        f"Niveau de licence : {step['license_level']}\n"
        f"Budget annuel estimé : {budget_min:,}€ – {budget_max:,}€\n\n"
        f"Prérequis :\n{prereqs}\n\n"
        f"💡 {step['next_step_advice']}"
    )


def _format_discipline_overview(discipline_key: str) -> str:
    regulations = load_regulations(discipline_key)
    discipline = regulations.get("discipline", {})
    discipline_name = discipline.get("display_name", discipline_key.title())
    pathway = regulations.get("pathway", [])

    lines = []
    for step in pathway:
        budget_min, budget_max = step["estimated_annual_budget_eur"]
        lines.append(
            f"{step['step']}. {step['display_name']} "
            f"(à partir de {step['typical_age_min']} ans, "
            f"~{budget_min:,}€–{budget_max:,}€/an)"
        )

    note = regulations.get("_meta", {}).get("scope", "")

    return (
        f"🏁 Filière {discipline_name} — vue d'ensemble :\n\n"
        + "\n".join(lines)
        + "\n\nDemande-moi plus de détails sur une étape précise pour les prérequis et le budget détaillé."
        + (f"\n\nℹ️ {note}" if note else "")
    )


def _format_global_overview() -> str:
    all_regs = load_all_regulations()

    lines = []
    for discipline_key, data in all_regs.items():
        discipline = data.get("discipline", {})
        name = discipline.get("display_name", discipline_key.title())
        pathway = data.get("pathway", [])
        if not pathway:
            continue
        entry_step = pathway[0]
        top_step = pathway[-1]
        lines.append(
            f"• {name} — de \"{entry_step['display_name']}\" "
            f"à \"{top_step['display_name']}\""
        )

    return (
        "🏁 Trois grandes voies s'offrent à toi en sport automobile :\n\n"
        + "\n".join(lines)
        + "\n\nDis-moi laquelle t'intéresse (karting, circuit, rallye) ou une "
          "catégorie précise (ex: \"GT4\", \"KZ\", \"WRC\") pour le détail "
          "des prérequis, licences et budgets."
    )


def handle(message: str) -> str:
    message = message.lower()

    step_match = find_pathway_step(message)
    if step_match:
        discipline_key, step_key = step_match
        data = load_regulations(discipline_key)
        step = next((s for s in data.get("pathway", []) if s["key"] == step_key), None)
        if step:
            return _format_step(discipline_key, step)

    discipline_key = find_discipline(message)
    if discipline_key:
        return _format_discipline_overview(discipline_key)

    return _format_global_overview()
