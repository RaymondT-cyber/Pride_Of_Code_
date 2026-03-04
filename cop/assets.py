from __future__ import annotations

import os
import pygame

from .constants import WHITE


class Assets:
    def __init__(self, base_dir: str):
        # base_dir comes from main.py and can vary (project root, cop package dir, etc.)
        self.base_dir = base_dir
        self.logo: pygame.Surface | None = None

        # Typography
        self.font_s: pygame.font.Font | None = None
        self.font_m: pygame.font.Font | None = None
        self.font_l: pygame.font.Font | None = None
        self.font_code: pygame.font.Font | None = None
        self.font_code_s: pygame.font.Font | None = None

        # Portraits (story)
        self.portraits: dict[str, pygame.Surface] = {}

    def _find_asset(self, *parts: str) -> str | None:
        """Find an asset path across a few likely roots."""
        roots = []
        # Provided base_dir (sometimes project root, sometimes cop/)
        roots.append(self.base_dir)
        # Parent (if base_dir is cop/)
        roots.append(os.path.dirname(self.base_dir))
        # CWD (when running from repo root in a terminal)
        roots.append(os.getcwd())

        for root in roots:
            p = os.path.join(root, *parts)
            if os.path.exists(p):
                return p
        return None

    @staticmethod
    def _make_logo_transparent(logo: pygame.Surface) -> pygame.Surface:
        """Remove the solid blue disc/background from the cougar logo so it blends."""
        surf = logo.convert_alpha()
        w, h = surf.get_size()
        # Sample center pixel (usually the blue disc). We'll remove colors close to it.
        cx, cy = w // 2, h // 2
        key = surf.get_at((cx, cy))
        key_rgb = (key.r, key.g, key.b)

        out = pygame.Surface((w, h), pygame.SRCALPHA)
        px = pygame.PixelArray(surf)
        out_px = pygame.PixelArray(out)

        # Tolerance tuned for this logo: remove disc blue + any near-black padding.
        tol_disc = 45
        tol_black = 18

        def close(a, b, tol):
            return abs(a[0]-b[0]) <= tol and abs(a[1]-b[1]) <= tol and abs(a[2]-b[2]) <= tol

        for y in range(h):
            for x in range(w):
                c = surf.unmap_rgb(px[x, y])
                rgb = (c.r, c.g, c.b)
                if close(rgb, key_rgb, tol_disc) or close(rgb, (0, 0, 0), tol_black):
                    out_px[x, y] = (0, 0, 0, 0)
                else:
                    out_px[x, y] = c

        del px
        del out_px
        return out

    def load(self) -> None:
        """
        Visual goals (pixel UI):
        - keep the retro/pixel vibe (no smooth system fonts)
        - readable at 384x216
        - monospace for code
        """
        # Default pygame font is crisp in this game because we scale the framebuffer.
        # (We also render with antialias=False throughout the UI helpers.)
        self.font_s = pygame.font.Font(None, 18)
        self.font_m = pygame.font.Font(None, 24)
        self.font_l = pygame.font.Font(None, 44)

        self.font_code = pygame.font.Font(None, 16)
        self.font_code_s = pygame.font.Font(None, 12)

        # Logo (try multiple roots so it never falls back accidentally)
        logo_path = self._find_asset("assets", "cgu_cougar_logo.png")
        if logo_path:
            try:
                raw = pygame.image.load(logo_path).convert_alpha()
                self.logo = self._make_logo_transparent(raw)
            except Exception:
                self.logo = None

        if not self.logo:
            # Fallback: no huge ring, just a tiny badge so the title screen doesn't look broken.
            self.logo = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(self.logo, WHITE, (12, 12), 10, 2)

        # Story portraits (optional)
        portraits_dir = self._find_asset("assets", "portraits")
        if portraits_dir and os.path.isdir(portraits_dir):
            for fn in os.listdir(portraits_dir):
                if not fn.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue
                key = os.path.splitext(fn)[0].lower()
                try:
                    self.portraits[key] = pygame.image.load(os.path.join(portraits_dir, fn)).convert_alpha()
                except Exception:
                    pass
