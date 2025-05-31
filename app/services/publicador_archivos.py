import os
import shutil
from datetime import datetime
import subprocess
import traceback

class LocalBucketTransfer:
    def __init__(self, base_path: str):
        """
        Inicializa la clase con la ruta base del bucket local.
        
        :param base_path: Ruta base donde se almacenarán los archivos.
        """
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)
    
    def _generate_destination_path(self, filename: str) -> str:
        """
        Genera la ruta de destino basada en la fecha actual y renombra el archivo con el formato requerido.
        
        :param filename: Nombre original del archivo.
        :return: Ruta completa del archivo en el bucket local.
        """
        today = datetime.today()
        year = str(today.year)
        month = f"{today.month:02d}"
        day = f"{today.day:02d}"
        
        # Extraer la extensión y generar el nuevo nombre con formato ArchivoDDMMAA.ext
        name, ext = os.path.splitext(filename)
        new_filename = f"{today.strftime('%d%m%y')} - {name}{ext}"
        
        destination_folder = os.path.join(self.base_path, year, month, day)
        os.makedirs(destination_folder, exist_ok=True)
        
        # Asegurar permisos para todo el árbol de directorios
        try:
            print(f"Cambiando permisos de {destination_folder}")
            subprocess.run(['chmod', '-R', '777', destination_folder], check=True)
            print(f"Permisos cambiados de {destination_folder}")
        except subprocess.CalledProcessError as e:
            print(f"Error al cambiar permisos de {destination_folder}: {e}")
        
        return os.path.join(destination_folder, new_filename)
    
    def transfer_file(self, source_path: str) -> str:
        """
        Transfiere un archivo a la estructura de carpetas del bucket local.
        
        :param source_path: Ruta completa del archivo de origen.
        :return: Ruta final del archivo en el bucket local.
        """
        print(f"Transferiendo archivo: {source_path}")
        if not os.path.isfile(source_path):
            raise FileNotFoundError(f"El archivo {source_path} no existe.")
        
        filename = os.path.basename(source_path)
        destination_path = self._generate_destination_path(filename)
        try:
            shutil.copy(source_path, destination_path)
            if os.path.exists(destination_path):
                estado = True
                print(f"Archivo {source_path} transferido a {destination_path}")
            else:
                estado = False
                print(f"Error al transferir el archivo {source_path} a {destination_path}")
        except shutil.SameFileError:
            if os.path.exists(destination_path):
                estado = True
                print(f"Archivo {source_path} ya existe en {destination_path}")
            else:
                estado = False
                print(f"Error al transferir el archivo {source_path} a {destination_path}")
                traceback.print_exc()
        except Exception as e:
            estado = False
            traceback.print_exc()
            print(f"Error al transferir el archivo {source_path}: {e}")
        return estado, destination_path