"""
Cross-working-directory regression tests.

These tests run the integration demo as a subprocess from:
- BLOON root
- BLOON_MACHINE root
- an unrelated temporary directory

They must all produce:
    Scenario A -> ACCEPT
    Scenario B -> REJECT

No PYTHONPATH manipulation is used as the fix.
"""

import os
import subprocess
import sys
import tempfile

import pytest

_BLOON_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
)

_DEMO_SCRIPT = os.path.join(_BLOON_ROOT, "examples", "run_heat_with_machine.py")


def _machine_directory():
    parent = os.path.dirname(_BLOON_ROOT)
    for name in ("BLOON_MACHINE", "bloon_machine"):
        candidate = os.path.abspath(os.path.join(parent, name))
        engine_init = os.path.join(candidate, "engine", "__init__.py")
        if os.path.isdir(candidate) and os.path.isfile(engine_init):
            return candidate
    return None


def _machine_available() -> bool:
    return _machine_directory() is not None


def _run_demo_from_cwd(cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, _DEMO_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        timeout=120,
    )


def _assert_demo_success(result: subprocess.CompletedProcess) -> None:
    stdout = result.stdout or ""
    stderr = result.stderr or ""

    assert result.returncode == 0, (
        f"Demo exited with code {result.returncode}\n"
        f"--- STDOUT ---\n{stdout}\n"
        f"--- STDERR ---\n{stderr}"
    )

    assert "Decision: ACCEPT" in stdout, (
        f"Missing ACCEPT decision.\n"
        f"--- STDOUT ---\n{stdout}\n"
        f"--- STDERR ---\n{stderr}"
    )

    assert "Decision: REJECT" in stdout, (
        f"Missing REJECT decision.\n"
        f"--- STDOUT ---\n{stdout}\n"
        f"--- STDERR ---\n{stderr}"
    )

    assert "Gate REJECTED. Simulation blocked" in stdout, (
        f"Missing expected rejection message.\n"
        f"--- STDOUT ---\n{stdout}\n"
        f"--- STDERR ---\n{stderr}"
    )

    # External rule must be loaded with the expected operator.
    assert "Loaded energy_limit operator: le" in stdout, (
        f"External rule operator not loaded as 'le'.\n"
        f"--- STDOUT ---\n{stdout}\n"
        f"--- STDERR ---\n{stderr}"
    )


@pytest.mark.skipif(not _machine_available(), reason="BLOON_MACHINE sibling not found")
class TestCrossCWDIntegration:

    def test_demo_from_bloon_root(self):
        result = _run_demo_from_cwd(_BLOON_ROOT)
        _assert_demo_success(result)

    def test_demo_from_bloon_machine_root(self):
        machine_root = _machine_directory()
        assert machine_root is not None
        result = _run_demo_from_cwd(machine_root)
        _assert_demo_success(result)

    def test_demo_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run_demo_from_cwd(tmpdir)
            _assert_demo_success(result)

    def test_engine_module_origin_reported(self):
        result = _run_demo_from_cwd(_BLOON_ROOT)
        _assert_demo_success(result)

        stdout = result.stdout
        assert "Engine resolved from:" in stdout
        assert "rule_engine from:" in stdout
        assert "bloon_machine from:" in stdout

        lowered = stdout.lower()
        assert "bloon_machine" in lowered

    def test_no_namespace_collision_from_machine_cwd(self):
        machine_root = _machine_directory()
        assert machine_root is not None

        result = _run_demo_from_cwd(machine_root)
        _assert_demo_success(result)

        engine_lines = [
            line
            for line in result.stdout.splitlines()
            if line.startswith("Engine resolved from:")
        ]

        assert len(engine_lines) == 1

        engine_path = engine_lines[0].split("Engine resolved from:", 1)[1].strip()

        assert "engine" in engine_path.lower()
        assert "__init__.py" in engine_path
        assert "bloon_machine" in engine_path.lower()
