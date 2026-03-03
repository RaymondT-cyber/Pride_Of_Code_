from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Level:
    id: int
    week: int
    lesson: int
    title: str
    mentor: str
    dialogue_pre: str
    hint_text: str
    dialogue_post: str
    allowed_api: list[str]
    start_entities: list[dict]
    objective: dict
    starter_code: str

    # Optional extras
    opponent_code: Optional[str] = None
    csta: list[str] | None = None


def load_levels(path: str) -> tuple[dict[str, Any], list[Level]]:
    """Load levels.json, tolerating older schemas."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("meta", {})
    lvls: list[Level] = []

    for d in data.get("levels", []):
        lvls.append(
            Level(
                id=int(d["id"]),
                week=int(d.get("week", 1)),
                lesson=int(d.get("lesson", 1)),
                title=str(d.get("title", "")),
                mentor=str(d.get("mentor", "")),
                dialogue_pre=str(d.get("dialogue_pre", "")),
                hint_text=str(d.get("hint_text", "")),
                dialogue_post=str(d.get("dialogue_post", "")),
                allowed_api=list(d.get("allowed_api", [])),
                start_entities=list(d.get("start_entities", [])),
                objective=dict(d.get("objective", {})),
                starter_code=str(d.get("starter_code", "")),
                opponent_code=d.get("opponent_code"),
                csta=list(d.get("csta", [])) if d.get("csta") is not None else [],
            )
        )

    return meta, lvls
