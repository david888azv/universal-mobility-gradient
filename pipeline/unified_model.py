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
Modelo unificado Song-Alessandretti-Schläpfer (proof-of-concept).

Mecanismos integrados:
- Containers hierárquicos (Alessandretti): 4 níveis de scale aninhados
- EPR temporal (Song): P_new = ρ S^(-γ_CP), retorno preferencial Π_i = f_i
- Lei de visitação (Schläpfer): velocidade v(r) controla η

Parâmetros do modelo (apenas dois variam por espécie):
- γ_CP ∈ [0, 0.4] : strength of preferential return → controla ζ
- η_v ∈ [0, 1.5] : heterogeneidade de v com r → controla η

Com (γ_CP, η_v) ajustados, devemos reproduzir:
- Elefante  ≈ (0.05, 0.0)   → ζ ≈ 0.3, η ≈ 1.0
- Gannet    ≈ (0.20, 0.0)   → ζ ≈ 0.7, η ≈ 1.0
- Cegonha   ≈ (0.30, 0.1)   → ζ ≈ 1.0, η ≈ 1.1
- Humano    ≈ (0.21, 1.0)   → ζ ≈ 1.0, η ≈ 2.0

Saída: heatmaps ζ(γ_CP, η_v) e η(γ_CP, η_v) + posições das 4 espécies.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from _helpers import FIG_BASE

OUT = FIG_BASE / "unified_model"
OUT.mkdir(parents=True, exist_ok=True)


# Hierarquia de containers: 4 níveis com tamanhos típicos (m)
LEVELS = [50, 500, 5000, 50000]   # quarto, bairro, cidade, região
LEVEL_PROBS = [0.50, 0.30, 0.15, 0.05]  # probabilidade de explorar em cada nível


def simulate_agent(n_steps, gamma_cp, eta_v, rho=0.6, seed=None):
    """
    Simula trajetória de 1 agente com:
    - P_new = rho * S^(-gamma_cp)
    - retorno preferencial proportional a f_i
    - velocidade v ~ r^(eta_v / 2) (custo cinético se eta_v=1)

    Retorna lista de coordenadas (x, y) e contagem visitas por cell.
    """
    rng = np.random.default_rng(seed)
    home = (0.0, 0.0)
    positions = [home]
    visits = {(0, 0): 1}  # cell at 50 m grid

    for step in range(1, n_steps):
        S = len(visits)
        p_new = rho * S ** (-gamma_cp)
        if rng.random() < p_new:
            # Explore new location: pick a hierarchy level
            level = rng.choice(len(LEVELS), p=LEVEL_PROBS)
            scale = LEVELS[level]
            theta = 2 * np.pi * rng.random()
            r = scale * rng.lognormal(0, 0.5)  # lognormal jump within level
            # Velocity heterogeneity: longer trips move faster (motorized) if eta_v>0
            # We model "effective r" = r * v_factor, where v ~ r^(eta_v/2)
            r_eff = r * (1 + r / 1000) ** (eta_v / 2.0)
            x = positions[-1][0] + r_eff * np.cos(theta)
            y = positions[-1][1] + r_eff * np.sin(theta)
        else:
            # Preferential return: pick one of the visited cells weighted by visits
            cells = list(visits.keys())
            weights = np.array([visits[c] for c in cells], dtype=float)
            weights /= weights.sum()
            idx = rng.choice(len(cells), p=weights)
            cell = cells[idx]
            # Random position within the chosen cell
            x = cell[0] * 50 + rng.uniform(0, 50)
            y = cell[1] * 50 + rng.uniform(0, 50)

        positions.append((x, y))
        # Update visit counts
        cx, cy = int(x // 50), int(y // 50)
        visits[(cx, cy)] = visits.get((cx, cy), 0) + 1

    return positions, visits


def measure_zeta(visits, n_top=50):
    """ζ from top-50 ranks of pooled visits."""
    counts = np.array(sorted(visits.values(), reverse=True))
    if len(counts) < 5:
        return None
    n_top = min(n_top, len(counts))
    rk = np.arange(1, n_top + 1)
    fr = counts[:n_top]
    if (fr <= 0).any():
        return None
    slope, *_ = stats.linregress(np.log10(rk), np.log10(fr))
    return -slope


def measure_eta(positions_list, visits_list):
    """η from rho(r,f) ~ (rf)^(-eta) for ensemble of agents.
    Each agent contributes (cell, r_from_home, freq) tuples.
    """
    rows = []
    for positions, visits in zip(positions_list, visits_list):
        if not visits:
            continue
        # home = modal cell
        home_cell = max(visits.keys(), key=lambda k: visits[k])
        hx, hy = home_cell
        for cell, n in visits.items():
            r_grid = np.sqrt((cell[0] - hx)**2 + (cell[1] - hy)**2)
            r_meters = r_grid * 50
            if r_meters > 0:
                rows.append((r_meters / 1000, n))  # r in km, n as freq
    if len(rows) < 50:
        return None
    rs, fs = zip(*rows)
    rf = np.array(rs) * np.array(fs)
    edges = np.logspace(np.log10(max(rf.min(), 0.001)),
                         np.log10(rf.max()), 30)
    cnts, _ = np.histogram(rf, bins=edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    widths = np.diff(edges)
    pdf = cnts / (widths * cnts.sum())
    rf_min, rf_max = np.percentile(rf, [10, 90])
    m = (centers >= rf_min) & (centers <= rf_max) & (pdf > 0)
    if m.sum() < 5:
        return None
    slope, *_ = stats.linregress(np.log10(centers[m]), np.log10(pdf[m]))
    return -slope


def sweep_2d(gamma_grid, eta_grid, n_agents=50, n_steps=2000):
    """Sweep (γ_CP, η_v) parameter space."""
    Z = np.zeros((len(eta_grid), len(gamma_grid)))
    H = np.zeros((len(eta_grid), len(gamma_grid)))
    for i, eta_v in enumerate(eta_grid):
        for j, gamma_cp in enumerate(gamma_grid):
            positions_all = []
            visits_all = []
            for k in range(n_agents):
                pos, v = simulate_agent(n_steps, gamma_cp, eta_v,
                                          seed=int(1000*eta_v + 100*gamma_cp + k))
                positions_all.append(pos)
                visits_all.append(v)
            # Pool visits across agents
            pooled = {}
            for v in visits_all:
                for c, n in v.items():
                    pooled[c] = pooled.get(c, 0) + n
            zeta = measure_zeta(pooled)
            eta = measure_eta(positions_all, visits_all)
            Z[i, j] = zeta if zeta is not None else np.nan
            H[i, j] = eta if eta is not None else np.nan
            print(f"    γ_CP={gamma_cp:.2f}  η_v={eta_v:.2f}  →  ζ={zeta:.2f}  η={eta:.2f}")
    return Z, H


# Empirical species values
SPECIES_PARAMS = {
    "Elefante": {"zeta": 0.28, "eta": 1.03, "color": "#8B4513"},
    "Gannet":   {"zeta": 0.89, "eta": 0.65, "color": "#1f77b4"},
    "Cegonha":  {"zeta": 0.86, "eta": 1.09, "color": "#d62728"},
    "Humano":   {"zeta": 1.00, "eta": 2.05, "color": "#2ca02c"},
}


def fit_species_to_grid(zeta_grid, eta_grid, Z, H, target_zeta, target_eta):
    """Find (γ_CP, η_v) closest to (target_zeta, target_eta)."""
    diff = (Z - target_zeta) ** 2 + (H - target_eta) ** 2
    if np.all(np.isnan(diff)):
        return None, None
    idx = np.unravel_index(np.nanargmin(diff), diff.shape)
    return zeta_grid[idx[1]], eta_grid[idx[0]]  # γ_CP, η_v


def plot_heatmaps(gamma_grid, eta_grid, Z, H):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Plot ζ heatmap
    im0 = axes[0].imshow(Z, origin="lower", aspect="auto",
                          extent=[gamma_grid[0], gamma_grid[-1],
                                   eta_grid[0], eta_grid[-1]],
                          cmap="viridis", vmin=0, vmax=1.5)
    axes[0].set_xlabel(r"$\gamma_{CP}$  (preferential-return strength)")
    axes[0].set_ylabel(r"$\eta_v$  (velocity heterogeneity)")
    axes[0].set_title(r"$\zeta$ predicted by unified model")
    plt.colorbar(im0, ax=axes[0])

    # Plot η heatmap
    im1 = axes[1].imshow(H, origin="lower", aspect="auto",
                          extent=[gamma_grid[0], gamma_grid[-1],
                                   eta_grid[0], eta_grid[-1]],
                          cmap="plasma", vmin=0.5, vmax=2.5)
    axes[1].set_xlabel(r"$\gamma_{CP}$")
    axes[1].set_ylabel(r"$\eta_v$")
    axes[1].set_title(r"$\eta$ predicted by unified model")
    plt.colorbar(im1, ax=axes[1])

    # Place species in both panels using fitted parameters
    print("\nFitting empirical species to model grid:")
    for name, p in SPECIES_PARAMS.items():
        gamma_fit, eta_v_fit = fit_species_to_grid(gamma_grid, eta_grid, Z, H,
                                                     p["zeta"], p["eta"])
        if gamma_fit is None:
            continue
        for ax in axes:
            ax.scatter([gamma_fit], [eta_v_fit], s=180, color=p["color"],
                        edgecolors="white", linewidths=2, zorder=5)
            ax.annotate(name, (gamma_fit, eta_v_fit),
                          xytext=(8, 8), textcoords="offset points",
                          color="white", fontsize=11, weight="bold")
        print(f"  {name}: γ_CP={gamma_fit:.2f}, η_v={eta_v_fit:.2f}  "
              f"(target ζ={p['zeta']:.2f}, η={p['eta']:.2f})")

    fig.suptitle("Modelo unificado Song-Alessandretti-Schläpfer  —  "
                  "espaço de parâmetros (γ_CP, η_v)", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "unified_model_heatmaps.png", dpi=160)
    plt.close(fig)
    print(f"  wrote {OUT}/unified_model_heatmaps.png")


if __name__ == "__main__":
    print("[unified] sweeping 2D parameter space ...")
    gamma_grid = np.linspace(0.0, 0.4, 9)
    eta_grid = np.linspace(0.0, 1.5, 7)
    Z, H = sweep_2d(gamma_grid, eta_grid, n_agents=30, n_steps=1500)
    plot_heatmaps(gamma_grid, eta_grid, Z, H)
    np.savez(OUT / "sweep_data.npz",
             gamma_grid=gamma_grid, eta_grid=eta_grid, Z=Z, H=H)
    print(f"\n[unified] data + figs em {OUT}")
