"""
tests/test_arithmetic.py
========================
Unit tests for the arithmetic module.
Run with: pytest tests/
"""

import numpy as np
import pytest
from sympy import isprime

from fibonacci_cm.arithmetic import (
    get_pisano_period,
    build_qr_table,
    fast_ap_engine,
    compute_prime_data,
)


# ============================================================
# PISANO PERIOD TESTS
# ============================================================

class TestPisanoPeriod:
    """
    Correct theory:
      If p ≡ 1,4 (mod 5):  π(p) | (p-1)
      If p ≡ 2,3 (mod 5):  π(p) | 2(p+1)
    """

    def test_known_values(self):
        known = {
            2: 3,
            3: 8,
            5: 20,
            7: 16,
            11: 10,
            13: 28,
            29: 14,
        }
        for p, expected in known.items():
            assert get_pisano_period(p) == expected, \
                f"pi({p}) = {get_pisano_period(p)}, expected {expected}"

    def test_inert_divides_2p_plus_2(self):
        inert = [7, 13, 17, 23, 37, 43, 47]
        for p in inert:
            pi_p = get_pisano_period(p)
            assert (2 * (p + 1)) % pi_p == 0


# ============================================================
# QUADRATIC RESIDUE TABLE
# ============================================================

class TestQRTable:

    def test_qr_table_properties(self):
        for p in [7, 11, 13, 17]:
            table = build_qr_table(p)
            assert len(table) == p
            assert table.sum() == (p - 1) // 2


# ============================================================
# FROBENIUS TRACE TESTS
# ============================================================

class TestFrobeniusTrace:

    def test_cm_property_inert(self):
        inert = [3, 7, 11, 19, 23, 31, 43, 47]
        for p in inert:
            qr = build_qr_table(p)
            ap = fast_ap_engine(p, qr)
            assert ap == 0, f"a_{p} should be 0 for CM inert prime"

    def test_known_split_primes(self):
        """
        Convention:
        a_p = p + 1 - #E(F_p)
        (LMFDB convention)
        """
        known = {
            5: -2,
            13: -6,
            17: 2,
            29: 10,
            37: 2,
        }
        for p, expected in known.items():
            qr = build_qr_table(p)
            ap = fast_ap_engine(p, qr)
            assert ap == expected, f"a_{p} = {ap}, expected {expected}"

    def test_hasse_bound(self):
        for p in range(3, 200):
            if isprime(p):
                qr = build_qr_table(p)
                ap = fast_ap_engine(p, qr)
                assert abs(ap) <= 2 * np.sqrt(p) + 1e-9


# ============================================================
# INTEGRATION TEST
# ============================================================

class TestComputePrimeData:

    def test_output_keys(self):
        data = compute_prime_data(7)
        for key in [
            "p",
            "type",
            "pisano_period",
            "a_p",
            "norm_trace",
            "weil_ratio",
        ]:
            assert key in data

    def test_inert_p7(self):
        data = compute_prime_data(7)
        assert data["p"] == 7
        assert data["type"] == "inert"
        assert data["pisano_period"] == 16
        assert data["a_p"] == 0
        assert data["norm_trace"] == 0.0
        assert data["weil_ratio"] == 0.0

    def test_split_p5(self):
        data = compute_prime_data(5)
        assert data["type"] == "split"
        assert data["a_p"] == -2
