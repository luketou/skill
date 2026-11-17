#!/usr/bin/env bash
# ==============================================================================
# One-click installer for Slurm Aliases
# Appends sourcing of slurm_aliases.sh to ~/.bashrc if not already present.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_FILE="${SCRIPT_DIR}/slurm_aliases.sh"
BASHRC="${HOME}/.bashrc"
SOURCE_LINE="[ -f \"${TARGET_FILE}\" ] && source \"${TARGET_FILE}\""

if [ ! -f "${TARGET_FILE}" ]; then
    echo "Error: ${TARGET_FILE} not found." >&2
    exit 1
fi

if [ ! -f "${BASHRC}" ]; then
    touch "${BASHRC}"
fi

if grep -Fxq "${SOURCE_LINE}" "${BASHRC}" 2>/dev/null; then
    echo "Slurm aliases already configured in ${BASHRC}"
else
    echo "" >> "${BASHRC}"
    echo "# Slurm aliases (q, qs, pbs)" >> "${BASHRC}"
    echo "${SOURCE_LINE}" >> "${BASHRC}"
    echo "Successfully added slurm aliases to ${BASHRC}"
fi

echo ""
echo "To activate immediately in your current terminal, run:"
echo "    source ~/.bashrc"
