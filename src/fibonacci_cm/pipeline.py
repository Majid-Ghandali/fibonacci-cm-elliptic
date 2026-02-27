"""
pipeline.py
===========
Hardened parallel processing pipeline for Fibonacci CM research.
Fault-tolerant, multi-core, checkpoint-recoverable.

Execution modes
---------------
    RESUME  (1) : Continue from the last successfully saved prime.
    RESTART (2) : Clear existing data and recompute from scratch.
    PLOT    (3) : Regenerate figures from an existing dataset only.

Architecture
------------
- Prime sieve via sympy.sieve.primerange (memory-efficient).
- Worker pool via multiprocessing.Pool with imap and chunksize=512.
- Results written row-by-row to CSV (safe to interrupt at any point).
- Progress bar via tqdm.
- Path-based I/O via pathlib for cross-platform compatibility.
"""

import csv
import sys
from multiprocessing import Pool, cpu_count, freeze_support
from pathlib import Path

import pandas as pd
from sympy import sieve
from tqdm import tqdm

try:
    from .arithmetic import compute_prime_data
except ImportError:
    # Fallback for local development when package is not installed
    sys.path.append(str(Path(__file__).parent.parent))
    from fibonacci_cm.arithmetic import compute_prime_data

# ---------------------------------------------------------------------------
# Dataset schema — canonical column order throughout the project
# ---------------------------------------------------------------------------
FIELDS       = ["p", "type", "pisano_period", "a_p", "norm_trace", "weil_ratio"]
CSV_FILENAME = "Dataset_Raw_Primes.csv"


def get_last_processed_prime(csv_path: Path) -> int:
    """
    Safely retrieve the last computed prime for checkpoint recovery.

    Uses a low-memory tail-read instead of loading the full CSV —
    critical for large datasets (148k+ rows).

    Returns 1 if the file is empty or unreadable.
    """
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        return 1
    try:
        with open(csv_path, "r") as fh:
            lines = fh.readlines()
            last_line = lines[-1].strip()
            return int(last_line.split(",")[0])
    except (IndexError, ValueError):
        return 1


def run(output_dir: str, max_p: int, mode: str) -> pd.DataFrame:
    """
    Execute the full computation pipeline and return the final DataFrame.

    Parameters
    ----------
    output_dir : str
        Directory for CSV and Excel outputs.
    max_p : int
        Upper bound on prime range (inclusive).
    mode : str
        'resume'  — continue from last checkpoint.
        'restart' — clear existing data and recompute.
        'plot'    — skip computation, load existing CSV.

    Returns
    -------
    pd.DataFrame with columns matching FIELDS, sorted by p.
    """
    freeze_support()   # Critical for Windows multiprocessing stability

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    csv_path = out_path / CSV_FILENAME

    # ── Plot-only mode ────────────────────────────────────────────────────────
    if mode == "plot":
        if csv_path.exists():
            return _load_sorted(csv_path)
        print("[Warning] No dataset found. Switching to restart mode.")
        mode = "restart"

    # ── Restart: remove existing data ─────────────────────────────────────────
    if mode == "restart" and csv_path.exists():
        csv_path.unlink()
        print("[Info] Existing dataset removed. Starting fresh.")

    # ── Resume: find checkpoint ───────────────────────────────────────────────
    start_p = 3
    if mode == "resume" and csv_path.exists():
        last_p  = get_last_processed_prime(csv_path)
        start_p = last_p + 1
        print(f"[Info] Resuming from p > {last_p:,}")

    # ── Enumerate primes and dispatch to worker pool ──────────────────────────
    primes     = list(sieve.primerange(start_p, max_p + 1))
    write_mode = "a" if (mode == "resume" and csv_path.exists()) else "w"

    if primes:
        nproc = max(1, cpu_count() - 1)   # reserve one core for OS
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


def _load_sorted(csv_path: Path) -> pd.DataFrame:
    """Load dataset from CSV and return sorted by p with canonical columns."""
    df = pd.read_csv(csv_path)
    return df[FIELDS].sort_values("p").reset_index(drop=True)
