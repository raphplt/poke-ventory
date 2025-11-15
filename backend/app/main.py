from fastapi import FastAPI
from app.routes import users_router
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PokeVentory API",
    description="API de gestion de collection Pokémon",
    version="0.1.0"
)

app.include_router(users_router)

@app.get("/health")
def health():
    return {"status": "ok"}
