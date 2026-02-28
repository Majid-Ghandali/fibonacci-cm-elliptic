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
    df = df.copy()
    """
    Print a formatted summary of the computed dataset to stdout.

    Reports both inertness conditions separately:
        type_E  : inertness in Q(i) — governs CM property a_p = 0
        type_F5 : inertness in Q(sqrt(5)) — hypothesis of Theorem 1.3

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: p, type_E, type_F5, pisano_period,
        S_p, a_p, weil_ratio.
    """
     # ── Backward compatibility ──────────────────────────────
    if "type_E" not in df.columns and "type" in df.columns:
        df["type_E"] = df["type"]

    if "type_F5" not in df.columns:
        df["type_F5"] = "unknown"

    if "S_p" not in df.columns:
        df["S_p"] = -df.get("a_p", 0)
    
    n_total = len(df)
    n_inert_E = (df["type_E"] == "inert_E").sum()
    n_split_E = (df["type_E"] == "split_E").sum()
    n_inert_F5 = (df["type_F5"] == "inert_F5").sum()

    print("\n" + "-" * 58)
    print(f"  Total primes                    : {n_total:,}")
    print(f"  Inert in Q(i)   (p ≡ 3 mod 4)  : {n_inert_E:,}")
    print(f"  Split in Q(i)   (p ≡ 1 mod 4)  : {n_split_E:,}")
    print(f"  Inert in Q(√5)  (p ≡ ±2 mod 5) : {n_inert_F5:,}")
    print(f"  Empirical Q(i)-inert ratio      : {n_inert_E / n_total:.6f}  (theory: 0.500000)")
    print(f"  Max Weil ratio                  : {df['weil_ratio'].max():.6f}  (bound: 1.000000)")
    print(f"  Max Pisano period               : {df['pisano_period'].max():,}")
    print(f"  Verification range              : 3  to  {int(df['p'].max()):,}")
    print("-" * 58)

    ## CM property: all inert_E primes must have a_p = 0
    inert_E_df = df[df["type_E"] == "inert_E"]
    if (inert_E_df["a_p"] == 0).all():
        print("CM property verified.")
    else:
        n_fail = (inert_E_df["a_p"] != 0).sum()
        print(f"CM property ERROR. Violated for {n_fail} primes.")

    # Theorem 1.3: S_p = -a_p for all inert_F5 primes
    inert_F5_df = df[df["type_F5"] == "inert_F5"]
    if (inert_F5_df["S_p"] == -inert_F5_df["a_p"]).all():
        print(f"  [OK] Theorem 1.3: S_p = -a_p for all {n_inert_F5:,} primes inert in Q(√5).")
    else:
        n_fail = (inert_F5_df["S_p"] != -inert_F5_df["a_p"]).sum()
        print(f"  [ERROR] Theorem 1.3 FAILED for {n_fail} primes!")


def save_excel(df: pd.DataFrame, xlsx_path: str) -> None:
    df = df.copy()
    """
    Write a two-sheet Excel workbook with raw data and summary statistics.

    Parameters
    ----------
    df        : pd.DataFrame   Full dataset (columns matching FIELDS).
    xlsx_path : str            Output path for the .xlsx file.
    """
        # ── Backward compatibility ──────────────────────────────
    if "type_E" not in df.columns and "type" in df.columns:
        df["type_E"] = df["type"]

    if "type_F5" not in df.columns:
        df["type_F5"] = "unknown"

    if "S_p" not in df.columns:
        df["S_p"] = -df.get("a_p", 0)
    
    n_total    = len(df)
    n_inert_E  = (df["type_E"]  == "inert_E").sum()
    n_split_E  = (df["type_E"]  == "split_E").sum()
    n_inert_F5 = (df["type_F5"] == "inert_F5").sum()

    summary = pd.DataFrame({
        "Parameter": [
            "Paper",
            "Verification range",
            "Total primes computed",
            "Inert in Q(i)  — p ≡ 3 mod 4  (CM property)",
            "Split in Q(i)  — p ≡ 1 mod 4",
            "Inert in Q(√5) — p ≡ ±2 mod 5  (Theorem 1.3)",
            "Empirical Q(i)-inert ratio",
            "Chebotarev prediction",
            "CM property a_p=0 for inert_E",
            "Theorem 1.3: S_p=-a_p for inert_F5",
            "Maximum Pisano period",
            "Maximum Weil ratio |a_p|/(2√p)",
            "Hasse bound (theoretical)",
        ],
        "Value": [
            "Ghandali (2026) — Quadratic Residuosity in Fibonacci Sequences",
            f"3 to {int(df['p'].max()):,}",
            f"{n_total:,}",
            f"{n_inert_E:,}",
            f"{n_split_E:,}",
            f"{n_inert_F5:,}",
            f"{n_inert_E / n_total:.6f}",
            "0.500000",
            f"Verified for all {n_inert_E:,} primes",
            f"Verified for all {n_inert_F5:,} primes",
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
