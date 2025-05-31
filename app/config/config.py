import json
import os
from dotenv import load_dotenv

class Config:
    def __init__(self, config_file='app/config/config.json'):
        
        # Cargar configuraciones generales desde el archivo JSON
        self.load_json_config(config_file)
        self.load_variables_env()
        # Configuración de la base de datos
        # db_config = self.DATABASE

        self.SQLALCHEMY_DATABASE_URI = self.get_sqlalchemy_database_uri()

        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.SQLALCHEMY_ECHO = False
        self.SQLALCHEMY_POOL_SIZE = 20         # 🔥 Número de conexiones en el pool
        self.SQLALCHEMY_MAX_OVERFLOW = 20      # 🔥 Conexiones adicionales permitidas
        self.SQLALCHEMY_POOL_TIMEOUT = 30      # 🔥 Tiempo de espera antes de fallar
        self.SQLALCHEMY_POOL_RECYCLE = 300     # 🔥 Reciclaje de conexiones
    def load_json_config(self, config_file):
        try:

            with open(config_file, 'r') as f:
                config_data = json.load(f)
                # Configurar valores desde el JSON
                self.GLOBALES = config_data.get('Globales', {})
                self.PARAMETROS = config_data.get('Parametros', {})
                self.LOGS = config_data.get('Logs', {})
                self.DATABASE = config_data.get('BaseDatos', {})
                self.WEBSCRAPING = config_data.get('WebScraping', {})   
                self.CONVERSIONFORMAT = config_data.get('DocumentConversion', {})
                self.NOTIFICACIONES = config_data.get('NotificacionesEmail', {})
                self.AIRFLOW = config_data.get('Airflow', {})   
                self.CORTES = config_data.get('Cortes', {})

        except FileNotFoundError:
            print(f"Configuration file {config_file} not found.")
            raise
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the configuration file {config_file}.")
            raise

    def load_variables_env(self):
        # Cargar las variables de entorno desde .env
        load_dotenv()
        print(os.getenv("FLASK_ENV"))  # Verificar si se está cargando correctamente
        
        #self.TOKEN_NOCODB = os.getenv('TOKEN_NOCODB')

        self.WEBCREDENTIALS = {
            "USERNAME": os.getenv('DAVIBOX_USERNAME'),
            "PASSWORD": os.getenv('DAVIBOX_PASSWORD'),
            }

        self.DOCFLY = {
            "CREDENTIAL": os.getenv('DOCFLY_CREDENTIAL'),
            "PROYECT_ID": os.getenv('DOCFLY_PROYECT_ID'),
            "REGION": os.getenv('DOCFLY_REGION'),
            "NAME_PUBLISHER": os.getenv('DOCFLY_NAME_PUBLISHER'),
            "NAME_RESPONSE": os.getenv('DOCFLY_NAME_RESPONSE'),
            }
        self.EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
        self.FLASK = {
            "HOST": os.getenv('FLASK_HOST'),
            "PORT": os.getenv('FLASK_PORT'),
            "DEBUG": os.getenv('FLASK_DEBUG'),
            }
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'configure_a_strong_random_secret_key_in_env') # Default is for dev only


    def get_sqlalchemy_database_uri(self):
        """
        Construye la URI de conexión para SQLAlchemy utilizando los valores del archivo JSON
        y solo toma credenciales sensibles desde las variables de entorno.
        """
        server = self.DATABASE.get('Servidor')
        port = self.DATABASE.get('Puerto')
        database = self.DATABASE.get('BaseDatos')
        username = os.getenv('SQL_USERNAME')
        password = os.getenv('SQL_PASSWORD')

        if not all([server, port, database, username, password]):
            raise ValueError("Faltan parámetros para construir la URI de conexión a la base de datos.")
        
        #print (f"postgresql+psycopg2:{username}:{password}@{server}:{port}/{database}")
            #"?driver=ODBC+Driver+17+for+SQL+Server")

        # URI para SQL Server con pyodbc
        return (
            f"postgresql+psycopg2://{username}:{password}@{server}:{port}/{database}"
        )

