from __future__ import annotations

import re
import pygame
from dataclasses import dataclass
from typing import Callable, Optional

from .constants import (
    LOGICAL_W, LOGICAL_H, U,
    CASA_BLUE, NAVY_DEEP,
    WHITE, OFF_WHITE, OUTLINE_BLACK
)
from .ui import Button, panel, progress_bar, toast, TextEditor
from .band import Band
from .code_runner import run_player_code
from .save import SaveSlot, load_slot, write_slot, delete_slot
from .levels import Level

# --- Story (robust import; works even if story.py is missing) ---
try:
    from .story import INTRO_PAGES, WEEK1_BRIEFING, WEEK1_LESSON
except Exception:
    INTRO_PAGES = [
        ("NARRATOR",
         "Hey! Welcome.\n\n"
         "You’re the new Band Director of the Pride of Code Marching Band.\n"
         "Time to make this band the greatest.\n\n"
         "Listen to your team, work together, and build the greatest marching show ever.")
    ]
    WEEK1_BRIEFING = [
        ("LEAH",
         "Director… a marching band is a team. If one person drifts, the whole form breaks.\n\n"
         "Programming helps us stay together: we can plan the same move for everyone, every time."),
        ("JACOB",
         "Think of code as rehearsal notes.\n"
         "Write clear instructions, and the band can repeat them perfectly.\n\n"
         "Today: VARIABLES.")
    ]
    WEEK1_LESSON = [
        ("LESSON: VARIABLES",
         "A variable stores information.\n\n"
         "Example:\n"
         "  target_x = 20\n"
         "  target_y = 11\n\n"
         "To move the Drum Major (DM) in 8 counts:\n"
         "  band.step_to(\"DM\", target_x, target_y, counts=8)\n\n"
         "Now you try. You must set the right numbers.")
    ]


def compute_viewport(logical: pygame.Surface, window: pygame.Surface) -> tuple[int, int, int, int, int]:
    """Returns (scale, x_off, y_off, scaled_w, scaled_h) for integer pixel-perfect presentation."""
    lw, lh = logical.get_size()
    ww, wh = window.get_size()
    scale = max(1, min(ww // lw, wh // lh))
    sw, sh = lw * scale, lh * scale
    x = (ww - sw) // 2
    y = (wh - sh) // 2
    return scale, x, y, sw, sh


def present(logical: pygame.Surface, window: pygame.Surface) -> tuple[int, int, int]:
    scale, x, y, sw, sh = compute_viewport(logical, window)
    surf = pygame.transform.scale(logical, (sw, sh))
    window.fill((0, 0, 0))
    window.blit(surf, (x, y))
    pygame.display.flip()
    return scale, x, y


# ----------------- Text helpers (clipping + safe wrapping) -----------------

def _wrap_text_safe(font: pygame.font.Font, text: str, max_w: int) -> list[str]:
    """
    Word-wrap that never overflows: splits long tokens at character level.
    Handles newlines.
    """
    out: list[str] = []
    for para in text.split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            test = (line + (" " if line else "") + w) if w else (line + " ").rstrip()
            if font.size(test)[0] <= max_w:
                line = test
                continue

            if line:
                out.append(line)
                line = ""

            # token fits alone?
            if font.size(w)[0] <= max_w:
                line = w
            else:
                # split token by characters
                chunk = ""
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


def draw_text_box(
    dst: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int] = WHITE,
    padding: int = 6,
    line_gap: int = 2,
    max_lines: int | None = None,
) -> None:
    """Draw wrapped text inside rect; always clipped to rect."""
    inner = rect.inflate(-padding * 2, -padding * 2)
    prev = dst.get_clip()
    dst.set_clip(inner)

    lines = _wrap_text_safe(font, text, inner.width)
    if max_lines is not None:
        lines = lines[:max_lines]

    y = inner.top
    lh = font.get_height() + line_gap
    for ln in lines:
        if y + lh > inner.bottom + 1:
            break
        surf = font.render(ln, False, color)
        dst.blit(surf, (inner.left, y))
        y += lh

    dst.set_clip(prev)


def banner(dst: pygame.Surface, rect: pygame.Rect, text: str, font: pygame.font.Font, danger: bool = False) -> None:
    """A toast-like banner that uses safe wrap + clipping."""
    bg = (0xD6, 0x29, 0x36) if danger else (0x16, 0x52, 0x9F)
    pygame.draw.rect(dst, OUTLINE_BLACK, rect, 2)
    inner = rect.inflate(-4, -4)
    pygame.draw.rect(dst, bg, inner)
    draw_text_box(dst, inner, text, font, color=WHITE, padding=4, max_lines=2)


# ----------------- Scene system -----------------

class Scene:
    def __init__(self, game: "Game"):
        self.game = game

    def handle(self, ev: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, dst: pygame.Surface) -> None:
        pass


@dataclass
class Game:
    window: pygame.Surface
    logical: pygame.Surface
    assets: any
    save_dir: str
    level_by_week: dict[int, Level]
    current_save: SaveSlot | None = None
    running: bool = True
    stack: list[Scene] = None
    toast_msg: str | None = None

    # viewport mapping
    view_scale: int = 1
    view_offset: tuple[int, int] = (0, 0)
    mouse_logical: tuple[int, int] = (0, 0)

    def to_logical(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        sx = max(1, int(self.view_scale))
        ox, oy = self.view_offset
        x = (pos[0] - ox) // sx
        y = (pos[1] - oy) // sx
        if x < 0 or y < 0 or x >= LOGICAL_W or y >= LOGICAL_H:
            return None
        return int(x), int(y)

    def push(self, scene: Scene) -> None:
        self.stack.append(scene)

    def pop(self) -> None:
        if len(self.stack) > 1:
            self.stack.pop()

    def replace(self, scene: Scene) -> None:
        self.stack = [scene]

    def scene(self) -> Scene:
        return self.stack[-1]


# ----------------- Dialogue / story -----------------

class DialogueScene(Scene):
    def __init__(self, game: Game, pages: list[tuple[str, str]], on_done: Callable[[], None]):
        super().__init__(game)
        self.pages = pages
        self.i = 0
        self.on_done = on_done
        self.btn_next = Button(pygame.Rect(280, 176, 88, 24), "NEXT", primary=True)
        self.btn_skip = Button(pygame.Rect(16, 176, 88, 24), "SKIP", primary=False)

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._next()
                return
            if ev.key == pygame.K_ESCAPE:
                self._finish()
                return

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_next.hit(ev.pos):
                self._next()
            elif self.btn_skip.hit(ev.pos):
                self._finish()

    def _next(self) -> None:
        self.i += 1
        if self.i >= len(self.pages):
            self._finish()

    def _finish(self) -> None:
        self.on_done()

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        pygame.draw.rect(dst, NAVY_DEEP, pygame.Rect(0, 0, LOGICAL_W, 24))
        dst.blit(self.game.assets.font_m.render("STORY", False, WHITE), (LOGICAL_W // 2 - 20, 6))

        panel(dst, pygame.Rect(16, 32, 352, 136), "DIALOGUE", self.game.assets.font_s)

        speaker, text = self.pages[min(self.i, len(self.pages) - 1)]
        draw_text_box(dst, pygame.Rect(24, 46, 336, 18), speaker, self.game.assets.font_m, color=OFF_WHITE, padding=0, max_lines=1)
        draw_text_box(dst, pygame.Rect(24, 66, 336, 96), text, self.game.assets.font_s, color=WHITE, padding=0)

        mx, my = self.game.mouse_logical
        self.btn_skip.draw(dst, self.game.assets.font_s, self.btn_skip.rect.collidepoint((mx, my)))
        self.btn_next.draw(dst, self.game.assets.font_s, self.btn_next.rect.collidepoint((mx, my)))


# ----------------- Title -----------------

class TitleScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        self.btn_play = Button(pygame.Rect(140, 140, 104, 32), "PLAY", primary=True)
        self.btn_quit = Button(pygame.Rect(140, 176, 104, 24), "QUIT")

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_play.hit(ev.pos):
                self.game.push(SaveSlotsScene(self.game))
            elif self.btn_quit.hit(ev.pos):
                self.game.running = False

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        pygame.draw.rect(dst, NAVY_DEEP, pygame.Rect(0, 0, LOGICAL_W, 24))

        title = self.game.assets.font_l.render("CODE OF PRIDE", False, WHITE)
        dst.blit(title, (LOGICAL_W // 2 - title.get_width() // 2, 2))

        # Logo
        if getattr(self.game.assets, "logo", None):
            logo = self.game.assets.logo
            target_h = 88
            scale = target_h / max(1, logo.get_height())
            w = max(24, int(logo.get_width() * scale))
            h = max(24, int(logo.get_height() * scale))
            dst.blit(pygame.transform.scale(logo, (w, h)), (16, 46))

        draw_text_box(dst, pygame.Rect(170, 58, 200, 44),
                      "RETRO BAND CODING\nEDIT • RUN • WATCH • IMPROVE",
                      self.game.assets.font_m, color=OFF_WHITE, padding=0)

        mx, my = self.game.mouse_logical
        self.btn_play.draw(dst, self.game.assets.font_m, self.btn_play.rect.collidepoint((mx, my)))
        self.btn_quit.draw(dst, self.game.assets.font_m, self.btn_quit.rect.collidepoint((mx, my)))


# ----------------- Save slots -----------------

class SaveSlotsScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        self.btn_back = Button(pygame.Rect(24, 176, 96, 24), "BACK")
        self.rows = []
        y = 56
        for slot in (1, 2, 3):
            self.rows.append((
                slot,
                pygame.Rect(24, y, 344, 36),
                Button(pygame.Rect(200, y + 6, 56, 24), "NEW", primary=True),
                Button(pygame.Rect(260, y + 6, 56, 24), "LOAD"),
                Button(pygame.Rect(320, y + 6, 48, 24), "DEL"),
            ))
            y += 44

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_back.hit(ev.pos):
                self.game.pop()
                return

            for slot, card, b_new, b_load, b_del in self.rows:
                s = load_slot(self.game.save_dir, slot)

                if b_del.hit(ev.pos) and s:
                    delete_slot(self.game.save_dir, slot)
                    self.game.toast_msg = "Deleted."
                    return

                if b_load.hit(ev.pos) and s:
                    self.game.current_save = s
                    self.game.replace(CampaignHubScene(self.game))
                    return

                if b_new.hit(ev.pos) and not s:
                    s = SaveSlot(slot=slot, name="DIRECTOR")
                    write_slot(self.game.save_dir, s)
                    self.game.current_save = s
                    self.game.replace(CampaignHubScene(self.game))
                    return

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        panel(dst, pygame.Rect(16, 32, 352, 136), "SAVE SLOTS", self.game.assets.font_m)

        mx, my = self.game.mouse_logical
        for slot, card, b_new, b_load, b_del in self.rows:
            s = load_slot(self.game.save_dir, slot)
            pygame.draw.rect(dst, OUTLINE_BLACK, card, 2)
            pygame.draw.rect(dst, NAVY_DEEP, card.inflate(-4, -4))

            label = f"SLOT {slot} — EMPTY" if not s else f"SLOT {slot} — WEEK {s.week_unlocked} • {s.pride_points} PP"
            draw_text_box(dst, pygame.Rect(card.left + 10, card.top + 8, 180, 18),
                          label, self.game.assets.font_m, color=WHITE, padding=0, max_lines=1)

            b_new.enabled = (s is None)
            b_load.enabled = (s is not None)
            b_del.enabled = (s is not None)

            b_new.draw(dst, self.game.assets.font_s, b_new.rect.collidepoint((mx, my)))
            b_load.draw(dst, self.game.assets.font_s, b_load.rect.collidepoint((mx, my)))
            b_del.draw(dst, self.game.assets.font_s, b_del.rect.collidepoint((mx, my)))

        self.btn_back.draw(dst, self.game.assets.font_m, self.btn_back.rect.collidepoint((mx, my)))

        if self.game.toast_msg:
            toast(dst, pygame.Rect(120, 8, 144, 20), self.game.toast_msg, self.game.assets.font_s)
            self.game.toast_msg = None


# ----------------- Schedule hub -----------------

class CampaignHubScene(Scene):
    def __init__(self, game: Game):
        super().__init__(game)
        self.btn_home = Button(pygame.Rect(24, 176, 96, 24), "HOME")
        self.btn_sandbox = Button(pygame.Rect(280, 176, 88, 24), "SANDBOX", primary=True)
        self.selected_week = game.current_save.last_played_week if game.current_save else 1

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_home.hit(ev.pos):
                self.game.replace(TitleScene(self.game))
                return
            if self.btn_sandbox.hit(ev.pos):
                self.game.push(LevelScene(self.game, None, sandbox=True))
                return

            if pygame.Rect(16, 48, 352, 44).collidepoint(ev.pos):
                relx = ev.pos[0] - 16
                w = 1 + (relx // 22)
                self.selected_week = max(1, min(16, int(w)))

            if pygame.Rect(140, 132, 104, 32).collidepoint(ev.pos):
                self._start_selected()

    def _start_selected(self) -> None:
        s = self.game.current_save
        if not s:
            return
        if self.selected_week > s.week_unlocked:
            return

        lvl = self.game.level_by_week.get(self.selected_week)
        if not lvl:
            self.game.toast_msg = "Week not implemented yet."
            return

        s.last_played_week = self.selected_week
        write_slot(self.game.save_dir, s)

        # Story gates for Week 1: Intro -> Briefing -> Lesson -> Practice
        if self.selected_week == 1 and not getattr(s, "intro_seen", False):
            s.intro_seen = True
            write_slot(self.game.save_dir, s)

            def after_intro() -> None:
                self.game.pop()
                self.game.push(DialogueScene(self.game, WEEK1_BRIEFING, on_done=after_brief))

            def after_brief() -> None:
                self.game.pop()
                s2 = self.game.current_save
                if s2:
                    s2.week1_briefing_seen = True
                    write_slot(self.game.save_dir, s2)
                self.game.push(DialogueScene(self.game, WEEK1_LESSON, on_done=start_practice))

            def start_practice() -> None:
                self.game.pop()
                s3 = self.game.current_save
                if s3:
                    s3.week1_lesson_seen = True
                    write_slot(self.game.save_dir, s3)
                self.game.push(LevelScene(self.game, lvl, sandbox=False))

            self.game.push(DialogueScene(self.game, INTRO_PAGES, on_done=after_intro))
            return

        if self.selected_week == 1 and not getattr(s, "week1_briefing_seen", False):
            def after_brief2() -> None:
                self.game.pop()
                s2 = self.game.current_save
                if s2:
                    s2.week1_briefing_seen = True
                    write_slot(self.game.save_dir, s2)
                self.game.push(DialogueScene(self.game, WEEK1_LESSON, on_done=start_practice2))

            def start_practice2() -> None:
                self.game.pop()
                s3 = self.game.current_save
                if s3:
                    s3.week1_lesson_seen = True
                    write_slot(self.game.save_dir, s3)
                self.game.push(LevelScene(self.game, lvl, sandbox=False))

            self.game.push(DialogueScene(self.game, WEEK1_BRIEFING, on_done=after_brief2))
            return

        if self.selected_week == 1 and not getattr(s, "week1_lesson_seen", False):
            def start_practice3() -> None:
                self.game.pop()
                s3 = self.game.current_save
                if s3:
                    s3.week1_lesson_seen = True
                    write_slot(self.game.save_dir, s3)
                self.game.push(LevelScene(self.game, lvl, sandbox=False))

            self.game.push(DialogueScene(self.game, WEEK1_LESSON, on_done=start_practice3))
            return

        self.game.push(LevelScene(self.game, lvl, sandbox=False))

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        pygame.draw.rect(dst, NAVY_DEEP, pygame.Rect(0, 0, LOGICAL_W, 24))
        dst.blit(self.game.assets.font_m.render("SEASON SCHEDULE", False, WHITE), (LOGICAL_W // 2 - 60, 6))

        s = self.game.current_save
        if s:
            pct = (s.week_unlocked - 1) / 15
            progress_bar(dst, pygame.Rect(16, 24, 352, 16), pct, f"WEEK {s.week_unlocked}/16", self.game.assets.font_s)

        panel(dst, pygame.Rect(16, 40, 352, 56), "WEEKS", self.game.assets.font_s)
        x = 20
        y = 60
        for w in range(1, 17):
            r = pygame.Rect(x, y, 20, 20)
            locked = bool(s and w > s.week_unlocked)
            col = (40, 40, 40) if locked else (230, 200, 90)
            pygame.draw.rect(dst, OUTLINE_BLACK, r, 2)
            pygame.draw.rect(dst, col, r.inflate(-4, -4))
            if w == self.selected_week:
                pygame.draw.rect(dst, WHITE, r, 1)
            num = self.game.assets.font_s.render(str(w), False, OUTLINE_BLACK if locked else NAVY_DEEP)
            dst.blit(num, (r.centerx - num.get_width() // 2, r.centery - num.get_height() // 2))
            x += 22

        panel(dst, pygame.Rect(16, 104, 352, 72), "THIS WEEK", self.game.assets.font_s)
        lvl = self.game.level_by_week.get(self.selected_week)
        if lvl:
            draw_text_box(dst, pygame.Rect(28, 122, 336, 18), f"WEEK {lvl.week}: {lvl.title}", self.game.assets.font_m, color=WHITE, padding=0, max_lines=1)
            draw_text_box(dst, pygame.Rect(28, 140, 336, 14), f"Mentor: {lvl.mentor}", self.game.assets.font_s, color=OFF_WHITE, padding=0, max_lines=1)

        mx, my = self.game.mouse_logical
        can = bool(s and lvl and self.selected_week <= s.week_unlocked)
        cont = Button(pygame.Rect(140, 132, 104, 32), "CONTINUE", primary=True, enabled=can)
        cont.draw(dst, self.game.assets.font_m, cont.rect.collidepoint((mx, my)))

        self.btn_home.draw(dst, self.game.assets.font_m, self.btn_home.rect.collidepoint((mx, my)))
        self.btn_sandbox.draw(dst, self.game.assets.font_s, self.btn_sandbox.rect.collidepoint((mx, my)))

        if self.game.toast_msg:
            toast(dst, pygame.Rect(88, 180, 208, 28), self.game.toast_msg, self.game.assets.font_s)
            self.game.toast_msg = None


# ----------------- Score -----------------

class ScoreScene(Scene):
    def __init__(self, game: Game, gained: int):
        super().__init__(game)
        self.gained = gained
        self.btn_ok = Button(pygame.Rect(140, 176, 104, 32), "OK", primary=True)

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.btn_ok.hit(ev.pos):
                while len(self.game.stack) > 1 and not isinstance(self.game.scene(), CampaignHubScene):
                    self.game.pop()
                self.game.pop()
                return

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        panel(dst, pygame.Rect(48, 40, 288, 136), "SCOREBOARD", self.game.assets.font_m)
        big = self.game.assets.font_l.render(f"+{self.gained} PP", False, WHITE)
        dst.blit(big, (LOGICAL_W // 2 - big.get_width() // 2, 62))
        s = self.game.current_save
        if s:
            draw_text_box(dst, pygame.Rect(92, 104, 200, 18), f"Total PP: {s.pride_points}", self.game.assets.font_m, color=OFF_WHITE, padding=0, max_lines=1)
        mx, my = self.game.mouse_logical
        self.btn_ok.draw(dst, self.game.assets.font_m, self.btn_ok.rect.collidepoint((mx, my)))


# ----------------- Level / practice -----------------

class LevelScene(Scene):
    def __init__(self, game: Game, level: Optional[Level], sandbox: bool):
        super().__init__(game)
        self.level = level
        self.sandbox = sandbox
        self.band = Band()

        self.error: str | None = None

        self.playing = False
        self.timeline = []
        self.timeline_i = 0
        self.count_timer = 0.0
        self.count_step = 0.10

        self.editor_rect = pygame.Rect(16, 48, 184, 124)
        self.field_rect = pygame.Rect(208, 48, 160, 124)

        self.btn_run = Button(pygame.Rect(16, 184, 88, 24), "RUN", primary=True, hotkey="Ctrl+R")
        self.btn_reset = Button(pygame.Rect(112, 184, 96, 24), "RESET", hotkey="Ctrl+E")
        self.btn_hint = Button(pygame.Rect(216, 184, 96, 24), "HINT", hotkey="Ctrl+H", enabled=not sandbox)
        self.btn_back = Button(pygame.Rect(300, 184, 72, 24), "BACK", hotkey="Esc")

        starter = "# Sandbox: experiment.\n" if sandbox else (level.starter_code if level else "")
        if (not sandbox) and level and game.current_save:
            key = f"week_{level.week}"
            code_by = getattr(game.current_save, "code_by_level", {}) or {}
            if key in code_by:
                starter = code_by[key]

        self.editor = TextEditor(self.editor_rect, starter)
        self._load_level()

    def _save_code(self) -> None:
        if self.sandbox or not self.level or not self.game.current_save:
            return
        key = f"week_{self.level.week}"
        self.game.current_save.code_by_level[key] = self.editor.get_text()
        write_slot(self.game.save_dir, self.game.current_save)

    def _load_level(self) -> None:
        self.band.entities.clear()
        self.band.reset_actions()
        self.error = None
        self.playing = False
        self.timeline = []
        self.timeline_i = 0
        self.count_timer = 0.0

        if self.level and not self.sandbox:
            for e in self.level.start_entities:
                self.band.spawn(e["name"], e["section"], e["x"], e["y"])

    def _tutorial_gate_message(self) -> str | None:
        # Week 1: Leah (DM) teaches variables; Jacob (Perc) teaches counts.
        if self.sandbox or not self.level:
            return None
        if self.level.week != 1:
            return None

        code = self.editor.get_text()

        # Leah: name your dot (variables)
        if not re.search(r"^\s*target_x\s*=\s*\d+", code, flags=re.M):
            return "LEAH (DM): Pick your dot. Set target_x = the target X."
        if not re.search(r"^\s*target_y\s*=\s*\d+", code, flags=re.M):
            return "LEAH (DM): Now set target_y = the target Y."

        # Jacob: call the move + lock the counts
        if not re.search(r"band\.step_to\(\s*[\"']DM[\"']\s*,\s*target_x\s*,\s*target_y", code):
            return 'JACOB (PERC): Call the move: band.step_to("DM", target_x, target_y, ...)'
        if not re.search(r"counts\s*=\s*8", code):
            return "JACOB (PERC): Lock the cadence: counts=8 for an 8-count phrase."

        return None

    def _objective_met(self) -> bool:
        if self.sandbox or not self.level:
            return False
        obj = self.level.objective
        if obj.get("type") == "reach":
            name = obj["entity"]
            tx, ty = obj["target"]["x"], obj["target"]["y"]
            x, y = self.band.get_pos(name)
            return (x, y) == (tx, ty)
        return False

    def _run(self) -> None:
        self._save_code()

        gate = self._tutorial_gate_message()
        if gate:
            self.error = gate
            return

        self._load_level()

        env = {"band": self.band}
        result = run_player_code(self.editor.get_text(), env)
        if not result.ok:
            self.error = result.error
            return

        if hasattr(self.band, "make_timeline"):
            self.timeline = self.band.make_timeline(max_counts=128)
        else:
            self.band.simulate(max_counts=128)
            self.timeline = []

        self.timeline_i = 0
        self.count_timer = 0.0
        if self.timeline and hasattr(self.band, "apply_snapshot"):
            self.band.apply_snapshot(self.timeline[0])
        self.playing = True
        self.error = None

    def _reset(self) -> None:
        self.playing = False
        self._load_level()
        if self.level and not self.sandbox:
            self.editor.set_text(self.level.starter_code)
        else:
            self.editor.set_text("# Sandbox: experiment.\n")

    def _hint(self) -> None:
        if self.sandbox or not self.level:
            return
        self.editor.lines.append("")
        self.editor.lines.append(f"# HINT: {self.level.hint_text}")
        self.editor.cy = len(self.editor.lines) - 1
        self.editor.cx = len(self.editor.lines[-1])

    def update(self, dt: float) -> None:
        if not self.playing:
            return
        self.count_timer += dt
        while self.count_timer >= self.count_step and self.playing:
            self.count_timer -= self.count_step
            self.timeline_i += 1
            if self.timeline_i >= len(self.timeline):
                self.playing = False
                if self._objective_met():
                    self._award_points()
                else:
                    self.error = "Objective not met. Adjust code and run again."
                break
            if hasattr(self.band, "apply_snapshot"):
                self.band.apply_snapshot(self.timeline[self.timeline_i])

    def _award_points(self) -> None:
        if self.sandbox or not self.level or not self.game.current_save:
            return
        s = self.game.current_save
        s.pride_points += 100
        if s.week_unlocked == self.level.week and s.week_unlocked < 16:
            s.week_unlocked += 1
        write_slot(self.game.save_dir, s)
        self.game.push(ScoreScene(self.game, 100))

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self._save_code()
                self.game.pop()
                return

            mod = pygame.key.get_mods()
            if mod & pygame.KMOD_CTRL:
                if ev.key == pygame.K_r:
                    self._run()
                    return
                if ev.key == pygame.K_e:
                    self._reset()
                    return
                if ev.key == pygame.K_h:
                    self._hint()
                    return

            self.editor.handle_key(ev)

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.playing:
                return
            if self.btn_run.hit(ev.pos):
                self._run()
            elif self.btn_reset.hit(ev.pos):
                self._reset()
            elif self.btn_hint.hit(ev.pos):
                self._hint()
            elif self.btn_back.hit(ev.pos):
                self._save_code()
                self.game.pop()

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        pygame.draw.rect(dst, NAVY_DEEP, pygame.Rect(0, 0, LOGICAL_W, 24))

        header = "SANDBOX" if self.sandbox else (f"WEEK {self.level.week}: {self.level.title}" if self.level else "PRACTICE")
        draw_text_box(dst, pygame.Rect(16, 4, 260, 18), header, self.game.assets.font_m, color=WHITE, padding=0, max_lines=1)

        pp = self.game.current_save.pride_points if self.game.current_save else 0
        draw_text_box(dst, pygame.Rect(LOGICAL_W - 80, 4, 72, 18), f"PP {pp}", self.game.assets.font_m, color=OFF_WHITE, padding=0, max_lines=1)

        # Mentor line (safe, clipped)
        if self.level and not self.sandbox:
            banner(dst, pygame.Rect(16, 24, 352, 20), self.level.dialogue_pre, self.game.assets.font_s, danger=False)

        panel(dst, pygame.Rect(16, 40, 184, 136), "CODE", self.game.assets.font_s)
        panel(dst, pygame.Rect(208, 40, 160, 136), "FIELD", self.game.assets.font_s)

        code_font = getattr(self.game.assets, "font_code", None) or self.game.assets.font_s
        self.editor.draw(dst, code_font)

        fr = self.field_rect
        pygame.draw.rect(dst, OUTLINE_BLACK, fr, 2)
        inner = fr.inflate(-4, -4)
        pygame.draw.rect(dst, (40, 120, 60), inner)

        for gx in range(0, inner.width, U):
            pygame.draw.line(dst, (30, 90, 50), (inner.left + gx, inner.top), (inner.left + gx, inner.bottom), 1)
        for gy in range(0, inner.height, U):
            pygame.draw.line(dst, (30, 90, 50), (inner.left, inner.top + gy), (inner.right, inner.top + gy), 1)

        for e in self.band.entities.values():
            px = inner.left + e.x * (U // 2)
            py = inner.top + e.y * (U // 2)
            pygame.draw.rect(dst, OUTLINE_BLACK, pygame.Rect(px - 3, py - 3, 8, 8), 1)
            pygame.draw.rect(dst, (240, 220, 120), pygame.Rect(px - 2, py - 2, 6, 6))

        if self.level and not self.sandbox:
            obj = self.level.objective
            if obj.get("type") == "reach":
                line = f"Objective: {obj['entity']} to ({obj['target']['x']},{obj['target']['y']})"
                draw_text_box(dst, pygame.Rect(16, 172, 352, 12), line, self.game.assets.font_s, color=OFF_WHITE, padding=4, max_lines=1)

        busy = self.playing
        self.btn_run.enabled = not busy
        self.btn_reset.enabled = not busy
        if not self.sandbox:
            self.btn_hint.enabled = not busy

        mx, my = self.game.mouse_logical
        self.btn_run.draw(dst, self.game.assets.font_s, self.btn_run.rect.collidepoint((mx, my)))
        self.btn_reset.draw(dst, self.game.assets.font_s, self.btn_reset.rect.collidepoint((mx, my)))
        self.btn_hint.draw(dst, self.game.assets.font_s, self.btn_hint.rect.collidepoint((mx, my)))
        self.btn_back.draw(dst, self.game.assets.font_s, self.btn_back.rect.collidepoint((mx, my)))

        if self.error:
            banner(dst, pygame.Rect(16, 156, 352, 20), self.error, self.game.assets.font_s, danger=True)