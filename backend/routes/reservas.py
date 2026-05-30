from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Reserva, Oferta
from schemas import ReservaCreate, ReservaResponse
from typing import List

router = APIRouter(prefix="/reservas", tags=["Reservas"])

@router.post("/", response_model=ReservaResponse)
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    oferta = db.query(Oferta).filter(Oferta.id == reserva.oferta_id).first()
    if not oferta:
        raise HTTPException(status_code=404, detail="Oferta no encontrada")
    if oferta.cupos_disponibles < reserva.num_personas:
        raise HTTPException(status_code=400, detail=f"Solo hay {oferta.cupos_disponibles} cupos disponibles")
    total = float(oferta.precio) * reserva.num_personas
    nueva_reserva = Reserva(**reserva.model_dump(), total=total)
    oferta.cupos_disponibles -= reserva.num_personas
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return nueva_reserva

@router.get("/", response_model=List[ReservaResponse])
def get_reservas(db: Session = Depends(get_db)):
    return db.query(Reserva).order_by(Reserva.creado_en.desc()).all()

@router.get("/{reserva_id}", response_model=ReservaResponse)
def get_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva

@router.put("/{reserva_id}/estado")
def actualizar_estado(reserva_id: int, estado: str, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if estado not in ["pendiente", "confirmada", "cancelada"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    if estado == "cancelada" and reserva.estado != "cancelada":
        oferta = db.query(Oferta).filter(Oferta.id == reserva.oferta_id).first()
        if oferta:
            oferta.cupos_disponibles += reserva.num_personas
    reserva.estado = estado
    db.commit()
    return {"message": f"Reserva #{reserva_id} actualizada a '{estado}'"}

@router.delete("/{reserva_id}")
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    if reserva.estado != "cancelada":
        oferta = db.query(Oferta).filter(Oferta.id == reserva.oferta_id).first()
        if oferta:
            oferta.cupos_disponibles += reserva.num_personas
    db.delete(reserva)
    db.commit()
    return {"message": f"Reserva #{reserva_id} eliminada"}

@router.patch("/{reserva_id}/cupos")
def actualizar_cupos(reserva_id: int, cupos: int, db: Session = Depends(get_db)):
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva.num_personas = cupos
    db.commit()
    return {"message": f"Cupos actualizados a {cupos}"}