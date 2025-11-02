#!/usr/bin/env bash
set -e

# Espera opcional por variáveis ou serviços — simples retry loop (opcional)
# Você pode melhorar esse bloco para checar conexão com o Postgres.
# Loop simples: tenta rodar migrate até 10x antes de falhar.
ATTEMPTS=0
MAX_ATTEMPTS=10
SLEEP_SECONDS=3

until psql -h "${DB_HOST:-${db_host:-localhost}}" -U "${DB_USER:-${db_user:-postgres}}" -c '\q' 2>/dev/null || [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; do
  ATTEMPTS=$((ATTEMPTS+1))
  echo "Aguardando Postgres... tentativa $ATTEMPTS/$MAX_ATTEMPTS"
  sleep $SLEEP_SECONDS
done

# Rodar migrations Alembic (se houver)
echo "Rodando migrations Alembic..."
alembic upgrade head || echo "Falha ao rodar alembic upgrade head - continueu mesmo assim"

# Start Gunicorn com Uvicorn worker. Porta é provida por $PORT (Render).
echo "Iniciando Gunicorn..."
exec gunicorn -k uvicorn.workers.UvicornWorker "app.main:app" \
  --bind "0.0.0.0:${PORT}" \
  --workers 2 \
  --timeout 120
