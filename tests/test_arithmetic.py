r"""
tests/test_arithmetic.py
========================
Research-grade unit tests for Fibonacci CM framework.
Validates optimized arithmetic against geometric first principles.

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
# GEOMETRIC REFERENCE ENGINE (Ground Truth)
# ============================================================

def brute_force_point_count(p, A=-4, B=0):
    r"""
    Reference geometric definition of the Frobenius trace.
    E: y^2 = x^3 + Ax + B
    Returns a_p = p + 1 - #E(F_p)
    """
    if p == 2:
        return 0

    points = 1  # point at infinity
    qr_table = build_qr_table(p)

    for x in range(p):
        rhs = (x**3 + A*x + B) % p
        if rhs == 0:
            points += 1
        elif qr_table[rhs] == 1:
            points += 2

    return p + 1 - points


# ============================================================
# PISANO PERIOD TESTS
# ============================================================

class TestPisanoPeriod:

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
            assert get_pisano_period(p) == expected

    def test_inert_divides_2p_plus_2(self):
        inert = [7, 13, 17, 23, 37, 43, 47]
        for p in inert:
            pi_p = get_pisano_period(p)
            assert (2 * (p + 1)) % pi_p == 0

    def test_split_divides_p_minus_1(self):
        split = [11, 19, 29, 31, 41, 59]
        for p in split:
            pi_p = get_pisano_period(p)
            assert (p - 1) % pi_p == 0


# ============================================================
# QUADRATIC RESIDUE TABLE TESTS
# ============================================================

class TestQRTable:

    def test_structure(self):
        for p in [7, 11, 13, 17]:
            table = build_qr_table(p)
            assert len(table) == p
            assert table.sum() == (p - 1) // 2


# ============================================================
# FROBENIUS TRACE TESTS
# ============================================================

class TestFrobeniusTrace:

    def test_cm_property_inert(self):
        inert_cm = [3, 7, 11, 19, 23, 31, 43, 47]
        for p in inert_cm:
            qr = build_qr_table(p)
            ap = fast_ap_engine(p, qr)
            assert ap == 0

    def test_against_geometric_definition(self):
        test_primes = [5, 13, 17, 29, 37, 41, 53]
        for p in test_primes:
            qr = build_qr_table(p)
            ap_fast = fast_ap_engine(p, qr)
            ap_ref = brute_force_point_count(p)
            assert ap_fast == ap_ref

    def test_hasse_bound(self):
        for p in range(3, 200):
            if isprime(p):
                qr = build_qr_table(p)
                ap = fast_ap_engine(p, qr)
                assert abs(ap) <= 2 * np.sqrt(p) + 1e-9


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestComputePrimeData:

    def test_split_p5(self):
        data = compute_prime_data(5)

        assert data["p"] == 5
        assert data["type"] == "split"
        assert data["pisano_period"] == 20
        assert data["a_p"] == -2

        expected_norm = -2 / np.sqrt(5)
        assert abs(data["norm_trace"] - expected_norm) < 1e-9

        expected_weil = abs(-2) / (2 * np.sqrt(5))
        assert abs(data["weil_ratio"] - expected_weil) < 1e-9

    def test_inert_p7(self):
        data = compute_prime_data(7)

        assert data["p"] == 7
        assert data["type"] == "inert"
        assert data["pisano_period"] == 16
        assert data["a_p"] == 0
        assert data["norm_trace"] == 0.0
        assert data["weil_ratio"] == 0.0

    def test_nonzero_primes_not_all_zero(self):
        split_primes = [5, 13, 17, 29]
        for p in split_primes:
            data = compute_prime_data(p)
            assert data["a_p"] != 0

    def test_internal_consistency(self):
        for p in [5, 13, 17, 29, 37]:
            data = compute_prime_data(p)
            assert abs(data["weil_ratio"] - abs(data["norm_trace"]) / 2) < 1e-9
