Scan all directories in /home/robin-hamers/ for git repositories and help me commit and push changes interactively.

Steps:
1. Run `find /home/robin-hamers -maxdepth 2 -name ".git" -type d 2>/dev/null` to find all git repos
2. For each repo found, run `git -C <repo_path> status --short` to check for changes
3. List only the repos that have uncommitted changes (skip clean repos)
4. For each repo with changes:
   a. Show the repo path and a summary of changes (`git -C <repo_path> diff --stat` and `git -C <repo_path> status --short`)
   b. Ask me: "Commit and push [repo name]? (yes/no/skip)"
   c. If I say yes: stage all changes, create a descriptive commit message based on the diff, commit, and push
   d. If I say no or skip: move to the next repo
5. At the end, show a summary of what was committed and what was skipped

Important:
- Never commit without my explicit confirmation for each repo
- Show me the actual changes before asking
- Use concise, meaningful commit messages based on what changed
- If a repo has no remote or push fails, report it and continue
