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
    pride_points: int = 0
    streak: int = 0
    hints_used: int = 0
    name: str = "DIRECTOR"
    code_by_level: dict[str, str] = field(default_factory=dict)

    # Story flags
    intro_seen: bool = False
    week1_briefing_seen: bool = False
    week1_lesson_seen: bool = False


def save_path(base_dir: str, slot: int) -> str:
    return os.path.join(base_dir, f"save_slot_{slot}.json")


def load_slot(base_dir: str, slot: int) -> Optional[SaveSlot]:
    p = save_path(base_dir, slot)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    if "code_by_level" not in d:
        d["code_by_level"] = {}
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
