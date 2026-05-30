from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import ofertas, reservas, contacto
from database import engine, Base

# Crea las tablas automáticamente si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ExploreRD API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ofertas.router)
app.include_router(reservas.router)
app.include_router(contacto.router)

@app.get("/")
def root():
    return {"message": "ExploreRD API funcionando ✅"}

@app.get("/health")
def health():
    from database import SessionLocal
    try:
        db = SessionLocal()
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db.close()
        return {"status": "ok", "db": "conectado ✅"}
    except Exception as e:
        return {"status": "error", "db": str(e)}
