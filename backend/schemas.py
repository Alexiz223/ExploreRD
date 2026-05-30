from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from decimal import Decimal

class OfertaCreate(BaseModel):
    nombre: str
    descripcion: str
    descripcion_larga: Optional[str] = None
    precio: Decimal
    duracion: Optional[str] = None
    ubicacion: Optional[str] = None
    imagen_url: Optional[str] = None
    cupos_disponibles: int = 10
    itinerario: Optional[str] = None

class OfertaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    descripcion_larga: Optional[str] = None
    precio: Decimal
    duracion: Optional[str] = None
    ubicacion: Optional[str] = None
    imagen_url: Optional[str] = None
    cupos_disponibles: int
    itinerario: Optional[str] = None

    class Config:
        from_attributes = True

class ReservaCreate(BaseModel):
    oferta_id: int
    nombre_cliente: str
    apellido_cliente: str
    email: EmailStr
    telefono: Optional[str] = None
    fecha_reserva: date
    num_personas: int
    metodo_pago: str
    notas: Optional[str] = None

class ReservaResponse(ReservaCreate):
    id: int
    estado: str
    total: Optional[Decimal] = None

    class Config:
        from_attributes = True

class ContactoCreate(BaseModel):
    nombre: str
    email: EmailStr
    mensaje: str

class ContactoResponse(ContactoCreate):
    id: int

    class Config:
        from_attributes = True