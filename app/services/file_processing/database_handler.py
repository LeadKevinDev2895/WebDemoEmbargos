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
            original_filename_for_check = str(Path(entry["original_filename_for_check"]))
            source_path_for_publishing = str(Path(entry["source_path_for_publishing"]))
            converted_path_from_processor = str(Path(entry["converted_path"]))
            file_hash = entry["hash"]
            file_type = entry["file_type"]

            LogService.audit_log(f"DB Handler: Processing entry for '{original_filename_for_check}'. Hash: {file_hash}", TASK_NAME)

            # Path for the converted document (e.g., the PDF version)
            final_ruta_convertido = self.file_publisher.copy_converted_file(converted_path_from_processor)

            # Path for the published original-form document
            final_ruta_publicado = None # Default to None

            # Duplicate checks
            hash_exists = DocumentoRepository.hash_exists(file_hash)

            # Use the filename part for the name check, as per original logic if DocumentoRepository.exists_by_nombre_archivo expects name without extension
            nombre_check_part = os.path.splitext(os.path.basename(original_filename_for_check))[0]
            name_exists_in_db = DocumentoRepository.exists_by_nombre_archivo(nombre_check_part) # This returns ID or None

            allow_duplicates_by_config = current_app.config['PARAMETROS']['InsertarDocumentosDuplicados']

            if not allow_duplicates_by_config:
                if hash_exists: # If content is the same, strictly skip.
                    LogService.audit_log(f"Skipping DB insert for '{original_filename_for_check}': Hash '{file_hash}' already exists.", TASK_NAME)
                    continue # Skip to the next entry in result_list
                # If hash doesn't exist, but name_exists_in_db is true, it's new content for an existing name. We will publish and insert.
                # If neither hash nor name exists, it's a new file. We will publish and insert.

            # If we reach here, it means either duplicates are allowed by config,
            # or they are not allowed AND the hash didn't exist.
            # In these cases, we attempt to publish the original-form file.
            LogService.audit_log(f"Attempting to publish original-form file for '{original_filename_for_check}'. Source: {source_path_for_publishing}", TASK_NAME)
            final_ruta_publicado = self.file_publisher.publish_file(source_path_for_publishing)
            if final_ruta_publicado:
                LogService.audit_log(f"Successfully published '{original_filename_for_check}' to '{final_ruta_publicado}'.", TASK_NAME)
            else:
                LogService.error_log(f"Failed to publish '{original_filename_for_check}'. 'rutaDocumento' will be NULL.", TASK_NAME)

            data_documento = {
                "rutaDocumentoConvertido": final_ruta_convertido,
                "rutaDocumento": final_ruta_publicado, # This will be None if publishing failed
                "hashDocumento": file_hash,
                "estadoOficio": "Pendiente", # Default status
                "estadoProceso": EstadoProceso.DESGARGADO.value, # Default status
                "tipoDocumento": file_type,
                "corte": calcular_corte()
                # NO "nombreOriginal" field
            }

            try:
                documento_creado = DocumentoRepository.create(data_documento)
                if documento_creado:
                    LogService.audit_log(f"Documento record created for '{original_filename_for_check}' with ID: {documento_creado.id}. Published: {final_ruta_publicado}, Converted: {final_ruta_convertido}", TASK_NAME)
                else: # Should not happen if create raises exception on failure
                    LogService.error_log(f"DocumentoRepository.create returned None for '{original_filename_for_check}'.", TASK_NAME)
            except Exception as e_create:
                LogService.error_log(f"Error creating Documento record for '{original_filename_for_check}': {e_create}. Data: {data_documento}", TASK_NAME)
                # If DB create fails, we might want to skip this entry or handle error. For now, loop continues.

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