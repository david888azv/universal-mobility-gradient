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
Bloco B — Song et al. 2010 (Nat. Phys. 6:818).

Estimadores temporais e relações escalares:
- S(t) = número de locais distintos visitados até tempo t  ⟹ μ
- f_k = frequência de visita ranqueada                      ⟹ ζ  (já em A.fig5)
- P_new(S) = ρ S^(-γ) (probabilidade de explorar novo local) ⟹ γ, ρ
- Testes das relações: μ = β/(1+γ), ζ = 1+γ, β = μζ
  (β aqui é o expoente de waiting-time; usamos β=0.8 humanos como referência
  e medimos β_anim em sub-figuras se houver dados de tempo de permanência)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from _helpers import load_data, per_indiv, fig_dir, LABEL, SPECIES

OUT = fig_dir("blocoB")

print("[Bloco B] loading data ...")
df = load_data()
INDIVIDUALS = sorted(df["individual-local-identifier"].unique())

GRID_M = 500  # cell size for "location" definition (Movebank)


def cells_per_indiv(df, grid):
    out = {}
    for ind, sub in per_indiv(df):
        x = sub["x"].values; y = sub["y"].values
        t = sub["timestamp"].values
        cx = (x // grid).astype(int); cy = (y // grid).astype(int)
        out[ind] = list(zip(cx, cy)), t
    return out


cells_data = cells_per_indiv(df, GRID_M)


# ---------- Fig B1: S(t) e μ --------------------------------------------
def figB1():
    """S(t) cumulative distinct locations vs time."""
    fig, ax = plt.subplots(figsize=(7, 5))

    print("\n[Fig B1] S(t) ~ t^μ por indivíduo:")
    mus = []
    for ind in INDIVIDUALS:
        cells, t = cells_data[ind]
        seen = set()
        S = []
        for c in cells:
            seen.add(c)
            S.append(len(seen))
        S = np.array(S)
        t_h = (t - t[0]).astype("timedelta64[s]").astype(float) / 3600.0
        # Avoid t=0; use t > 1h for fit
        valid = (t_h > 1) & (S > 1)
        if valid.sum() < 50:
            continue
        slope, intercept, r, *_ = stats.linregress(np.log10(t_h[valid]),
                                                    np.log10(S[valid]))
        mus.append(slope)
        ax.loglog(t_h[valid], S[valid], "-", lw=0.7, alpha=0.5,
                  label=f"{ind} μ={slope:.2f}")
    mu_mean = np.mean(mus); mu_std = np.std(mus)
    print(f"        μ médio = {mu_mean:.3f} ± {mu_std:.3f} (n={len(mus)})")
    print(f"        comparação Song humanos: μ ≈ 0.6")

    # Aggregate curve
    t_grid = np.logspace(0, np.log10(2 * 365 * 24), 60)
    S_curves = []
    for ind in INDIVIDUALS:
        cells, t = cells_data[ind]
        seen = set(); S = []
        for c in cells:
            seen.add(c); S.append(len(seen))
        t_h = (t - t[0]).astype("timedelta64[s]").astype(float) / 3600.0
        valid = t_h > 1
        if valid.sum() > 10:
            S_curves.append(np.interp(t_grid, t_h[valid], np.array(S)[valid],
                                       left=np.nan, right=np.nan))
    S_mean = np.nanmean(np.vstack(S_curves), axis=0)

    ax.plot(t_grid, S_mean, "k-", lw=2.5, label=f"média (μ̄ = {mu_mean:.2f})")

    ax.set_xlabel("t (horas)")
    ax.set_ylabel("S(t) = nº locais distintos")
    ax.set_title(f"Fig. B1 — S(t) ~ t^μ  (grid {GRID_M} m)")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "figB1_St_mu.png", dpi=150)
    plt.close(fig)
    return mu_mean, mu_std


# ---------- Fig B2: P_new(S) e γ ----------------------------------------
def figB2():
    """P_new(S) = probabilidade de o próximo passo introduzir local novo,
    como função de S(t)."""
    fig, ax = plt.subplots(figsize=(7, 5))

    print("\n[Fig B2] P_new(S) ~ S^(-γ) por indivíduo:")
    gammas = []
    for ind in INDIVIDUALS:
        cells, t = cells_data[ind]
        seen = set(); is_new = []; S_curr = []
        for c in cells:
            new = c not in seen
            S_curr.append(len(seen))
            is_new.append(int(new))
            seen.add(c)
        S_curr = np.array(S_curr)
        is_new = np.array(is_new)
        # Bin by S
        max_S = S_curr.max()
        if max_S < 30:
            continue
        S_bins = np.unique(np.logspace(np.log10(2), np.log10(max_S), 25).astype(int))
        S_bins = np.unique(np.clip(S_bins, 2, max_S))
        # For each bin, P_new = mean(is_new[S in bin])
        P_new = []
        S_mid = []
        for i in range(len(S_bins) - 1):
            mask = (S_curr >= S_bins[i]) & (S_curr < S_bins[i + 1])
            if mask.sum() >= 10:
                P_new.append(is_new[mask].mean())
                S_mid.append((S_bins[i] + S_bins[i + 1]) / 2)
        S_mid = np.array(S_mid); P_new = np.array(P_new)
        # Fit log P_new ~ -γ log S, only positive P_new
        valid = P_new > 0
        if valid.sum() < 5:
            continue
        slope, intercept, r, *_ = stats.linregress(np.log10(S_mid[valid]),
                                                    np.log10(P_new[valid]))
        gammas.append(-slope)
        ax.loglog(S_mid[valid], P_new[valid], "o-", ms=3, lw=0.6, alpha=0.6,
                  label=f"{ind} γ={-slope:.2f}")
    gamma_mean = np.mean(gammas); gamma_std = np.std(gammas)
    print(f"        γ médio = {gamma_mean:.3f} ± {gamma_std:.3f} (n={len(gammas)})")
    print(f"        comparação Song humanos: γ ≈ 0.21")

    ax.set_xlabel("S (locais já visitados)")
    ax.set_ylabel(r"$P_{\rm new}(S)$")
    ax.set_title(f"Fig. B2 — P_new(S) ~ S^(-γ)  ({GRID_M} m grid)")
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "figB2_Pnew_gamma.png", dpi=150)
    plt.close(fig)
    return gamma_mean, gamma_std


# ---------- Fig B3: relações escalares ----------------------------------
def figB3(mu, gamma):
    """Testes das 3 relações de Song: μ = β/(1+γ), ζ = 1+γ, β = μ·ζ.
    Usa ζ medido em A.fig5 (grid 500m); β estimado de waiting-time
    via tempo de permanência por célula.
    """
    print("\n[Fig B3] Relações escalares de Song:")
    # ζ measurement inline at grid 500m (top-50 ranks), per species
    all_ranks = []
    for ind in INDIVIDUALS:
        cells, _ = cells_data[ind]
        s = pd.Series(cells).value_counts()
        all_ranks.append(s.values)
    max_rank = max(len(r) for r in all_ranks)
    grid_ranks = np.arange(1, max_rank + 1)
    mean_freq = np.zeros(max_rank); n_contrib = np.zeros(max_rank)
    for r in all_ranks:
        mean_freq[:len(r)] += r
        n_contrib[:len(r)] += 1
    mean_freq /= np.maximum(n_contrib, 1)
    rk = grid_ranks[mean_freq > 0]; fr = mean_freq[mean_freq > 0]
    n_top = min(50, len(rk))
    slope, _, _, *_ = stats.linregress(np.log10(rk[:n_top]), np.log10(fr[:n_top]))
    zeta_anim = -slope

    # β: waiting time exponent from time-spent-per-cell
    waiting = []
    for ind in INDIVIDUALS:
        cells, t = cells_data[ind]
        # collapse consecutive same-cell into a single "stay"
        prev = None; t_in = None
        for c, ti in zip(cells, t):
            if c != prev:
                if prev is not None:
                    dur_s = (np.datetime64(ti) - np.datetime64(t_in)) \
                            .astype("timedelta64[s]").astype(float)
                    if dur_s > 0:
                        waiting.append(dur_s / 60.0)  # minutes
                prev = c
                t_in = ti
    waiting = np.array(waiting)
    waiting = waiting[waiting > 1]  # > 1 minute

    # MLE Clauset on waiting
    from _helpers import clauset_mle
    a_w, xmin_w, sa_w, ks_w, n_w = clauset_mle(waiting, min_tail=500)
    beta = a_w - 1 if a_w is not None else None  # Convention: P(Δt) ~ Δt^(-1-β)

    print(f"        ζ (animal, grid 500m) = {zeta_anim:.3f}")
    if beta is not None:
        print(f"        β (waiting-time, MLE) = {beta:.3f}")
    else:
        print("        β = N/A")
    print(f"        γ (animal) = {gamma:.3f}")
    print(f"        μ (animal) = {mu:.3f}")
    if beta is not None:
        print(f"        Predito por Song: μ = β/(1+γ) = {beta/(1+gamma):.3f} "
              f"(medido μ = {mu:.3f})")
    print(f"        Predito por Song: ζ = 1+γ = {1+gamma:.3f} "
          f"(medido ζ = {zeta_anim:.3f})")
    if beta is not None:
        print(f"        Identidade β = μζ ⟹ μζ = {mu*zeta_anim:.3f}, β = {beta:.3f}")

    # Plot waiting time distribution
    fig, ax = plt.subplots(figsize=(7, 5))
    from _helpers import log_bin_pdf
    centers, pdf = log_bin_pdf(waiting, n_bins=40)
    ax.loglog(centers, pdf, "o", color="C2", ms=4,
              label=f"Δt (n={len(waiting)})")
    if beta is not None:
        x_fit = np.logspace(np.log10(xmin_w), np.log10(centers.max()), 50)
        y_fit = (a_w - 1) * xmin_w ** (a_w - 1) * x_fit ** (-a_w)
        ax.loglog(x_fit, y_fit, "r--", lw=2,
                  label=f"MLE: 1+β = {a_w:.2f}±{sa_w:.2f}, β = {beta:.2f}")

    ax.set_xlabel(r"$\Delta t$ (minutos)")
    ax.set_ylabel(r"$P(\Delta t)$")
    ax.set_title("Fig. B3 — Waiting-time distribution + relações escalares")
    ax.grid(True, which="both", alpha=0.3)

    # Annotate scaling relations
    beta_str = f"{beta:.2f}" if beta is not None else "N/A"
    pred_mu = f"{beta/(1+gamma):.2f}" if beta is not None else "N/A"
    text = (f"ζ = {zeta_anim:.2f}  γ = {gamma:.2f}  μ = {mu:.2f}\n"
            f"β medido = {beta_str}\n"
            f"Song: β/(1+γ) = {pred_mu} (esperado μ)\n"
            f"Song: 1+γ = {1+gamma:.2f} (esperado ζ)\n"
            f"μ·ζ = {mu*zeta_anim:.2f} (esperado β)")
    ax.text(0.05, 0.05, text, transform=ax.transAxes, fontsize=9,
            verticalalignment="bottom", family="monospace",
            bbox=dict(facecolor="white", alpha=0.85, edgecolor="grey"))
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "figB3_scaling_relations.png", dpi=150)
    plt.close(fig)
    return beta, zeta_anim


if __name__ == "__main__":
    mu, mu_std = figB1()
    gamma, gamma_std = figB2()
    beta, zeta = figB3(mu, gamma)
    print(f"\n[Bloco B] figures em {OUT}")
