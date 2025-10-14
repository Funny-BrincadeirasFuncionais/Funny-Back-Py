# Dockerfile para Funny-Back-Py
FROM python:3.11-slim

# Evitar prompts e configurar diretório de trabalho
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do SO necessárias para alguns pacotes (caso precise)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    wget \
  && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copiar o restante do projeto
COPY . /app

# Garantir permissão do script de entrada
RUN chmod +x /app/entrypoint.sh

# Variável padrão (o Render define $PORT automaticamente)
ENV PORT=8000

EXPOSE ${PORT}

# Entrypoint: aplica migrations e inicia o servidor
ENTRYPOINT ["/app/entrypoint.sh"]
