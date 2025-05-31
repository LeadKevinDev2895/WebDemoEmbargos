# database_handler.py
import os
import shutil
from pathlib import Path
from app.models.enums import EstadoProceso, TipoDocumento, TipoProcesamiento
from app.repositories.reporte_cruce_repository import CruceRepository
from flask import current_app
from app.utils.LogService import LogService
from app.utils.funciones import create_or_get_pdf_directory, calcular_corte
from app.repositories.documento_repository import DocumentoRepository

TASK_NAME = "DatabaseHandler"

class DatabaseHandler:
    def __init__(self, file_publisher):
        self.file_publisher = file_publisher

    def insert_document_data(self, result_list):
        """
        Inserta metadatos de documentos en la base de datos, manejando duplicados y publicación.
        Solo publica el archivo la primera vez que se inserta.
        """
        print(f"Insertando documentos en la base de datos")
        print(f"Result list: {result_list}")
        for entry in result_list:
            user_facing_original_name = str(Path(entry["user_facing_original_name"]))
            actual_source_path = str(Path(entry["actual_source_path_for_publishing"]))
            converted_path = str(Path(entry["converted_path"]))
            file_hash = entry["hash"]
            file_type = entry["file_type"]

            print(f"Procesando entrada para la base de datos: {entry} (Original Name: {user_facing_original_name})")
            LogService.audit_log(f"Procesando entrada para la base de datos (Original Name: {user_facing_original_name}): {entry}", TASK_NAME)

            hash_exists = DocumentoRepository.hash_exists(file_hash)
            nombre_archivo = os.path.basename(user_facing_original_name).split('.')[0] # Use user-facing name for this check
            
            archivo_exists = DocumentoRepository.exists_by_nombre_archivo(nombre_archivo)
            print(f"Hash exist? {hash_exists}, Archivo (based on user_facing_original_name) exist? {archivo_exists}")

            LogService.audit_log(f"Validación de existencia del archivo '{user_facing_original_name}' en la base de datos (by name): {archivo_exists}", TASK_NAME)
            print(f"Validando existencia del hash en la base de datos: {file_hash} (for {user_facing_original_name})")
            LogService.audit_log(f"Validando existencia del hash '{file_hash}' en la base de datos (for {user_facing_original_name})", TASK_NAME)

            final_converted_path_location = self.file_publisher.copy_converted_file(converted_path)

            validate_hash_and_route = current_app.config['PARAMETROS']['InsertarDocumentosDuplicados']

            data_documento = {
                # "rutaDocumento": original_path, # Will be set based on publishing
                "rutaDocumentoConvertido": final_converted_path_location,
                "hashDocumento": file_hash,
                "estadoOficio": "Pendiente",
                "nombreOriginal": user_facing_original_name, # Assuming Documento model has this field
                "estadoProceso": EstadoProceso.DESGARGADO.value, # Or a new status like "CARGADO_USUARIO"? For now, DESGARGADO.
                "tipoDocumento": file_type,
                "corte": calcular_corte()
            }

            # Default rutaDocumento to the name the user gave it, in case it's not published.
            data_documento["rutaDocumento"] = user_facing_original_name

            if not validate_hash_and_route:
                if hash_exists and archivo_exists:
                    print(f"Documento con hash {file_hash} (nombre: {user_facing_original_name}) ya existe. No se insertará.")
                    LogService.audit_log(f"El archivo {user_facing_original_name} (hash: {file_hash}) ya existe. No se insertará.", TASK_NAME)
                    continue
                # elif hash_exists and archivo_exists is None: # This was commented out before
                #     print(f"Documento con hash {file_hash} ya existe. Se actualizará el estado.")
                #     LogService.audit_log(f"El archivo {nombre_archivo} ya existe. Se actualizará el estado.", TASK_NAME)
                #     data_documento["estadoProceso"] = "Documento Duplicado"
                #     data_documento["estadoOficio"] = "Documento no procesable por duplicidad"
                elif hash_exists is None and archivo_exists: # File name exists, but different content
                    LogService.audit_log(f"El archivo con nombre {user_facing_original_name} existe pero tiene hash diferente. Se publicará nueva versión.", TASK_NAME)
                    # Use actual_source_path for publishing
                    nueva_ruta_publicador = self.file_publisher.publish_file(actual_source_path)
                    if nueva_ruta_publicador:
                        data_documento["rutaDocumento"] = nueva_ruta_publicador
                else: # Neither hash nor name exists (truly new file)
                    LogService.audit_log(f"El archivo {user_facing_original_name} no existe previamente. Se publicará.", TASK_NAME)
                    # Use actual_source_path for publishing
                    nueva_ruta_publicador = self.file_publisher.publish_file(actual_source_path)
                    if nueva_ruta_publicador:
                        data_documento["rutaDocumento"] = nueva_ruta_publicador
            else: # If duplicate validation is off, always publish
                LogService.audit_log(f"Validación de duplicados desactivada. Publicando {user_facing_original_name}.", TASK_NAME)
                # Use actual_source_path for publishing
                nueva_ruta_publicador = self.file_publisher.publish_file(actual_source_path)
                if nueva_ruta_publicador:
                    data_documento["rutaDocumento"] = nueva_ruta_publicador

            try:
                documento_creado = DocumentoRepository.create(data_documento)
                if documento_creado:
                    print(f"Documento creado con ID: {documento_creado.id}")
                    LogService.audit_log(f"Documento creado con ID: {documento_creado.id}", TASK_NAME)
                else:
                    print("No se pudo crear el documento.")
                    LogService.error_log("No se pudo crear el documento.", TASK_NAME)
            except Exception as e:
                print(f"Error al crear el documento: {e}")
                LogService.error_log(f"Error al crear el documento: {e}", TASK_NAME)

        LogService.audit_log("Actualizando IDs de documentos relacionados.", TASK_NAME)
        print("Actualizando IDs de documentos relacionados.")
        import time
        time.sleep(2)
        asign_idParent = DocumentoRepository.update_parent_ids()
        LogService.audit_log(f"Resultado de actualización de IDs: {asign_idParent}", TASK_NAME)
        print(f"Resultado de actualización de IDs: {asign_idParent}")

    def report_process(self):
        try:
            LogService.audit_log("Procesando REPORTES.", TASK_NAME)
            # Obtener documentos con tipoDocumento = 'REPORTE'
            report_documents = DocumentoRepository.get_by_tipo_procesamiento(TipoProcesamiento.REPORTE)
            if not report_documents:
                LogService.audit_log("No se encontraron documentos REPORTE.", TASK_NAME)
                return

            for doc in report_documents:
                bulk_succesfull = CruceRepository.bulk_insert_from_excel(doc.rutaDocumentoConvertido)
                if bulk_succesfull:
                    DocumentoRepository.update(
                        doc.id,
                        {
                            "estadoOficio": "Archivo de cruce insertado",
                            "estadoProceso": EstadoProceso.EXITOSO.value
                        }
                    )
            LogService.audit_log(f"Reportes procesados.", TASK_NAME)
        except Exception as e:
            LogService.error_log(f"Error al procesar los reportes: {e}", TASK_NAME)

    def update_excel_processing_type(self):
        """
        Procesa los documentos EXCEL y actualiza su tipoProcesamiento.
        """
        try:
            LogService.audit_log("Actualizando tipoProcesamiento de documentos EXCEL.", TASK_NAME)
            # Obtener documentos con tipoDocumento = 'EXCEL'
            excel_documents = DocumentoRepository.get_by_tipo_documento(TipoDocumento.EXCEL)
            if not excel_documents:
                LogService.audit_log("No se encontraron documentos EXCEL.", TASK_NAME)
                return
                
            for doc in excel_documents:
                if 'OCR' in doc.rutaDocumentoConvertido:
                    DocumentoRepository.update_tipo_procesamiento(doc.id, TipoProcesamiento.REPORTE)
                    LogService.audit_log(f"TipoProcesamiento actualizado a REPORTE para {doc.id}.", TASK_NAME)
                    continue
                DocumentoRepository.update_tipo_procesamiento(doc.id, TipoProcesamiento.ANEXO_EXCEL)
            LogService.audit_log("Actualización de tipoProcesamiento de documentos EXCEL completada.", TASK_NAME)
                
        except Exception as e:
            LogService.error_log(f"Error al actualizar tipoProcesamiento: {e}", TASK_NAME)
            raise Exception(f"Error al actualizar tipoProcesamiento: {e}")