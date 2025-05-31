from flask import current_app
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app import db


class Prompts(db.Model):
    __tablename__ = 'Prompts'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    tipoPrompt = Column(String, nullable=False, unique=True)
    prompt = Column(db.Text, nullable=True)
    context = Column(db.Text, nullable=True)
    json = Column(db.Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)