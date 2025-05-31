from flask import current_app
import logging
import os
import socket
import sys
from datetime import datetime

class LogService:
    hostname = socket.gethostname()

    logger = logging.getLogger("LogService")
    logger.setLevel(logging.INFO)

    @classmethod
    def initialize_logger(cls):
        if not cls.logger.handlers:
            # Forzar UTF-8 en la salida estándar y de errores
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')

            ruta_usuario = ''  # Se puede dejar vacío si `RutaBaseProyecto` ya es absoluta
            audit_log_path = ruta_usuario + current_app.config['GLOBALES']['RutaBaseProyecto'] + current_app.config['LOGS']['RutaLogAuditoria']
            error_log_path = ruta_usuario + current_app.config['GLOBALES']['RutaBaseProyecto'] + current_app.config['LOGS']['RutaLogSistema']

            # Crear directorios de logs si no existen
            os.makedirs(audit_log_path, exist_ok=True)
            os.makedirs(error_log_path, exist_ok=True)

            audit_log_path = os.path.join(audit_log_path, current_app.config['LOGS']['NombreLogAuditoria'])
            error_log_path = os.path.join(error_log_path, current_app.config['LOGS']['NombreLogSistema'])

            fmt = f"{cls.hostname};%(asctime)s;%(levelname)s - %(message)s"
            formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d;%H:%M:%S')

            # ✅ Audit log handler con UTF-8
            audit_handler = logging.FileHandler(audit_log_path, encoding='utf-8')
            audit_handler.setLevel(logging.DEBUG)
            audit_handler.setFormatter(formatter)
            cls.logger.addHandler(audit_handler)

            # ✅ Error log handler con UTF-8
            error_handler = logging.FileHandler(error_log_path, encoding='utf-8')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            cls.logger.addHandler(error_handler)

            # ✅ Agregar logs a la terminal (Consola) con UTF-8
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            cls.logger.addHandler(console_handler)

    @staticmethod
    def audit_log(message, task_name):
        formatted_message = f"{LogService.hostname};{task_name};{message}"
        LogService.logger.info(formatted_message)

    @staticmethod
    def error_log(message, task_name):
        formatted_message = f"{LogService.hostname};{task_name};{message}"
        LogService.logger.error(formatted_message)
