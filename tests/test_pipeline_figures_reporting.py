r"""
tests/test_pipeline_figures_reporting.py
========================================
Coverage tests for pipeline.py, figures.py, and reporting.py.

Schema note (v3 - final)
------------------------
Two distinct inertness conditions:
    type_E  : 'inert_E' if p ≡ 3 (mod 4)  — CM property: a_p = 0
    type_F5 : 'inert_F5' if p ≡ ±2 (mod 5) — hypothesis of Theorem 1.3
    S_p     : raw character sum; S_p = -a_p (Theorem 1.3)

Note: p=5 is excluded (5%5=0, bad reduction). p=2 is excluded (bad reduction).
All primes in small_df are > 5.
"""

import csv
import pytest
import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# SHARED FIXTURE
# ============================================================

@pytest.fixture
def small_df():
    """
    Synthetic DataFrame with all primes > 5, covering all 4 combinations
    of (type_E x type_F5). Values verified against arithmetic.py.

    p=7  : 7%4=3->inert_E,  7%5=2->inert_F5,  a_p=0,  S_p=0
    p=11 : 11%4=3->inert_E, 11%5=1->split_F5, a_p=0,  S_p=0
    p=23 : 23%4=3->inert_E, 23%5=3->inert_F5, a_p=0,  S_p=0
    p=19 : 19%4=3->inert_E, 19%5=4->split_F5, a_p=0,  S_p=0
    p=13 : 13%4=1->split_E, 13%5=3->inert_F5, a_p=-2, S_p=2
    p=17 : 17%4=1->split_E, 17%5=2->inert_F5, a_p=2,  S_p=-2
    p=29 : 29%4=1->split_E, 29%5=4->split_F5, a_p=10, S_p=-10
    p=41 : 41%4=1->split_E, 41%5=1->split_F5, a_p=-8, S_p=8
    """
    rows = [
        {"p": 7,  "type_E": "inert_E", "type_F5": "inert_F5",
         "pisano_period": 16, "S_p":   0, "a_p":  0,
         "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 11, "type_E": "inert_E", "type_F5": "split_F5",
         "pisano_period": 10, "S_p":   0, "a_p":  0,
         "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 23, "type_E": "inert_E", "type_F5": "inert_F5",
         "pisano_period": 48, "S_p":   0, "a_p":  0,
         "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 19, "type_E": "inert_E", "type_F5": "split_F5",
         "pisano_period": 18, "S_p":   0, "a_p":  0,
         "norm_trace":  0.000, "weil_ratio": 0.000},
        {"p": 13, "type_E": "split_E", "type_F5": "inert_F5",
         "pisano_period": 28, "S_p":   2, "a_p": -2,
         "norm_trace": -0.555, "weil_ratio": 0.277},
        {"p": 17, "type_E": "split_E", "type_F5": "inert_F5",
         "pisano_period": 36, "S_p":  -2, "a_p":  2,
         "norm_trace":  0.485, "weil_ratio": 0.243},
        {"p": 29, "type_E": "split_E", "type_F5": "split_F5",
         "pisano_period": 14, "S_p": -10, "a_p": 10,
         "norm_trace":  1.857, "weil_ratio": 0.928},
        {"p": 41, "type_E": "split_E", "type_F5": "split_F5",
         "pisano_period": 20, "S_p":   8, "a_p": -8,
         "norm_trace": -1.249, "weil_ratio": 0.625},
    ]
    return pd.DataFrame(rows)


# ============================================================
# PIPELINE TESTS
# ============================================================

class TestPipeline:

    def test_restart_mode_small_range(self, tmp_path):
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        for col in ["p", "type_E", "type_F5", "pisano_period",
                    "S_p", "a_p", "norm_trace", "weil_ratio"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_restart_creates_csv(self, tmp_path):
        from fibonacci_cm.pipeline import run
        run(output_dir=str(tmp_path), max_p=20, mode="restart")
        csv_file = tmp_path / "Dataset_Raw_Primes.csv"
        assert csv_file.exists()
        assert csv_file.stat().st_size > 0

    def test_resume_mode_continues(self, tmp_path):
        from fibonacci_cm.pipeline import run
        df1 = run(output_dir=str(tmp_path), max_p=13, mode="restart")
        df2 = run(output_dir=str(tmp_path), max_p=30, mode="resume")
        assert len(df2) >= len(df1)

    def test_plot_mode_loads_existing(self, tmp_path):
        from fibonacci_cm.pipeline import run
        run(output_dir=str(tmp_path), max_p=20, mode="restart")
        df = run(output_dir=str(tmp_path), max_p=0, mode="plot")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_plot_mode_no_csv_falls_back(self, tmp_path):
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=20, mode="plot")
        assert isinstance(df, pd.DataFrame)

    def test_output_schema(self, tmp_path):
        """CM property and Theorem 1.3 verified on actual pipeline output."""
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")

        # No p=2 in output (bad reduction)
        assert 2 not in df["p"].values, "p=2 should be excluded"

        # CM property: a_p=0 for all inert_E
        inert_E = df[df["type_E"] == "inert_E"]
        assert (inert_E["a_p"] == 0).all(), (
            f"CM property violated for primes: {inert_E[inert_E['a_p']!=0]['p'].tolist()}"
        )

        # Theorem 1.3: S_p = -a_p for all inert_F5
        inert_F5 = df[df["type_F5"] == "inert_F5"]
        assert (inert_F5["S_p"] == -inert_F5["a_p"]).all(), (
            f"Theorem 1.3 violated"
        )

        # Hasse bound
        assert (df["weil_ratio"] < 1.0 + 1e-9).all(), "Hasse bound violated"

        # split_E primes exist
        assert len(df[df["type_E"] == "split_E"]) > 0

    def test_sorted_by_p(self, tmp_path):
        from fibonacci_cm.pipeline import run
        df = run(output_dir=str(tmp_path), max_p=30, mode="restart")
        assert list(df["p"]) == sorted(df["p"].tolist())

    def test_get_last_processed_prime_empty(self, tmp_path):
        from fibonacci_cm.pipeline import get_last_processed_prime
        empty = tmp_path / "empty.csv"
        empty.touch()
        assert get_last_processed_prime(empty) == 1

    def test_get_last_processed_prime_nonexistent(self, tmp_path):
        from fibonacci_cm.pipeline import get_last_processed_prime
        assert get_last_processed_prime(tmp_path / "no.csv") == 1

    def test_get_last_processed_prime_valid(self, tmp_path):
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
        from fibonacci_cm.figures import generate_all
        generate_all(small_df, str(tmp_path))
        assert (tmp_path / "Fig1_Trace_Analysis.png").exists()
        assert (tmp_path / "Fig2_SatoTate.png").exists()
        assert (tmp_path / "Fig3_Convergence.png").exists()

    def test_figures_are_nonempty(self, tmp_path, small_df):
        from fibonacci_cm.figures import generate_all
        generate_all(small_df, str(tmp_path))
        for fname in ["Fig1_Trace_Analysis.png", "Fig2_SatoTate.png", "Fig3_Convergence.png"]:
            size = (tmp_path / fname).stat().st_size
            assert size > 1000, f"{fname} too small ({size} bytes)"

    def test_figures_no_exception(self, tmp_path, small_df):
        from fibonacci_cm.figures import generate_all
        try:
            generate_all(small_df, str(tmp_path))
        except Exception as exc:
            pytest.fail(f"generate_all raised: {exc}")

    def test_figures_creates_output_dir(self, tmp_path, small_df):
        from fibonacci_cm.figures import generate_all
        new_dir = tmp_path / "new_output"
        generate_all(small_df, str(new_dir))
        assert new_dir.exists()


# ============================================================
# REPORTING TESTS
# ============================================================

class TestReporting:

    def test_print_summary_runs(self, small_df, capsys):
        from fibonacci_cm.reporting import print_summary
        print_summary(small_df)
        captured = capsys.readouterr()
        assert "Total primes" in captured.out
        assert "[OK]" in captured.out

    def test_print_summary_cm_failure_branch(self, capsys):
        from fibonacci_cm.reporting import print_summary
        bad_df = pd.DataFrame([{
            "p": 7, "type_E": "inert_E", "type_F5": "inert_F5",
            "pisano_period": 16, "S_p": -1, "a_p": 1,
            "norm_trace": 0.378, "weil_ratio": 0.189,
        }])
        print_summary(bad_df)
        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    def test_print_summary_theorem_failure_branch(self, capsys):
        from fibonacci_cm.reporting import print_summary
        bad_df = pd.DataFrame([{
            "p": 13, "type_E": "split_E", "type_F5": "inert_F5",
            "pisano_period": 28, "S_p": 99, "a_p": -2,
            "norm_trace": -0.555, "weil_ratio": 0.277,
        }])
        print_summary(bad_df)
        captured = capsys.readouterr()
        assert "ERROR" in captured.out

    def test_save_excel_creates_file(self, tmp_path, small_df):
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)
        assert Path(xlsx).exists()
        assert Path(xlsx).stat().st_size > 0

    def test_save_excel_two_sheets(self, tmp_path, small_df):
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)
        wb = pd.ExcelFile(xlsx)
        assert "Trace_Data_Raw" in wb.sheet_names
        assert "Analysis_Summary" in wb.sheet_names

    def test_save_excel_raw_data_complete(self, tmp_path, small_df):
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)
        raw = pd.read_excel(xlsx, sheet_name="Trace_Data_Raw")
        assert len(raw) == len(small_df)
        assert "a_p" in raw.columns

    def test_save_excel_summary_structure(self, tmp_path, small_df):
        from fibonacci_cm.reporting import save_excel
        xlsx = str(tmp_path / "report.xlsx")
        save_excel(small_df, xlsx)
        summary = pd.read_excel(xlsx, sheet_name="Analysis_Summary")
        assert "Parameter" in summary.columns
        assert "Value" in summary.columns

    def test_save_excel_invalid_path(self, small_df, capsys):
        from fibonacci_cm.reporting import save_excel
        save_excel(small_df, "/invalid/path/report.xlsx")
        captured = capsys.readouterr()
        assert "Warning" in captured.out or "failed" in captured.out.lower()


# ============================================================
# PIPELINE COVERAGE COMPLETION
# ============================================================

class TestPipelineCoverageCompletion:

    def test_restart_deletes_existing_csv(self, tmp_path):
        from fibonacci_cm.pipeline import run
        run(output_dir=str(tmp_path), max_p=13, mode="restart")
        assert (tmp_path / "Dataset_Raw_Primes.csv").exists()
        df = run(output_dir=str(tmp_path), max_p=13, mode="restart")
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_last_prime_corrupted_csv(self, tmp_path):
        from fibonacci_cm.pipeline import get_last_processed_prime
        bad_csv = tmp_path / "bad.csv"
        bad_csv.write_text("p,type_E,type_F5,a_p\nNOT_AN_INT,inert_E,inert_F5,0\n")
        assert get_last_processed_prime(bad_csv) == 1

    def test_get_last_prime_only_header(self, tmp_path):
        from fibonacci_cm.pipeline import get_last_processed_prime
        header_only = tmp_path / "header.csv"
        header_only.write_text(
            "p,type_E,type_F5,pisano_period,S_p,a_p,norm_trace,weil_ratio\n"
        )
        assert get_last_processed_prime(header_only) == 1

    def test_import_fallback_path(self, tmp_path):
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from fibonacci_cm.arithmetic import compute_prime_data
        result = compute_prime_data(7)
        assert result["a_p"] == 0
        assert result["type_E"] == "inert_E"
        assert result["type_F5"] == "inert_F5"
