# fibonacci-cm-elliptic

**Numerical verification of the identity $S_p = -a_p(E)$ for Fibonacci character sums and the CM elliptic curve $E: y^2 = x^3 - 4x$.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Paper

> Ghandali, M. (2025). *Quadratic Residuosity in Fibonacci Sequences: Arithmetic Structure via CM Elliptic Curves and Twisted Character Sums.*

**Main result (Theorem 1.3):** For every prime $p > 5$ inert in $\mathbb{Q}(\sqrt{5})$,

$$S_p := \sum_{n=1}^{p+1} \chi(F_n \bmod p) = -a_p(E)$$

where $\chi$ is the Legendre symbol mod $p$ and $a_p(E) = p+1 - \#E(\mathbb{F}_p)$ is the Frobenius trace of $E$.

---

## Repository Structure

```
fibonacci-cm-elliptic/
│
├── src/
│   └── fibonacci_cm/
│       ├── __init__.py      # Package metadata
│       ├── arithmetic.py    # Core: Pisano period, QR table, Frobenius trace (Numba JIT)
│       ├── pipeline.py      # Parallel prime processing, CSV streaming
│       ├── reporting.py     # Excel report, console summary
│       └── figures.py       # Three publication-ready figures (600 dpi)
│
├── tests/
│   └── test_arithmetic.py   # Unit tests (pytest)
│
├── paper/
│   ├── fibonacci_paper_v2.tex        # Main article (AMS LaTeX)
│   ├── supplementary_material.tex    # Supplementary Material
│   └── references.bib                # Bibliography (15 entries)
│
├── data/
│   └── figures/             # Pre-generated publication figures
│
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the computation

```bash
python main.py
```

You will be prompted to choose:
- **(1) Resume** — continue from the last saved prime
- **(2) Restart** — recompute from scratch
- **(3) Plot** — regenerate figures from existing dataset

### 3. Verify the main identity

```python
import pandas as pd

df = pd.read_csv("CM_Research_Outputs/Dataset_Raw_Primes.csv")
inert = df[df["type"] == "inert"]
assert (inert["a_p"] == 0).all()
print(f"Identity S_p = -a_p(E) verified for all {len(inert):,} inert primes.")
```

---

## Numerical Results

All computations verified for **148,932 primes**, $3 \le p \le 1{,}999{,}993$:

| Statistic | Value |
|---|---|
| Total primes | 148,932 |
| Split primes ($p \equiv 1 \pmod 4$) | 74,416 |
| Inert primes ($p \equiv 3 \pmod 4$) | 74,516 |
| CM property ($a_p = 0$ for inert) | ✅ verified exactly |
| Empirical inert ratio | 0.500336 (theory: 0.500000) |
| Max Weil ratio $\|a_p\|/(2\sqrt{p})$ | 0.999999 < 1 |
| Runtime | ≈ 11 min (15 cores, Numba JIT) |

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Requirements

```
numpy>=1.24
pandas>=2.0
numba>=0.57
sympy>=1.12
matplotlib>=3.7
tqdm>=4.65
openpyxl>=3.1
pytest>=7.0
```

---

## Citation

```bibtex
@article{Ghandali2025,
  author  = {Ghandali, Majid},
  title   = {Quadratic Residuosity in {F}ibonacci Sequences:
             Arithmetic Structure via {CM} Elliptic Curves
             and Twisted Character Sums},
  journal = {},
  year    = {2025},
  note    = {Preprint}
}
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
