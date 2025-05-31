
from datetime import datetime, timedelta
from app import db
from app.models.documento import Documento
from app.models.enums import EstadoProceso, TipoDocumento
import app.utils
from sqlalchemy.sql import text, or_

class DocumentoRepository:
    """Repository layer for managing Documento database interactions."""

    @staticmethod
    def get_all():
        """Retrieve all records."""
        return Documento.query.all()
    
    @staticmethod
    def get_all_today():
        """
        Obtiene todos los documentos cuya fecha_actualizacion sea dentro del día actual.
        """
        fecha_hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_manana = fecha_hoy + timedelta(days=1)

        documentos = (
            db.session.query(Documento)
            .filter(Documento.fecha_actualizacion >= fecha_hoy)
            .filter(Documento.fecha_actualizacion < fecha_manana)
            .all()
        )
        return documentos

    @staticmethod
    def get_by_id(record_id):
        """Retrieve a record by its ID."""
        return Documento.query.get(record_id)

    @staticmethod
    def create(data):
        """Create a new record."""
        new_record = Documento(**data)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    @staticmethod
    def update(record_id, data):
        """Update an existing record by its ID."""
        record = Documento.query.get(record_id)
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        db.session.commit()
        return record

    @staticmethod
    def delete(record_id):
        """Delete a record by its ID."""
        record = Documento.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
    
    @staticmethod
    def get_by_estado_proceso(estado):
        """Retrieve all documents with the given estadoProceso."""
        return Documento.query.filter_by(estadoProceso=estado).all()
    
    @staticmethod
    def update_estadoOficio(documentos, data):
        """Update an existing record by its ID."""
        if not documentos:
            return None  # Retorna None si la lista está vacía

        for record in documentos:
            setattr(record, 'estadoOficio', f"{record.estadoOficio}|{data}")

        db.session.commit()
        
        return documentos  # Retorna la lista completa de documentos modificados

    @staticmethod
    def update_parent_ids():
        """
        Update the 'idPadre' field in the Documento table for child documents,
        assigning the 'id' of the parent document based on the file names.
        """
         # Verificar si la función existe
        check_query = text("""
        SELECT EXISTS (
            SELECT 1
            FROM pg_proc
            WHERE proname = 'actualizar_relaciones_documentos'
        );
        """)
        result = db.session.execute(check_query).scalar()

        # Si no existe, crear la función
        if not result:
            app.utils.funciones.create_update_parent_ids_function()
        try:
            query = text("SELECT actualizar_relaciones_documentos();")
            db.session.execute(query)
            db.session.commit()
            return "IdPadres asignados correctamente"
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error updating parent IDs: {e}")


    @staticmethod
    def reprocesar_tipificaciones():
        """
        Verifica y ejecuta el procedimiento almacenado 'reprocesar_documentos'.
        Si la función no existe, la crea antes de ejecutarla.
        """
        try:
            # Ejecutar el procedimiento 'reprocesar_documentos'
            query = text("SELECT reprocesar_tipificaciones();")
            db.session.execute(query)
            db.session.commit()
            return "✅ Documentos reprocesados correctamente."

        except Exception as e:
            db.session.rollback()
            raise Exception(f"❌ Error al reprocesar documentos: {e}")
    @staticmethod
    def reprocesar_documentos():
        """
        Verifica y ejecuta el procedimiento almacenado 'reprocesar_documentos'.
        Si la función no existe, la crea antes de ejecutarla.
        """
        try:
            # # Verificar si la función 'eliminar_relaciones_documento' existe
            # check_query_1 = text("""
            # SELECT EXISTS (
            #     SELECT 1
            #     FROM pg_proc
            #     WHERE proname = 'eliminar_relaciones_documento'
            # );
            # """)
            # exists_eliminar_relaciones = db.session.execute(check_query_1).scalar()

            # # Si no existe, crear la función
            # if not exists_eliminar_relaciones:
            #     app.utils.funciones.crear_procedimiento_eliminar_relaciones_documento()

            # # Verificar si la función 'reprocesar_documentos' existe
            # check_query_2 = text("""
            # SELECT EXISTS (
            #     SELECT 1
            #     FROM pg_proc
            #     WHERE proname = 'reprocesar_documentos'
            # );
            # """)
            # exists_reprocesar = db.session.execute(check_query_2).scalar()

            # # Si no existe, crear la función
            # if not exists_reprocesar:
            #     app.utils.funciones.crear_procedimiento_reprocesar_documentos()

            # Ejecutar el procedimiento 'reprocesar_documentos'
            query = text("SELECT reprocesar_documentos();")
            db.session.execute(query)
            db.session.commit()
            return "✅ Documentos reprocesados correctamente."

        except Exception as e:
            db.session.rollback()
            raise Exception(f"❌ Error al reprocesar documentos: {e}")

    @staticmethod
    def hash_exists(hash_value):
        """
        Check if a given hash value exists in the 'hashDocumento' field.
        
        :param hash_value: The hash value to check.
        :return: True if the hash value exists, False otherwise.
        """
        return db.session.query(Documento.query.filter_by(hashDocumento=hash_value).exists()).scalar()

    @staticmethod
    def obtener_vista_documentos():
        """
        Obtiene todos los documentos desde la vista 'vista_documentos'.
        """
        query = text("SELECT * FROM vista_documentos")
        result = db.session.execute(query)
        documentos = [dict(row._mapping) for row in result]  # Convierte a lista de diccionarios
        return documentos
    
    @staticmethod
    def ruta_exists(ruta_documento):
        """
        Verifica si una ruta de documento existe en el campo 'rutaDocumento'.
        """
        return db.session.query(
            db.session.query(Documento).filter_by(rutaDocumento=ruta_documento).exists()
        ).scalar()

    @staticmethod
    def get_by_tipo_documento(tipo_documento):
        """
        Obtiene todos los documentos con el tipoDocumento especificado y estadoProceso='Pendiente'.
        """
        return Documento.query.filter_by(tipoDocumento=tipo_documento, estadoProceso=EstadoProceso.DESGARGADO.value).all()

    @staticmethod
    def update_tipo_procesamiento(ids, tipo_procesamiento):
        """
        Actualiza el campo tipoProcesamiento para los documentos con los IDs proporcionados.
        """
        try:
            if not isinstance(ids, (list, tuple)):
                ids = [ids]

            updated_count = db.session.query(Documento).filter(
                Documento.id.in_(ids)
            ).update(
                {Documento.tipoProcesamiento: tipo_procesamiento},
                synchronize_session=False
            )

            db.session.commit()
            print(f"Se actualizaron {updated_count} registros con tipoProcesamiento='{tipo_procesamiento}'.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar tipoProcesamiento: {e}")
            raise Exception(f"Error al actualizar tipoProcesamiento: {e}")

    @staticmethod
    def get_by_tipo_procesamiento_null():
        """
        Obtiene todos los documentos cuyo tipoProcesamiento es NULL,
        cuyo tipoDocumento no es 'DESCONOCIDO' o también es NULL y el estadoProceso es 'Pendiente'.
        """
        try:
            documentos = (
                Documento.query.filter(
                    or_(
                        Documento.tipoProcesamiento.is_(None)
                    ),
                    or_(
                        Documento.tipoDocumento != "DESCONOCIDO",
                        Documento.tipoDocumento.is_(None)
                    ),
                    Documento.estadoProceso == EstadoProceso.DESGARGADO.value
                ).all()
            )
            print(f"Documentos encontrados: {len(documentos)}")
            return documentos
        except Exception as e:
            print(f"Error al ejecutar la consulta: {e}")
            return []

    @staticmethod
    def exists_by_nombre_archivo(nombre_archivo):
        """
        Verifica si un documento con el nombre del archivo especificado existe en la base de datos.
        Args:
            nombre_archivo (str): Nombre del archivo con extensión (ej: 'RCCI2210325058.PDF').

        Returns:
            int/None: ID del documento o None.
        """
        documento = (
            Documento.query
            .with_entities(Documento.id)
            .filter(Documento.rutaDocumento.ilike(f"%{nombre_archivo}%"))
            .first()
        )
        return documento.id if documento else None

    @staticmethod
    def get_fathers_by_estado_proceso(estado_proceso):
        """
        Obtiene todos los documentos padre con un estadoProceso específico.
        """
        return Documento.query.filter_by(estadoProceso=estado_proceso, idPadre=None).all()

    @staticmethod
    def get_by_tipo_procesamiento(tipo_procesamiento):
        """
        Obtiene todos los documentos con un tipoProcesamiento específico o en una lista de tipos,
        y cuyo estadoProceso sea 'PENDIENTE'.
        """
        if isinstance(tipo_procesamiento, list):
            return Documento.query.filter(
                Documento.tipoProcesamiento.in_(tipo_procesamiento),
                Documento.estadoProceso == EstadoProceso.DESGARGADO.value,
                Documento.idPadre.is_(None)
            ).all()
        else:
            return Documento.query.filter_by(
                tipoProcesamiento=tipo_procesamiento,
                estadoProceso=EstadoProceso.DESGARGADO.value,
                idPadre=None
            ).all()

    @staticmethod
    def get_by_id_padre(id_padre, estado=EstadoProceso.DESGARGADO.value):
        """
        Obtiene todos los documentos con un idPadre específico y proceso especifico
        'Pendiente' es el estado default.
        """
        return Documento.query.filter_by(idPadre=id_padre, estadoProceso=estado).all()
      
    @staticmethod
    def stabilize_estado_proceso():
        """Update estadoProceso to 'Procesado' for documents with tipoDocumento as 'DESCONOCIDO' in a single query."""
        Documento.query.filter_by(tipoDocumento=TipoDocumento.DESCONOCIDO).update(
            {Documento.estadoProceso: 'Procesado'}, synchronize_session=False
        )
        db.session.commit()