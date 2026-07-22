"""
Limiteur de débit partagé (protection anti-abus). Défini dans un module à
part pour que main.py et auth/routes.py puissent tous les deux l'utiliser
sans créer d'import circulaire.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Une limite par adresse IP. Simple et suffisant pour démarrer ; si le site
# passe derrière un proxy/CDN plus tard, il faudra adapter get_remote_address
# pour lire le bon en-tête (X-Forwarded-For) plutôt que l'IP directe.
limiter = Limiter(key_func=get_remote_address)
