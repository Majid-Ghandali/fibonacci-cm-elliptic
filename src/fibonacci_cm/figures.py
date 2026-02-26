"""
figures.py
==========
Publication-ready figure generation for the Fibonacci CM paper.

Produces three 600 dpi grayscale PNG figures:

    Fig1_Trace_Analysis.png
        Scatter of normalised Frobenius traces a_p/sqrt(p) vs p.
        Split primes fill [-2, 2]; inert primes cluster at 0 (CM property).
        Includes an inset showing exact-zero behaviour for small primes.

    Fig2_SatoTate.png
        Histogram of normalised traces for split primes vs the theoretical
        CM Sato--Tate density  rho(x) = 1/(pi * sqrt(4 - x^2)).

    Fig3_Convergence.png
        Cumulative inert-prime fraction converging to the Chebotarev
        density delta = 1/2.

Style
-----
Serif typeface (DejaVu Serif), inward ticks, major/minor grid, 600 dpi.
Consistent with AMS publication standards.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# ---------------------------------------------------------------------------
# Global style — applied once at import time
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family":         "serif",
    "mathtext.fontset":    "dejavuserif",
    "axes.linewidth":      0.75,
    "xtick.direction":     "in",
    "ytick.direction":     "in",
    "xtick.major.width":   0.75,
    "ytick.major.width":   0.75,
    "xtick.major.size":    4,
    "ytick.major.size":    4,
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    "xtick.minor.width":   0.5,
    "ytick.minor.width":   0.5,
    "xtick.minor.size":    2,
    "ytick.minor.size":    2,
    "xtick.labelsize":     9,
    "ytick.labelsize":     9,
    "axes.labelsize":      10,
    "legend.fontsize":     8.5,
    "legend.framealpha":   0.95,
    "legend.edgecolor":    "0.6",
    "figure.dpi":          150,
    "savefig.dpi":         600,
    "savefig.bbox":        "tight",
    "savefig.pad_inches":  0.08,
})


def generate_all(df: pd.DataFrame, output_dir: str) -> None:
    """
    Generate and save all three publication figures.

    Parameters
    ----------
    df         : pd.DataFrame   Full dataset with columns p, type,
                                norm_trace, weil_ratio, pisano_period.
    output_dir : str            Directory where PNG files are saved.
    """
    print("\n[Figures] Generating publication figures ...")
    np.random.seed(42)   # fix jitter seed for reproducibility

    os.makedirs(output_dir, exist_ok=True)

    _fig1_trace_scatter(df, output_dir)
    _fig2_sato_tate(df, output_dir)
    _fig3_chebotarev(df, output_dir)

    print("[Figures] Done.")


# ============================================================================
# Figure 1 — Frobenius trace scatter
# ============================================================================

def _fig1_trace_scatter(df: pd.DataFrame, output_dir: str) -> None:
    split  = df[df["type"] == "split"]
    inert  = df[df["type"] == "inert"]
    max_p  = int(df["p"].max())

    fig, ax = plt.subplots(figsize=(6.0, 4.0))

    ax.scatter(split["p"], split["norm_trace"],
               s=1, color="0.35", alpha=0.45, linewidths=0,
               label=r"Split primes ($p \equiv 1\ (\mathrm{mod}\ 4)$)")

    jitter = np.random.uniform(-0.04, 0.04, size=len(inert))
    ax.scatter(inert["p"], jitter,
               s=2, color="black", alpha=0.30, linewidths=0,
               label=r"Inert primes ($p \equiv 3\ (\mathrm{mod}\ 4)$, $a_p = 0$)")

    ax.axhline( 2, color="0.4", lw=0.8, ls="--", label=r"Weil bound $\pm 2$")
    ax.axhline(-2, color="0.4", lw=0.8, ls="--")
    ax.axhline( 0, color="0.55", lw=0.5, ls=":")

    # Inset
    axins = inset_axes(ax, width="35%", height="35%", loc="upper right",
                       bbox_to_anchor=(-0.02, -0.02, 1, 1),
                       bbox_transform=ax.transAxes)
    small = df[df["p"] < 500]
    sp    = small[small["type"] == "split"]
    ip    = small[small["type"] == "inert"]
    axins.scatter(sp["p"], sp["norm_trace"], s=4, color="0.35", alpha=0.6,
                  linewidths=0)
    axins.scatter(ip["p"], np.zeros(len(ip)), s=6, color="black", alpha=0.8,
                  linewidths=0)
    axins.axhline(0, color="0.4", lw=0.5, ls=":")
    axins.set_xlim(0, 500)
    axins.set_ylim(-2.3, 2.3)
    axins.set_title(r"$p \leq 500$", fontsize=7)
    axins.tick_params(labelsize=6)

    ax.set_xlim(0, max_p)
    ax.set_ylim(-2.4, 2.6)
    ax.set_xlabel(r"Prime $p$", labelpad=4)
    ax.set_ylabel(r"Normalised trace $a_p / \sqrt{p}$", labelpad=4)
    ax.set_title(
        r"Fig. 1.  Normalised Frobenius traces $a_p/\sqrt{p}$ for"
        r" $E\colon y^2 = x^3 - 4x$."
        "\n"
        rf"All {len(df):,} primes $p \leq {max_p:,}$."
        r"  Inert primes satisfy $a_p = 0$ exactly (CM property).",
        fontsize=7.8, pad=6)
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.yaxis.set_minor_locator(MultipleLocator(0.5))
    ax.legend(loc="upper left", fontsize=8.5, handlelength=1.6,
              markerscale=3)

    path = os.path.join(output_dir, "Fig1_Trace_Analysis.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  -> {path}")


# ============================================================================
# Figure 2 — CM Sato--Tate distribution
# ============================================================================

def _fig2_sato_tate(df: pd.DataFrame, output_dir: str) -> None:
    split = df[df["type"] == "split"]
    max_p = int(df["p"].max())

    fig, ax = plt.subplots(figsize=(5.5, 4.0))

    ax.hist(split["norm_trace"], bins=80, density=True,
            color="0.65", edgecolor="0.4", linewidth=0.4,
            label=rf"Empirical ({len(split):,} split primes)")

    x_th = np.linspace(-1.98, 1.98, 800)
    y_th = 1.0 / (np.pi * np.sqrt(4.0 - x_th ** 2))
    ax.plot(x_th, y_th, color="black", lw=1.6, ls="--",
            label=r"Theoretical: $\rho(x) = 1/(\pi\sqrt{4 - x^2})$")

    ax.axvline(-2, color="0.55", lw=0.7, ls=":")
    ax.axvline( 2, color="0.55", lw=0.7, ls=":")

    ax.set_xlim(-2.15, 2.15)
    ax.set_ylim(0, None)
    ax.set_xlabel(r"$x = a_p / \sqrt{p}$", labelpad=4)
    ax.set_ylabel(r"Probability density", labelpad=4)
    ax.set_title(
        r"Fig. 2.  Empirical trace distribution vs.\ CM Sato--Tate density"
        r" for $E\colon y^2 = x^3 - 4x$."
        "\n"
        r"Histogram: split primes ($p \equiv 1\ (\mathrm{mod}\ 4)$),"
        rf" $p \leq {max_p:,}$."
        "\n"
        r"Dashed: CM Sato--Tate density $\rho(x) = 1/(\pi\sqrt{4-x^2})$."
        r"  Dotted verticals: Weil bound $\pm 2$.",
        fontsize=7.8, pad=6)
    ax.xaxis.set_minor_locator(MultipleLocator(0.25))
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.legend(loc="upper center", fontsize=8.5, handlelength=1.8)

    path = os.path.join(output_dir, "Fig2_SatoTate.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  -> {path}")


# ============================================================================
# Figure 3 — Chebotarev density convergence
# ============================================================================

def _fig3_chebotarev(df: pd.DataFrame, output_dir: str) -> None:
    total     = len(df)
    cum_ratio = (df["type"] == "inert").astype(int).cumsum() / (df.index + 1)
    x_vals    = df.index.values + 1

    fig, ax = plt.subplots(figsize=(5.5, 4.0))

    ax.plot(x_vals, cum_ratio, color="black", lw=1.0, alpha=0.90,
            label=r"Cumulative inert fraction $\pi_{\mathrm{in}}(n)/n$")
    ax.axhline(0.5, color="0.4", lw=1.3, ls="--",
               label=r"Chebotarev density: $\delta = 1/2$")
    ax.fill_between(x_vals, cum_ratio, 0.5, alpha=0.10, color="0.4")

    idx_end = total - max(1, int(total * 0.005))
    offset  = max(10,  int(total * 0.025))
    ax.annotate("",
                xy=(idx_end, 0.501),
                xytext=(idx_end - offset, 0.530),
                arrowprops=dict(arrowstyle="->", color="0.35", lw=0.8))
    ax.text(idx_end - offset - 2, 0.534, r"$\to 1/2$",
            fontsize=9, ha="right", color="0.35")

    ax.set_xlim(1, total)
    ax.set_ylim(0.35, 0.70)
    ax.set_xlabel(r"Prime index $n$", labelpad=4)
    ax.set_ylabel(r"Fraction of inert primes", labelpad=4)
    ax.set_title(
        r"Fig. 3.  Convergence of the inert prime fraction to the"
        r" Chebotarev density."
        "\n"
        r"Solid: cumulative ratio $\pi_{\mathrm{in}}(n)/n$"
        r" of inert primes ($p \equiv 3\ (\mathrm{mod}\ 4)$)."
        r"  Dashed: limit $\delta = 1/2$.",
        fontsize=7.8, pad=6)
    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.yaxis.set_minor_locator(MultipleLocator(0.05))
    ax.legend(loc="upper right", fontsize=8.5, handlelength=1.6)

    path = os.path.join(output_dir, "Fig3_Convergence.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"  -> {path}")
