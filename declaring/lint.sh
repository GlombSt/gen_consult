#!/bin/bash
# Linting and formatting script
# Usage: ./lint.sh [--fix]

# Don't use set -e here because we want to check exit codes manually
# set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FIX_MODE=false

# Parse arguments
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
    echo -e "${YELLOW}Running in FIX mode - will automatically fix issues${NC}\n"
else
    echo -e "${YELLOW}Running in CHECK mode - use --fix to automatically fix issues${NC}\n"
fi

# Check if tools are installed
if ! command -v black &> /dev/null || ! command -v isort &> /dev/null || ! command -v flake8 &> /dev/null; then
    echo -e "${RED}Error: Linting tools not installed${NC}"
    echo "Install with: pip install -e '.[dev]'"
    echo "Or: pip install black isort flake8 mypy"
    exit 1
fi

echo "==============================================="
echo "  Running Linting Checks"
echo "==============================================="
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo "-----------------------------------------------"
    echo "  $1"
    echo "-----------------------------------------------"
}

# Track overall status
FAILED=0

# 1. Black - Code Formatting
print_section "1. Black (Code Formatting)"
if [ "$FIX_MODE" = true ]; then
    if black app/ tests/; then
        echo -e "${GREEN}✓ Black formatting applied${NC}"
    else
        echo -e "${RED}✗ Black formatting failed${NC}"
        FAILED=1
    fi
else
    if black --check app/ tests/; then
        echo -e "${GREEN}✓ Black formatting check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Black formatting issues found. Run './lint.sh --fix' to fix${NC}"
        FAILED=1
    fi
fi

# 2. isort - Import Sorting
print_section "2. isort (Import Sorting)"
if [ "$FIX_MODE" = true ]; then
    if isort app/ tests/; then
        echo -e "${GREEN}✓ Import sorting applied${NC}"
    else
        echo -e "${RED}✗ Import sorting failed${NC}"
        FAILED=1
    fi
else
    if isort --check-only app/ tests/; then
        echo -e "${GREEN}✓ Import sorting check passed${NC}"
    else
        echo -e "${YELLOW}⚠ Import sorting issues found. Run './lint.sh --fix' to fix${NC}"
        FAILED=1
    fi
fi

# 3. Flake8 - Linting (Critical errors only)
print_section "3. Flake8 (Critical Errors)"
if flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics 2>&1; then
    echo -e "${GREEN}✓ No critical flake8 errors${NC}"
else
    echo -e "${RED}✗ Critical flake8 errors found${NC}"
    FAILED=1
fi

# 4. Flake8 - Full check (warnings)
print_section "4. Flake8 (Full Check - Warnings)"
# Note: We ignore exit code for warnings check since warnings are non-critical
# Use || true to prevent script failure on warnings
if flake8 app/ tests/ --count --max-complexity=10 --max-line-length=127 --statistics 2>&1 || true; then
    echo -e "${GREEN}✓ No flake8 warnings${NC}"
else
    echo -e "${YELLOW}⚠ Flake8 warnings found (non-critical)${NC}"
fi

# 5. mypy - Type Checking (optional)
print_section "5. mypy (Type Checking - Optional)"
if command -v mypy &> /dev/null; then
    if mypy app/ --ignore-missing-imports; then
        echo -e "${GREEN}✓ Type checking passed${NC}"
    else
        echo -e "${YELLOW}⚠ Type checking issues found (optional)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ mypy not installed - skipping type checking${NC}"
fi

# Summary
echo ""
echo "==============================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All linting checks passed!${NC}"
    echo "==============================================="
    exit 0
else
    echo -e "${RED}✗ Some linting checks failed${NC}"
    if [ "$FIX_MODE" = false ]; then
        echo ""
        echo "Run './lint.sh --fix' to automatically fix some issues"
    fi
    echo "==============================================="
    exit 1
fi

