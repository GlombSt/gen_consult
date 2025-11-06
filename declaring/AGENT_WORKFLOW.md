# Agent Development Workflow

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** MANDATORY - All coding agents must follow this workflow  
**Audience:** AI Coding Agents (Cursor, Claude Code, etc.)

---

## Overview

This document defines the **mandatory completion criteria** for coding agents working on the `declaring/` backend. Agents must NOT mark work as complete until ALL criteria are met.

## Critical Completion Criteria

An agent MUST NOT say work is finished until:

1. ✅ **All code changes are committed to git**
2. ✅ **All code changes are pushed to a branch**
3. ✅ **Local linting passes** (`./lint.sh` exits with code 0)
4. ✅ **Local tests pass** (`pytest` exits with code 0)
5. ✅ **CI GitHub Actions workflow is GREEN** (all checks pass)
6. ✅ **No linting errors in CI**

---

## Step-by-Step Agent Workflow

### Phase 1: Development

1. **Understand the task**
   - Read relevant documentation (CLAUDE.md, DEVELOPMENT_STANDARDS.md)
   - Understand existing code structure
   - Plan the approach

2. **Make code changes**
   - Follow TDD principles (write tests first)
   - Follow architecture standards
   - Make incremental changes

3. **Run local validation frequently**
   ```bash
   cd declaring
   ./lint.sh --fix  # Auto-fix formatting issues
   ./lint.sh        # Verify all linting passes
   pytest           # Verify all tests pass
   ```

### Phase 2: Pre-Commit Validation

**MANDATORY:** Before committing, run:

```bash
cd declaring

# Step 1: Auto-fix formatting issues
./lint.sh --fix

# Step 2: Verify all linting passes (MUST exit 0)
./lint.sh

# Step 3: Verify all tests pass (MUST exit 0)
pytest --cov=app --cov-fail-under=80 -v
```

**If any step fails, fix the issues and repeat.**

### Phase 3: Commit and Push

1. **Stage changes**
   ```bash
   git add .
   ```

2. **Commit with descriptive message**
   ```bash
   git commit -m "Descriptive commit message"
   ```

3. **Push to branch**
   ```bash
   # If working on a new branch
   git push -u origin branch-name
   
   # If branch already exists
   git push
   ```

**CRITICAL:** The agent MUST push code to a branch. Do NOT mark work as complete without pushing.

### Phase 4: CI Verification

**MANDATORY:** After pushing, verify CI passes:

1. **Check GitHub Actions status**
   - Navigate to: `https://github.com/OWNER/REPO/actions`
   - Find the workflow run for your branch
   - Verify all jobs are GREEN (✅)

2. **Verify specific checks passed:**
   - ✅ Lint and Test Backend job completed successfully
   - ✅ All linting checks passed (Black, isort, Flake8)
   - ✅ All tests passed
   - ✅ Coverage requirements met (≥80%)

3. **If CI fails:**
   - Read the error messages
   - Fix the issues locally
   - Re-run local validation (`./lint.sh` and `pytest`)
   - Commit fixes
   - Push again
   - Wait for CI to pass

**CRITICAL:** The agent MUST wait for CI to pass before marking work as complete.

---

## Agent Completion Checklist

Before saying "I'm finished" or "The work is complete", verify:

- [ ] All code changes are committed to git
- [ ] All code changes are pushed to a branch
- [ ] `./lint.sh` passes locally (exit code 0)
- [ ] `pytest` passes locally (exit code 0)
- [ ] GitHub Actions workflow is GREEN
- [ ] All CI checks passed (linting, tests, coverage)
- [ ] No linting errors in CI logs

**If ANY item is unchecked, the work is NOT complete.**

---

## Common Issues and Solutions

### Issue: Linting fails in CI but passes locally

**Cause:** CI uses different Python version or dependencies

**Solution:**
1. Ensure you're using the same Python version (3.11)
2. Install dev dependencies: `pip install -r requirements-dev.txt`
3. Run `./lint.sh` (not just individual tools)
4. Check CI logs for specific error messages

### Issue: Tests pass locally but fail in CI

**Cause:** Environment differences, missing dependencies, or test isolation issues

**Solution:**
1. Run tests in a clean environment
2. Check CI logs for specific test failures
3. Ensure all dependencies are in `requirements.txt` or `requirements-dev.txt`
4. Verify test fixtures and mocks work in CI environment

### Issue: CI doesn't run

**Cause:** Workflow triggers not configured or branch not pushed

**Solution:**
1. Verify code is pushed to a branch (not just committed locally)
2. Check that files changed are in `declaring/` directory
3. Verify workflow file exists: `.github/workflows/backend-ci.yml`

---

## Quick Reference Commands

```bash
# Full validation (run before committing)
cd declaring
./lint.sh --fix && ./lint.sh && pytest

# Check git status
git status

# Push to branch
git push origin branch-name

# Check CI status (after pushing)
# Visit: https://github.com/OWNER/REPO/actions
```

---

## Integration with Cursor/Other Agents

When working as a coding agent:

1. **Always run local validation** before suggesting completion
2. **Always push code** to a branch (don't just commit locally)
3. **Always check CI status** before marking work complete
4. **Provide the branch name** and CI status URL when reporting completion
5. **If CI fails, fix it** before reporting completion

**Example completion message:**
```
✅ Work complete!

- Code committed and pushed to branch: feature/add-intent-validation
- Local linting: ✅ Passed
- Local tests: ✅ Passed
- CI Status: ✅ All checks passing
- CI URL: https://github.com/owner/repo/actions/runs/123456

All criteria met. Ready for review.
```

---

## Related Documentation

- [DEVELOPMENT_STANDARDS.md](./DEVELOPMENT_STANDARDS.md) - General development workflow
- [LINTING_STANDARDS.md](./LINTING_STANDARDS.md) - Linting requirements
- [TESTING_STANDARDS.md](./TESTING_STANDARDS.md) - Testing requirements
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Code organization rules

