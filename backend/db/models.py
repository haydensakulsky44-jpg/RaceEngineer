from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    memory_entries = relationship(
        "UserMemory", back_populates="user", cascade="all, delete-orphan"
    )


class UserMemory(Base):
    """
    Remplace l'ancien memory.json : mémoire clé/valeur par utilisateur
    (ex: key="car", value="bmw_m4_gt3"), maintenant stockée en base et liée
    à un vrai compte utilisateur authentifié.
    """
    __tablename__ = "user_memory"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_user_memory_key"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    user = relationship("User", back_populates="memory_entries")
