\
from __future__ import annotations

from dataclasses import dataclass
import math as _math
from typing import Dict, List, Tuple, Iterable

@dataclass
class Entity:
    name: str
    section: str
    x: int
    y: int

@dataclass
class StepAction:
    entity: str
    start: Tuple[int,int]
    end: Tuple[int,int]
    counts: int
    t: int = 0  # progressed counts

class Band:
    """Band API v1: safe, schedule-based calls (player code queues actions; sim executes deterministically)."""
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.queue: List[StepAction] = []
        self.time = 0
        self.math = _math  # safe math proxy (no import needed)

    # --- entity management
    def spawn(self, name: str, section: str, x: int, y: int) -> None:
        self.entities[name] = Entity(name=name, section=section, x=int(x), y=int(y))

    def set_pos(self, name: str, x: int, y: int) -> None:
        e = self.entities.get(name)
        if not e:
            self.spawn(name, section="GEN", x=x, y=y)
        else:
            e.x, e.y = int(x), int(y)

    def get_pos(self, name: str) -> Tuple[int,int]:
        e = self.entities[name]
        return (e.x, e.y)

    def get_all(self) -> List[str]:
        return list(self.entities.keys())

    def is_occupied(self, x: int, y: int) -> bool:
        for e in self.entities.values():
            if e.x == int(x) and e.y == int(y):
                return True
        return False

    # --- schedule API
    def step_to(self, who: str | Iterable[str], x: int, y: int, counts: int=8) -> None:
        counts = max(1, int(counts))
        if isinstance(who, str):
            names = [who]
        else:
            names = list(who)
        for n in names:
            if n not in self.entities:
                self.spawn(n, section="GEN", x=0, y=0)
            e = self.entities[n]
            self.queue.append(StepAction(entity=n, start=(e.x,e.y), end=(int(x),int(y)), counts=counts))

    def wait(self, counts: int=8) -> None:
        # wait is represented as an action with no entity; sim will just tick
        self.queue.append(StepAction(entity="__WAIT__", start=(0,0), end=(0,0), counts=max(1,int(counts))))

    # --- sim
    def reset_actions(self) -> None:
        self.queue.clear()
        self.time = 0


    def snapshot(self) -> dict[str, tuple[int,int]]:
        return {k: (e.x, e.y) for k, e in self.entities.items()}

    def apply_snapshot(self, snap: dict[str, tuple[int,int]]) -> None:
        # keep existing entities, update coords, and spawn missing ones if needed
        for name, (x, y) in snap.items():
            if name in self.entities:
                self.entities[name].x = int(x)
                self.entities[name].y = int(y)
            else:
                self.spawn(name, section="GEN", x=int(x), y=int(y))

    def make_timeline(self, max_counts: int=128) -> list[dict[str, tuple[int,int]]]:
        """
        Build a deterministic per-count timeline WITHOUT permanently mutating entity positions.
        Returns list of snapshots, including the initial snapshot at index 0.
        """
        initial = self.snapshot()
        timeline: list[dict[str, tuple[int,int]]] = [dict(initial)]
        t_global = 0

        # local mutable positions
        pos = dict(initial)

        for act in self.queue:
            for t in range(act.counts):
                t_global += 1
                if t_global > max_counts:
                    break
                if act.entity != "__WAIT__":
                    sx, sy = act.start
                    ex, ey = act.end
                    fx = sx + (ex - sx) * (t+1) / act.counts
                    fy = sy + (ey - sy) * (t+1) / act.counts
                    pos[act.entity] = (int(round(fx)), int(round(fy)))
                timeline.append(dict(pos))
            if t_global > max_counts:
                break

        # restore entities to initial positions
        self.apply_snapshot(initial)
        return timeline

    def simulate(self, max_counts: int=64) -> None:
        """Run queued actions sequentially (MVP)."""
        self.time = 0
        for act in self.queue:
            for t in range(act.counts):
                self.time += 1
                if self.time > max_counts:
                    return
                if act.entity == "__WAIT__":
                    continue
                e = self.entities.get(act.entity)
                if not e:
                    continue
                # linear interpolation per count
                fx = act.start[0] + (act.end[0] - act.start[0]) * (t+1) / act.counts
                fy = act.start[1] + (act.end[1] - act.start[1]) * (t+1) / act.counts
                e.x = int(round(fx))
                e.y = int(round(fy))
