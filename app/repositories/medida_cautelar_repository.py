from sqlalchemy import or_
from app import db
from app.models.medida_cautelar import MedidaCautelar
from app.models.demandante import Demandante
from app.models.demandado import Demandado
from app.models.producto import Producto
from app.models.documento import Documento

class MedidaCautelarRepository:
    """Repository layer for managing MedidaCautelar database interactions."""

    @staticmethod
    def get_all():
        """Retrieve all records."""
        return MedidaCautelar.query.all()

    @staticmethod
    def get_by_id(record_id):
        """Retrieve a record by its ID."""
        return MedidaCautelar.query.get(record_id)

    @staticmethod
    def create(data):
        """Create a new record."""
        new_record = MedidaCautelar(**data)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    @staticmethod
    def update(record_id, data):
        """Update an existing record by its ID."""
        record = MedidaCautelar.query.get(record_id)
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        db.session.commit()
        return record

    @staticmethod
    def delete(record_id):
        """Delete a record by its ID."""
        record = MedidaCautelar.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record

    @staticmethod
    def obtener_vista_medidas(cartero, tipo_embargo):
        """
        Retrieve a filtered view of medidas based on cartero and tipo_embargo.

        :param cartero: The cartero number to filter by.
        :param tipo_embargo: The type of measure ("EMBARGO" or "DESEMBARGO").
        :return: A list of dictionaries with the filtered results.
        """
        try:
            resultados = (
                db.session.query(
                    MedidaCautelar.numeroCarteroWeb,
                    Demandante.tipoEntidad,
                    Demandante.nombre,
                    Demandante.correoElectronico,
                    Demandante.direccionFisica,
                    Demandante.ciudadDepartamento,
                    MedidaCautelar.numeroOficio,
                    MedidaCautelar.firmaOficio,
                    Demandado.numResolucionEmbargo,
                    Demandado.numResolucionDesembargo,
                    MedidaCautelar.codDespachoJudicial,
                    MedidaCautelar.annoRadicadoJudicial,
                    MedidaCautelar.consAsignadoJudicial,
                    MedidaCautelar.codInstanciaJudicial,
                    MedidaCautelar.tipoMedida,
                    Documento.fechaRecepcion,
                    Demandado.tipoIdentificacion,
                    Demandado.numeroIdentificacion,
                    Demandado.nombreApellidosRazonSocial,
                    Producto.numeroProducto,
                    Producto.tipoProducto
                )
                .join(Demandante, MedidaCautelar.demandante_id == Demandante.id)
                .join(Demandado, MedidaCautelar.demandado_id == Demandado.id)
                .join(Producto, MedidaCautelar.producto_id == Producto.id)
                .join(Documento, MedidaCautelar.documento_id == Documento.id)
                .filter(
                    MedidaCautelar.numeroCarteroWeb == cartero,
                    or_(
                        (tipo_embargo == "EMBARGO" and Demandado.numResolucionEmbargo.isnot(None)),
                        (tipo_embargo == "DESEMBARGO" and Demandado.numResolucionDesembargo.isnot(None))
                    )
                )
                .all()
            )

            # Formatear resultados
            return [
                {
                    "numeroCarteroWeb": r.numeroCarteroWeb,
                    "tipoEntidad": r.tipoEntidad,
                    "nombre": r.nombre,
                    "correoElectronico": r.correoElectronico,
                    "direccionFisica": r.direccionFisica,
                    "ciudadDepartamento": r.ciudadDepartamento,
                    "numeroOficio": r.numeroOficio,
                    "firmaOficio": r.firmaOficio,
                    "numResolucionEmbargo": r.numResolucionEmbargo,
                    "numResolucionDesembargo": r.numResolucionDesembargo,
                    "codDespachoJudicial": r.codDespachoJudicial,
                    "annoRadicadoJudicial": r.annoRadicadoJudicial,
                    "consAsignadoJudicial": r.consAsignadoJudicial,
                    "codInstanciaJudicial": r.codInstanciaJudicial,
                    "tipoMedida": r.tipoMedida,
                    "fechaRecepcion": r.fechaRecepcion,
                    "tipoIdentificacion": r.tipoIdentificacion,
                    "numeroIdentificacion": r.numeroIdentificacion,
                    "nombreApellidosRazonSocial": r.nombreApellidosRazonSocial,
                    "numeroProducto": r.numeroProducto,
                    "tipoProducto": r.tipoProducto,
                }
                for r in resultados
            ]

        except Exception as e:
            raise ValueError(f"Error al obtener medidas: {str(e)}")
