Show a human-readable summary of all uncommitted changes across repos in /home/robin-hamers/. No commits — review only.

Steps:
1. Run `find /home/robin-hamers -maxdepth 2 -name ".git" -type d 2>/dev/null` to find all git repos
2. For each repo, check `git -C <repo> status --short`
3. For repos with changes:
   a. Show repo name as a header
   b. Show `git -C <repo> diff --stat` (summary of changed lines)
   c. For modified files with <100 line diff, show `git -C <repo> diff -- <file>` inline
   d. For large diffs or untracked files, just list the names
4. Group by category:
   - Modified files (with diff)
   - New untracked files
   - Deleted files
5. At the end, show a one-line summary per repo: "repo-name: X modified, Y untracked, Z deleted"

Important:
- This is READ ONLY — never stage, commit, or push anything
- Skip repos with no changes
- Truncate very large diffs (>200 lines) with a note
- Show relative paths from repo root for readability
