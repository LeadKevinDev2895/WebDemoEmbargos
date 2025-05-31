
from flask import current_app
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app import db
from .enums import TipoDocumento, TipoProcesamiento

class Documento(db.Model):
    __tablename__ = 'Documento'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    fechaRecepcion = Column(String, nullable=True)
    rutaDocumento = Column(String, nullable=True)
    rutaDocumentoConvertido = Column(String, nullable=True)
    tipoDocumento = Column(Enum(TipoDocumento), nullable=True)
    hashDocumento = Column(String, nullable=True)
    tipoProcesamiento = Column(Enum(TipoProcesamiento), nullable=True)
    estadoOficio = Column(String, nullable=True)
    estadoProceso = Column(String, nullable=True)
    motivoNovedad = Column(String, nullable=True)
    idPadre = Column(Integer, ForeignKey('Documento.id', name='fk_documento_id_padre'), nullable=True)  # Relación jerárquica con Documento
    corte = Column(String, nullable=False)
    cantidadPaginas = Column(Integer, nullable=True)
    medida_id = Column(Integer, ForeignKey('MedidaCautelar.id', name='fk_documento_medida'), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    medidas_cautelares = relationship("MedidaCautelar", back_populates="documentos")
