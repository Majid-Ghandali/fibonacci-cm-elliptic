r"""
arithmetic.py
=============
Core number-theoretic computations for the Fibonacci CM project.

All performance-critical functions are JIT-compiled via Numba for
efficient evaluation over large prime ranges.

Mathematical background
-----------------------
For a prime p inert in Q(sqrt(5)), i.e. (5/p) = -1:
  - The Pisano period satisfies pi(p) = p + 1   [Wall 1960]
  - The Frobenius trace of E: y^2 = x^3 - 4x satisfies a_p = 0
    when p ≡ 3 (mod 4)  (CM property, Silverman 1994)
  - The main identity:  S_p = sum_{n=1}^{p+1} chi(F_n mod p) = -a_p(E)

References
----------
Wall (1960), Silverman (1994, 2009), Deligne (1974), Katz (1988).
"""

import numpy as np
from numba import njit
from typing import Dict


# ============================================================================
# Pisano period
# ============================================================================

@njit(fastmath=True, cache=True)
def get_pisano_period(p: int) -> int:
    r"""
    Return the Pisano period pi(p).

    The Pisano period is the smallest positive integer k such that
        F_k ≡ 0 (mod p)  and  F_{k+1} ≡ 1 (mod p).

    For inert primes (5/p) = -1, theory guarantees pi(p) = p + 1.

    Parameters
    ----------
    p : int
        A prime number >= 2.

    Returns
    -------
    int
        The Pisano period pi(p).
    """
    if p == 2:
        return 3
    if p == 5:
        return 20
    prev, curr = 0, 1
    for period in range(1, p * p + 1):
        prev, curr = curr, (prev + curr) % p
        if prev == 0 and curr == 1:
            return period
    return 0


# ============================================================================
# Quadratic residue table
# ============================================================================

@njit(fastmath=True, cache=True)
def build_qr_table(p: int) -> np.ndarray:
    r"""
    Build a lookup table for quadratic residues modulo p.

    table[v] = 1  if v is a non-zero quadratic residue mod p,
    table[v] = 0  otherwise (including v = 0).

    Computed in O(p) by squaring each element of (Z/pZ)*.
    This avoids repeated Euler-criterion evaluations during the
    character sum computation.

    Parameters
    ----------
    p : int
        An odd prime.

    Returns
    -------
    np.ndarray of shape (p,) and dtype int8.
    """
    table = np.zeros(p, dtype=np.int8)
    for x in range(1, p):
        table[(x * x) % p] = 1
    return table


# ============================================================================ 
# Frobenius trace via character sum identity
# ============================================================================

@njit(fastmath=True, cache=True)
def fast_ap_engine(p: int, qr_table: np.ndarray) -> int:
    """
    Compute the character sum S_p = sum_{t in F_p} chi(t^3 - 4t)

    Returns the raw sum S_p (not yet signed as Frobenius trace).
    """
    s_t = 0
    for t in range(p):
        val = (t * t * t - 4 * t) % p
        if val == 0:
            continue
        s_t += 1 if qr_table[val] == 1 else -1

    return s_t  
# ============================================================================ 
# Per-prime computation entry point
# ============================================================================

def compute_prime_data(p: int) -> Dict:
    """
    Compute all arithmetic quantities for a single prime p.
    """
    qr_table = build_qr_table(p)
    S_p      = fast_ap_engine(p, qr_table)  # raw character sum

    # Frobenius trace according to Theorem 1.3
    a_p = -S_p

    sqrt_p = np.sqrt(p)
    pisano_len = get_pisano_period(p)

    return {
        "p":             p,
        "type":          "split" if p % 4 == 1 else "inert",
        "pisano_period": pisano_len,
        "a_p":           a_p,
        "norm_trace":    a_p / sqrt_p,
        "weil_ratio":    abs(a_p) / (2.0 * sqrt_p),
    }
