from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RunResult:
    ok: bool
    error: str | None = None
    lines_executed: int = 0
    used_hint: bool = False
    error_line: int | None = None


class StepLimit(Exception):
    pass


def _friendly_error(err: BaseException) -> str:
    name = type(err).__name__
    msg = str(err)
    if name == "SyntaxError":
        return f"SyntaxError: {msg}"
    if name == "NameError":
        return f"NameError: {msg}. Tip: define the variable before using it."
    if name == "TypeError":
        return f"TypeError: {msg}. Tip: check function arguments and value types."
    return f"{name}: {msg}"


def _extract_error_line(err: BaseException) -> int | None:
    if isinstance(err, SyntaxError):
        return err.lineno
    tb = err.__traceback__
    frames = traceback.extract_tb(tb)
    for frame in reversed(frames):
        if frame.filename == "<string>":
            return frame.lineno
    return None


def run_player_code(code: str, env: Dict[str, Any], *, line_limit: int = 8000) -> RunResult:
    """
    Executes player code with:
    - restricted builtins (no imports)
    - sys.settrace line counter (kills runaway loops)
    """
    counter = {"lines": 0}

    def tracer(frame, event, arg):
        if event == "line":
            counter["lines"] += 1
            if counter["lines"] > line_limit:
                raise StepLimit("Your rehearsal ran too long (possible infinite loop).")
        return tracer

    safe_builtins = {
        "range": range,
        "len": len,
        "min": min,
        "max": max,
        "abs": abs,
        "int": int,
        "float": float,
        "str": str,
        "print": print,
        "list": list,
        "dict": dict,
        "sum": sum,
        "enumerate": enumerate,
    }

    globals_dict = {"__builtins__": safe_builtins}
    locals_dict = dict(env)

    try:
        sys.settrace(tracer)
        exec(code, globals_dict, locals_dict)
        return RunResult(ok=True, lines_executed=counter["lines"])
    except StepLimit as e:
        return RunResult(ok=False, error=str(e), lines_executed=counter["lines"])
    except Exception as e:
        return RunResult(
            ok=False,
            error=_friendly_error(e),
            lines_executed=counter["lines"],
            error_line=_extract_error_line(e),
        )
    finally:
        sys.settrace(None)
