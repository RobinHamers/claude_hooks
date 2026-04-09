#!/bin/bash
# PostToolUse hook: feed Biscuit a bite for every tool call.
# Silently exits — never blocks.

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', 'Unknown'))
except Exception:
    print('Unknown')
" 2>/dev/null)

python3 ~/claude_hooks/Scripts/buddy.py track "$TOOL_NAME" 2>/dev/null

exit 0
