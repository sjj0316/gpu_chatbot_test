#!/usr/bin/env bash
set -euo pipefail

docker compose --env-file .env.prod -f docker-compose.prod.yml config >/dev/null
