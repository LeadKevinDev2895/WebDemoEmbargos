
from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .enums import TipoIdentificacion
from app import db
from flask import current_app 

class Demandado(db.Model):
    
    __tablename__ = 'Demandado'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipoIdentificacion = Column(Enum(TipoIdentificacion), nullable=True)
    numeroIdentificacion = Column(String, nullable=True)
    dv = Column(String, nullable=True)
    nombreApellidosRazonSocial = Column(String, nullable=True)
    cuantiaEmbargada = Column(String, nullable=True)
    cuantiaLetras = Column(String, nullable=True)
    embargoConLimite = Column(Boolean, nullable=True)
    # numResolucionEmbargo = Column(String, nullable=True)
    # numResolucionDesembargo = Column(String, nullable=True)
    medida_id = Column(Integer, ForeignKey('MedidaCautelar.id', name='fk_producto_medida'), nullable=True)  # Relación con MedidaCautelar
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relación con MedidaCautelar
    medida = relationship("MedidaCautelar", back_populates="demandados")
    productos = relationship("Producto", back_populates="demandado")
    resoluciones = relationship("Resolucion", back_populates="demandado")