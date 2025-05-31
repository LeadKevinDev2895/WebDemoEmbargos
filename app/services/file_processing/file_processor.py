# file_processor.py
import os
from pathlib import Path
from flask import current_app
from app.utils.LogService import LogService
from app.utils.conversion import convert_to_pdf

TASK_NAME = "FileProcessor"

class FileProcessor:
    def process_text_file(self, file_path):
        """Procesa un archivo de texto."""
        print(f"Procesando archivo de texto: {file_path}")
        LogService.audit_log(f"Procesando archivo de texto: {file_path}", TASK_NAME)
        return file_path, "DESCONOCIDO"

    def process_image_file(self, file_path):
        """Procesa un archivo de imagen convirtiéndolo a PDF."""
        print(f"Procesando archivo de imagen: {file_path}")
        LogService.audit_log(f"Procesando archivo de imagen: {file_path}", TASK_NAME)
        output_file = f"{os.path.splitext(file_path)[0]}.pdf"
        result = convert_to_pdf(file_path, output_file)
        print(f"Resultado conversión Imagen: {result}")
        LogService.audit_log(f"Resultado conversión Imagen: {result}", TASK_NAME)
        return output_file, "IMAGEN"

    def process_pdf_file(self, file_path):
        """Procesa un archivo PDF."""
        print(f"Procesando archivo PDF: {file_path}")
        return file_path, "PDF"

    def process_word_file(self, file_path):
        """Procesa un archivo de Word convirtiéndolo a PDF."""
        print(f"Procesando archivo de Word: {file_path}")
        LogService.audit_log(f"Procesando archivo de Word: {file_path}", TASK_NAME)
        output_file = f"{os.path.splitext(file_path)[0]}.pdf"
        result = convert_to_pdf(file_path, output_file)
        print(f"Resultado conversión Word: {result}")
        LogService.audit_log(f"Resultado conversión Word: {result}", TASK_NAME)
        return output_file, "WORD"

    def process_excel_file(self, file_path):
        """Procesa un archivo de Excel."""
        print(f"Procesando archivo de Excel: {file_path}")
        return file_path, "EXCEL"

    def process_unknown_file(self, file_path):
        """Maneja tipos de archivo desconocidos."""
        print(f"Tipo de archivo desconocido: {file_path}")
        return file_path, "DESCONOCIDO"

    def process_file(self, file_path, file_set):
        """
        Determina el tipo de un archivo y llama a la función de procesamiento adecuada.
        Maneja archivos comprimidos llamando al procesador de archivos comprimidos.
        """
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower()

        if file_extension in ['.txt', '.csv']:
            return self.process_text_file(str(file_path))
        elif file_extension in ['.jpg', '.png', '.jpeg', '.bmp', '.tiff', '.tif']:
            return self.process_image_file(str(file_path))
        elif file_extension == '.pdf':
            return self.process_pdf_file(str(file_path))
        elif file_extension in ['.doc', '.docx']:
            return self.process_word_file(str(file_path))
        elif file_extension in ['.xls', '.xlsx']:
            return self.process_excel_file(str(file_path))
        elif file_extension in ['.zip', '.7z', '.tar', '.rar', '.gz', '.bz2', '.xz']:
            # La lógica para procesar archivos comprimidos ahora está en CompressedFileHandler
            # Aquí simplemente indicamos que es un archivo comprimido
            return None, "Comprimido"
        else:
            return self.process_unknown_file(str(file_path))