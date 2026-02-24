# Project Review: Code of Pride (MVP)

## Overall assessment
The project is a strong MVP foundation with a clear architecture for:
- scene-driven gameplay flow,
- deterministic band simulation,
- constrained code execution,
- and data-driven level content.

The codebase is readable and modular for its size.

## What is working well
- **Clean module boundaries** (`scenes`, `ui`, `band`, `code_runner`, `levels`, `save`, `assets`).
- **Data-first levels** via `data/levels.json` keeps gameplay iteration low-friction.
- **Safety-minded execution loop** using restricted builtins + line-trace guard in `run_player_code`.
- **Pixel-first rendering discipline** with integer scaling/letterboxing support.

## Key issues found
1. **Scene click guard robustness**
   - Several scenes check `if self.playing:` in click handlers but did not define `playing` locally.
   - This can produce runtime errors when those handlers receive click events.
   - Fixed by defining a safe default `self.playing = False` in the base `Scene` class.

2. **Hover state used window coordinates in scaled mode**
   - Some scenes used `pygame.mouse.get_pos()` directly for button hover checks.
   - That mismatches logical-space UI hit boxes when letterboxed/scaled.
   - Fixed by consistently using `game.mouse_logical` for hover checks.

## Recommendations (next steps)
- Add automated tests for scene input/coordinate mapping and run-loop state transitions.
- Add type checking (`mypy`/`pyright`) and linting (`ruff`) in CI.
- Expand sandbox hardening notes if this is ever used beyond a local prototype.
- Consider adding one snapshot/UI smoke test for each major scene.
