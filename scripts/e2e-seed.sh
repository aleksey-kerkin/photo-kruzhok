#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "${DEMO_MEMBER_PASSWORD:-}" ] || [ -z "${DEMO_LEADER_PASSWORD:-}" ]; then
  echo "DEMO_MEMBER_PASSWORD and DEMO_LEADER_PASSWORD must be set." >&2
  exit 1
fi

if docker info >/dev/null 2>&1; then
  COMPOSE="docker compose"
else
  COMPOSE="podman compose"
fi

$COMPOSE exec -T \
  -e DEMO_MEMBER_PASSWORD \
  -e DEMO_LEADER_PASSWORD \
  -e SECRET_KEY="${SECRET_KEY:-e2e-secret-key}" \
  api sh -c 'python manage.py migrate --noinput && python manage.py seed_demo'
