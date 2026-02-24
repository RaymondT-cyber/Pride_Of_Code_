import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from cop.scenes import Game, TitleScene, compute_viewport


class SceneInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def _make_game(self):
        window = pygame.Surface((384 * 2, 216 * 2))
        logical = pygame.Surface((384, 216))
        assets = SimpleNamespace(font_s=None, font_m=None, font_l=None, logo=None)
        return Game(window=window, logical=logical, assets=assets, save_dir=".", level_by_week={}, stack=[])

    def test_title_scene_click_guard_has_default_playing_flag(self):
        game = self._make_game()
        scene = TitleScene(game)
        ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (0, 0)})
        # Should not raise AttributeError due to missing `playing`.
        scene.handle(ev)

    def test_viewport_scale_is_integer_and_nonzero(self):
        logical = pygame.Surface((384, 216))
        window = pygame.Surface((1000, 600))
        scale, x, y, sw, sh = compute_viewport(logical, window)
        self.assertGreaterEqual(scale, 1)
        self.assertEqual(sw, logical.get_width() * scale)
        self.assertEqual(sh, logical.get_height() * scale)


if __name__ == "__main__":
    unittest.main()
