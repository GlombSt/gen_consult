#!/bin/bash
# Linting and formatting script
# Usage: ./lint.sh [--fix]
#
# Optimizations:
# - CHECK mode: Black, isort, Flake8 run in parallel (background + wait); mypy runs after.
# - In CI (GITHUB_ACTIONS or CI): only lint changed .py files (incremental); fallback to full tree.
# - Flake8: single pass; critical codes (E9,F63,F7,F82) cause failure; warnings shown.
# - Mypy: no -j (not in mypy 1.x CLI); optional so does not fail the run.

set -o pipefail
# Don't use set -e; we check exit codes manually for parallel runs

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
    echo -e "${YELLOW}Running in FIX mode - will automatically fix issues${NC}\n"
else
    echo -e "${YELLOW}Running in CHECK mode - use --fix to automatically fix issues${NC}\n"
fi

if ! command -v black &> /dev/null || ! command -v isort &> /dev/null || ! command -v flake8 &> /dev/null; then
    echo -e "${RED}Error: Linting tools not installed${NC}"
    echo "Install with: pip install -e '.[dev]' or: uv sync --extra dev"
    exit 1
fi

# Detect CI for incremental linting
IN_CI=false
[ -n "$GITHUB_ACTIONS" ] && IN_CI=true
[ -n "$CI" ] && IN_CI=true

# Allow forcing full lint in CI (useful for timing/diagnostics)
FULL_LINT=false
[ "${FULL_LINT:-}" = "true" ] && FULL_LINT=true
[ "${CI_FULL_LINT:-}" = "true" ] && FULL_LINT=true

# Resolve list of Python files to lint (run from intentions/).
# In CI: only changed .py under app/ or tests/; fallback full tree.
get_py_targets() {
    local files=""
    if [ "$FULL_LINT" = true ]; then
        echo "app/ tests/"
        return
    fi
    if [ "$IN_CI" = true ]; then
        local base="${GITHUB_BASE_REF:-main}"
        local ref="origin/$base"
        git rev-parse --verify "$ref" &> /dev/null || ref="HEAD~1"
        files=$(git diff --name-only "$ref"...HEAD 2>/dev/null | grep '\.py$' || true)
        if [ -n "$files" ]; then
            # Paths may be intentions/... when repo root is parent; we run from intentions/
            files=$(echo "$files" | sed 's|^intentions/||' | grep -E '^(app|tests)/' || true)
        fi
    fi
    if [ -z "$files" ]; then
        echo "app/ tests/"
        return
    fi
    echo "$files" | tr '\n' ' '
}

# Get target argument for tools: either "app/ tests/" or a list of filenames
TARGETS=$(get_py_targets)
if [ "$TARGETS" = "app/ tests/" ]; then
    USE_FULL_TREE=true
    BLACK_ARGS="app/ tests/"
    ISORT_ARGS="app/ tests/"
    FLAKE8_ARGS="app/ tests/"
else
    USE_FULL_TREE=false
    BLACK_ARGS=$TARGETS
    ISORT_ARGS=$TARGETS
    FLAKE8_ARGS=$TARGETS
fi

echo "==============================================="
echo "  Running Linting Checks"
echo "==============================================="
if [ "$USE_FULL_TREE" = false ]; then
    echo -e "${YELLOW}Incremental mode (CI): linting changed .py files only${NC}"
fi
echo ""

print_section() {
    echo ""
    echo "-----------------------------------------------"
    echo "  $1"
    echo "-----------------------------------------------"
}

FAILED=0

# ---------- FIX mode: sequential (tools modify files) ----------
if [ "$FIX_MODE" = true ]; then
    print_section "1. Black (Code Formatting)"
    if black $BLACK_ARGS; then
        echo -e "${GREEN}✓ Black formatting applied${NC}"
    else
        echo -e "${RED}✗ Black formatting failed${NC}"
        FAILED=1
    fi

    print_section "2. isort (Import Sorting)"
    if isort $ISORT_ARGS; then
        echo -e "${GREEN}✓ Import sorting applied${NC}"
    else
        echo -e "${RED}✗ Import sorting failed${NC}"
        FAILED=1
    fi

    # Optional: re-run black after isort (they can interact)
    print_section "2b. Black (re-check after isort)"
    if black $BLACK_ARGS; then
        echo -e "${GREEN}✓ Black still ok${NC}"
    else
        echo -e "${RED}✗ Black needs another pass${NC}"
        FAILED=1
    fi

    # 3. Flake8 - Critical errors only
    print_section "3. Flake8 (Critical Errors)"
    if flake8 $FLAKE8_ARGS --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1; then
        echo -e "${GREEN}✓ No critical flake8 errors${NC}"
    else
        echo -e "${RED}✗ Critical flake8 errors found${NC}"
        FAILED=1
    fi

    # 4. Flake8 - Full check (warnings)
    print_section "4. Flake8 (Full Check - Warnings)"
    FLAKE8_OUTPUT=$(flake8 $FLAKE8_ARGS --count --max-complexity=10 --max-line-length=127 --statistics 2>&1 || true)
    if [ -z "$FLAKE8_OUTPUT" ] || echo "$FLAKE8_OUTPUT" | grep -q "^0"; then
        echo -e "${GREEN}✓ No flake8 warnings${NC}"
    else
        echo "$FLAKE8_OUTPUT"
        echo -e "${YELLOW}⚠ Flake8 warnings found (non-critical)${NC}"
    fi

    # 5. mypy - Type Checking (optional; -j auto when supported; default: incremental via changed files)
    print_section "5. mypy (Type Checking - Optional)"
    if command -v mypy &> /dev/null; then
        MYPY_TARGETS="app/"
        BASE="${GITHUB_BASE_REF:-main}"
        REF="origin/$BASE"
        git rev-parse --verify "$REF" &> /dev/null || REF="HEAD~1"
        CHANGED=$(git diff --name-only "$REF"...HEAD 2>/dev/null | grep '\.py$' | sed 's|^intentions/||' | grep -E '^app/' || true)
        if [ -n "$CHANGED" ]; then
            MYPY_TARGETS=$(echo "$CHANGED" | tr '\n' ' ')
        fi
        MYPY_OUT=$(mypy $MYPY_TARGETS --ignore-missing-imports -j auto 2>&1)
        MYPY_RC=$?
        if [ $MYPY_RC -eq 2 ]; then
            MYPY_OUT=$(mypy $MYPY_TARGETS --ignore-missing-imports 2>&1)
            MYPY_RC=$?
        fi
        echo "$MYPY_OUT"
        if [ $MYPY_RC -eq 0 ]; then
            echo -e "${GREEN}✓ Type checking passed${NC}"
        else
            echo -e "${YELLOW}⚠ Type checking issues found (optional)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ mypy not installed - skipping${NC}"
    fi
fi

# ---------- CHECK mode: Black, isort, Flake8 in parallel ----------
if [ "$FIX_MODE" = false ]; then
    print_section "1–3. Black, isort, Flake8 (parallel)"
    rm -f /tmp/lint_black_rc /tmp/lint_isort_rc /tmp/lint_flake8.out

    ( black --check $BLACK_ARGS > /tmp/lint_black.out 2>&1; echo $? > /tmp/lint_black_rc ) &
    ( isort --check-only $ISORT_ARGS > /tmp/lint_isort.out 2>&1; echo $? > /tmp/lint_isort_rc ) &
    ( flake8 $FLAKE8_ARGS --count --max-complexity=10 --max-line-length=127 --show-source --statistics > /tmp/lint_flake8.out 2>&1 ) &
    wait

    BLACK_FAIL=0
    [ -f /tmp/lint_black_rc ] && [ "$(cat /tmp/lint_black_rc)" != "0" ] && BLACK_FAIL=1
    ISORT_FAIL=0
    [ -f /tmp/lint_isort_rc ] && [ "$(cat /tmp/lint_isort_rc)" != "0" ] && ISORT_FAIL=1
    FLAKE8_OUTPUT=$(cat /tmp/lint_flake8.out 2>/dev/null || true)
    FLAKE8_FAIL=0
    echo "$FLAKE8_OUTPUT" | grep -qE ':\s*(E9|F63|F7|F82)\s' && FLAKE8_FAIL=1

    cat /tmp/lint_black.out 2>/dev/null || true
    if [ $BLACK_FAIL -eq 0 ]; then
        echo -e "${GREEN}✓ Black check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Black formatting issues. Run './lint.sh --fix' to fix${NC}"
        FAILED=1
    fi
    cat /tmp/lint_isort.out 2>/dev/null || true
    if [ $ISORT_FAIL -eq 0 ]; then
        echo -e "${GREEN}✓ isort check passed${NC}"
    else
        echo -e "${YELLOW}⚠ isort issues. Run './lint.sh --fix' to fix${NC}"
        FAILED=1
    fi
    if [ $FLAKE8_FAIL -eq 1 ]; then
        echo "$FLAKE8_OUTPUT"
        echo -e "${RED}✗ Critical flake8 errors (E9,F63,F7,F82) found${NC}"
        FAILED=1
    elif [ -n "$FLAKE8_OUTPUT" ] && ! echo "$FLAKE8_OUTPUT" | grep -q "^0"; then
        echo "$FLAKE8_OUTPUT"
        echo -e "${YELLOW}⚠ Flake8 warnings (non-critical)${NC}"
    else
        echo -e "${GREEN}✓ Flake8 passed (no critical errors)${NC}"
    fi

    # Mypy: no -j (not supported in mypy 1.x CLI); runs after parallel tools
    print_section "4. mypy (Type Checking - Optional)"
    if command -v mypy &> /dev/null; then
        if mypy app/ --ignore-missing-imports; then
            echo -e "${GREEN}✓ Type checking passed${NC}"
        else
            echo -e "${YELLOW}⚠ Type checking issues found (optional)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ mypy not installed - skipping${NC}"
    fi
fi

echo ""
echo "==============================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All linting checks passed!${NC}"
    echo "==============================================="
    exit 0
else
    echo -e "${RED}✗ Some linting checks failed${NC}"
    [ "$FIX_MODE" = false ] && echo "" && echo "Run './lint.sh --fix' to automatically fix some issues"
    echo "==============================================="
    exit 1
fi
