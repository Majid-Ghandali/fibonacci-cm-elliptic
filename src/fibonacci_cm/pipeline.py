"""
pipeline.py
===========
Parallel prime processing pipeline with fault-tolerant CSV streaming.

Handles three execution modes:
    RESUME  (1) : Continue from the last successfully saved prime.
    RESTART (2) : Clear existing data and recompute from scratch.
    PLOT    (3) : Regenerate figures from an existing dataset only.

Architecture
------------
- Prime sieve via sympy.sieve.primerange (memory-efficient generator).
- Worker pool via multiprocessing.Pool with imap for ordered streaming.
- Results written row-by-row to CSV (fault-tolerant: safe to interrupt).
- Progress bar via tqdm.
"""

import os
import csv
from multiprocessing import Pool, cpu_count, freeze_support

import pandas as pd
from sympy import sieve
from tqdm import tqdm

from .arithmetic import compute_prime_data

# ---------------------------------------------------------------------------
# Dataset schema — column order is canonical throughout the project
# ---------------------------------------------------------------------------
FIELDS = ["p", "type", "pisano_period", "a_p", "norm_trace", "weil_ratio"]


def run(output_dir: str, max_p: int, mode: str) -> pd.DataFrame:
    """
    Execute the full computation pipeline and return the final DataFrame.

    Parameters
    ----------
    output_dir : str   Directory for CSV and Excel outputs.
    max_p      : int   Upper bound on prime range (inclusive).
    mode       : str   '1' = Resume, '2' = Restart, '3' = Plot only.

    Returns
    -------
    pd.DataFrame with columns matching FIELDS, sorted by p.
    """
    freeze_support()
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "Dataset_Raw_Primes.csv")

    # ── Plot-only mode ────────────────────────────────────────────────────────
    if mode == "3":
        if os.path.exists(csv_path):
            return _load_sorted(csv_path)
        print("[Warning] No dataset found. Switching to Restart mode.")
        mode = "2"

    # ── Determine starting prime ──────────────────────────────────────────────
    start_p = 3
    if mode == "1" and os.path.exists(csv_path):
        try:
            tmp = pd.read_csv(csv_path)
            if not tmp.empty:
                start_p = int(tmp["p"].max()) + 1
                print(f"[Info] Resuming from p > {start_p - 1:,}")
        except Exception:
            pass

    # ── Enumerate primes and dispatch to worker pool ──────────────────────────
    primes     = list(sieve.primerange(start_p, max_p + 1))
    write_mode = "a" if (mode == "1" and os.path.exists(csv_path)) else "w"

    if primes:
        nproc = max(1, cpu_count() - 1)
        print(f"[Compute] {len(primes):,} primes on {nproc} core(s) ...")

        with Pool(nproc) as pool:
            with open(csv_path, write_mode, newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=FIELDS)
                if write_mode == "w":
                    writer.writeheader()
                for result in tqdm(
                    pool.imap(compute_prime_data, primes, chunksize=512),
                    total=len(primes),
                    desc="Computing a_p",
                ):
                    writer.writerow(result)
                    fh.flush()   # safe checkpoint after every prime

    # ── Consolidate, sort, and return ─────────────────────────────────────────
    print("\n[Data] Consolidating results ...")
    df = _load_sorted(csv_path)
    df.to_csv(csv_path, index=False)
    return df


def _load_sorted(csv_path: str) -> pd.DataFrame:
    """Load dataset from CSV and return sorted by p with canonical columns."""
    df = pd.read_csv(csv_path)
    return df[FIELDS].sort_values("p").reset_index(drop=True)
