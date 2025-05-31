from datetime import datetime

from flask import current_app
from sqlalchemy import Column, String, Integer, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship

from app import db

# Tabla intermedia entre MedidaCautelar y Motivo
MedidaMotivo = Table(
    'MedidaMotivo',
    db.metadata,
    Column('medidaId', Integer, ForeignKey('MedidaCautelar.id', name='fk_medida_motivo_medida'), primary_key=True),
    Column('motivoId', Integer, ForeignKey('Motivos.id', name='fk_medida_motivo_motivo'), primary_key=True),
    Column('fecha_creacion', DateTime, default=datetime.now),
    Column('fecha_actualizacion', DateTime, default=datetime.now, onupdate=datetime.now),

    schema=current_app.config['DATABASE']['SqlSchema']
)

class Motivo(db.Model):
    __tablename__ = 'Motivos'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    etapa = Column(String, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    medidas = relationship("MedidaCautelar", secondary=MedidaMotivo, back_populates="motivos")