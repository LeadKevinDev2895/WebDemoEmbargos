# orchestrator.py
import os
import shutil
from pathlib import Path
from shutil import copy2
from app.models.enums import EstadoProceso, TipoProcesamiento
from flask import current_app
import hashlib # Add to imports
from app.utils.LogService import LogService
from app.repositories.documento_repository import DocumentoRepository
from app.utils.funciones import unir_pdfs, es_pdf_valido

TASK_NAME = "FileOrchestrator"

class FileOrchestrator:
    def __init__(self, compressed_file_handler, file_publisher, database_handler):
        self.compressed_handler = compressed_file_handler
        self.file_publisher = file_publisher
        self.database_handler = database_handler

    def process_file_main(self, file_path, original_filename_param=None):
        # file_path is the path to the file already saved in RutaTemp by the Bot.
        # original_filename_param is the original name of the uploaded file.

        LogService.audit_log(f"Starting processing for file: {file_path}, Original filename hint: {original_filename_param}", TASK_NAME)

        file_set = {} # This will be populated by process_compressed

        self.compressed_handler.process_compressed(
            file_path,
            file_set=file_set,
            original_filename_for_single_file=original_filename_param # Pass it here
        )

        # Construct result_list from file_set, ensuring keys match DatabaseHandler expectations
        result_list = []
        for key_path, file_info in file_set.items(): # key_path is the actual path of the file processed (either the uploaded single file, or an extracted file)
            if not all(k in file_info for k in ["hash", "converted_path", "file_type", "user_facing_original_name", "actual_source_path_for_publishing"]):
                LogService.error_log(f"Skipping file_info for key {key_path} due to missing essential keys. Info: {file_info}", TASK_NAME)
                continue

            result_list.append({
                "user_facing_original_name": file_info["user_facing_original_name"],
                "actual_source_path_for_publishing": file_info["actual_source_path_for_publishing"],
                "hash": file_info["hash"],
                "converted_path": str(file_info["converted_path"]).replace('\\', '/'), # Ensure path is clean
                "file_type": file_info["file_type"]
            })

        if not result_list and file_set:
             LogService.error_log(f"No valid files to insert into DB from file_set for {file_path} (original: {original_filename_param}). File_set: {file_set}", TASK_NAME)
        elif not file_set:
             LogService.audit_log(f"No files were processed (file_set is empty) for {file_path} (original: {original_filename_param}). This might be normal if it was an empty archive or an unsupported single file type not processed by CompressedFileHandler.", TASK_NAME)


        self.database_handler.insert_document_data(result_list)
        return result_list # Return the list of processed data, useful for logging or potential future use.

    def unir_archivos_padre_hijos(self):
        """
        Orquesta la fusión de documentos PDF padre e hijo.
        """
        documentos_padre = DocumentoRepository.get_fathers_by_estado_proceso(EstadoProceso.DESGARGADO.value)

        for documento_padre in documentos_padre:
            documentos_hijos = DocumentoRepository.get_by_id_padre(documento_padre.id)

            # Separar PDFs y XLSX
            pdfs_hijos = []
            xlsx_hijos = []
            
            for doc in documentos_hijos:
                extension = Path(doc.rutaDocumentoConvertido).suffix.upper()
                if extension == '.PDF':
                    pdfs_hijos.append(doc.rutaDocumentoConvertido)
                elif extension == '.XLSX' or extension == '.XLS':
                    xlsx_hijos.append(doc)

            # Procesar PDFs
            lista_pdfs = [pdf for pdf in pdfs_hijos if es_pdf_valido(pdf)]

            if lista_pdfs:
                unir_pdfs(documento_padre.rutaDocumentoConvertido, lista_pdfs)

                # Actualizar los PDFs anexados
                for doc in documentos_hijos:
                    if Path(doc.rutaDocumentoConvertido).suffix.upper() == '.PDF':
                        DocumentoRepository.update(doc.id, {
                            "estadoProceso": EstadoProceso.ANEXADO.value,
                            "estadoOficio": "Archivo anexado al oficio exitosamente",
                            "tipoProcesamiento": TipoProcesamiento.ANEXO_PDF
                        })
            
            # Actualizar estado de los XLSX
            for xlsx_doc in xlsx_hijos:
                DocumentoRepository.update(xlsx_doc.id, {
                    "estadoProceso": EstadoProceso.PENDIENTE.value,
                })
            
            # Actualizar estado del padre
            DocumentoRepository.update(documento_padre.id, {
                "estadoProceso": EstadoProceso.PENDIENTE.value,
                "tipoProcesamiento": TipoProcesamiento.OFICIO
            })
        

    def remove_processing_files(self, pdf_path):
        """
        Orquesta la eliminación de archivos de procesamiento temporales.
        """
        from app.utils.funciones import eliminar_archivo
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        path_parts = pdf_path.split(os.sep)

        if 'PDFs' in path_parts:
            temp_index = path_parts.index('PDFs')
            path_parts[temp_index] = 'Extraccion'
            extraction_dir = os.sep.join(path_parts[:-1])
            path_parts[temp_index] = 'Procesamiento'
            processing_dir = os.sep.join(path_parts[:-1])

            for dir_path in [extraction_dir, processing_dir]:
                if os.path.exists(dir_path):
                    for file_name in os.listdir(dir_path):
                        if base_name in file_name:
                            eliminar_archivo(os.path.join(dir_path, file_name))
                            print(f"Archivo eliminado: {os.path.join(dir_path, file_name)}")
                            LogService.audit_log(f"Archivo eliminado: {os.path.join(dir_path, file_name)}", TASK_NAME)

    def backup_compressed_file(self, compressed_file_path):
        """
        Orquesta la copia de seguridad del archivo comprimido original.
        """
        base_dir = current_app.config['GLOBALES']['RutaBaseProyecto']
        backup_dir = os.path.join(base_dir, "Backup")
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
            print(f"Carpeta temporal eliminada: {backup_dir}")
        os.makedirs(backup_dir, exist_ok=True)

        to_backup = os.path.join(backup_dir, os.path.basename(compressed_file_path))
        copy2(compressed_file_path, to_backup)

    def stabilize_estado_proceso(self):
        """
        Orquesta la estabilización y el reprocesamiento de documentos 'Redocfly'.
        """
        DocumentoRepository.stabilize_estado_proceso()
        LogService.audit_log("Descartando Documentos Desconocidos", TASK_NAME)
        docs = DocumentoRepository.get_by_estado_proceso('Redocfly')

        for doc in docs:
            try:
                self.remove_processing_files(doc.rutaDocumentoConvertido)
                DocumentoRepository.update(doc.id, {"estadoProceso": "Reprocesamiento"})
            except Exception as e:
                LogService.error_log(f"Error al intentar eliminar archivos de extracción y procesamiento docfly: {e}", TASK_NAME)

        DocumentoRepository.reprocesar_documentos()
        LogService.audit_log("Actualizando Reprocesamiento...", TASK_NAME)
        DocumentoRepository.reprocesar_tipificaciones()
        LogService.audit_log("Actualizando Re-Tipificaciones...", TASK_NAME)