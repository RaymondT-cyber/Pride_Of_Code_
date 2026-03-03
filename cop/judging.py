from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class JudgeScore:
    total: int
    technique: int
    show_quality: int
    efficiency: int
    creativity: int
    notes: list[str]


def judge_week1_battle(player_band: "Band", lines_executed: int) -> JudgeScore:
    """
    Week 1 Invitational rubric.

    - Technique (50): 2+ moves AND exactly 16 total counts.
    - Show Quality (25): DM ends exactly at (20, 11).
    - Efficiency (15): keep it under ~10 executed lines.
    - Creativity (10): free points in week 1 (confidence builder).

    Notes are written in plain language so beginners can act on them.
    """
    notes: list[str] = []

    technique = 0
    show_quality = 0
    efficiency = 0
    creativity = 10

    total_counts = sum(act.counts for act in getattr(player_band, "queue", []))
    moves = [act for act in getattr(player_band, "queue", []) if getattr(act, "entity", "") != "__WAIT__"]

    # Technique: moves
    if len(moves) >= 2:
        technique += 25
        notes.append("✅ Technique: 2+ distinct moves.")
    else:
        notes.append("❌ Technique: You need at least 2 distinct moves.")

    # Technique: timing
    if total_counts == 16:
        technique += 25
        notes.append("✅ Timing: Exactly 16 counts.")
    else:
        notes.append(f"⏱ Timing: Your show was {total_counts} counts. Target is 16.")

    # Show quality: final dot
    end_pos = None
    try:
        if "DM" in getattr(player_band, "entities", {}):
            end_pos = player_band.get_pos("DM")
    except Exception:
        end_pos = None

    if end_pos == (20, 11):
        show_quality = 25
        notes.append("✅ Show Quality: DM hit the final dot (20, 11).")
    else:
        notes.append(f"❌ Show Quality: DM ended at {end_pos}. Final dot is (20, 11).")

    # Efficiency
    if lines_executed <= 10:
        efficiency = 15
        notes.append("🧠 Code: Efficient rehearsal. Clean instructions.")
    else:
        notes.append("🧠 Code: It works, but could be shorter next rep.")

    total = technique + show_quality + efficiency + creativity
    return JudgeScore(
        total=total,
        technique=technique,
        show_quality=show_quality,
        efficiency=efficiency,
        creativity=creativity,
        notes=notes,
    )
