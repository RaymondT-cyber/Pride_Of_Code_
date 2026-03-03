from __future__ import annotations

import json
import re
from dataclasses import dataclass

def _wrap_safe_tokens(font: pygame.font.Font, text: str, max_w: int) -> list[str]:
    """Wrap text to max_w. Splits long tokens so nothing overflows."""
    out: list[str] = []
    for para in text.split('\n'):
        words = para.split(' ')
        line = ''
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

from pathlib import Path

import pygame

from .constants import (
    U,
    ALERT_RED,
    CASA_BLUE,
    GOLD_HILITE,
    GOLD_PRIMARY,
    GOLD_SHADOW,
    NAVY_DEEP,
    NAVY_SHADOW,
    OFF_WHITE,
    OUTLINE_BLACK,
    WHITE,
)


def _load_ui_tokens() -> dict:
    token_path = Path(__file__).resolve().parents[1] / "data" / "ui_tokens.json"
    if token_path.exists():
        with token_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "spacing": {"u": 8, "panel_padding": 8, "button_padding_x": 8, "button_padding_y": 4},
        "line": {"frame": 2, "inset": 1},
        "shadow": {"x": 1, "y": 1},
    }


UI_TOKENS = _load_ui_tokens()

def wrap_text(font: pygame.font.Font, text: str, max_width: int, preserve_newlines: bool = True) -> list[str]:
    """
    Word-wrap text to max_width. Handles very long tokens by splitting them so nothing
    can render beyond the box width (critical for code-like strings).
    """
    if max_width <= 0:
        return [text]

    # Split into paragraphs if requested (keeps intentional blank lines/code blocks).
    raw_lines = text.splitlines() if preserve_newlines else [text]
    out: list[str] = []
    for raw in raw_lines:
        if preserve_newlines and raw.strip() == "":
            out.append("")
            continue

        # Preserve leading indentation (useful for code samples).
        indent = len(raw) - len(raw.lstrip(" "))
        prefix = " " * indent
        content = raw.lstrip(" ")
        if content == "":
            out.append(prefix)
            continue

        words = content.split(" ")
        line = prefix
        for w in words:
            candidate = (line + (" " if line.strip() else "") + w) if line != prefix else (prefix + w)
            if font.size(candidate)[0] <= max_width:
                line = candidate
                continue

            # If the current line has content, push it and start a new line.
            if line.strip() != "":
                out.append(line)
                line = prefix

            # w might be longer than max_width: split it into chunks.
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
    """Trim text with … so it fits max_width."""
    if font.size(text)[0] <= max_width:
        return text
    ell = "…"
    if font.size(ell)[0] > max_width:
        return ""
    lo, hi = 0, len(text)
    best = ell
    while lo <= hi:
        mid = (lo + hi) // 2
        cand = text[:mid].rstrip() + ell
        if font.size(cand)[0] <= max_width:
            best = cand
            lo = mid + 1
        else:
            hi = mid - 1
    return best

def blit_text_lines(dst: pygame.Surface, rect: pygame.Rect, font: pygame.font.Font, lines: list[str],
                    color=(255,255,255), shadow: bool=True, line_gap: int=2) -> None:
    """Draw pre-wrapped lines into rect, clipped."""
    prev = dst.get_clip()
    dst.set_clip(rect)
    y = rect.top
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


@dataclass
class Button:
    rect: pygame.Rect
    text: str
    primary: bool = False
    enabled: bool = True
    hotkey: str | None = None

    def draw(self, dst: pygame.Surface, font: pygame.font.Font, hovered: bool, pressed: bool = False) -> None:
        face = GOLD_PRIMARY if self.primary else CASA_BLUE
        hi = GOLD_HILITE if self.primary else OFF_WHITE
        sh = GOLD_SHADOW if self.primary else NAVY_SHADOW

        if not self.enabled:
            face, hi, sh = (80, 80, 80), (110, 110, 110), (60, 60, 60)

        frame_w = int(UI_TOKENS["line"].get("frame", 2))
        pygame.draw.rect(dst, OUTLINE_BLACK, self.rect, frame_w)

        depth_off = 1 if pressed and self.enabled else 0
        inner = self.rect.inflate(-4, -4).move(0, depth_off)
        pygame.draw.rect(dst, face, inner)

        # Bevel edges (invert when pressed for depth illusion)
        top_left = sh if pressed else hi
        bot_right = hi if pressed else sh
        pygame.draw.line(dst, top_left, (inner.left, inner.top), (inner.right - 1, inner.top), 1)
        pygame.draw.line(dst, top_left, (inner.left, inner.top), (inner.left, inner.bottom - 1), 1)
        pygame.draw.line(dst, bot_right, (inner.left, inner.bottom - 1), (inner.right - 1, inner.bottom - 1), 1)
        pygame.draw.line(dst, bot_right, (inner.right - 1, inner.top), (inner.right - 1, inner.bottom - 1), 1)

        label = self.text if not self.hotkey else f"{self.text} [{self.hotkey}]"
        txt = font.render(label, False, WHITE)
        shadow = font.render(label, False, OUTLINE_BLACK)
        tx = self.rect.centerx - txt.get_width() // 2
        ty = self.rect.centery - txt.get_height() // 2 + depth_off
        sx, sy = UI_TOKENS["shadow"].get("x", 1), UI_TOKENS["shadow"].get("y", 1)
        dst.blit(shadow, (tx + sx, ty + sy))
        dst.blit(txt, (tx, ty))

        if hovered and self.enabled:
            pygame.draw.rect(dst, OFF_WHITE, self.rect, 1)

    def hit(self, pos: tuple[int, int]) -> bool:
        return self.enabled and self.rect.collidepoint(pos)


def panel(dst: pygame.Surface, rect: pygame.Rect, title: str | None, font: pygame.font.Font) -> None:
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, int(UI_TOKENS["line"].get("frame", 2)))
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(dst, NAVY_DEEP, inner)
    pygame.draw.rect(dst, NAVY_SHADOW, inner, int(UI_TOKENS["line"].get("inset", 1)))

    if title:
        t = font.render(title, False, WHITE)
        s = font.render(title, False, OUTLINE_BLACK)
        dst.blit(s, (rect.left + U + 1, rect.top + 1))
        dst.blit(t, (rect.left + U, rect.top))


def header_bar(
    dst: pygame.Surface,
    rect: pygame.Rect,
    title: str,
    font: pygame.font.Font,
    left_text: str | None = None,
    right_text: str | None = None,
) -> None:
    pygame.draw.rect(dst, NAVY_DEEP, rect)
    t = font.render(title, False, WHITE)
    dst.blit(t, (rect.centerx - t.get_width() // 2, rect.top + 4))
    if left_text:
        l = font.render(left_text, False, OFF_WHITE)
        dst.blit(l, (rect.left + U, rect.top + 4))
    if right_text:
        r = font.render(right_text, False, OFF_WHITE)
        dst.blit(r, (rect.right - r.get_width() - U, rect.top + 4))


def progress_bar(dst: pygame.Surface, rect: pygame.Rect, pct: float, label: str, font: pygame.font.Font) -> None:
    pct = max(0.0, min(1.0, pct))
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, int(UI_TOKENS["line"].get("frame", 2)))
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(dst, NAVY_SHADOW, inner)
    fill = inner.copy()
    fill.width = int(inner.width * pct)
    pygame.draw.rect(dst, GOLD_PRIMARY, fill)

    txt = font.render(label, False, WHITE)
    sh = font.render(label, False, OUTLINE_BLACK)
    dst.blit(sh, (rect.left + U + 1, rect.top + 1))
    dst.blit(txt, (rect.left + U, rect.top))


def toast(dst: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font, danger: bool = False) -> None:
    bg = ALERT_RED if danger else CASA_BLUE
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, int(UI_TOKENS["line"].get("frame", 2)))
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(dst, bg, inner)

    # Wrap safely (break long tokens) and clip so nothing leaks.
    lines = wrap_text(font, text, max_width=inner.width - 8, preserve_newlines=True)
    blit_text_lines(dst, pygame.Rect(inner.left + 4, inner.top + 2, inner.width - 8, inner.height - 4),
                    font, lines[:8], color=WHITE, shadow=True, line_gap=1)


class TextEditor:
    """Minimal multi-line editor for the MVP (with mouse scroll + click caret)."""

    def __init__(self, rect: pygame.Rect, initial_text: str = ""):
        self.rect = rect
        self.lines = initial_text.splitlines() or [""]
        self.cx = 0
        self.cy = 0
        self.scroll = 0              # vertical scroll in lines
        self.hscroll_px = 0          # horizontal scroll in pixels
        self.blink = 0
        self.insert_spaces = 4
        self.error_line: int | None = None

    def get_text(self) -> str:
        return "\n".join(self.lines) + ("\n" if len(self.lines) else "")

    def set_text(self, t: str) -> None:
        self.lines = t.splitlines() or [""]
        self.cx = 0
        self.cy = 0
        self.scroll = 0
        self.hscroll_px = 0
        self.error_line = None

    def set_error_line(self, line_number: int | None) -> None:
        self.error_line = line_number

    # --------------------------
    # Layout + scrolling helpers
    # --------------------------

    def _inner(self) -> pygame.Rect:
        return self.rect.inflate(-4, -4)

    def _line_h(self, font: pygame.font.Font) -> int:
        return max(12, font.get_linesize())

    def _view_lines(self, font: pygame.font.Font) -> int:
        inner = self._inner()
        lh = self._line_h(font)
        return max(1, (inner.height - 4) // lh)

    def _clamp_cursor(self) -> None:
        self.cy = max(0, min(self.cy, len(self.lines) - 1))
        self.cx = max(0, min(self.cx, len(self.lines[self.cy])))

    def _clamp_vscroll(self, font: pygame.font.Font) -> None:
        view = self._view_lines(font)
        max_scroll = max(0, len(self.lines) - view)
        self.scroll = max(0, min(self.scroll, max_scroll))

    def _ensure_cursor_visible(self, font: pygame.font.Font) -> None:
        view = self._view_lines(font)
        if self.cy < self.scroll:
            self.scroll = self.cy
        elif self.cy >= self.scroll + view:
            self.scroll = self.cy - view + 1
        self._clamp_vscroll(font)

    # --------------------------
    # Mouse support
    # --------------------------

    def scroll_by(self, delta_lines: int, font: pygame.font.Font) -> None:
        self.scroll += int(delta_lines)
        self._clamp_vscroll(font)

    def hscroll_by(self, delta_px: int, font: pygame.font.Font) -> None:
        inner = self._inner()
        visible_w = max(10, inner.width - 8)

        # estimate max horizontal scroll based on longest visible-ish line
        start = max(0, self.scroll - 2)
        end = min(len(self.lines), self.scroll + self._view_lines(font) + 2)
        longest = 0
        for ln in self.lines[start:end]:
            longest = max(longest, font.size(ln)[0])

        max_h = max(0, longest - visible_w + 6)
        self.hscroll_px = max(0, min(self.hscroll_px + int(delta_px), max_h))

    def set_caret_from_mouse(self, pos: tuple[int, int], font: pygame.font.Font) -> None:
        inner = self._inner()
        if not inner.collidepoint(pos):
            return

        lh = self._line_h(font)
        x0 = inner.left + 4
        y0 = inner.top + 2

        row = int((pos[1] - y0) // lh)
        row = max(0, row)
        line_idx = max(0, min(self.scroll + row, len(self.lines) - 1))

        px = (pos[0] - x0) + self.hscroll_px
        s = self.lines[line_idx]

        # binary search nearest column by rendered width
        lo, hi = 0, len(s)
        best = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            w = font.size(s[:mid])[0]
            if w <= px:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1

        self.cy = line_idx
        self.cx = best
        self._clamp_cursor()
        self._ensure_cursor_visible(font)

    # --------------------------
    # Keyboard editing
    # --------------------------

    def handle_key(self, ev: pygame.event.Event) -> None:
        self.error_line = None

        if ev.key == pygame.K_BACKSPACE:
            if self.cx > 0:
                ln = self.lines[self.cy]
                self.lines[self.cy] = ln[: self.cx - 1] + ln[self.cx :]
                self.cx -= 1
            elif self.cy > 0:
                prev = self.lines[self.cy - 1]
                cur = self.lines[self.cy]
                self.cx = len(prev)
                self.lines[self.cy - 1] = prev + cur
                del self.lines[self.cy]
                self.cy -= 1

        elif ev.key == pygame.K_RETURN:
            ln = self.lines[self.cy]
            left, right = ln[: self.cx], ln[self.cx :]

            # carry indentation to the next line
            m = re.match(r"[ ]*", ln)
            indent = m.group(0) if m else ""

            self.lines[self.cy] = left
            self.lines.insert(self.cy + 1, indent + right.lstrip(" "))
            self.cy += 1
            self.cx = len(indent)

        elif ev.key == pygame.K_TAB:
            ln = self.lines[self.cy]
            ins = " " * self.insert_spaces
            self.lines[self.cy] = ln[:self.cx] + ins + ln[self.cx:]
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
            self.lines[self.cy] = ln[:self.cx] + ev.unicode + ln[self.cx:]
            self.cx += 1

        self._clamp_cursor()
        # vscroll is finalized in draw() or when called by scene with a font.

    # --------------------------
    # Rendering
    # --------------------------

    def draw(self, dst: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(dst, OUTLINE_BLACK, self.rect, 2)
        inner = self._inner()
        pygame.draw.rect(dst, (10, 10, 14), inner)

        # Keep cursor visible with correct metrics
        self._ensure_cursor_visible(font)

        prev_clip = dst.get_clip()
        dst.set_clip(inner)

        keywords = {"def", "for", "if", "else", "elif", "return", "in", "range", "len", "int", "float", "str", "True", "False"}
        lh = self._line_h(font)
        y = inner.top + 2
        x0 = inner.left + 4
        visible_w = max(10, inner.width - 8)

        # Horizontal scroll: keep cursor visible
        cursor_px = font.size(self.lines[self.cy][: self.cx])[0]
        if (cursor_px - self.hscroll_px) > (visible_w - 6):
            self.hscroll_px = max(0, cursor_px - (visible_w - 6))
        elif (cursor_px - self.hscroll_px) < 0:
            self.hscroll_px = max(0, cursor_px)

        # Clamp horizontal scroll to longest nearby line
        longest = 0
        for ln in self.lines[max(0, self.cy - 2) : min(len(self.lines), self.cy + 3)]:
            longest = max(longest, font.size(ln)[0])
        self.hscroll_px = min(self.hscroll_px, max(0, longest - visible_w + 6))

        view_lines = self._view_lines(font)
        start_ln = self.scroll
        end_ln = min(len(self.lines), start_ln + view_lines)
        max_x = inner.right - 6  # leave space for scrollbar

        for i in range(start_ln, end_ln):
            ln = self.lines[i]

            # Soft highlights to guide beginners
            if i == self.cy:
                hl_cur = pygame.Rect(inner.left + 1, y - 1, inner.width - 6, lh)
                pygame.draw.rect(dst, (18, 18, 28), hl_cur)
            if "TODO" in ln:
                hl_todo = pygame.Rect(inner.left + 1, y - 1, inner.width - 6, lh)
                pygame.draw.rect(dst, (50, 45, 18), hl_todo)
            if self.error_line is not None and i + 1 == self.error_line:
                hl = pygame.Rect(inner.left + 1, y - 1, inner.width - 2, lh)
                pygame.draw.rect(dst, (110, 34, 40), hl)

            x = (x0 - self.hscroll_px)
            for token in re.split(r"(\W)", ln):
                if token == "":
                    continue
                col = (220, 220, 220)
                if token in keywords:
                    col = (255, 220, 120)
                elif token.startswith("#"):
                    col = (120, 180, 120)

                t = font.render(token, False, col)
                tw = t.get_width()

                if x + tw < x0:
                    x += tw
                    continue
                if x >= max_x or (x + tw) > max_x:
                    break

                dst.blit(t, (x, y))
                x += tw

            y += lh

        # Caret blink
        self.blink = (self.blink + 1) % 60
        if self.blink < 30:
            cur_y = inner.top + 2 + (self.cy - self.scroll) * lh
            cur_x = (x0 - self.hscroll_px) + cursor_px
            if inner.top <= cur_y <= inner.bottom - lh:
                pygame.draw.rect(dst, OFF_WHITE, pygame.Rect(cur_x, cur_y + 2, 2, lh - 4))

        # Vertical scrollbar
        max_scroll = max(0, len(self.lines) - view_lines)
        if max_scroll > 0:
            track = pygame.Rect(inner.right - 4, inner.top + 2, 3, inner.height - 4)
            pygame.draw.rect(dst, (40, 40, 50), track)
            thumb_h = max(10, int(track.height * (view_lines / max(1, len(self.lines)))))
            frac = self.scroll / max_scroll if max_scroll else 0.0
            thumb_y = track.top + int((track.height - thumb_h) * frac)
            thumb = pygame.Rect(track.left, thumb_y, track.width, thumb_h)
            pygame.draw.rect(dst, OFF_WHITE, thumb)

        # Horizontal scrollbar (shows when content is wider than view)
        # Reserve space above bottom edge so it doesn't overlap text.
        longest_all = 0
        for ln2 in self.lines[start_ln:end_ln]:
            longest_all = max(longest_all, font.size(ln2)[0])
        max_h = max(0, longest_all - visible_w + 6)
        if max_h > 0:
            htrack = pygame.Rect(inner.left + 2, inner.bottom - 4, inner.width - 8, 3)
            pygame.draw.rect(dst, (40, 40, 50), htrack)
            thumb_w = max(12, int(htrack.width * (visible_w / max(1, longest_all + 6))))
            frac_h = self.hscroll_px / max_h if max_h else 0.0
            thumb_x = htrack.left + int((htrack.width - thumb_w) * frac_h)
            hthumb = pygame.Rect(thumb_x, htrack.top, thumb_w, htrack.height)
            pygame.draw.rect(dst, OFF_WHITE, hthumb)

        dst.set_clip(prev_clip)
