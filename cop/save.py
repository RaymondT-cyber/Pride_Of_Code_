\
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
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

def save_path(base_dir: str, slot: int) -> str:
    return os.path.join(base_dir, f"save_slot_{slot}.json")

def load_slot(base_dir: str, slot: int) -> Optional[SaveSlot]:
    p = save_path(base_dir, slot)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    return SaveSlot(**d)

def write_slot(base_dir: str, s: SaveSlot) -> None:
    p = save_path(base_dir, s.slot)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(asdict(s), f, indent=2)

def delete_slot(base_dir: str, slot: int) -> None:
    p = save_path(base_dir, slot)
    if os.path.exists(p):
        os.remove(p)
