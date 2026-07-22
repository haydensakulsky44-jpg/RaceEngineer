"""
Configuration SQLAlchemy. Utilise DATABASE_URL depuis l'environnement.

- En développement, si DATABASE_URL n'est pas défini, on retombe sur un
  fichier SQLite local (data/raceengineer.db) pour pouvoir travailler sans
  serveur PostgreSQL.
- En production, définir DATABASE_URL avec une URL PostgreSQL, ex:
  postgresql://user:password@host:5432/raceengineer
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DATA_DIR / 'raceengineer.db'}")

# SQLite a besoin de cet argument pour fonctionner correctement avec FastAPI
# (qui peut utiliser la connexion depuis plusieurs threads). PostgreSQL n'en
# a pas besoin.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dépendance FastAPI : fournit une session DB et la ferme après la requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crée les tables si elles n'existent pas encore. Appelé au démarrage de l'API."""
    from backend.db import models  # noqa: F401 (nécessaire pour enregistrer les modèles)
    Base.metadata.create_all(bind=engine)
