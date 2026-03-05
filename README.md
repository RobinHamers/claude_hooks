# Claude Hooks

A collection of [Claude Code](https://claude.ai/claude-code) hooks to improve security and control over what Claude can access in your projects.

## What are Claude Code hooks?

Hooks are shell commands that run automatically in response to Claude Code events — before or after tool calls like reading a file, editing code, running a bash command, etc. They let you enforce rules, block actions, or log activity without relying on prompts.

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

---

## Setup

### Option A — Use in your own project (recommended for teams)

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

### Option B — Install globally (applies to all your projects)

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

---

## Configuring `.claudeignore`

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

## Requirements

- [Claude Code](https://claude.ai/claude-code)
- Python 3 (used inside the hook script for JSON parsing and glob matching)
- bash

---

## Contributing

Feel free to open a PR to add new hooks or improve existing ones.
