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
            return False, "No file or filename provided."

        original_filename = secure_filename(uploaded_file_object.filename)
        LogService.audit_log(f"Attempting unified upload for: {original_filename}", self.bot_name)

        temp_dir = None # Define temp_dir to ensure it's in scope for finally
        temp_save_path = None # Define temp_save_path for broader scope in finally

        try:
            with self.app.app_context(): # Ensure app context for config access
                temp_dir = current_app.config['GLOBALES']['RutaTemp']
                os.makedirs(temp_dir, exist_ok=True)

            temp_save_path = os.path.join(temp_dir, original_filename)

            LogService.audit_log(f"Attempting to save uploaded file to: {temp_save_path}", self.bot_name)
            uploaded_file_object.save(temp_save_path)

            # ---- START DIAGNOSTIC LOGS ----
            LogService.audit_log(f"File supposedly saved to: {temp_save_path}", self.bot_name)
            if os.path.exists(temp_save_path):
                LogService.audit_log(f"CONFIRMED by os.path.exists: File is present at {temp_save_path} immediately after save.", self.bot_name)
                # Optional: Check file size if useful
                try:
                    file_size = os.path.getsize(temp_save_path)
                    LogService.audit_log(f"CONFIRMED file size: {file_size} bytes at {temp_save_path}.", self.bot_name)
                    if file_size == 0:
                        LogService.error_log(f"WARNING: File at {temp_save_path} is 0 bytes after save!", self.bot_name)
                except OSError as e_size:
                    LogService.error_log(f"WARNING: Could not get size for file at {temp_save_path}: {e_size}", self.bot_name)

            else:
                LogService.error_log(f"CRITICAL ERROR: File DOES NOT exist at {temp_save_path} immediately after save operation!", self.bot_name)
                # Consider the implications if the save operation itself might raise an error that's caught by the outer try-except.
                # If save() fails and raises an IOError/OSError, it might be caught by the broader 'except Exception as e'.
                # This specific check is for cases where save() doesn't raise an error but the file is still not found.
                return False, f"Failed to save uploaded file to temporary path. Check logs for path: {temp_save_path}" # Early exit
            # ---- END DIAGNOSTIC LOGS ----

            file_orchestrator = self._get_file_orchestrator()

            # Assuming process_file_main will be adapted to handle original_filename
            # and internally pass it to where it's needed (CompressedFileHandler for single files).
            # For now, process_file_main might not use original_filename directly,
            # but CompressedFileHandler will need it.
            # The result_list from process_file_main is not directly used here for messaging,
            # as process_file_main's main job is orchestration and DB insertion.
            # We rely on logs for details and assume success if no exception.

            # process_file_main returns a result_list, but for messaging, we'll give a generic one for now,
            # or adapt process_file_main to return a (bool, message) pair.
            # For now, let's assume it raises exceptions on critical failure.
            file_orchestrator.process_file_main(temp_save_path, original_filename_param=original_filename)

            # If process_file_main completes without error, assume success for this high-level task.
            # Detailed per-file success/failure is handled within the orchestrator/DB handler.
            success_message = f"File '{original_filename}' received and processing initiated."
            LogService.audit_log(success_message, self.bot_name)
            return True, success_message

        except Exception as e:
            error_message = f"Error during unified upload processing for '{original_filename}': {str(e)}"
            LogService.error_log(error_message, self.bot_name)
            # Consider logging traceback.format_exc() for more detail in logs
            return False, error_message
        finally:
            # Clean up the temporarily saved file
            if temp_save_path and os.path.exists(temp_save_path):
                try:
                    os.remove(temp_save_path)
                    LogService.audit_log(f"Temporary file {temp_save_path} removed.", self.bot_name)
                except Exception as e_remove:
                    LogService.error_log(f"Error removing temporary file {temp_save_path}: {e_remove}", self.bot_name)

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
