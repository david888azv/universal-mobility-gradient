# =============================================================================
# Author:      David L. Azevedo
# Affiliation: Instituto de Física, Universidade de Brasília (UnB), Brazil
# E-mail:      david888azv@unb.br
# ORCID:       0000-0002-3456-554X
# Project:     Universal Phenomenology, Divergent Mechanism — A Behavioural
#              Gradient of Mobility from Foraging to Commute
#              (Azevedo 2026, submitted to Nature)
# Repository:  https://github.com/david888azv/universal-mobility-gradient
# Licence:     CC BY 4.0
# =============================================================================

"""
Bloco C — Alessandretti et al. 2020 (Nature 587:402): hierarchical containers.

Versão simplificada para teste cross-species:
- Grid multi-escala (100m, 500m, 2km, 10km, 50km).
- Para cada escala l, P(Δr | dentro do contêiner l) = distribuição de
  step-lengths *intra-célula*; se Alessandretti vale, esperamos lognormal
  por nível (não power-law).
- A power-law agregada vem da mistura de lognormais entre níveis.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from _helpers import load_data, per_indiv, log_bin_pdf, fig_dir, LABEL, SPECIES

OUT = fig_dir("blocoC")

print("[Bloco C] loading data ...")
df = load_data()
INDIVIDUALS = sorted(df["individual-local-identifier"].unique())

LEVELS_M = [100, 500, 2000, 10000, 50000]  # cell sizes per level


def compute_intra_cell_steps():
    """Para cada nível l, retorna lista de Δr entre fixes consecutivos
    *que caem na mesma célula de tamanho l_m*. Esses são os steps "dentro
    do contêiner" do nível l."""
    intra = {l: [] for l in LEVELS_M}
    for ind, sub in per_indiv(df):
        x = sub["x"].values; y = sub["y"].values
        dx = np.diff(x); dy = np.diff(y)
        dr = np.sqrt(dx * dx + dy * dy)
        for l in LEVELS_M:
            cx = (x // l).astype(int); cy = (y // l).astype(int)
            same = (cx[:-1] == cx[1:]) & (cy[:-1] == cy[1:])
            valid = same & (dr > 0)
            intra[l].extend(dr[valid].tolist())
    return {l: np.array(v) for l, v in intra.items()}


def figC1():
    """P(Δr) dentro de cada contêiner. Testa lognormalidade vs power-law."""
    intra = compute_intra_cell_steps()

    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    cmap = plt.get_cmap("viridis")
    colors = [cmap(i / (len(LEVELS_M) - 1)) for i in range(len(LEVELS_M))]

    print("\n[Fig C1] Δr intra-cell — teste de lognormalidade:")
    print(f"        {'level (m)':>10s} {'N':>9s} {'mean':>10s} {'median':>10s} "
          f"{'KS lognormal':>14s}")

    for l, col in zip(LEVELS_M, colors):
        v = intra[l]
        v = v[v > 0]
        if len(v) < 50:
            continue
        centers, pdf = log_bin_pdf(v, n_bins=35)
        ax.loglog(centers, pdf, "o-", color=col, ms=4, lw=0.8,
                  label=f"contêiner {l} m  (n={len(v)})")

        # Lognormal MLE: fit log(v) ~ N(mu, sigma)
        log_v = np.log(v)
        mu_ln = log_v.mean(); sigma_ln = log_v.std()
        # KS test against lognormal CDF
        sorted_v = np.sort(v)
        emp_cdf = np.arange(1, len(v) + 1) / len(v)
        theo_cdf = stats.norm.cdf((np.log(sorted_v) - mu_ln) / sigma_ln)
        ks = np.max(np.abs(emp_cdf - theo_cdf))
        print(f"        {l:>10d} {len(v):>9d} {v.mean():>10.1f} "
              f"{np.median(v):>10.1f} {ks:>14.3f}")

    ax.set_xlabel(r"$\Delta r$ intra-contêiner (m)")
    ax.set_ylabel(r"$P(\Delta r)$")
    ax.set_title("Fig. C1 — P(Δr) dentro de contêineres por escala")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "figC1_intra_container.png", dpi=150)
    plt.close(fig)


def figC2():
    """Tamanho típico do contêiner por nível: para cada cell visitada por
    indivíduo, computa o "diâmetro" como percentil 95 das distâncias entre
    fixes dentro dela. Plota distribuição entre cells."""
    fig, ax = plt.subplots(figsize=(7, 5))
    cmap = plt.get_cmap("viridis")
    colors = [cmap(i / (len(LEVELS_M) - 1)) for i in range(len(LEVELS_M))]

    print("\n[Fig C2] tamanho efetivo do contêiner por nível "
          "(p95 da extensão intra-cell):")
    print(f"        {'level':>10s} {'N cells':>10s} "
          f"{'median p95(m)':>15s} {'IQR (m)':>15s}")

    for l, col in zip(LEVELS_M, colors):
        diams = []
        for ind, sub in per_indiv(df):
            x = sub["x"].values; y = sub["y"].values
            cx = (x // l).astype(int); cy = (y // l).astype(int)
            cells = pd.DataFrame({"cx": cx, "cy": cy, "x": x, "y": y})
            for (_, _), grp in cells.groupby(["cx", "cy"]):
                if len(grp) < 5:
                    continue
                xc, yc = grp["x"].mean(), grp["y"].mean()
                d = np.sqrt((grp["x"] - xc) ** 2 + (grp["y"] - yc) ** 2)
                diams.append(np.percentile(d, 95))
        diams = np.array(diams)
        diams = diams[diams > 0]
        if len(diams) > 5:
            sd = np.sort(diams)
            ccdf = 1 - np.arange(len(sd)) / len(sd)
            ax.loglog(sd, ccdf, "-", color=col, lw=1.5,
                      label=f"nível {l} m (n={len(diams)})")
            print(f"        {l:>10d} {len(diams):>10d} "
                  f"{np.median(diams):>15.1f} "
                  f"{np.percentile(diams, 75) - np.percentile(diams, 25):>15.1f}")

    ax.set_xlabel("diâmetro efetivo (p95 das distâncias intra-cell, m)")
    ax.set_ylabel("CCDF")
    ax.set_title("Fig. C2 — Tamanho efetivo do contêiner por nível")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "figC2_container_sizes.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    figC1()
    figC2()
    print(f"\n[Bloco C] figures em {OUT}")
