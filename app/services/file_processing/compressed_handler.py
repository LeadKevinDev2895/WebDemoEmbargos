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

    def process_compressed(self, file_path, extract_to=None, file_set=None, original_filename_for_single_file=None):
        file_path_abs = self.ensure_valid_path(file_path) # Ensure path is absolute and handles long paths

        if file_set is None:
            file_set = {}

        is_archive = False
        try:
            if zipfile.is_zipfile(file_path_abs):
                is_archive = True
            elif rarfile.is_rarfile(file_path_abs):
                is_archive = True
            elif tarfile.is_tarfile(file_path_abs): # This checks for .tar, .tar.gz, .tar.bz2 etc.
                is_archive = True
            elif file_path_abs.lower().endswith('.7z'): # py7zr doesn't have a simple is_7zfile
                # Basic check, could be more robust by trying to open with py7zr
                try:
                    with py7zr.SevenZipFile(file_path_abs, mode='r') as _:
                        is_archive = True
                except py7zr.exceptions.Bad7zFile:
                    is_archive = False # Not a valid 7z file
                except Exception: # Other errors during check
                    is_archive = False
        except Exception as e_check:
            LogService.error_log(f"Error during archive type check for {file_path_abs}: {e_check}", TASK_NAME)
            is_archive = False # Assume not an archive if check fails

        if is_archive:
            LogService.audit_log(f"Processing as ARCHIVE: {file_path_abs}", TASK_NAME)
            if extract_to is None:
                # Default extraction path: subdirectory named after the archive file (without extension)
                extract_to = Path(file_path_abs).parent / Path(file_path_abs).stem
            extract_to_abs = self.ensure_valid_path(str(extract_to))

            if not os.path.exists(extract_to_abs):
                os.makedirs(extract_to_abs)

            try:
                extraction_success = self.extract_file(file_path_abs, extract_to_abs) # extract_file is an existing method
                if not extraction_success:
                    LogService.error_log(f"Extraction failed for archive {file_path_abs}. Cannot process contents.", TASK_NAME)
                    return # Stop if extraction fails
            except Exception as e_extract:
                LogService.error_log(f"Exception during extraction of {file_path_abs}: {e_extract}", TASK_NAME)
                return

            # Process extracted files
            for root, dirs, files in os.walk(extract_to_abs):
                for file_in_archive in files:
                    extracted_file_full_path = os.path.join(root, file_in_archive)
                    # Use relative path within archive as user_facing_original_name
                    # This requires making extracted_file_full_path relative to extract_to_abs
                    relative_path_in_archive = os.path.relpath(extracted_file_full_path, extract_to_abs)

                    if extracted_file_full_path not in file_set: # Avoid reprocessing if somehow already there
                        file_hash = self.calculate_hash(extracted_file_full_path)
                        if not file_hash:
                            LogService.error_log(f"Could not calculate hash for extracted file {extracted_file_full_path}. Skipping.", TASK_NAME)
                            continue
                        try:
                            # file_set is passed for FileProcessor internal state if it ever needs it, currently not used by it.
                            converted_path, file_type = self.file_processor.process_file(extracted_file_full_path, file_set)

                            file_set[extracted_file_full_path] = { # Key is the actual path of the extracted file
                                "hash": file_hash,
                                "converted_path": str(converted_path) if converted_path else str(extracted_file_full_path),
                                "file_type": file_type,
                                "original_filename_for_check": relative_path_in_archive.replace('\\', '/'), # Key changed
                                "source_path_for_publishing": extracted_file_full_path  # Key changed
                            }
                        except Exception as e_proc:
                            LogService.error_log(f"Error processing extracted file {extracted_file_full_path}: {e_proc}", TASK_NAME)

            # Optional: Clean up extract_to_abs directory if it's temporary and all files are copied/processed.
            # Current logic keeps it. If it needs cleanup, shutil.rmtree(extract_to_abs) could be added.

        else: # Process as a SINGLE FILE
            LogService.audit_log(f"Processing as SINGLE FILE: {file_path_abs}", TASK_NAME)
            file_hash = self.calculate_hash(file_path_abs)
            if not file_hash:
                LogService.error_log(f"Could not calculate hash for single file {file_path_abs}. Skipping.", TASK_NAME)
                return # Stop if hash fails

            try:
                # file_set is passed for FileProcessor internal state, currently not used by it.
                converted_path, file_type = self.file_processor.process_file(file_path_abs, file_set)

                user_name = original_filename_for_single_file if original_filename_for_single_file else os.path.basename(file_path_abs)

                file_set[file_path_abs] = { # Key is the actual path of the single uploaded file
                    "hash": file_hash,
                    "converted_path": str(converted_path) if converted_path else str(file_path_abs),
                    "file_type": file_type,
                    "original_filename_for_check": user_name, # Key changed
                    "source_path_for_publishing": file_path_abs  # Key changed
                }
            except Exception as e_proc_single:
                LogService.error_log(f"Error processing single file {file_path_abs}: {e_proc_single}", TASK_NAME)

        # file_set is populated by reference and used by FileOrchestrator after this method returns.