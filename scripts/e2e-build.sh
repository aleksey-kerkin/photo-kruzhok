#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

case "$(node -v)" in
  v22.23.1) ;;
  *)
    echo "Node $(node -v) is installed; this repo requires v22.23.1" >&2
    exit 1
    ;;
esac

export LANDING_API_ORIGIN="${LANDING_API_ORIGIN:-http://127.0.0.1:8000}"

pnpm --filter @photo-kruzhok/web build
pnpm --filter @photo-kruzhok/admin build
pnpm --filter @photo-kruzhok/landing build
