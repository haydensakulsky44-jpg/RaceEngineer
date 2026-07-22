"""
Fonctions de sécurité : hash de mot de passe (bcrypt direct) et tokens JWT
(via python-jose) pour l'authentification par Bearer token.

Note : on utilise le package "bcrypt" directement plutôt que "passlib",
qui n'est plus maintenu et a un bug de compatibilité connu avec les
versions récentes de bcrypt (passlib >= 4.1 lève une erreur au premier hash).
"""

import os
from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 jours

# bcrypt ignore silencieusement tout ce qui dépasse 72 octets ; on tronque
# nous-mêmes pour un comportement prévisible plutôt que de laisser la lib
# lever une erreur sur un mot de passe très long.
_BCRYPT_MAX_BYTES = 72


def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    hashed = bcrypt.hashpw(truncated, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    truncated = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(truncated, hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY n'est pas défini. Ajoute une valeur aléatoire longue dans .env "
            "(génère-en une avec : python -c \"import secrets; print(secrets.token_hex(32))\")."
        )

    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    if not SECRET_KEY:
        return None
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
