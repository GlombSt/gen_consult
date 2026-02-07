# Backend CI optimization (intentions)

## What we look at (from recent runs)

- **Set up Python (~5+ min)** – Largest cost. On self-hosted runners, `actions/setup-python` may download/install Python every run if the version isn’t cached; pip cache only caches packages, not the interpreter.
- **Run full linting (~2+ min)** – Lint runs twice (`./lint.sh --fix` then `./lint.sh`). CI only needs the check; fix is for local use. Lint tools (Black, isort, Flake8, mypy) run **sequentially** in one step. **Why lint duration is high:** (1) **mypy** type-checks the whole codebase and can take 2–3+ minutes on a large repo; (2) **Black** and **isort** each scan all Python files; (3) **Flake8** runs twice (critical select codes, then full). To reduce: run tools in parallel (e.g. separate job steps or background processes), or exclude/skip mypy in CI if optional; keep a single lint run (check only) to avoid doubling time.
- **Install dependencies (~13 s)** – Uses `pip install -e ".[dev]"` while the repo has `uv.lock`; uv is much faster and benefits from a single lockfile-based cache.
- **Caching** – Only pip cache with `pyproject.toml`; no uv cache, no shared Python interpreter cache when using uv.

## Optimization plan (implemented)

1. **Use uv in CI** – `astral-sh/setup-uv` so one step can provide Python + tooling. Do **not** use GitHub’s cache (`enable-cache: false`): GitHub cache still involves network traffic to save/restore. On self-hosted runners, use the **local machine’s uv cache** via `UV_CACHE_DIR` so dependencies are pulled once and reused on disk without extra network.
2. **Install with lockfile** – `uv sync --frozen --extra dev` in `intentions/` for fast, reproducible installs (including dev tools). `--frozen` is equivalent to `--locked` (don’t update lockfile).
3. **Lint once** – Run `./lint.sh` only (check mode). Remove the `--fix` run; fix is for local development.
4. **Run via uv** – Use `uv run` for lint and pytest so they use the synced environment.

## Workflow pattern (local uv cache)

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v7
  with:
    version: "latest"
    enable-cache: false   # Use UV_CACHE_DIR instead of GitHub cloud

- name: Install package and dev dependencies
  run: uv sync --frozen --extra dev
  env:
    UV_CACHE_DIR: /home/sgl/.cache/uv   # or ${HOME}/.cache/uv for portability
```

**Rationale:** GitHub cache is still network traffic (upload/download). Using the self-hosted runner’s local uv cache (`UV_CACHE_DIR`) keeps the cache on the machine and avoids that traffic while still reusing Python and dependencies across runs.

On self-hosted runners, set `UV_CACHE_DIR` to a path that persists on the runner (e.g. `$HOME/.cache/uv` or a shared path like `/home/sgl/.cache/uv`). Ensure the directory exists and the runner user can write to it.
