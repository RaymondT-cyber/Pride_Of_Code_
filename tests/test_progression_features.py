import os
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from cop.code_runner import run_player_code
from cop.save import SaveSlot, load_slot, write_slot


class ProgressionFeatureTests(unittest.TestCase):
    def test_code_runner_returns_error_line_for_name_error(self):
        result = run_player_code("x = 1\nprint(y)\n", env={})
        self.assertFalse(result.ok)
        self.assertEqual(result.error_line, 2)
        self.assertIn("NameError", result.error)

    def test_save_slot_backward_compat_adds_code_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            slot = SaveSlot(slot=1)
            write_slot(tmp, slot)
            loaded = load_slot(tmp, 1)
            self.assertIsNotNone(loaded)
            self.assertIsInstance(loaded.code_by_level, dict)


if __name__ == "__main__":
    unittest.main()
