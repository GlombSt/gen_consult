# Linting Standards

**Version:** 1.0
**Last Updated:** December 2025
**Status:** MANDATORY - All code must pass linting before merging
**Audience:** Experts familiar with Python linting tools

For detailed examples and explanations, see [LINTING_GUIDE.md](./LINTING_GUIDE.md)

**Related Documentation:**
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Code organization rules

---

## Required Tools

**MUST** use the following linting tools:

| Tool | Purpose | Auto-fix Available | Required |
|------|---------|-------------------|----------|
| **Black** | Code formatting (PEP 8 compliance) | ✅ Yes | ✅ Mandatory |
| **isort** | Import organization and sorting | ✅ Yes | ✅ Mandatory |
| **Flake8** | Code quality and style checks | ❌ Manual | ✅ Mandatory |
| **mypy** | Static type checking | ❌ Manual | ⚠️ Recommended |

All tools **MUST** pass before code can be merged.

---

## Configuration Requirements

**MUST** configure all linting tools in `pyproject.toml`:

### Black Configuration

```toml
[tool.black]
line-length = 127
target-version = ['py311', 'py312', 'py313']
exclude = ['.venv', 'venv', 'htmlcov', '__pycache__']
```

### isort Configuration

```toml
[tool.isort]
profile = "black"
line_length = 127
known_first_party = ["app", "tests"]
```

### Flake8 Configuration

```toml
[tool.flake8]
max-line-length = 127
max-complexity = 10
```

---

## Linting Rules

### Code Formatting (Black)

**MUST:**
- ✅ Use Black for all Python files
- ✅ Maximum line length: **127 characters**
- ✅ Use 4 spaces for indentation
- ✅ Use double quotes for strings
- ✅ All code **MUST** pass `black --check`

**Forbidden:**
- ❌ Manual formatting (Black handles it)
- ❌ Disabling Black for specific files without team approval
- ❌ Line length > 127 characters

### Import Organization (isort)

**MUST:**
- ✅ Organize imports in this order:
  1. Future imports (`from __future__ import ...`)
  2. Standard library imports
  3. Third-party imports
  4. First-party imports (`from app import ...`)
  5. Local folder imports (`from . import ...`)
- ✅ Sort imports alphabetically within each section
- ✅ All imports **MUST** pass `isort --check-only`

**Forbidden:**
- ❌ Mixing import styles (use consistent `from` vs `import`)
- ❌ Out-of-order imports

### Code Quality (Flake8)

**MUST:**
- ✅ Maximum cyclomatic complexity: **10**
- ✅ Maximum line length: **127 characters**
- ✅ Fix all critical errors (E9, F63, F7, F82)
- ✅ Fix all unused imports (F401)
- ✅ Fix all unused variables (F841)

**Critical Errors (Block Merging):**
- `E9xx` - Runtime errors (syntax errors)
- `F63x` - Invalid assert or print statements
- `F7xx` - Syntax errors in type comments
- `F82x` - Undefined names in `__all__`

**Warnings (Should Fix):**
- `E501` - Line too long (> 127 chars)
- `F401` - Imported but unused
- `F841` - Local variable assigned but never used
- `C901` - Function too complex (cyclomatic complexity > 10)

### Type Checking (mypy)

**MUST:**
- ✅ Add type hints to all public functions
- ✅ Add type hints to all class methods
- ✅ Use `Optional[T]` for nullable types
- ✅ Use `List[T]`, `Dict[K, V]` for collections

**Recommended:**
- Use `from typing import` for type hints
- Avoid `# type: ignore` without justification
- Fix type errors rather than ignoring them

---

## Pre-Commit Requirements

**MUST** run linting before committing:

```bash
# Check all linting rules
./lint.sh

# Fix auto-fixable issues
./lint.sh --fix
```

**Rules:**
- ✅ Run `./lint.sh` before every commit
- ✅ Fix all auto-fixable issues with `./lint.sh --fix`
- ✅ Fix all manual issues before committing
- ❌ Never commit code that fails linting checks

---

## CI/CD Requirements

**MUST** configure CI/CD to enforce linting:

The CI pipeline **MUST** run:
1. **Black check** - Ensures code is formatted
2. **isort check** - Ensures imports are sorted
3. **Flake8 (critical)** - Blocks on syntax errors
4. **Flake8 (warnings)** - Shows warnings but doesn't block

**Rules:**
- ✅ All linting checks **MUST** pass in CI
- ✅ Critical errors **MUST** block merging
- ✅ Warnings should be addressed but don't block
- ❌ Never disable linting checks in CI

---

## Best Practices

**MUST follow:**

1. **✅ Run linting before committing**
   - Use `./lint.sh` to check everything
   - Fix issues immediately (don't accumulate technical debt)

2. **✅ Use auto-fix when possible**
   - Run `./lint.sh --fix` for Black and isort
   - Only manual fixes needed for Flake8 and mypy

3. **✅ Keep functions simple**
   - Cyclomatic complexity **MUST** be < 10
   - Refactor complex functions into smaller ones

4. **✅ Add type hints**
   - All public functions **MUST** have type hints
   - Use proper types (no `Any` without justification)

5. **✅ Organize imports**
   - Run `isort` to auto-organize imports
   - Follow the standard import order

**Forbidden:**

1. **❌ Disable linting rules without team discussion**
   - No `# noqa` comments without justification
   - No skipping linting in CI/CD

2. **❌ Ignore type hints**
   - All public functions **MUST** have type hints
   - Fix type errors, don't ignore them

3. **❌ Commit code that fails linting**
   - All checks **MUST** pass before committing
   - CI will block failing code

---

## Summary

**Required:**
- Black formatting (line length 127)
- isort import organization
- Flake8 quality checks (complexity < 10, fix critical errors)
- mypy type checking (type hints on public functions)
- Run `./lint.sh` before every commit
- All checks **MUST** pass in CI

**Forbidden:**
- Disabling linting rules without approval
- Committing code that fails linting
- Line length > 127 characters
- Cyclomatic complexity > 10
- Missing type hints on public functions

