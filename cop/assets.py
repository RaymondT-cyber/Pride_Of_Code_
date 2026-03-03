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
        self.font_code = None
        self.font_code_s = None

    def load(self) -> None:
        """
        Typography goals:
        - readable at low logical resolution (384x216)
        - crisp when scaled up (we always integer-scale the whole framebuffer)
        - consistent line height (use font.get_linesize())
        """
        # Use system monospace if available for code, fall back to default.
        # NOTE: UI now renders with antialias=True for readability (especially when scaled).
        self.font_s = pygame.font.Font(None, 18)   # body
        self.font_m = pygame.font.Font(None, 24)   # headings/buttons
        self.font_l = pygame.font.Font(None, 40)   # big titles

        try:
            self.font_code = pygame.font.SysFont("Consolas", 18)
        except Exception:
            self.font_code = pygame.font.Font(None, 18)


        try:
            self.font_code_s = pygame.font.SysFont("Consolas", 14)
        except Exception:
            self.font_code_s = pygame.font.Font(None, 14)

        logo_path = os.path.join(self.base_dir, "assets", "cgu_cougar_logo.png")
        if os.path.exists(logo_path):
            img = pygame.image.load(logo_path).convert_alpha()
            self.logo = img
        else:
            self.logo = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.logo, WHITE, (16, 16), 15, 2)
