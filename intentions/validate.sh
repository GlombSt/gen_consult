#!/bin/bash
# Validation script for coding agents
# Usage: ./validate.sh [--skip-push]
# 
# This script validates that all code quality checks pass before marking work as complete.
# It should be run before the agent reports completion.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SKIP_PUSH=false

# Parse arguments
if [ "$1" == "--skip-push" ]; then
    SKIP_PUSH=true
fi

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}  Agent Validation Checklist${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

FAILED=0

# Check if we're in the right directory
if [ ! -f "lint.sh" ]; then
    echo -e "${RED}✗ Error: Must run from intentions/ directory${NC}"
    exit 1
fi

# 1. Check git status
echo -e "${BLUE}1. Checking git status...${NC}"
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${YELLOW}⚠ Warning: Uncommitted changes detected${NC}"
    echo "   Run: git add . && git commit -m 'Your message'"
    FAILED=1
else
    echo -e "${GREEN}✓ No uncommitted changes${NC}"
fi

# 2. Check if code is pushed
if [ "$SKIP_PUSH" = false ]; then
    echo -e "${BLUE}2. Checking if code is pushed to remote...${NC}"
    CURRENT_BRANCH=$(git branch --show-current)
    if [ -z "$CURRENT_BRANCH" ]; then
        echo -e "${RED}✗ Error: Not on a branch (detached HEAD)${NC}"
        FAILED=1
    else
        LOCAL=$(git rev-parse @)
        REMOTE=$(git rev-parse @{u} 2>/dev/null || echo "")
        if [ -z "$REMOTE" ]; then
            echo -e "${YELLOW}⚠ Warning: Branch '$CURRENT_BRANCH' has no upstream${NC}"
            echo "   Run: git push -u origin $CURRENT_BRANCH"
            FAILED=1
        elif [ "$LOCAL" != "$REMOTE" ]; then
            echo -e "${YELLOW}⚠ Warning: Local branch is ahead of remote${NC}"
            echo "   Run: git push"
            FAILED=1
        else
            echo -e "${GREEN}✓ Code is pushed to remote branch: $CURRENT_BRANCH${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Skipping push check (--skip-push flag)${NC}"
fi

# 3. Run linting
echo -e "${BLUE}3. Running linting checks...${NC}"
if ./lint.sh; then
    echo -e "${GREEN}✓ Linting passed${NC}"
else
    echo -e "${RED}✗ Linting failed${NC}"
    echo "   Run: ./lint.sh --fix"
    FAILED=1
fi

# 4. Run tests
echo -e "${BLUE}4. Running tests...${NC}"
if pytest --cov=app --cov-fail-under=80 -v; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    FAILED=1
fi

# Summary
echo ""
echo -e "${BLUE}===============================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All local validation checks passed!${NC}"
    echo -e "${BLUE}===============================================${NC}"
    echo ""
    if [ "$SKIP_PUSH" = false ]; then
        CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
        echo -e "${YELLOW}⚠ IMPORTANT: Verify CI status on GitHub${NC}"
        echo "   Branch: $CURRENT_BRANCH"
        echo "   Check: https://github.com/OWNER/REPO/actions"
        echo ""
        echo "   The agent MUST verify CI is GREEN before marking work complete."
    fi
    exit 0
else
    echo -e "${RED}✗ Validation failed${NC}"
    echo -e "${BLUE}===============================================${NC}"
    echo ""
    echo "Fix the issues above before marking work as complete."
    exit 1
fi

