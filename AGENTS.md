# Repository Guidelines

## Project Structure & Module Organization
- Root contains `.github/` (automation) and `prompt.prompt.md` (prompt spec).
- Place application code in `src/`, tests in `tests/`, utilities in `scripts/`, docs in `docs/`.
- Example layout:
  - `src/` — core modules (e.g., `src/tax/`, `src/io/`)
  - `tests/` — mirrors `src/` (e.g., `tests/tax/test_cost_basis.py`)
  - `.github/workflows/` — CI pipelines
  - `data/` (optional) — sample inputs; never commit secrets or real trade data.

## Build, Test, and Development Commands
- Prefer repeatable scripts: add commands to `scripts/` or package scripts.
- Examples (adapt per stack):
  - Run locally: `python -m src.main` or `node src/index.js`
  - Tests: `pytest -q` or `npm test`
  - Lint/format: `ruff check . && black .` or `eslint . && prettier -w .`
- If a `Makefile` exists, provide: `make test`, `make lint`, `make fmt`, `make run`.

## Coding Style & Naming Conventions
- Files/modules: `snake_case`; classes: `PascalCase`; functions/vars: `snake_case`.
- Indentation: 4 spaces; suggested max line length: 100.
- Keep functions focused; place shared helpers in `src/**/utils.py` (or `utils.ts`).
- Recommended tools: Python — `black`, `ruff`; JS/TS — `prettier`, `eslint`.

## Testing Guidelines
- Structure: tests live in `tests/` and mirror `src/` paths.
- Naming: Python `tests/test_*.py`; JS/TS `*.test.ts` or `*.spec.ts`.
- Coverage: aim ≥80% on critical tax logic (P&L, fees, cost basis).
- Include edge cases for exchange behavior (funding, partial fills, liquidations).

## Commit & Pull Request Guidelines
- Commit messages: Conventional Commits (e.g., `feat: add FIFO cost basis`).
- PR checklist: clear description, linked issue, tests added/updated, examples of input→output, and CI passing.
- Keep PRs small and focused; update `prompt.prompt.md` if behavior or prompts change.

## Security & Configuration Tips
- Do not commit API keys or real trade data. Use environment variables via `.env`; document required vars in `.env.example`.
- Validate and sanitize all user-provided files (CSV/JSON). Log only non-sensitive metadata.

## Agent-Specific Instructions
- Prompts live under `.github/prompts/`; keep them versioned and reference from `prompt.prompt.md`.
- Document assumptions (API endpoints, fee schedules) near the code that uses them.
