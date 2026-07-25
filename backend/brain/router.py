from backend.brain.modules import circuits, orientation, driving_tips, race_rules, driver_prep
from backend.brain.modules.general import greeting
from backend.brain.modules.setup import setup, diagnostic_response, priority_advice
from backend.brain.modules.telemetry import telemetry, topic_response as telemetry_topic_response
from backend.brain.knowledge_loader import find_car, get_car, get_circuit
from backend.memory.memory import set_memory, get_memory
from backend.brain.parser import parse_message
from backend.brain.llm.client import ask_llm
from backend.brain.llm.prompts import SYSTEM_PROMPT, build_user_context


def route(message: str, user_id: int, db) -> str:
    intent = parse_message(message)
    message_lower = message.lower()

    responses = {
        "circuit": None,
        "diagnostic": None,
        "corner_tip": None,
        "race_rule": None,
        "driver_prep": None,
        "priority_advice": None,
        "setup": None,
        "telemetry": None,
        "orientation": None,
        "general": None,
    }

    if "je roule en" in message_lower:
        raw_car = message_lower.replace("je roule en", "").strip()
        car_key = find_car(raw_car)

        if car_key:
            car_name = get_car(car_key)["display_name"]
            set_memory(db, user_id, "car", car_key)
            return f"Ok, je retiens que tu roules en {car_name}."

        set_memory(db, user_id, "car", raw_car)
        return f"Ok, je retiens que tu roules en {raw_car} (voiture pas encore dans ma base de connaissances)."

    if intent["greeting"]:
        responses["general"] = greeting()

    if intent["handling_diagnostic"]:
        responses["diagnostic"] = diagnostic_response(intent["handling_diagnostic"])

    if intent["corner_type"]:
        responses["corner_tip"] = driving_tips.handle(intent["corner_type"])

    if intent["race_rule"]:
        responses["race_rule"] = race_rules.handle(intent["race_rule"])

    if intent["driver_prep_topic"]:
        responses["driver_prep"] = driver_prep.handle(intent["driver_prep_topic"])

    if intent["priority_advice"]:
        responses["priority_advice"] = priority_advice()

    if intent["setup"] and not responses["diagnostic"]:
        car_key = intent["car"] or get_memory(db, user_id, "car")
        circuit_key = intent["circuit"]

        car_infos = get_car(car_key) if car_key else None
        circuit_infos = get_circuit(circuit_key) if circuit_key else None

        if car_infos and circuit_infos:
            return (
                f"Setup {car_infos['display_name']} pour "
                f"{circuit_infos['display_name']} : priorité stabilité et traction."
            )

        car_msg = f"Tu roules en {car_infos['display_name']}. " if car_infos else ""
        responses["setup"] = car_msg + setup()

    if intent["telemetry_topic"]:
        responses["telemetry"] = telemetry_topic_response(intent["telemetry_topic"])
    elif intent["telemetry"]:
        responses["telemetry"] = telemetry()

    if intent["orientation"]:
        responses["orientation"] = orientation.handle(message_lower)

    show_bare_circuit = intent["circuit"] and not (
        intent["performance_question"] and not intent["setup"]
    )
    if show_bare_circuit:
        responses["circuit"] = circuits.handle(intent["circuit"])

    ordered = []
    for key in [
        "circuit", "diagnostic", "corner_tip", "race_rule", "driver_prep",
        "priority_advice", "setup", "telemetry", "orientation", "general",
    ]:
        if responses[key]:
            ordered.append(responses[key])

    if not ordered:
        car_key = get_memory(db, user_id, "car")
        car_infos = get_car(car_key) if car_key else None
        car_display_name = car_infos["display_name"] if car_infos else car_key

        context_prefix = build_user_context(car_key, car_display_name)
        return ask_llm(message, SYSTEM_PROMPT, context_prefix)

    return "\n\n".join(ordered)