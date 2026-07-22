"""
Client d'appel au LLM (API Anthropic / Claude), utilisé en repli par le
router quand aucun module basé sur des règles n'a su répondre.

Configuration requise :
    - Variable d'environnement ANTHROPIC_API_KEY (clé obtenue sur
      https://console.anthropic.com/). Ne jamais coder la clé en dur dans
      le code source.

Installation :
    pip install anthropic
"""

import os

MODEL = "claude-sonnet-5"
MAX_TOKENS = 1024

_client = None
_client_init_error = None


def _get_client():
    """Initialise le client Anthropic une seule fois (lazy loading),
    pour ne pas planter au démarrage de l'app si la lib ou la clé
    manquent et que l'utilisateur n'a pas encore atteint une question
    nécessitant le LLM."""
    global _client, _client_init_error

    if _client is not None or _client_init_error is not None:
        return _client

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        _client_init_error = (
            "Variable d'environnement ANTHROPIC_API_KEY manquante. "
            "Définis-la avant de lancer le serveur (ex: export ANTHROPIC_API_KEY=sk-ant-...)."
        )
        return None

    try:
        import anthropic
    except ImportError:
        _client_init_error = (
            "Le package 'anthropic' n'est pas installé. Lance : pip install anthropic"
        )
        return None

    try:
        _client = anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        _client_init_error = f"Impossible d'initialiser le client Anthropic : {e}"
        return None

    return _client


def ask_llm(message: str, system_prompt: str, context_prefix: str = "") -> str:
    """
    Envoie le message de l'utilisateur au LLM et retourne sa réponse
    textuelle. En cas de problème de configuration ou d'appel API,
    retourne un message d'erreur clair plutôt que de faire planter le
    router (le pilote qui teste l'app doit comprendre ce qui manque).
    """
    client = _get_client()

    if client is None:
        return (
            "⚠️ Le module LLM n'est pas encore configuré côté serveur.\n"
            f"({_client_init_error})"
        )

    full_message = f"{context_prefix}{message}"

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": full_message}],
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

    except Exception as e:
        return (
            "⚠️ Une erreur est survenue en contactant le LLM. "
            f"Détail technique : {e}"
        )
