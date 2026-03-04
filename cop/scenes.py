"""
scenes_patch.py
───────────────
This file documents the EXACT changes needed in scenes.py.
Copy-paste each section into the corresponding location.

CHANGE 1 — Add field_renderer import at the top of scenes.py
CHANGE 2 — Replace the raw field drawing block in GameScene.draw()
CHANGE 3 — New ScoreScene with judge sheet + breakdown
CHANGE 4 — New BattlePreScene (pre-battle opponent card)
CHANGE 5 — _objective_met() and _objective_text() upgrades
"""

# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 1 — Add near the top of scenes.py, with the other imports
# ══════════════════════════════════════════════════════════════════════════════

# from .field_renderer import draw_field
# from .judging import judge_battle
# from .ui import draw_judge_sheet, draw_pp_chip, draw_week_node


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 2
# In GameScene.draw(), find the block that starts:
#
#     fr = self.field_rect
#     pygame.draw.rect(dst, OUTLINE_BLACK, fr, 2)
#     inner = fr.inflate(-4, -4)
#     pygame.draw.rect(dst, (40, 120, 60), inner)
#     ...
#     for e in self.band.entities.values():
#         ...
#
# Replace that entire block (through the entity loop) with:
# ══════════════════════════════════════════════════════════════════════════════

def _draw_field_section(self, dst):
    """
    Drop-in replacement for the raw field block in GameScene.draw().
    Paste the body of this function where the old field code was.
    """
    from .field_renderer import draw_field   # local import avoids circular refs

    draw_field(
        dst        = dst,
        rect       = self.field_rect,
        band       = self.band,
        objective  = self.level.objective if self.level else None,
        assets     = self.game.assets,
        timeline_i = self.timeline_i,
        timeline   = self.timeline,
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 3 — _objective_met() replacement for GameScene
# Replace the existing _objective_met method with this one.
# ══════════════════════════════════════════════════════════════════════════════

def _objective_met(self) -> bool:
    """Generic objective checker driven by Level.objective dict."""
    if self.sandbox or not self.level:
        return True

    obj  = self.level.objective
    otype = obj.get("type", "position")

    entity = obj.get("entity", "DM")
    target = obj.get("target")

    # Final position check (all types use this)
    if target:
        tx, ty = target
        pos = None
        try:
            pos = self.band.get_pos(entity)
        except Exception:
            pass
        if pos != (tx, ty):
            return False

    # Count-specific checks
    total_counts = sum(
        getattr(a, "counts", 0) for a in getattr(self.band, "queue", [])
    )
    if otype in ("timing", "phrase", "battle"):
        tc = obj.get("total_counts")
        if tc is not None and total_counts != tc:
            return False

    # Minimum moves
    min_moves = obj.get("min_moves")
    if min_moves:
        moves = [
            a for a in getattr(self.band, "queue", [])
            if getattr(a, "entity", "") == entity
            and getattr(a, "entity", "") != "__WAIT__"
        ]
        if len(moves) < min_moves:
            return False

    # Requires wait
    if obj.get("requires_wait"):
        waits = [
            a for a in getattr(self.band, "queue", [])
            if getattr(a, "entity", "") == "__WAIT__"
        ]
        if not waits:
            return False

    return True


def _objective_text(self) -> str:
    """Return a one-line objective summary for the HUD."""
    if self.sandbox:
        return "SANDBOX — no objective"
    if not self.level:
        return ""
    return self.level.objective.get("label", "")


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 4 — _award_points() replacement
# This version uses the generic judge_battle() + drives node_unlocked correctly.
# ══════════════════════════════════════════════════════════════════════════════

def _award_points(self) -> None:
    from .judging import judge_battle

    if self.sandbox or not self.level or not self.game.current_save:
        return

    s = self.game.current_save

    # Score the run
    obj   = self.level.objective
    score = judge_battle(self.band, self._last_lines_executed, obj)

    # Save code
    level_key = f"w{self.level.week}d{self.level.day}"
    s.code_by_level[level_key] = self.editor.get_text()

    if score.passed:
        earned = score.total
        s.pride_points += earned

        # Advance node_unlocked linearly
        node = (self.level.week - 1) * 5 + (self.level.day - 1)
        if node >= s.node_unlocked:
            s.node_unlocked = node + 1

        # Keep week/day in sync (derived from node)
        s.last_played_week = self.level.week
        s.last_played_day  = self.level.day

        # Unlock next week if this was day 5
        if self.level.day == 5 and self.level.week == s.week_unlocked:
            s.week_unlocked = min(17, s.week_unlocked + 1)

        from .save import write_slot
        write_slot(self.game.save_dir, s)
        self.game.push(ScoreScene(self.game, score))
    else:
        # Show score but don't advance
        from .save import write_slot
        write_slot(self.game.save_dir, s)
        self.game.push(ScoreScene(self.game, score))


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 5 — New ScoreScene
# Add this class to scenes.py (replace or extend the old ScoreScene).
# ══════════════════════════════════════════════════════════════════════════════

import pygame as _pg
from .constants import (
    LOGICAL_W, LOGICAL_H,
    CASA_BLUE, NAVY_DEEP, NAVY_SHADOW,
    GOLD_PRIMARY, GOLD_HILITE,
    WHITE, OFF_WHITE, OUTLINE_BLACK,
    SUCCESS_GREEN, ALERT_RED,
)
from .ui import Button, panel, draw_judge_sheet, draw_pp_chip


class ScoreScene:
    """
    Post-run judge sheet breakdown.
    Shows: grade, category bars, notes, pass/fail, continue button.
    """

    def __init__(self, game, score):
        self.game    = game
        self.score   = score

        btn_w, btn_h = 80, 16
        self.btn_continue = Button(
            rect    = _pg.Rect(LOGICAL_W // 2 - btn_w // 2, LOGICAL_H - 30, btn_w, btn_h),
            text    = "CONTINUE" if score.passed else "TRY AGAIN",
            primary = score.passed,
        )

    def handle(self, ev: _pg.event.Event) -> None:
        if ev.type == _pg.KEYDOWN and ev.key in (_pg.K_RETURN, _pg.K_SPACE, _pg.K_ESCAPE):
            self.game.pop()
            return
        if ev.type == _pg.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_continue.hit(ev.pos):
                self.game.pop()

    def update(self, dt: float) -> None:
        pass

    def draw(self, dst: _pg.Surface) -> None:
        # Dim the scene below
        overlay = _pg.Surface((LOGICAL_W, LOGICAL_H), _pg.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        dst.blit(overlay, (0, 0))

        # Main sheet panel
        sheet_rect = _pg.Rect(24, 20, LOGICAL_W - 48, LOGICAL_H - 50)
        draw_judge_sheet(dst, sheet_rect, self.score, self.game.assets)

        # Header accent bar
        hbar = _pg.Rect(sheet_rect.left, sheet_rect.top, sheet_rect.width, 14)
        _pg.draw.rect(dst, NAVY_DEEP, hbar)
        col = SUCCESS_GREEN if self.score.passed else ALERT_RED
        _pg.draw.line(dst, col, hbar.bottomleft, hbar.bottomright, 2)

        title_text = "SHOW REVIEW — PASSED" if self.score.passed else "SHOW REVIEW — TRY AGAIN"
        title_col  = SUCCESS_GREEN if self.score.passed else ALERT_RED
        font_m     = self.game.assets.font_m
        t  = font_m.render(title_text, False, title_col)
        s  = font_m.render(title_text, False, OUTLINE_BLACK)
        dst.blit(s, (hbar.left + 9, hbar.top + 1))
        dst.blit(t, (hbar.left + 8, hbar.top))

        # PP earned chip (top right)
        if self.score.passed:
            pp_rect = _pg.Rect(sheet_rect.right - 72, sheet_rect.top + 18, 68, 14)
            draw_pp_chip(dst, pp_rect, self.score.total, self.game.assets.font_s)

        # Continue button
        mx, my = self.game.mouse_logical
        self.btn_continue.draw(
            dst,
            self.game.assets.font_s,
            self.btn_continue.rect.collidepoint((mx, my)),
        )


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE 6 — New BattlePreScene  (show before the Week 5 battle)
# ══════════════════════════════════════════════════════════════════════════════

class BattlePreScene:
    """
    Opponent card screen shown before a battle level.
    Inspired by the Retro Bowl team matchup screen (Week 7 screenshot).
    Displays: your school vs opponent, mentor pep talk, PLAY button.
    """

    def __init__(self, game, level, on_play):
        self.game    = game
        self.level   = level
        self.on_play = on_play          # callback: starts the GameScene

        self._pages   = self._build_pages()
        self._page_i  = 0

        btn_w, btn_h = 64, 16
        self.btn_play = Button(
            rect    = _pg.Rect(LOGICAL_W - btn_w - 16, LOGICAL_H - 28, btn_w, btn_h),
            text    = "PLAY",
            primary = True,
        )
        self.btn_back = Button(
            rect    = _pg.Rect(16, LOGICAL_H - 28, 48, btn_h),
            text    = "BACK",
        )

    def _build_pages(self) -> list[tuple[str, str]]:
        obj      = self.level.objective
        opp      = obj.get("opponent", "???")
        opp_nick = obj.get("opponent_nickname", "")
        pages    = []

        pages.append((
            self.level.mentor,
            self.level.dialogue_pre,
        ))
        pages.append((
            "REQUIREMENTS",
            obj.get("label", ""),
        ))
        return pages

    def handle(self, ev: _pg.event.Event) -> None:
        if ev.type == _pg.KEYDOWN:
            if ev.key in (_pg.K_SPACE, _pg.K_RETURN):
                if self._page_i < len(self._pages) - 1:
                    self._page_i += 1
                else:
                    self._start()
            if ev.key == _pg.K_ESCAPE:
                self.game.pop()
                return
        if ev.type == _pg.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_play.hit(ev.pos):
                self._start()
            elif self.btn_back.hit(ev.pos):
                self.game.pop()

    def _start(self) -> None:
        self.game.pop()
        self.on_play()

    def update(self, dt: float) -> None:
        pass

    def draw(self, dst: _pg.Surface) -> None:
        dst.fill(CASA_BLUE)

        obj      = self.level.objective
        opp      = obj.get("opponent",          "???")
        opp_nick = obj.get("opponent_nickname", "")
        school   = "CASA GRANDE UNION HS"
        mascot   = "COUGARS"

        # ── Header ──────────────────────────────────────────────────────────
        hbar = _pg.Rect(0, 0, LOGICAL_W, 18)
        _pg.draw.rect(dst, NAVY_DEEP, hbar)
        font_m = self.game.assets.font_m
        font_s = self.game.assets.font_s
        font_l = self.game.assets.font_l

        week_text = f"★ WEEK {self.level.week} · DAY {self.level.day} — BATTLE ★"
        t = font_m.render(week_text, False, GOLD_PRIMARY)
        dst.blit(t, (LOGICAL_W // 2 - t.get_width() // 2, 2))

        # ── VS card ──────────────────────────────────────────────────────────
        card_y  = 24
        card_h  = 80
        half_w  = LOGICAL_W // 2

        # Left card — player school
        left_card = _pg.Rect(12, card_y, half_w - 18, card_h)
        _pg.draw.rect(dst, NAVY_DEEP,     left_card)
        _pg.draw.rect(dst, GOLD_PRIMARY,  left_card, 2)

        t = font_m.render(school, False, WHITE)
        if t.get_width() > left_card.width - 8:
            font_s_r = self.game.assets.font_s
            t = font_s_r.render(school, False, WHITE)
        dst.blit(t, (left_card.centerx - t.get_width() // 2, left_card.top + 8))

        t2 = font_l.render(mascot, False, GOLD_PRIMARY) if font_l else font_m.render(mascot, False, GOLD_PRIMARY)
        dst.blit(t2, (left_card.centerx - t2.get_width() // 2, left_card.top + 24))

        # Right card — opponent
        right_card = _pg.Rect(half_w + 6, card_y, half_w - 18, card_h)
        _pg.draw.rect(dst, NAVY_DEEP,    right_card)
        _pg.draw.rect(dst, (100, 80, 80), right_card, 2)

        t = font_m.render(opp, False, WHITE)
        if t.get_width() > right_card.width - 8:
            t = self.game.assets.font_s.render(opp, False, WHITE)
        dst.blit(t, (right_card.centerx - t.get_width() // 2, right_card.top + 8))

        t3 = font_m.render(f'"{opp_nick}"', False, OFF_WHITE)
        dst.blit(t3, (right_card.centerx - t3.get_width() // 2, right_card.top + 30))

        # VS medallion
        vs_x, vs_y = LOGICAL_W // 2, card_y + card_h // 2
        _pg.draw.circle(dst, NAVY_DEEP,   (vs_x, vs_y), 14)
        _pg.draw.circle(dst, GOLD_PRIMARY,(vs_x, vs_y), 14, 2)
        vt = font_m.render("VS", False, GOLD_PRIMARY)
        dst.blit(vt, (vs_x - vt.get_width() // 2, vs_y - vt.get_height() // 2))

        # ── Dialogue page ────────────────────────────────────────────────────
        page_rect = _pg.Rect(12, card_y + card_h + 8, LOGICAL_W - 24, 56)
        _pg.draw.rect(dst, NAVY_DEEP,   page_rect)
        _pg.draw.rect(dst, NAVY_SHADOW, page_rect, 1)

        if self._page_i < len(self._pages):
            speaker, text = self._pages[self._page_i]
            sp_t = font_s.render(speaker + ":", False, GOLD_PRIMARY)
            dst.blit(sp_t, (page_rect.left + 6, page_rect.top + 4))
            text_rect = _pg.Rect(
                page_rect.left + 6,
                page_rect.top + 4 + sp_t.get_height() + 2,
                page_rect.width - 12,
                page_rect.height - sp_t.get_height() - 12,
            )
            from .scenes import draw_text_box
            draw_text_box(dst, text_rect, text, font_s, color=OFF_WHITE, padding=0, max_lines=4)

        # Page dots
        for i in range(len(self._pages)):
            col = GOLD_PRIMARY if i == self._page_i else NAVY_SHADOW
            _pg.draw.circle(dst, col, (LOGICAL_W // 2 - (len(self._pages) - 1) * 6 + i * 12, page_rect.bottom + 6), 3)

        # ── Buttons ──────────────────────────────────────────────────────────
        mx, my = self.game.mouse_logical
        self.btn_play.draw(dst, font_s, self.btn_play.rect.collidepoint((mx, my)))
        self.btn_back.draw(dst, font_s, self.btn_back.rect.collidepoint((mx, my)))

        # Space to continue hint
        hint = font_s.render("[SPACE] next", False, (80, 82, 90))
        dst.blit(hint, (LOGICAL_W // 2 - hint.get_width() // 2, LOGICAL_H - 12))