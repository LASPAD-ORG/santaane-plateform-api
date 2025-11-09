from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Santaane API", version="0.1.0")

# Inclure les routes
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur Santaane API 🚀"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Santaane API"}
