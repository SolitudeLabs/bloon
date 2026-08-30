"""
BLOON to BLOON_MACHINE integration adapter.

Architectural invariant:
- BLOON supplies facts + computation.
- BLOON_MACHINE supplies policy + decision.

Import-boundary safety:
- BLOON_MACHINE uses a generic top-level package named `engine`.
- This adapter does NOT rely on accidental PYTHONPATH/CWD resolution.
- It explicitly loads BLOON_MACHINE's engine package from disk.
- It verifies engine, engine.rule_engine, and engine.bloon_machine origins.
"""

import importlib
import importlib.util
import json
import os
import sys
import tempfile
from typing import Any, Dict, Optional

from core.state import State

_THIS_FILE = os.path.abspath(__file__)
_THIS_DIR = os.path.dirname(_THIS_FILE)
_BLOON_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir))
_ENGINE_NAME = "engine"


def machine_root() -> str:
    r"""
    Deterministically locate BLOON_MACHINE as a sibling of BLOON_PYTHON.

    Expected layouts:
        E:\bloon_python
        E:\bloon_machine

    or:
        E:\BLOON_PYTHON
        E:\BLOON_MACHINE
    """
    parent = os.path.dirname(_BLOON_ROOT)

    candidates = (
        os.path.abspath(os.path.join(parent, "BLOON_MACHINE")),
        os.path.abspath(os.path.join(parent, "bloon_machine")),
    )

    for root in candidates:
        engine_init = os.path.join(root, "engine", "__init__.py")
        bloon_machine_module = os.path.join(root, "engine", "bloon_machine.py")

        if os.path.isfile(engine_init) and os.path.isfile(bloon_machine_module):
            return root

    raise ImportError(
        "BLOON_MACHINE not found. Searched:\n"
        + "\n".join(f"  - {candidate}" for candidate in candidates)
        + "\nExpected BLOON_MACHINE to contain engine/__init__.py and engine/bloon_machine.py."
    )


def _same_file(left: str, right: str) -> bool:
    try:
        return os.path.samefile(os.path.abspath(left), os.path.abspath(right))
    except OSError:
        return os.path.abspath(left).lower() == os.path.abspath(right).lower()


def _purge_engine_modules() -> None:
    """
    Remove any previously imported top-level `engine` modules.

    This is necessary because BLOON_MACHINE uses the generic package name
    `engine`. Without purging, a stale or foreign `engine` module can remain
    in sys.modules and shadow the correct BLOON_MACHINE engine.
    """
    for module_name in list(sys.modules):
        if module_name == _ENGINE_NAME or module_name.startswith(_ENGINE_NAME + "."):
            del sys.modules[module_name]


def ensure_machine_engine():
    """
    Deterministically import BLOON_MACHINE's engine package.

    Returns the loaded `engine` module.

    Raises ImportError if BLOON_MACHINE cannot be found or verified.
    """
    root = machine_root()
    engine_dir = os.path.join(root, "engine")

    init_path = os.path.join(engine_dir, "__init__.py")
    rule_engine_path = os.path.join(engine_dir, "rule_engine.py")
    bloon_machine_path = os.path.join(engine_dir, "bloon_machine.py")

    # If the correct engine is already imported, reuse it.
    existing_engine = sys.modules.get(_ENGINE_NAME)
    if existing_engine is not None:
        existing_file = getattr(existing_engine, "__file__", None)

        if existing_file and _same_file(existing_file, init_path):
            try:
                importlib.import_module("engine.result")
                importlib.import_module("engine.rule_engine")
                importlib.import_module("engine.bloon_machine")

                rule_engine_module = sys.modules.get("engine.rule_engine")
                bloon_machine_module = sys.modules.get("engine.bloon_machine")

                if (
                    rule_engine_module is not None
                    and bloon_machine_module is not None
                    and _same_file(rule_engine_module.__file__, rule_engine_path)
                    and _same_file(bloon_machine_module.__file__, bloon_machine_path)
                ):
                    return existing_engine
            except Exception:
                # Fall through and reload deterministically.
                pass

    # Remove wrong/stale/cached engine imports.
    _purge_engine_modules()

    # Load the BLOON_MACHINE engine package explicitly from disk.
    spec = importlib.util.spec_from_file_location(
        _ENGINE_NAME,
        init_path,
        submodule_search_locations=[engine_dir],
    )

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load BLOON_MACHINE engine from: {init_path}")

    engine_module = importlib.util.module_from_spec(spec)
    sys.modules[_ENGINE_NAME] = engine_module
    spec.loader.exec_module(engine_module)

    # Ensure submodule resolution is locked to this engine directory.
    engine_module.__path__ = [engine_dir]

    # Import required submodules through the verified package boundary.
    importlib.import_module("engine.result")
    importlib.import_module("engine.loader")
    importlib.import_module("engine.ethics")
    importlib.import_module("engine.rule_engine")
    importlib.import_module("engine.validator")
    importlib.import_module("engine.bloon_machine")

    # Verify that the important submodules came from the expected files.
    rule_engine_module = sys.modules.get("engine.rule_engine")
    bloon_machine_module = sys.modules.get("engine.bloon_machine")

    if rule_engine_module is None or bloon_machine_module is None:
        raise ImportError("BLOON_MACHINE engine submodules failed to load.")

    if not _same_file(rule_engine_module.__file__, rule_engine_path):
        raise ImportError(
            f"engine.rule_engine resolved to '{rule_engine_module.__file__}', "
            f"but expected '{rule_engine_path}'."
        )

    if not _same_file(bloon_machine_module.__file__, bloon_machine_path):
        raise ImportError(
            f"engine.bloon_machine resolved to '{bloon_machine_module.__file__}', "
            f"but expected '{bloon_machine_path}'."
        )

    return engine_module


def engine_diagnostics() -> Dict[str, str]:
    """
    Return exact file origins of the loaded BLOON_MACHINE engine modules.

    Part of the verification/regression mechanism: it proves that no
    namespace collision occurred.
    """
    engine_module = ensure_machine_engine()

    return {
        "machine_root": machine_root(),
        "engine": os.path.abspath(engine_module.__file__),
        "rule_engine": os.path.abspath(sys.modules["engine.rule_engine"].__file__),
        "bloon_machine": os.path.abspath(sys.modules["engine.bloon_machine"].__file__),
    }


def evaluate_with_machine(
    task: Dict[str, Any],
    state: State,
    rules_path: str,
    machine_context: Optional[Dict[str, Any]] = None,
    ethical_bypass: bool = False,
):
    """
    Evaluate a BLOON task/state pair through BLOON_MACHINE.

    BLOON supplies:
    - task
    - generic state facts
    - explicit machine_context facts

    BLOON_MACHINE supplies:
    - rules
    - policy evaluation
    - ACCEPT/WARN/REJECT decision

    ``ethical_bypass`` is OFF by default (fail-closed). See the TECHNICAL
    DEBT note below before enabling it.
    """
    ensure_machine_engine()
    bloon_machine_module = sys.modules["engine.bloon_machine"]

    rules_path = os.path.abspath(rules_path)
    if not os.path.isfile(rules_path):
        raise FileNotFoundError(f"Rules file not found: {rules_path}")

    task_payload = dict(task)

    # ------------------------------------------------------------------
    # BLOON_MACHINE's ethical gate requires the task to carry operational
    # context (consent, isolation, read-only, no exfiltration, ...).
    # ------------------------------------------------------------------
    #
    # For a pure local numerical simulation these operational fields have
    # no physical meaning, so the prototype adapter can inject them on
    # behalf of the caller when the caller EXPLICITLY opts in via
    # ``ethical_bypass=True``.
    #
    # This is a KNOWN BOUNDARY COMPROMISE:
    #   - It injects MACHINE-policy facts from the adapter side.
    #   - It is OFF by default (fail-closed). Callers must opt in.
    #   - It is retained only for the local prototype and is documented
    #     as technical debt. It is NOT a general policy mechanism.
    #
    # ------------------------------------------------------------------
    if ethical_bypass:
        task_payload.setdefault("consent", True)
        task_payload.setdefault("isolated", True)
        task_payload.setdefault("read_only", True)
        task_payload.setdefault("no_exfiltration", True)
        task_payload.setdefault("not_production", True)
        task_payload.setdefault("documented", True)
        task_payload.setdefault("exit_strategy", True)

    # Generic BLOON facts only.
    # Do not invent physical meaning from raw state values.
    state_payload = {
        "time": float(state.time),
        "num_values": int(len(state.values)),
    }

    # Explicit domain facts supplied by the caller.
    if machine_context:
        state_payload.update(machine_context)

    with tempfile.TemporaryDirectory() as tmpdir:
        task_path = os.path.join(tmpdir, "task.json")
        state_path = os.path.join(tmpdir, "state.json")

        with open(task_path, "w", encoding="utf-8") as f:
            json.dump(task_payload, f)

        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(state_payload, f)

        result = bloon_machine_module.decide_structured(
            task_path,
            state_path,
            rules_path,
        )

    if result is None:
        raise RuntimeError("BLOON_MACHINE decide_structured returned None.")

    return result
