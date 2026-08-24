#!/usr/bin/env bash
set -e # Exit immediately if a command exits with a non-zero status.

echo "=========================================="
echo " BLOON CI/CD: Automated Acceptance Tests"
echo "=========================================="

echo "[1/3] Running Unit Tests (PyTest)..."
pytest -q tests/

echo "[2/3] Running Legacy Examples (Cartesian)..."
python run_examples.py

echo "[3/3] Running Manifold Examples (S^2 Topology)..."
python -m bloon.examples.run_topology
python -m bloon.examples.run_manifold_diffusion
# Note: visualize_manifold.py is skipped in automated CI because it spawns a blocking GUI window

echo "=========================================="
echo " ALL TESTS PASSED. READY FOR COMMIT."
echo "=========================================="