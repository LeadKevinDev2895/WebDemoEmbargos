from flask import current_app
from app import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Resolucion(db.Model):
    __tablename__ = "Resolucion"
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String, nullable=True)
    tipo = Column(String, nullable=True)  # Puede ser "Embargo", "Desembargo", placa, radicado, etc

    # Relación con MedidaCautelar (opcional)
    medida_id = Column(Integer, ForeignKey("MedidaCautelar.id", name="fk_resolucion_medida"), nullable=True)

    # Relación con Demandado (opcional)
    demandado_id = Column(Integer, ForeignKey("Demandado.id", name="fk_resolucion_demandado"), nullable=True)

    # Relaciónes
    medida = relationship("MedidaCautelar", back_populates="resoluciones", overlaps="resoluciones")
    demandado = relationship("Demandado", back_populates="resoluciones")
