\
from __future__ import annotations

import os
import pygame

from .constants import WHITE

class Assets:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.logo = None
        self.font_s = None
        self.font_m = None
        self.font_l = None

    def load(self) -> None:
        # Fonts: built-in, rendered with antialias=False to keep pixel edges.
        self.font_s = pygame.font.Font(None, 12)
        self.font_m = pygame.font.Font(None, 16)
        self.font_l = pygame.font.Font(None, 24)

        logo_path = os.path.join(self.base_dir, "assets", "cgu_cougar_logo.png")
        if os.path.exists(logo_path):
            img = pygame.image.load(logo_path).convert_alpha()
            # Pixel-orthodox: never smoothscale; scale with integer-ish factor later.
            self.logo = img
        else:
            self.logo = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.logo, WHITE, (16, 16), 15, 2)
