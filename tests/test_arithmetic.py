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
    E: y^2 = x^3 + Ax + B,  a_p = p + 1 - #E(F_p).

    Ground truth values:
        p=5:  #E(F_5)=4   => a_p = +2,  S_p = -a_p = -2
        p=13: #E(F_13)=20 => a_p = -6,  S_p = -a_p = +6
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
        known = {2: 3, 3: 8, 5: 20, 7: 16, 11: 10, 13: 28, 29: 14}
        for p, expected in known.items():
            assert get_pisano_period(p) == expected

    def test_inert_divides_2p_plus_2(self):
        for p in [7, 13, 17, 23, 37, 43, 47]:
            pi_p = get_pisano_period(p)
            assert (2 * (p + 1)) % pi_p == 0

    def test_split_divides_p_minus_1(self):
        for p in [11, 19, 29, 31, 41, 59]:
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
        """
        CM property: S_p = 0 for inert primes => a_p = -S_p = 0.
        fast_ap_engine returns S_p directly.
        """
        for p in [3, 7, 11, 19, 23, 31, 43, 47]:
            qr = build_qr_table(p)
            S_p = fast_ap_engine(p, qr)
            assert S_p == 0, f"CM property violated at p={p}: S_p={S_p}"

    def test_against_geometric_definition(self):
        """
        fast_ap_engine returns S_p = -a_p.
        So fast_ap_engine must equal -brute_force_point_count.
        """
        for p in [5, 13, 17, 29, 37, 41, 53]:
            qr    = build_qr_table(p)
            S_p   = fast_ap_engine(p, qr)
            a_p   = brute_force_point_count(p)
            assert S_p == -a_p, (
                f"p={p}: S_p={S_p}, expected -a_p={-a_p}"
            )

    def test_hasse_bound(self):
        """Hasse bound: |S_p| = |a_p| <= 2*sqrt(p) for all primes."""
        for p in range(3, 200):
            if isprime(p):
                qr  = build_qr_table(p)
                S_p = fast_ap_engine(p, qr)
                assert abs(S_p) <= 2 * np.sqrt(p) + 1e-9


# ============================================================
# INTEGRATION TESTS  (compute_prime_data applies a_p = -S_p)
# ============================================================

class TestComputePrimeData:

    def test_split_p5(self):
        """
        p=5: split prime (5 ≡ 1 mod 4).
        #E(F_5) = 4  =>  a_p = +2  =>  S_p = -2.
        compute_prime_data must store a_p = +2.
        """
        data = compute_prime_data(5)
        assert data["p"] == 5
        assert data["type"] == "split"
        assert data["pisano_period"] == 20
        assert data["a_p"] == 2                  # a_p = -S_p = -(-2) = +2

        expected_norm = 2 / np.sqrt(5)
        assert abs(data["norm_trace"] - expected_norm) < 1e-9

        expected_weil = 2 / (2 * np.sqrt(5))
        assert abs(data["weil_ratio"] - expected_weil) < 1e-9

    def test_inert_p7(self):
        """p=7: inert prime. CM property: S_p = 0 => a_p = 0."""
        data = compute_prime_data(7)
        assert data["p"] == 7
        assert data["type"] == "inert"
        assert data["pisano_period"] == 16
        assert data["a_p"] == 0
        assert data["norm_trace"] == 0.0
        assert data["weil_ratio"] == 0.0

    def test_nonzero_split_primes(self):
        """
        Split primes must have nonzero a_p.
        Guards against algorithmic collapse to zero.
        """
        for p in [5, 13, 17, 29]:
            data = compute_prime_data(p)
            assert data["a_p"] != 0, (
                f"a_p should be nonzero for split p={p}"
            )

    def test_internal_consistency(self):
        """weil_ratio = |norm_trace| / 2 for all primes."""
        for p in [5, 13, 17, 29, 37]:
            data = compute_prime_data(p)
            assert abs(data["weil_ratio"] - abs(data["norm_trace"]) / 2) < 1e-9

    def test_identity_S_p_equals_minus_a_p(self):
        """
        Explicit verification of Theorem 1.3: S_p = -a_p(E).
        Checks that fast_ap_engine (S_p) and compute_prime_data (a_p)
        are consistent with the main identity.
        """
        for p in [5, 7, 11, 13, 17, 19, 23, 29, 37]:
            qr   = build_qr_table(p)
            S_p  = fast_ap_engine(p, qr)
            data = compute_prime_data(p)
            assert S_p == -data["a_p"], (
                f"Identity S_p = -a_p violated at p={p}: "
                f"S_p={S_p}, -a_p={-data['a_p']}"
            )
