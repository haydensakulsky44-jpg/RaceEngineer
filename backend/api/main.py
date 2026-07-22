import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session

from backend.api.rate_limit import limiter
from backend.auth.dependencies import get_current_user
from backend.auth.routes import router as auth_router
from backend.brain.brain import think
from backend.db.database import get_db, init_db
from backend.db.models import User

# Lancer avec : uvicorn backend.api.main:app --reload

load_dotenv()  # charge ANTHROPIC_API_KEY, SECRET_KEY, DATABASE_URL, etc. depuis .env

app = FastAPI(title="RaceEngineer API")

RACEENGINEER_NAME = "RaceEngineer"
VERSION = "0.5"

# ---- CORS ----
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN")
allow_origins = [FRONTEND_ORIGIN] if FRONTEND_ORIGIN else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,  # on utilise un Bearer token, pas des cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Rate limiting (protection anti-abus) ----
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Trop de requêtes. Attends un instant avant de réessayer."},
    )


# ---- Filet de sécurité : ne jamais renvoyer de détail technique au client.
# Les vraies erreurs restent visibles dans les logs serveur (le terminal
# où tourne uvicorn) pour le débogage, mais le client ne voit qu'un message
# générique — pas de traceback, pas de chemin de fichier, rien d'exploitable.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue. Réessaie dans un instant."},
    )


app.include_router(auth_router)


@app.on_event("startup")
def on_startup():
    init_db()


class ChatRequest(BaseModel):
    message: str


@app.get("/status")
def status():
    return {
        "status": "online",
        "name": RACEENGINEER_NAME,
        "version": VERSION,
    }


@app.post("/chat")
@limiter.limit("20/minute")
def chat(
    request: Request,  # requis par slowapi pour identifier l'appelant (IP)
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Nécessite un token Bearer valide (obtenu via POST /auth/login).
    L'identité de l'utilisateur vient du token, jamais d'un champ envoyé
    par le client.
    """
    response = think(payload.message, current_user.id, db)

    return {
        "assistant": RACEENGINEER_NAME,
        "version": VERSION,
        "question": payload.message,
        "response": response,
    }
