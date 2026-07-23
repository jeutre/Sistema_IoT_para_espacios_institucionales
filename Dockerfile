FROM python:3.12-slim

# Evitar que python escriba archivos .pyc y forzar salida stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema operativo requeridas para algunos paquetes python
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Exponer el puerto
EXPOSE 8000

# Script de entrada para correr migraciones y arrancar
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
