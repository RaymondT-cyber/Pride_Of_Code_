from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Optional


def _default_lesson_unlocks() -> dict[str, int]:
    # Week 1, Lesson 1 unlocked by default.
    return {"1": 1}


@dataclass
class SaveSlot:
    slot: int

    # Progress
    week_unlocked: int = 1
    last_played_week: int = 1
    last_played_lesson: int = 1

    # For the currently unlocked week, this stores how many lessons are unlocked.
    # Keys are strings for stable JSON storage.
    lesson_unlocked_by_week: dict[str, int] = field(default_factory=_default_lesson_unlocks)

    # Rewards
    pride_points: int = 0
    streak: int = 0
    hints_used: int = 0

    # Profile
    name: str = "DIRECTOR"

    # Persisted code per lesson (keyed by 'w{week}_l{lesson}')
    code_by_level: dict[str, str] = field(default_factory=dict)

    # Story flags
    intro_seen: bool = False
    week1_briefing_seen: bool = False
    week1_battle_intro_seen: bool = False
    week1_battle_cleared: bool = False

    # Legacy story flags (kept for backward compatibility)
    week1_lesson_seen: bool = False
    week2_briefing_seen: bool = False
    week2_lesson_seen: bool = False


def save_path(base_dir: str, slot: int) -> str:
    return os.path.join(base_dir, f"save_slot_{slot}.json")


def _normalize_lesson_unlocks(d: dict) -> None:
    """Back-compat: ensure lesson_unlocked_by_week exists and looks sane."""
    week_unlocked = int(d.get("week_unlocked", 1) or 1)

    # Convert keys to strings (in case older saves wrote ints).
    lubw = d.get("lesson_unlocked_by_week")
    if isinstance(lubw, dict):
        d["lesson_unlocked_by_week"] = {str(k): int(v) for k, v in lubw.items()}
    else:
        d["lesson_unlocked_by_week"] = _default_lesson_unlocks()

    # If an older save only tracked weeks, infer lesson unlocks.
    # - all prior weeks are considered "completed" (5 lessons unlocked)
    # - current unlocked week has lesson 1 unlocked
    lubw = d["lesson_unlocked_by_week"]
    for w in range(1, week_unlocked):
        lubw[str(w)] = max(5, int(lubw.get(str(w), 5)))
    lubw.setdefault(str(week_unlocked), int(lubw.get(str(week_unlocked), 1) or 1))

    # Clamp unlocked lessons to 1..5
    for k in list(lubw.keys()):
        try:
            lubw[k] = max(1, min(5, int(lubw[k])))
        except Exception:
            lubw[k] = 1


def load_slot(base_dir: str, slot: int) -> Optional[SaveSlot]:
    p = save_path(base_dir, slot)
    if not os.path.exists(p):
        return None

    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)

    # Backward compatibility
    if "code_by_level" not in d or not isinstance(d.get("code_by_level"), dict):
        d["code_by_level"] = {}

    if "last_played_lesson" not in d:
        d["last_played_lesson"] = 1

    _normalize_lesson_unlocks(d)

    return SaveSlot(**d)


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
