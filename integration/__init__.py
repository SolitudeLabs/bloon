"""
BLOON Integration Layer.

Provides adapters and bridges to external systems (e.g., BLOON_MACHINE)
without contaminating the core numerical architecture.

Architectural Invariant:
- BLOON = facts + computation
- BLOON_MACHINE = policy + decision
"""
