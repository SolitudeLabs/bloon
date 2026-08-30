"""
Integration tests for BLOON + BLOON_MACHINE adapter.
These tests do not depend on accidental PYTHONPATH resolution.
They use the adapter's deterministic engine loader.
"""
import os
import tempfile

import numpy as np
import pytest


def _skip_if_machine_missing() -> bool:
    try:
        from integration.machine import ensure_machine_engine
        ensure_machine_engine()
        return False
    except Exception:
        return True


def _decision_enum():
    from integration.machine import ensure_machine_engine
    ensure_machine_engine()
    import engine.result as result_module
    return result_module.Decision


RULE_LE = """hard_constraints:
  - id: energy_check
    type: threshold
    severity: HARD
    task_field: energy_required
    state_field: energy
    operator: le
"""

RULE_GE = """hard_constraints:
  - id: energy_check
    type: threshold
    severity: HARD
    task_field: energy_required
    state_field: energy
    operator: ge
"""


def test_bloon_works_without_machine():
    """
    Prove BLOON core works without invoking BLOON_MACHINE.
    """
    from core import (
        State,
        Topology1D,
        PositivityConstraint,
        AdmissibilityLayer,
        ObservableManager,
        run_simulation,
    )
    from physics.heat import HeatPhysics
    from evolution.backward_euler import BackwardEulerIntegrator

    topo = Topology1D(num_nodes=11, x_min=0.0, x_max=1.0)
    physics = HeatPhysics(topology=topo, alpha=1.0)
    u0 = np.sin(np.pi * topo.nodes)
    init_state = State(values=u0, time=0.0)

    integrator = BackwardEulerIntegrator()
    admissibility = AdmissibilityLayer([PositivityConstraint()])
    observables = ObservableManager({})

    result = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=integrator,
        admissibility=admissibility,
        observables=observables,
        dt=0.01,
        num_steps=2,
    )

    assert len(result.time_history) == 3
    assert result.admissibility_reports[-1].passed is True


@pytest.mark.skipif(_skip_if_machine_missing(), reason="BLOON_MACHINE not available")
def test_rule_change_changes_decision_without_bloon_modification():
    """
    Prove that changing only the YAML rule changes the decision,
    while BLOON source code and adapter remain untouched.
    """
    from integration.machine import evaluate_with_machine
    from core import State

    Decision = _decision_enum()

    state = State(values=np.array([1.0, 2.0, 3.0]), time=0.0)
    task = {"goal": "test", "energy_required": 15.0}
    machine_context = {"energy": 10.0}

    with tempfile.TemporaryDirectory() as tmpdir:
        rules_le = os.path.join(tmpdir, "rules_le.yaml")
        with open(rules_le, "w", encoding="utf-8") as f:
            f.write(RULE_LE)

        result_le = evaluate_with_machine(
            task=task,
            state=state,
            rules_path=rules_le,
            machine_context=machine_context,
            ethical_bypass=True,
        )
        assert result_le.decision == Decision.REJECT

        rules_ge = os.path.join(tmpdir, "rules_ge.yaml")
        with open(rules_ge, "w", encoding="utf-8") as f:
            f.write(RULE_GE)

        result_ge = evaluate_with_machine(
            task=task,
            state=state,
            rules_path=rules_ge,
            machine_context=machine_context,
            ethical_bypass=True,
        )
        assert result_ge.decision == Decision.ACCEPT


@pytest.mark.skipif(_skip_if_machine_missing(), reason="BLOON_MACHINE not available")
def test_accept_path():
    from integration.machine import evaluate_with_machine
    from core import State

    Decision = _decision_enum()

    with tempfile.TemporaryDirectory() as tmpdir:
        rules_path = os.path.join(tmpdir, "rules.yaml")
        with open(rules_path, "w", encoding="utf-8") as f:
            f.write(RULE_LE)

        state = State(values=np.array([1.0, 2.0, 3.0]), time=0.0)
        task = {"goal": "test", "energy_required": 5.0}
        machine_context = {"energy": 10.0}

        result = evaluate_with_machine(
            task=task,
            state=state,
            rules_path=rules_path,
            machine_context=machine_context,
            ethical_bypass=True,
        )

        assert result.decision == Decision.ACCEPT
        assert result.to_dict()["result"] == "VALID"


@pytest.mark.skipif(_skip_if_machine_missing(), reason="BLOON_MACHINE not available")
def test_reject_path():
    from integration.machine import evaluate_with_machine
    from core import State

    Decision = _decision_enum()

    with tempfile.TemporaryDirectory() as tmpdir:
        rules_path = os.path.join(tmpdir, "rules.yaml")
        with open(rules_path, "w", encoding="utf-8") as f:
            f.write(RULE_LE)

        state = State(values=np.array([1.0, 2.0, 3.0]), time=0.0)
        task = {"goal": "test", "energy_required": 50.0}
        machine_context = {"energy": 10.0}

        result = evaluate_with_machine(
            task=task,
            state=state,
            rules_path=rules_path,
            machine_context=machine_context,
            ethical_bypass=True,
        )

        assert result.decision == Decision.REJECT
        assert result.to_dict()["result"] == "INVALID"
        assert len(result.violations) == 1
        assert result.violations[0].rule_id == "energy_check"


@pytest.mark.skipif(_skip_if_machine_missing(), reason="BLOON_MACHINE not available")
def test_engine_diagnostics_point_to_bloon_machine():
    from integration.machine import engine_diagnostics

    diagnostics = engine_diagnostics()

    assert diagnostics["engine"].endswith(os.path.join("engine", "__init__.py"))
    assert diagnostics["rule_engine"].endswith(os.path.join("engine", "rule_engine.py"))
    assert diagnostics["bloon_machine"].endswith(os.path.join("engine", "bloon_machine.py"))

    lowered_root = diagnostics["machine_root"].lower()
    assert "bloon_machine" in lowered_root


@pytest.mark.skipif(_skip_if_machine_missing(), reason="BLOON_MACHINE not available")
def test_ethical_gate_fail_closed_when_bypass_disabled():
    """
    With ethical_bypass disabled (the default) and no ethical context in
    the task, BLOON_MACHINE's ethical gate must reject (fail-closed).
    """
    from integration.machine import evaluate_with_machine
    from core import State

    Decision = _decision_enum()

    with tempfile.TemporaryDirectory() as tmpdir:
        rules_path = os.path.join(tmpdir, "rules.yaml")
        with open(rules_path, "w", encoding="utf-8") as f:
            f.write(RULE_LE)

        state = State(values=np.array([1.0, 2.0, 3.0]), time=0.0)
        task = {"goal": "test", "energy_required": 5.0}
        machine_context = {"energy": 10.0}

        result = evaluate_with_machine(
            task=task,
            state=state,
            rules_path=rules_path,
            machine_context=machine_context,
            ethical_bypass=False,
        )

        assert result.decision == Decision.REJECT
        assert any(v.rule_id == "ethical_condom" for v in result.violations)
