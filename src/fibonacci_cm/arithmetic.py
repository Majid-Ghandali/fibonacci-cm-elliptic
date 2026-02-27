"""
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
  - The main identity:  S_p = sum_{t in F_p} chi(t^3 - 4t) = -a_p(E)
    This is made explicit in code: fast_ap_engine returns S_p,
    and compute_prime_data applies a_p = -S_p.

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
    """
    Return the Pisano period pi(p): the smallest k such that
        F_k ≡ 0 (mod p)  and  F_{k+1} ≡ 1 (mod p).

    For inert primes (5/p) = -1, theory guarantees pi(p) = p + 1.
    """
    if p == 2:
        return 3
    if p == 5:
        return 20
    prev, curr = 0, 1
    period = 0
    while True:
        prev, curr = curr, (prev + curr) % p
        period += 1
        if prev == 0 and curr == 1:
            return period


# ============================================================================
# Quadratic residue table
# ============================================================================

@njit(fastmath=True, cache=True)
def build_qr_table(p: int) -> np.ndarray:
    """
    Build a lookup table for quadratic residues modulo p.

    table[v] = 1  if v is a non-zero QR mod p,
    table[v] = 0  otherwise (including v = 0).

    Computed in O(p) by squaring each element of (Z/pZ)*.
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
    Compute the raw Fibonacci character sum S_p for E: y^2 = x^3 - 4x.

    Evaluates the twisted character sum (Theorem 1.3):

        S_p := sum_{t in F_p} chi(t^3 - 4t)

    where chi is the Legendre symbol mod p.

    Note
    ----
    This function returns S_p (the raw character sum), NOT a_p.
    The identity is  a_p(E) = -S_p,  applied explicitly in compute_prime_data.
    This separation makes the main identity S_p = -a_p(E) visible in code.

    CM property: for inert primes p ≡ 3 (mod 4), S_p = 0 exactly,
    hence a_p = -S_p = 0.

    Returns
    -------
    int : S_p  (raw character sum; |S_p| <= 2*sqrt(p) by Hasse bound)
    """
    s_t = 0
    for t in range(p):
        val = (t * t * t - 4 * t) % p
        if val == 0:
            continue          # chi(0) = 0
        s_t += 1 if qr_table[val] == 1 else -1
    return s_t   # raw S_p; caller applies a_p = -S_p


# ============================================================================
# Per-prime computation entry point
# ============================================================================

def compute_prime_data(p: int) -> Dict:
    """
    Compute all arithmetic quantities for a single prime p.

    Applies the main identity explicitly:
        S_p  = fast_ap_engine(p, qr_table)   # raw character sum
        a_p  = -S_p                           # Theorem 1.3: a_p = -S_p

    Parameters
    ----------
    p : int
        A prime number >= 3.

    Returns
    -------
    dict with keys:
        p             : int    The prime.
        type          : str    'split' (p ≡ 1 mod 4) or 'inert' (p ≡ 3 mod 4).
        pisano_period : int    Pisano period pi(p).
        a_p           : int    Frobenius trace; 0 for all inert primes.
        norm_trace    : float  a_p / sqrt(p) in [-2, 2].
        weil_ratio    : float  |a_p| / (2*sqrt(p)) in [0, 1).
    """
    qr_table   = build_qr_table(p)
    S_p        = fast_ap_engine(p, qr_table)   # raw character sum
    a_p        = -S_p                           # Theorem 1.3: a_p(E) = -S_p
    sqrt_p     = np.sqrt(p)
    pisano_len = get_pisano_period(p)

    return {
        "p":             p,
        "type":          "split" if p % 4 == 1 else "inert",
        "pisano_period": pisano_len,
        "a_p":           a_p,
        "norm_trace":    a_p / sqrt_p,
        "weil_ratio":    abs(a_p) / (2.0 * sqrt_p),
    }
