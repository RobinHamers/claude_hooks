# Claude Hooks, Skills & Commands

A collection of [Claude Code](https://claude.ai/claude-code) hooks, skills, and commands to improve security, control, and productivity.

---

## What are Claude Code hooks?

Hooks are shell commands that run automatically in response to Claude Code events — before or after tool calls like reading a file, editing code, running a bash command, etc. They let you enforce rules, block actions, or log activity without relying on prompts.

## What are Claude Code skills?

Skills are reusable prompt templates invoked via `/skill-name` in Claude Code. They are packaged as `.skill` files and live in `~/.claude/skills/`.

## What are Claude Code commands?

Commands are slash commands you invoke in Claude Code with `/command-name`. They are defined as markdown files inside a **plugin** — a small folder with a specific structure that Claude Code loads at startup.

---

## Hooks

### `check-claudeignore` — Block file access via `.claudeignore`

Prevents Claude from reading, editing, or searching files that match patterns listed in a `.claudeignore` file at the root of your project.

**Blocked tools:** `Read`, `Edit`, `Grep`

**How it works:**
1. Before Claude opens a file, the hook intercepts the tool call
2. It walks up the directory tree to find a `.claudeignore` file
3. If the file path matches any pattern, the tool call is blocked with a clear error message

**Example error:**
```
Blocked: '/project/secrets/.env' matches '*.env' in .claudeignore
```

### Setup

**Option A — Use in your own project (recommended for teams)**

Copy the `.claude/` folder and `.claudeignore.example` into your project:

```bash
cp -r .claude /your-project/
cp .claudeignore.example /your-project/.claudeignore
```

Then commit everything:

```bash
git add .claude/ .claudeignore
git update-index --chmod=+x .claude/hooks/check-claudeignore.sh
git commit -m "add Claude hooks"
```

Claude Code will automatically pick up `.claude/settings.json` when your colleagues open the project. They will be prompted once to approve the hook.

**Option B — Install globally (applies to all your projects)**

Copy the hook script somewhere permanent:

```bash
mkdir -p ~/.claude/hooks
cp .claude/hooks/check-claudeignore.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/check-claudeignore.sh
```

Then add the hook to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Grep",
        "hooks": [
          {
            "type": "command",
            "command": "/home/YOUR_USERNAME/.claude/hooks/check-claudeignore.sh"
          }
        ]
      }
    ]
  }
}
```

### Configuring `.claudeignore`

Rename `.claudeignore.example` to `.claudeignore` in your project root and add the files or patterns you want to protect. The syntax is similar to `.gitignore`.

```bash
# Block specific files
.env
secrets.json

# Block by extension
*.pem
*.key

# Block a directory
private/*
vault/*
```

> `.claudeignore` should be committed to your repo so the rules apply to your whole team.

---

## Skills

Skills live in the `Skills/` directory as `.skill` files. To use them, copy the file into your Claude Code skills directory:

```bash
cp Skills/<skill-name>.skill ~/.claude/skills/
```

Then invoke it in Claude Code with:

```
/<skill-name>
```

### Available skills

| Skill | Description |
|---|---|
| `morning-email-briefing` | Generates a morning briefing from your emails |

---

## Commands

Commands live in the `Commands/` directory as `.md` files. Installing a command requires setting up a small **plugin folder** and registering it with Claude Code. Do this once — then every command you add to the folder becomes a new slash command automatically.

### One-time setup

**1. Create the plugin folder structure**

```bash
mkdir -p ~/.claude/plugins/cache/local-plugins/my-commands/local/commands
mkdir -p ~/.claude/plugins/cache/local-plugins/my-commands/local/.claude-plugin
```

**2. Create the plugin metadata file**

Create `~/.claude/plugins/cache/local-plugins/my-commands/local/.claude-plugin/plugin.json`:

```json
{
  "name": "my-commands",
  "description": "My local Claude Code commands",
  "author": {
    "name": "Your Name"
  }
}
```

**3. Register it in `~/.claude/plugins/installed_plugins.json`**

Add the following entry inside the `"plugins"` object:

```json
"my-commands@local-plugins": [
  {
    "scope": "user",
    "installPath": "/home/YOUR_USERNAME/.claude/plugins/cache/local-plugins/my-commands/local",
    "version": "local",
    "installedAt": "2026-01-01T00:00:00.000Z",
    "lastUpdated": "2026-01-01T00:00:00.000Z"
  }
]
```

**4. Enable it in `~/.claude/settings.json`**

Add to the `"enabledPlugins"` object:

```json
"my-commands@local-plugins": true
```

**5. Restart Claude Code**

### Adding a command

Copy any `.md` file from the `Commands/` directory into your plugin's `commands/` folder:

```bash
cp Commands/commit-all.md ~/.claude/plugins/cache/local-plugins/my-commands/local/commands/
```

Then restart Claude Code. The command is immediately available as `/commit-all`.

Each command file can optionally have a frontmatter header:

```markdown
---
description: Short description shown in /help
allowed-tools: [Bash, Read, Edit]
---
```

### Available commands

| Command | Description |
|---|---|
| `commit-all` | Scans all git repos in your home folder, shows changes, and lets you commit and push each one interactively |

#### `commit-all` — Interactive multi-repo commit & push

Scans up to 2 levels deep in your home directory for git repositories, shows the diff/status for each one that has uncommitted changes, and asks you repo by repo whether to commit and push.

**Usage:**
```
/commit-all
```

**What it does:**
1. Finds all git repos under your home folder
2. Skips repos with no changes
3. For each dirty repo, shows a diff summary and asks: commit and push? (yes/no/skip)
4. Commits with a descriptive message and pushes only when you confirm
5. Prints a final summary of what was committed and what was skipped

> **Note:** The `commit-all.md` file scans `/home/robin-hamers/` by default. Edit the path inside the file to match your own username before using it.

---

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- Python 3 (used inside hook scripts for JSON parsing and glob matching)
- bash
- git

---

## Contributing

Feel free to open a PR to add new hooks, skills, or commands.
