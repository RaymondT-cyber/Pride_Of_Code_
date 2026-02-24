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

    words = text.split()
    lines: list[str] = []
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if font.size(test)[0] <= inner.width - U:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)

    y = inner.top + 4
    for ln in lines[:5]:
        t = font.render(ln, False, WHITE)
        s = font.render(ln, False, OUTLINE_BLACK)
        dst.blit(s, (inner.left + 5, y + 1))
        dst.blit(t, (inner.left + 4, y))
        y += t.get_height() + 2


class TextEditor:
    """Minimal multi-line editor for the MVP. Not a full IDE (yet)."""

    def __init__(self, rect: pygame.Rect, initial_text: str = ""):
        self.rect = rect
        self.lines = initial_text.splitlines() or [""]
        self.cx = 0
        self.cy = 0
        self.scroll = 0
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
        self.error_line = None

    def set_error_line(self, line_number: int | None) -> None:
        self.error_line = line_number

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
            self.lines[self.cy] = left
            self.lines.insert(self.cy + 1, right)
            self.cy += 1
            self.cx = 0
        elif ev.key == pygame.K_TAB:
            ln = self.lines[self.cy]
            ins = " " * self.insert_spaces
            self.lines[self.cy] = ln[:self.cx] + ins + ln[self.cx:]
            self.cx += len(ins)
        elif ev.key == pygame.K_LEFT:
            self.cx = max(0, self.cx - 1)
        elif ev.key == pygame.K_RIGHT:
            self.cx = min(len(self.lines[self.cy]), self.cx + 1)
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

        view_lines = max(1, (self.rect.height - 12) // 14)
        if self.cy < self.scroll:
            self.scroll = self.cy
        if self.cy >= self.scroll + view_lines:
            self.scroll = self.cy - view_lines + 1

    def draw(self, dst: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(dst, OUTLINE_BLACK, self.rect, 2)
        inner = self.rect.inflate(-4, -4)
        pygame.draw.rect(dst, (10, 10, 14), inner)

        keywords = {"def", "for", "if", "else", "elif", "return", "in", "range", "len", "int", "float", "str", "True", "False"}
        y = inner.top + 2
        x0 = inner.left + 4
        lh = 14
        view_lines = max(1, inner.height // lh)
        start = self.scroll
        end = min(len(self.lines), start + view_lines)

        for i in range(start, end):
            ln = self.lines[i]
            if self.error_line is not None and i + 1 == self.error_line:
                hl = pygame.Rect(inner.left + 1, y - 1, inner.width - 2, lh)
                pygame.draw.rect(dst, (110, 34, 40), hl)
            x = x0
            for token in re.split(r"(\W)", ln):
                if token == "":
                    continue
                col = (220, 220, 220)
                if token in keywords:
                    col = (255, 220, 120)
                elif token.startswith("#"):
                    col = (120, 180, 120)
                t = font.render(token, False, col)
                dst.blit(t, (x, y))
                x += t.get_width()
            y += lh

        self.blink = (self.blink + 1) % 60
        if self.blink < 30:
            cur_y = inner.top + 2 + (self.cy - self.scroll) * lh
            cur_x = x0 + font.size(self.lines[self.cy][: self.cx])[0]
            if inner.top <= cur_y <= inner.bottom - lh:
                pygame.draw.rect(dst, OFF_WHITE, pygame.Rect(cur_x, cur_y + 2, 2, lh - 4))
