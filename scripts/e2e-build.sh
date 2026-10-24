#!/bin/sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

NODE_DIR="/tmp/pk-node-22.23.4"
if ! node -v 2>/dev/null | grep -q "22.23.4"; then
  if [ ! -x "$NODE_DIR/bin/node" ]; then
    mkdir -p "$NODE_DIR"
    curl -fsSL "https://nodejs.org/dist/v22.23.4/node-v22.23.4-linux-x64.tar.xz" \
      | tar -xJ -C "$NODE_DIR" --strip-components=1
  fi
  export PATH="$NODE_DIR/bin:$PATH"
fi

export LANDING_API_ORIGIN="${LANDING_API_ORIGIN:-http://127.0.0.1:8000}"

pnpm --filter @photo-kruzhok/web build
pnpm --filter @photo-kruzhok/admin build
pnpm --filter @photo-kruzhok/landing build
