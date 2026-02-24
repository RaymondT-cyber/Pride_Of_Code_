Code of Pride (MVP Prototype) — Python/Pygame

This is a playable MVP prototype that implements the core Code of Pride loop:
edit → run → watch → debug → improve, with a Retro Bowl–style pixel dashboard.

Run
---
1) Install Python 3.10+
2) Install pygame:
   pip install pygame
3) Start:
   python main.py

Controls
--------
- Mouse: click buttons
- Keyboard: type in the editor
- Enter: new line
- Tab: inserts 4 spaces
- Ctrl+R: Run
- Ctrl+E: Reset
- Ctrl+H: Hint
- Esc: Back

Where to add levels
-------------------
Edit data/levels.json. Add more levels under the "levels" array:
- start_entities (positions)
- objective (targets / constraints)
- mentor dialogue + hint
