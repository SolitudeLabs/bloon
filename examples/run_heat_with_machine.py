"""
Integration demo: 1D heat transport gated by BLOON_MACHINE.

This demo is deterministic with respect to:
- BLOON source location
- BLOON_MACHINE sibling location
- rules file location
- current working directory

It prints:
- exact engine module origins
- exact rules file path
- exact loaded rule operator
"""

import functools
import os
import sys

# Force immediate output flushing. This avoids empty captured stdout in tests.
print = functools.partial(print, flush=True)

_THIS_FILE = os.path.abspath(__file__)
_THIS_DIR = os.path.dirname(_THIS_FILE)
_BLOON_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir))

if _BLOON_ROOT not in sys.path:
    sys.path.insert(0, _BLOON_ROOT)

import numpy as np

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


def _read_energy_limit_operator(rules_path: str) -> str:
    """
    Read the operator for rule id 'energy_limit' from the YAML rules file.
    """
    import yaml

    with open(rules_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    for rule in data.get("hard_constraints", []):
        if rule.get("id") == "energy_limit":
            return str(rule.get("operator", ""))

    return ""


def main() -> int:
    print("=== Integration Demo: 1D Heat Transport + BLOON_MACHINE ===")

    try:
        from integration.machine import (
            evaluate_with_machine,
            engine_diagnostics,
        )
    except Exception as exc:
        print(f"ERROR: failed to import integration adapter: {exc}")
        return 1

    try:
        diagnostics = engine_diagnostics()
    except Exception as exc:
        print(f"ERROR: failed to load BLOON_MACHINE engine: {exc}")
        return 1

    print(f"Machine root:       {diagnostics['machine_root']}")
    print(f"Engine resolved from: {diagnostics['engine']}")
    print(f"rule_engine from:     {diagnostics['rule_engine']}")
    print(f"bloon_machine from:   {diagnostics['bloon_machine']}")

    rules_path = os.path.join(_THIS_DIR, "machine_rules", "heat_constraints.yaml")
    print(f"Rules file:           {rules_path}")

    if not os.path.isfile(rules_path):
        print("ERROR: rules file not found.")
        return 1

    try:
        loaded_operator = _read_energy_limit_operator(rules_path)
    except Exception as exc:
        print(f"ERROR: cannot parse rules file: {exc}")
        return 1

    print(f"Loaded energy_limit operator: {loaded_operator}")

    if loaded_operator != "le":
        print(
            "FATAL: demo policy expects operator 'le'. "
            "The rules file has diverged from the expected integration policy."
        )
        return 1

    # ------------------------------------------------------------------
    # BLOON computational setup: facts + computation
    # ------------------------------------------------------------------
    topo = Topology1D(num_nodes=51, x_min=0.0, x_max=1.0)
    physics = HeatPhysics(topology=topo, alpha=1.0)

    u0 = np.sin(np.pi * topo.nodes)
    init_state = State(values=u0, time=0.0)

    integrator = BackwardEulerIntegrator()
    admissibility = AdmissibilityLayer([PositivityConstraint()])
    observables = ObservableManager({})

    # ------------------------------------------------------------------
    # Scenario A: valid request -> ACCEPT
    # ------------------------------------------------------------------
    print()
    print("--- SCENARIO A: Valid Request (ACCEPT) ---")

    task_valid = {
        "goal": "heat_transport_simulation",
        "energy_required": 5.0,
    }

    machine_context_valid = {
        "energy": 10.0,
    }

    result_a = evaluate_with_machine(
        task=task_valid,
        state=init_state,
        rules_path=rules_path,
        machine_context=machine_context_valid,
        ethical_bypass=True,
    )

    decision_a = result_a.decision.value
    print(f"Decision: {decision_a}")

    if decision_a != "ACCEPT":
        print("UNEXPECTED: valid request was not accepted.")
        for violation in result_a.violations:
            severity = getattr(getattr(violation, "severity", None), "value", "")
            print(f"  - {violation.rule_id} ({severity}): {violation.reason}")
        return 1

    print("Gate passed. Proceeding with BLOON simulation...")

    simulation_result = run_simulation(
        initial_state=init_state,
        topology=topo,
        residual_op=physics,
        storage_op=physics,
        jacobian_op=physics,
        integrator=integrator,
        admissibility=admissibility,
        observables=observables,
        dt=0.01,
        num_steps=5,
    )

    print(f"Simulation completed. Final time: {simulation_result.time_history[-1]:.4f}")
    print(
        "Admissibility: "
        f"{'PASS' if simulation_result.admissibility_reports[-1].passed else 'FAIL'}"
    )

    # ------------------------------------------------------------------
    # Scenario B: invalid request -> REJECT
    # ------------------------------------------------------------------
    print()
    print("--- SCENARIO B: Invalid Request (REJECT) ---")

    task_invalid = {
        "goal": "heat_transport_simulation",
        "energy_required": 50.0,
    }

    machine_context_invalid = {
        "energy": 10.0,
    }

    result_b = evaluate_with_machine(
        task=task_invalid,
        state=init_state,
        rules_path=rules_path,
        machine_context=machine_context_invalid,
        ethical_bypass=True,
    )

    decision_b = result_b.decision.value
    print(f"Decision: {decision_b}")

    if decision_b != "REJECT":
        print("UNEXPECTED: invalid request was not rejected.")
        return 1

    print("Gate REJECTED. Simulation blocked (Fail-Closed behavior).")
    for violation in result_b.violations:
        severity = getattr(getattr(violation, "severity", None), "value", "")
        print(f"  - {violation.rule_id} ({severity}): {violation.reason}")

    print()
    print("=== Integration Demo Completed ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
