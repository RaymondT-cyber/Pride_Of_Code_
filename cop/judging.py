from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ──────────────────────────────────────────────────────────────────────────────
# Score model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class JudgeScore:
    total: int
    technique: int
    show_quality: int
    efficiency: int
    creativity: int
    notes: list[str] = field(default_factory=list)
    passed: bool = False

    def grade(self) -> str:
        if self.total >= 90:  return "A+"
        if self.total >= 80:  return "A"
        if self.total >= 70:  return "B"
        if self.total >= 60:  return "C"
        return "D"


# ──────────────────────────────────────────────────────────────────────────────
# Generic judge — driven by the Level's objective dict
# ──────────────────────────────────────────────────────────────────────────────

def judge_battle(band: Any, lines_executed: int, objective: dict) -> JudgeScore:
    """
    Drive scoring entirely from the Level.objective dict.
    Supports objective types: position, position_and_moves, timing, phrase, battle.
    """
    obj_type = objective.get("type", "position")

    if obj_type == "battle":
        return _judge_battle_week(band, lines_executed, objective)
    if obj_type == "phrase":
        return _judge_phrase(band, lines_executed, objective)
    if obj_type == "timing":
        return _judge_timing(band, lines_executed, objective)
    if obj_type == "position_and_moves":
        return _judge_position_and_moves(band, lines_executed, objective)
    # Default: simple position check
    return _judge_position(band, lines_executed, objective)


# ──────────────────────────────────────────────────────────────────────────────
# Objective type handlers
# ──────────────────────────────────────────────────────────────────────────────

def _judge_position(band: Any, lines_executed: int, obj: dict) -> JudgeScore:
    """Day 1 style: just land the entity at the right dot."""
    notes: list[str] = []
    technique = 0
    show_quality = 0
    efficiency = 0
    creativity = 10

    entity  = obj.get("entity", "DM")
    tx, ty  = obj.get("target", [0, 0])

    # Technique: did they call step_to at all?
    moves = _get_moves(band, entity)
    if moves:
        technique = 50
        notes.append("✅ Technique: move command used.")
    else:
        notes.append("❌ Technique: no step_to found. Call band.step_to() to move.")

    # Show quality: correct final position
    pos = _get_pos(band, entity)
    if pos == (tx, ty):
        show_quality = 25
        notes.append(f"✅ Show Quality: {entity} hit the target ({tx}, {ty}).")
    else:
        notes.append(f"❌ Show Quality: {entity} ended at {pos}. Target is ({tx}, {ty}).")

    # Efficiency
    efficiency, eff_note = _score_efficiency(lines_executed, target=8)
    notes.append(eff_note)

    total = technique + show_quality + efficiency + creativity
    return JudgeScore(
        total=total, technique=technique, show_quality=show_quality,
        efficiency=efficiency, creativity=creativity, notes=notes,
        passed=(total >= 60 and pos == (tx, ty)),
    )


def _judge_position_and_moves(band: Any, lines_executed: int, obj: dict) -> JudgeScore:
    """Day 2 style: land at target AND use multiple moves."""
    notes: list[str] = []
    technique = 0
    show_quality = 0
    efficiency = 0
    creativity = 10

    entity    = obj.get("entity", "DM")
    tx, ty    = obj.get("target", [0, 0])
    min_moves = obj.get("min_moves", 2)

    moves = _get_moves(band, entity)

    # Technique: move count
    if len(moves) >= min_moves:
        technique += 30
        notes.append(f"✅ Technique: {len(moves)} distinct moves. (Need {min_moves}+)")
    else:
        notes.append(f"❌ Technique: {len(moves)} move(s). Need at least {min_moves}.")

    # Technique: all moves have valid counts
    bad_counts = [m for m in moves if getattr(m, "counts", 0) <= 0]
    if not bad_counts and moves:
        technique += 20
        notes.append("✅ Technique: all counts are positive.")
    elif bad_counts:
        notes.append("⚠️ Technique: some moves have 0 counts — DM won't move.")

    # Show quality: final position
    pos = _get_pos(band, entity)
    if pos == (tx, ty):
        show_quality = 25
        notes.append(f"✅ Show Quality: {entity} hit ({tx}, {ty}).")
    else:
        notes.append(f"❌ Show Quality: {entity} ended at {pos}. Target is ({tx}, {ty}).")

    efficiency, eff_note = _score_efficiency(lines_executed, target=10)
    notes.append(eff_note)

    total = technique + show_quality + efficiency + creativity
    return JudgeScore(
        total=total, technique=technique, show_quality=show_quality,
        efficiency=efficiency, creativity=creativity, notes=notes,
        passed=(total >= 60 and pos == (tx, ty) and len(moves) >= min_moves),
    )


def _judge_timing(band: Any, lines_executed: int, obj: dict) -> JudgeScore:
    """Day 3 style: correct total counts + correct final position."""
    notes: list[str] = []
    technique = 0
    show_quality = 0
    efficiency = 0
    creativity = 10

    entity        = obj.get("entity", "DM")
    tx, ty        = obj.get("target", [0, 0])
    target_counts = obj.get("total_counts", 12)
    min_moves     = obj.get("min_moves", 2)

    moves        = _get_moves(band, entity)
    total_counts = _total_counts(band)

    # Technique: move count
    if len(moves) >= min_moves:
        technique += 25
        notes.append(f"✅ Technique: {len(moves)} moves.")
    else:
        notes.append(f"❌ Technique: need {min_moves}+ moves. Found {len(moves)}.")

    # Technique: total counts
    if total_counts == target_counts:
        technique += 25
        notes.append(f"✅ Timing: Exactly {target_counts} counts.")
    else:
        notes.append(
            f"⏱ Timing: {total_counts} counts. Target is {target_counts}. "
            f"{'Add' if total_counts < target_counts else 'Remove'} "
            f"{abs(target_counts - total_counts)} count(s)."
        )

    # Show quality: final dot
    pos = _get_pos(band, entity)
    if pos == (tx, ty):
        show_quality = 25
        notes.append(f"✅ Show Quality: {entity} hit ({tx}, {ty}).")
    else:
        notes.append(f"❌ Show Quality: {entity} ended at {pos}. Target ({tx}, {ty}).")

    efficiency, eff_note = _score_efficiency(lines_executed, target=8)
    notes.append(eff_note)

    total = technique + show_quality + efficiency + creativity
    return JudgeScore(
        total=total, technique=technique, show_quality=show_quality,
        efficiency=efficiency, creativity=creativity, notes=notes,
        passed=(total >= 60 and total_counts == target_counts and pos == (tx, ty)),
    )


def _judge_phrase(band: Any, lines_executed: int, obj: dict) -> JudgeScore:
    """Day 4 style: correct structure (moves + wait) + timing + final dot."""
    notes: list[str] = []
    technique = 0
    show_quality = 0
    efficiency = 0
    creativity = 10

    entity        = obj.get("entity", "DM")
    tx, ty        = obj.get("target", [0, 0])
    target_counts = obj.get("total_counts", 24)
    requires_wait = obj.get("requires_wait", True)

    moves        = _get_moves(band, entity)
    waits        = _get_waits(band)
    total_counts = _total_counts(band)

    # Technique: moves
    if len(moves) >= 2:
        technique += 20
        notes.append("✅ Technique: 2+ move commands.")
    else:
        notes.append("❌ Technique: need at least 2 step_to calls.")

    # Technique: wait
    if requires_wait:
        if waits:
            technique += 15
            notes.append("✅ Technique: wait (mark time) included in phrase.")
        else:
            notes.append("❌ Technique: no band.wait() found. Add a mark-time hold.")

    # Technique: total counts
    if total_counts == target_counts:
        technique += 15
        notes.append(f"✅ Timing: Exactly {target_counts} counts.")
    else:
        notes.append(
            f"⏱ Timing: {total_counts} counts. Target {target_counts}. "
            f"Difference: {target_counts - total_counts:+d}."
        )

    # Show quality: final dot
    pos = _get_pos(band, entity)
    if pos == (tx, ty):
        show_quality = 25
        notes.append(f"✅ Show Quality: {entity} hit ({tx}, {ty}).")
    else:
        notes.append(f"❌ Show Quality: {entity} ended at {pos}. Target ({tx}, {ty}).")

    efficiency, eff_note = _score_efficiency(lines_executed, target=10)
    notes.append(eff_note)

    total = technique + show_quality + efficiency + creativity
    passed = (
        total >= 60
        and pos == (tx, ty)
        and total_counts == target_counts
        and (not requires_wait or bool(waits))
    )
    return JudgeScore(
        total=total, technique=technique, show_quality=show_quality,
        efficiency=efficiency, creativity=creativity, notes=notes,
        passed=passed,
    )


def _judge_battle_week(band: Any, lines_executed: int, obj: dict) -> JudgeScore:
    """
    Week 1 Battle rubric (also the generic battle template):
      Technique  50: 2+ moves AND exact count target
      Show Qual  25: entity ends at target
      Efficiency 15: code line count
      Creativity 10: free points Week 1 (confidence builder)
    """
    notes: list[str] = []
    technique = 0
    show_quality = 0
    efficiency = 0
    creativity = 10  # free this week

    entity        = obj.get("entity", "DM")
    tx, ty        = obj.get("target", [20, 11])
    target_counts = obj.get("total_counts", 16)
    min_moves     = obj.get("min_moves", 2)

    moves        = _get_moves(band, entity)
    total_counts = _total_counts(band)

    # Technique: move count
    if len(moves) >= min_moves:
        technique += 25
        notes.append(f"✅ Technique: {len(moves)} distinct moves.")
    else:
        notes.append(
            f"❌ Technique: {len(moves)} move(s). Need at least {min_moves}.\n"
            "   Tip: call band.step_to() more than once."
        )

    # Technique: exact timing
    if total_counts == target_counts:
        technique += 25
        notes.append(f"✅ Timing: Exactly {target_counts} counts.")
    elif total_counts == 0:
        notes.append(f"❌ Timing: 0 counts. Make sure your counts= values are > 0.")
    else:
        diff = target_counts - total_counts
        notes.append(
            f"⏱ Timing: {total_counts} counts. Target is {target_counts}. "
            f"{'Add' if diff > 0 else 'Remove'} {abs(diff)} count(s)."
        )

    # Show quality: final dot
    pos = _get_pos(band, entity)
    if pos == (tx, ty):
        show_quality = 25
        notes.append(f"✅ Show Quality: {entity} hit the final dot ({tx}, {ty}).")
    else:
        notes.append(
            f"❌ Show Quality: {entity} ended at {pos}. Final dot is ({tx}, {ty}).\n"
            f"   Tip: x={tx} is the 50-yard line — the strongest position on the field."
        )

    # Efficiency
    efficiency, eff_note = _score_efficiency(lines_executed, target=10)
    notes.append(eff_note)

    total = technique + show_quality + efficiency + creativity
    passed = (total >= 70)
    return JudgeScore(
        total=total, technique=technique, show_quality=show_quality,
        efficiency=efficiency, creativity=creativity, notes=notes,
        passed=passed,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Backwards-compatible alias (used by older scene code)
# ──────────────────────────────────────────────────────────────────────────────

def judge_week1_battle(player_band: Any, lines_executed: int) -> JudgeScore:
    """Legacy wrapper — delegates to the generic judge."""
    return _judge_battle_week(player_band, lines_executed, {
        "entity": "DM",
        "target": [20, 11],
        "total_counts": 16,
        "min_moves": 2,
    })


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_moves(band: Any, entity: str) -> list:
    """Return all non-wait queued actions for entity."""
    queue = getattr(band, "queue", [])
    return [
        a for a in queue
        if getattr(a, "entity", "") == entity
        and getattr(a, "entity", "") != "__WAIT__"
    ]


def _get_waits(band: Any) -> list:
    queue = getattr(band, "queue", [])
    return [a for a in queue if getattr(a, "entity", "") == "__WAIT__"]


def _total_counts(band: Any) -> int:
    queue = getattr(band, "queue", [])
    return sum(getattr(a, "counts", 0) for a in queue)


def _get_pos(band: Any, entity: str) -> tuple[int, int] | None:
    try:
        entities = getattr(band, "entities", {})
        if entity in entities:
            e = entities[entity]
            return (e.x, e.y)
    except Exception:
        pass
    return None


def _score_efficiency(lines_executed: int, target: int = 10) -> tuple[int, str]:
    """Return (points, note) for code efficiency."""
    if lines_executed <= target:
        return 15, "🧠 Code: Efficient. Clean instructions."
    elif lines_executed <= target * 2:
        return 8, f"🧠 Code: {lines_executed} lines. Could be tighter — but it works."
    else:
        return 0, f"🧠 Code: {lines_executed} lines is a lot. Look for repeated patterns."