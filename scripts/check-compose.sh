#!/bin/sh
set -eu
docker compose config | grep -q "published: \"8000\""
docker compose config | grep -q "published: \"5432\""
docker compose config | grep -q "published: \"9000\""
