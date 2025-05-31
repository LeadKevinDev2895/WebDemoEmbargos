# database_handler.py
import os
import shutil
from pathlib import Path
from app.models.enums import EstadoProceso, TipoDocumento, TipoProcesamiento
from app.repositories.reporte_cruce_repository import CruceRepository
from flask import current_app
from app.utils.LogService import LogService
from app.utils.funciones import calcular_corte # create_or_get_pdf_directory might not be needed here directly
from app.repositories.documento_repository import DocumentoRepository
from datetime import datetime # Ensure this is imported

TASK_NAME = "DatabaseHandler"

class DatabaseHandler:
    def __init__(self, file_publisher):
        self.file_publisher = file_publisher

    def insert_document_data(self, result_list):
        LogService.audit_log(f"DB Handler: Starting insert_document_data for {len(result_list)} items.", TASK_NAME)
        processed_results_for_bot = []

        for entry in result_list:
            original_filename_for_check = str(Path(entry["original_filename_for_check"]))
            source_path_for_publishing = str(Path(entry["source_path_for_publishing"]))
            converted_path_from_processor = str(Path(entry["converted_path"]))
            file_hash = entry["hash"]
            file_type = entry["file_type"]

            current_file_result = {
                'filename': original_filename_for_check,
                'status': 'error', # Default status
                'message_detail': 'Unknown processing error during DB handling.'
            }
            LogService.audit_log(f"DB Handler: Processing entry for '{original_filename_for_check}'. Hash: {file_hash}", TASK_NAME)

            # Path for the converted document (e.g., the PDF version)
            # This copy happens regardless of duplication, as the converted file might be new even if content is old.
            # However, if we skip DB insert, this might be an orphan. Consider if this copy should be conditional.
            # For now, let's assume it's always copied, and cleanup of orphans is a separate concern or happens if temp dirs are managed.
            final_ruta_convertido = self.file_publisher.copy_converted_file(converted_path_from_processor)
            LogService.audit_log(f"DB Handler: Converted file copied to '{final_ruta_convertido}' for '{original_filename_for_check}'.", TASK_NAME)

            # Duplicate checks
            existing_doc_by_hash = DocumentoRepository.get_by_hash(file_hash)
            nombre_check_part = os.path.splitext(os.path.basename(original_filename_for_check))[0]
            existing_doc_id_by_name = DocumentoRepository.exists_by_nombre_archivo(nombre_check_part) # Returns ID or None

            allow_duplicates_by_config = current_app.config['PARAMETROS']['InsertarDocumentosDuplicados']
            final_ruta_publicado = None # Initialize

            LogService.audit_log(f"DB Handler: Checks for '{original_filename_for_check}': hash_exists={bool(existing_doc_by_hash)}, name_id_exists={existing_doc_id_by_name}, allow_duplicates_config={allow_duplicates_by_config}", TASK_NAME)

            operation_performed = False # Flag to track if any DB write operation (create/update) happens

            if not allow_duplicates_by_config:
                if existing_doc_by_hash:
                    # True Duplicate (Content Exists)
                    LogService.audit_log(f"DB Handler: True duplicate (hash exists) for '{original_filename_for_check}'. Current status: {existing_doc_by_hash.estadoProceso}.", TASK_NAME)
                    current_file_result['status'] = 'duplicate_true'
                    current_file_result['message_detail'] = existing_doc_by_hash.estadoProceso
                    # No DB write, loop to next entry
                elif existing_doc_id_by_name:
                    # Name Duplicate, New Content (Reprocessing Case)
                    LogService.audit_log(f"DB Handler: Name duplicate, new content for '{original_filename_for_check}'. Updating for reprocessing (ID: {existing_doc_id_by_name}).", TASK_NAME)
                    final_ruta_publicado = self.file_publisher.publish_file(source_path_for_publishing)
                    if final_ruta_publicado is None:
                         LogService.error_log(f"DB Handler: Publish failed for reprocessing '{original_filename_for_check}'. rutaDocumento will be None.", TASK_NAME)

                    data_to_update = {
                        "hashDocumento": file_hash,
                        "rutaDocumento": final_ruta_publicado,
                        "rutaDocumentoConvertido": final_ruta_convertido,
                        "estadoProceso": "Reprocesamiento", # Target state for SP
                        "fecha_actualizacion": datetime.now(), # Update timestamp
                        "tipoDocumento": file_type, # Potentially update type if it changed
                        "corte": calcular_corte() # Update corte
                        # estadoOficio might also need reset/update here
                    }
                    try:
                        DocumentoRepository.update(existing_doc_id_by_name, data_to_update)
                        current_file_result['status'] = 'reprocessing_triggered'
                        current_file_result['message_detail'] = "Updated with new content and set for Reprocessing."
                        operation_performed = True
                    except Exception as e_update:
                        LogService.error_log(f"DB Handler: Error updating document ID {existing_doc_id_by_name} for reprocessing: {e_update}", TASK_NAME)
                        current_file_result['message_detail'] = f"Error updating for reprocessing: {str(e_update)}"
                else:
                    # New File (Duplicate Validation ON, but no duplicate found)
                    LogService.audit_log(f"DB Handler: New file '{original_filename_for_check}'. Processing normally.", TASK_NAME)
                    final_ruta_publicado = self.file_publisher.publish_file(source_path_for_publishing)
                    if final_ruta_publicado is None:
                         LogService.error_log(f"DB Handler: Publish failed for new file '{original_filename_for_check}'. rutaDocumento will be None.", TASK_NAME)

                    data_to_create = {
                        "rutaDocumento": final_ruta_publicado,
                        "rutaDocumentoConvertido": final_ruta_convertido,
                        "hashDocumento": file_hash,
                        "estadoOficio": "Pendiente",
                        "estadoProceso": EstadoProceso.DESGARGADO.value,
                        "tipoDocumento": file_type,
                        "corte": calcular_corte()
                    }
                    try:
                        created_doc = DocumentoRepository.create(data_to_create)
                        current_file_result['status'] = 'processed_new'
                        current_file_result['message_detail'] = f"Processed successfully. DB ID: {created_doc.id if created_doc else 'N/A'}"
                        operation_performed = True
                    except Exception as e_create:
                        LogService.error_log(f"DB Handler: Error creating new document for '{original_filename_for_check}': {e_create}", TASK_NAME)
                        current_file_result['message_detail'] = f"Error creating new record: {str(e_create)}"
            else:
                # Duplicates Allowed by Config
                LogService.audit_log(f"DB Handler: Duplicate validation disabled. Processing '{original_filename_for_check}' as new.", TASK_NAME)
                final_ruta_publicado = self.file_publisher.publish_file(source_path_for_publishing)
                if final_ruta_publicado is None:
                    LogService.error_log(f"DB Handler: Publish failed (duplicates allowed) for '{original_filename_for_check}'. rutaDocumento will be None.", TASK_NAME)

                data_to_create = {
                    "rutaDocumento": final_ruta_publicado,
                    "rutaDocumentoConvertido": final_ruta_convertido,
                    "hashDocumento": file_hash,
                    "estadoOficio": "Pendiente",
                    "estadoProceso": EstadoProceso.DESGARGADO.value,
                    "tipoDocumento": file_type,
                    "corte": calcular_corte()
                }
                try:
                    created_doc = DocumentoRepository.create(data_to_create)
                    current_file_result['status'] = 'processed_new_duplicates_allowed'
                    current_file_result['message_detail'] = f"Processed successfully (duplicates allowed). DB ID: {created_doc.id if created_doc else 'N/A'}"
                    operation_performed = True
                except Exception as e_create_dup:
                    LogService.error_log(f"DB Handler: Error creating new document (duplicates allowed) for '{original_filename_for_check}': {e_create_dup}", TASK_NAME)
                    current_file_result['message_detail'] = f"Error creating new record (duplicates allowed): {str(e_create_dup)}"

            processed_results_for_bot.append(current_file_result)

        # End of loop
        if any(res['status'] not in ['duplicate_true', 'error'] for res in processed_results_for_bot): # If any actual DB write happened
            LogService.audit_log("DB Handler: Calling update_parent_ids after processing batch.", TASK_NAME)
            try:
                DocumentoRepository.update_parent_ids()
            except Exception as e_parent_ids:
                LogService.error_log(f"DB Handler: Error in update_parent_ids: {e_parent_ids}", TASK_NAME)

        LogService.audit_log(f"DB Handler: Finished insert_document_data. Results: {processed_results_for_bot}", TASK_NAME)
        return processed_results_for_bot

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