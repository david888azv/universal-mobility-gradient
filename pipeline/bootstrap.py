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
Bootstrap por indivíduo (1000 resamples) das métricas-chave do paper N6.

Métricas testadas: α (P(Δr) tail MLE), ζ (Zipf top-50), μ (S(t)~t^μ),
γ (P_new ~ S^(-γ)), η (lei de visitação).

Saída: tabela markdown com mean, SE, 95% CI por espécie.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from _helpers import (load_data, per_indiv, clauset_mle,
                       bootstrap_individuals, FIG_BASE, LABEL, SPECIES)

print(f"[Bootstrap] species = {SPECIES} ({LABEL})")
df = load_data()
INDIVIDUALS = sorted(df["individual-local-identifier"].unique())
N = len(INDIVIDUALS)
GRID_M = 500
# N_BOOT scales with dataset size to keep each species under a few minutes.
# stork has 13M rows → 50 iter; elephant 280K → 500 iter; gannet 700K → 200 iter
N_ROWS = len(df)
if N_ROWS > 5_000_000:
    N_BOOT = 50
elif N_ROWS > 1_000_000:
    N_BOOT = 100
else:
    N_BOOT = 500
print(f"  N_rows = {N_ROWS:,} ⟹ N_BOOT = {N_BOOT}")

# Pre-extract per-individual data
per_ind_step = {}
per_ind_cells = {}
per_ind_xy = {}
per_ind_t = {}
for ind, sub in per_indiv(df):
    x = sub["x"].values; y = sub["y"].values
    dx = np.diff(x); dy = np.diff(y)
    dr = np.sqrt(dx*dx + dy*dy)
    per_ind_step[ind] = dr[dr > 0]
    cx = (x // GRID_M).astype(int); cy = (y // GRID_M).astype(int)
    per_ind_cells[ind] = list(zip(cx, cy))
    per_ind_xy[ind] = (x, y)
    per_ind_t[ind] = sub["timestamp"].values


def metric_alpha(sample_inds):
    """α (Clauset MLE) on pooled step lengths from sampled individuals."""
    arrs = [per_ind_step[i] for i in sample_inds if i in per_ind_step]
    if not arrs:
        return None
    pooled = np.concatenate(arrs)
    a, _, _, _, _ = clauset_mle(pooled, min_tail=200)
    return a


def metric_zeta(sample_inds):
    """ζ from top-50 ranks of pooled visitation."""
    cells_all = []
    for i in sample_inds:
        cells_all.extend(per_ind_cells.get(i, []))
    if not cells_all:
        return None
    s = pd.Series(cells_all).value_counts()
    n_top = min(50, len(s))
    if n_top < 5:
        return None
    rk = np.arange(1, n_top + 1)
    fr = s.values[:n_top]
    if (fr <= 0).any():
        return None
    slope, _, _, *_ = stats.linregress(np.log10(rk), np.log10(fr))
    return -slope


def metric_mu(sample_inds):
    """μ (S(t) ~ t^μ) — average over sampled individuals."""
    mus = []
    for i in sample_inds:
        cells = per_ind_cells.get(i)
        t = per_ind_t.get(i)
        if cells is None or t is None:
            continue
        seen = set(); S = []
        for c in cells:
            seen.add(c); S.append(len(seen))
        S = np.array(S)
        t_h = (t - t[0]).astype("timedelta64[s]").astype(float) / 3600.0
        valid = (t_h > 1) & (S > 1)
        if valid.sum() < 50:
            continue
        slope, *_ = stats.linregress(np.log10(t_h[valid]), np.log10(S[valid]))
        mus.append(slope)
    return np.mean(mus) if mus else None


def metric_gamma(sample_inds):
    """γ (P_new ~ S^(-γ)) — average."""
    gs = []
    for i in sample_inds:
        cells = per_ind_cells.get(i)
        if cells is None:
            continue
        seen = set(); is_new = []; S_curr = []
        for c in cells:
            new = c not in seen
            S_curr.append(len(seen)); is_new.append(int(new)); seen.add(c)
        S_curr = np.array(S_curr); is_new = np.array(is_new)
        max_S = S_curr.max()
        if max_S < 30:
            continue
        bins = np.unique(np.logspace(np.log10(2), np.log10(max_S), 25).astype(int))
        bins = np.clip(bins, 2, max_S)
        Pn, Sm = [], []
        for k in range(len(bins) - 1):
            mask = (S_curr >= bins[k]) & (S_curr < bins[k+1])
            if mask.sum() >= 10:
                Pn.append(is_new[mask].mean())
                Sm.append((bins[k] + bins[k+1]) / 2)
        Sm = np.array(Sm); Pn = np.array(Pn)
        valid = Pn > 0
        if valid.sum() < 5:
            continue
        slope, *_ = stats.linregress(np.log10(Sm[valid]), np.log10(Pn[valid]))
        gs.append(-slope)
    return np.mean(gs) if gs else None


def metric_beta_waiting(sample_inds):
    """β (waiting-time MLE)."""
    waits = []
    for i in sample_inds:
        cells = per_ind_cells.get(i)
        t = per_ind_t.get(i)
        if cells is None or t is None:
            continue
        prev = None; t_in = None
        for c, ti in zip(cells, t):
            if c != prev:
                if prev is not None:
                    dur = (np.datetime64(ti) - np.datetime64(t_in)) \
                            .astype("timedelta64[s]").astype(float)
                    if dur > 0:
                        waits.append(dur / 60.0)
                prev = c; t_in = ti
    waits = np.array(waits)
    waits = waits[waits > 1]
    if len(waits) < 200:
        return None
    a, _, _, _, _ = clauset_mle(waits, min_tail=200)
    return a - 1 if a is not None else None


def metric_eta(sample_inds):
    """η: power-law slope of pooled rf-density."""
    rows = []
    for i in sample_inds:
        cells = per_ind_cells.get(i)
        t = per_ind_t.get(i)
        if cells is None:
            continue
        cell_counts = pd.Series(cells).value_counts()
        home = cell_counts.idxmax()
        hx, hy = home
        period_idx = (t.astype("int64") // (30 * 86400 * 10**9))
        df_v = pd.DataFrame({"cell": cells, "period": period_idx})
        v = df_v.groupby(["cell", "period"]).size().reset_index(name="n")
        v_by_cell = v.groupby("cell")["n"].mean().reset_index()
        for _, row in v_by_cell.iterrows():
            c = row["cell"]
            f = row["n"]
            r_km = np.sqrt((c[0]-hx)**2 + (c[1]-hy)**2) * GRID_M / 1000
            if r_km > 0:
                rows.append((r_km, f))
    if len(rows) < 100:
        return None
    rs, fs = zip(*rows)
    rf = np.array(rs) * np.array(fs)
    edges = np.logspace(np.log10(max(rf.min(), 0.01)),
                         np.log10(rf.max()), 35)
    cnts, _ = np.histogram(rf, bins=edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    widths = np.diff(edges)
    pdf = cnts / (widths * cnts.sum())
    rf_min, rf_max = np.percentile(rf, [10, 90])
    mask = (centers >= rf_min) & (centers <= rf_max) & (pdf > 0)
    if mask.sum() < 5:
        return None
    slope, *_ = stats.linregress(np.log10(centers[mask]), np.log10(pdf[mask]))
    return -slope


METRICS = {
    "α (P(Δr) MLE)": metric_alpha,
    "ζ (Zipf top-50)": metric_zeta,
    "μ (S(t)~t^μ)": metric_mu,
    "γ (P_new~S^-γ)": metric_gamma,
    "β (waiting MLE)": metric_beta_waiting,
    "η (visitação)": metric_eta,
}


print(f"\n[Bootstrap] N indiv = {N}, N_boot = {N_BOOT}")
print(f"\n{'metric':<22s} {'mean':>8s} {'SE':>8s} {'95% CI':>22s}")
print("-" * 64)

results = {}
for name, fn in METRICS.items():
    mean, se, lo, hi = bootstrap_individuals(INDIVIDUALS, fn, n_boot=N_BOOT)
    if mean is None:
        print(f"{name:<22s} {'N/A':>8s}")
        continue
    print(f"{name:<22s} {mean:>8.3f} {se:>8.3f}  [{lo:>7.3f}, {hi:>7.3f}]")
    results[name] = (mean, se, lo, hi)

# Save table
out_md = FIG_BASE / f"bootstrap_{SPECIES}.md"
with open(out_md, "w") as f:
    f.write(f"# Bootstrap N6 — {LABEL} (N={N}, n_boot={N_BOOT})\n\n")
    f.write("| Métrica | mean | SE | 95% CI |\n|---|---:|---:|---|\n")
    for name, (m, se, lo, hi) in results.items():
        f.write(f"| {name} | {m:.3f} | {se:.3f} | [{lo:.3f}, {hi:.3f}] |\n")
print(f"\n[Bootstrap] tabela em {out_md}")
