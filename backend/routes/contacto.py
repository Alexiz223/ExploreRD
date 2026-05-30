from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import ContactoMensaje
from schemas import ContactoCreate, ContactoResponse
from typing import List

router = APIRouter(prefix="/contacto", tags=["Contacto"])

@router.post("/", response_model=ContactoResponse)
def enviar_mensaje(contacto: ContactoCreate, db: Session = Depends(get_db)):
    nuevo = ContactoMensaje(**contacto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=List[ContactoResponse])
def get_mensajes(db: Session = Depends(get_db)):
    return db.query(ContactoMensaje).order_by(ContactoMensaje.creado_en.desc()).all()

@router.delete("/{mensaje_id}")
def eliminar_mensaje(mensaje_id: int, db: Session = Depends(get_db)):
    msg = db.query(ContactoMensaje).filter(ContactoMensaje.id == mensaje_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    db.delete(msg)
    db.commit()
    return {"message": "Mensaje eliminado"}