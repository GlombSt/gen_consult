# Linting Guide

**Companion to:** [LINTING_STANDARDS.md](./LINTING_STANDARDS.md)
**Version:** 1.0
**Last Updated:** December 2025
**Audience:** Developers implementing and fixing linting issues

**Related Documentation:**
- [Linting Standards](./LINTING_STANDARDS.md) - Mandatory rules (read first!)
- [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md) - Code organization rules

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Tool Installation](#tool-installation)
3. [Running Individual Tools](#running-individual-tools)
4. [Configuration Details](#configuration-details)
5. [Common Issues and Fixes](#common-issues-and-fixes)
6. [IDE Integration](#ide-integration)
7. [Pre-commit Hooks](#pre-commit-hooks)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Linting Tools

```bash
# Option 1: Install with dev dependencies (recommended)
pip install -e '.[dev]'

# Option 2: Install individually
pip install black isort flake8 mypy
```

### Run All Checks

```bash
# Check all linting rules (does not modify files)
./lint.sh

# Fix auto-fixable issues (Black and isort)
./lint.sh --fix
```

---

## Tool Installation

### Option 1: Dev Dependencies (Recommended)

Install all linting tools at once:

```bash
pip install -e '.[dev]'
```

This installs all tools specified in `pyproject.toml` under `[project.optional-dependencies.dev]`.

### Option 2: Individual Installation

Install each tool separately:

```bash
pip install black isort flake8 mypy
```

### Verify Installation

```bash
black --version
isort --version
flake8 --version
mypy --version
```

---

## Running Individual Tools

### 1. Black - Code Formatting

Black enforces consistent code formatting across the entire codebase.

**Check formatting:**
```bash
black --check app/ tests/
```

**Fix formatting automatically:**
```bash
black app/ tests/
```

**Format a single file:**
```bash
black app/items/service.py
```

**What Black formats:**
- Line length (127 characters max)
- Indentation (4 spaces)
- Quote style (double quotes preferred)
- Trailing commas
- Blank lines and spacing

**Example:**
```python
# Before
def create_item(name:str,price:float)->Item:
    return Item(name=name,price=price)

# After Black
def create_item(name: str, price: float) -> Item:
    return Item(name=name, price=price)
```

### 2. isort - Import Sorting

isort organizes imports into logical sections and sorts them alphabetically.

**Check import sorting:**
```bash
isort --check-only app/ tests/
```

**Fix imports automatically:**
```bash
isort app/ tests/
```

**Import order:**
1. Future imports (`from __future__ import ...`)
2. Standard library imports (`import os, sys, ...`)
3. Third-party imports (`import fastapi, pydantic, ...`)
4. First-party imports (`from app import ...`)
5. Local folder imports (`from . import ...`)

**Example of properly sorted imports:**
```python
# Standard library
import os
from datetime import datetime
from typing import Optional

# Third-party
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# First-party
from app.shared.events import publish_event
from app.users.models import User

# Local
from .models import Item
from .schemas import ItemCreate
```

### 3. Flake8 - Code Quality Linting

Flake8 checks for code quality issues, style problems, and potential bugs.

**Run all checks:**
```bash
flake8 app/ tests/ --max-complexity=10 --max-line-length=127
```

**Check critical errors only:**
```bash
flake8 app/ tests/ --select=E9,F63,F7,F82
```

**Common error codes:**
- `E9xx` - Runtime errors (syntax errors)
- `F63x` - Invalid assert or print statements
- `F7xx` - Syntax errors in type comments
- `F82x` - Undefined names in `__all__`
- `E501` - Line too long (> 127 chars)
- `F401` - Imported but unused
- `F841` - Local variable assigned but never used
- `C901` - Function too complex (cyclomatic complexity > 10)

**Fix common issues:**
- **Remove unused imports:** Delete the unused import lines
- **Break long lines:** Split into multiple lines using parentheses
- **Reduce complexity:** Refactor complex functions into smaller ones

### 4. mypy - Type Checking

mypy performs static type analysis to catch type-related bugs.

**Run type checking:**
```bash
mypy app/ --ignore-missing-imports
```

**Check a specific module:**
```bash
mypy app/items/
```

**Type hints example:**
```python
from typing import Optional, List

def create_item(name: str, price: float) -> Item:
    """Create a new item with type hints."""
    return Item(name=name, price=price)

async def get_items(limit: Optional[int] = None) -> List[Item]:
    """Get items with optional limit."""
    # Implementation
    pass
```

---

## Configuration Details

All linting rules are configured in `pyproject.toml` at the project root.

### Black Configuration

```toml
[tool.black]
line-length = 127
target-version = ['py314']
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

### mypy Configuration

```toml
[tool.mypy]
python_version = "3.14"
strict_equality = true
warn_unused_configs = true
ignore_missing_imports = true
```

---

## Common Issues and Fixes

### Issue 1: Line Too Long (E501)

**Problem:**
```python
raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found in the database")
```

**Fix:**
```python
raise HTTPException(
    status_code=404,
    detail=f"Item with ID {item_id} not found in the database"
)
```

### Issue 2: Unused Import (F401)

**Problem:**
```python
from typing import Optional, List
from app.items.models import Item

def create_item(name: str) -> Item:
    return Item(name=name)
```

**Fix:**
```python
from app.items.models import Item

def create_item(name: str) -> Item:
    return Item(name=name)
```

### Issue 3: Import Not Sorted

**Problem:**
```python
from app.items.models import Item
from fastapi import APIRouter
import os
```

**Fix (run `isort`):**
```python
import os

from fastapi import APIRouter

from app.items.models import Item
```

### Issue 4: Complex Function (C901)

**Problem:**
```python
def process_item(item):
    if item.price > 100:
        if item.discount > 0.5:
            if item.category == "electronics":
                # Many nested conditions...
```

**Fix - Refactor:**
```python
def is_high_value_electronics(item):
    return (
        item.price > 100
        and item.discount > 0.5
        and item.category == "electronics"
    )

def process_item(item):
    if is_high_value_electronics(item):
        # Simplified logic
```

### Issue 5: Missing Type Hints

**Problem:**
```python
def calculate_total(items):
    return sum(item.price for item in items)
```

**Fix:**
```python
from typing import List

def calculate_total(items: List[Item]) -> float:
    return sum(item.price for item in items)
```

---

## IDE Integration

### VS Code

**1. Install Python extension**

**2. Add to `.vscode/settings.json`:**
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=127",
    "--max-complexity=10"
  ],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

### PyCharm

**1. Configure Black:**
- Settings → Tools → External Tools → Add Black
- Configure to run on save

**2. Configure Flake8:**
- Settings → Editor → Inspections → Python
- Enable Flake8 inspection

**3. Configure isort:**
- Settings → Tools → Python Integrated Tools
- Set import sorter to "isort"

---

## Pre-commit Hooks

For automatic linting before every commit, install pre-commit hooks:

**1. Install pre-commit:**
```bash
pip install pre-commit
```

**2. Create `.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.14

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=127', '--max-complexity=10']
```

**3. Install hooks:**
```bash
pre-commit install
```

Now linting runs automatically before every commit!

---

## Troubleshooting

### Black and Flake8 Conflict on Line Length

**This shouldn't happen** with our configuration (both set to 127), but if it does:

```bash
# Black takes precedence - format with Black first
black app/ tests/

# Then check flake8
flake8 app/ tests/ --max-line-length=127
```

### isort Messing Up Imports

If isort incorrectly categorizes an import:

```python
# Add a comment to override
from third_party_lib import something  # isort: skip
```

Or configure in `pyproject.toml`:

```toml
[tool.isort]
known_third_party = ["library_name"]
```

### mypy False Positives

Add type ignore comments for genuine false positives:

```python
result = some_function()  # type: ignore[arg-type]
```

But investigate first - often the type hint can be improved!

### Lint Script Not Working

If `./lint.sh` fails:

1. **Check file permissions:**
   ```bash
   chmod +x lint.sh
   ```

2. **Check if tools are installed:**
   ```bash
   which black isort flake8 mypy
   ```

3. **Run tools individually:**
   ```bash
   black --check app/
   isort --check-only app/
   flake8 app/
   mypy app/
   ```

---

## Summary Commands

```bash
# Quick check everything
./lint.sh

# Fix auto-fixable issues
./lint.sh --fix

# Individual checks
black --check app/ tests/
isort --check-only app/ tests/
flake8 app/ tests/ --max-complexity=10 --max-line-length=127
mypy app/

# Individual fixes
black app/ tests/
isort app/ tests/
```

---

## References

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)

