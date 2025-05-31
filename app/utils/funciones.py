import os
from typing import List
from datetime import datetime
import tempfile
import shutil
from zoneinfo import ZoneInfo
import PyPDF2
import fitz # PyMuPDF
from flask import current_app
from app.repositories.prompts_repository import PromptsRepository
from app.utils.LogService import LogService
import traceback

# Se inicializa nombre de tarea
TASK_NAME = "funciones.py"

def unir_pdfs(pdf_principal: str, lista_pdfs: List[str]) -> str:
    """
    Une varios archivos PDF en uno solo, reemplazando el PDF principal con el resultado final.

    :param pdf_principal: Ruta del archivo PDF principal.
    :param lista_pdfs: Lista de rutas de archivos PDF adicionales a unir.
    :return: Ruta del archivo PDF combinado.
    """

    LogService.audit_log(f"Se inicia la unión de los PDFs: PDF Principal {pdf_principal} Hijos: {lista_pdfs}",
                         TASK_NAME)

    if not os.path.isfile(pdf_principal):
        raise FileNotFoundError(f"El archivo principal '{pdf_principal}' no existe.")

    for pdf in lista_pdfs:
        if not os.path.isfile(pdf):
            raise FileNotFoundError(f"El archivo '{pdf}' no existe.")

    try:
        # Crear un nuevo PDF vacío
        pdf_final = fitz.open()

        # Agregar el PDF principal
        with fitz.open(pdf_principal) as pdf:
            pdf_final.insert_pdf(pdf)

        # Agregar los PDFs adicionales
        for pdf_path in lista_pdfs:
            with fitz.open(pdf_path) as pdf:
                pdf_final.insert_pdf(pdf)

        # Guardar en un archivo temporal
        temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        os.close(temp_fd)  # Cerrar descriptor antes de escribir
        pdf_final.save(temp_path)
        pdf_final.close()

        # Reemplazar el archivo original con el nuevo
        shutil.move(temp_path, pdf_principal)

        LogService.audit_log(f"Archivo temporal {temp_path} movido a {pdf_principal}", TASK_NAME)

        return pdf_principal

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        if tb:
            last_trace = tb[-1]
            error_line = last_trace.lineno
            error_file = last_trace.filename
            error_func = last_trace.name
        else:
            error_line = error_file = error_func = "N/A"
        LogService.audit_log(
            f"Error al unir los PDFs en {error_file}, función {error_func}, línea {error_line}: {e}. "
            f"PDF principal: {pdf_principal}, PDFs hijos: {lista_pdfs}",
            TASK_NAME
        )
        raise RuntimeError(f"Error al unir los PDFs: {e} (línea {error_line})")

def create_or_get_pdf_directory(pdf_path: str) -> str:
    """
    Crea una carpeta llamada 'Preprocesamiento' reemplazando la carpeta raíz `Temp`
    del archivo original y devuelve la ruta de la nueva carpeta.

    Args:
        pdf_path (str): Ruta del archivo original.

    Returns:
        str: Ruta de la carpeta de preprocesamiento.
    """
    # Divide la ruta en partes para manipularla
    path_parts = str(pdf_path).split(os.sep)
    
    # Encuentra el índice de la carpeta 'Temp' en la ruta
    if 'Temp' in path_parts:
        temp_index = path_parts.index('Temp')
        # Reemplaza 'Temp' con 'Preprocesamiento'
        path_parts[temp_index] = 'PDFs'
    else:
        raise ValueError("La ruta no contiene la carpeta 'Temp'.")

    # Reconstruye la nueva ruta base
    pdfs_dir = os.sep.join(path_parts[:-1])  # Mantiene los subdirectorios
    #print(preprocessing_dir)

    # Crea la carpeta de preprocesamiento si no existe
    os.makedirs(pdfs_dir, exist_ok=True)

    return pdfs_dir

def es_pdf_valido(ruta_pdf):
    """Verifica si un archivo PDF es válido y no está corrupto"""
    try:
        with open(ruta_pdf, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return len(reader.pages) > 0  # Si tiene páginas, es válido
    except Exception as e:
        print(f"Archivo inválido: {ruta_pdf} - Error: {e}")
        return False

def calcular_corte():
    """Determina el corte del día con manejo de zona horaria."""
    tz = ZoneInfo("America/Bogota")
    now = datetime.now(tz)
    hora_actual = now.time()
    fecha_actual = now.strftime("%d%m%Y")

    # Obtener configuraciones
    config = current_app.config['CORTES']
    inicio_corte1 = datetime.strptime(config['InicioCorte1'], "%H:%M:%S").time()
    fin_corte1 = datetime.strptime(config['FinCorte1'], "%H:%M:%S").time()
    inicio_corte2 = datetime.strptime(config['InicioCorte2'], "%H:%M:%S").time()
    fin_corte2 = datetime.strptime(config['FinCorte2'], "%H:%M:%S").time()

    # Validación
    if fin_corte1 >= inicio_corte2:
        current_app.logger.error("Configuración de cortes inválida: rangos solapados")
        return f"{fecha_actual}_0"  # Fallback

    # Determinar corte
    if inicio_corte1 <= hora_actual <= fin_corte1:
        return f"{fecha_actual}_1"
    elif inicio_corte2 <= hora_actual <= fin_corte2:
        return f"{fecha_actual}_2"
    else:
        return f"{fecha_actual}_3"
    
def eliminar_archivo(file_path: str) -> None:
    """Delete files if they exist."""
    if os.path.isfile(file_path):  # Check if file exists
        os.remove(file_path)  # Delete file
        LogService.audit_log(f"Archivo eliminado: {file_path}", TASK_NAME)
    else:
        LogService.audit_log(f"El archivo no existe: {file_path}", TASK_NAME)

def backup_compressed_file(compressed_file_path):
    # Obtener la ruta base del proyecto desde la configuración
    base_dir: str = current_app.config['GLOBALES']['RutaBaseProyecto']
    backup_dir: str = os.path.join(base_dir, "Backup")

    os.makedirs(backup_dir, exist_ok=True)

    # Obtener nombre base y extensión
    file_name = os.path.basename(compressed_file_path)
    name, ext = os.path.splitext(file_name)
    
    timestamp = datetime.now().strftime("%H%M%S")
    new_file_name = f"{name}_{timestamp}{ext}"

    # Ruta destino con nuevo nombre
    to_backup = os.path.join(backup_dir, new_file_name)

    # Copiar el archivo
    shutil.copy2(compressed_file_path, to_backup)
    print(f"Backup creado en: {to_backup}")
