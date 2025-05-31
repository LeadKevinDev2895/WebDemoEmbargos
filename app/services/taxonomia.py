import os
import csv
import shutil
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import traceback
from app.repositories.documento_repository import DocumentoRepository
from app.repositories.medida_cautelar_repository import MedidaCautelarRepository
from app.repositories.entidad_repository import EntidadRepository
from app.utils.barcode_generator import BarcodeGenerator
from app.utils.LogService import LogService
from flask import current_app


class Taxonomia:

    def __init__(self, app=None):
        self.consulta = DocumentoRepository()
        self.medida = MedidaCautelarRepository()
        self.entidad = EntidadRepository()
        self.barcode = BarcodeGenerator()
        self.app = app
        self.TASKNAME = "taxonomia.py"
        with self.app.app_context(): 
            self.ruta_salida = current_app.config["GLOBALES"]["RutaSalidaArchivos"]
            #crea la ruta de salida si no existe
            os.makedirs(self.ruta_salida, exist_ok=True)
            self.ruta_origen_publicador = current_app.config["GLOBALES"]["RutaPublicador"]
            self.ruta_origen_Datos = current_app.config["GLOBALES"]["RutaPublicador"]

    def trasladar_archivos(self):
        """
        copia y pega archivos teniendo en cuenta las limitantes
        """
        try:
            LogService.audit_log("Comienza la tarea trasladar archivos", self.TASKNAME)
            #muestra una lista con las carpetas que hay en la ruta de salida
            carpetas = [item for item in os.listdir(self.ruta_salida) if os.path.isdir(os.path.join(self.ruta_salida, item))]
            #verifica si hay carpetas para comprmir en la ruta de salida
            if not carpetas:   
                nueva_carpeta = f"{self.ruta_salida}/TRY_{datetime.now().strftime('%d-%m-%Y-%H-%M')}"
                #crea una carpeta si no existe alguna en la ruta de salida
                os.makedirs(nueva_carpeta, True)
                
            #Esta variable sirve para identificar si se integraron nuevos pdfs a la taxonomia
            nuevo_documento = False

            #este bucle itera todos los documentos de la base de datos
            for documento in [item for item in self.consulta.get_all_today()]:

                conteo_total_pdfs = 0

                #este bucle identifica que capeta usar para el traslado de  imagenes
                for i in [item for item in os.listdir(self.ruta_salida) if os.path.isdir(os.path.join(self.ruta_salida, item))]:

                    ruta_carpeta_comprimir = f"{self.ruta_salida}/{i}"

                    lista_pdfs = [archivo for archivo in os.listdir(ruta_carpeta_comprimir)]
                    #Este contador es para verificar que carpeta no tiene 5.000 pdfs para copiar y pegar los pdfs
                    contador_pdfs_carpeta = len(list(filter(lambda e: Path(e).suffix.upper().__eq__('.PDF'), lista_pdfs)))
                    
                    #Si la carpeta tiene menos de 5000 pdfs y la fecha de la carpeta es igual a la fecha actual
                    #se usara esa carpeta para la taxonomia
                    if contador_pdfs_carpeta < 5000 and i[4:14] == datetime.now().strftime("%d-%m-%Y"):
                        ruta_valida = True
                        break

                    ruta_valida = False

                if not ruta_valida:
                    ruta_carpeta_comprimir = f"{self.ruta_salida}/TRY_{datetime.now().strftime('%d-%m-%Y-%H-%M')}"
                    os.makedirs(ruta_carpeta_comprimir, exist_ok=True)
                
                """
                consulta a la base de datos por id de la tabla documento
                si tiene anexos tomar documento desde el campo rutaDocumento pero si no entonces tomarlo
                de rutaDocumentoConvertido
                """
                #ruta_anexo = documento.rutaDocumentoConvertido

                #Determina que tipo ruta de archivo se usara
                ruta_origen = documento.rutaDocumentoConvertido
                
                # Usar pathlib para manejo correcto de rutas
                path_origen = Path(ruta_origen)
                nombre_base = path_origen.stem  # Nombre sin extensión
                extension = path_origen.suffix  # Extensión

                if self.verificacion_documento_csv(ruta_carpeta_comprimir, nombre_base):
                    LogService.audit_log(f"Documento {nombre_base} ya existe en el archivo csv", self.TASKNAME)
                    print(f"Documento {nombre_base} ya existe en el archivo csv")
                    continue

                nuevo_documento = True

                #Valida que el radicado del documento sea correcto
                numeros_radicado = [
                    r"^(R)([a-zA-Z]{3})[0-9]{,1}([0-9]{6})([0-9]{3,4})$",
                    r"^(R)([a-zA-Z]{3})[0-9]{6}([0-9]{4})$"
                    ]

                #identifica si el tipo de medida es embargo o desembargo
                tipo_medida = "Otro".capitalize()
                if documento.medida_id:
                    tipo_medida = self.medida.get_by_id(documento.medida_id).tipoMedida.value.capitalize()

                #Si el numero de radicado no es valido entonces pasara a revizar el siguiente documento
                #o el tipo de medida es diferente a embargo o desembargo se descartara de la taxonomia
                if not any(re.search(condicion.upper(),nombre_base) for condicion in numeros_radicado):

                    print(f"Radicado invalido: {nombre_base} - doc {documento.id}")

                    continue

                if tipo_medida.capitalize() != "Embargo".capitalize() and tipo_medida.capitalize() != "Desembargo".capitalize():
                    print(f"Tipo medida invalida - {tipo_medida} - doc {documento.id}")

                    continue

                #Se excluyen los archivos que no sean pdfs
                if extension.upper() != ".pdf".upper():
                    LogService.audit_log(f"Documento {documento.id} no es un pdf - extension {extension}",self.TASKNAME)
                    continue
            
                #Crear nuevo nombre del documento segun el estado del proceso
                if not (documento.estadoProceso.__eq__('ERROR')):
                    nuevo_nombre = f"{nombre_base}_{tipo_medida}Procesado{extension}"

                elif documento.estadoProceso.__eq__('ERROR'):
                    nuevo_nombre = f"{nombre_base}_{tipo_medida}NoProcesado{extension}"
                    
                # Ruta destino
                ruta_destino = Path(ruta_carpeta_comprimir) / nuevo_nombre
                
                # Copiar archivo
                # shutil.copy2(path_origen, ruta_destino)
                base_name = os.path.basename(documento.rutaDocumentoConvertido)
                name = os.path.splitext(base_name)[0]
                self.barcode.process_single_pdf(name, path_origen, ruta_destino)

                medida = self.medida.get_by_id(documento.medida_id) if documento.medida_id else None
                entidad = self.entidad.get_by_id(medida.entidad_id) if medida else None

                #Extrae la fecha de creacion del documento y le da el formato dd-mm-aaaa
                regex_fecha = r"(19\d{2}|20\d{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])"
                fecha = '/'.join(next(iter(re.findall(regex_fecha, str(medida.fecha_creacion))), [])) if medida else None
                fecha_creacion = datetime.strptime(fecha, '%Y/%m/%d').strftime('%d/%m/%Y') if fecha else ''
                fecha_recepcion = datetime.strptime(documento.fechaRecepcion, "%d/%m/%Y %H:%M").strftime("%d%m%Y")
                # Limitar caracteres de origen
                name_origin = entidad.entidad if entidad and entidad.entidad else ''
                if len(name_origin) > 64:
                    name_origin = name_origin[:64]
                nueva_fila = [
                    "Correspondencia", 
                    f"tipoDocumento={tipo_medida}Procesado",
                    f"fechaExpedicion={fecha_creacion}",
                    f"Origen={name_origin}",
                    f"radicado={medida.numeroCarteroWeb if medida else ''}",
                    f"Oficio={medida.numeroOficio if medida.numeroOficio else fecha_recepcion}",
                    f"proceso=CorrespondenciaTrycore",
                    f"{nuevo_nombre}"
                    ]

                #Se filtran los campos que no esten vacios y sin valores nulos
                nueva_fila = list(filter(lambda e: e.split("=")[-1].strip() and not ("NONE" in e.upper()), nueva_fila))

                self.taxonomia_csv(nueva_fila, ruta_carpeta_comprimir, medida.numeroCarteroWeb if medida else '')

                #Regex para extraer la fecha
                fecha_regex = r"(0[1-9]|[12]\d|3[01])-(0[1-9]|1[0-2])-(19\d{2}|20\d{2})"
                #Lista de carpetas que tienen la fecha actual
                carpetas_actuales = list(map(lambda e: os.path.join(self.ruta_salida, e), #Devuelve la ruta completa de cada carpeta
                                        filter(
                                                #filtro que verifica que solo hayan carpetas y que la fecha de la carpeta sea una fecha actual mediante regex
                                                lambda carpeta: not Path(carpeta).suffix and '-'.join(next(iter(re.findall(fecha_regex, carpeta)), []))==datetime.now().strftime("%d-%m-%Y"),
                                                #Lista de carptas en la ruta de taxonomia
                                                os.listdir(self.ruta_salida))
                                        ))

                #suma el numero total de pdfs que que tiene cada carpeta
                conteo_total_pdfs = sum(list(map(lambda ruta: len(list(filter(lambda archivo: Path(archivo).suffix.__eq__('.pdf'),os.listdir(ruta)))), carpetas_actuales)))

                LogService.audit_log(f"Numero total de pdfs: {conteo_total_pdfs} - fecha: {datetime.now().strftime('%d-%m-%Y')} ", self.TASKNAME)

    
            #Verifica si hay 60000 pdfs procesados en el dia para la taxonomia
            if conteo_total_pdfs >= 60000:

                LogService.audit_log(f"¡Advertencia! Hay mas de 60000 pdfs el dia de hoy {datetime.now().strftime('%d-%m-%Y')}", self.TASKNAME)

            LogService.audit_log("Termina la tarea trasladar archivos", self.TASKNAME)
            return self.comprimir_archivos(ruta_carpeta_comprimir) if nuevo_documento else None
        except Exception as e:

            print(f"Error en el bot: {e}")
            # Captura el traceback completo
            error_trace = traceback.format_exc()

            # Registra el error en logs (si usas logging, puedes integrarlo aquí)
            print("Traceback completo del error:")
            print(error_trace)
            LogService.error_log(f"Ha ocurrido un error inesperado al trasladar archivos: {e}", self.TASKNAME)
            return None


    def comprimir_archivos(self, ruta):
        """
        Comprime una carpeta
        """
        try:
            shutil.make_archive(ruta, 'zip', ruta)
            LogService.audit_log("Termina la tarea comprimir archivos", self.TASKNAME)
            return os.path.abspath(f"{ruta}.zip")
        except Exception as e:
            LogService.error_log(f"Ha ocurrido un error al comprimir archivos: {e}", self.TASKNAME)
            return None

    def verificacion_documento_csv(self, ruta_archivo_csv, numero_cartero_web):
        """
        verifica si el documento ya fue registrado en el archivo csv
        retorna True en caso de que este ya exista en el csv, de lo contrario retornara False
        """
        archivos_csv = [f for f in os.listdir(ruta_archivo_csv) if f.endswith(".csv")]
        for archivo in archivos_csv:
            #Verifica si el numero de radicado esta en el archivo csv para excluirlo
            df = pd.read_csv(f"{ruta_archivo_csv}/{archivo}", header=None, sep=';', names=list(range(8)), engine='python')
            formato_csv_ncw = [
                    r"radicado=(R[A-Z]{3})(\d{2})(\d{2})(\d{2})(\d{3,4})",
                    r"radicado=(R[A-Z]{3})(\d{6})(\d{4})"
            ]
            
            radicados_csv = []
            #identifica el numero de radicado en cada fila del archivo csv
            for index, row in df.iterrows():
                # Acceder a cada columna de la fila actual
                for col_num in range(len(row)):
                    if any(re.search(e, str(row[col_num])) for e in formato_csv_ncw):
                        #Agrega el numero de radicado
                        radicados_csv.append(row[col_num].split("=")[-1])
                
            if any([str(num_csv).__eq__(str(numero_cartero_web)) for num_csv in radicados_csv]):
                return True
        return False

    def taxonomia_csv(self, nueva_fila, ruta_archivo_csv, numero_cartero_web):
        """
        gestiona el archivo csv de taxonomia
        """
        try:
            LogService.audit_log("Comienza la tarea taxonomia csv", self.TASKNAME)
            # Lista solo los archivos que terminan en .csv
            archivos_csv = [f for f in os.listdir(ruta_archivo_csv) if f.endswith(".csv")]

            if archivos_csv:
                for i in archivos_csv:
                    # cuenta el numero de filas del archivo
                    with open(f"{ruta_archivo_csv}/{i}", 'r', encoding='utf-8') as archivo:
                        contador = sum(1 for _ in archivo)
                    #verifica si tiene la extension .csv
                    extension_csv = Path(f"{ruta_archivo_csv}/{i}").suffix.lower() == ".csv"

                    #verifica que el archivo sea del dia de la fecha actual y que no tenga mas de 5000 datos y que la extension sea .csv
                    if i[4:-10] == datetime.now().strftime("%d-%m-%Y") and contador<5000 and extension_csv:
                        #escribe una nueva fila
                        with open(f"{ruta_archivo_csv}/{i}", mode="a", newline="", encoding="utf-8") as archivo:
                            escritor = csv.writer(archivo, delimiter=";")
                            escritor.writerow(nueva_fila)

                        break
                    else:
                        #crea un archivo csv en caso de que hayan archivos csv pero no de la fecha actual
                        nombre_archivo = f"TRY_{datetime.now().strftime('%d-%m-%Y-%H-%M')}.csv"
                        #escribe una nueva fila
                        with open(f"{ruta_archivo_csv}/{nombre_archivo}", mode="w", newline="", encoding="utf-8") as archivo:
                            escritor = csv.writer(archivo, delimiter=";")
                            escritor.writerow(nueva_fila)
                        break
            else:
                #crea el nombre del archivo con la fecha y hora actual en caso de no haber archivos csv
                nombre_archivo = f"TRY_{datetime.now().strftime('%d-%m-%Y-%H-%M')}.csv"
                #escribe una nueva fila
                with open(f"{ruta_archivo_csv}/{nombre_archivo}", mode="w", newline="", encoding="utf-8") as archivo:
                    escritor = csv.writer(archivo, delimiter=";")
                    escritor.writerow(nueva_fila)
            LogService.audit_log("Termina la tarea taxonomia csv", self.TASKNAME)
        except Exception as e:
            error_trace = traceback.format_exc()

            # Registra el error en logs (si usas logging, puedes integrarlo aquí)
            print("Traceback completo del error:")
            print(error_trace)
            LogService.error_log(f"Ha ocurrido un error inesperado en la tarea taxonomia_csv {e}", self.TASKNAME)
