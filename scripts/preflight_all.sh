#!/usr/bin/env bash
set -euo pipefail

bash scripts/preflight_env.sh
bash scripts/preflight_compose.sh
