from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Date, Enum, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Oferta(Base):
    __tablename__ = "ofertas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=False)
    descripcion_larga = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    duracion = Column(String(50))
    ubicacion = Column(String(150))
    imagen_url = Column(String(300))
    cupos_disponibles = Column(Integer, default=10)
    itinerario = Column(Text)
    activo = Column(Boolean, default=True)
    creado_en = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    reservas = relationship("Reserva", back_populates="oferta")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    oferta_id = Column(Integer, ForeignKey("ofertas.id"), nullable=False)
    nombre_cliente = Column(String(100), nullable=False)
    apellido_cliente = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    telefono = Column(String(20))
    fecha_reserva = Column(Date, nullable=False)
    num_personas = Column(Integer, default=1)
    metodo_pago = Column(Enum("tarjeta", "transferencia", "efectivo"), nullable=False)
    estado = Column(Enum("pendiente", "confirmada", "cancelada"), default="pendiente")
    total = Column(Numeric(10, 2))
    notas = Column(Text)
    creado_en = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    oferta = relationship("Oferta", back_populates="reservas")

class ContactoMensaje(Base):
    __tablename__ = "contacto_mensajes"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    creado_en = Column(TIMESTAMP, default=datetime.datetime.utcnow)
