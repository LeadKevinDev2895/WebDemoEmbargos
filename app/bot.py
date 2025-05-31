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
