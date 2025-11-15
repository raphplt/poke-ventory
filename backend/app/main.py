from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users_router
from app.routes.auth import router as auth_router
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PokeVault API",
    description="API de gestion de collection Pokémon",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_router)
app.include_router(users_router)

@app.get("/health")
def health():
    return {"status": "ok"}
