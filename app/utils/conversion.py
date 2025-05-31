# app/services/conversion.py
import os
import subprocess
from PIL import Image
from flask import current_app
from app.utils.LogService import LogService

def convert_to_pdf(input_file, output_file):
    libreoffice_path = current_app.config['CONVERSIONFORMAT']['LibreOfficePath']
    LogService.audit_log("Inicia tarea conversión archivo a PDF", "convert_to_pdf.py")

    if not os.path.exists(input_file):
        return "El archivo de entrada no existe."

    if not os.path.exists(libreoffice_path):
        return "No se encontró LibreOffice en la ruta especificada. Verifica la instalación."

    file_extension = os.path.splitext(input_file)[1].lower()

    try:
        if file_extension in ['.doc', '.docx', '.odt', '.rtf']:
            subprocess.run([
                libreoffice_path, '--headless', '--convert-to', 'pdf', input_file, '--outdir', os.path.dirname(output_file)
            ], check=True)
            generated_pdf = os.path.splitext(input_file)[0] + '.pdf'
            if os.path.exists(generated_pdf):
                os.rename(generated_pdf, output_file)
                return f"El archivo se ha convertido a PDF correctamente: {output_file}"
            else:
                return "No se pudo generar el archivo PDF con LibreOffice."
        elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            with Image.open(input_file) as img:
                img.convert('RGB').save(output_file, 'PDF', resolution=100.0)
            return f"La imagen se ha convertido a PDF correctamente: {output_file}"
        else:
            return "El formato de archivo no es compatible para la conversión a PDF."
    except subprocess.CalledProcessError as e:
        LogService.error_log(f"Error al usar LibreOffice, observación: {str(e)}", "convert_to_pdf.py")
        return f"Error al usar LibreOffice: {e}"
    except Exception as e:
        LogService.error_log(f"Se produjo un error durante la conversión, observación: {str(e)}", "convert_to_pdf.py")
        return f"Se produjo un error durante la conversión: {e}"
