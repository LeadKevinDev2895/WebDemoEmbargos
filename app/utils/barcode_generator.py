import os
import re

import fitz  # PyMuPDF
from reportlab.graphics.barcode import code128
from reportlab.pdfgen import canvas
from io import BytesIO
from multiprocessing import Pool, cpu_count

from app.utils.LogService import LogService

TASKNAME = "barcode_generator.py"

class BarcodeGenerator:
    """
    Clase para agregar códigos de barras únicos a una lista de PDF y guardarlos en una carpeta temporal.
    """

    def __init__(self):
        """
        Constructor de la clase.
        """

    @staticmethod
    def generate_barcode_image(text, barcode_width, barcode_height):
        """
        Genera un código de barras en memoria con el número de radicado y el nombre del archivo debajo.

        Args:
            text (str): Número de radicado
            barcode_width (int): Ancho del código de barras. Por defecto es 180
            barcode_height (int): Alto del código de barras. Por defecto es 50.

        Returns:
            bytes: Imagen del código de barras con el texto debajo, en formato PNG.
        """
        try:
            # Ajustar la altura para incluir el texto debajo del código de barras
            total_height = barcode_height + 40  # 40 unidades adicionales para el texto

            # Crear un PDF temporal en memoria
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=(barcode_width, total_height))

            # Dibujar el código de barras
            barcode = code128.Code128(text, barWidth=1, barHeight=barcode_height)
            barcode.drawOn(c, 0, 30)  # 30 unidades de margen para el texto debajo

            # Configurar la fuente y el tamaño del texto
            c.setFont("Helvetica", 10)

            # Centrar el número de radicado debajo del código de barras
            text_width = c.stringWidth(text, "Helvetica", 10)  # Usar stringWidth desde el objeto canvas
            c.drawString((barcode_width - text_width) / 2, 20, text)  # Centrado en X

            # Finalizar el PDF
            c.save()

            # Convertir el PDF temporal en una imagen PNG en memoria
            buffer.seek(0)
            pdf_doc = fitz.open(stream=buffer.read(), filetype="pdf")
            page = pdf_doc[0]
            pix = page.get_pixmap()
            return pix.tobytes()  # Devuelve la imagen en formato PNG
        except Exception as e:
            LogService.error_log(f"Error al generar el código de barras: {e}", TASKNAME)
            raise

    @staticmethod
    def extract_radicado_number(filename):
        """
        Extrae el número de radicado del nombre del archivo.

        Args:
            filename (str): Nombre del archivo PDF.

        Returns:
            str: Número de radicado extraído.
        """
        # La expresión regular busca una secuencia de letras y números antes de ".pdf"
        patron = r'([A-Za-z0-9]+)(?=\.pdf$)'
        resultado = re.search(patron, filename)
        if resultado:
            return resultado.group(1)
        return None

    def process_single_pdf(self, code_barcode, input_pdf, output_pdf, barcode_width = 180, barcode_height = 50, margin_right = 10, margin_top = 10):
        """
        Procesa un solo PDF agregando un código de barras único a cada uno.
        """
        try:
            if not code_barcode:
                LogService.audit_log(f"No se genero código de barras, numero de radicado incorrecto: {output_pdf}", TASKNAME)
                return None
            # Generar el código de barras con el texto debajo
            barcode_image = self.generate_barcode_image(code_barcode, barcode_width, barcode_height)

            # Insertar el código de barras en el PDF
            doc = fitz.open(input_pdf)
            for page in doc:
                page_width = page.rect.width
                x = page_width - barcode_width - margin_right
                y = margin_top
                rect = fitz.Rect(x, y, x + barcode_width, y + barcode_height + 40)  # Ajustar altura para el texto
                page.insert_image(rect, stream=barcode_image)  # Insertar la imagen desde memoria
            doc.save(output_pdf)
            LogService.audit_log(f"PDF con código de barras guardado en: {output_pdf}", TASKNAME)
        except Exception as e:
            LogService.error_log(f"Error al procesar {input_pdf}: {e}", TASKNAME)

    def process_pdfs(self, input_folder, temp_output_folder, barcode_width = 180, barcode_height = 50, margin_right = 10, margin_top = 10):
        """
        Procesa todos los PDF en la carpeta de entrada, agregando un código de barras único a cada uno.
        """
        try:
            LogService.audit_log(f"Procesando PDFs en: {input_folder}", TASKNAME)
            # Verificar si la carpeta de salida temporal existe, si no, crearla
            if not os.path.exists(temp_output_folder):
                os.makedirs(temp_output_folder)
            # Preparar los argumentos para el procesamiento en paralelo
            args_list = []
            for filename in os.listdir(input_folder):
                if filename.endswith(".pdf"):
                    code_barcode = self.extract_radicado_number(filename)
                    input_pdf = os.path.join(input_folder, filename)
                    output_filename = os.path.splitext(filename)[0] + "_Barcode.pdf"  # Agregar _Barcode al nombre
                    output_pdf = os.path.join(temp_output_folder, output_filename)
                    args_list.append((code_barcode, input_pdf, output_pdf, barcode_width, barcode_height, margin_right, margin_top))

            # Procesar en paralelo
            with Pool(cpu_count()) as pool:
                pool.starmap(self.process_single_pdf, args_list)

            LogService.audit_log(f"Procesamiento completado. PDFs modificados guardados en: {temp_output_folder}", TASKNAME)
        except Exception as e:
            LogService.error_log(f"Error al procesar los PDFs: {e}", TASKNAME)
            raise

# Ejemplo de uso por carpeta
# if __name__ == "__main__":
#     try:
#         # Rutas de las carpetas de entrada y salida temporal
#         input_folder = "C:/Users/Usuario/Desktop/PDFs_Originales"
#         temp_output_folder = "C:/Users/Usuario/Desktop/PDFs_Temporales"
#
#         # Crear una instancia de BarcodeGenerator
#         barcode_adder = BarcodeGenerator()
#
#         # Procesar los PDFs
#         barcode_adder.process_pdfs(input_folder, temp_output_folder)
#     except Exception as e:
#         print(f"Ocurrió un error: {e}")

# Ejemplo de uso documentos individuales
# if __name__ == "__main__":
#     try:
#         # Rutas de las carpetas de entrada y salida temporal
#         input_folder = "C:/Users/Usuario/Desktop/PDFs_Originales/RCCI2030225001.pdf"
#         temp_output_folder = "C:/Users/Usuario/Desktop/PDFs_Temporales/RCCI2030225001_Barcode_Individual.pdf"
#
#         # Crear una instancia de BarcodeGenerator
#         barcode_adder = BarcodeGenerator()
#
#         # Procesar los PDFs
#         barcode_adder.process_single_pdf("RCCI2030225001", input_folder, temp_output_folder)
#     except Exception as e:
#         print(f"Ocurrido un error: {e}")