from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Retro-pixel UI contract (logical resolution — all drawing targets this canvas)
# ──────────────────────────────────────────────────────────────────────────────
LOGICAL_W, LOGICAL_H = 384, 216
U = 8  # base grid unit (px)

# ──────────────────────────────────────────────────────────────────────────────
# Color palette — Greatness.INC / Casa Grande Cougars
# Dark charcoal shell, gold accents, deep-green field
# ──────────────────────────────────────────────────────────────────────────────
CASA_BLUE     = (0x22, 0x24, 0x2B)   # app background (charcoal)
NAVY_MID      = (0x2B, 0x2E, 0x38)   # mid panels
NAVY_DEEP     = (0x34, 0x38, 0x44)   # panel faces
NAVY_SHADOW   = (0x18, 0x1A, 0x1F)   # deep shadow

GOLD_PRIMARY  = (0xF2, 0xC2, 0x3A)   # logo-gold
GOLD_HILITE   = (0xFF, 0xDE, 0x6E)   # bevel highlight
GOLD_SHADOW   = (0x9B, 0x78, 0x1E)   # bevel shadow
GOLD_DIM      = (0xB8, 0x91, 0x28)   # muted gold (ghost targets)

BROWN_DEEP    = (0x3A, 0x2E, 0x18)
WHITE         = (0xFA, 0xFA, 0xFC)
OFF_WHITE     = (0xE7, 0xE8, 0xED)
OUTLINE_BLACK = (0x0E, 0x0F, 0x12)
ALERT_RED     = (0xD6, 0x29, 0x36)
SUCCESS_GREEN = (0x2A, 0xC4, 0x6B)

# Field colors
FIELD_GREEN        = (0x26, 0x6E, 0x37)   # main turf
FIELD_GREEN_DARK   = (0x1E, 0x58, 0x2C)   # alternating stripe
FIELD_LINE         = (0x4A, 0xA8, 0x5C)   # yard line
FIELD_50_LINE      = (0xC8, 0xC8, 0x60)   # 50-yard center line (bright)
FIELD_HASH         = (0x3C, 0x8A, 0x4A)   # hash marks

# Section colors (used in field renderer for entity dots)
COLOR_DM        = (0xF2, 0xC2, 0x3A)   # Drum Major — gold
COLOR_PERC      = (0xD6, 0x55, 0x4A)   # Percussion — rust red
COLOR_WINDS     = (0x4A, 0xA0, 0xD8)   # Winds/Sax — steel blue
COLOR_BRASS     = (0xE8, 0xC0, 0x50)   # High Brass — bright gold
COLOR_LOW_BRASS = (0xC8, 0x82, 0x38)   # Low Brass — bronze
COLOR_WW        = (0x88, 0xCC, 0x88)   # Woodwinds — sage green
COLOR_GUARD     = (0xD8, 0x60, 0xB0)   # Color Guard — magenta
COLOR_PROP      = (0xA0, 0x88, 0xD0)   # Props — lavender
COLOR_GEN       = (0xB0, 0xB0, 0xB0)   # Generic — grey

SECTION_COLORS: dict[str, tuple[int,int,int]] = {
    "DM":    COLOR_DM,
    "PERC":  COLOR_PERC,
    "WINDS": COLOR_WINDS,
    "BRASS": COLOR_BRASS,
    "LOW":   COLOR_LOW_BRASS,
    "WW":    COLOR_WW,
    "GUARD": COLOR_GUARD,
    "PROP":  COLOR_PROP,
    "GEN":   COLOR_GEN,
}

# ──────────────────────────────────────────────────────────────────────────────
# Field coordinate system
#   x : 0–40   (left endzone → right endzone; 40 units = 100 yards)
#   y : 0–28   (front sideline → back sideline)
#
#   One unit ≈ 2.5 yards ≈ 2 marching steps (at 8-to-5 ratio)
# ──────────────────────────────────────────────────────────────────────────────
FIELD_W = 40
FIELD_H = 28

# Landmark y-positions
FRONT_SIDE  = 0
FRONT_HASH  = 8
FIELD_MID_Y = 14
BACK_HASH   = 20
BACK_SIDE   = 28

# Yard line x-positions (every 4 units = 5 yards)
# Side 1 (left of 50)
L_GOAL  = 0
L_05    = 2
L_10    = 4
L_15    = 6
L_20    = 8
L_25    = 10
L_30    = 12
L_35    = 14
L_40    = 16
L_45    = 18
YD_50   = 20   # center 50-yard line
R_45    = 22
R_40    = 24
R_35    = 26
R_30    = 28
R_25    = 30
R_20    = 32
R_15    = 34
R_10    = 36
R_05    = 38
R_GOAL  = 40

# Yard line display labels (every 4 units = visible 5-yard marks)
YARD_LINE_LABELS: list[tuple[int, str]] = [
    (4,  "10"), (8,  "20"), (12, "30"), (16, "40"),
    (20, "50"),
    (24, "40"), (28, "30"), (32, "20"), (36, "10"),
]

FPS = 60