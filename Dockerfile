# ✅ Usamos una imagen base basada en Debian Buster
FROM python:3.9-slim-buster

# Establecemos el directorio de trabajo
WORKDIR /

# ✅ Configuramos `archive.debian.org` y deshabilitamos la verificación de firmas
RUN echo 'deb [trusted=yes] http://archive.debian.org/debian buster main contrib non-free' > /etc/apt/sources.list && \
    echo 'deb [trusted=yes] http://archive.debian.org/debian buster-updates main contrib non-free' >> /etc/apt/sources.list

# ✅ Instalamos las dependencias necesarias
RUN apt-get update -o Acquire::Check-Valid-Until=false \
    && apt-get install -y --no-install-recommends \
       wget \
       curl \
       unzip \
       gnupg \
       python3-pip \
       gcc \
       git \
       nano \
       sshfs \
       fuse3 \
       libpq-dev \
       libreoffice \
       unrar \
       chromium \
       #chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# # ✅ Buscar la ruta real de ChromeDriver
# RUN find / -name chromedriver 2>/dev/null

# # ✅ Crear enlace simbólico si se encuentra ChromeDriver
# RUN if [ -f "/usr/lib/chromium/chromedriver" ]; then ln -s /usr/lib/chromium/chromedriver /usr/local/bin/chromedriver; \
#     elif [ -f "/usr/lib/chromium-browser/chromedriver" ]; then ln -s /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver; \
#     else echo "⚠️ ChromeDriver no encontrado en las rutas esperadas"; exit 1; fi

# # ✅ Verificar que ChromeDriver tiene permisos de ejecución
# RUN chmod +x /usr/local/bin/chromedriver

# Descargar ChromeDriver 90.0.4430.24 manualmente
RUN wget -q "https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip" -O /tmp/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver_linux64.zip

# ✅ Verificar que ChromeDriver tiene permisos de ejecución
RUN chmod +x /usr/local/bin/chromedriver

# ✅ Configuramos Python 3.9 como predeterminado (Si es necesario)
RUN ln -sf /usr/bin/python3 /usr/bin/python
RUN ln -sf /usr/bin/pip3 /usr/bin/pip

# ✅ Copiamos el código fuente
COPY ./app /app
COPY ./run.py run.py
COPY ./docker/requirements.txt requirements.txt
COPY ./docker/.env .env
COPY ./docker/config.json /app/config/config.json

# ✅ Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Configuramos PYTHONPATH
ENV PYTHONPATH=/app 

# ✅ Exponemos el puerto 5000
EXPOSE 5000

# ✅ Comando correcto para iniciar
CMD ["python3", "run.py"]
