"""
Minimal harness runner: executes the full evaluation sequence in a single command.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, script_path: Path, env: dict[str, str] | None = None) -> None:
    print("\n" + "=" * 80)
    print(f"STEP: {name}")
    print("=" * 80)
    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(ROOT),
            env=env or os.environ.copy(),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] Step failed: {name}")
        raise SystemExit(exc.returncode) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the guardrail harness sequence in one command."
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use EVAL_LIMIT=100 for Eval.py (quick pass).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override EVAL_LIMIT for Eval.py (e.g., 20, 100, 500).",
    )
    parser.add_argument("--skip-verify", action="store_true", help="Skip OWASP verification.")
    parser.add_argument("--skip-clean", action="store_true", help="Skip clean benign eval.")
    parser.add_argument("--skip-pentest", action="store_true", help="Skip adversarial pentest.")
    parser.add_argument("--skip-eval", action="store_true", help="Skip main Eval.py run.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    eval_limit = args.limit
    if args.quick and eval_limit is None:
        eval_limit = 100

    steps: list[tuple[str, Path, dict[str, str] | None]] = []
    if not args.skip_verify:
        steps.append(
            ("Verify OWASP integration", ROOT / "scripts" / "testing" / "Verify_OWASP_Integration.py", None)
        )
    if not args.skip_clean:
        steps.append(
            ("Eval clean benign corpus", ROOT / "scripts" / "evaluation" / "Eval_Clean_Benign_Corpus.py", None)
        )
    if not args.skip_pentest:
        steps.append(
            ("Eval adversarial pentest", ROOT / "scripts" / "evaluation" / "Eval_Adversarial_Pentest.py", None)
        )
    if not args.skip_eval:
        env = os.environ.copy()
        if eval_limit is not None:
            env["EVAL_LIMIT"] = str(eval_limit)
        steps.append(("Eval benchmark suite", ROOT / "scripts" / "evaluation" / "Eval.py", env))

    if not steps:
        print("[WARN] No steps to run. Remove a --skip-* flag.")
        return

    print(f"[INFO] Project root: {ROOT}")
    if eval_limit is not None:
        print(f"[INFO] Eval limit: {eval_limit}")

    for name, path, env in steps:
        run_step(name, path, env)

    print("\n" + "=" * 80)
    print("[OK] Harness sequence complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
