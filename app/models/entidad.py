# 🔹 Clase para Entidad (Persona Jurídica)

from flask import current_app
from sqlalchemy import Column, Integer, String, Enum, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from .enums import TipoIdentificacion, TipoEntidad
from app import db

class Entidad(db.Model):
    __tablename__ = 'Entidad'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipoIdentificacionEntidad = Column(Enum(TipoIdentificacion), nullable=True)
    numeroIdentificacionEntidad = Column(String, nullable=True)
    tipoEntidad = Column(Enum(TipoEntidad), nullable=True)
    entidad = Column(String, nullable=True)
    correoElectronicoEntidad = Column(String, nullable=True)
    direccionFisicaEntidad = Column(String, nullable=True)
    ciudadDepartamentoEntidad = Column(String, nullable=True)
    telefonoEntidad = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 🔹 Relación con MedidaCautelar
    medida_cautelar = relationship("MedidaCautelar", back_populates="entidad")