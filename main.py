main.py
=======
Entry point for the Fibonacci CM computation pipeline.

Usage
-----
    python main.py

The script prompts for:
    - Execution mode  (1=Resume, 2=Restart, 3=Plot)
    - Upper bound on prime range

All outputs are written to  CM_Research_Outputs/
"""

import os
from fibonacci_cm import pipeline, reporting, figures

OUTPUT_DIR = "CM_Research_Outputs"
XLSX_PATH  = os.path.join(OUTPUT_DIR, "CM_Statistical_Report.xlsx")


def main() -> None:
    print("=" * 60)
    print("  FIBONACCI CM ANALYSIS  —  Journal Edition v1.0")
    print("  Identity verified: S_p = -a_p(E),  E: y^2 = x^3 - 4x")
    print("=" * 60)

    # ── Mode selection ────────────────────────────────────────────────────────
    print("\n[Mode] Choose execution mode:")
    print("  (1) RESUME  : Continue from the last saved prime.")
    print("  (2) RESTART : Clear existing data and start fresh.")
    print("  (3) PLOT    : Regenerate figures from existing dataset.")

    try:
        mode = input("\nEnter choice [1/2/3] (default: 1): ").strip() or "1"
    except EOFError:
        mode = "1"

    # ── Prime range ───────────────────────────────────────────────────────────
    if mode != "3":
        try:
            raw   = input("Upper bound for primes (default: 100000): ").strip()
            max_p = int(raw) if raw else 100_000
        except ValueError:
            max_p = 100_000
    else:
        max_p = 0   # unused in plot-only mode

    # ── Run pipeline ──────────────────────────────────────────────────────────
    df = pipeline.run(output_dir=OUTPUT_DIR, max_p=max_p, mode=mode)

    if df.empty:
        print("[Error] Dataset is empty — nothing to report.")
        return

    # ── Reports ───────────────────────────────────────────────────────────────
    reporting.print_summary(df)
    reporting.save_excel(df, XLSX_PATH)

    # ── Figures ───────────────────────────────────────────────────────────────
    figures.generate_all(df, OUTPUT_DIR)

    print("\n" + "=" * 60)
    print(f"  ALL OUTPUTS SAVED TO: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
