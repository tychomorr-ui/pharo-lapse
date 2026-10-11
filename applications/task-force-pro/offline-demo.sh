#!/usr/bin/env bash
# Product-specific Dimension 5 demo entry point. No product data is generated here.
set -Eeuo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../run-offline-reference-demo.sh" "task-force-pro" "$@"
