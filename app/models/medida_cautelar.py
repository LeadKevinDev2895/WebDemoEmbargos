
from flask import current_app
from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from .enums import TipoMedida, ClaseDeposito, TipoEmbargo
from app import db
from .motivos import MedidaMotivo


class MedidaCautelar(db.Model):
    __tablename__ = 'MedidaCautelar'
    schema = current_app.config['DATABASE']['SqlSchema']
    __table_args__ = {'schema': schema}

    id = Column(Integer, primary_key=True, autoincrement=True)
    #documento_id = Column(Integer, ForeignKey('Documento.id', name='fk_medida_documento'), nullable=False)  # Relación con Documento
    demandante_id = Column(Integer, ForeignKey('Demandante.id', name='fk_medida_demandante'), nullable=False)  # Relación con Demandante
    entidad_id = Column(Integer, ForeignKey('Entidad.id', name='fk_medida_entidad'), nullable=False)  # Relación con Entidad
    numeroCarteroWeb = Column(String, nullable=True, unique=True)
    numeroIq = Column(String, nullable=True)
    cuentaEnte = Column(String, nullable=True)
    numeroOficio = Column(String, nullable=True)
    firmaOficio = Column(Boolean, nullable=True)
    correoOrigen = Column(Boolean, nullable=True)
    bancoCuentaDeposito = Column(String, nullable=True)
    tipoEmbargo = Column(Enum(TipoEmbargo), nullable=True)
    claseDeposito = Column(Enum(ClaseDeposito), nullable=True)
    tipoMedida = Column(Enum(TipoMedida), nullable=True)
    noAfectarCuentaNomina = Column(Boolean, nullable=True)
    afectarCdt = Column(Boolean, nullable=True)
    multasSancionesReiteraciones = Column(Boolean, nullable=True)
    tercerasPartes = Column(Boolean, nullable=True)
    asociacionProductoEspecifico = Column(Boolean, nullable=True)
    codDespachoJudicial = Column(String, nullable=True)
    annoRadicadoJudicial = Column(String, nullable=True)
    consAsignadoJudicial = Column(String, nullable=True)
    codInstanciaJudicial = Column(String, nullable=True)
    incluir = Column(Boolean, nullable=True)
    removerCuantia = Column(Boolean, nullable=True)
    solicitudProductosDeudores = Column(Boolean, nullable=True)
    cambioCorreo = Column(String, nullable=True)
    existeNuevoCorreo = Column(Boolean, nullable=True)
    cambioCuentaEnte = Column(Boolean, nullable=True)
    existeNuevaCuantia = Column(Boolean, nullable=True)
    cuantiaEnLetras = Column(String, nullable=True)
    procesoRemanante = Column(Boolean, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    destinatariosOficio = Column(String, nullable=True)
    existeOficioAuto = Column(Boolean, nullable=True)
    imagenOficioEmbargo = Column(Boolean, nullable=True)
    existeDerechosEconomicos = Column(Boolean, nullable=True)
    canonArrendamiento = Column(Boolean, nullable=True)
    numeroOficios = Column(String, nullable=True)
    correoDestinatariosOficio = Column(String, nullable=True)
    esCorreoElectronico = Column(Boolean, nullable=True)

    # Relaciones
    resoluciones = relationship("Resolucion", back_populates="medida", overlaps="resoluciones")
    documentos = relationship("Documento", back_populates="medidas_cautelares")
    demandante = relationship("Demandante", back_populates="medidas_cautelares")
    entidad = relationship("Entidad", back_populates="medida_cautelar")
    productos = relationship("Producto", back_populates="medida")
    demandados = relationship("Demandado", back_populates="medida")
    motivos = relationship("Motivo", secondary=MedidaMotivo, back_populates="medidas")