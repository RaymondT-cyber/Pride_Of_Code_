from __future__ import annotations

"""
field_renderer.py
─────────────────
Drop-in field drawing module for GameScene.

Usage in scenes.py — replace the raw field drawing block with:

    from .field_renderer import draw_field
    ...
    draw_field(
        dst        = dst,
        rect       = self.field_rect,
        band       = self.band,
        objective  = self.level.objective if self.level else None,
        assets     = self.game.assets,
        timeline_i = self.timeline_i,
        timeline   = self.timeline,
    )
"""

import pygame
from .constants import (
    OUTLINE_BLACK, OFF_WHITE, WHITE, GOLD_PRIMARY, GOLD_DIM,
    FIELD_GREEN, FIELD_GREEN_DARK, FIELD_LINE, FIELD_50_LINE, FIELD_HASH,
    ALERT_RED, SUCCESS_GREEN,
    SECTION_COLORS,
    FIELD_W, FIELD_H,
    FRONT_HASH, BACK_HASH,
    YARD_LINE_LABELS,
)


# ─── tuning constants ────────────────────────────────────────────────────────
DOT_SIZE      = 5     # entity square half-size (px)
TARGET_SIZE   = 6     # ghost target half-size (px)
LABEL_OFFSET  = 8     # px above entity center for name label


def draw_field(
    dst:        pygame.Surface,
    rect:       pygame.Rect,
    band:       object,
    objective:  dict | None,
    assets:     object,
    timeline_i: int = 0,
    timeline:   list | None = None,
) -> None:
    """
    Draw the full field panel:
      1. Outer frame + turf
      2. Alternating yard-line stripes
      3. Yard lines + hash marks
      4. Yard-line number labels
      5. Ghost target dot(s)
      6. Entity dots with section colors + name labels
      7. Collision highlights
    """
    inner = rect.inflate(-4, -4)

    # 1. Frame + base turf
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, 2)
    pygame.draw.rect(dst, FIELD_GREEN, inner)

    cell_w = inner.width  / FIELD_W
    cell_h = inner.height / FIELD_H

    def fx(x: float) -> int:
        return inner.left + int(x * cell_w)

    def fy(y: float) -> int:
        return inner.top + int(y * cell_h)

    # 2. Alternating 5-yard stripes (subtle dark/light banding)
    for stripe in range(0, FIELD_W, 8):
        sx  = fx(stripe)
        ex  = fx(min(stripe + 4, FIELD_W))
        band_rect = pygame.Rect(sx, inner.top, ex - sx, inner.height)
        pygame.draw.rect(dst, FIELD_GREEN_DARK, band_rect)

    # 3a. Hash-mark lines (horizontal, subtle)
    for hy in (FRONT_HASH, BACK_HASH):
        pygame.draw.line(dst, FIELD_HASH,
                         (inner.left,  fy(hy)),
                         (inner.right, fy(hy)), 1)

    # 3b. Yard lines (vertical)
    for gx in range(0, FIELD_W + 1, 4):
        px  = fx(gx)
        col = FIELD_50_LINE if gx == FIELD_W // 2 else FIELD_LINE
        lw  = 2 if gx == FIELD_W // 2 else 1
        pygame.draw.line(dst, col, (px, inner.top), (px, inner.bottom), lw)

    # 4. Yard-line number labels (very small, clipped)
    font = getattr(assets, "font_code_s", None) or getattr(assets, "font_s", None)
    if font:
        prev_clip = dst.get_clip()
        dst.set_clip(inner)
        for gx, label in YARD_LINE_LABELS:
            px = fx(gx)
            t  = font.render(label, False, (180, 200, 180))
            # top label
            dst.blit(t, (px - t.get_width() // 2, inner.top + 2))
            # bottom label
            dst.blit(t, (px - t.get_width() // 2, inner.bottom - t.get_height() - 2))
        dst.set_clip(prev_clip)

    # 5. Ghost target(s) — show where entity needs to land
    if objective:
        _draw_ghost_targets(dst, inner, fx, fy, objective)

    # 6. Collect current positions (from timeline snapshot if available)
    positions: dict[str, tuple[int, int]] = {}
    entities = getattr(band, "entities", {})

    if timeline and 0 <= timeline_i < len(timeline):
        snap = timeline[timeline_i]
        for name, pos in snap.items():
            positions[name] = pos
    else:
        for name, e in entities.items():
            positions[name] = (e.x, e.y)

    # 7. Detect collisions
    seen: dict[tuple[int,int], list[str]] = {}
    for name, pos in positions.items():
        seen.setdefault(pos, []).append(name)
    collisions = {pos for pos, names in seen.items() if len(names) > 1}

    # 8. Draw entities
    prev_clip = dst.get_clip()
    dst.set_clip(inner)
    for name, (ex, ey) in positions.items():
        _draw_entity(dst, inner, fx, fy, name, ex, ey, entities, collisions, font, assets)
    dst.set_clip(prev_clip)


# ─── private helpers ─────────────────────────────────────────────────────────

def _draw_ghost_targets(
    dst:   pygame.Surface,
    inner: pygame.Rect,
    fx,
    fy,
    obj:   dict,
) -> None:
    """Draw star-shaped ghost target(s) from objective dict."""
    targets: list[tuple[int, int]] = []

    if "target" in obj:
        tx, ty = obj["target"]
        targets.append((tx, ty))
    if "targets" in obj:           # future: multi-target objectives
        for t in obj["targets"]:
            targets.append(tuple(t))

    prev_clip = dst.get_clip()
    dst.set_clip(inner)

    for tx, ty in targets:
        px = fx(tx)
        py = fy(ty)
        s  = TARGET_SIZE

        # Cross/star outline in dim gold
        pygame.draw.line(dst, GOLD_DIM, (px - s, py),     (px + s, py),     1)
        pygame.draw.line(dst, GOLD_DIM, (px,     py - s), (px,     py + s), 1)

        # Diamond outline
        pts = [(px, py - s), (px + s, py), (px, py + s), (px - s, py)]
        pygame.draw.polygon(dst, GOLD_DIM, pts, 1)

        # Bright center pixel
        pygame.draw.rect(dst, GOLD_PRIMARY, pygame.Rect(px - 1, py - 1, 3, 3))

    dst.set_clip(prev_clip)


def _draw_entity(
    dst:        pygame.Surface,
    inner:      pygame.Rect,
    fx,
    fy,
    name:       str,
    ex:         int,
    ey:         int,
    entities:   dict,
    collisions: set,
    font,
    assets,
) -> None:
    """Draw one entity as a colored square with name label."""
    px = fx(ex)
    py = fy(ey)
    s  = DOT_SIZE

    # Determine section color
    section = "GEN"
    if name in entities:
        section = getattr(entities[name], "section", "GEN")
    col = SECTION_COLORS.get(section, SECTION_COLORS["GEN"])

    in_collision = (ex, ey) in collisions

    # Shadow
    pygame.draw.rect(dst, OUTLINE_BLACK, pygame.Rect(px - s + 1, py - s + 1, s * 2, s * 2))

    # Body
    body_col = ALERT_RED if in_collision else col
    pygame.draw.rect(dst, body_col, pygame.Rect(px - s, py - s, s * 2, s * 2))

    # Highlight edge (top-left bevel)
    hi = _lighten(body_col, 60)
    pygame.draw.line(dst, hi, (px - s, py - s), (px + s - 1, py - s), 1)
    pygame.draw.line(dst, hi, (px - s, py - s), (px - s, py + s - 1), 1)

    # Outline
    pygame.draw.rect(dst, OUTLINE_BLACK, pygame.Rect(px - s, py - s, s * 2, s * 2), 1)

    # Name label (tiny, above entity)
    if font:
        label = name
        t = font.render(label, False, WHITE)
        s2 = font.render(label, False, OUTLINE_BLACK)
        lx = px - t.get_width() // 2
        ly = py - s - LABEL_OFFSET
        # Keep label inside inner rect
        lx = max(inner.left, min(lx, inner.right - t.get_width()))
        ly = max(inner.top, min(ly, inner.bottom - t.get_height()))
        dst.blit(s2, (lx + 1, ly + 1))
        dst.blit(t,  (lx,     ly))


def _lighten(color: tuple[int,int,int], amount: int) -> tuple[int,int,int]:
    return tuple(min(255, c + amount) for c in color)  # type: ignore