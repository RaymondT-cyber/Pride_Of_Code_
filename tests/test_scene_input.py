import os
import tempfile
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from cop.levels import Level
from cop.scenes import Game, LevelScene, TitleScene, compute_viewport


class SceneInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _assets(self):
        return SimpleNamespace(
            font_s=pygame.font.Font(None, 12),
            font_m=pygame.font.Font(None, 16),
            font_l=pygame.font.Font(None, 24),
            logo=pygame.Surface((64, 64), pygame.SRCALPHA),
        )

    def _make_game(self):
        window = pygame.Surface((384 * 2, 216 * 2))
        logical = pygame.Surface((384, 216))
        return Game(window=window, logical=logical, assets=self._assets(), save_dir=".", level_by_week={}, stack=[])

    def test_title_scene_click_guard_has_default_playing_flag(self):
        game = self._make_game()
        scene = TitleScene(game)
        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (0, 0)})
        # Should not raise AttributeError due to missing `playing`.
        scene.handle(ev)

    def test_title_scene_layout_keeps_copy_above_buttons(self):
        game = self._make_game()
        game.mouse_logical = (0, 0)
        scene = TitleScene(game)
        scene.draw(game.logical)
        info_bottom = 72 + (len(scene.info_lines) - 1) * 14 + 12
        self.assertGreaterEqual(scene.btn_play.rect.top, info_bottom + 8)

    def test_level_scene_objective_text_for_reach(self):
        level = Level(
            id=1,
            week=1,
            title="First Downbeat",
            mentor="LEAH",
            dialogue_pre="Ready",
            hint_text="Use step_to",
            dialogue_post="Great",
            allowed_api=["spawn", "step_to"],
            start_entities=[{"name": "D1", "section": "DRUM", "x": 2, "y": 2}],
            objective={"type": "reach", "entity": "D1", "target": {"x": 10, "y": 4}},
            starter_code="band.step_to('D1', 10, 4, counts=8)\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            game = Game(
                window=pygame.Surface((384 * 2, 216 * 2)),
                logical=pygame.Surface((384, 216)),
                assets=self._assets(),
                save_dir=tmp,
                level_by_week={1: level},
                stack=[],
            )
            scene = LevelScene(game, level, sandbox=False)
            self.assertIn("Objective: D1 to (10,4)", scene._objective_text())

    def test_viewport_scale_is_integer_and_nonzero(self):
        logical = pygame.Surface((384, 216))
        window = pygame.Surface((1000, 600))
        scale, x, y, sw, sh = compute_viewport(logical, window)
        self.assertGreaterEqual(scale, 1)
        self.assertEqual(sw, logical.get_width() * scale)
        self.assertEqual(sh, logical.get_height() * scale)


if __name__ == "__main__":
    unittest.main()
