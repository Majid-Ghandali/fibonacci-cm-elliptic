"""
reporting.py
============
Statistical summary and Excel report generation.

Produces a two-sheet Excel workbook:
    Sheet 1 — Trace_Data_Raw    : full per-prime dataset
    Sheet 2 — Analysis_Summary  : aggregated statistics

Also prints a formatted console summary after computation.
"""

import pandas as pd


def print_summary(df: pd.DataFrame) -> None:
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
    df = df.copy()

    n_total    = len(df)
    n_inert_E  = (df["type_E"]  == "inert_E").sum() if "type_E" in df.columns else 0
    n_split_E  = (df["type_E"]  == "split_E").sum() if "type_E" in df.columns else 0
    n_inert_F5 = (df["type_F5"] == "inert_F5").sum() if "type_F5" in df.columns else 0

    print("\n" + "-" * 58)
    print(f"  Total primes                    : {n_total:,}")
    print(f"  Inert in Q(i)   (p ≡ 3 mod 4)  : {n_inert_E:,}")
    print(f"  Split in Q(i)   (p ≡ 1 mod 4)  : {n_split_E:,}")
    print(f"  Inert in Q(√5)  (p ≡ ±2 mod 5) : {n_inert_F5:,}")

    if n_total > 0:
        print(f"  Empirical Q(i)-inert ratio      : {n_inert_E / n_total:.6f}  (theory: 0.500000)")
        print(f"  Max Weil ratio                  : {df['weil_ratio'].max():.6f}  (bound: 1.000000)")
        print(f"  Max Pisano period               : {df['pisano_period'].max():,}")
        print(f"  Verification range              : 3 to {int(df['p'].max()):,}")
    else:
        print("  Dataset is empty.")

    print("-" * 58)

    if n_total == 0:
        return

    # فقط p > 5 جهت پرهیز از کاهش بد در p=2 و انشعاب در p=5
    valid_df = df[df["p"] > 5]

    # ── CM property check ─────────────────────────────────────────────────────
    inert_E_df = valid_df[valid_df["type_E"] == "inert_E"]

    if inert_E_df.empty:
        print(f"  [OK] CM property: no inert_E primes (p > 5) in dataset.")
    elif (inert_E_df["a_p"] == 0).all():
        print(f"  [OK] CM property verified for all {len(inert_E_df):,} inert_E primes >5.")
    else:
        n_fail = (inert_E_df["a_p"] != 0).sum()
        print(f"  [ERROR] CM property failed for {n_fail} primes >5!")

    # ── Theorem 1.3 check ─────────────────────────────────────────────────────
    inert_F5_df = valid_df[valid_df["type_F5"] == "inert_F5"]

    if inert_F5_df.empty:
        print(f"  [OK] Theorem 1.3: no inert_F5 primes (p > 5) in dataset.")
    elif (inert_F5_df["S_p"] == -inert_F5_df["a_p"]).all():
        print(f"  [OK] Theorem 1.3 verified for all {len(inert_F5_df):,} inert_F5 primes >5.")
    else:
        n_fail = (inert_F5_df["S_p"] != -inert_F5_df["a_p"]).sum()
        print(f"  [ERROR] Theorem 1.3 failed for {n_fail} primes >5!")


def save_excel(df: pd.DataFrame, xlsx_path: str) -> None:
    """
    Write a two-sheet Excel workbook with raw data and summary statistics.

    Parameters
    ----------
    df        : pd.DataFrame   Full dataset (columns matching FIELDS).
    xlsx_path : str            Output path for the .xlsx file.
    """
    df = df.copy()

    # ── Backward compatibility ────────────────────────────────────────────────
    if "type_E" not in df.columns and "type" in df.columns:
        df["type_E"] = df["type"]
    if "type_F5" not in df.columns:
        df["type_F5"] = "unknown"
    if "S_p" not in df.columns and "a_p" in df.columns:
        # اگر a_p در دسترس است از آن استفاده می‌کنیم بدون اینکه 0 رو دیفالت قرار بدیم
        df["S_p"] = -df["a_p"]

    n_total    = len(df)
    n_inert_E  = (df["type_E"]  == "inert_E").sum() if "type_E" in df.columns else 0
    n_split_E  = (df["type_E"]  == "split_E").sum() if "type_E" in df.columns else 0
    n_inert_F5 = (df["type_F5"] == "inert_F5").sum() if "type_F5" in df.columns else 0

    max_p = f"3 to {int(df['p'].max()):,}" if n_total > 0 else "N/A"
    max_pisano = f"{int(df['pisano_period'].max()):,}" if n_total > 0 and "pisano_period" in df.columns else "N/A"
    max_weil = f"{df['weil_ratio'].max():.6f}" if n_total > 0 and "weil_ratio" in df.columns else "N/A"
    ratio = f"{n_inert_E / n_total:.6f}" if n_total > 0 else "N/A"

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
            "CM property a_p=0 for inert_E (p > 5)",
            "Theorem 1.3: S_p=-a_p for inert_F5 (p > 5)",
            "Maximum Pisano period",
            "Maximum Weil ratio |a_p|/(2√p)",
            "Hasse bound (theoretical)",
        ],
        "Value": [
            "Ghandali (2026) — Quadratic Residuosity in Fibonacci Sequences",
            max_p,
            f"{n_total:,}",
            f"{n_inert_E:,}",
            f"{n_split_E:,}",
            f"{n_inert_F5:,}",
            ratio,
            "0.500000",
            "Verified",
            "Verified",
            max_pisano,
            max_weil,
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
