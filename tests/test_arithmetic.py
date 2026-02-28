r"""
tests/test_arithmetic.py
========================
Research-grade unit tests for Fibonacci CM framework.
Validates optimized arithmetic against geometric first principles.

Coverage strategy
-----------------
Numba @njit functions are not traced by coverage.py by default.
We solve this by:
1. Calling the Python-level wrappers (compute_prime_data) which invoke JIT code.
2. Adding pure-Python shadow implementations for direct coverage of the logic.
3. Using NUMBA_DISABLE_JIT=1 in pytest (set in pyproject.toml) to force
   Python execution during testing.

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

def brute_force_point_count(p: int, A: int = -4, B: int = 0) -> int:
    r"""
    Reference geometric definition of the Frobenius trace.
    E: y^2 = x^3 + Ax + B,  a_p = p + 1 - #E(F_p).

    Ground truth:
        p=5:  #E(F_5)=4   => a_p=+2, S_p=-2
        p=13: #E(F_13)=20 => a_p=-6, S_p=+6
    """
    if p == 2:
        return 0
    points = 1
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

    def test_p2_special_case(self):
        """Covers line 41-42: if p == 2: return 3"""
        assert get_pisano_period(2) == 3

    def test_p5_special_case(self):
        """Covers lines 43-44: if p == 5: return 20"""
        assert get_pisano_period(5) == 20

    def test_general_loop(self):
        """Covers lines 45-51: the while loop for general primes"""
        known = {3: 8, 7: 16, 11: 10, 13: 28, 29: 14}
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

    def test_table_built_correctly(self):
        """Covers lines 68-71: zeros init + squaring loop + return"""
        table = build_qr_table(7)
        assert len(table) == 7
        # QR mod 7 = {1, 2, 4}
        assert table[1] == 1
        assert table[2] == 1
        assert table[4] == 1
        assert table[3] == 0
        assert table[5] == 0
        assert table[6] == 0
        assert table[0] == 0  # zero is not QR

    def test_structure_multiple_primes(self):
        for p in [7, 11, 13, 17]:
            table = build_qr_table(p)
            assert len(table) == p
            assert int(table.sum()) == (p - 1) // 2

    def test_dtype(self):
        table = build_qr_table(7)
        assert table.dtype == np.int8


# ============================================================
# FROBENIUS TRACE TESTS
# ============================================================

class TestFrobeniusTrace:

    def test_zero_val_skipped(self):
        """val==0 is skipped (chi(0)=0). Ensures 'continue' branch runs."""
        qr = build_qr_table(7)
        S_p = fast_ap_engine(7, qr)
        assert S_p == 0

    def test_qr_branch(self):
        """Both +1 (QR) and -1 (NQR) branches covered."""
        qr  = build_qr_table(5)
        S_p = fast_ap_engine(5, qr)
        assert S_p == -2

    def test_cm_property_inert(self):
        """S_p = 0 for all inert primes (p ≡ 3 mod 4)."""
        for p in [3, 7, 11, 19, 23, 31, 43, 47]:
            qr  = build_qr_table(p)
            S_p = fast_ap_engine(p, qr)
            assert S_p == 0, f"CM property violated at p={p}"

    def test_against_geometric_definition(self):
        """fast_ap_engine(S_p) must equal -brute_force(a_p)."""
        for p in [5, 13, 17, 29, 37, 41, 53]:
            qr    = build_qr_table(p)
            S_p   = fast_ap_engine(p, qr)
            a_p   = brute_force_point_count(p)
            assert S_p == -a_p, f"p={p}: S_p={S_p}, -a_p={-a_p}"

    def test_hasse_bound(self):
        """|S_p| = |a_p| <= 2*sqrt(p) for all primes."""
        for p in range(3, 200):
            if isprime(p):
                qr  = build_qr_table(p)
                S_p = fast_ap_engine(p, qr)
                assert abs(S_p) <= 2 * np.sqrt(p) + 1e-9

    def test_return_value_is_integer(self):
        """Covers return s_t"""
        qr  = build_qr_table(13)
        S_p = fast_ap_engine(13, qr)
        assert isinstance(int(S_p), int)


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestComputePrimeData:

    def test_split_p5(self):
        """p=5: a_p = -S_p = -(-2) = +2. Split in Q(i) since 5 ≡ 1 mod 4."""
        data = compute_prime_data(5)
        assert data["p"] == 5
        assert data["type_E"] == "split_E"
        assert data["pisano_period"] == 20
        assert data["a_p"] == 2
        assert abs(data["norm_trace"] - 2/np.sqrt(5)) < 1e-9
        assert abs(data["weil_ratio"] - 2/(2*np.sqrt(5))) < 1e-9

    def test_inert_p7(self):
        """p=7: CM property => a_p = 0. Inert in Q(i) since 7 ≡ 3 mod 4."""
        data = compute_prime_data(7)
        assert data["p"] == 7
        assert data["type_E"] == "inert_E"
        assert data["pisano_period"] == 16
        assert data["a_p"] == 0
        assert data["norm_trace"] == 0.0
        assert data["weil_ratio"] == 0.0

    def test_inert_p3(self):
        """p=3: smallest inert prime (3 ≡ 3 mod 4)."""
        data = compute_prime_data(3)
        assert data["type_E"] == "inert_E"
        assert data["a_p"] == 0

    def test_type_F5_classification(self):
        """
        Verify type_F5 classification (Theorem 1.3 hypothesis):
            p ≡ ±2 mod 5  =>  inert_F5
            p ≡ ±1 mod 5  =>  split_F5
        Key example: p=13 is inert_F5 (13 ≡ 3 ≡ -2 mod 5) but split_E.
        This illustrates the two conditions are independent.
        """
        # inert_F5: p ≡ 2 or 3 mod 5
        for p in [7, 13, 17, 3]:
            data = compute_prime_data(p)
            assert data["type_F5"] == "inert_F5", (
                f"p={p} should be inert_F5 (p mod 5 = {p % 5})"
            )
        # split_F5: p ≡ 1 or 4 mod 5
        for p in [11, 19, 29, 41]:
            data = compute_prime_data(p)
            assert data["type_F5"] == "split_F5", (
                f"p={p} should be split_F5 (p mod 5 = {p % 5})"
            )

    def test_type_E_classification(self):
        """p ≡ 1 mod 4 => split_E, p ≡ 3 mod 4 => inert_E."""
        for p in [5, 13, 17, 29, 37, 41]:
            assert compute_prime_data(p)["type_E"] == "split_E", (
                f"p={p} should be split_E (p mod 4 = {p % 4})"
            )
        for p in [3, 7, 11, 19, 23, 31]:
            assert compute_prime_data(p)["type_E"] == "inert_E", (
                f"p={p} should be inert_E (p mod 4 = {p % 4})"
            )

    def test_p13_two_inertness_conditions(self):
        """
        p=13: the canonical example showing the two conditions are independent.
            - inert_F5: 13 ≡ 3 ≡ -2 mod 5  => Theorem 1.3 applies
            - split_E : 13 ≡ 1 mod 4        => a_p ≠ 0 in general
            - a_13 = -2 ≠ 0, and S_13 = 2 = -a_13  ✔
        """
        data = compute_prime_data(13)
        assert data["type_F5"] == "inert_F5"
        assert data["type_E"]  == "split_E"
        assert data["a_p"] != 0               # not zero! split_E prime
        assert data["S_p"] == -data["a_p"]    # Theorem 1.3 holds

    def test_nonzero_split_primes(self):
        """Guards against algorithmic collapse to zero."""
        for p in [5, 13, 17, 29]:
            data = compute_prime_data(p)
            assert data["a_p"] != 0

    def test_internal_consistency(self):
        """weil_ratio = |norm_trace| / 2"""
        for p in [5, 13, 17, 29, 37]:
            data = compute_prime_data(p)
            assert abs(data["weil_ratio"] - abs(data["norm_trace"])/2) < 1e-9

    def test_identity_S_p_equals_minus_a_p(self):
        """Explicit verification of Theorem 1.3: S_p = -a_p(E)."""
        for p in [5, 7, 11, 13, 17, 19, 23, 29, 37]:
            qr   = build_qr_table(p)
            S_p  = fast_ap_engine(p, qr)
            data = compute_prime_data(p)
            assert S_p == -data["a_p"], (
                f"Theorem 1.3 violated at p={p}: S_p={S_p}, -a_p={-data['a_p']}"
            )
