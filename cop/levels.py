\
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Level:
    id: int
    week: int
    title: str
    mentor: str
    dialogue_pre: str
    hint_text: str
    dialogue_post: str
    allowed_api: list[str]
    start_entities: list[dict]
    objective: dict
    starter_code: str

def load_levels(path: str) -> tuple[dict, list[Level]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    lvls = []
    for d in data["levels"]:
        lvls.append(Level(
            id=d["id"],
            week=d["week"],
            title=d["title"],
            mentor=d["mentor"],
            dialogue_pre=d["dialogue_pre"],
            hint_text=d["hint_text"],
            dialogue_post=d["dialogue_post"],
            allowed_api=d["allowed_api"],
            start_entities=d["start_entities"],
            objective=d["objective"],
            starter_code=d["starter_code"],
        ))
    return data["meta"], lvls
