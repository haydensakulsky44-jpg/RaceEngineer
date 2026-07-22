# RaceEngineer

AI assistant for motorsport, sim racing, and driver development.

## Objectif

Aider n'importe qui, débutant ou pilote confirmé, à :
- s'orienter dans le sport automobile (licences, coûts, filières karting/circuit/rallye, réglementation)
- obtenir des specs techniques voiture/circuit
- recevoir des conseils de setup et de pilotage pour gagner du temps au tour
- comprendre les règles de course, se préparer physiquement/mentalement, lire sa télémétrie
- poser des questions ouvertes sur le sport automobile qui sortent du cadre structuré (via le LLM)

## Architecture

```
backend/
  api/
    main.py                    # FastAPI, CORS, rate limiting, endpoint /chat protégé
    rate_limit.py               # limiteur de débit partagé (slowapi)
  auth/                        # inscription, connexion (limitées), JWT
  db/                          # SQLAlchemy (SQLite dev / PostgreSQL prod)
  brain/                       # routeur, parser, modules à règles, LLM fallback
  knowledge/                   # bases de connaissances sport auto (JSON)
  memory/                      # mémoire utilisateur, stockée en DB
frontend/
  index.html                   # porte d'entrée : redirige vers chat.html (connecté)
                                # ou login.html (pas connecté) — pas de page marketing
                                # pour l'instant, un site vitrine séparé viendra plus tard
  login.html                   # connexion
  register.html                # inscription
  chat.html                    # l'application : chat + bouton "Nouveau chat" +
                                # suggestions de questions sous la barre de saisie
  css/style.css
  js/api.js                    # appels API + gestion du token JWT
  js/chat.js                   # logique du chat (envoi, nouveau chat, suggestions)
requirements.txt
.env.example
```

## Installation et lancement — backend

```bash
pip install -r requirements.txt
```

Copie `.env.example` en `.env`, renseigne `ANTHROPIC_API_KEY` et `SECRET_KEY`.

```bash
uvicorn backend.api.main:app --reload
```

## Lancement — frontend (en local)

```bash
cd frontend
python -m http.server 5500
```

Ouvre `http://localhost:5500`. Le backend doit tourner en parallèle.

## Parcours utilisateur (façon ChatGPT/Claude)

1. On arrive sur `index.html` → redirection immédiate et automatique :
   - Pas connecté → `login.html`
   - Déjà connecté (token valide, jusqu'à 7 jours) → directement `chat.html`
2. `chat.html` est "chez soi" : chat prêt à l'emploi, avec des suggestions de
   questions sous la barre de saisie (masquées dès le premier message envoyé)
3. Bouton **"+ Nouveau chat"** : vide la conversation affichée et réaffiche
   les suggestions, sans perdre la session
4. Le token reste valide 7 jours dans le navigateur : pas besoin de se
   reconnecter à chaque visite tant qu'on ne s'est pas explicitement déconnecté

## Sécurité en place

- Mots de passe hashés (bcrypt), sessions par JWT (7 jours)
- `/chat` nécessite un token valide, l'identité vient du token
- Rate limiting par IP : `/chat` 20/min, `/auth/login` 10/min, `/auth/register` 5/heure
- Aucune fuite d'erreur technique vers le client (message générique, détail
  dans les logs serveur uniquement)
- CORS configurable via `FRONTEND_ORIGIN`

## État actuel

- [x] Base de contenu sport auto complète
- [x] Routeur hybride : modules à règles en priorité, LLM en repli
- [x] Authentification complète — testée en conditions réelles
- [x] Base de données (SQLAlchemy, SQLite en dev / PostgreSQL en prod)
- [x] Frontend façon ChatGPT/Claude (porte d'entrée intelligente, chat direct,
      nouveau chat, suggestions) — **à valider en conditions réelles**
- [x] Rate limiting — à valider en conditions réelles
- [x] Masquage des erreurs techniques
- [ ] Fiches réglementation par pays (générique/international pour l'instant)
- [ ] Analyse réelle de fichiers de télémétrie
- [ ] Hébergement / déploiement en production
- [ ] Historique de conversation persistant (le "Nouveau chat" efface juste
      l'affichage, rien n'est encore sauvegardé côté serveur par conversation)
- [ ] Site vitrine séparé pour présenter le projet (idée notée pour plus tard)

## Notes de test

Comme le rate limiting, cette restructuration du frontend (index.html en
porte d'entrée, nouveau chat, suggestions) n'a pas pu être testée dans un
vrai navigateur ici — seulement vérifiée syntaxiquement (HTML bien formé,
JS et CSS sans erreur). **Teste chez toi** : ouvre `index.html`, vérifie la
redirection automatique selon que tu es connecté ou non, envoie un message,
vérifie que les suggestions disparaissent, clique "Nouveau chat" et vérifie
qu'elles réapparaissent.
