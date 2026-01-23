#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

DOCKER="${DOCKER:-docker}"
PANDOC_IMAGE="${PANDOC_IMAGE:-pandoc/core:3.1.13}"
# Optional override (useful if an image lacks native support on your host):
#   DOCKER_PLATFORM=linux/amd64 ./export.sh
DOCKER_PLATFORM="${DOCKER_PLATFORM:-}"

DIR="business/Gründungszuschuss"
OUTDIR="$DIR/output"
MD="$OUTDIR/business_plan.md"
REF="$OUTDIR/reference.docx"
OUT_DOCX="$OUTDIR/business_plan.docx"
TOC_FILTER_HOST="${REPO_ROOT}/${OUTDIR}/_pandoc_unlist_title.lua"

if [[ ! -f "${REPO_ROOT}/${MD}" ]]; then
  echo "ERROR: Missing input Markdown: ${MD}" >&2
  echo "Fix: Put your source of truth here, then rerun:" >&2
  echo "  ${MD}" >&2
  exit 1
fi

if [[ ! -f "${REPO_ROOT}/${REF}" ]]; then
  echo "ERROR: Missing Word reference template: ${REF}" >&2
  echo "Fix: Put your template here (no fallback paths are used):" >&2
  echo "  ${REF}" >&2
  exit 1
fi

PLATFORM_ARGS=()
if [[ -n "${DOCKER_PLATFORM}" ]]; then
  PLATFORM_ARGS=( --platform "${DOCKER_PLATFORM}" )
else
  # Auto-pick platform based on the locally available image arch to avoid warnings
  # like "requested image's platform (linux/amd64) does not match detected host".
  IMAGE_ARCH="$("${DOCKER}" image inspect "${PANDOC_IMAGE}" --format '{{.Architecture}}' 2>/dev/null || true)"
  case "${IMAGE_ARCH}" in
    amd64) PLATFORM_ARGS=( --platform linux/amd64 ) ;;
    arm64) PLATFORM_ARGS=( --platform linux/arm64/v8 ) ;;
    "") : ;; # unknown / not pulled yet
    *) : ;;  # unexpected
  esac
fi

# We want a 2-level TOC of the document content (# + ##).
# Pandoc's toc-depth counts absolute heading levels, so we set toc-depth=2 and
# exclude the first level-1 header (the document title) from the TOC.
cat > "${TOC_FILTER_HOST}" <<'LUA'
local seen_title = false

function Header(el)
  if el.level == 1 and not seen_title then
    seen_title = true
    el.classes:insert('unlisted') -- exclude from TOC
    return el
  end
  return nil
end
LUA

cleanup() {
  rm -f "${TOC_FILTER_HOST}" || true
}
trap cleanup EXIT

echo "Generating DOCX (pandoc): ${OUT_DOCX}"
"${DOCKER}" run --rm ${PLATFORM_ARGS[@]+"${PLATFORM_ARGS[@]}"} \
  -v "${REPO_ROOT}/${DIR}:/proj" \
  -w /proj \
  "${PANDOC_IMAGE}" \
  "/proj/output/business_plan.md" \
    --from=markdown \
    --toc --toc-depth=2 \
    --lua-filter="/proj/output/_pandoc_unlist_title.lua" \
    --reference-doc="/proj/output/reference.docx" \
    -o "/proj/output/business_plan.docx"

echo "Done."

