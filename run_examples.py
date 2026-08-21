from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run_command(label: str, command: list[str]) -> None:
    print()
    print("=" * 70)
    print(f"  {label}")
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=ROOT,
    )

    if result.returncode != 0:
        raise SystemExit(
            f"\n[FAILED] {label} (exit code {result.returncode})"
        )


def run_examples() -> None:
    examples = [
        ("Heat Transport", [sys.executable, "-m", "examples.run_heat"]),
        ("Reaction-Diffusion", [sys.executable, "-m", "examples.run_reaction"]),
        ("Structural Dynamics", [sys.executable, "-m", "examples.run_structural"]),
    ]

    for label, command in examples:
        run_command(label, command)

    run_command(
        "Pytest Verification Suite",
        [sys.executable, "-m", "pytest", "-q"],
    )

    print()
    print("=" * 70)
    print("  BLOON EXAMPLE + VERIFICATION SUITE: PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_examples()