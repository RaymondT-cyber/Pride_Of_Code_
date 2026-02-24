from __future__ import annotations

import os
import pygame
from dataclasses import dataclass
from typing import Optional, Callable

from .constants import LOGICAL_W, LOGICAL_H, U, FPS, CASA_BLUE, NAVY_DEEP, WHITE, OFF_WHITE, OUTLINE_BLACK
from .ui import Button, panel, toast, progress_bar, TextEditor, header_bar
from .band import Band
from .code_runner import run_player_code
from .save import SaveSlot, load_slot, write_slot, delete_slot, save_level_code
from .levels import Level

def compute_viewport(logical: pygame.Surface, window: pygame.Surface) -> tuple[int,int,int,int,int]:
    """Returns (scale, x_off, y_off, scaled_w, scaled_h) for integer pixel-perfect presentation."""
    lw, lh = logical.get_size()
    ww, wh = window.get_size()
    scale = max(1, min(ww // lw, wh // lh))
    sw, sh = lw * scale, lh * scale
    x = (ww - sw) // 2
    y = (wh - sh) // 2
    return scale, x, y, sw, sh

def present(logical: pygame.Surface, window: pygame.Surface) -> tuple[int,int,int]:
    scale, x, y, sw, sh = compute_viewport(logical, window)
    surf = pygame.transform.scale(logical, (sw, sh))
    window.fill((0, 0, 0))
    window.blit(surf, (x, y))
    pygame.display.flip()
    return scale, x, y

class Scene:
    def __init__(self, game: "Game"):
        self.game = game
        # Most scenes are not "playing" an animation timeline; keep a safe default
        # so click handlers can guard on this without per-scene boilerplate.
        self.playing = False

    def handle(self, ev: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, dst: pygame.Surface) -> None:
        pass

class TitleScene(Scene):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.btn_play = Button(pygame.Rect(140, 140, 104, 32), "PLAY", primary=True)
        self.btn_quit = Button(pygame.Rect(140, 176, 104, 24), "QUIT", primary=False)
        self.info_lines = [
            "RETRO BAND CODING",
            "EDIT → RUN → WATCH → IMPROVE",
        ]
        self.logo_rect = pygame.Rect(16, 36, 96, 96)

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.playing:
                return
            if self.btn_play.hit(ev.pos):
                self.game.push(SaveSlotsScene(self.game))
            if self.btn_quit.hit(ev.pos):
                self.game.running = False

    def _draw_branding(self, dst: pygame.Surface) -> None:
        """Draw title, logo, and helper copy with stable non-overlapping layout."""
        if self.game.assets.logo:
            logo = self.game.assets.logo
            target_h = 84
            h0 = max(1, logo.get_height())
            w0 = max(1, logo.get_width())
            scale = target_h / h0
            w = max(24, int(w0 * scale))
            h = max(24, int(h0 * scale))
            scaled = pygame.transform.scale(logo, (w, h))
            self.logo_rect = pygame.Rect(16, 36, w, h)
            dst.blit(scaled, self.logo_rect.topleft)

        info_center_x = (self.logo_rect.right + LOGICAL_W) // 2
        info_y = 72
        for i, line in enumerate(self.info_lines):
            info = self.game.assets.font_m.render(line, False, OFF_WHITE)
            dst.blit(info, (info_center_x - info.get_width()//2, info_y + i * 14))

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        header_bar(dst, pygame.Rect(0, 0, LOGICAL_W, 24), "CODE OF PRIDE", self.game.assets.font_l)
        self._draw_branding(dst)

        # Stable button layout below the title copy.
        self.btn_play.rect.topleft = (140, 132)
        self.btn_quit.rect.topleft = (140, 170)

        mx, my = self.game.mouse_logical
        self.btn_play.draw(dst, self.game.assets.font_m, self.btn_play.rect.collidepoint((mx,my)))
        self.btn_quit.draw(dst, self.game.assets.font_m, self.btn_quit.rect.collidepoint((mx,my)))

class SaveSlotsScene(Scene):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.btn_back = Button(pygame.Rect(8, 184, 72, 24), "BACK")
        self.slot_btns = []
        y0 = 48
        for i in range(1,4):
            self.slot_btns.append((i,
                Button(pygame.Rect(168, y0 + 4, 56, 24), "NEW", primary=True),
                Button(pygame.Rect(228, y0 + 4, 56, 24), "LOAD", primary=False),
                Button(pygame.Rect(288, y0 + 4, 56, 24), "DEL", primary=False)
            ))
            y0 += 44
        self.toast_msg = None

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.playing:
                return
            if self.btn_back.hit(ev.pos):
                self.game.pop()
                return
            for slot, b_new, b_load, b_del in self.slot_btns:
                s = load_slot(self.game.save_dir, slot)
                if b_del.hit(ev.pos):
                    delete_slot(self.game.save_dir, slot)
                    self.toast_msg = "Deleted."
                elif b_load.hit(ev.pos) and s:
                    self.game.current_save = s
                    self.game.replace(CampaignHubScene(self.game))
                elif b_new.hit(ev.pos) and not s:
                    s = SaveSlot(slot=slot, name="DIRECTOR")
                    write_slot(self.game.save_dir, s)
                    self.game.current_save = s
                    self.game.replace(CampaignHubScene(self.game))

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        panel(dst, pygame.Rect(16, 32, 352, 140), "SAVE SLOTS", self.game.assets.font_m)
        mx, my = self.game.mouse_logical

        y = 44
        for slot, b_new, b_load, b_del in self.slot_btns:
            s = load_slot(self.game.save_dir, slot)
            label = f"SLOT {slot} — EMPTY" if not s else f"SLOT {slot} — WEEK {s.week_unlocked} • {s.pride_points} PP"
            # draw slot card
            r = pygame.Rect(28, y, 328, 36)
            pygame.draw.rect(dst, OUTLINE_BLACK, r, 2)
            inner = r.inflate(-4,-4)
            pygame.draw.rect(dst, NAVY_DEEP, inner)
            txt = self.game.assets.font_m.render(label, False, WHITE)
            dst.blit(txt, (r.left+8, r.top+10))

            # buttons
            if s:
                b_new.enabled = False
                b_load.enabled = True
                b_del.enabled = True
            else:
                b_new.enabled = True
                b_load.enabled = False
                b_del.enabled = False
            b_new.draw(dst, self.game.assets.font_s, b_new.rect.collidepoint((mx,my)))
            b_load.draw(dst, self.game.assets.font_s, b_load.rect.collidepoint((mx,my)))
            b_del.draw(dst, self.game.assets.font_s, b_del.rect.collidepoint((mx,my)))
            y += 44

        self.btn_back.draw(dst, self.game.assets.font_m, self.btn_back.rect.collidepoint((mx,my)))

        if self.toast_msg:
            toast(dst, pygame.Rect(88, 180, 208, 28), self.toast_msg, self.game.assets.font_s)
            # fade quickly
            self.toast_msg = None

class CampaignHubScene(Scene):
    def __init__(self, game: "Game"):
        super().__init__(game)
        self.btn_back = Button(pygame.Rect(8, 184, 72, 24), "HOME")
        self.btn_sandbox = Button(pygame.Rect(288, 184, 88, 24), "SANDBOX", primary=True)
        self.selected_week = game.current_save.last_played_week if game.current_save else 1

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.playing:
                return
            if self.btn_back.hit(ev.pos):
                self.game.replace(TitleScene(self.game))
                return
            if self.btn_sandbox.hit(ev.pos):
                self.game.push(LevelScene(self.game, None, sandbox=True))
                return

            # week strip click
            if pygame.Rect(16, 40, 352, 44).collidepoint(ev.pos):
                relx = ev.pos[0] - 16
                week = 1 + (relx // 22)
                week = max(1, min(16, week))
                self.selected_week = week

            # continue
            if pygame.Rect(140, 128, 104, 32).collidepoint(ev.pos):
                self._start_selected()

    def _start_selected(self) -> None:
        if not self.game.current_save:
            return
        if self.selected_week > self.game.current_save.week_unlocked:
            return
        # map week->level id (MVP has level ids 1-5)
        level = self.game.level_by_week.get(self.selected_week)
        if not level:
            self.game.toast_msg = "Week not implemented in MVP."
            return
        self.game.current_save.last_played_week = self.selected_week
        write_slot(self.game.save_dir, self.game.current_save)
        self.game.push(LevelScene(self.game, level, sandbox=False))

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        header_bar(dst, pygame.Rect(0, 0, LOGICAL_W, 24), "SEASON SCHEDULE", self.game.assets.font_m)

        # Top progress
        if self.game.current_save:
            pct = (self.game.current_save.week_unlocked-1)/15
            progress_bar(dst, pygame.Rect(16, 24, 352, 16), pct, f"WEEK {self.game.current_save.week_unlocked}/16", self.game.assets.font_s)

        panel(dst, pygame.Rect(16, 36, 352, 56), "WEEKS", self.game.assets.font_s)

        # week strip
        x = 20
        y = 56
        for w in range(1,17):
            r = pygame.Rect(x, y, 20, 20)
            locked = self.game.current_save and w > self.game.current_save.week_unlocked
            col = (40,40,40) if locked else (230, 200, 90)
            pygame.draw.rect(dst, OUTLINE_BLACK, r, 2)
            pygame.draw.rect(dst, col, r.inflate(-4,-4))
            if w == self.selected_week:
                pygame.draw.rect(dst, WHITE, r, 1)
            num = self.game.assets.font_s.render(str(w), False, OUTLINE_BLACK if locked else NAVY_DEEP)
            dst.blit(num, (r.centerx - num.get_width()//2, r.centery - num.get_height()//2))
            x += 22

        # Detail panel
        panel(dst, pygame.Rect(16, 96, 352, 80), "THIS WEEK", self.game.assets.font_s)
        level = self.game.level_by_week.get(self.selected_week)
        if level:
            txt1 = self.game.assets.font_m.render(f"WEEK {level.week}: {level.title}", False, WHITE)
            dst.blit(txt1, (28, 114))
            txt2 = self.game.assets.font_s.render(f"Mentor: {level.mentor}", False, OFF_WHITE)
            dst.blit(txt2, (28, 132))
        else:
            txt1 = self.game.assets.font_m.render(f"WEEK {self.selected_week}: (not in MVP yet)", False, OFF_WHITE)
            dst.blit(txt1, (28, 120))

        mx, my = self.game.mouse_logical
        # Continue button
        can = self.game.current_save and self.selected_week <= self.game.current_save.week_unlocked and level is not None
        cont = Button(pygame.Rect(140, 140, 104, 32), "CONTINUE", primary=True, enabled=bool(can))
        cont.draw(dst, self.game.assets.font_m, cont.rect.collidepoint((mx,my)))

        self.btn_back.draw(dst, self.game.assets.font_m, self.btn_back.rect.collidepoint((mx,my)))
        self.btn_sandbox.draw(dst, self.game.assets.font_s, self.btn_sandbox.rect.collidepoint((mx,my)))

        if self.game.toast_msg:
            toast(dst, pygame.Rect(88, 180, 208, 28), self.game.toast_msg, self.game.assets.font_s)
            self.game.toast_msg = None

class LevelScene(Scene):
    def __init__(self, game: "Game", level: Optional[Level], sandbox: bool):
        super().__init__(game)
        self.level = level
        self.sandbox = sandbox
        self.band = Band()
        self.error = None
        self.pass_state = False
        self.used_hint = False
        self.playing = False
        self.eval_on_end = False
        self.scrub_drag = False
        self.marker_counts = []
        self.timeline = []
        self.timeline_i = 0
        self.count_timer = 0.0
        self.count_step = 0.12  # seconds per count
        self._pending_lines = 0
        self.eval_on_end = False
        self.marker_counts: list[int] = []
        self.scrub_drag = False
        self.timeline_rect = pygame.Rect(16, 168, 352, 24)

        self.btn_run = Button(pygame.Rect(16, 192, 72, 24), "RUN", primary=True, hotkey="Ctrl+R")
        self.btn_reset = Button(pygame.Rect(92, 192, 72, 24), "RESET", hotkey="Ctrl+E")
        self.btn_hint = Button(pygame.Rect(168, 192, 72, 24), "HINT", hotkey="Ctrl+H", enabled=not sandbox)
        self.btn_back = Button(pygame.Rect(300, 192, 72, 24), "BACK", hotkey="Esc")

        # editor / field layout (split-screen)
        self.editor_rect = pygame.Rect(16, 40, 168, 112)
        self.field_rect = pygame.Rect(200, 40, 168, 112)
        starter = "# Sandbox: write code to move marchers.\n" if sandbox else (level.starter_code if level else "")
        self.editor = TextEditor(self.editor_rect, starter)
        if self.game.current_save:
            saved = self.game.current_save.code_by_level.get(self._level_code_key())
            if saved:
                self.editor.set_text(saved)

        self.toast_pre = level.dialogue_pre if level else ("Sandbox mode: experiment freely.")
        self.toast_post = None

        self._load_level()

    def _level_code_key(self) -> str:
        if self.sandbox:
            return "sandbox"
        return f"week_{self.level.week}" if self.level else "unknown"

    def _autosave_code(self) -> None:
        if not self.game.current_save:
            return
        save_level_code(self.game.save_dir, self.game.current_save, self._level_code_key(), self.editor.get_text())
        self.game.toast_msg = "Saved rehearsal code"

    def _load_level(self) -> None:
        self.band.entities.clear()
        self.band.reset_actions()
        self.error = None
        self.pass_state = False
        if self.level and not self.sandbox:
            for e in self.level.start_entities:
                self.band.spawn(e["name"], e["section"], e["x"], e["y"])

    def _score_and_progress(self, lines_executed: int) -> None:
        if not self.game.current_save or self.sandbox or not self.level:
            return
        base = 100
        code = self.editor.get_text()
        eff = 0
        if "for " in code and "range" in code:
            eff = 20  # loop bonus
        clean = 10  # no error bonus
        hint_pen = -10 if self.used_hint else 0

        # streak
        s = self.game.current_save
        s.streak = (s.streak + 1)
        streak_bonus = 50 if s.streak >= 3 else 0

        total = base + eff + clean + hint_pen + streak_bonus
        s.pride_points += total
        if self.used_hint:
            s.hints_used += 1

        # unlock next week
        if self.level.week == s.week_unlocked and s.week_unlocked < 16:
            s.week_unlocked += 1
        write_slot(self.game.save_dir, s)

        self.game.push(ScoreScene(self.game, total, base, eff, clean, streak_bonus, hint_pen))

    def _objective_met(self) -> bool:
        if self.sandbox or not self.level:
            return False
        obj = self.level.objective
        t = obj.get("type")
        if t == "reach":
            name = obj["entity"]
            tx, ty = obj["target"]["x"], obj["target"]["y"]
            x,y = self.band.get_pos(name)
            return (x,y) == (tx,ty)
        if t == "line":
            # check 5 winds exist at exact positions
            y = obj["y"]
            x0 = obj["x_start"]
            dx = obj["dx"]
            for i in range(obj["count"]):
                name = f"W{i+1}"
                if name not in self.band.entities:
                    return False
                if self.band.get_pos(name) != (x0 + i*dx, y):
                    return False
            return True
        if t == "sync_swap":
            # after sim, we just check expected final x positions for each group
            # winds should be at x=16; perc at x=16
            for n in ["W1","W2","P1","P2"]:
                if n not in self.band.entities:
                    return False
                x,_ = self.band.get_pos(n)
                if x != 16:
                    return False
            return True
        if t == "avoid_collision":
            # ensure entity not on obstacle position at any point (MVP approximates by final position + not landing on obstacle)
            ent = obj["entity"]
            obs = obj["obstacle"]
            if ent not in self.band.entities or obs not in self.band.entities:
                return False
            if self.band.get_pos(ent) == self.band.get_pos(obs):
                return False
            return self.band.get_pos(ent) == (obj["target"]["x"], obj["target"]["y"])
        if t == "arc":
            # rough: just check distances of each from center ~= radius
            cx, cy = obj["center"]["x"], obj["center"]["y"]
            r = obj["radius"]
            names = obj["entities"]
            for n in names:
                if n not in self.band.entities:
                    return False
                x,y = self.band.get_pos(n)
                d = ((x-cx)**2 + (y-cy)**2)**0.5
                if abs(d - r) > 1.5:
                    return False
            return True
        return False

    def _objective_text(self) -> str:
        if self.sandbox or not self.level:
            return "Objective: Free rehearsal"
        obj = self.level.objective
        t = obj.get("type")
        if t == "reach":
            tr = obj["target"]
            return f"Objective: {obj['entity']} to ({tr['x']},{tr['y']})"
        if t == "line":
            return f"Objective: Form line of {obj['count']} at y={obj['y']}"
        if t == "sync_swap":
            return "Objective: Sync swap to x=16"
        if t == "avoid_collision":
            tr = obj["target"]
            return f"Objective: Reach ({tr['x']},{tr['y']}) avoiding {obj['obstacle']}"
        if t == "arc":
            c = obj["center"]
            return f"Objective: Arc radius {obj['radius']} around ({c['x']},{c['y']})"
        return "Objective: Complete the drill"

    def _run(self) -> None:
        self.error = None
        self.pass_state = False
        self.band.reset_actions()

        # Provide API surface per level (MVP: always provide, but conceptually could restrict)
        env = {"band": self.band}

        result = run_player_code(self.editor.get_text(), env)
        if not result.ok:
            self.error = result.error
            self.editor.set_error_line(result.error_line)
            if self.game.current_save and not self.sandbox:
                self.game.current_save.streak = 0
                write_slot(self.game.save_dir, self.game.current_save)
            self._autosave_code()
            return

        # Build playback timeline, then animate it in update()
        self.timeline = self.band.make_timeline(max_counts=128)
        self.timeline_i = 0
        self.count_timer = 0.0
        self._pending_lines = result.lines_executed
        self.eval_on_end = True
        if self.timeline:
            self.band.apply_snapshot(self.timeline[0])
        self._set_markers_from_queue()
        self.playing = True
        self.error = None
        self.editor.set_error_line(None)
        self._autosave_code()

    def _reset(self) -> None:
        self.used_hint = False
        self._load_level()
        if self.level and not self.sandbox:
            self.editor.set_text(self.level.starter_code)
        else:
            self.editor.set_text("# Sandbox: write code to move marchers.\n")

    def _hint(self) -> None:
        if self.sandbox or not self.level:
            return
        self.used_hint = True
        # Append hint as comment
        self.editor.lines.append("")
        self.editor.lines.append(f"# HINT: {self.level.hint_text}")
        self.editor.cy = len(self.editor.lines)-1
        self.editor.cx = len(self.editor.lines[-1])
        self._autosave_code()

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                self._autosave_code()
                self.game.pop()
                return
            mod = pygame.key.get_mods()
            if mod & pygame.KMOD_CTRL:
                if ev.key == pygame.K_r:
                    self._run(); return
                if ev.key == pygame.K_e:
                    self._reset(); return
                if ev.key == pygame.K_h:
                    self._hint(); return
            # Timeline navigation (when a timeline exists)
            if ev.key == pygame.K_SPACE and self.timeline:
                # Toggle playback from current count (replay mode, no scoring)
                if self.playing:
                    self.playing = False
                    self.eval_on_end = False
                else:
                    self.playing = True
                    self.eval_on_end = False
                return
            if ev.key in (pygame.K_LEFT, pygame.K_RIGHT) and self.timeline and not self.playing:
                d = -1 if ev.key == pygame.K_LEFT else 1
                self._set_timeline_i(self.timeline_i + d)
                return
            # editor typing
            self.editor.handle_key(ev)
            self._autosave_code()

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            # Timeline scrub has priority (works even during playback)
            c = self._count_from_timeline_pos(ev.pos)
            if c is not None:
                self.playing = False
                self.eval_on_end = False
                self.scrub_drag = True
                self._set_timeline_i(c)
                return
            if self.playing:
                return
            if self.btn_run.hit(ev.pos): self._run()
            elif self.btn_reset.hit(ev.pos): self._reset()
            elif self.btn_hint.hit(ev.pos): self._hint()
            elif self.btn_back.hit(ev.pos):
                self._autosave_code()
                self.game.pop()

        if ev.type == pygame.MOUSEMOTION and self.scrub_drag:
            c = self._count_from_timeline_pos(ev.pos)
            if c is not None:
                self._set_timeline_i(c)

        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            self.scrub_drag = False

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)

        header = "SANDBOX" if self.sandbox else f"WEEK {self.level.week}: {self.level.title}"
        right = f"PP {self.game.current_save.pride_points}" if self.game.current_save else None
        header_bar(dst, pygame.Rect(0, 0, LOGICAL_W, 24), header, self.game.assets.font_m, right_text=right)

        # Panels
        panel(dst, pygame.Rect(16, 32, 168, 136), "CODE", self.game.assets.font_s)
        panel(dst, pygame.Rect(200, 32, 168, 136), "FIELD", self.game.assets.font_s)

        # Toast
        if self.toast_pre:
            toast(dst, pygame.Rect(16, 24, 352, 24), self.toast_pre, self.game.assets.font_s)

        # Editor
        self.editor.draw(dst, self.game.assets.font_s)

        # Field render (simple yard grid)
        fr = self.field_rect
        pygame.draw.rect(dst, OUTLINE_BLACK, fr, 2)
        inner = fr.inflate(-4,-4)
        pygame.draw.rect(dst, (40, 120, 60), inner)

        # grid
        for gx in range(0, inner.width, U):
            pygame.draw.line(dst, (30, 90, 50), (inner.left+gx, inner.top), (inner.left+gx, inner.bottom), 1)
        for gy in range(0, inner.height, U):
            pygame.draw.line(dst, (30, 90, 50), (inner.left, inner.top+gy), (inner.right, inner.top+gy), 1)

        # midfield line
        pygame.draw.line(dst, (220,220,220), (inner.left + inner.width//2, inner.top), (inner.left + inner.width//2, inner.bottom), 1)

        # entities
        for e in self.band.entities.values():
            # map grid coordinate to inner
            px = inner.left + e.x * (U//2)
            py = inner.top + e.y * (U//2)
            # sprite placeholder
            col = (240, 220, 120)
            if e.section == "PERC": col = (180,180,240)
            if e.section == "BRASS": col = (240,180,180)
            if e.section == "GUARD": col = (220,160,240)
            if e.section == "OBST": col = (50,50,50)
            pygame.draw.rect(dst, OUTLINE_BLACK, pygame.Rect(px-3, py-3, 8, 8), 1)
            pygame.draw.rect(dst, col, pygame.Rect(px-2, py-2, 6, 6))


        # Buttons
        mx,my = self.game.mouse_logical
        busy = self.playing
        self.btn_run.enabled = not busy
        self.btn_reset.enabled = not busy
        if not self.sandbox:
            self.btn_hint.enabled = (not busy)
        self.btn_run.draw(dst, self.game.assets.font_s, self.btn_run.rect.collidepoint((mx,my)))
        self.btn_reset.draw(dst, self.game.assets.font_s, self.btn_reset.rect.collidepoint((mx,my)))
        self.btn_hint.draw(dst, self.game.assets.font_s, self.btn_hint.rect.collidepoint((mx,my)))
        self.btn_back.draw(dst, self.game.assets.font_s, self.btn_back.rect.collidepoint((mx,my)))

        panel(dst, pygame.Rect(16, 156, 352, 12), None, self.game.assets.font_s)
        objective = self.game.assets.font_s.render(self._objective_text(), False, OFF_WHITE)
        dst.blit(objective, (20, 158))

        panel(dst, pygame.Rect(16, 170, 352, 14), None, self.game.assets.font_s)
        count_label = self.game.assets.font_m.render("COUNTS", False, OFF_WHITE)
        dst.blit(count_label, (20, 171))
        if self.timeline:
            pct = min(1.0, self.timeline_i / max(1, len(self.timeline) - 1))
            progress_bar(dst, pygame.Rect(20, 172, 344, 10), pct, f"SET {self.timeline_i}/{max(0, len(self.timeline)-1)}", self.game.assets.font_s)

        if self.error:
            toast(dst, pygame.Rect(16, 142, 352, 14), self.error, self.game.assets.font_s, danger=True)
        elif self.pass_state and self.toast_post:
            toast(dst, pygame.Rect(16, 142, 352, 14), f"PASS: {self.toast_post}", self.game.assets.font_s)

class ScoreScene(Scene):
    def __init__(self, game: "Game", total: int, base: int, eff: int, clean: int, streak: int, hint: int):
        super().__init__(game)
        self.total = total
        self.rows = [
            ("Base Score", base),
            ("Efficiency Bonus", eff),
            ("Clean Run", clean),
            ("Streak Bonus", streak),
            ("Hint Used", hint),
        ]
        self.btn_ok = Button(pygame.Rect(140, 176, 104, 32), "OK", primary=True)

    def handle(self, ev: pygame.event.Event) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.playing:
                return
            if self.btn_ok.hit(ev.pos):
                self.game.pop()

    def draw(self, dst: pygame.Surface) -> None:
        dst.fill(CASA_BLUE)
        panel(dst, pygame.Rect(48, 40, 288, 136), "SCOREBOARD", self.game.assets.font_m)

        big = self.game.assets.font_l.render(f"+{self.total} PP", False, WHITE)
        sh = self.game.assets.font_l.render(f"+{self.total} PP", False, OUTLINE_BLACK)
        dst.blit(sh, (LOGICAL_W//2 - big.get_width()//2 + 1, 58+1))
        dst.blit(big, (LOGICAL_W//2 - big.get_width()//2, 58))

        y = 92
        for name, val in self.rows:
            t = self.game.assets.font_m.render(f"{name}: {val:+d}", False, OFF_WHITE)
            dst.blit(t, (72, y))
            y += 16

        mx, my = self.game.mouse_logical
        self.btn_ok.draw(dst, self.game.assets.font_m, self.btn_ok.rect.collidepoint((mx,my)))

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
    view_scale: int = 1
    view_offset: tuple[int,int] = (0, 0)
    mouse_logical: tuple[int,int] = (0, 0)

    def to_logical(self, pos: tuple[int,int]) -> tuple[int,int] | None:
        """Convert window mouse coords -> logical coords; returns None if outside the letterboxed area."""
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
