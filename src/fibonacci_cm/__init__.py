"""
fibonacci_cm
============
Numerical verification of the identity  S_p = -a_p(E)  for the CM
elliptic curve  E : y^2 = x^3 - 4x  and Fibonacci character sums.

Reference
---------
Ghandali, M. (2025). Quadratic Residuosity in Fibonacci Sequences:
Arithmetic Structure via CM Elliptic Curves and Twisted Character Sums.

Modules
-------
arithmetic   : Pisano period, Legendre symbol, Frobenius trace (Numba JIT)
pipeline     : Parallel prime processing and CSV streaming
reporting    : Excel report generation and console summary
figures      : Publication-ready figure generation (600 dpi)
"""

__version__ = "1.0.0"
__author__  = "Majid Ghandali"
__email__   = "majid.ghandali@gmail.com"
