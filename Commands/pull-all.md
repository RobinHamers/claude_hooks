Scan all directories in /home/robin-hamers/ for git repositories and pull the latest changes.

Steps:
1. Run `find /home/robin-hamers -maxdepth 2 -name ".git" -type d 2>/dev/null` to find all git repos
2. For each repo, check if it has a remote: `git -C <repo> remote -v`
3. For repos with a remote, run `git -C <repo> pull --ff-only`
4. Report results:
   - Already up to date
   - Successfully pulled (show what changed)
   - Failed / conflicts (show the error)
   - No remote (skipped)
5. Show a summary at the end

Important:
- Do not pull repos with no remote, skip silently
- If a pull fails due to local changes (not fast-forward), report it clearly and do not force
- Show repo name, not full path, for readability
