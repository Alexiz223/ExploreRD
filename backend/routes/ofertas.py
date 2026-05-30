from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Oferta
from schemas import OfertaResponse, OfertaCreate
from typing import List

router = APIRouter(prefix="/ofertas", tags=["Ofertas"])

@router.get("/", response_model=List[OfertaResponse])
def get_ofertas(db: Session = Depends(get_db)):
    return db.query(Oferta).filter(Oferta.activo == True).all()

@router.post("/", response_model=OfertaResponse)
def crear_oferta(oferta: OfertaCreate, db: Session = Depends(get_db)):
    nueva = Oferta(**oferta.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.get("/{oferta_id}", response_model=OfertaResponse)
def get_oferta(oferta_id: int, db: Session = Depends(get_db)):
    oferta = db.query(Oferta).filter(Oferta.id == oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    return oferta

@router.put("/{oferta_id}", response_model=OfertaResponse)
def actualizar_oferta(oferta_id: int, oferta: OfertaCreate, db: Session = Depends(get_db)):
    obj = db.query(Oferta).filter(Oferta.id == oferta_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    for k, v in oferta.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{oferta_id}")
def eliminar_oferta(oferta_id: int, db: Session = Depends(get_db)):
    obj = db.query(Oferta).filter(Oferta.id == oferta_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    obj.activo = False
    db.commit()
    return {"message": f"Oferta #{oferta_id} eliminada"}