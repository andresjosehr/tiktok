FROM python:3.11-slim

# Evitar preguntas durante la instalación
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Chrome y dependencias
RUN apt-get update && apt-get install -y \
    gnupg \
    && curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o /tmp/chrome.deb \
    && apt-get install -y /tmp/chrome.deb || apt-get -f install -y \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Exponer puerto
EXPOSE 8000
