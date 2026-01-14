#!/usr/bin/env bash
set -euo pipefail

SAMPLE_FILE=".env.sample"
PROD_FILE=".env.prod"

if [[ ! -f "$SAMPLE_FILE" ]]; then
  echo "[FAIL] $SAMPLE_FILE not found (root standard required)."
  exit 1
fi

if [[ ! -f "$PROD_FILE" ]]; then
  echo "[FAIL] $PROD_FILE not found. Provide it before deploy."
  exit 1
fi

missing=()

# Extract keys from .env.sample (KEY=... lines, ignore comments/blank)
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ "$line" != *"="* ]] && continue

  key="${line%%=*}"
  key="$(echo "$key" | tr -d '[:space:]')"
  [[ -z "$key" ]] && continue

  if grep -qE "^${key}=" "$PROD_FILE"; then
    val="$(grep -E "^${key}=" "$PROD_FILE" | head -n 1 | cut -d= -f2-)"
    if [[ -z "$val" ]]; then
      missing+=("$key")
    fi
  else
    if [[ -z "${!key:-}" ]]; then
      missing+=("$key")
    fi
  fi
done < "$SAMPLE_FILE"

# Explicit TAG check (must exist in .env.prod or environment)
if ! grep -qE '^TAG=' "$PROD_FILE" && [[ -z "${TAG:-}" ]]; then
  missing+=("TAG")
fi

if (( ${#missing[@]} > 0 )); then
  echo "[FAIL] Missing required env keys (names only):"
  for k in "${missing[@]}"; do echo " - $k"; done
  exit 1
fi

echo "[OK] Required env keys are present (values not displayed)."
