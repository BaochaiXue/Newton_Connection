#!/usr/bin/env bash
set -euo pipefail

# Fill these before use.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
OUT_DIR="${ROOT}/tmp/<experiment_name>"

mkdir -p "${OUT_DIR}"

echo "Replace this template command with the canonical experiment invocation."
