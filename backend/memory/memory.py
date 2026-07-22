"""
Mémoire utilisateur, maintenant stockée en base de données (table
user_memory) plutôt que dans un fichier JSON plat. L'interface des
fonctions (get_memory/set_memory) reste volontairement proche de l'ancienne
version pour limiter les changements dans le reste du code, mais prend
maintenant une session DB et un user_id numérique (celui du compte
authentifié).
"""

from sqlalchemy.orm import Session

from backend.db.models import UserMemory


def get_memory(db: Session, user_id: int, key: str) -> str | None:
    entry = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id, UserMemory.key == key)
        .first()
    )
    return entry.value if entry else None


def set_memory(db: Session, user_id: int, key: str, value: str) -> None:
    entry = (
        db.query(UserMemory)
        .filter(UserMemory.user_id == user_id, UserMemory.key == key)
        .first()
    )

    if entry:
        entry.value = value
    else:
        entry = UserMemory(user_id=user_id, key=key, value=value)
        db.add(entry)

    db.commit()
