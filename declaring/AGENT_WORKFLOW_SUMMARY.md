# Agent Workflow Improvements - Summary

**Date:** January 2025  
**Purpose:** Improve development flow for coding agents to prevent CI linting errors

---

## Problem Statement

The development flow in `declaring/` did not work well with coding agents like Cursor:
- Agents would mark work as complete without pushing to branches
- Agents would not verify CI status before completion
- CI would fail with linting errors that weren't caught locally
- CI workflow only ran on `main` and `develop` branches (not feature branches)
- CI only ran partial linting (flake8 only, not full `lint.sh` script)

---

## Solutions Implemented

### 1. Updated CI Workflow (`.github/workflows/backend-ci.yml`)

**Changes:**
- ✅ **Runs on ALL branches** (removed branch restriction)
- ✅ **Uses full `lint.sh` script** (Black, isort, Flake8 - not just flake8)
- ✅ **Installs dev dependencies** (`requirements-dev.txt`)
- ✅ **Better caching** (uses pip cache from setup-python action)
- ✅ **Clearer job name** ("Lint and Test Backend")

**Before:**
- Only ran on `main` and `develop` branches
- Only ran flake8 (missing Black and isort)
- Manually installed individual packages

**After:**
- Runs on any branch when `declaring/**` files change
- Runs complete `./lint.sh` script (all linting tools)
- Installs from `requirements-dev.txt` (all dev dependencies)

### 2. Created Agent Workflow Document (`AGENT_WORKFLOW.md`)

**Purpose:** Mandatory workflow for coding agents with clear completion criteria

**Key Sections:**
- **Critical Completion Criteria** - 6 mandatory checks before completion
- **Step-by-Step Workflow** - Phase 1 (Development) → Phase 2 (Pre-Commit) → Phase 3 (Commit/Push) → Phase 4 (CI Verification)
- **Agent Completion Checklist** - Checkbox list agents must verify
- **Common Issues and Solutions** - Troubleshooting guide
- **Integration with Cursor/Other Agents** - Specific guidance for AI agents

**Completion Criteria:**
1. ✅ All code committed to git
2. ✅ All code pushed to a branch
3. ✅ Local linting passes (`./lint.sh` exits 0)
4. ✅ Local tests pass (`pytest` exits 0)
5. ✅ CI GitHub Actions workflow is GREEN
6. ✅ No linting errors in CI

### 3. Updated Development Standards (`DEVELOPMENT_STANDARDS.md`)

**Changes:**
- Added **Phase e: Commit and Push** - Mandatory push requirement
- Added **Phase f: Verify CI Passes** - Mandatory CI verification
- Added **Section 4: Agent-Specific Workflow** - References `AGENT_WORKFLOW.md`

**New Requirements:**
- Code MUST be pushed to a branch (not just committed locally)
- Do NOT mark work as complete until CI passes
- Agents must read `AGENT_WORKFLOW.md` before starting work

### 4. Created Validation Script (`validate.sh`)

**Purpose:** Automated validation script agents can run before completion

**Features:**
- Checks git status (uncommitted changes)
- Checks if code is pushed to remote
- Runs linting (`./lint.sh`)
- Runs tests (`pytest`)
- Provides clear error messages
- Exit code 0 = all checks pass, 1 = validation failed

**Usage:**
```bash
cd declaring
./validate.sh        # Full validation including push check
./validate.sh --skip-push  # Skip push check (for local validation only)
```

### 5. Updated Main Documentation (`CLAUDE.md`)

**Changes:**
- Added `AGENT_WORKFLOW.md` to "Important Reference Files"
- Added principle #10: "Complete workflow - MUST push code and verify CI passes"

---

## How Agents Should Use This

### Before Starting Work

1. Read `declaring/AGENT_WORKFLOW.md`
2. Read `declaring/DEVELOPMENT_STANDARDS.md`

### During Development

1. Make code changes
2. Run `./lint.sh --fix` frequently
3. Run `./lint.sh` to verify
4. Run `pytest` to verify tests pass

### Before Completion

1. **Run validation script:**
   ```bash
   cd declaring
   ./validate.sh
   ```

2. **If validation passes, push code:**
   ```bash
   git add .
   git commit -m "Descriptive message"
   git push origin branch-name
   ```

3. **Verify CI passes:**
   - Check GitHub Actions: `https://github.com/OWNER/REPO/actions`
   - Verify all checks are GREEN (✅)
   - If CI fails, fix issues and push again

4. **Only mark work complete when:**
   - ✅ All code pushed to branch
   - ✅ Local validation passed
   - ✅ CI is GREEN
   - ✅ All CI checks passed

---

## Benefits

1. **Prevents CI failures** - Full linting runs locally and in CI
2. **Catches issues early** - Validation script catches problems before push
3. **Clear completion criteria** - Agents know exactly when work is done
4. **Works on all branches** - CI runs on feature branches, not just main/develop
5. **Consistent tooling** - CI uses same `lint.sh` script as local development

---

## Testing the Changes

### Test CI Workflow

1. Create a feature branch:
   ```bash
   git checkout -b test/agent-workflow
   ```

2. Make a small change (e.g., add a comment)

3. Push to branch:
   ```bash
   git add .
   git commit -m "Test: Agent workflow improvements"
   git push origin test/agent-workflow
   ```

4. Verify CI runs:
   - Go to GitHub Actions tab
   - Find workflow run for your branch
   - Verify it runs "Lint and Test Backend" job
   - Verify all checks pass

### Test Validation Script

1. Run validation:
   ```bash
   cd declaring
   ./validate.sh
   ```

2. Should pass if:
   - No uncommitted changes
   - Code is pushed to remote
   - Linting passes
   - Tests pass

---

## Files Changed

1. `.github/workflows/backend-ci.yml` - Updated CI workflow
2. `declaring/AGENT_WORKFLOW.md` - **NEW** - Agent workflow document
3. `declaring/DEVELOPMENT_STANDARDS.md` - Updated with agent workflow
4. `declaring/validate.sh` - **NEW** - Validation script
5. `CLAUDE.md` - Updated to reference agent workflow

---

## Next Steps

1. **Test the changes** - Create a test branch and verify CI runs
2. **Update agent instructions** - Ensure agents read `AGENT_WORKFLOW.md`
3. **Monitor CI** - Watch for any issues with the new workflow
4. **Iterate** - Adjust based on agent feedback

---

## Questions or Issues?

If you encounter issues:
1. Check `AGENT_WORKFLOW.md` - "Common Issues and Solutions" section
2. Review CI logs - Look for specific error messages
3. Run `./validate.sh` locally - Catch issues before pushing

