r"""
tests/test_pipeline_figures_reporting.py
========================================
Coverage tests for pipeline.py, figures.py, and reporting.py.

Strategy
--------
- Pipeline : use tmp_path + small prime range (p <= 30) to avoid heavy compute.
- Figures  : use a synthetic DataFrame; assert files are created, no exceptions.
- Reporting: use a synthetic DataFrame; assert console output and Excel file.

All tests run with NUMBA_DISABLE_JIT=1 (set in pyproject.toml).
"""

import os
import pytest
import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# SHARED FIXTURE — small synthetic dataset
# ============================================================

@pytest.fixture
def small_df():
    """
    Minimal synthetic DataFrame matching the FIELDS schema.
    Contains 4 split and 4 inert primes with correct CM property.
    """
    rows = [
        # split primes (p ≡ 1 mod 4)
        {"p": 5,  "type": "split", "pisano_period": 20, "a_p":  2, "norm_trace":  0.894, "weil_ratio": 0.447},
        {"p": 13, "type": "split", "pisano_period": 28, "a_p": -6, "norm_trace": -1.664, "weil_ratio": 0.832},
        {"p": 17, "type": "split", "pisano_period": 36, "a_p":  2, "norm_trace":  0.485, "weil_ratio": 0.243},
        {"p": 29, "type": "split", "pisano_period": 14, "a_p": 10, "norm_trace":  1.857, "weil_ratio": 0.928},
        # inert primes (p ≡ 3 mod 4) — CM property: a_p = 0
        {"p": 3,  "type": "inert", "pisano_period":  8, "a_p":  0, "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 7,  "type": "inert", "pisano_period": 16, "a_p":  0, "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 11, "type": "inert", "pisano_period": 10, "a_p":  0, "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 19, "type": "inert", "pisano_period": 18, "a_p":  0, "norm_trace":  0.000, "weil_ratio": 0.000},
    ]
    return pd.DataFrame(rows)


# ============================================================
# PIPELINE TESTS
# ============================================================

class TestPipeline:

    def test_restart_mode_small_range(self, tmp_path):
        """
        Covers: mkdir, restart branch, primes loop, CSV write, _load_sorted.
        Uses p <= 30 for speed.
        """
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        # All expected columns present
        for col in ["p", "type", "pisano_period", "a_p", "norm_trace", "weil_ratio"]:
            assert col in df.columns

    def test_restart_creates_csv(self, tmp_path):
        """CSV file is created after restart run."""
        from fibonacci_cm.pipeline import run
        run(output_dir=str(tmp_path), max_p=20, mode="restart")
        csv_file = tmp_path / "Dataset_Raw_Primes.csv"
        assert csv_file.exists()
        assert csv_file.stat().st_size > 0

    def test_resume_mode_continues(self, tmp_path):
        """
        Covers: resume branch + get_last_processed_prime.
        First run up to p=13, then resume up to p=30.
        """
        from fibonacci_cm.pipeline import run
        df1 = run(output_dir=str(tmp_path), max_p=13, mode="restart")
        df2 = run(output_dir=str(tmp_path), max_p=30, mode="resume")
        assert len(df2) >= len(df1)

    def test_plot_mode_loads_existing(self, tmp_path):
        """Covers: plot mode branch — loads CSV without recomputing."""
        from fibonacci_cm.pipeline import run
        run(output_dir=str(tmp_path), max_p=20, mode="restart")
        df = run(output_dir=str(tmp_path), max_p=0, mode="plot")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_plot_mode_no_csv_falls_back(self, tmp_path):
        """Covers: plot mode warning when no CSV exists -> fallback to restart."""
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=20, mode="plot")
        assert isinstance(df, pd.DataFrame)

    def test_output_schema(self, tmp_path):
        """All rows have correct types and CM property holds."""
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")

        inert = df[df["type"] == "inert"]
        split = df[df["type"] == "split"]

        assert (inert["a_p"] == 0).all(), "CM property violated"
        assert len(split) > 0
        assert (df["weil_ratio"] < 1.0 + 1e-9).all(), "Hasse bound violated"

    def test_sorted_by_p(self, tmp_path):
        """Output DataFrame is sorted by p."""
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")
        assert list(df["p"]) == sorted(df["p"].tolist())

    def test_get_last_processed_prime_empty(self, tmp_path):
        """Covers: empty file returns 1."""
        from fibonacci_cm.pipeline import get_last_processed_prime
        empty = tmp_path / "empty.csv"
        empty.touch()
        assert get_last_processed_prime(empty) == 1

    def test_get_last_processed_prime_nonexistent(self, tmp_path):
        """Covers: nonexistent file returns 1."""
        from fibonacci_cm.pipeline import get_last_processed_prime
        assert get_last_processed_prime(tmp_path / "no.csv") == 1

    def test_get_last_processed_prime_valid(self, tmp_path):
        """Covers: valid CSV returns last prime correctly."""
        from fibonacci_cm.pipeline import get_last_processed_prime, FIELDS
        import csv
        csv_path = tmp_path / "test.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerow({"p": 7, "type": "inert", "pisano_period": 16,
                             "a_p": 0, "norm_trace": 0.0, "weil_ratio": 0.0})
        assert get_last_processed_prime(csv_path) == 7


# ============================================================
# FIGURES TESTS
# ============================================================

class TestFigures:

    def test_generate_all_creates_three_files(self, tmp_path, small_df):
        """Covers: generate_all + all three figure functions."""
        from fibonacci_cm.figures import generate_all
        generate_all(small_df, str(tmp_path))

        assert (tmp_path / "Fig1_Trace_Analysis.png").exists()
        assert (tmp_path / "Fig2_SatoTate.png").exists()
        assert (tmp_path / "Fig3_Convergence.png").exists()

    def test_figures_are_nonempty(self, tmp_path, small_df):
        """Generated PNG files must have non-zero size."""
        from fibonacci_cm.figures import generate_all
        generate_all(small_df, str(tmp_path))

        for fname in ["Fig1_Trace_Analysis.png", "Fig2_SatoTate.png", "Fig3_Convergence.png"]:
            size = (tmp_path / fname).stat().st_size
            assert size > 1000, f"{fname} is suspiciously small ({size} bytes)"

    def test_figures_no_exception(self, tmp_path, small_df):
        """generate_all must not raise any exception."""
        from fibonacci_cm.figures import generate_all
        try:
            generate_all(small_df, str(tmp_path))
        except Exception as exc:
            pytest.fail(f"generate_all raised: {exc}")

    def test_figures_creates_output_dir(self, tmp_path, small_df):
        """generate_all creates the output directory if it doesn't exist."""
        from fibonacci_cm.figures import generate_all
        new_dir = tmp_path / "new_output"
        generate_all(small_df, str(new_dir))
        assert new_dir.exists()


# ============================================================
# REPORTING TESTS
# ============================================================

class TestReporting:

    def test_print_summary_runs(self, small_df, capsys):
        """Covers: print_summary — all print branches."""
        from fibonacci_cm.reporting import print_summary
        print_summary(small_df)
        captured = capsys.readouterr()
        assert "Total primes" in captured.out
        assert "CM property verified" in captured.out

    def test_print_summary_cm_failure_branch(self, capsys):
        """Covers: the [ERROR] branch when CM property is violated."""
        from fibonacci_cm.reporting import print_summary
        bad_df = pd.DataFrame([
            {"p": 7, "type": "inert", "pisano_period": 16,
             "a_p": 1, "norm_trace": 0.378, "weil_ratio": 0.189,
             "weil_ratio": 0.189},
        ])
        print_summary(bad_df)
        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    def test_save_excel_creates_file(self, tmp_path, small_df):
        """Covers: save_excel — full ExcelWriter block."""
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)
        assert Path(xlsx).exists()
        assert Path(xlsx).stat().st_size > 0

    def test_save_excel_two_sheets(self, tmp_path, small_df):
        """Excel workbook must have exactly two sheets."""
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)

        wb = pd.ExcelFile(xlsx)
        assert "Trace_Data_Raw" in wb.sheet_names
        assert "Analysis_Summary" in wb.sheet_names

    def test_save_excel_raw_data_complete(self, tmp_path, small_df):
        """Sheet 1 must contain all rows from the input DataFrame."""
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)

        raw = pd.read_excel(xlsx, sheet_name="Trace_Data_Raw")
        assert len(raw) == len(small_df)
        assert "a_p" in raw.columns

    def test_save_excel_summary_structure(self, tmp_path, small_df):
        """Sheet 2 must have Parameter and Value columns."""
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)

        summary = pd.read_excel(xlsx, sheet_name="Analysis_Summary")
        assert "Parameter" in summary.columns
        assert "Value" in summary.columns

    def test_save_excel_invalid_path(self, small_df, capsys):
        """Covers: except branch when Excel write fails."""
        from fibonacci_cm.reporting import save_excel
        save_excel(small_df, "/invalid/path/report.xlsx")
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "failed" in captured.out.lower()
