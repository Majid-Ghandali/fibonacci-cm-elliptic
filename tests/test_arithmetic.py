"""
tests/test_arithmetic.py
========================
Unit tests for the arithmetic module.

Run with:  pytest tests/
"""

import numpy as np
import pytest
from fibonacci_cm.arithmetic import (
    get_pisano_period,
    build_qr_table,
    fast_ap_engine,
    compute_prime_data,
)


class TestPisanoPeriod:
    """Verify pi(p) = p+1 for inert primes and known values."""

    def test_inert_primes_pisano_equals_p_plus_1(self):
        """For all inert primes (5/p)=-1, pi(p) must equal p+1."""
        inert_primes = [7, 13, 17, 23, 37, 43, 47, 53, 67, 73]
        for p in inert_primes:
            assert get_pisano_period(p) == p + 1, \
                f"pi({p}) = {get_pisano_period(p)}, expected {p+1}"

    def test_known_values(self):
        """Check against a table of known Pisano periods."""
        known = {2: 3, 3: 8, 5: 20, 11: 10, 29: 14}
        for p, expected in known.items():
            assert get_pisano_period(p) == expected, \
                f"pi({p}) = {get_pisano_period(p)}, expected {expected}"


class TestQRTable:
    """Verify the quadratic residue lookup table."""

    def test_qr_table_p7(self):
        """QR mod 7 = {1, 2, 4}."""
        table = build_qr_table(7)
        assert table[1] == 1
        assert table[2] == 1
        assert table[4] == 1
        assert table[3] == 0
        assert table[5] == 0
        assert table[6] == 0
        assert table[0] == 0

    def test_qr_table_size(self):
        for p in [7, 11, 13, 17]:
            table = build_qr_table(p)
            assert len(table) == p
            # Exactly (p-1)/2 non-zero QRs for odd prime p
            assert table.sum() == (p - 1) // 2


class TestFrobeniusTrace:
    """Verify a_p(E) for known small primes."""

    def test_cm_property_inert(self):
        """For inert primes p ≡ 3 (mod 4), a_p must be 0."""
        inert = [3, 7, 11, 19, 23, 31, 43, 47, 59, 67]
        for p in inert:
            qr = build_qr_table(p)
            ap = fast_ap_engine(p, qr)
            assert ap == 0, f"a_{p} = {ap}, expected 0 (CM property)"

    def test_known_split_primes(self):
        """Check a_p for a few split primes against hand-computed values."""
        # E: y^2 = x^3 - 4x
        # These values can be verified with Sage or LMFDB
        known = {5: 2, 13: 6, 17: -2, 29: -10, 37: -2}
        for p, expected in known.items():
            qr = build_qr_table(p)
            ap = fast_ap_engine(p, qr)
            assert ap == expected, f"a_{p} = {ap}, expected {expected}"

    def test_hasse_bound(self):
        """Verify |a_p| <= 2*sqrt(p) for all primes up to 200."""
        from sympy import isprime
        for p in range(3, 200):
            if isprime(p):
                qr = build_qr_table(p)
                ap = fast_ap_engine(p, qr)
                assert abs(ap) <= 2 * np.sqrt(p) + 1e-9, \
                    f"Hasse bound violated: |a_{p}| = {abs(ap)} > 2*sqrt({p})"


class TestComputePrimeData:
    """Integration test for compute_prime_data."""

    def test_output_keys(self):
        data = compute_prime_data(7)
        for key in ["p", "type", "pisano_period", "a_p", "norm_trace", "weil_ratio"]:
            assert key in data

    def test_inert_p7(self):
        data = compute_prime_data(7)
        assert data["p"] == 7
        assert data["type"] == "inert"       # 7 ≡ 3 (mod 4)
        assert data["pisano_period"] == 8    # pi(7) = 8 = 7+1
        assert data["a_p"] == 0             # CM property
        assert data["norm_trace"] == 0.0
        assert data["weil_ratio"] == 0.0

    def test_split_p5(self):
        data = compute_prime_data(5)
        assert data["type"] == "split"      # 5 ≡ 1 (mod 4)
        assert data["a_p"] == 2
