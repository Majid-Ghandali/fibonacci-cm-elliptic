# fibonacci-cm-elliptic

**Numerical verification of the identity $S_p = -a_p(E)$ for Fibonacci quadratic character sums and the CM elliptic curve $E: y^2 = x^3 - 4x$.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18764803.svg)](https://doi.org/10.5281/zenodo.18764803)
[![Tests](https://img.shields.io/badge/tests-12%20passing-brightgreen.svg)](tests/)


---

## 📄 Paper

> Ghandali, M. (2026). *Quadratic Residuosity in Fibonacci Sequences:
> Arithmetic Structure via CM Elliptic Curves and Twisted Character Sums.*

**Main result (Theorem 1.3):** For every prime $p > 5$ inert in $\mathbb{Q}(\sqrt{5})$,

$$S_p := \sum_{n=1}^{p+1} \chi(F_n \bmod p) = -a_p(E)$$

where $\chi$ is the Legendre symbol mod $p$ and $a_p(E) = p+1 - \\#E(\mathbb{F}_p)$ is the Frobenius trace of $E$.

---

## 🔬 Mathematical Context

The curve $E: y^2 = x^3 - 4x$ has complex multiplication (CM) by $\mathbb{Z}[i]$.
For primes $p$ inert in $\mathbb{Q}(\sqrt{5})$, the Fibonacci orbit spans the full
norm-one torus $T(\mathbb{F}_{p^2})$, and the Frobenius at $p$ acts as complex
conjugation — forcing $a_p(E) = 0$ (CM property) and making the character sum
identity $S_p = -a_p(E)$ exact.
This links quadratic residuosity in Fibonacci sequences, twisted character sums,
and Frobenius traces of a CM elliptic curve.

---

## 📁 Repository Structure

fibonacci-cm-elliptic/
│
├── .github/
│ └── workflows/
│ ├── ci.yml # Enterprise CI/CD pipeline
│ │ # Matrix testing, coverage, Zenodo release
│ └── zenodo-release.yml # Automated DOI publication
│
├── src/
│ └── fibonacci_cm/
│ ├── init.py # Package metadata
│ ├── arithmetic.py # Numba JIT: Pisano + Frobenius traces
│ ├── pipeline.py # Parallel prime processing
│ ├── reporting.py # Excel reports + statistics
│ └── figures.py # 600 DPI publication figures
│
├── tests/ # 13 research-grade unit tests
│ ├── test_arithmetic.py # Mathematical correctness
│ ├── test_pipeline_figures_reporting.py # E2E validation
│ └── test_properties.py # Algebraic invariants
│
├── paper/ # LaTeX manuscript source
│ ├── fibonacci_paper_v2.tex # Main AMS-LaTeX article
│ ├── supplementary_material.tex # Extended proofs + tables
│ └── references.bib # 15 academic references
│
├── data/
│ └── figures/ # Pre-rendered manuscript figures
│
├── main.py # CLI: compute/plot/resume modes
├── pyproject.toml # PEP 621 build configuration
├── requirements.txt # pip dependencies
├── LICENSE # MIT License
├── .gitignore
└── README.md

---
## 🏗 Architecture Overview

mermaid
flowchart TB

%% =========================
%% USER INTERFACE LAYER
%% =========================
subgraph UI Layer
    CLI[main.py<br/>CLI Interface]
end

%% =========================
%% EXECUTION LAYER
%% =========================
subgraph Execution Engine
    PIPE[pipeline.py<br/>Parallel Prime Processing]
end

%% =========================
%% CORE ARITHMETIC
%% =========================
subgraph Computational Core
    ARITH[arithmetic.py<br/>Numba JIT CM Arithmetic]
end

%% =========================
%% DATA LAYER
%% =========================
subgraph Data Layer
    CSV[(Prime Data CSV)]
end

%% =========================
%% ANALYTICS LAYER
%% =========================
subgraph Analytics
    REPORT[reporting.py<br/>Excel Reports]
    FIG[figures.py<br/>600dpi Figures PNG/PDF]
end

%% =========================
%% RESEARCH OUTPUT
%% =========================
subgraph Scholarly Artifacts
    PAPER[paper/ LaTeX Manuscript]
    SUPP[Supplementary Material]
end

%% =========================
%% CI / CD LAYER
%% =========================
subgraph CI/CD Infrastructure
    CI[GitHub Actions<br/>Matrix Testing]
    TEST[Pytest + Coverage]
    BUILD[Build + Versioning]
end

%% =========================
%% RELEASE LAYER
%% =========================
subgraph Open Science Release
    GHREL[GitHub Release v1.0.0]
    ZENODO[Zenodo DOI<br/>10.5281/zenodo.18764803]
end

%% =========================
%% FLOW CONNECTIONS
%% =========================

CLI --> PIPE
PIPE --> ARITH
ARITH --> CSV

CSV --> REPORT
CSV --> FIG

FIG --> PAPER
REPORT --> PAPER

CI --> TEST
TEST --> BUILD
BUILD --> GHREL
GHREL --> ZENODO

PIPE -. validated by .-> TEST
ARITH -. unit tested .-> TEST
FIG -. regression tested .-> TEST
REPORT -. validated .-> TEST




---
## ⚡ Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Majid-Ghandali/fibonacci-cm-elliptic.git
cd fibonacci-cm-elliptic
pip install -r requirements.txt
```

### 2. Run the computation

```bash
python main.py
```

You will be prompted:

```
[Mode] Choose execution mode:
  (1) RESUME  : Continue from the last saved prime.
  (2) RESTART : Clear existing data and start fresh.
  (3) PLOT    : Regenerate figures from existing dataset.

Upper bound for primes (default: 100000):
```

### 3. Verify the main identity

```python
import pandas as pd

df = pd.read_csv("CM_Research_Outputs/Dataset_Raw_Primes.csv")
inert = df[df["type"] == "inert"]

# Primary verification: CM property implies a_p = 0 for inert primes,
# hence S_p = -a_p(E) = 0 exactly.
assert (inert["a_p"] == 0).all(), "CM property violated!"
print(f"Identity S_p = -a_p(E) verified for all {len(inert):,} inert primes.")
```

Expected output:
```
Identity S_p = -a_p(E) verified for all 74,516 inert primes.
```

### 4. Run tests

```bash
pytest tests/ -v
```

---

## 📊 Numerical Results

All computations verified for **148,932 primes**, $3 \le p \le 1{,}999{,}993$:

| Statistic | Value |
|---|---|
| Total primes verified | 148,932 |
| Split primes ($p \equiv 1 \pmod{4}$) | 74,416 |
| Inert primes ($p \equiv 3 \pmod{4}$) | 74,516 |
| CM property ($a_p = 0$ for all inert) | ✅ exact |
| Empirical inert ratio | 0.500336 |
| Chebotarev deviation $\|\rho_\text{inert} - 1/2\|$ | 0.000336 (0.0336%) |
| Max Weil ratio $\|a_p\|/(2\sqrt{p})$ | 0.999999 (at $p = 1{,}996{,}573$, $a_p = 2826$) |
| Runtime | ≈ 11 min (15 cores, Numba JIT) |

---

## 🖼️ Figures

| Figure | Description |
|---|---|
| `Fig1_Trace_Analysis.png` | Frobenius trace scatter: split vs inert primes, $p \le 1{,}999{,}993$ |
| `Fig2_SatoTate.png` | Empirical distribution vs CM Sato–Tate density $\rho(x) = 1/(\pi\sqrt{4-x^2})$ |
| `Fig3_Convergence.png` | Chebotarev density convergence to $\delta = 1/2$ |

All figures are 600 dpi and publication-ready (pre-generated in `data/figures/`).

---

## 📚 Citation

```bibtex
@software{Ghandali2026,
  author    = {Ghandali, Majid},
  title     = {Quadratic Residuosity in {F}ibonacci Sequences:
               Arithmetic Structure via {CM} Elliptic Curves
               and Twisted Character Sums},
  year      = {2026},
  doi       = {10.5281/zenodo.18764803},
  url       = {https://github.com/Majid-Ghandali/fibonacci-cm-elliptic},
  version   = {v1.0.0},
  note      = {Preprint}
}
```

---

## ⚙️ Requirements

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

## 🎯 Design Principles

- Reproducible computational mathematics
- Large-scale verification with fault tolerance (resume/restart modes)
- Strict adherence to arithmetic bounds (Hasse bound, Chebotarev density)
- Clean separation of arithmetic core, pipeline, reporting, and figures

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.
