import os
import tempfile
import unittest
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from cop.levels import Level
from cop.scenes import Game, LevelScene


class TimelineScrubTests(unittest.TestCase):
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

    def _level(self):
        return Level(
            id=1,
            week=1,
            title="First Downbeat",
            mentor="LEAH",
            dialogue_pre="Ready",
            hint_text="Hint",
            dialogue_post="Great",
            allowed_api=["step_to"],
            start_entities=[{"name": "DM", "section": "DM", "x": 1, "y": 1}],
            objective={"type": "reach", "entity": "DM", "target": {"x": 3, "y": 1}},
            starter_code="band.step_to('DM', 3, 1, counts=2)\n",
        )

    def test_count_mapping_and_jump(self):
        level = self._level()
        with tempfile.TemporaryDirectory() as tmp:
            g = Game(
                window=pygame.Surface((768, 432)),
                logical=pygame.Surface((384, 216)),
                assets=self._assets(),
                save_dir=tmp,
                level_by_week={1: level},
                stack=[],
            )
            scene = LevelScene(g, level, sandbox=False)
            scene.timeline = [scene.band.snapshot(), {"DM": (2, 1)}, {"DM": (3, 1)}]
            idx = scene._count_from_timeline_pos((scene.counts_bar_rect.centerx, scene.counts_bar_rect.centery))
            self.assertIsNotNone(idx)
            scene._jump_to_count(idx)
            self.assertGreaterEqual(scene.timeline_i, 1)


if __name__ == "__main__":
    unittest.main()
