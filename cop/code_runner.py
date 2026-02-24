\
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class RunResult:
    ok: bool
    error: str | None = None
    lines_executed: int = 0
    used_hint: bool = False

class StepLimit(Exception):
    pass

def run_player_code(code: str, env: Dict[str, Any], *, line_limit: int = 8000) -> RunResult:
    """
    Executes player code with:
    - restricted builtins (no imports)
    - sys.settrace line counter (kills runaway loops)
    Note: This is an MVP sandbox, not a hardened security boundary.
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
        return RunResult(ok=False, error=f"{type(e).__name__}: {e}", lines_executed=counter["lines"])
    finally:
        sys.settrace(None)
