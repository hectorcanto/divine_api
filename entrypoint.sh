#!/usr/bin/env bash

set -euo pipefail
# Exit immediately if a command exits with a non-zero status.

echo "Applying migrations..."
alembic upgrade head
echo "Migrations applied successfully"


echo "Starting app..."
APP_MODULE=${APP_MODULE:-"divine.app_factory:create_app"}
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-8080}
LOG_LEVEL=${LOG_LEVEL:-info}
# WORKERS=$(( $(nproc) * 2 + 1))
WORKERS=1
#RELOAD=${RELOAD:-false}

echo "Starting FastAPI app Divine"

# TODO: use PORT env var
cd src
exec uvicorn \
  $APP_MODULE \
  --factory \
  --host $HOST \
  --port $PORT \
  --workers $WORKERS \
  --loop uvloop \
  --http httptools \
  --log-level $LOG_LEVEL \
  --log-config divine/uvicorn_log_config.yml \
  --access-log \
  "$@"
# --access-logformat '%(t)s %(h)s "%(r)s" %(L)s %(s)s' \
# --log-config logging.yml \
# -- reload \
# %(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s"
