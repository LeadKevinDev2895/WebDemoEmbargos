# file_publisher.py
import os
import shutil
from pathlib import Path
from flask import current_app
from app.utils.LogService import LogService
from app.utils.funciones import create_or_get_pdf_directory
from app.services.publicador_archivos import LocalBucketTransfer
from app.repositories.documento_repository import DocumentoRepository

TASK_NAME = "FilePublisher"

class FilePublisher:
    def __init__(self):
        self.dir_publicador = current_app.config['GLOBALES']['RutaPublicador']
        self.bucket = LocalBucketTransfer(self.dir_publicador)

    def publish_file(self, original_path):
        """
        Publica un archivo en el directorio designado si no es un duplicado.
        Devuelve la nueva ruta en el directorio del publicador si tiene éxito, None en caso contrario.
        """
        estado_transfer, nueva_ruta_publicador = self.bucket.transfer_file(original_path)
        print(f"Estado transfer: {estado_transfer}, Nueva ruta publicador: {nueva_ruta_publicador}")
        LogService.audit_log(f"Estado transfer: {estado_transfer}, Nueva ruta publicador: {nueva_ruta_publicador}", TASK_NAME)

        if estado_transfer:
            return nueva_ruta_publicador
        else:
            print(f"Error al transferir el archivo {original_path} a {nueva_ruta_publicador}, debe transferirse manualmente.")
            LogService.error_log(f"Error al transferir el archivo {original_path} a {nueva_ruta_publicador}, debe transferirse manualmente.", TASK_NAME)
            # Alerta a area tecnica
            return None

    def copy_converted_file(self, converted_path):
        """
        Copia el archivo convertido al directorio de PDFs.
        Devuelve la ruta del archivo copiado.
        """
        pdfs_dir = create_or_get_pdf_directory(converted_path)
        copied_path = shutil.copy(converted_path, pdfs_dir)
        return copied_path