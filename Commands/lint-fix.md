Run linting and auto-formatting on Python files in the current repo.

Steps:
1. Find the current git repo root: `git rev-parse --show-toplevel`
2. Check which tools are available: `which ruff black isort 2>/dev/null`
3. Find Python files with changes: `git diff --name-only HEAD` + `git ls-files --others --exclude-standard` filtered to `*.py`
   - If no changed files, run on all `.py` files in the repo
4. Run available tools in this order:
   a. `ruff check --fix <files>` — fix auto-fixable lint issues
   b. `ruff format <files>` — format (if ruff available)
   c. OR `black <files>` + `isort <files>` — if ruff not available
5. Show a summary:
   - Which files were modified
   - Which issues were fixed vs still need manual attention
   - Any errors

Important:
- Prefer ruff over black/isort (faster, covers both)
- If no linter is installed, suggest: `pip install ruff`
- Do not modify files outside the current git repo
- If inside a virtualenv or the project has a pyproject.toml / .ruff.toml, respect those configs
