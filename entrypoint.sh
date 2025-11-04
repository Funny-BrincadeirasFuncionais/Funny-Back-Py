#!/usr/bin/env bash
set -e

echo "Verificando disponibilidade do Postgres..."
ATTEMPTS=0
MAX_ATTEMPTS=10
SLEEP_SECONDS=3

wait_for_postgres() {
  if [ -n "$DATABASE_URL" ]; then
    # Usa a URI completa (inclui usuário/senha/host/porta/db)
    psql "$DATABASE_URL" -c '\q' 2>/dev/null && return 0 || return 1
  else
    # Fallback para variáveis individuais
    DB_HOST_VAR="${db_host:-localhost}"
    DB_USER_VAR="${db_user:-postgres}"
    if [ -n "$db_password" ]; then
      PGPASSWORD="$db_password" psql -h "$DB_HOST_VAR" -U "$DB_USER_VAR" -c '\q' 2>/dev/null && return 0 || return 1
    else
      psql -h "$DB_HOST_VAR" -U "$DB_USER_VAR" -c '\q' 2>/dev/null && return 0 || return 1
    fi
  fi
}

until wait_for_postgres || [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; do
  ATTEMPTS=$((ATTEMPTS+1))
  echo "Aguardando Postgres... tentativa $ATTEMPTS/$MAX_ATTEMPTS"
  sleep $SLEEP_SECONDS
done

# Rodar migrations Alembic
echo "Rodando migrations Alembic..."
if command -v alembic &> /dev/null; then
  if alembic upgrade head; then
    echo "Migrations aplicadas com sucesso."
  else
    echo "⚠️  Falha ao rodar alembic upgrade head. Tentando 'alembic stamp head' como fallback..."
    if alembic stamp head; then
      echo "Alembic version tabelada (stamp head). Continuando."
    else
      echo "⚠️  Falha ao executar 'alembic stamp head'. Continuando mesmo assim."
    fi
  fi
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
