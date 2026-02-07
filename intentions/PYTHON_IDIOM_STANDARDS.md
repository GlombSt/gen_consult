# Python Idiom Standards

**Version:** 1.0  
**Last Updated:** February 2026  
**Status:** MANDATORY - Python code in intentions/ must follow these rules  
**Audience:** Coding agents and developers

In addition to [AGENTS.md](../AGENTS.md) (readable code) and the standards below, follow these Python-idiomatic rules.

**Already covered elsewhere (pointers only):**

- **Formatting and tooling:** PEP 8, PEP 257; line length and formatting: see [LINTING_STANDARDS.md](LINTING_STANDARDS.md) (Black, isort, Flake8).
- **Exceptions:** Specific exceptions, no swallowing, re-raise after logging: see [EXCEPTION_HANDLING_STANDARDS.md](EXCEPTION_HANDLING_STANDARDS.md).
- **Logging:** Use `logging`, lazy formatting; full rules: [LOGGING_STANDARDS.md](LOGGING_STANDARDS.md).

---

## Style & conventions

- snake_case (vars/functions), PascalCase (classes), UPPER_CASE (constants).
- Absolute imports; order: stdlib → third-party → local; no wildcard imports.

## Typing

- Type hints required for public functions.
- Prefer built-in generics: `list[str]`, `dict[str, int]` (Python 3.10+).
- Use `|` for unions (`str | None`). Prefer this over `Optional[T]` where the repo allows (pyproject targets Python 3.13).
- Prefer `dataclass`, `TypedDict`, or `Protocol` over raw `dict`.

## Data modeling

- **Pydantic in `schemas.py` is the semantic source of truth** for API request/response and field documentation; domain models live in `models.py`. See [ARCHITECTURE_STANDARDS.md](ARCHITECTURE_STANDARDS.md) for the three model types (DB, domain, DTOs).
- Use `@dataclass` only for internal helpers or non-domain structured data (e.g. config objects); do not replace domain models or Pydantic schemas with dataclasses.
- Use `Enum` for fixed value sets.
- Avoid passing loosely structured dictionaries across layers.

## Comprehensions

- Only for simple transformations.
- No side effects inside comprehensions.
- Use `any()` / `all()` where appropriate.

## Forbidden

- Mutable default arguments.
- Dynamic attribute mutation unless necessary.
- Overusing `lambda` for multi-step logic.
- Constructing external clients inside business logic.

## Resource handling

- Always use `with` for files, locks, DB connections.
- Prefer `pathlib` over `os.path`.

## Logging (summary)

- Use `logging`, not `print`.
- Use lazy formatting: `logger.info("User %s", user_id)`.
- Full rules: [LOGGING_STANDARDS.md](LOGGING_STANDARDS.md).

## Tooling

- Code must pass repo lint (see [LINTING_STANDARDS.md](LINTING_STANDARDS.md); tools may include ruff or flake8).
- Prefer pytest-friendly design: pure functions, injected dependencies.

---

**Related Documentation:**

- [ARCHITECTURE_STANDARDS.md](ARCHITECTURE_STANDARDS.md) - Model types (DB, domain, DTOs) and Pydantic as source of truth
- [AGENTS.md](../AGENTS.md) - Readable code conventions
- [LINTING_STANDARDS.md](LINTING_STANDARDS.md) - Formatting and lint rules
- [EXCEPTION_HANDLING_STANDARDS.md](EXCEPTION_HANDLING_STANDARDS.md) - Exception handling
- [LOGGING_STANDARDS.md](LOGGING_STANDARDS.md) - Logging requirements
