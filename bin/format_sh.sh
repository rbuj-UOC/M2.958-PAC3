#!/usr/bin/env bash
set -euo pipefail

# Script per a donar format a tots els fitxers .sh del projecte amb shfmt.

# S'ha d'executar des de la carpeta arrel del projecte.
if [[ ! -f "bin/format_sh.sh" ]]; then
	echo "Aquest script s'ha d'executar des de la carpeta arrel del projecte." >&2
	exit 1
fi

# Comprova si shfmt està instal·lat o si la variable d'entorn SHFMT està definida.
SHFMT_PATH="${SHFMT:-shfmt}"
if ! command -v "${SHFMT_PATH}" >/dev/null 2>&1; then
	echo "shfmt not found. Install it or set SHFMT environment variable to its path." >&2
	exit 1
fi

echo "Finding .sh files (excluding .conda, data, img) and formatting with ${SHFMT_PATH}..."

find . -type f -name '*.sh' \
	-not -path './.conda/*' \
	-not -path './data/*' \
	-not -path './img/*' \
	-print0 | xargs -0 "${SHFMT_PATH}" -w -- || true

echo "Done."
