#!/bin/bash
# Stop hook: send a desktop notification when Claude finishes a task

INPUT=$(cat)

TITLE="Claude Code"
MESSAGE="Task finished"

# Try to extract a summary from the stop reason if available
REASON=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('stop_reason', '') or d.get('reason', ''))
except:
    print('')
" 2>/dev/null)

[ -n "$REASON" ] && MESSAGE="Done: $REASON"

# notify-send (Linux desktop)
if command -v notify-send &>/dev/null; then
    DISPLAY="${DISPLAY:-:0}" notify-send "$TITLE" "$MESSAGE" --icon=dialog-information 2>/dev/null
fi

exit 0
