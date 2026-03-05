#!/bin/bash
# PreToolUse hook: block file access for paths listed in .claudeignore

INPUT=$(cat)

# Extract file path from tool input JSON (Read/Edit use file_path, Grep uses path)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    print(inp.get('file_path', '') or inp.get('path', ''))
except:
    print('')
" 2>/dev/null)

[ -z "$FILE_PATH" ] && exit 0

# Walk up from cwd looking for .claudeignore
find_claudeignore() {
    local dir
    dir=$(pwd)
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/.claudeignore" ]; then
            echo "$dir/.claudeignore"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    return 1
}

IGNORE_FILE=$(find_claudeignore)
[ -z "$IGNORE_FILE" ] && exit 0

# Check if file_path matches any pattern in .claudeignore
MATCH=$(python3 - <<PYEOF
import sys, fnmatch, os

file_path = "$FILE_PATH"
ignore_file = "$IGNORE_FILE"
ignore_dir = os.path.dirname(ignore_file)

try:
    with open(ignore_file) as f:
        patterns = f.readlines()
except Exception:
    sys.exit(0)

for raw in patterns:
    pattern = raw.strip()
    if not pattern or pattern.startswith('#'):
        continue

    if not os.path.isabs(pattern):
        abs_pattern = os.path.join(ignore_dir, pattern)
    else:
        abs_pattern = pattern

    if (fnmatch.fnmatch(file_path, abs_pattern) or
        fnmatch.fnmatch(file_path, abs_pattern.rstrip('/') + '/*') or
        fnmatch.fnmatch(os.path.basename(file_path), pattern) or
        fnmatch.fnmatch(file_path, '*/' + pattern)):
        print(pattern)
        sys.exit(0)

sys.exit(0)
PYEOF
)

if [ -n "$MATCH" ]; then
    echo "Blocked: '$FILE_PATH' matches '$MATCH' in .claudeignore" >&2
    exit 2
fi
