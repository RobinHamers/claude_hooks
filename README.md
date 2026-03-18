# Claude Hooks & Commands

A personal collection of [Claude Code](https://claude.ai/claude-code) hooks and slash commands.

---

## Quick install via Claude Code

You can ask Claude Code to read this repo, explain what's available, and let you pick what to install. Just open Claude Code and say:

> "Read https://github.com/RobinHamers/claude_hooks, explain what hooks, skills, and commands are available and what each one does, then ask me which ones I want to install before doing anything."

Claude will summarize everything in plain language, ask for your confirmation on each item (or as a whole), then clone the repo, symlink commands, register selected hooks in `settings.json`, and install any skill dependencies — only for what you chose.

---

## Setup (single machine)

Everything lives in this repo. `~/.claude/` just links/references here — no duplication.

```bash
git clone git@github.com:RobinHamers/claude_hooks.git ~/claude_hooks

# Symlink commands directory
rm -rf ~/.claude/commands
ln -s ~/claude_hooks/Commands ~/.claude/commands

# Make hooks executable
chmod +x ~/claude_hooks/.claude/hooks/*.sh
```

Then update `~/.claude/settings.json` to reference the hooks (see [settings template](#settings-template) below).

---

## Hooks

Hook scripts live in `.claude/hooks/`. They are registered in `~/.claude/settings.json` using absolute paths to this repo.

### `check-claudeignore` — Block file access via `.claudeignore`

**Event:** `PreToolUse` — `Read | Edit | Grep`

Prevents Claude from reading, editing, or searching files that match patterns in a `.claudeignore` file at your project root. Syntax is similar to `.gitignore`.

```
# .claudeignore example
.env
secrets.json
*.pem
private/*
```

**Example error:**
```
Blocked: '/project/.env' matches '*.env' in .claudeignore
```

---

### `block-force-push` — Block `git push --force`

**Event:** `PreToolUse` — `Bash`

Intercepts any bash command containing `git push --force` or `git push -f` and blocks it. Claude must be explicitly told to force push for it to proceed.

**Example error:**
```
Blocked: 'git push --force' detected. Confirm explicitly if you want to force push.
```

---

### `notify-on-stop` — Desktop notification when Claude finishes

**Event:** `Stop`

Sends a desktop notification via `notify-send` when Claude finishes a task. Useful when running long operations in the background.

Requires `notify-send` (pre-installed on most Linux desktops). Silent no-op if not available.

---

## Commands

Command files live in `Commands/` as `.md` files. `~/.claude/commands/` is a symlink to this directory, so all commands are available immediately after cloning.

Invoke any command with `/command-name` in Claude Code.

### `/pull-all`

Scans all git repos under `~/` (up to 2 levels deep), pulls the latest changes on each, and reports what updated, what was already up to date, and what failed (e.g. local conflicts).

### `/commit-all`

Scans all git repos under `~/` for uncommitted changes, shows a diff summary for each, and asks interactively whether to commit and push. Never commits without your confirmation.

### `/review-changes`

Read-only version of `commit-all`. Shows a human-readable diff summary across all repos — useful for a daily review of what changed. No staging or committing.

### `/gcp-status`

Shows the current GCP/Vertex AI status for your active project: running/pending custom jobs, recent batch prediction jobs, and billing account. Tries `europe-west1` first, falls back to `us-central1`.

Requires `gcloud` authenticated (`gcloud auth login`).

### `/explore-dataset`

Given a file path, runs a quick EDA and prints a structured summary. Supports:

| Format | Library |
|--------|---------|
| `.csv`, `.parquet` | pandas |
| `.geojson`, `.gpkg` | geopandas |
| `.tif`, `.tiff` | rasterio |

Reports shape, dtypes, nulls, value ranges, CRS (for geo files), and flags anomalies like high null rates or suspicious ranges.

### `/lint-fix`

Runs linting and auto-formatting on Python files in the current repo. Targets only files changed since last commit (or all `.py` files if nothing is staged). Prefers `ruff`; falls back to `black` + `isort`.

Install ruff if missing: `pip install ruff`

### `/requirements-audit`

Scans all `requirements*.txt` files under `~/` and reports:
- Unpinned packages (no `==`)
- Loosely pinned packages (`>=`, `~=`)
- Imports in Python files with no matching requirement

Focuses on common ML/geo packages: `torch`, `numpy`, `pandas`, `geopandas`, `rasterio`, `transformers`.

---

## Skills

Skill files live in `Skills/` as `.skill` files (ZIP archives containing `SKILL.md` and optional scripts). Install via the Claude Code plugin system.

### `morning-email-briefing`

Fetches all new emails from the last 24 hours via Microsoft 365 (Outlook), summarizes each one, drafts a copy-paste-ready reply in a formal-yet-friendly style, and saves everything as a structured Notion page.

**Trigger phrases:** "morning briefing", "check my emails", "email summary", "daily email digest", "what's in my inbox?"

**Output:** A Notion page titled `📬 Email Briefing — [Date]` with urgent/normal sections, 2-line summaries, and draft replies per email. Confirms in chat with a stat line.

**Requires:** Microsoft 365 (Outlook) and Notion connectors enabled in Claude.ai.

### `extent-to-polygon`

Converts a bounding box extent (xmin, ymin, xmax, ymax) with a source EPSG code into a WKT `POLYGON((...))` string, with optional reprojection to another CRS.

**Trigger phrases:** "extent to polygon", "bbox to WKT", "convert extent", "reproject bounding box", any 4 coordinates + EPSG + polygon/WKT request.

**Usage:**
```bash
python Skills/extent-to-polygon/scripts/extent_to_polygon.py \
  --extent <xmin> <ymin> <xmax> <ymax> \
  --source-epsg <code> \
  [--target-epsg <code>] \
  [--output <filepath>]
```

**Requires:** `pip install pyproj`

### `context-hub`

Fetches curated, versioned API documentation via the [`chub` CLI](https://github.com/andrewyng/context-hub) before writing code against any external library or SDK. Prevents hallucinated method names and stale API assumptions.

**Trigger phrases:** "use context-hub", "check the docs for", "fetch docs", any request to write code using an external library/API, or any time API correctness is uncertain.

**Workflow:**
```bash
# 1. Search for the doc
chub search <library>

# 2. Fetch it
chub get <id> --lang py   # or --lang js

# 3. Annotate gaps found
chub annotate <id> "<note>"

# 4. Rate quality
chub feedback <id> up|down
```

**Requires:** `npm install -g @aisuite/chub` (or `npm install -g @aisuite/chub --prefix ~/.npm-global` if no global npm write access)

---

## Settings template

`~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Grep",
        "hooks": [
          {
            "type": "command",
            "command": "/home/YOUR_USERNAME/claude_hooks/.claude/hooks/check-claudeignore.sh"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/home/YOUR_USERNAME/claude_hooks/.claude/hooks/block-force-push.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/YOUR_USERNAME/claude_hooks/.claude/hooks/notify-on-stop.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- `bash`
- `python3` (used in hook scripts for JSON parsing)
- `git`
- `gcloud` — for `/gcp-status`
- `ruff` or `black` — for `/lint-fix`
- `pandas`, `geopandas`, `rasterio` — for `/explore-dataset`
- `notify-send` — for `notify-on-stop` hook (optional)
- `npm` + `@aisuite/chub` — for `context-hub` skill (`npm install -g @aisuite/chub`)
