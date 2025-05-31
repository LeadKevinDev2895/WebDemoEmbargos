import os
import time
from app.services.taxonomia import Taxonomia
from app.utils.LogService import LogService
from app.repositories.documento_repository import DocumentoRepository
from app.services import SeleniumBot
from app.services.email import EmailService
from app.services.file_processing.file_processor import FileProcessor
from app.services.file_processing.file_publisher import FilePublisher
from app.services.file_processing.compressed_handler import CompressedFileHandler
from app.services.file_processing.database_handler import DatabaseHandler
from app.services.file_processing.orchestrator import FileOrchestrator
import traceback
from flask import current_app
from werkzeug.utils import secure_filename


class Bot:
    def __init__(self, app):
        self.documento_repo = DocumentoRepository()
        self.taxonomia = Taxonomia(app)
        self.running = False
        self.app = app  # Pasamos la aplicación Flask

        with self.app.app_context():  # Inicia el contexto de la aplicación
            # Se instancia servicio de email
            self.bot_name = current_app.config['GLOBALES']['NombreProyecto']
            self.folder_main = current_app.config['GLOBALES']['RutaBaseProyecto']
            os.makedirs(self.folder_main, exist_ok=True)
            self.smtp_server = current_app.config['NOTIFICACIONES']['SMTPServer']
            self.smtp_port = current_app.config['NOTIFICACIONES']['SMTPPort']
            self.sender_email = current_app.config['NOTIFICACIONES']['EmailRemitente']
            self.to_emails = current_app.config['NOTIFICACIONES']['EmailDestinatarios']
            self.email_password = current_app.config['EMAIL_PASSWORD']
            self.folder_taxonomy = current_app.config["GLOBALES"]["RutaSalidaArchivos"]
            self.email_service = EmailService(self.smtp_server, self.smtp_port, self.sender_email,
                                              self.email_password, self.to_emails, self.bot_name)

    def _get_file_orchestrator(self):
        # Ensures that instances are created within the app context if they need config
        with self.app.app_context():
            file_processor_instance = FileProcessor()
            file_publisher_instance = FilePublisher() # FilePublisher uses current_app.config
            compressed_file_handler_instance = CompressedFileHandler(file_processor_instance)
            database_handler_instance = DatabaseHandler(file_publisher_instance) # DatabaseHandler uses current_app.config
            file_orchestrator = FileOrchestrator(compressed_file_handler_instance,
                                                 file_publisher_instance,
                                                 database_handler_instance)
        return file_orchestrator

    def run_download_files(self):
        with self.app.app_context():  # Inicia el contexto de la aplicación
            print("Bot Descarga Archivos está ejecutándose...")
            url = current_app.config['WEBSCRAPING']['UrlBase']
            username = current_app.config['WEBCREDENTIALS']['USERNAME']
            password = current_app.config['WEBCREDENTIALS']['PASSWORD']

            try:
                self.selenium_bot = None
                with self.app.app_context():
                    self.ruta_download = self.app.config['WEBSCRAPING']['RutaDescarga']
                    self.selenium_bot = SeleniumBot(self.ruta_download)  # Ruta para descargas

                file_download = self.selenium_bot.download_file(url, username, password)
                # file_download = '/home/kevin-orduz/Descargas/Davivienda/prueba-18032025.zip'
                if file_download is None:
                    raise Exception("No se pudo descargar el archivo")
                
                # Instanciamiento de la clase
                file_processor = FileProcessor()
                file_publisher = FilePublisher()
                compressed_file_handler = CompressedFileHandler(file_processor)
                database_handler = DatabaseHandler(file_publisher)
                file_orchestrator = FileOrchestrator(compressed_file_handler, file_publisher, database_handler)
                file_orchestrator.process_file_main(file_download)
                
                # Se actualiza el estado de los documentos EXCEL y se publican los reportes
                database_handler.update_excel_processing_type()
                database_handler.report_process()
                file_orchestrator.stabilize_estado_proceso()
                
                # Se unen archivos hijos a archivos padre
                file_orchestrator.unir_archivos_padre_hijos()

                time.sleep(2)

                self.selenium_bot = None
                with self.app.app_context():
                    self.ruta_download = self.app.config['WEBSCRAPING']['RutaDescarga']
                    self.selenium_bot = SeleniumBot(self.ruta_download)  # Ruta para descargas

                delete_files = self.selenium_bot.delete_files(url, username, password)
                if not delete_files:
                    LogService.audit_log("No se pudo eliminar los archivos", "Bot.py")

                # Se envia notificacion de finalizacion
                self.email_service.notify_execution_end()
                return "Bot Descarga Archivos executed successfully!"

            except Exception as e:
                print(f"Error en el bot: {e}")
                # Captura el traceback completo
                error_trace = traceback.format_exc()

                # Registra el error en logs (si usas logging, puedes integrarlo aquí)
                print("Traceback completo del error:")
                print(error_trace)

                # Levanta una nueva excepción con más detalles
                raise Exception(f"Error el funcionamiento del BOT: {e}\nTraceback: {error_trace}")

    def run_unified_upload_processing(self, uploaded_file_object):
        if not uploaded_file_object or not uploaded_file_object.filename:
            LogService.error_log("Invalid file object or filename received for upload.", self.bot_name)
            return False, "No file or filename provided.", "error" # Return category

        original_filename = secure_filename(uploaded_file_object.filename)
        LogService.audit_log(f"Attempting unified upload for: {original_filename}", self.bot_name)

        temp_dir = None
        temp_save_path = None

        # Default return values
        overall_success = False
        message_for_ui = f"An error occurred while processing '{original_filename}'."
        ui_category = "error"

        try:
            with self.app.app_context(): # Ensure app context for config access
                temp_dir = current_app.config['GLOBALES']['RutaTemp']
                os.makedirs(temp_dir, exist_ok=True)

            temp_save_path = os.path.join(temp_dir, original_filename)

            LogService.audit_log(f"Attempting to save uploaded file to: {temp_save_path}", self.bot_name)
            uploaded_file_object.save(temp_save_path)

            LogService.audit_log(f"File supposedly saved to: {temp_save_path}", self.bot_name)
            if not os.path.exists(temp_save_path):
                LogService.error_log(f"CRITICAL ERROR: File DOES NOT exist at {temp_save_path} immediately after save operation!", self.bot_name)
                return False, f"Failed to save uploaded file to temporary path: {temp_save_path}", "error"

            # (Optional: file size check logs can remain if desired)
            try:
                file_size = os.path.getsize(temp_save_path)
                LogService.audit_log(f"CONFIRMED file size: {file_size} bytes at {temp_save_path}.", self.bot_name)
                if file_size == 0:
                    LogService.error_log(f"WARNING: File at {temp_save_path} is 0 bytes after save!", self.bot_name)
                    # Potentially return error here too if 0 byte files are invalid
                    # return False, f"Uploaded file '{original_filename}' is empty (0 bytes).", "error"
            except OSError as e_size:
                LogService.error_log(f"WARNING: Could not get size for file at {temp_save_path}: {e_size}", self.bot_name)


            file_orchestrator = self._get_file_orchestrator()

            # process_file_main now returns a list of status objects
            # [{'filename': ..., 'status': ..., 'message_detail': ...}, ...]
            processed_results = file_orchestrator.process_file_main(temp_save_path, original_filename_param=original_filename)

            if not processed_results: # If process_file_main returned empty or None (e.g. error before processing any file info)
                LogService.error_log(f"No processing results returned from FileOrchestrator for '{original_filename}'.", self.bot_name)
                message_for_ui = f"Processing failed to return any results for '{original_filename}'."
                ui_category = "error"
                # overall_success remains False
            elif len(processed_results) == 1: # Single file upload scenario (or archive with one file)
                result = processed_results[0]
                fn = result.get('filename', original_filename) # Fallback to original_filename
                status = result.get('status')
                detail = result.get('message_detail', '')

                if status == 'duplicate_true':
                    message_for_ui = f"File '{fn}' has already been processed. Current DB status: '{detail}'."
                    ui_category = 'warning'
                    overall_success = True # Operation completed, duplicate found
                elif status == 'reprocessing_triggered':
                    message_for_ui = f"File '{fn}' was updated with new content and set for Reprocessing."
                    ui_category = 'info' # Using 'info' for this distinct state
                    overall_success = True # Operation completed, reprocessing triggered
                elif status in ['processed_new', 'processed_new_duplicates_allowed']:
                    message_for_ui = f"File '{fn}' processed successfully. {detail if 'DB ID' in detail else ''}".strip()
                    ui_category = 'success'
                    overall_success = True
                else: # Includes 'error' status from DatabaseHandler or other unknown status
                    message_for_ui = f"Error processing file '{fn}': {detail}"
                    ui_category = 'error'
                    overall_success = False
            else: # Archive with multiple files
                # Summarize for multiple files
                success_count = sum(1 for r in processed_results if r.get('status') in ['processed_new', 'processed_new_duplicates_allowed'])
                duplicate_count = sum(1 for r in processed_results if r.get('status') == 'duplicate_true')
                reprocessing_count = sum(1 for r in processed_results if r.get('status') == 'reprocessing_triggered')
                error_count = len(processed_results) - success_count - duplicate_count - reprocessing_count

                message_for_ui = f"Archive '{original_filename}' processed. Total: {len(processed_results)} files. " \
                                 f"Successful: {success_count}, Duplicates: {duplicate_count}, Reprocessing: {reprocessing_count}, Errors: {error_count}."
                if error_count > 0 or reprocessing_count > 0 or duplicate_count > 0 :
                    ui_category = 'warning' # Use warning if any non-standard success
                else:
                    ui_category = 'success'
                overall_success = True # Batch operation itself completed

            # --- Add post-processing calls ---
            if overall_success: # Only run these if the main processing part seemed to complete
                LogService.audit_log("Executing post-upload global processing steps.", self.bot_name)
                try:
                    database_handler = file_orchestrator.database_handler
                    database_handler.update_excel_processing_type()
                    database_handler.report_process()
                    file_orchestrator.stabilize_estado_proceso()
                    LogService.audit_log("Post-upload global processing steps completed.", self.bot_name)
                except Exception as e_post_proc:
                    LogService.error_log(f"Error during post-upload global processing steps: {e_post_proc}", self.bot_name)
                    # Optionally append to message_for_ui or change status if these are critical
                    # For now, just log. The main file operation status is already set.

        except Exception as e:
            # This catches errors from file save, _get_file_orchestrator, or if process_file_main itself raises an unhandled one
            message_for_ui = f"Critical error during unified upload processing for '{original_filename}': {str(e)}"
            LogService.error_log(message_for_ui + f" Traceback: {traceback.format_exc()}", self.bot_name) # Add traceback
            ui_category = "error"
            overall_success = False
        finally:
            if temp_save_path and os.path.exists(temp_save_path):
                try:
                    os.remove(temp_save_path)
                    LogService.audit_log(f"Temporary file {temp_save_path} removed.", self.bot_name)
                except Exception as e_remove:
                    LogService.error_log(f"Error removing temporary file {temp_save_path}: {e_remove}", self.bot_name)

        # ---- ADD DIAGNOSTIC LOG HERE ----
        LogService.audit_log(f"BOT: About to return from run_unified_upload_processing. Success: {overall_success}, UI_Msg: '{message_for_ui}', UI_Cat: '{ui_category}'", self.bot_name)

        return overall_success, message_for_ui, ui_category

    def run_taxonomia(self):
        with self.app.app_context():  # Inicia el contexto de la aplicación
            print("Bot Taxonomia está ejecutándose...")
            url = current_app.config['WEBSCRAPING']['UrlBase']
            username = current_app.config['WEBCREDENTIALS']['USERNAME']
            password = current_app.config['WEBCREDENTIALS']['PASSWORD']

            try:

                print("-------------------Taxonomia----------------------")
                compressed_files = self.taxonomia.trasladar_archivos()
                if compressed_files is None:
                    LogService.audit_log(f"No hay carpeta comprimida de la taxonomia para subir a Davibox", "Bot.py")
                    return "No se encontro carpeta comprimida de la taxonomia para subir a Davibox"
                LogService.audit_log(f"Archvos comprimidos: {compressed_files}", "Bot.py")
                print("-------------------Carga de archivos Davibox----------------------")
                self.selenium_bot = None
                with self.app.app_context():
                    self.ruta_download = self.app.config['WEBSCRAPING']['RutaDescarga']
                    self.selenium_bot = SeleniumBot(self.ruta_download)
                self.selenium_bot.upload_files(url, username, password, compressed_files)

                # Se envia notificacion de finalizacion
                self.email_service.notify_execution_end()
                return "Bot Taxonomia executed successfully!"

            except Exception as e:
                print(f"Error en el bot: {e}")
                # Captura el traceback completo
                error_trace = traceback.format_exc()

                # Registra el error en logs (si usas logging, puedes integrarlo aquí)
                print("Traceback completo del error:")
                print(error_trace)

                # Levanta una nueva excepción con más detalles
                raise Exception(f"Error el funcionamiento del BOT: {e}\nTraceback: {error_trace}")
    
    def run_upload_files(self, nombre_taxonomia):
        try:
            with self.app.app_context(): 
                url = current_app.config['WEBSCRAPING']['UrlBase']
                username = current_app.config['WEBCREDENTIALS']['USERNAME']
                password = current_app.config['WEBCREDENTIALS']['PASSWORD']
                #Se arma la ruta completa de la carpeta comprimida
                compressed_files = os.path.abspath(os.path.join(self.folder_taxonomy,f"{nombre_taxonomia}.zip"))
                if not os.path.exists(compressed_files):
                    LogService.audit_log(f"El Nombre del archivo {nombre_taxonomia} o la ruta {compressed_files} no es valido", "Bot.py")
                    return f"El Nombre del archivo {nombre_taxonomia} o la ruta {compressed_files} no es valido"
                print("-------------------Carga de archivos Davibox----------------------")
                self.selenium_bot = None
                with self.app.app_context():
                    print("Bot Cargue de la taxonomia esta ejecutandose...")
                    self.ruta_download = self.app.config['WEBSCRAPING']['RutaDescarga']
                    self.selenium_bot = SeleniumBot(self.ruta_download)
                self.selenium_bot.upload_files(url, username, password, compressed_files)
                self.email_service.notify_execution_end()
                return "Bot Cargue de la taxonomia executed successfully!"
        except Exception as e:
                print(f"Error en el bot: {e}")
                # Captura el traceback completo
                error_trace = traceback.format_exc()

                # Registra el error en logs (si usas logging, puedes integrarlo aquí)
                print("Traceback completo del error:")
                print(error_trace)

                # Levanta una nueva excepción con más detalles
                raise Exception(f"Error el funcionamiento del BOT: {e}\nTraceback: {error_trace}")
