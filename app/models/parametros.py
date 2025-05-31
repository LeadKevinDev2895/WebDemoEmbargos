from flask import current_app
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app import db

class Parametros(db.Model):
    __tablename__ = 'Parametros'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    ramaPadre = Column(String, nullable=True)
    llave = Column(String, nullable=False)
    valor = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)