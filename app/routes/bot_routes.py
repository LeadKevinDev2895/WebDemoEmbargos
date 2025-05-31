import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, current_app, request
from app.bot import Bot


# Crear el Blueprint para las rutas

bp = Blueprint('routes', __name__)


@bp.route('/')
def index():
    return jsonify({"message": "Servicio Flask activo"})

@bp.route('/download_files')
def start_download_files():
    with current_app.app_context():
        bot = Bot(current_app)
        message = bot.run_download_files()
    return jsonify({"message": message})

@bp.route('/taxonomia')
def start_taxonomia():
    with current_app.app_context():
        bot = Bot(current_app)
        message = bot.run_taxonomia()
    return jsonify({"message": message})

@bp.route('/upload_taxonomia')
def start_upload_taxonomia():
    #trae el parametro 'nombre' que es el nombre de la carpeta comprimida de la taxonomia
    nombre_taxonomia = request.args.get('nombre')
    
    if nombre_taxonomia is None:
        return jsonify({"error": "no se obtuvo el parametro 'nombre'"})
    
    with current_app.app_context():
        bot = Bot(current_app)
        message = bot.run_upload_files(nombre_taxonomia)
    return jsonify({"message": message})

# @bp.route("/reload_env")
# def reload_env():
#     load_dotenv(override=True)  # Recarga el .env
#     print(f"Variables recargadas {current_app.config['WEBCREDENTIALS']['USERNAME']}")
#     return {"status": "Variables recargadas"}
