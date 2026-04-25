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
Bloco A — protocolo González 2008 (Nature 453:779) refinado.

Refinamentos vs versão inicial:
- Fig 1: MLE Clauset (com xmin auto, IC) substituindo regressão log-log.
- Fig 4: F_pt(t) com 3 valores de R (500m, 2km, 3km) sobrepostos.
- Fig 5: Zipf P(L) em 3 grids (200, 500, 1000m) com fit em cada.
- Fig 6: MLE Clauset por grupo de rg + colapso reescalado.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from _helpers import (load_data, per_indiv, log_bin_pdf, clauset_mle,
                       fig_dir, LABEL, SPECIES)

OUT = fig_dir("blocoA")

print("[Bloco A] loading data ...")
df = load_data()
INDIVIDUALS = sorted(df["individual-local-identifier"].unique())
print(f"  {len(df)} fixes, {len(INDIVIDUALS)} individuals")

# -- Pre-compute per-individual quantities --------------------------------
step_lens = {}
rg_full = {}
rg_t_curve = {}
xy_per_ind = {}

for ind, sub in per_indiv(df):
    x = sub["x"].values
    y = sub["y"].values
    t = sub["timestamp"].values
    xy_per_ind[ind] = (x, y, t)

    dx = np.diff(x); dy = np.diff(y)
    dr = np.sqrt(dx * dx + dy * dy)
    step_lens[ind] = dr[dr > 0]

    xc, yc = x.mean(), y.mean()
    rg_full[ind] = np.sqrt(((x - xc) ** 2 + (y - yc) ** 2).mean())

    n = len(x)
    t_h = (t - t[0]).astype("timedelta64[s]").astype(float) / 3600.0
    rg_curve = np.empty(n)
    sx = sy = sxx = syy = 0.0
    for k in range(n):
        sx += x[k]; sy += y[k]
        sxx += x[k] * x[k]; syy += y[k] * y[k]
        m = k + 1
        rg_curve[k] = np.sqrt(max(sxx / m - (sx / m) ** 2 +
                                    syy / m - (sy / m) ** 2, 0.0))
    rg_t_curve[ind] = (t_h, rg_curve)


# ---------- Fig 1: P(Δr) com MLE Clauset --------------------------------
def fig1():
    all_dr = np.concatenate(list(step_lens.values()))
    centers, pdf = log_bin_pdf(all_dr, n_bins=50)

    alpha, xmin, std_a, ks, n_tail = clauset_mle(all_dr)
    print(f"\n[Fig 1] N step-lengths: {len(all_dr)}; "
          f"median={np.median(all_dr):.0f} m, max={all_dr.max():.0f} m")
    if alpha is not None:
        print(f"        Clauset MLE: α = {alpha:.3f} ± {std_a:.3f}, "
              f"x_min = {xmin:.0f} m, KS = {ks:.3f}, n_tail = {n_tail}")

    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.loglog(centers, pdf, "o", color="C0", ms=4,
              label=f"dados ({len(INDIVIDUALS)} indiv)")
    if alpha is not None:
        # P(x) = (α-1) x_min^(α-1) x^(-α) for x ≥ x_min
        x_fit = np.logspace(np.log10(xmin), np.log10(centers.max()), 60)
        y_fit = (alpha - 1) * xmin ** (alpha - 1) * x_fit ** (-alpha)
        ax.loglog(x_fit, y_fit, "--", color="C3", lw=2,
                  label=f"MLE: α = {alpha:.2f}±{std_a:.2f}\n"
                        f"x_min = {xmin:.0f} m, KS = {ks:.3f}")
        ax.axvline(xmin, color="grey", ls=":", alpha=0.6)

    ax.set_xlabel(r"$\Delta r$ (m)")
    ax.set_ylabel(r"$P(\Delta r)$")
    ax.set_title(f"Fig. 1 — P(Δr) {LABEL} — MLE Clauset")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig1_step_length_pdf.png", dpi=150)
    plt.close(fig)


# ---------- Fig 2: P(rg) ------------------------------------------------
def fig2():
    rgs = np.array([rg_full[i] for i in INDIVIDUALS])
    rgs_sorted = np.sort(rgs)
    ccdf = 1 - np.arange(len(rgs_sorted)) / len(rgs_sorted)
    print(f"\n[Fig 2] rg values (km): {(rgs/1000).round(2).tolist()}")

    fig, ax = plt.subplots(figsize=(6.5, 5))
    ax.loglog(rgs_sorted / 1000, ccdf, "o-", color="C2", ms=6,
              label=f"CCDF empírica ({len(INDIVIDUALS)} indiv)")
    ax.set_xlabel(r"$r_g$ (km)")
    ax.set_ylabel(r"$P(R_g \geq r_g)$")
    ax.set_title(f"Fig. 2 — Distribuição de rg ({LABEL})")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig2_rg_distribution.png", dpi=150)
    plt.close(fig)


# ---------- Fig 3: rg(t) ------------------------------------------------
def fig3():
    rgs = np.array([rg_full[i] for i in INDIVIDUALS])
    qs = np.quantile(rgs, [1/3, 2/3])
    groups = {"baixo rg": [], "médio rg": [], "alto rg": []}
    for ind in INDIVIDUALS:
        if rg_full[ind] <= qs[0]:
            groups["baixo rg"].append(ind)
        elif rg_full[ind] <= qs[1]:
            groups["médio rg"].append(ind)
        else:
            groups["alto rg"].append(ind)

    t_max = max(rg_t_curve[i][0][-1] for i in INDIVIDUALS)
    t_grid = np.logspace(np.log10(1.0), np.log10(t_max), 80)

    fig, ax = plt.subplots(figsize=(6.5, 5))
    colors = {"baixo rg": "C0", "médio rg": "C1", "alto rg": "C3"}
    for label, inds in groups.items():
        curves = []
        for ind in inds:
            t_h, rg_c = rg_t_curve[ind]
            tm = t_h > 0
            curves.append(np.interp(t_grid, t_h[tm], rg_c[tm],
                                     left=np.nan, right=np.nan))
        mean_c = np.nanmean(np.vstack(curves), axis=0)
        ax.plot(t_grid, mean_c / 1000, "-", lw=1.8, color=colors[label],
                label=f"{label} ({len(inds)} indiv)")

    # log-fit on the alto-rg group, t > 24h
    inds = groups["alto rg"]
    curves = []
    for ind in inds:
        t_h, rg_c = rg_t_curve[ind]
        tm = t_h > 1
        curves.append(np.interp(t_grid, t_h[tm], rg_c[tm],
                                 left=np.nan, right=np.nan))
    mean_hi = np.nanmean(np.vstack(curves), axis=0)
    valid = ~np.isnan(mean_hi) & (t_grid > 24) & (mean_hi > 0)
    if valid.sum() > 10:
        a, b, r, *_ = stats.linregress(np.log(t_grid[valid]),
                                        mean_hi[valid] / 1000)
        print(f"\n[Fig 3] alto rg log-fit: rg(t) ≈ {b:.2f} + "
              f"{a:.2f}·ln(t)  R²={r**2:.3f}")
        t_fit = np.logspace(np.log10(24), np.log10(t_max), 40)
        ax.plot(t_fit, b + a * np.log(t_fit), "k--", alpha=0.5,
                label="log-fit alto rg")

    ax.set_xscale("log")
    ax.set_xlabel("t (horas)")
    ax.set_ylabel(r"$\langle r_g(t) \rangle$ (km)")
    ax.set_title(f"Fig. 3 — rg(t) médio ({LABEL})")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig3_rg_of_t.png", dpi=150)
    plt.close(fig)


# ---------- Fig 4: F_pt(t) com R = 500m, 2km, 3km -----------------------
def fig4():
    fig, ax = plt.subplots(figsize=(7, 5))
    bin_edges = np.arange(0, 30 * 24 + 1, 1)  # 1h bins, até 30 dias
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    Rs = [500, 2000, 3000]
    colors = ["C0", "C1", "C3"]

    print("\n[Fig 4] F_pt(t) — picos circadianos por R:")
    for R, color in zip(Rs, colors):
        counts_total = np.zeros(len(bin_centers))
        counts_close = np.zeros(len(bin_centers))
        for ind in INDIVIDUALS:
            x, y, t = xy_per_ind[ind]
            t_h = (t - t[0]).astype("timedelta64[s]").astype(float) / 3600.0
            x0, y0 = x[0], y[0]
            d_home = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)
            mask = t_h <= bin_edges[-1]
            idx = np.digitize(t_h[mask], bin_edges) - 1
            for k, close in zip(idx, d_home[mask] < R):
                if 0 <= k < len(bin_centers):
                    counts_total[k] += 1
                    counts_close[k] += int(close)
        f_pt = np.where(counts_total > 0, counts_close / counts_total, np.nan)
        # Smooth with running mean (3h window)
        kern = np.ones(3) / 3
        f_smooth = np.convolve(f_pt, kern, mode="same")

        ax.plot(bin_centers, f_smooth, color=color, lw=1.5,
                label=f"R = {R} m")

        # Print values near 24, 48, 72, 96 h
        peaks = [f_pt[24*k] if 24*k < len(f_pt) else np.nan for k in (1,2,3,4)]
        print(f"        R={R:>4} m: F_pt em 24/48/72/96 h = "
              + ", ".join(f"{p:.3f}" for p in peaks))

    for k in range(1, 8):
        ax.axvline(24 * k, ls=":", color="grey", alpha=0.4, lw=0.8)

    ax.set_xlabel("t (h desde primeira observação)")
    ax.set_ylabel(r"$F_{pt}(t)$  (P[d<R])")
    ax.set_title(f"Fig. 4 — F_pt(t) ({LABEL})")
    ax.set_xlim(0, 7 * 24)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "fig4_return_probability.png", dpi=150)
    plt.close(fig)


# ---------- Fig 5: P(L) Zipf em 3 grids ---------------------------------
def fig5():
    fig, ax = plt.subplots(figsize=(7, 5))
    grid_sizes = [200, 500, 1000]
    colors = ["C0", "C5", "C3"]

    print("\n[Fig 5] Zipf P(L) — por grid:")
    for g, col in zip(grid_sizes, colors):
        all_ranks = []
        for ind in INDIVIDUALS:
            x, y, _ = xy_per_ind[ind]
            cx = (x // g).astype(int); cy = (y // g).astype(int)
            cells = list(zip(cx, cy))
            s = pd.Series(cells).value_counts()
            all_ranks.append(s.values)
        max_rank = max(len(r) for r in all_ranks)
        grid_ranks = np.arange(1, max_rank + 1)
        mean_freq = np.zeros(max_rank); n_contrib = np.zeros(max_rank)
        for r in all_ranks:
            n = len(r)
            mean_freq[:n] += r
            n_contrib[:n] += 1
        mean_freq = mean_freq / np.maximum(n_contrib, 1)

        ax.loglog(grid_ranks, mean_freq, "o", ms=3, color=col,
                  label=f"grid {g} m, max rank = {max_rank}")

        # Fit slope on top 50 ranks (avoiding cutoff)
        rk = grid_ranks[mean_freq > 0]
        fr = mean_freq[mean_freq > 0]
        n_top = min(50, len(rk))
        if n_top > 5:
            slope, intercept, r, *_ = stats.linregress(np.log10(rk[:n_top]),
                                                       np.log10(fr[:n_top]))
            print(f"        grid {g:>4} m: ζ ≈ {-slope:.2f}  "
                  f"(R²={r**2:.3f}, top {n_top})")

    ax.set_xlabel("rank L do local")
    ax.set_ylabel("frequência média de visita")
    ax.set_title(f"Fig. 5 — Zipf P(L) ({LABEL})")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig5_zipf_locations.png", dpi=150)
    plt.close(fig)


# ---------- Fig 6: P(Δr|rg) collapse com MLE α --------------------------
def fig6():
    rgs = np.array([rg_full[i] for i in INDIVIDUALS])
    qs = np.quantile(rgs, [1/3, 2/3])
    groups = {"baixo rg": [], "médio rg": [], "alto rg": []}
    for ind in INDIVIDUALS:
        if rg_full[ind] <= qs[0]:
            groups["baixo rg"].append(ind)
        elif rg_full[ind] <= qs[1]:
            groups["médio rg"].append(ind)
        else:
            groups["alto rg"].append(ind)

    # MLE α per group
    print("\n[Fig 6] MLE Clauset por grupo:")
    alphas_by_group = {}
    for label, inds in groups.items():
        all_dr = np.concatenate([step_lens[i] for i in inds])
        a, xm, sa, ks, n = clauset_mle(all_dr)
        alphas_by_group[label] = a
        print(f"        {label}: α = {a:.3f}±{sa:.3f}, x_min = {xm:.0f} m, "
              f"KS = {ks:.3f}, n_tail = {n}")

    # Use median α as universal exponent for rescaling
    alpha = np.median([a for a in alphas_by_group.values() if a is not None])
    print(f"        ⟹ α universal (mediana) = {alpha:.3f}")
    # González used α = 1.2 in his rescaling Fig 2b; this is the analog measurement.
    # But Clauset MLE on tail typically gives ~2-3 (= 1+α_clauset = β); we want
    # the exponent of P(Δr|rg) ~ rg^{-α} F(Δr/rg). For rescaling, use α-1
    # in his notation conversion. We use α_resc as a tunable parameter.
    alpha_resc = 1.2  # González's empirical value, kept for comparison

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax_raw, ax_resc = axes
    colors = {"baixo rg": "C0", "médio rg": "C1", "alto rg": "C3"}
    for label, inds in groups.items():
        all_dr = np.concatenate([step_lens[i] for i in inds])
        if len(all_dr) < 100:
            continue
        rg_grp = np.mean([rg_full[i] for i in inds])
        centers, pdf = log_bin_pdf(all_dr, n_bins=40)
        ax_raw.loglog(centers, pdf, "o", color=colors[label], ms=4,
                       label=f"{label} (rg≈{rg_grp/1000:.1f} km, "
                             f"α_MLE={alphas_by_group[label]:.2f})")
        ax_resc.loglog(centers / rg_grp, pdf * (rg_grp ** alpha_resc), "o",
                        color=colors[label], ms=4,
                        label=f"{label}")

    ax_raw.set_xlabel(r"$\Delta r$ (m)")
    ax_raw.set_ylabel(r"$P(\Delta r | r_g)$")
    ax_raw.set_title(f"Fig. 6a — P(Δr|rg) ({LABEL})")
    ax_raw.grid(True, which="both", alpha=0.3)
    ax_raw.legend(fontsize=8)

    ax_resc.set_xlabel(r"$\Delta r / r_g$")
    ax_resc.set_ylabel(rf"$r_g^{{{alpha_resc}}} \cdot P(\Delta r | r_g)$")
    ax_resc.set_title(rf"Fig. 6b — colapso com α_resc = {alpha_resc}")
    ax_resc.grid(True, which="both", alpha=0.3)
    ax_resc.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_collapse.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fig1(); fig2(); fig3(); fig4(); fig5(); fig6()
    print(f"\n[Bloco A] 6 figures em {OUT}")
