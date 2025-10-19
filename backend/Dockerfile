# ================================================================================================
# BACKEND DOCKERFILE - Django REST API
# ================================================================================================

# Use uma imagem oficial do Python como base
FROM python:3.11-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Define o diretório de trabalho no container
WORKDIR /app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos primeiro (melhor cache do Docker)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do backend
COPY . .

# Expõe a porta 8000
EXPOSE 8000

# Executa migrações e inicia o servidor
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver_plus --cert-file certs/dev-cert.pem --key-file certs/dev-key.pem 0.0.0.0:8000"]
