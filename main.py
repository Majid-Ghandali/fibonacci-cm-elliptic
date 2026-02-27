"""
main.py
=======
Entry point for the Fibonacci CM computation pipeline.

Mathematical scope
------------------
Numerical verification of the identity

    S_p = -a_p(E),   E : y^2 = x^3 - 4x

for all primes p inert in Q(sqrt(5)), up to a user-specified bound.
The CM property of E forces a_p = 0 for inert primes, making S_p = 0 exactly.

Usage
-----
    python main.py

Prompts for:
    - Execution mode  (1=Resume, 2=Restart, 3=Plot)
    - Upper prime bound (default: 100,000)

All outputs are written to  CM_Research_Outputs/
"""

import sys
from pathlib import Path

from fibonacci_cm import pipeline, reporting, figures

OUTPUT_DIR = Path("CM_Research_Outputs")
XLSX_PATH  = OUTPUT_DIR / "CM_Statistical_Report.xlsx"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("  FIBONACCI CM ANALYSIS SUITE  —  Research Edition v1.0")
    print("  Identity: S_p = -a_p(E),  E: y^2 = x^3 - 4x")
    print("=" * 65)

    # ── Mode selection ────────────────────────────────────────────────────────
    print("\n[Mode] Choose execution strategy:")
    print("  (1) RESUME  : Continue from the last saved checkpoint.")
    print("  (2) RESTART : Clear existing data and recompute from scratch.")
    print("  (3) PLOT    : Regenerate figures from existing dataset only.")

    try:
        choice   = input("\nEnter choice [1/2/3] (default: 1): ").strip() or "1"
        mode_map = {"1": "resume", "2": "restart", "3": "plot"}
        mode     = mode_map.get(choice, "resume")
    except (EOFError, KeyboardInterrupt):
        print("\n[System] Execution interrupted. Exiting.")
        sys.exit(0)

    # ── Prime range ───────────────────────────────────────────────────────────
    max_p = 100_000
    if mode != "plot":
        try:
            raw = input(f"Upper bound for primes (default: {max_p:,}): ").strip()
            if raw:
                max_p = int(raw)
                if max_p < 2:
                    print("[Warning] Prime range must be >= 2. Using default.")
                    max_p = 100_000
        except ValueError:
            print(f"[Warning] Invalid input. Using default: {max_p:,}")
        except (EOFError, KeyboardInterrupt):
            pass
    else:
        max_p = 0   # unused in plot-only mode

    # ── Run pipeline ──────────────────────────────────────────────────────────
    print(f"\n[Pipeline] Starting in {mode.upper()} mode ...")
    try:
        df = pipeline.run(output_dir=str(OUTPUT_DIR), max_p=max_p, mode=mode)
    except Exception as exc:
        print(f"\n[Critical] Pipeline failed: {exc}")
        sys.exit(1)

    if df is None or df.empty:
        print("[Error] Dataset is empty — nothing to report.")
        return

    # ── Reports and figures ───────────────────────────────────────────────────
    reporting.print_summary(df)
    reporting.save_excel(df, str(XLSX_PATH))
    figures.generate_all(df, str(OUTPUT_DIR))

    print("\n" + "=" * 65)
    print(f"  SUCCESS: All outputs saved to {OUTPUT_DIR}/")
    print("=" * 65)


if __name__ == "__main__":
    main()
