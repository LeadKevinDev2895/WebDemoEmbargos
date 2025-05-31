
from flask import current_app
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from app import db

class Producto(db.Model):
    __tablename__ = 'Producto'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipoProducto = Column(String, nullable=True)
    numeroProducto = Column(String, nullable=True)
    sigla = Column(String, nullable=True)
    # Relación con Demandado (en caso de que el producto esté vinculado a un demandado)
    demandado_id = Column(Integer, ForeignKey("Demandado.id", name="fk_producto_demandado"), nullable=True)
    # Relación con MedidaCautelar (en caso de que el producto esté vinculado a la medida en general)
    medida_id = Column(Integer, ForeignKey("MedidaCautelar.id", name="fk_producto_medida"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Definir relaciones
    medida = relationship("MedidaCautelar", back_populates="productos")
    demandado = relationship("Demandado", back_populates="productos")
