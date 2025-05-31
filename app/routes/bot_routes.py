import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, current_app, request, render_template, flash, redirect, url_for
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

@bp.route('/upload_ui')
def upload_ui():
    return render_template('upload.html')

@bp.route('/upload_document_or_archive', methods=['POST'])
def upload_document_or_archive():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('routes.upload_ui'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('routes.upload_ui'))

    if file:
        try:
            bot = Bot(current_app._get_current_object())
            # Bot method now returns: overall_success (bool), message_for_ui (str), ui_category (str)
            overall_success, message_for_ui, ui_category = bot.run_unified_upload_processing(file)
            flash(message_for_ui, ui_category) # Use the category returned by the Bot
        except Exception as e:
            # Log the exception e using LogService or current_app.logger
            # For now, flash a generic error.
            # Consider using LogService.error_log(f"Error in upload: {e}", "Routes")
            flash(f"An unexpected error occurred during processing: {str(e)}", 'error')
    else:
        # This case should ideally not be reached if above checks are done.
        flash('File upload failed for an unknown reason.', 'error')

    return redirect(url_for('routes.upload_ui'))
