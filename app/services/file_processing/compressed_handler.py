# compressed_handler.py
import os
import zipfile
import tarfile
import shutil
import rarfile
import py7zr
from pathlib import Path
from flask import current_app
from app.utils.LogService import LogService
import hashlib

TASK_NAME = "CompressedFileHandler"

class CompressedFileHandler:
    def __init__(self, file_processor):
        self.file_processor = file_processor

    def ensure_valid_path(self, path):
        """Asegura que la ruta sea absoluta y maneja rutas largas en Windows."""
        path = os.path.abspath(path)
        if os.name == 'nt' and len(path) > 260:
            return f"\\\\?\\{path}"
        return path

    def extract_file(self, file_path, output_dir):
        """
        Extrae un archivo comprimido al directorio de salida especificado,
        manteniendo la estructura original.
        Soporta los formatos zip, rar, tar, tar.gz, tgz, tar.bz2, tar.xz y 7z.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            if zipfile.is_zipfile(file_path):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    for member in zip_ref.infolist():
                        fixed_member = member.filename.replace('\\', '/')
                        target_path = os.path.join(output_dir, fixed_member)
                        if member.is_dir() or fixed_member.endswith('/') or member.file_size == 0:
                            os.makedirs(target_path, exist_ok=True)
                            print(f"Carpeta creada: {target_path}")
                            LogService.audit_log(f"Carpeta creada: {target_path}", TASK_NAME)
                        else:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
                            print(f"Archivo extraído: {fixed_member} -> {target_path}")
                            LogService.audit_log(f"Archivo extraído: {fixed_member} -> {target_path}", TASK_NAME)

            elif rarfile.is_rarfile(file_path):
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    for member in rar_ref.infolist():
                        target_path = os.path.join(output_dir, member.filename)
                        if member.isdir() or member.filename.endswith('/'):
                            os.makedirs(target_path, exist_ok=True)
                            print(f"Carpeta creada: {target_path}")
                            LogService.audit_log(f"Carpeta creada: {target_path}", TASK_NAME)
                        else:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            rar_ref.extract(member, output_dir)
                            print(f"Archivo extraído: {member.filename} -> {target_path}")
                            LogService.audit_log(f"Archivo extraído: {member.filename} -> {target_path}", TASK_NAME)

            elif file_path.endswith(('.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tar.xz')):
                with tarfile.open(file_path, 'r:*') as tar_ref:
                    for member in tar_ref.getmembers():
                        target_path = os.path.join(output_dir, member.name)
                        if member.isdir():
                            os.makedirs(target_path, exist_ok=True)
                            print(f"Carpeta creada: {target_path}")
                            LogService.audit_log(f"Carpeta creada: {target_path}", TASK_NAME)
                        else:
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with tar_ref.extractfile(member) as source, open(target_path, 'wb') as target:
                                if source:
                                    shutil.copyfileobj(source, target)
                            print(f"Archivo extraído: {member.name} -> {target_path}")
                            LogService.audit_log(f"Archivo extraído: {member.name} -> {target_path}", TASK_NAME)

            elif file_path.endswith('.7z'):
                with py7zr.SevenZipFile(file_path, mode='r') as seven_z_ref:
                    seven_z_ref.extractall(output_dir)

                for root, dirs, files in os.walk(output_dir):
                    for dir_name in dirs:
                        print(f"Carpeta creada: {os.path.join(root, dir_name)}")
                        LogService.audit_log(f"Carpeta creada: {os.path.join(root, dir_name)}", TASK_NAME)
                    for file_name in files:
                        print(f"Archivo extraído: {os.path.join(root, file_name)}")
                        LogService.audit_log(f"Archivo extraído: {os.path.join(root, file_name)}", TASK_NAME)

            else:
                print("Formato no soportado o archivo no válido.")
                LogService.error_log("Formato no soportado o archivo no válido.", TASK_NAME)
                return False

            print(f"Archivo extraído en: {output_dir}")
            LogService.audit_log(f"Archivo extraído en: {output_dir}", TASK_NAME)
            return True

        except Exception as e:
            print(f"Error al extraer el archivo {file_path}: {e}")
            LogService.error_log(f"Error al extraer el archivo {file_path}: {e}", TASK_NAME)
            return False

    def calculate_hash(self, file_path):
        """Calcula el hash SHA-256 de un archivo."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error al calcular el hash para {file_path}: {e}")
            LogService.error_log(f"Error al calcular el hash para {file_path}: {e}", TASK_NAME)
            return None

    def process_compressed(self, file_path, extract_to=None, file_set=None):
        """
        Extrae archivos de un archivo comprimido y procesa cada archivo extraído.
        """
        file_path = self.ensure_valid_path(file_path)

        if extract_to is None:
            extract_to = Path(file_path).parent / Path(file_path).stem
        extract_to = self.ensure_valid_path(extract_to)

        if not os.path.exists(extract_to):
            os.makedirs(extract_to)

        if file_set is None:
            file_set = {}

        print(f"Extrayendo y procesando archivo comprimido: {file_path}")
        LogService.audit_log(f"Extrayendo y procesando archivo comprimido: {file_path}", TASK_NAME)
        try:
            self.extract_file(file_path, extract_to)
            LogService.audit_log(f"Archivo extraído: {file_path}", TASK_NAME)
        except Exception as e:
            print(f"Error al extraer el archivo {file_path}: {e}")
            LogService.error_log(f"Error al extraer el archivo {file_path}: {e}", TASK_NAME)
            return

        for root, dirs, files in os.walk(extract_to):
            for file in files:
                extracted_file_path = os.path.join(root, file)
                if extracted_file_path not in file_set:
                    file_hash = self.calculate_hash(extracted_file_path)
                    try:
                        converted_path, file_type = self.file_processor.process_file(extracted_file_path, file_set)
                        file_set[extracted_file_path] = {
                            "hash": file_hash,
                            "converted_path": str(converted_path) if converted_path else str(extracted_file_path),
                            "file_type": file_type
                        }
                    except Exception as e:
                        print(f"Error al procesar el archivo {extracted_file_path}: {e}")
                        LogService.error_log(f"Error al procesar el archivo {extracted_file_path}: {e}", TASK_NAME)