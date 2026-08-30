# BLOON + BLOON_MACHINE Integration

## Architectural Invariant
- **BLOON** = facts + computation
- **BLOON_MACHINE** = policy + decision

Never reverse this dependency. BLOON_MACHINE does not replace BLOON's numerical engine; it acts as an external decision gate.

## Where They Interact
They interact at the task initiation boundary via the `bloon.integration.machine.evaluate_with_machine` adapter.

## The Adapter (`bloon/integration/machine.py`)
The `evaluate_with_machine` function provides a minimal, loosely coupled bridge:
- **Input**: `task` (dict), BLOON `State`, `rules_path` (str), and optional `machine_context` (dict).
- **Output**: BLOON_MACHINE `DecisionResult`.
- **Fact Extraction**: The adapter extracts ONLY generic, non-physics-specific facts from the BLOON State (e.g., `time`, `num_values`). It does **not** invent physical meaning for generic quantities (e.g., it does not assume `sum(values)` is `energy`).
- **Explicit Context**: Domain-specific facts required by policies must be explicitly supplied by the caller via the `machine_context` dictionary.
- **Ethical Bypass**: Defaults to `True` to automatically satisfy BLOON_MACHINE's ethical gate for local, trusted numerical simulations, preventing contamination of scientific workflows with irrelevant policy fields.

## Decision Semantics in BLOON Lifecycle
- **ACCEPT**: The computational request is valid. BLOON proceeds with `run_simulation`.
- **WARN**: The request is valid but violates a `SOFT` constraint. BLOON proceeds, but the warning is logged.
- **REJECT**: A `HARD` constraint is violated, or the kernel failed-closed. BLOON **blocks** the evolution.

## What is NOT Integrated (Yet)
- **Runtime Rule Generation**: The adapter reads existing YAML configurations. It does NOT manufacture policy configuration at runtime.
- **HANKER Persistence**: State serialization and long-term memory are future architectural possibilities.
- **MachineState Abstraction**: No new core abstraction was created; the existing `State` remains the source of truth for numerical validity.
- **Warning Handlers**: Formal propagation of warnings up the BLOON lifecycle is deferred.
