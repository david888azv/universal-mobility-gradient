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
Análise estacional da cegonha — split breeding / migration / wintering.

Hipótese central: Song relations falham na cegonha agregada porque misturam
3 regimes (breeding, migration, wintering). Em fase breeding *pura* — quando
a cegonha está obrigada ao ninho — Song deveria valer.

Saída: tabela de métricas por fase + figura comparativa.
"""

from pathlib import Path
import os
os.environ["SPECIES"] = "stork"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from _helpers import load_data, lonlat_to_xy, log_bin_pdf, clauset_mle, FIG_BASE

OUT = FIG_BASE / "stork_seasonal"
OUT.mkdir(parents=True, exist_ok=True)

print("[stork-seasonal] loading ...")
df = load_data()

# Add month and define seasonal phase
df["month"] = df["timestamp"].dt.month
df["lat"] = df["location-lat"]


def phase_of(row):
    m = row["month"]; lat = row["lat"]
    if m in (4, 5, 6, 7, 8) and lat > 40:
        return "breeding"
    if m in (11, 12, 1) and lat < 30:
        return "wintering"
    if m in (9, 10, 2, 3):
        return "migration"
    return "transition"  # ambiguous


# vectorized assignment
in_breeding = df["month"].isin([4, 5, 6, 7, 8]) & (df["lat"] > 40)
in_wintering = df["month"].isin([11, 12, 1]) & (df["lat"] < 30)
in_migration = df["month"].isin([9, 10, 2, 3])
df["phase"] = "transition"
df.loc[in_migration, "phase"] = "migration"
df.loc[in_breeding, "phase"] = "breeding"
df.loc[in_wintering, "phase"] = "wintering"

print("\nphase counts:")
print(df["phase"].value_counts())

GRID_M = 500
PHASES = ["breeding", "migration", "wintering"]
COLORS = {"breeding": "#2ca02c", "migration": "#d62728", "wintering": "#1f77b4"}


def compute_metrics(sub_df):
    """Compute α, ζ, μ, γ, β, η for a phase-filtered sub-dataset."""
    out = {}

    # Step lengths
    all_dr = []
    for ind in sub_df["individual-local-identifier"].unique():
        s = sub_df[sub_df["individual-local-identifier"] == ind].sort_values("timestamp")
        x = s["x"].values; y = s["y"].values
        dx = np.diff(x); dy = np.diff(y)
        dr = np.sqrt(dx*dx + dy*dy)
        all_dr.append(dr[dr > 0])
    if not all_dr:
        return None
    pooled_dr = np.concatenate(all_dr)
    a, _, sa, ks, _ = clauset_mle(pooled_dr, min_tail=200)
    out["alpha"] = (a, sa, ks)

    # Cells per indiv
    cells_per_ind = {}
    for ind in sub_df["individual-local-identifier"].unique():
        s = sub_df[sub_df["individual-local-identifier"] == ind].sort_values("timestamp")
        x = s["x"].values; y = s["y"].values
        cx = (x // GRID_M).astype(int); cy = (y // GRID_M).astype(int)
        cells_per_ind[ind] = (list(zip(cx, cy)), s["timestamp"].values)

    # Zeta (pooled top-50)
    cells_all = []
    for cells, _ in cells_per_ind.values():
        cells_all.extend(cells)
    s = pd.Series(cells_all).value_counts()
    n_top = min(50, len(s))
    if n_top > 5:
        rk = np.arange(1, n_top + 1); fr = s.values[:n_top]
        slope, *_ = stats.linregress(np.log10(rk), np.log10(fr))
        out["zeta"] = -slope
    else:
        out["zeta"] = None

    # mu and gamma per individual
    mus, gammas = [], []
    for cells, t in cells_per_ind.values():
        if len(cells) < 50:
            continue
        seen = set(); S = []
        for c in cells:
            seen.add(c); S.append(len(seen))
        S = np.array(S)
        t_h = (t - t[0]).astype("timedelta64[s]").astype(float) / 3600.0
        valid = (t_h > 1) & (S > 1)
        if valid.sum() > 30:
            sl, *_ = stats.linregress(np.log10(t_h[valid]), np.log10(S[valid]))
            mus.append(sl)

        # gamma
        seen2 = set(); is_new = []; S_curr = []
        for c in cells:
            new = c not in seen2
            S_curr.append(len(seen2)); is_new.append(int(new)); seen2.add(c)
        S_curr = np.array(S_curr); is_new = np.array(is_new)
        max_S = S_curr.max()
        if max_S > 30:
            bins = np.unique(np.logspace(np.log10(2), np.log10(max_S), 25).astype(int))
            bins = np.clip(bins, 2, max_S)
            Pn, Sm = [], []
            for k in range(len(bins) - 1):
                m = (S_curr >= bins[k]) & (S_curr < bins[k+1])
                if m.sum() >= 10:
                    Pn.append(is_new[m].mean()); Sm.append((bins[k]+bins[k+1])/2)
            Sm = np.array(Sm); Pn = np.array(Pn)
            v = Pn > 0
            if v.sum() >= 5:
                sl, *_ = stats.linregress(np.log10(Sm[v]), np.log10(Pn[v]))
                gammas.append(-sl)

    out["mu"] = np.mean(mus) if mus else None
    out["gamma"] = np.mean(gammas) if gammas else None

    # waiting time -> beta
    waits = []
    for cells, t in cells_per_ind.values():
        prev = None; t_in = None
        for c, ti in zip(cells, t):
            if c != prev:
                if prev is not None:
                    dur = (np.datetime64(ti) - np.datetime64(t_in)) \
                            .astype("timedelta64[s]").astype(float)
                    if dur > 0:
                        waits.append(dur / 60.0)
                prev = c; t_in = ti
    waits = np.array(waits); waits = waits[waits > 1]
    if len(waits) > 200:
        a, _, sa, _, _ = clauset_mle(waits, min_tail=200)
        out["beta"] = (a - 1, sa) if a else None
    else:
        out["beta"] = None

    # eta (visitation)
    rows = []
    for cells, t in cells_per_ind.values():
        cell_counts = pd.Series(cells).value_counts()
        if cell_counts.empty:
            continue
        home = cell_counts.idxmax(); hx, hy = home
        period_idx = (t.astype("int64") // (120 * 86400 * 10**9))
        df_v = pd.DataFrame({"cell": cells, "period": period_idx})
        v = df_v.groupby(["cell", "period"]).size().reset_index(name="n")
        v_by_cell = v.groupby("cell")["n"].mean().reset_index()
        for _, row in v_by_cell.iterrows():
            c = row["cell"]; f = row["n"]
            r_km = np.sqrt((c[0]-hx)**2 + (c[1]-hy)**2) * GRID_M / 1000
            if r_km > 0:
                rows.append((r_km, f))
    if len(rows) > 100:
        rs, fs = zip(*rows)
        rf = np.array(rs) * np.array(fs)
        edges = np.logspace(np.log10(max(rf.min(), 0.01)),
                             np.log10(rf.max()), 35)
        cnts, _ = np.histogram(rf, bins=edges)
        centers = np.sqrt(edges[:-1] * edges[1:])
        widths = np.diff(edges)
        pdf = cnts / (widths * cnts.sum())
        rf_min, rf_max = np.percentile(rf, [10, 90])
        m = (centers >= rf_min) & (centers <= rf_max) & (pdf > 0)
        if m.sum() >= 5:
            sl, *_ = stats.linregress(np.log10(centers[m]), np.log10(pdf[m]))
            out["eta"] = -sl
        else:
            out["eta"] = None
    else:
        out["eta"] = None

    return out, pooled_dr


# Project xy
df["x"], df["y"] = lonlat_to_xy(df["location-long"].values, df["lat"].values)

results = {}
step_lens = {}
print(f"\n{'phase':<12s} {'N rows':>10s} {'N indiv':>8s} {'α':>10s} {'ζ':>8s} "
      f"{'μ':>8s} {'γ':>8s} {'β':>8s} {'η':>8s}")
print("-" * 84)

for phase in PHASES:
    sub = df[df["phase"] == phase]
    n_indiv = sub["individual-local-identifier"].nunique()
    if len(sub) < 1000:
        print(f"{phase:<12s} {len(sub):>10d} {n_indiv:>8d}  insufficient")
        continue
    res = compute_metrics(sub)
    if res is None:
        continue
    out, dr = res
    results[phase] = out
    step_lens[phase] = dr
    a = out["alpha"][0] if out["alpha"] else None
    z = out["zeta"]
    m = out["mu"]
    g = out["gamma"]
    b = out["beta"][0] if out["beta"] else None
    e = out["eta"]
    print(f"{phase:<12s} {len(sub):>10d} {n_indiv:>8d}  "
          f"{a:>9.2f} {z:>8.2f} {m:>8.2f} {g:>8.2f} {b:>8.2f} {e:>8.2f}"
          if all(v is not None for v in [a, z, m, g, b, e])
          else f"{phase:<12s} {len(sub):>10d} {n_indiv:>8d}  partial")

# Test Song relations per phase
print("\n=== Relações de Song por fase ===")
print(f"{'phase':<12s} {'μ':>8s} {'β/(1+γ)':>10s} {'ratio':>8s} | "
      f"{'ζ':>8s} {'1+γ':>8s} {'ratio':>8s} | "
      f"{'β':>8s} {'μζ':>8s} {'ratio':>8s}")
for phase, r in results.items():
    if not all(r.get(k) is not None for k in ("mu", "gamma", "beta", "zeta")):
        continue
    mu_p = r["mu"]; g_p = r["gamma"]
    b_p = r["beta"][0]; z_p = r["zeta"]
    pred_mu = b_p / (1 + g_p) if (1 + g_p) != 0 else float('nan')
    pred_zeta = 1 + g_p
    pred_beta = mu_p * z_p
    rmu = max(pred_mu, mu_p)/min(abs(pred_mu), abs(mu_p)) if min(abs(pred_mu), abs(mu_p)) > 0.01 else float('nan')
    rzeta = max(pred_zeta, z_p)/min(abs(pred_zeta), abs(z_p)) if min(abs(pred_zeta), abs(z_p)) > 0.01 else float('nan')
    rbeta = max(pred_beta, b_p)/min(abs(pred_beta), abs(b_p)) if min(abs(pred_beta), abs(b_p)) > 0.01 else float('nan')
    print(f"{phase:<12s} {mu_p:>8.2f} {pred_mu:>10.2f} {rmu:>8.2f} | "
          f"{z_p:>8.2f} {pred_zeta:>8.2f} {rzeta:>8.2f} | "
          f"{b_p:>8.2f} {pred_beta:>8.2f} {rbeta:>8.2f}")

# Plot P(Δr) per phase + ζ comparison
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax_pdr, ax_metrics = axes

for phase in PHASES:
    if phase not in step_lens:
        continue
    c, p = log_bin_pdf(step_lens[phase], n_bins=45)
    ax_pdr.loglog(c, p, "o-", color=COLORS[phase], ms=4, lw=0.8,
                   label=f"{phase}  α = {results[phase]['alpha'][0]:.2f}"
                         if results[phase].get("alpha") else phase)

ax_pdr.set_xlabel(r"$\Delta r$ (m)")
ax_pdr.set_ylabel(r"$P(\Delta r)$")
ax_pdr.set_title("Stork P(Δr) por fase")
ax_pdr.grid(True, which="both", alpha=0.3)
ax_pdr.legend()

# Bar chart of ζ, η per phase
metrics_to_plot = ["zeta", "mu", "gamma", "eta"]
labels_pt = [r"$\zeta$", r"$\mu$", r"$\gamma$", r"$\eta$"]
x_pos = np.arange(len(metrics_to_plot))
bar_w = 0.25
for i, phase in enumerate(PHASES):
    if phase not in results:
        continue
    vals = []
    for m in metrics_to_plot:
        v = results[phase].get(m)
        if isinstance(v, tuple):
            v = v[0]
        vals.append(v if v is not None else 0)
    ax_metrics.bar(x_pos + (i - 1) * bar_w, vals, bar_w,
                    label=phase, color=COLORS[phase])

# Reference humano lines
human_refs = {"zeta": 1.0, "mu": 0.6, "gamma": 0.21, "eta": 2.05}
for k, v in human_refs.items():
    if k in metrics_to_plot:
        idx = metrics_to_plot.index(k)
        ax_metrics.hlines(v, idx - 0.4, idx + 0.4, colors="black", linestyles=":",
                           lw=1.5, alpha=0.6)

ax_metrics.set_xticks(x_pos)
ax_metrics.set_xticklabels(labels_pt, fontsize=12)
ax_metrics.axhline(0, color="grey", lw=0.5)
ax_metrics.set_title("Métricas por fase (linhas pretas = humano)")
ax_metrics.legend()
ax_metrics.grid(True, axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(OUT / "stork_seasonal_comparison.png", dpi=160)
plt.close(fig)

# Save results table
with open(OUT / "stork_seasonal_results.md", "w") as f:
    f.write("# Stork seasonal split — N6 robustness check\n\n")
    f.write("| phase | N rows | N indiv | α | ζ | μ | γ | β | η |\n|---|---|---|---|---|---|---|---|---|\n")
    for phase in PHASES:
        if phase not in results:
            continue
        sub = df[df["phase"] == phase]
        r = results[phase]
        a = r["alpha"][0] if r["alpha"] else None
        b = r["beta"][0] if r["beta"] else None
        f.write(f"| **{phase}** | {len(sub):,} | "
                f"{sub['individual-local-identifier'].nunique()} | "
                f"{a:.2f} | {r['zeta']:.2f} | {r['mu']:.2f} | "
                f"{r['gamma']:.2f} | {b:.2f} | {r['eta']:.2f} |\n")
    f.write("\n### Song scaling relations per phase\n\n")
    f.write("| phase | μ | β/(1+γ) | ratio | ζ | 1+γ | ratio | β | μζ | ratio |\n")
    f.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for phase, r in results.items():
        if not all(r.get(k) is not None for k in ("mu", "gamma", "beta", "zeta")):
            continue
        mu_p = r["mu"]; g_p = r["gamma"]; b_p = r["beta"][0]; z_p = r["zeta"]
        pred_mu = b_p / (1 + g_p)
        pred_zeta = 1 + g_p
        pred_beta = mu_p * z_p
        rmu = max(pred_mu, mu_p)/min(abs(pred_mu), abs(mu_p))
        rzeta = max(pred_zeta, z_p)/min(abs(pred_zeta), abs(z_p))
        rbeta = max(pred_beta, b_p)/min(abs(pred_beta), abs(b_p))
        f.write(f"| **{phase}** | {mu_p:.2f} | {pred_mu:.2f} | {rmu:.2f} | "
                f"{z_p:.2f} | {pred_zeta:.2f} | {rzeta:.2f} | "
                f"{b_p:.2f} | {pred_beta:.2f} | {rbeta:.2f} |\n")
print(f"\n[stork-seasonal] outputs em {OUT}")
