Audit requirements.txt files across all repos in /home/robin-hamers/.

Steps:
1. Find all requirements files: `find /home/robin-hamers -maxdepth 3 -name "requirements*.txt" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null`
2. For each file found:
   a. Show the path and number of dependencies
   b. Check for unpinned packages (no `==` version): list them
   c. Check for packages pinned with `>=` or `~=` (loose pins): list them
   d. Run `pip index versions <package>` or use `pip install <package>==999 2>&1` trick to check latest version for key packages
3. Additionally, for each repo with Python files, check for imports not in requirements:
   - Extract `import X` and `from X import` statements
   - Compare against requirements (rough match on package names)
4. Report:
   - Files with unpinned dependencies
   - Potentially outdated packages (if checkable)
   - Missing requirements (imports without matching package)

Important:
- Skip .venv, node_modules, __pycache__ directories
- Don't install anything — report only
- Keep it fast: don't check every package's latest version, focus on common ones (torch, numpy, pandas, geopandas, rasterio, transformers)
- Group output by repo for readability
