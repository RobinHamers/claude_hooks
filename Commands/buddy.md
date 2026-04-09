Display your Claude Code companion.

Steps:
1. Run: `python3 ~/claude_hooks/Scripts/buddy.py show`
2. Report the output verbatim to the user — do not summarize or paraphrase it.

Notes:
- On first run, a companion is randomly hatched (name, animal, rarity are all random).
- Rarity is determined at birth: Common (60%), Uncommon (25%), Rare (10%), Shiny (4%), Ultra Rare (1%).
- The buddy evolves through 5 stages as it accumulates lifetime bites (tool calls feed it).
- Run `/buddy reset` to hatch a new companion (the old one is gone forever).
- Run `/buddy birth` to force a new hatch (for testing — also erases the old one).
