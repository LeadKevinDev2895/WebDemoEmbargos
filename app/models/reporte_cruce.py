
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app import db

class ReporteCruce(db.Model):
    __tablename__ = 'ReporteCruce'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    numRadicado = Column(String, nullable=True)
    masivo = Column(String, nullable=True)
    cantidadMedidas = Column(Integer, nullable=True)
    cantidadAnexos = Column(Integer, nullable=True)
    corte = Column(String, nullable=True)
    rutaArchivo = Column(String, nullable=True)
    cantidadPaginas = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)