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
Bloco D — Schläpfer et al. 2021 (Nature 593:522): lei universal de visitação.

ρ_i(r, f) = μ_i / (rf)^η, com η ≈ 2 em humanos.

Ajuste para 14 elefantes Kruger:
- Locais i = células de grid (1 km).
- Para cada par (cell_alvo, cell_origem) entre os 14 indivíduos:
  - r = distância entre origem e alvo
  - f = nº de visitas do indivíduo (com home = cell modal) ao alvo
  - ρ_i(r, f) = nº de visitantes / area(r) bin
- Plot ρ vs r·f e ajusta η.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from _helpers import load_data, per_indiv, fig_dir, LABEL, SPECIES

OUT = fig_dir("blocoD")

print("[Bloco D] loading data ...")
df = load_data()
INDIVIDUALS = sorted(df["individual-local-identifier"].unique())

GRID_M = 1000  # 1 km grid for "locations"
T_PERIOD_DAYS = 120  # Schläpfer 2021 usa T = 4 meses para Boston


def figD1():
    """Calcula a lei de visitação ρ(r, f) e ajusta η.

    Para cada indivíduo:
    - identifica home cell (cell mais visitada)
    - cell home → distância r até qualquer cell alvo
    - frequência f = nº de "ocorrências" no alvo dividido por nº de períodos T
    Para cada cell alvo i, agregamos ρ_i(r, f) = quantos visitantes (de
    qualquer home) com (r, f) na vizinhança. ρ é normalizado por anel
    A(r) = 2π r δr.
    """
    # 1. Build per-individual cell sequences and home cell
    per_ind = {}
    for ind, sub in per_indiv(df):
        cx = (sub["x"].values // GRID_M).astype(int)
        cy = (sub["y"].values // GRID_M).astype(int)
        cells = list(zip(cx, cy))
        cell_counts = pd.Series(cells).value_counts()
        home = cell_counts.idxmax()
        period_idx = (sub["timestamp"].astype("int64").values
                      // (T_PERIOD_DAYS * 86400 * 10**9))
        # for each (cell, period) compute visit count
        df_visits = pd.DataFrame({"cell": cells, "period": period_idx})
        # visits per (cell, period) per individual:
        visits = df_visits.groupby(["cell", "period"]).size().reset_index(name="n")
        per_ind[ind] = {
            "home": home,
            "visits": visits,
        }

    # 2. Aggregate ρ_i(r, f) over (cell_target, individual)
    # For each individual+target, compute (r, f) where:
    #   r = euclidean distance home → target (in km)
    #   f = mean visits per period
    rows = []
    for ind, info in per_ind.items():
        h = info["home"]
        # Aggregate visits by cell across periods (mean per period)
        v_by_cell = info["visits"].groupby("cell")["n"].mean().reset_index()
        for _, row in v_by_cell.iterrows():
            cell = row["cell"]
            f = row["n"]  # mean visits per period (T = 30 days)
            r_km = np.sqrt((cell[0] - h[0])**2 + (cell[1] - h[1])**2) * GRID_M / 1000
            rows.append((ind, cell, r_km, f))
    visits_df = pd.DataFrame(rows, columns=["ind", "cell", "r_km", "f"])
    print(f"\n[Fig D1] {len(visits_df)} (indiv, target-cell, period) records")
    print(f"        across {visits_df['cell'].nunique()} unique cells, "
          f"{visits_df['ind'].nunique()} individuals")

    # 3. For each cell, count visitors (unique individuals) at each (r,f) bin
    # We aggregate ρ as: nº de visitantes únicos com r·f no bin específico,
    # normalizado por nº de anéis (raio).
    # Schläpfer abstracts via grid (target, origin distance, frequency bin).
    rf = visits_df["r_km"].values * visits_df["f"].values
    # Need r > 0 (skip home cell itself)
    mask = visits_df["r_km"].values > 0
    rf = rf[mask]; r = visits_df["r_km"].values[mask]; f = visits_df["f"].values[mask]

    if len(rf) < 100:
        print(f"        Insuficiente para fit ({len(rf)} records)")
        return

    # Histogram in rf-space: how many visitor-trips per rf bin per area
    # Use log bins
    n_bins = 35
    edges = np.logspace(np.log10(max(rf.min(), 0.01)), np.log10(rf.max()), n_bins + 1)
    counts, _ = np.histogram(rf, bins=edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    widths = np.diff(edges)
    pdf = counts / (widths * counts.sum())  # density estimator

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax_raw, ax_collapse = axes

    # Raw: r vs f vs ρ — in 3 frequency bands like Fig 1d
    f_bands = [(0.5, 5), (5, 20), (20, 100)]
    band_colors = ["C0", "C2", "C3"]
    for (fmin, fmax), col in zip(f_bands, band_colors):
        sel = (f >= fmin) & (f < fmax)
        if sel.sum() < 10:
            continue
        # Bin by r
        r_edges = np.logspace(np.log10(max(r[sel].min(), 0.5)),
                               np.log10(r[sel].max()), 25)
        cnts, _ = np.histogram(r[sel], bins=r_edges)
        r_centers = np.sqrt(r_edges[:-1] * r_edges[1:])
        # area normalize: divide by (2 π r dr) → density per unit area
        areas = 2 * np.pi * r_centers * np.diff(r_edges)
        rho = cnts / np.maximum(areas, 1e-9)
        valid = rho > 0
        ax_raw.loglog(r_centers[valid], rho[valid], "o-", color=col, ms=4,
                       label=f"f ∈ [{fmin}, {fmax}) visits/30d")

    ax_raw.set_xlabel("r (km, distância home → target)")
    ax_raw.set_ylabel(r"$\rho(r, f)$ (visitantes/km²)")
    ax_raw.set_title("Fig. D1a — ρ(r, f) por banda de frequência")
    ax_raw.grid(True, which="both", alpha=0.3)
    ax_raw.legend(fontsize=9)

    # Collapse: ρ vs r·f — should follow 1/(rf)^η
    ax_collapse.loglog(centers, pdf, "o", color="C0", ms=4, label="dados")
    valid = pdf > 0
    if valid.sum() > 5:
        # Fit on inner part (avoid noisy ends)
        rf_min, rf_max = np.percentile(rf, [10, 90])
        mask_fit = (centers >= rf_min) & (centers <= rf_max) & valid
        if mask_fit.sum() > 5:
            slope, intercept, rsq, *_ = stats.linregress(np.log10(centers[mask_fit]),
                                                          np.log10(pdf[mask_fit]))
            eta = -slope
            print(f"        η (lei de visitação) ≈ {eta:.2f}  R² = {rsq**2:.3f}")
            print(f"        comparação Schläpfer humanos: η ≈ 2.05")
            x_fit = np.logspace(np.log10(rf_min), np.log10(rf_max), 50)
            y_fit = 10 ** (intercept + slope * np.log10(x_fit))
            ax_collapse.loglog(x_fit, y_fit, "r--", lw=2,
                                label=f"power-law η = {eta:.2f}  R²={rsq**2:.3f}")

    ax_collapse.set_xlabel(r"$r \cdot f$ (km · visits/30d)")
    ax_collapse.set_ylabel(r"density (≈ $\rho(r,f)$)")
    ax_collapse.set_title("Fig. D1b — colapso ρ ~ (r·f)^(-η)")
    ax_collapse.grid(True, which="both", alpha=0.3)
    ax_collapse.legend(fontsize=9)

    fig.tight_layout()
    fig.savefig(OUT / "figD1_visitation_law.png", dpi=150)
    plt.close(fig)


def figD2():
    """Distância efetiva por visitante invariante: ⟨d⟩_i não depende
    da atratividade μ_i da cell (Schläpfer Fig. 2)."""
    # For each cell i: compute total travelled distance / total unique visitors
    fig, ax = plt.subplots(figsize=(6.5, 5))

    # Collect per-cell stats
    per_cell_visits = {}
    per_cell_total_dist = {}

    for ind, sub in per_indiv(df):
        x = sub["x"].values; y = sub["y"].values
        cx = (x // GRID_M).astype(int); cy = (y // GRID_M).astype(int)
        cells = list(zip(cx, cy))
        # home cell = mode
        home = pd.Series(cells).mode().iloc[0]
        hx, hy = home
        # for each unique cell visited by this individual, compute distance home → cell
        unique_cells = set(cells)
        for c in unique_cells:
            d = np.sqrt((c[0] - hx)**2 + (c[1] - hy)**2) * GRID_M / 1000
            per_cell_visits.setdefault(c, set()).add(ind)
            per_cell_total_dist.setdefault(c, 0.0)
            per_cell_total_dist[c] += d  # sum of distance for each unique visitor

    # ⟨d⟩_i = total dist / N visitors; μ_i ~ N visitors (proxy of attractiveness)
    cells = list(per_cell_visits.keys())
    N_visits = np.array([len(per_cell_visits[c]) for c in cells])
    mean_d = np.array([per_cell_total_dist[c] / max(len(per_cell_visits[c]), 1)
                       for c in cells])

    ax.semilogx(N_visits, mean_d, "o", color="C5", ms=4, alpha=0.5)

    # Linear regression in log N space — Schläpfer expects ~flat (R² < 0.05)
    valid = (N_visits > 0) & (mean_d > 0)
    if valid.sum() > 10:
        slope, intercept, rsq, *_ = stats.linregress(np.log10(N_visits[valid]),
                                                      mean_d[valid])
        print(f"\n[Fig D2] ⟨d⟩_i vs nº visitantes:")
        print(f"        slope = {slope:.3f}, R² = {rsq**2:.4f}")
        print(f"        Schläpfer humanos: R² < 0.05 (efetivamente plano)")
        x_fit = np.logspace(np.log10(N_visits[valid].min()),
                             np.log10(N_visits[valid].max()), 50)
        ax.semilogx(x_fit, intercept + slope * np.log10(x_fit), "r--",
                     label=f"slope = {slope:.2f}  R² = {rsq**2:.3f}")

    ax.set_xlabel("nº de visitantes únicos por cell")
    ax.set_ylabel(r"$\langle d \rangle_i$ (km, dist média home→cell)")
    ax.set_title("Fig. D2 — Invariância da distância efetiva por visitante")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "figD2_invariant_distance.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    figD1()
    figD2()
    print(f"\n[Bloco D] figures em {OUT}")
