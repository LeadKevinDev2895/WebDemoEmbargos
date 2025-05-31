from flask import Flask
from app.config.config import Config 
from app.utils.LogService import LogService
from flask_sqlalchemy import SQLAlchemy
#from flask_migrate import Migrate
from sqlalchemy import MetaData


# metadata = MetaData(schema="public")
# db = SQLAlchemy(metadata=metadata)  # Inicialización directa de SQLAlchemy

db = SQLAlchemy()
#migrate = Migrate()  # Instancia de Flask-Migrate

def create_app():
    app = Flask(__name__)
   
    app.config.from_object(Config())
    
    # Obtener el esquema de la configuración
    schema = app.config['DATABASE']['SqlSchema']

    # Configurar el esquema en la metadata de SQLAlchemy
    db.metadata.schema = schema

    db.init_app(app)  # Inicializar SQLAlchemy
    #migrate.init_app(app, db) # Inicializar Flask-Migrate
    
    with app.app_context():
        
        from app.models.demandado import Demandado
        from app.models.demandante import Demandante
        from app.models.entidad import Entidad
        from app.models.documento import Documento
        from app.models.medida_cautelar import MedidaCautelar
        from app.models.producto import Producto
        from app.models.parametros import Parametros
        from app.models.prompts import Prompts
        from app.models.resoluciones import Resolucion
        from app.models.reporte_cruce import ReporteCruce
        from app.models.enums import ClaseDeposito, TipoEntidad, TipoIdentificacion, TipoMedida,TipoEmbargo, TipoDocumento, TipoProcesamiento
        
        # db.create_all()  # Crea las tablas en la base de datos
        db.session.commit()  # Asegura que los cambios sean aplicados
        # print("Tablas creadas exitosamente.")
        from .routes import bp as main_bp
        app.register_blueprint(main_bp)

        LogService.initialize_logger()

    # 🔥 Aquí añadimos la función para cerrar sesiones después de cada request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()  # 🔥 Libera la sesión después de cada request    

    return app

# ✅ Función para obtener la sesión de SQLAlchemy
def get_session():
    """Obtiene la sesión actual de la base de datos."""
    return db.session