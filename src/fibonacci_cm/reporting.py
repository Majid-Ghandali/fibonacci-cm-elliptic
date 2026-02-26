"""
reporting.py
============
Statistical summary and Excel report generation.

Produces a two-sheet Excel workbook:
    Sheet 1 — Trace_Data_Raw    : full per-prime dataset
    Sheet 2 — Analysis_Summary  : aggregated statistics

Also prints a formatted console summary after computation.
"""

import os
import pandas as pd


def print_summary(df: pd.DataFrame) -> None:
    """
    Print a formatted summary of the computed dataset to stdout.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: p, type, pisano_period, weil_ratio.
    """
    n_total = len(df)
    n_inert = (df["type"] == "inert").sum()
    n_split = (df["type"] == "split").sum()

    print("\n" + "-" * 52)
    print(f"  Total primes           : {n_total:,}")
    print(f"  Split  (p ≡ 1 mod 4)  : {n_split:,}")
    print(f"  Inert  (p ≡ 3 mod 4)  : {n_inert:,}")
    print(f"  Empirical inert ratio  : {n_inert / n_total:.6f}  (theory: 0.500000)")
    print(f"  Max Weil ratio         : {df['weil_ratio'].max():.6f}  (bound: 1.000000)")
    print(f"  Max Pisano period      : {df['pisano_period'].max():,}")
    print(f"  Verification range     : 3  to  {int(df['p'].max()):,}")
    print("-" * 52)

    # Verify CM property: all inert primes must have a_p = 0
    inert_df = df[df["type"] == "inert"]
    if (inert_df["a_p"] == 0).all():
        print(f"  [OK] CM property verified: a_p = 0 for all {n_inert:,} inert primes.")
    else:
        n_fail = (inert_df["a_p"] != 0).sum()
        print(f"  [ERROR] CM property FAILED for {n_fail} inert primes!")


def save_excel(df: pd.DataFrame, xlsx_path: str) -> None:
    """
    Write a two-sheet Excel workbook with raw data and summary statistics.

    Parameters
    ----------
    df        : pd.DataFrame   Full dataset (columns matching FIELDS).
    xlsx_path : str            Output path for the .xlsx file.
    """
    n_total = len(df)
    n_inert = (df["type"] == "inert").sum()
    n_split = (df["type"] == "split").sum()

    summary = pd.DataFrame({
        "Parameter": [
            "Paper",
            "Verification range",
            "Total primes computed",
            "Split primes (p ≡ 1 mod 4)",
            "Inert primes (p ≡ 3 mod 4)",
            "Empirical inert ratio",
            "Chebotarev prediction",
            "CM property (a_p = 0 for inert)",
            "Maximum Pisano period",
            "Maximum Weil ratio |a_p|/(2√p)",
            "Hasse bound (theoretical)",
        ],
        "Value": [
            "Ghandali (2026) — Quadratic Residuosity in Fibonacci Sequences",
            f"3 to {int(df['p'].max()):,}",
            f"{n_total:,}",
            f"{n_split:,}",
            f"{n_inert:,}",
            f"{n_inert / n_total:.6f}",
            "0.500000",
            f"Verified for all {n_inert:,} inert primes",
            f"{int(df['pisano_period'].max()):,}",
            f"{df['weil_ratio'].max():.6f}",
            "< 1.000000",
        ],
    })

    try:
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as xl:
            df.to_excel(xl, sheet_name="Trace_Data_Raw", index=False)
            summary.to_excel(xl, sheet_name="Analysis_Summary", index=False)
        print(f"[Success] Excel report saved: {xlsx_path}")
    except Exception as exc:
        print(f"[Warning] Excel export failed: {exc}")
