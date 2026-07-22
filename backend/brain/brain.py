from backend.brain.router import route


def think(message: str, user_id: int, db):
    return route(message, user_id, db)