#!/usr/bin/env bash
set -euo pipefail

# Regenerate LLM-friendly exports for business-case-sheet.xlsx
#
# Usage:
#   ./business/Gründungszuschuss/export_business_case_sheet.sh
#   ./business/Gründungszuschuss/export_business_case_sheet.sh --clean
#
# Env overrides:
#   PYTHON_BIN=python3 ./business/Gründungszuschuss/export_business_case_sheet.sh

usage() {
  cat <<'USAGE'
Regenerate LLM-friendly exports for business-case-sheet.xlsx.

Usage:
  export_business_case_sheet.sh [--clean] [--help]

Options:
  --clean   Delete the export directory before regenerating it
  --help    Show this help

Env:
  PYTHON_BIN  Python executable to use (default: python3)
USAGE
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

CLEAN=false
if [[ "${1:-}" == "--clean" ]]; then
  CLEAN=true
  shift
fi

if [[ $# -ne 0 ]]; then
  echo "ERROR: Unexpected arguments: $*" >&2
  usage >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

XLSX_REL="business/Gründungszuschuss/business-case-sheet.xlsx"
OUT_REL="business/Gründungszuschuss/llm_exports/business-case-sheet"
TOOL_REL="business/tools/xlsx_to_llm.py"

XLSX="${REPO_ROOT}/${XLSX_REL}"
OUTDIR="${REPO_ROOT}/${OUT_REL}"
TOOL="${REPO_ROOT}/${TOOL_REL}"

if [[ ! -f "${XLSX}" ]]; then
  echo "ERROR: Missing XLSX: ${XLSX_REL}" >&2
  exit 1
fi

if [[ ! -f "${TOOL}" ]]; then
  echo "ERROR: Missing exporter script: ${TOOL_REL}" >&2
  exit 1
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "ERROR: Python not found: ${PYTHON_BIN}" >&2
  echo "Fix: install python3 or run with PYTHON_BIN=/path/to/python3" >&2
  exit 1
fi

if [[ "${CLEAN}" == "true" && -d "${OUTDIR}" ]]; then
  # Safety check: only allow deleting the expected directory.
  case "${OUTDIR}" in
    "${REPO_ROOT}/business/Gründungszuschuss/llm_exports/business-case-sheet") ;;
    *)
      echo "ERROR: Refusing to delete unexpected OUTDIR: ${OUTDIR}" >&2
      exit 1
      ;;
  esac
  rm -rf "${OUTDIR}"
fi

mkdir -p "${OUTDIR}"

echo "Exporting XLSX → LLM artifacts"
echo "- XLSX:   ${XLSX_REL}"
echo "- OUT:    ${OUT_REL}"
echo "- Python: ${PYTHON_BIN}"

# Keep pycache out of the repo tree (matches plan.md recommendation).
PYTHONPYCACHEPREFIX="${REPO_ROOT}/.pycache" \
  "${PYTHON_BIN}" "${TOOL}" "${XLSX}" --out "${OUTDIR}"

echo "Done."
