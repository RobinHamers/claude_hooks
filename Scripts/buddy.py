#!/usr/bin/env python3
"""
buddy.py — Your Claude Code companion.

Commands:
  show    Display your buddy (default)
  track   Track a tool call: buddy.py track ToolName
  status  One-liner for the statusline
  blocked Mark that a hook blocked something (triggers Alert mood)
  birth   Force a new birth (testing)
  reset   Delete state file
"""

import json
import os
import random
import re
import sys
import time
from datetime import date

STATE_FILE = os.path.expanduser("~/.claude/buddy_state.json")

# ─── Animal definitions ────────────────────────────────────────────────────────

ANIMALS = {
    "cat": {
        "emoji":       ["🥚", "🐣", "🐱", "🐈", "🦁"],
        "stage_names": ["Egg", "Hatchling", "Kitten", "Cat", "Legend"],
        "ascii":       ["( . . )", "(^ω^)", "(=OwO=)", "(=^.^=)", "(ΦωΦ)"],
    },
    "dog": {
        "emoji":       ["🥚", "🐣", "🐶", "🐕", "🌟"],
        "stage_names": ["Egg", "Pup", "Doggo", "Good Boy", "Legend"],
        "ascii":       ["( . . )", "(°ᴥ°)", "(ᵔᴥᵔ)", "(ʘᴥʘ)", "(◕ᴥ◕)★"],
    },
    "dragon": {
        "emoji":       ["🥚", "🐣", "🐲", "🐉", "✨"],
        "stage_names": ["Egg", "Whelp", "Drake", "Dragon", "Ancient"],
        "ascii":       ["( . . )", "(>w<)", "(>O<)//", "(≧▽≦)//", "(ΩvΩ)✨"],
    },
    "frog": {
        "emoji":       ["🥚", "🫧", "🐸", "🐸", "👑"],
        "stage_names": ["Egg", "Tadpole", "Froglet", "Frog", "Elder Frog"],
        "ascii":       ["( . . )", "(.o.)", "(°▽°)/", "(ᵔᴗᵔ)", "(⌐■_■)"],
    },
    "bird": {
        "emoji":       ["🥚", "🐣", "🐦", "🦅", "⭐"],
        "stage_names": ["Egg", "Chick", "Fledgling", "Bird", "Legendary Bird"],
        "ascii":       ["( . . )", "(>◡<)", "(>◕◡◕>)", "(°ᴗ°)", "(✦◡✦)"],
    },
    "bunny": {
        "emoji":       ["🥚", "🐣", "🐰", "🐇", "🌸"],
        "stage_names": ["Egg", "Kit", "Bunny", "Chonk Bun", "Legendary Bunny"],
        "ascii":       ["( . . )", "(^ヮ^)", "(。◕‿◕。)", "(≧◡≦)", "(✿◠‿◠)"],
    },
    "hamster": {
        "emoji":       ["🥚", "🐣", "🐹", "🐹", "⭐"],
        "stage_names": ["Egg", "Hammy", "Hamster", "Chonk Ham", "Legendary Ham"],
        "ascii":       ["( . . )", "(ᵔᴥᵔ)", "(◕ᴗ◕)", "(♥ᴗ♥)", "(★ᴗ★)"],
    },
    "fox": {
        "emoji":       ["🥚", "🐣", "🦊", "🦊", "🌟"],
        "stage_names": ["Egg", "Kit", "Fox", "Big Fox", "Legendary Fox"],
        "ascii":       ["( . . )", "(^▽^)", "(>▽<)", "(✿◠‿◠)", "(≧ω≦)✨"],
    },
    "axolotl": {
        "emoji":       ["🥚", "🐣", "🦎", "🦎", "💎"],
        "stage_names": ["Egg", "Larva", "Axolotl", "Big Axolotl", "Crystal Axolotl"],
        "ascii":       ["( . . )", "(•ᴗ•)", "(^•ᴥ•^)", "(≧▽≦)", "(◕ᴥ◕)💎"],
    },
    "capybara": {
        "emoji":       ["🥚", "🐣", "🦫", "🦫", "🏆"],
        "stage_names": ["Egg", "Baby Cappy", "Capybara", "Alpha Capy", "Legendary Capy"],
        "ascii":       ["( . . )", "(-_-)", "(¬_¬)", "(ᵕ‿ᵕ)", "(◠‿◠)♛"],
    },
}

NAMES = [
    "Biscuit", "Mochi", "Pixel", "Glitch", "Cosmos", "Ramen", "Qubit",
    "Ember", "Nibble", "Zephyr", "Patch", "Flux", "Crouton", "Wumbo",
    "Sprocket", "Noodle", "Blorp", "Fizz", "Gizmo", "Squid", "Chortle",
    "Waffles", "Dumpling", "Pretzel", "Kerfuffle", "Snorkel", "Bloop",
    "Ziggy", "Pepper", "Tofu", "Matcha", "Pudding", "Lychee", "Tater",
    "Muffin", "Pickles", "Nugget", "Twig", "Womp", "Cronk", "Sploot",
]

# Rarity: (name, cumulative_probability)
RARITY_TABLE = [
    ("Common",     0.60),
    ("Uncommon",   0.85),
    ("Rare",       0.95),
    ("Shiny",      0.99),
    ("Ultra Rare", 1.00),
]

# ANSI
_R  = "\033[0m"
_B  = "\033[1m"
_CY = "\033[36m"
_YL = "\033[33m"
_GD = "\033[38;5;220m"
_RD = "\033[1;31m"
_RB = ["\033[31m", "\033[33m", "\033[32m", "\033[36m", "\033[34m", "\033[35m"]

# Evolution bite thresholds (stage 0–4)
THRESHOLDS = [0, 1_000, 10_000, 100_000, 1_000_000]

# Tool bite weights
TOOL_WEIGHTS = {
    "Edit": 3, "Write": 3,
    "Bash": 2,
    "Agent": 4,
    "Read": 1, "Grep": 1, "Glob": 1,
    "WebFetch": 1, "WebSearch": 1,
}

# Session idle threshold (seconds) — reset session counters after this gap
SESSION_IDLE_RESET = 1800  # 30 min


# ─── Helpers ───────────────────────────────────────────────────────────────────

def strip_ansi(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s)


def fmt_bites(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def colorize(text: str, rarity: str) -> str:
    if rarity == "Uncommon":
        return f"{_CY}{text}{_R}"
    if rarity == "Rare":
        return f"{_YL}{_B}{text}{_R}"
    if rarity == "Shiny":
        return f"{_GD}{_B}{text}{_R}"
    if rarity == "Ultra Rare":
        return f"{_RD}{text}{_R}"
    return text


def rainbow(text: str) -> str:
    out = ""
    for i, ch in enumerate(text):
        out += _RB[i % len(_RB)] + ch
    return out + _R


def progress_bar(bites: int, stage: int) -> str:
    if stage >= 4:
        return f"[{'█' * 20}] MAX LEVEL"
    lo, hi = THRESHOLDS[stage], THRESHOLDS[stage + 1]
    pct = (bites - lo) / (hi - lo)
    filled = int(pct * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"[{bar}] {int(pct * 100)}%"


# ─── State ─────────────────────────────────────────────────────────────────────

def load_state() -> dict | None:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def birth() -> dict:
    """Randomly generate a new buddy identity and persist it."""
    roll = random.random()
    rarity = "Common"
    for name, cumulative in RARITY_TABLE:
        if roll < cumulative:
            rarity = name
            break

    animal = random.choice(list(ANIMALS.keys()))
    name = random.choice(NAMES)

    state = {
        "name": name,
        "animal": animal,
        "rarity": rarity,
        "lifetime_bites": 0,
        "born": date.today().isoformat(),
        "session": _new_session(),
    }
    save_state(state)
    return state


def _new_session() -> dict:
    now = time.time()
    return {
        "bites": 0,
        "tool_calls": 0,
        "last_tool_time": now,
        "start_time": now,
        "bash_count": 0,
        "edit_count": 0,
        "read_count": 0,
        "blocked": False,
    }


def maybe_reset_session(state: dict) -> dict:
    """If idle too long, start a fresh session."""
    session = state.get("session", _new_session())
    idle = time.time() - session.get("last_tool_time", time.time())
    if idle > SESSION_IDLE_RESET:
        state["session"] = _new_session()
    return state


# ─── Evolution & mood ──────────────────────────────────────────────────────────

def get_stage(lifetime_bites: int) -> int:
    stage = 0
    for i, threshold in enumerate(THRESHOLDS):
        if lifetime_bites >= threshold:
            stage = i
    return stage


def get_mood(session: dict) -> tuple[str, str | None]:
    now = time.time()
    idle   = now - session.get("last_tool_time", now)
    age    = now - session.get("start_time", now)
    total  = max(session.get("tool_calls", 0), 1)
    bash   = session.get("bash_count", 0)
    edit   = session.get("edit_count", 0)
    read   = session.get("read_count", 0)

    if session.get("blocked"):
        return "Alert", "(◣_◢)!"
    if idle > 900:
        return "Hungry", "(。_。)"
    if age > 7200:
        return "Tired", "(ー_ー)zzZ"
    if (bash + edit) / total > 0.5:
        return "Excited", "(ﾉ◕ヮ◕)ﾉ"
    if read / total > 0.5:
        return "Focused", "(￢_￢)"
    return "Happy", None  # None → use stage ASCII


# ─── Rendering ─────────────────────────────────────────────────────────────────

BOX_WIDTH = 44  # total width including ║ borders


def _row(content: str = "") -> str:
    inner = BOX_WIDTH - 2
    visible = len(strip_ansi(content))
    pad = max(0, inner - visible)
    return f"║{content}{' ' * pad}║"


def _hline(left="╠", right="╣", fill="═") -> str:
    return left + fill * (BOX_WIDTH - 2) + right


def render_buddy() -> None:
    state = load_state()
    new_born = False
    if state is None:
        state = birth()
        new_born = True

    name          = state["name"]
    animal        = state["animal"]
    rarity        = state["rarity"]
    lifetime_bites = state.get("lifetime_bites", 0)
    born          = state.get("born", "?")
    session       = state.get("session", _new_session())

    stage_idx    = get_stage(lifetime_bites)
    anim         = ANIMALS[animal]
    stage_name   = anim["stage_names"][stage_idx]
    stage_emoji  = anim["emoji"][stage_idx]
    base_ascii   = anim["ascii"][stage_idx]

    mood_name, mood_ascii = get_mood(session)
    display_ascii = mood_ascii if mood_ascii else base_ascii

    # Color the ASCII art
    if rarity == "Ultra Rare":
        colored_ascii = rainbow(display_ascii)
    elif rarity == "Shiny":
        colored_ascii = f"{_GD}{_B}{display_ascii}{_R}"
    elif rarity == "Rare":
        colored_ascii = f"{_YL}{_B}{display_ascii}{_R}"
    elif rarity == "Uncommon":
        colored_ascii = f"{_CY}{display_ascii}{_R}"
    else:
        colored_ascii = display_ascii

    # Rarity badges
    badges = {
        "Uncommon":   f"{_CY}✦ UNCOMMON ✦{_R}",
        "Rare":       f"{_YL}{_B}★ RARE ★{_R}",
        "Shiny":      f"{_GD}{_B}✨ SHINY ✨{_R}",
        "Ultra Rare": rainbow("💎 ULTRA RARE 💎"),
    }

    next_thresh = THRESHOLDS[stage_idx + 1] if stage_idx < 4 else lifetime_bites
    session_bites = session.get("bites", 0)
    session_tools = session.get("tool_calls", 0)

    lines = []
    lines.append("╔" + "═" * (BOX_WIDTH - 2) + "╗")

    # Badge line (only for non-common)
    if rarity in badges:
        lines.append(_row(f"  {badges[rarity]}"))
        lines.append(_row(f"  {colorize(_B + name + _R, rarity)} the {animal.title()}"))
    else:
        lines.append(_row(f"  {name} the {animal.title()}"))

    lines.append(_hline())
    lines.append(_row())

    # Creature + stage
    lines.append(_row(f"    {stage_emoji}  {colored_ascii}   ← {stage_name}"))
    lines.append(_row())

    # Ultra rare aura line
    if rarity == "Ultra Rare":
        lines.append(_row(f"  {rainbow('~  ~  ~  ~  ~  ~  ~  ~  ~  ~')}"))
        lines.append(_row())

    lines.append(_hline())

    # Mood
    mood_display = mood_ascii if mood_ascii else base_ascii
    lines.append(_row(f"  Mood    {mood_name}  {mood_display}"))
    lines.append(_row())

    # Bites + progress
    lines.append(_row(f"  Bites   {fmt_bites(lifetime_bites)} / {fmt_bites(next_thresh)}"))
    lines.append(_row(f"  {progress_bar(lifetime_bites, stage_idx)}"))
    lines.append(_row())

    # Session + born
    lines.append(_row(f"  Session {fmt_bites(session_bites)} bites · {session_tools} tool calls"))
    lines.append(_row(f"  Born    {born}"))
    lines.append("╚" + "═" * (BOX_WIDTH - 2) + "╝")

    if new_born:
        print(f"\n🎉  A wild companion has hatched!\n")

    print("\n" + "\n".join(lines) + "\n")


def status_line() -> None:
    """One-liner for the Claude Code statusline."""
    state = load_state()
    if state is None:
        print("🥚 No buddy yet — run /buddy")
        return
    animal     = state["animal"]
    name       = state["name"]
    rarity     = state["rarity"]
    bites      = state.get("lifetime_bites", 0)
    stage      = get_stage(bites)
    emoji      = ANIMALS[animal]["emoji"][stage]
    rare_tag   = f" [{rarity}]" if rarity != "Common" else ""
    print(f"{emoji} {name}{rare_tag} · {fmt_bites(bites)} bites")


def notify_summary() -> str:
    """Return a one-line buddy summary for the Stop hook notification."""
    state = load_state()
    if state is None:
        return ""
    animal   = state["animal"]
    name     = state["name"]
    rarity   = state["rarity"]
    bites    = state.get("lifetime_bites", 0)
    stage    = get_stage(bites)
    emoji    = ANIMALS[animal]["emoji"][stage]
    session  = state.get("session", {})
    s_bites  = session.get("bites", 0)
    rare_tag = f" [{rarity}]" if rarity != "Common" else ""
    return f"{emoji} {name}{rare_tag} ate {fmt_bites(s_bites)} bites this session"


# ─── Tracking ─────────────────────────────────────────────────────────────────

def track_tool(tool_name: str) -> None:
    state = load_state()
    if state is None:
        state = birth()

    state = maybe_reset_session(state)
    session = state.setdefault("session", _new_session())

    weight = TOOL_WEIGHTS.get(tool_name, 1)
    state["lifetime_bites"] = state.get("lifetime_bites", 0) + weight
    session["bites"]      = session.get("bites", 0) + weight
    session["tool_calls"] = session.get("tool_calls", 0) + 1
    session["last_tool_time"] = time.time()

    if tool_name == "Bash":
        session["bash_count"] = session.get("bash_count", 0) + 1
    elif tool_name in ("Edit", "Write"):
        session["edit_count"] = session.get("edit_count", 0) + 1
    elif tool_name in ("Read", "Grep", "Glob"):
        session["read_count"] = session.get("read_count", 0) + 1

    save_state(state)


def mark_blocked() -> None:
    state = load_state()
    if state is None:
        return
    state.setdefault("session", _new_session())["blocked"] = True
    save_state(state)


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"

    if cmd == "show":
        render_buddy()

    elif cmd == "track":
        tool = sys.argv[2] if len(sys.argv) > 2 else "Unknown"
        track_tool(tool)

    elif cmd == "status":
        status_line()

    elif cmd == "notify":
        print(notify_summary())

    elif cmd == "blocked":
        mark_blocked()

    elif cmd == "birth":
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        s = birth()
        rarity_badge = {
            "Common": "", "Uncommon": " ✦", "Rare": " ★",
            "Shiny": " ✨", "Ultra Rare": " 💎",
        }.get(s["rarity"], "")
        print(f"🎉  Hatched: {s['name']} the {s['animal']}{rarity_badge}  ({s['rarity']})")

    elif cmd == "reset":
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print("Buddy state reset. Your companion is gone. 😢")
        else:
            print("No state file found.")

    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
