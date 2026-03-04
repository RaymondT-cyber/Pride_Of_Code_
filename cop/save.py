from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class SaveSlot:
    slot: int
    week_unlocked: int = 1
    last_played_week: int = 1
    last_played_day: int = 1
    # Linear progression through the season: (week-1)*5 + (day-1)
    node_unlocked: int = 0
    # Dialogue keys the player has already seen (so briefings don't repeat).
    seen_dialogue: list[str] = field(default_factory=list)
    pride_points: int = 0
    streak: int = 0
    hints_used: int = 0
    name: str = "DIRECTOR"
    code_by_level: dict[str, str] = field(default_factory=dict)

    # Story flags
    intro_seen: bool = False
    week1_briefing_seen: bool = False
    week1_lesson_seen: bool = False
    week2_briefing_seen: bool = False
    week2_lesson_seen: bool = False


def save_path(base_dir: str, slot: int) -> str:
    return os.path.join(base_dir, f"save_slot_{slot}.json")


def load_slot(base_dir: str, slot: int) -> Optional[SaveSlot]:
    p = save_path(base_dir, slot)
    if not os.path.exists(p):
        return None

    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)

    # ------------------------------------------------------------------
    # Backwards compatibility / schema hygiene
    # ------------------------------------------------------------------
    # Older builds might have written different keys (ex: last_played_lesson).
    # Newer builds might add fields. Save loading should never crash.

    # Map legacy key -> current key
    if "last_played_day" not in d and "last_played_lesson" in d:
        try:
            d["last_played_day"] = int(d.get("last_played_lesson") or 1)
        except Exception:
            d["last_played_day"] = 1

    if "code_by_level" not in d:
        d["code_by_level"] = {}

    if "node_unlocked" not in d:
        # Back-compat: older saves only tracked week_unlocked. Assume day 1 of that week.
        try:
            wu = int(d.get("week_unlocked", 1) or 1)
        except Exception:
            wu = 1
        d["node_unlocked"] = max(0, (wu - 1) * 5)

    if "last_played_day" not in d:
        d["last_played_day"] = 1

    if "seen_dialogue" not in d:
        d["seen_dialogue"] = []

    # Drop unknown keys so older/newer saves don't explode the dataclass.
    allowed = set(SaveSlot.__annotations__.keys())
    d_clean = {k: v for k, v in d.items() if k in allowed}

    return SaveSlot(**d_clean)


def write_slot(base_dir: str, s: SaveSlot) -> None:
    p = save_path(base_dir, s.slot)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(asdict(s), f, indent=2)


def delete_slot(base_dir: str, slot: int) -> None:
    p = save_path(base_dir, slot)
    if os.path.exists(p):
        os.remove(p)


def save_level_code(base_dir: str, s: SaveSlot, level_key: str, code_text: str) -> None:
    s.code_by_level[level_key] = code_text
    write_slot(base_dir, s)
