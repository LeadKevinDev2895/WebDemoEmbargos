
from flask import current_app
from sqlalchemy import Column, Integer, String, Enum, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from .enums import TipoIdentificacion
from app import db

class Demandante(db.Model):
    __tablename__ = 'Demandante'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipoIdentificacion = Column(Enum(TipoIdentificacion), nullable=True)
    numeroIdentificacion = Column(String, nullable=True)
    dv = Column(Integer, nullable=True)
    nombre = Column(String, nullable=True)
    apellido = Column(String, nullable=True)
    razonSocial = Column(String, nullable=True)
    correoElectronico = Column(String, nullable=True)
    direccionFisica = Column(String, nullable=True)
    ciudadDepartamento = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relación con MedidaCautelar
    medidas_cautelares = relationship("MedidaCautelar", back_populates="demandante")
