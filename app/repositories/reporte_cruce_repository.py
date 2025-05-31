import os
from app import db
from app.models.reporte_cruce import ReporteCruce
import pandas as pd
from app.utils.LogService import LogService

TASK_NAME = "reporte_cruce_repository.py"
class CruceRepository:
    @staticmethod
    def get_by_id(cruce_id):
        """Obtiene un registro de Cruce por su ID."""
        return db.session.get(ReporteCruce, cruce_id)

    @staticmethod
    def get_all():
        """Obtiene todos los registros de la tabla Cruce."""
        return ReporteCruce.query.all()

    @staticmethod
    def create(cruce_data):
        """Crea un nuevo registro de Cruce."""
        new_cruce = ReporteCruce(**cruce_data)
        db.session.add(new_cruce)
        db.session.commit()
        return new_cruce

    @staticmethod
    def update(cruce_id, update_data):
        """Actualiza un registro de Cruce por su ID."""
        cruce = db.session.get(ReporteCruce, cruce_id)
        if cruce:
            for key, value in update_data.items():
                setattr(cruce, key, value)
            db.session.commit()
        return cruce

    @staticmethod
    def delete(cruce_id):
        """Elimina un registro de Cruce por su ID."""
        cruce = db.session.get(ReporteCruce, cruce_id)
        if cruce:
            db.session.delete(cruce)
            db.session.commit()
        return cruce
    
    @staticmethod
    def get_by_num_radicado(num_radicado):
        """Retrieve all documents with the given estadoProceso."""
        return ReporteCruce.query.filter_by(numRadicado=num_radicado).first()
    
    @staticmethod
    def bulk_insert_from_excel(file_path) -> bool:
        """Lee un archivo XLSX y registra los datos en la base de datos."""
        try:
            df = pd.read_excel(file_path, dtype=str)  # Leer archivo Excel como texto
            
            # Reemplazar NaN con None (para evitar problemas con valores nulos)
            df = df.where(pd.notna(df), None)
            
            # Convertir los datos en objetos ReporteCruce
            registros = []
            for _, row in df.iterrows():
                try:
                    nuevo_reporte = ReporteCruce(
                        numRadicado=row['RADICADO'],
                        masivo=row['MASIVO'],
                        cantidadMedidas=row.get('CANTIDAD DE MEDIDAS', 0) or 0,
                        cantidadAnexos=row.get('CANTIDAD DE ANEXOS', 0) or 0,
                        corte=os.path.splitext(os.path.basename(file_path))[0].split("_", 1)[1] if "_" in os.path.basename(file_path) else '',
                        rutaArchivo=file_path,
                        cantidadPaginas=row.get('CANTIDAD DE PAGINAS', 0) or 0
                    )
                    LogService.audit_log(f"Registro creado: {nuevo_reporte}", TASK_NAME)
                    registros.append(nuevo_reporte)
                except ValueError as e:
                    print(f"Error de conversión en fila {row}: {e}")
                    LogService.error_log(f"Error de conversión en fila {row}: {e}", TASK_NAME)

            # Insertar en la base de datos en bloque
            if registros:
                db.session.bulk_save_objects(registros)
                db.session.commit()
                print(f"{len(registros)} registros insertados correctamente.")
                LogService.audit_log(f"{len(registros)} registros insertados correctamente.", TASK_NAME)
            else:
                print("No hay registros válidos para insertar.")
                LogService.audit_log("No hay registros válidos para insertar.", TASK_NAME)
            
            return True

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {file_path}")
            LogService.error_log(f"Error: No se encontró el archivo {file_path}", TASK_NAME)
            db.session.rollback()
            return False
        except Exception as e:
            print(f"Error inesperado: {e}")
            LogService.error_log(f"Error inesperado: {e}", TASK_NAME)
            db.session.rollback()
            return False
