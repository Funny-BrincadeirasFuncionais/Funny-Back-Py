#!/usr/bin/env bash
set -e

# Aguarda o PostgreSQL estar pronto usando as variáveis de ambiente corretas do Render
ATTEMPTS=0
MAX_ATTEMPTS=10
SLEEP_SECONDS=3

# Extrair host, user do DATABASE_URL se existir, senão usar valores padrão
DB_HOST_VAR="${db_host:-localhost}"
DB_USER_VAR="${db_user:-postgres}"

until psql -h "$DB_HOST_VAR" -U "$DB_USER_VAR" -c '\q' 2>/dev/null || [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; do
  ATTEMPTS=$((ATTEMPTS+1))
  echo "Aguardando Postgres... tentativa $ATTEMPTS/$MAX_ATTEMPTS"
  sleep $SLEEP_SECONDS
done

# Rodar migrations Alembic
echo "Rodando migrations Alembic..."
if command -v alembic &> /dev/null; then
  alembic upgrade head || echo "⚠️  Falha ao rodar alembic upgrade head - continuando mesmo assim"
else
  echo "⚠️  Alembic não encontrado - pulando migrations"
fi

# Start Gunicorn com Uvicorn worker. Porta provida por $PORT (Render usa 10000)
echo "Iniciando Gunicorn..."
exec gunicorn -k uvicorn.workers.UvicornWorker "app.main:app" \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
