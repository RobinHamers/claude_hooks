#!/bin/bash
# PreToolUse hook: block git force push

INPUT=$(cat)

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except:
    print('')
" 2>/dev/null)

[ -z "$COMMAND" ] && exit 0

if echo "$COMMAND" | grep -qE 'git\s+.*push\s+.*(--force|-f)\b'; then
    echo "Blocked: 'git push --force' detected. Confirm explicitly if you want to force push." >&2
    exit 2
fi

exit 0
