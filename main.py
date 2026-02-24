from __future__ import annotations

import os
import pygame

from cop.constants import LOGICAL_W, LOGICAL_H, FPS
from cop.assets import Assets
from cop.levels import load_levels
from cop.scenes import Game, TitleScene, present, compute_viewport

def main() -> None:
    pygame.init()
    pygame.display.set_caption("Code of Pride (MVP)")
    window = pygame.display.set_mode((LOGICAL_W*3, LOGICAL_H*3), pygame.RESIZABLE)
    logical = pygame.Surface((LOGICAL_W, LOGICAL_H))

    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets = Assets(base_dir)
    assets.load()

    meta, levels = load_levels(os.path.join(base_dir, "data", "levels.json"))
    level_by_week = {lv.week: lv for lv in levels}

    save_dir = os.path.join(base_dir, "saves")
    os.makedirs(save_dir, exist_ok=True)

    game = Game(window=window, logical=logical, assets=assets, save_dir=save_dir, level_by_week=level_by_week, stack=[])
    game.push(TitleScene(game))

    clock = pygame.time.Clock()

    while game.running:
        dt = clock.tick(FPS) / 1000.0
        # Keep input aligned with the pixel-perfect letterboxed viewport
        scale, xoff, yoff, sw, sh = compute_viewport(logical, window)
        game.view_scale = scale
        game.view_offset = (xoff, yoff)
        game.mouse_logical = game.to_logical(pygame.mouse.get_pos()) or (-999, -999)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                game.running = False
                break
            # Remap mouse events to logical coords so buttons are clickable when scaled
            if ev.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                if hasattr(ev, 'pos'):
                    lp = game.to_logical(ev.pos)
                    if lp is None:
                        continue
                    ev = pygame.event.Event(ev.type, {**ev.dict, 'pos': lp})
            game.scene().handle(ev)

        game.scene().update(dt)
        game.scene().draw(logical)
        present(logical, window)

    pygame.quit()

if __name__ == "__main__":
    main()
