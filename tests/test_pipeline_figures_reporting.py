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

Schema note (v2)
----------------
Two distinct inertness conditions are tracked separately:
    type_E  : 'inert_E' if p ≡ 3 (mod 4)  — CM property: a_p = 0
    type_F5 : 'inert_F5' if p ≡ ±2 (mod 5) — hypothesis of Theorem 1.3
    S_p     : raw character sum; S_p = -a_p (Theorem 1.3)
"""

import csv
import pytest
import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# SHARED FIXTURE — small synthetic dataset (new schema)
# ============================================================

@pytest.fixture
def small_df():
    """
    Minimal synthetic DataFrame matching the current FIELDS schema.

    type_E  : 'inert_E'  if p ≡ 3 (mod 4)  — governs CM property a_p = 0
              'split_E'  if p ≡ 1 (mod 4)
    type_F5 : 'inert_F5' if p ≡ ±2 (mod 5) — hypothesis of Theorem 1.3
              'split_F5' if p ≡ ±1 (mod 5)
    S_p     : raw character sum; S_p = -a_p

    Primes chosen to cover all four (type_E × type_F5) combinations:
        p=7  : inert_E  ∩ inert_F5  (p≡3 mod 4, p≡2 mod 5)  a_p=0
        p=13 : split_E  ∩ inert_F5  (p≡1 mod 4, p≡3 mod 5)  a_p=-2 ≠ 0
        p=11 : inert_E  ∩ split_F5  (p≡3 mod 4, p≡1 mod 5)  a_p=0
        p=29 : split_E  ∩ split_F5  (p≡1 mod 4, p≡4 mod 5)  a_p=10
    """
    rows = [
        # inert_E ∩ inert_F5  (p=7: 7≡3 mod4, 7≡2 mod5)
        {"p": 7,  "type_E": "inert_E",  "type_F5": "inert_F5",
         "pisano_period": 16, "S_p":  0, "a_p":  0,
         "norm_trace": 0.000, "weil_ratio": 0.000},

        # inert_E ∩ split_F5  (p=11: 11≡3 mod4, 11≡1 mod5)
        {"p": 11, "type_E": "inert_E",  "type_F5": "split_F5",
         "pisano_period": 10, "S_p":  0, "a_p":  0,
         "norm_trace": 0.000, "weil_ratio": 0.000},

        # inert_E ∩ inert_F5  (p=19: 19≡3 mod4, 19≡4 mod5 ≡ -1 mod5)
        {"p": 19, "type_E": "inert_E",  "type_F5": "inert_F5",
         "pisano_period": 18, "S_p":  0, "a_p":  0,
         "norm_trace": 0.000, "weil_ratio": 0.000},

        # inert_E ∩ split_F5  (p=3: 3≡3 mod4, 3≡3 mod5 — wait: 3 mod5=3 ≡ -2, so inert_F5)
        # Correction: p=3, 3 mod 5 = 3 ≡ -2 mod 5  => inert_F5
        {"p": 3,  "type_E": "inert_E",  "type_F5": "inert_F5",
         "pisano_period":  8, "S_p":  0, "a_p":  0,
         "norm_trace": 0.000, "weil_ratio": 0.000},

        # split_E ∩ inert_F5  (p=13: 13≡1 mod4, 13≡3 mod5 ≡ -2 mod5)
        {"p": 13, "type_E": "split_E",  "type_F5": "inert_F5",
         "pisano_period": 28, "S_p":  2, "a_p": -2,
         "norm_trace": -0.555, "weil_ratio": 0.277},

        # split_E ∩ split_F5  (p=29: 29≡1 mod4, 29≡4 mod5 ≡ -1 mod5)
        {"p": 29, "type_E": "split_E",  "type_F5": "split_F5",
         "pisano_period": 14, "S_p": -10, "a_p": 10,
         "norm_trace":  1.857, "weil_ratio": 0.928},

        # split_E ∩ inert_F5  (p=17: 17≡1 mod4, 17≡2 mod5)
        {"p": 17, "type_E": "split_E",  "type_F5": "inert_F5",
         "pisano_period": 36, "S_p": -2, "a_p":  2,
         "norm_trace":  0.485, "weil_ratio": 0.243},

        # split_E ∩ split_F5  (p=5: special, split_E since 5≡1 mod4)
        {"p": 5,  "type_E": "split_E",  "type_F5": "split_F5",
         "pisano_period": 20, "S_p": -2, "a_p":  2,
         "norm_trace":  0.894, "weil_ratio": 0.447},
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
        # All expected columns present (new schema)
        for col in ["p", "type_E", "type_F5", "pisano_period",
                    "S_p", "a_p", "norm_trace", "weil_ratio"]:
            assert col in df.columns, f"Missing column: {col}"

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
        """
        All rows have correct types and both properties hold for p > 5:
        1. CM property  : a_p = 0 for all inert_E primes (p ≡ 3 mod 4)
        2. Theorem 1.3  : S_p = -a_p for all inert_F5 primes (p ≡ ±2 mod 5)
        """
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")

        # Exclude bad reduction primes (p=2) and ramified primes in Q(sqrt(5)) (p=5)
        valid_primes = df[df["p"] > 5]

        # ── CM property ───────────────────────────────────────────────────────
        inert_E = valid_primes[valid_primes["type_E"] == "inert_E"]
        assert len(inert_E) > 0, "No inert_E primes found for p > 5"
        assert (inert_E["a_p"] == 0).all(), (
            f"CM property violated for {(inert_E['a_p'] != 0).sum()} primes"
        )

        # ── Theorem 1.3 ───────────────────────────────────────────────────────
        inert_F5 = valid_primes[valid_primes["type_F5"] == "inert_F5"]
        assert len(inert_F5) > 0, "No inert_F5 primes found for p > 5"
        assert (inert_F5["S_p"] == -inert_F5["a_p"]).all(), (
            f"Theorem 1.3 violated for {(inert_F5['S_p'] != -inert_F5['a_p']).sum()} primes"
        )

        # ── Hasse bound ───────────────────────────────────────────────────────
        assert (valid_primes["weil_ratio"] < 1.0 + 1e-9).all(), "Hasse bound violated"

        # ── split_E property (Mathematical necessity for CM curves) ──────────
        split_E = valid_primes[valid_primes["type_E"] == "split_E"]
        assert len(split_E) > 0, "No split_E primes found for p > 5"
        assert (split_E["a_p"] != 0).all(), "Mathematical violation: split_E primes must have a_p != 0"

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
        csv_path = tmp_path / "test.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerow({
                "p": 7, "type_E": "inert_E", "type_F5": "inert_F5",
                "pisano_period": 16, "S_p": 0,
                "a_p": 0, "norm_trace": 0.0, "weil_ratio": 0.0,
            })
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
        """Covers: print_summary — all print branches (new schema)."""
        from fibonacci_cm.reporting import print_summary
        print_summary(small_df)
        captured = capsys.readouterr()
        assert "Total primes" in captured.out
        assert "[OK]" in captured.out

    def test_print_summary_cm_failure_branch(self, capsys):
        """Covers: the [ERROR] branch when CM property is violated."""
        from fibonacci_cm.reporting import print_summary
        # inert_E prime with a_p ≠ 0 (and p > 5) — deliberately wrong to trigger ERROR branch
        bad_df = pd.DataFrame([{
            "p": 7, "type_E": "inert_E", "type_F5": "inert_F5",
            "pisano_period": 16, "S_p": -1, "a_p": 1,
            "norm_trace": 0.378, "weil_ratio": 0.189,
        }])
        print_summary(bad_df)
        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    def test_print_summary_theorem_failure_branch(self, capsys):
        """Covers: the [ERROR] branch when Theorem 1.3 is violated."""
        from fibonacci_cm.reporting import print_summary
        # inert_F5 prime where S_p ≠ -a_p (and p > 5) — deliberately wrong
        bad_df = pd.DataFrame([{
            "p": 13, "type_E": "split_E", "type_F5": "inert_F5",
            "pisano_period": 28, "S_p": 99, "a_p": -2,
            "norm_trace": -0.555, "weil_ratio": 0.277,
        }])
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

    # ── Additional Reporting Coverage Tests ───────────────────────────────────

    def test_reporting_empty_dataframe(self, capsys):
        """Covers: 'Dataset is empty' branch in print_summary."""
        from fibonacci_cm.reporting import print_summary
        empty_df = pd.DataFrame(columns=["p", "type_E", "type_F5", "a_p", "S_p"])
        print_summary(empty_df)
        assert "Dataset is empty" in capsys.readouterr().out

    def test_reporting_no_specific_primes(self, capsys):
        """Covers: Branches where no inert_E or inert_F5 primes are found."""
        from fibonacci_cm.reporting import print_summary
        # Only split primes
        df = pd.DataFrame([{"p": 29, "type_E": "split_E", "type_F5": "split_F5", "a_p": 10, "S_p": -10}])
        print_summary(df)
        captured = capsys.readouterr().out
        assert "no inert_E primes" in captured
        assert "no inert_F5 primes" in captured

    def test_save_excel_backward_compatibility(self, tmp_path):
        """Covers: Schema normalization logic in save_excel."""
        from fibonacci_cm.reporting import save_excel
        old_df = pd.DataFrame([{"p": 7, "type": "inert_E", "a_p": 0}])
        xlsx = str(tmp_path / "compat.xlsx")
        save_excel(old_df, xlsx)
        saved = pd.read_excel(xlsx)
        assert "type_E" in saved.columns


# ============================================================
# PIPELINE — COVERAGE COMPLETION
# ============================================================

class TestPipelineCoverageCompletion:

    def test_restart_deletes_existing_csv(self, tmp_path):
        """
        Covers: csv_path.unlink() when restart mode finds an existing CSV.
        """
        from fibonacci_cm.pipeline import run
        run(output_dir=str(tmp_path), max_p=13, mode="restart")
        csv_file = tmp_path / "Dataset_Raw_Primes.csv"
        assert csv_file.exists()

        df = run(output_dir=str(tmp_path), max_p=13, mode="restart")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_last_prime_corrupted_csv(self, tmp_path):
        """
        Covers: except (IndexError, ValueError) branch.
        A CSV with non-integer first column triggers ValueError.
        """
        from fibonacci_cm.pipeline import get_last_processed_prime
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("p,type_E,type_F5,a_p\nNOT_AN_INT,inert_E,inert_F5,0\n")
        result = get_last_processed_prime(bad_csv)
        assert result == 1

    def test_get_last_prime_only_header(self, tmp_path):
        """
        Covers: IndexError when CSV has only header row.
        """
        from fibonacci_cm.pipeline import get_last_processed_prime
        header_only = tmp_path / "header.csv"
        header_only.write_text(
            "p,type_E,type_F5,pisano_period,S_p,a_p,norm_trace,weil_ratio\n"
        )
        result = get_last_processed_prime(header_only)
        assert result == 1

    def test_import_fallback_path(self, tmp_path):
        """
        Covers: the except ImportError fallback in pipeline.py.
        Verifies compute_prime_data is importable via absolute path.
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from fibonacci_cm.arithmetic import compute_prime_data
        result = compute_prime_data(7)
        assert result["a_p"] == 0
        assert result["type_E"] == "inert_E"
        assert result["type_F5"] == "inert_F5"
