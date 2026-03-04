from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import pygame

from .constants import (
    U,
    ALERT_RED,
    CASA_BLUE,
    GOLD_HILITE,
    GOLD_PRIMARY,
    GOLD_SHADOW,
    GOLD_DIM,
    NAVY_MID,
    NAVY_DEEP,
    NAVY_SHADOW,
    OFF_WHITE,
    OUTLINE_BLACK,
    SUCCESS_GREEN,
    WHITE,
)

# ─── NOTE: _wrap_safe_tokens MUST appear AFTER the pygame import ──────────────

def _wrap_safe_tokens(font: pygame.font.Font, text: str, max_w: int) -> list[str]:
    """Wrap text to max_w. Splits long tokens so nothing overflows."""
    out: list[str] = []
    for para in text.split('\n'):
        words = para.split(' ')
        line  = ''
        for w in words:
            test = (line + (' ' if line else '') + w) if w else (line + ' ').rstrip()
            if font.size(test)[0] <= max_w:
                line = test
                continue
            if line:
                out.append(line)
                line = ''
            if font.size(w)[0] <= max_w:
                line = w
            else:
                chunk = ''
                for ch in w:
                    t = chunk + ch
                    if font.size(t)[0] <= max_w:
                        chunk = t
                    else:
                        if chunk:
                            out.append(chunk)
                        chunk = ch
                line = chunk
        out.append(line)
    return out


def _load_ui_tokens() -> dict:
    token_path = Path(__file__).resolve().parents[1] / "data" / "ui_tokens.json"
    if token_path.exists():
        with token_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "spacing":   {"u": 8, "panel_padding": 8, "button_padding_x": 8, "button_padding_y": 4},
        "line":      {"frame": 2, "inset": 1},
        "shadow":    {"x": 1, "y": 1},
    }


UI_TOKENS = _load_ui_tokens()


# ──────────────────────────────────────────────────────────────────────────────
# Text utilities
# ──────────────────────────────────────────────────────────────────────────────

def wrap_text(
    font:              pygame.font.Font,
    text:              str,
    max_width:         int,
    preserve_newlines: bool = True,
) -> list[str]:
    """
    Word-wrap text to max_width. Handles very long tokens by character-splitting.
    Preserves indentation (useful for code samples in hint text).
    """
    if max_width <= 0:
        return [text]

    raw_lines = text.splitlines() if preserve_newlines else [text]
    out: list[str] = []

    for raw in raw_lines:
        if preserve_newlines and raw.strip() == "":
            out.append("")
            continue

        indent  = len(raw) - len(raw.lstrip(" "))
        prefix  = " " * indent
        content = raw.lstrip(" ")
        if content == "":
            out.append(prefix)
            continue

        words = content.split(" ")
        line  = prefix
        for w in words:
            candidate = (line + (" " if line.strip() else "") + w) if line != prefix else (prefix + w)
            if font.size(candidate)[0] <= max_width:
                line = candidate
                continue

            if line.strip():
                out.append(line)
                line = prefix

            chunk = ""
            for ch in w:
                test = prefix + chunk + ch
                if font.size(test)[0] <= max_width:
                    chunk += ch
                else:
                    if chunk:
                        out.append(prefix + chunk)
                    chunk = ch
            line = prefix + chunk

        out.append(line)

    return out


def ellipsize(font: pygame.font.Font, text: str, max_width: int) -> str:
    """Trim text with '…' so it fits max_width."""
    if font.size(text)[0] <= max_width:
        return text
    ell = "…"
    if font.size(ell)[0] > max_width:
        return ""
    lo, hi = 0, len(text)
    best   = ell
    while lo <= hi:
        mid  = (lo + hi) // 2
        cand = text[:mid].rstrip() + ell
        if font.size(cand)[0] <= max_width:
            best = cand
            lo   = mid + 1
        else:
            hi = mid - 1
    return best


def blit_text_lines(
    dst:      pygame.Surface,
    rect:     pygame.Rect,
    font:     pygame.font.Font,
    lines:    list[str],
    color:    tuple = (255, 255, 255),
    shadow:   bool  = True,
    line_gap: int   = 2,
) -> None:
    """Draw pre-wrapped lines into rect, clipped."""
    prev = dst.get_clip()
    dst.set_clip(rect)
    y  = rect.top
    lh = font.get_linesize()
    for ln in lines:
        if y + lh > rect.bottom:
            break
        if ln == "":
            y += lh
            continue
        t = font.render(ln, False, color)
        if shadow:
            s = font.render(ln, False, OUTLINE_BLACK)
            dst.blit(s, (rect.left + 1, y + 1))
        dst.blit(t, (rect.left, y))
        y += lh + line_gap
    dst.set_clip(prev)


# ──────────────────────────────────────────────────────────────────────────────
# Widget: Button
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Button:
    rect:    pygame.Rect
    text:    str
    primary: bool        = False
    enabled: bool        = True
    hotkey:  str | None  = None

    def draw(
        self,
        dst:     pygame.Surface,
        font:    pygame.font.Font,
        hovered: bool,
        pressed: bool = False,
    ) -> None:
        face = GOLD_PRIMARY if self.primary else NAVY_MID
        hi   = GOLD_HILITE  if self.primary else OFF_WHITE
        sh   = GOLD_SHADOW  if self.primary else NAVY_SHADOW

        if not self.enabled:
            face, hi, sh = (80, 80, 80), (110, 110, 110), (60, 60, 60)

        frame_w  = int(UI_TOKENS["line"].get("frame", 2))
        pygame.draw.rect(dst, OUTLINE_BLACK, self.rect, frame_w)

        depth_off = 1 if pressed and self.enabled else 0
        inner     = self.rect.inflate(-4, -4).move(0, depth_off)
        pygame.draw.rect(dst, face, inner)

        # Bevel
        tl = sh if pressed else hi
        br = hi if pressed else sh
        pygame.draw.line(dst, tl, (inner.left, inner.top),      (inner.right - 1, inner.top),       1)
        pygame.draw.line(dst, tl, (inner.left, inner.top),      (inner.left,      inner.bottom - 1), 1)
        pygame.draw.line(dst, br, (inner.left, inner.bottom - 1),(inner.right - 1, inner.bottom - 1), 1)
        pygame.draw.line(dst, br, (inner.right - 1, inner.top), (inner.right - 1, inner.bottom - 1), 1)

        label = self.text if not self.hotkey else f"{self.text} [{self.hotkey}]"
        txt    = font.render(label, False, WHITE)
        shadow = font.render(label, False, OUTLINE_BLACK)
        tx     = self.rect.centerx - txt.get_width()  // 2
        ty     = self.rect.centery - txt.get_height() // 2 + depth_off
        sx, sy = UI_TOKENS["shadow"].get("x", 1), UI_TOKENS["shadow"].get("y", 1)
        dst.blit(shadow, (tx + sx, ty + sy))
        dst.blit(txt,    (tx, ty))

        if hovered and self.enabled:
            pygame.draw.rect(dst, OFF_WHITE, self.rect, 1)

    def hit(self, pos: tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(pos)


# ──────────────────────────────────────────────────────────────────────────────
# Panels & bars
# ──────────────────────────────────────────────────────────────────────────────

def panel(
    dst:   pygame.Surface,
    rect:  pygame.Rect,
    title: str | None,
    font:  pygame.font.Font,
) -> None:
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, int(UI_TOKENS["line"].get("frame", 2)))
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(dst, NAVY_DEEP,   inner)
    pygame.draw.rect(dst, NAVY_SHADOW, inner, int(UI_TOKENS["line"].get("inset", 1)))

    if title:
        t = font.render(title, False, WHITE)
        s = font.render(title, False, OUTLINE_BLACK)
        dst.blit(s, (rect.left + U + 1, rect.top + 1))
        dst.blit(t, (rect.left + U,     rect.top))


def header_bar(
    dst:   pygame.Surface,
    rect:  pygame.Rect,
    title: str,
    font:  pygame.font.Font,
    right: str | None = None,
) -> None:
    """Full-width header bar with optional right-side label."""
    pygame.draw.rect(dst, NAVY_DEEP, rect)
    pygame.draw.line(dst, OUTLINE_BLACK, rect.bottomleft, rect.bottomright, 1)

    t = font.render(title, False, WHITE)
    s = font.render(title, False, OUTLINE_BLACK)
    dst.blit(s, (rect.left + U + 1, rect.centery - t.get_height() // 2 + 1))
    dst.blit(t, (rect.left + U,     rect.centery - t.get_height() // 2))

    if right:
        rt = font.render(right, False, OFF_WHITE)
        dst.blit(rt, (rect.right - rt.get_width() - U, rect.centery - rt.get_height() // 2))


def progress_bar(
    dst:    pygame.Surface,
    rect:   pygame.Rect,
    value:  float,           # 0.0–1.0
    color:  tuple = None,
    label:  str | None = None,
    font:   pygame.font.Font | None = None,
) -> None:
    if color is None:
        color = GOLD_PRIMARY
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, 1)
    inner = rect.inflate(-2, -2)
    pygame.draw.rect(dst, NAVY_SHADOW, inner)
    fill = inner.copy()
    fill.width = max(1, int(inner.width * max(0.0, min(1.0, value))))
    pygame.draw.rect(dst, color, fill)
    if label and font:
        t  = font.render(label, False, WHITE)
        tx = rect.centerx - t.get_width()  // 2
        ty = rect.centery - t.get_height() // 2
        dst.blit(t, (tx, ty))


def toast(
    dst:  pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
) -> None:
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, 2)
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(dst, GOLD_PRIMARY, inner)
    t  = font.render(text, False, OUTLINE_BLACK)
    tx = rect.centerx - t.get_width()  // 2
    ty = rect.centery - t.get_height() // 2
    dst.blit(t, (tx, ty))


# ──────────────────────────────────────────────────────────────────────────────
# Judge Sheet panel — draws a JudgeScore result in a styled breakdown box
# ──────────────────────────────────────────────────────────────────────────────

def draw_judge_sheet(
    dst:    pygame.Surface,
    rect:   pygame.Rect,
    score,                        # JudgeScore dataclass
    assets: object,
) -> None:
    """
    Render a full judge sheet inside rect.
    Expects a JudgeScore with: total, technique, show_quality, efficiency,
    creativity, notes (list[str]), grade(), passed.
    """
    font_s = getattr(assets, "font_s",  None)
    font_m = getattr(assets, "font_m",  None)
    font_l = getattr(assets, "font_l",  None)
    if not font_s:
        return

    panel(dst, rect, "JUDGE SHEET", font_s)
    inner = rect.inflate(-8, -16)
    inner.top += 8

    y = inner.top + 4
    x = inner.left + 4
    w = inner.width - 8

    # ── Grade + total ────────────────────────────────────────────────────────
    if font_l:
        grade_col = SUCCESS_GREEN if score.passed else ALERT_RED
        grade_t   = font_l.render(score.grade(), False, grade_col)
        total_t   = font_m.render(f"{score.total}/100", False, OFF_WHITE) if font_m else None
        dst.blit(grade_t, (rect.right - grade_t.get_width() - 12, rect.top + 2))
        if total_t:
            dst.blit(total_t, (rect.right - total_t.get_width() - 12, rect.top + grade_t.get_height() + 2))

    # ── Category bars ────────────────────────────────────────────────────────
    categories = [
        ("TECHNIQUE",   score.technique,    50, GOLD_PRIMARY),
        ("SHOW QUAL",   score.show_quality, 25, (0x4A, 0xA0, 0xD8)),
        ("EFFICIENCY",  score.efficiency,   15, (0x88, 0xCC, 0x88)),
        ("CREATIVITY",  score.creativity,   10, (0xD8, 0x60, 0xB0)),
    ]

    bar_h = 10
    bar_gap = 3

    for label, pts, max_pts, col in categories:
        if y + bar_h > inner.bottom - 40:
            break
        # Label
        lt = font_s.render(f"{label}", False, OFF_WHITE)
        dst.blit(lt, (x, y))

        # Score text right-aligned
        st = font_s.render(f"{pts}/{max_pts}", False, WHITE)
        dst.blit(st, (x + w - st.get_width(), y))

        y += font_s.get_height() + 1

        # Bar
        bar_rect = pygame.Rect(x, y, w, bar_h)
        progress_bar(
            dst, bar_rect,
            value=pts / max_pts if max_pts else 0,
            color=col,
        )
        y += bar_h + bar_gap + 2

    # ── Notes ────────────────────────────────────────────────────────────────
    y += 4
    if y < inner.bottom - 4 and score.notes:
        # Divider
        pygame.draw.line(dst, NAVY_SHADOW, (x, y), (x + w, y), 1)
        y += 4

        for note in score.notes:
            if y >= inner.bottom - 2:
                break
            lines = _wrap_safe_tokens(font_s, note, w)
            for ln in lines:
                if y >= inner.bottom - 2:
                    break
                t = font_s.render(ln, False, OFF_WHITE)
                dst.blit(t, (x, y))
                y += font_s.get_height() + 1


# ──────────────────────────────────────────────────────────────────────────────
# Widget: Pride Points HUD chip
# ──────────────────────────────────────────────────────────────────────────────

def draw_pp_chip(
    dst:   pygame.Surface,
    rect:  pygame.Rect,
    pp:    int,
    font:  pygame.font.Font,
) -> None:
    """Small gold badge showing current Pride Points."""
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, 1)
    pygame.draw.rect(dst, NAVY_DEEP, rect.inflate(-2, -2))
    # Gold left accent stripe
    accent = pygame.Rect(rect.left + 1, rect.top + 2, 3, rect.height - 4)
    pygame.draw.rect(dst, GOLD_PRIMARY, accent)
    t  = font.render(f"PP {pp:,}", False, GOLD_PRIMARY)
    s  = font.render(f"PP {pp:,}", False, OUTLINE_BLACK)
    tx = rect.left + 8
    ty = rect.centery - t.get_height() // 2
    dst.blit(s, (tx + 1, ty + 1))
    dst.blit(t, (tx,     ty))


# ──────────────────────────────────────────────────────────────────────────────
# Widget: Week node map chip (for season map rendering)
# ──────────────────────────────────────────────────────────────────────────────

def draw_week_node(
    dst:      pygame.Surface,
    center:   tuple[int, int],
    radius:   int,
    week:     int,
    day:      int,
    state:    str,           # "locked" | "available" | "complete" | "current"
    font:     pygame.font.Font,
    is_battle: bool = False,
) -> None:
    """Draw a single season-map node circle."""
    cx, cy = center
    colors = {
        "locked":    ((40, 42, 52),    (70, 72, 80)),
        "available": (NAVY_DEEP,        GOLD_DIM),
        "complete":  ((28, 100, 52),    (60, 180, 100)),
        "current":   (GOLD_PRIMARY,     (255, 240, 160)),
    }
    face, border = colors.get(state, colors["locked"])

    pygame.draw.circle(dst, OUTLINE_BLACK, (cx + 1, cy + 1), radius)
    pygame.draw.circle(dst, face,          (cx, cy),          radius)
    pygame.draw.circle(dst, border,        (cx, cy),          radius, 2)

    if is_battle:
        # Small sword icon approximation: two crossed lines
        pygame.draw.line(dst, border, (cx - 4, cy - 4), (cx + 4, cy + 4), 1)
        pygame.draw.line(dst, border, (cx + 4, cy - 4), (cx - 4, cy + 4), 1)
    else:
        label_col = OUTLINE_BLACK if state == "current" else OFF_WHITE
        t  = font.render(str(day), False, label_col)
        tx = cx - t.get_width()  // 2
        ty = cy - t.get_height() // 2
        dst.blit(t, (tx, ty))


# ──────────────────────────────────────────────────────────────────────────────
# Code editor (unchanged from original, kept here for single-file import)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class TextEditor:
    rect:          pygame.Rect
    lines:         list[str]
    cx:            int   = 0
    cy:            int   = 0
    scroll:        int   = 0
    hscroll_px:    int   = 0
    blink:         int   = 0
    error_line:    int | None = None
    insert_spaces: int   = 4

    @classmethod
    def from_text(cls, rect: pygame.Rect, text: str) -> "TextEditor":
        return cls(rect=rect, lines=text.splitlines() or [""])

    def get_text(self) -> str:
        return "\n".join(self.lines)

    def set_error_line(self, lineno: int | None) -> None:
        self.error_line = lineno
        if lineno is not None:
            self.cy = max(0, lineno - 1)
            self._clamp_cursor()

    def _inner(self) -> pygame.Rect:
        return self.rect.inflate(-4, -4)

    def _line_h(self, font: pygame.font.Font) -> int:
        return font.get_linesize() + 1

    def _view_lines(self, font: pygame.font.Font) -> int:
        inner = self._inner()
        lh    = self._line_h(font)
        return max(1, (inner.height - 4) // lh)

    def _clamp_cursor(self) -> None:
        self.cy = max(0, min(self.cy, len(self.lines) - 1))
        self.cx = max(0, min(self.cx, len(self.lines[self.cy])))

    def _clamp_vscroll(self, font: pygame.font.Font) -> None:
        max_s    = max(0, len(self.lines) - self._view_lines(font))
        self.scroll = max(0, min(self.scroll, max_s))

    def _ensure_cursor_visible(self, font: pygame.font.Font) -> None:
        vl = self._view_lines(font)
        if self.cy < self.scroll:
            self.scroll = self.cy
        elif self.cy >= self.scroll + vl:
            self.scroll = self.cy - vl + 1
        self._clamp_vscroll(font)

    def scroll_by(self, delta_lines: int, font: pygame.font.Font) -> None:
        self.scroll += int(delta_lines)
        self._clamp_vscroll(font)

    def hscroll_by(self, delta_px: int, font: pygame.font.Font) -> None:
        inner    = self._inner()
        visible_w = max(10, inner.width - 8)
        start    = max(0, self.scroll - 2)
        end      = min(len(self.lines), self.scroll + self._view_lines(font) + 2)
        longest  = 0
        for ln in self.lines[start:end]:
            longest = max(longest, font.size(ln)[0])
        max_h       = max(0, longest - visible_w + 6)
        self.hscroll_px = max(0, min(self.hscroll_px + int(delta_px), max_h))

    def set_caret_from_mouse(self, pos: tuple[int, int], font: pygame.font.Font) -> None:
        inner = self._inner()
        if not inner.collidepoint(pos):
            return
        lh   = self._line_h(font)
        x0   = inner.left + 4
        y0   = inner.top + 2
        row  = int((pos[1] - y0) // lh)
        row  = max(0, row)
        line_idx = max(0, min(self.scroll + row, len(self.lines) - 1))
        px   = (pos[0] - x0) + self.hscroll_px
        s    = self.lines[line_idx]
        lo, hi = 0, len(s)
        best = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            w   = font.size(s[:mid])[0]
            if w <= px:
                best = mid
                lo   = mid + 1
            else:
                hi = mid - 1
        self.cy = line_idx
        self.cx = best
        self._clamp_cursor()
        self._ensure_cursor_visible(font)

    def handle_key(self, ev: pygame.event.Event) -> None:
        self.error_line = None

        if ev.key == pygame.K_BACKSPACE:
            if self.cx > 0:
                ln = self.lines[self.cy]
                self.lines[self.cy] = ln[: self.cx - 1] + ln[self.cx :]
                self.cx -= 1
            elif self.cy > 0:
                prev        = self.lines[self.cy - 1]
                cur         = self.lines[self.cy]
                self.cx     = len(prev)
                self.lines[self.cy - 1] = prev + cur
                del self.lines[self.cy]
                self.cy -= 1

        elif ev.key == pygame.K_RETURN:
            ln    = self.lines[self.cy]
            left, right = ln[: self.cx], ln[self.cx :]
            m     = re.match(r"[ ]*", ln)
            indent = m.group(0) if m else ""
            self.lines[self.cy] = left
            self.lines.insert(self.cy + 1, indent + right.lstrip(" "))
            self.cy += 1
            self.cx  = len(indent)

        elif ev.key == pygame.K_TAB:
            ln = self.lines[self.cy]
            ins = " " * self.insert_spaces
            self.lines[self.cy] = ln[: self.cx] + ins + ln[self.cx :]
            self.cx += len(ins)

        elif ev.key == pygame.K_HOME:
            self.cx = 0
        elif ev.key == pygame.K_END:
            self.cx = len(self.lines[self.cy])
        elif ev.key == pygame.K_LEFT:
            if self.cx > 0:
                self.cx -= 1
            elif self.cy > 0:
                self.cy -= 1
                self.cx = len(self.lines[self.cy])
        elif ev.key == pygame.K_RIGHT:
            if self.cx < len(self.lines[self.cy]):
                self.cx += 1
            elif self.cy < len(self.lines) - 1:
                self.cy += 1
                self.cx = 0
        elif ev.key == pygame.K_UP:
            self.cy = max(0, self.cy - 1)
            self.cx = min(self.cx, len(self.lines[self.cy]))
        elif ev.key == pygame.K_DOWN:
            self.cy = min(len(self.lines) - 1, self.cy + 1)
            self.cx = min(self.cx, len(self.lines[self.cy]))
        elif ev.unicode and ev.unicode.isprintable():
            ln = self.lines[self.cy]
            self.lines[self.cy] = ln[: self.cx] + ev.unicode + ln[self.cx :]
            self.cx += 1

        self._clamp_cursor()

    def draw(self, dst: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(dst, OUTLINE_BLACK, self.rect, 2)
        inner = self._inner()
        pygame.draw.rect(dst, (10, 10, 14), inner)

        self._ensure_cursor_visible(font)

        prev_clip = dst.get_clip()
        dst.set_clip(inner)

        keywords = {
            "def", "for", "if", "else", "elif", "return",
            "in", "range", "len", "int", "float", "str",
            "True", "False", "and", "or", "not",
        }

        lh       = self._line_h(font)
        y        = inner.top + 2
        x0       = inner.left + 4
        visible_w = max(10, inner.width - 8)

        # Auto-reset hscroll when line fits or caret is near left
        cur_line_w = font.size(self.lines[self.cy])[0] if (0 <= self.cy < len(self.lines)) else 0
        if cur_line_w <= (visible_w - 2) or self.cx <= 2:
            self.hscroll_px = 0

        # Keep caret visible horizontally
        cursor_px = font.size(self.lines[self.cy][: self.cx])[0]
        if (cursor_px - self.hscroll_px) > (visible_w - 6):
            self.hscroll_px = max(0, cursor_px - (visible_w - 6))
        elif (cursor_px - self.hscroll_px) < 0:
            self.hscroll_px = max(0, cursor_px)

        # Clamp hscroll to longest nearby line
        longest = 0
        for ln in self.lines[max(0, self.cy - 2) : min(len(self.lines), self.cy + 3)]:
            longest = max(longest, font.size(ln)[0])
        self.hscroll_px = min(self.hscroll_px, max(0, longest - visible_w + 6))

        view_lines = self._view_lines(font)
        start_ln   = self.scroll
        end_ln     = min(len(self.lines), start_ln + view_lines)
        max_x      = inner.right - 6

        for i in range(start_ln, end_ln):
            ln = self.lines[i]

            # Error line highlight
            if self.error_line is not None and i + 1 == self.error_line:
                hl = pygame.Rect(inner.left + 1, y - 1, inner.width - 2, lh)
                pygame.draw.rect(dst, (110, 34, 40), hl)

            x = x0 - self.hscroll_px
            for token in re.split(r"(\W)", ln):
                if token == "":
                    continue
                # Syntax coloring
                if token in keywords:
                    col = (255, 220, 120)    # yellow: keywords
                elif token.startswith("#"):
                    col = (100, 160, 100)    # green: comments
                elif token.startswith('"') or token.startswith("'"):
                    col = (200, 140, 100)    # orange: strings
                elif token.lstrip("-").isdigit():
                    col = (160, 220, 255)    # cyan: numbers
                else:
                    col = (220, 220, 220)    # default: off-white

                t  = font.render(token, False, col)
                tw = t.get_width()

                if x + tw < x0:
                    x += tw
                    continue
                if x >= max_x or (x + tw) > max_x:
                    break

                dst.blit(t, (x, y))
                x += tw

            y += lh

        # Cursor blink
        self.blink = (self.blink + 1) % 60
        if self.blink < 30:
            cur_y = inner.top + 2 + (self.cy - self.scroll) * lh
            cur_x = (x0 - self.hscroll_px) + cursor_px
            if inner.top <= cur_y <= inner.bottom - lh:
                pygame.draw.rect(dst, OFF_WHITE, pygame.Rect(cur_x, cur_y + 2, 2, lh - 4))

        # Vertical scrollbar
        max_scroll = max(0, len(self.lines) - view_lines)
        if max_scroll > 0:
            track   = pygame.Rect(inner.right - 4, inner.top + 2, 3, inner.height - 4)
            pygame.draw.rect(dst, (40, 40, 50), track)
            thumb_h = max(10, int(track.height * (view_lines / max(1, len(self.lines)))))
            frac    = self.scroll / max_scroll if max_scroll else 0.0
            thumb_y = track.top + int((track.height - thumb_h) * frac)
            thumb   = pygame.Rect(track.left, thumb_y, track.width, thumb_h)
            pygame.draw.rect(dst, OFF_WHITE, thumb)

        dst.set_clip(prev_clip)