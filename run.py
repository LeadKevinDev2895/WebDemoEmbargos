# import sys
# import os
# sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Agrega el directorio actual al path

from app import create_app

import threading
import sys

# Crear la instancia de Flask y el Bot
app = create_app()


def run_flask():
    """Función para ejecutar Flask en un hilo."""
    print("Ejecutando servicio Flask...")
    app.run(host=app.config['FLASK']['HOST'], port=app.config['FLASK']['PORT'], debug=app.config['FLASK']['DEBUG'])


if __name__ == "__main__":
    # Si se pasa el argumento "bot", ejecuta solo el bot directamente

    #if  
    if len(sys.argv) > 1 and sys.argv[1] == "bot":
        from app.bot import Bot
        print("Ejecutando bot directamente...")
        bot = Bot(app)
        bot.run()

    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        from app.bot import Bot
        print("Ejecutando bot directamente...")
        bot = Bot(app)
        bot.test()
    else:
        # Ejecuta tanto el servicio Flask
        print("Iniciando servicio Flask")

        # Iniciar servicio Flask 
        run_flask()
