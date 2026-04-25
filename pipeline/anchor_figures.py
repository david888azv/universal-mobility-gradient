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
4 figuras-âncora cross-species do paper N6.

Pré-condição: ter rodado blocoA-D para todas as espécies em SPECIES_CONFIG.
Consolida resultados em 4 painéis comparativos para o paper.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

import os
# Don't lock to a single species
from _helpers import (FIG_BASE, SPECIES_CONFIG, load_data, per_indiv,
                       lonlat_to_xy, log_bin_pdf, clauset_mle,
                       M_PER_DEG_LAT)

OUT = FIG_BASE / "anchor"
OUT.mkdir(parents=True, exist_ok=True)

SPECIES_LIST = ["elephant", "gannet", "stork"]
SPECIES_COLOR = {"elephant": "#8B4513", "gannet": "#1f77b4", "stork": "#d62728"}
SPECIES_LABEL_SHORT = {"elephant": "Elefante", "gannet": "Gannet", "stork": "Cegonha"}
HUMAN_REF = "#2ca02c"


def load_species(species):
    """Load a species directly with its own ref center (override env var)."""
    cfg = SPECIES_CONFIG[species]
    csv = cfg["csv"]
    ref_lat = cfg["ref_lat"]; ref_lon = cfg["ref_lon"]
    df = pd.read_csv(csv, usecols=["timestamp", "location-long", "location-lat",
                                    "visible", "individual-local-identifier"],
                     parse_dates=["timestamp"])
    df = df[df["visible"]].copy()
    df = df.dropna(subset=["location-lat", "location-long"])
    m_lon = M_PER_DEG_LAT * np.cos(np.deg2rad(ref_lat))
    df["x"] = (df["location-long"] - ref_lon) * m_lon
    df["y"] = (df["location-lat"] - ref_lat) * M_PER_DEG_LAT
    df = df.sort_values(["individual-local-identifier",
                          "timestamp"]).reset_index(drop=True)
    return df


def step_lens_pooled(df):
    arrs = []
    for ind in df["individual-local-identifier"].unique():
        sub = df[df["individual-local-identifier"] == ind]
        x = sub["x"].values; y = sub["y"].values
        dx = np.diff(x); dy = np.diff(y)
        dr = np.sqrt(dx*dx + dy*dy)
        arrs.append(dr[dr > 0])
    return np.concatenate(arrs) if arrs else np.array([])


# Pré-computa os dados de cada espécie
print("loading 3 species ...")
data = {}
for sp in SPECIES_LIST:
    print(f"  {sp} ...")
    df = load_species(sp)
    sl = step_lens_pooled(df)
    data[sp] = {"df": df, "step_lens": sl}
    print(f"    {len(sl)} step-lengths, {df['individual-local-identifier'].nunique()} indiv")


# ---------- Anchor Fig 1: P(Δr) cross-species --------------------------
def fig1():
    fig, ax = plt.subplots(figsize=(8, 5.5))
    fits = {}
    for sp in SPECIES_LIST:
        sl = data[sp]["step_lens"]
        c, p = log_bin_pdf(sl, n_bins=50)
        ax.loglog(c, p, "o", color=SPECIES_COLOR[sp], ms=4,
                  label=SPECIES_LABEL_SHORT[sp])
        a, xm, sa, ks, n_tail = clauset_mle(sl, min_tail=200)
        fits[sp] = (a, xm, sa, ks)
        if a is not None:
            x_fit = np.logspace(np.log10(xm), np.log10(c.max()), 50)
            y_fit = (a-1) * xm**(a-1) * x_fit**(-a)
            ax.loglog(x_fit, y_fit, "--", color=SPECIES_COLOR[sp], lw=1.4, alpha=0.6)

    # Reference: human α ≈ 1.75 from González 2008
    ax.text(0.02, 0.05,
            "MLE Clauset (α ± SE):\n"
            + "\n".join(f"  {SPECIES_LABEL_SHORT[sp]}: α = {fits[sp][0]:.2f} ± {fits[sp][2]:.2f}, "
                        f"x_min = {fits[sp][1]:.0f} m"
                        for sp in SPECIES_LIST)
            + f"\n  Humano (González 2008): α ≈ 1.75",
            transform=ax.transAxes, fontsize=9, family="monospace",
            verticalalignment="bottom",
            bbox=dict(facecolor="white", alpha=0.9, edgecolor="grey"))
    ax.set_xlabel(r"$\Delta r$ (m)")
    ax.set_ylabel(r"$P(\Delta r)$")
    ax.set_title(r"Anchor Fig. 1 — P($\Delta r$) cross-species com fit MLE Clauset")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig1_step_length_xspecies.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig1")
    return fits


# ---------- Anchor Fig 2: Zipf gradient ---------------------------------
def fig2():
    fig, ax = plt.subplots(figsize=(7, 5))
    GRID_M = 500
    species_zetas = {}
    for sp in SPECIES_LIST:
        df = data[sp]["df"]
        all_ranks = []
        for ind in df["individual-local-identifier"].unique():
            sub = df[df["individual-local-identifier"] == ind]
            cx = (sub["x"].values // GRID_M).astype(int)
            cy = (sub["y"].values // GRID_M).astype(int)
            s = pd.Series(list(zip(cx, cy))).value_counts()
            all_ranks.append(s.values)
        max_rank = max(len(r) for r in all_ranks)
        ranks = np.arange(1, max_rank + 1)
        mean_freq = np.zeros(max_rank); n = np.zeros(max_rank)
        for r in all_ranks:
            mean_freq[:len(r)] += r; n[:len(r)] += 1
        mean_freq /= np.maximum(n, 1)
        valid = mean_freq > 0
        rk = ranks[valid]; fr = mean_freq[valid]
        n_top = min(50, len(rk))
        slope, *_ = stats.linregress(np.log10(rk[:n_top]), np.log10(fr[:n_top]))
        zeta = -slope
        species_zetas[sp] = zeta
        ax.loglog(rk, fr, "o-", ms=3, color=SPECIES_COLOR[sp], alpha=0.7,
                  label=f"{SPECIES_LABEL_SHORT[sp]}  ζ = {zeta:.2f}")

    # Human reference: 1/L (slope -1)
    rk_human = np.logspace(0, 3, 50)
    ax.loglog(rk_human, 100 / rk_human, "--", color=HUMAN_REF, lw=2,
              label="Humano (Gonzalez 08): ζ = 1.0")

    ax.set_xlabel("rank L do local")
    ax.set_ylabel("frequência média de visita")
    ax.set_title(f"Anchor Fig. 2 — Gradiente Zipf P(L)  (grid {GRID_M} m)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig2_zipf_gradient.png", dpi=160)
    plt.close(fig)
    print(f"  wrote anchor_fig2  (ζ: {species_zetas})")
    return species_zetas


# ---------- Anchor Fig 3: Song validity gradient ------------------------
def fig3(species_zetas):
    """Plot factor-of-error in Song's 3 scaling relations per species."""
    GRID_M = 500
    # Bring measurements from blocoB outputs (we ran them) — hardcode now.
    measurements = {
        "elephant": {"mu": 0.819, "gamma": 0.098, "beta": 1.370},
        "gannet":   {"mu": 0.934, "gamma": -0.128, "beta": 0.765},
        "stork":    {"mu": 1.979, "gamma": -0.569, "beta": 0.823},
        "human":    {"mu": 0.6,   "gamma": 0.21,  "beta": 0.8},
    }
    species_zetas["human"] = 1.2  # González/Song

    rels = ["μ = β/(1+γ)", "ζ = 1+γ", "β = μ·ζ"]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    species_order = ["elephant", "gannet", "stork", "human"]
    species_pos = np.arange(len(species_order))
    bar_w = 0.25
    for i, rel in enumerate(rels):
        ratios = []
        for sp in species_order:
            m = measurements[sp]; z = species_zetas[sp]
            if rel == "μ = β/(1+γ)":
                pred = m["beta"] / (1 + m["gamma"])
                meas = m["mu"]
            elif rel == "ζ = 1+γ":
                pred = 1 + m["gamma"]
                meas = z
            else:  # β = μ·ζ
                pred = m["mu"] * z
                meas = m["beta"]
            ratio = max(pred, meas) / min(abs(pred), abs(meas)) if min(abs(pred), abs(meas)) > 0.01 else np.nan
            ratios.append(ratio)
        ax.bar(species_pos + (i - 1) * bar_w, ratios, bar_w, label=rel)

    ax.axhline(1.0, color="green", ls="--", alpha=0.6, label="ratio = 1.0 (Song holds)")
    ax.set_yscale("log")
    ax.set_xticks(species_pos)
    ax.set_xticklabels(["Elefante", "Gannet", "Cegonha", "Humano"])
    ax.set_ylabel("ratio = max(pred, meas) / min(pred, meas)")
    ax.set_title("Anchor Fig. 3 — Validade das 3 relações escalares de Song por espécie")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig3_song_validity.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig3")


# ---------- Anchor Fig 4: η visitação --------------------------------
def fig4():
    """Bar plot η (lei de visitação) por espécie + linha de regime físico."""
    # Hardcode from blocoD outputs (T=120 days)
    etas = {
        "elephant": (0.90, 0.948),  # (η, R²)
        "gannet": (0.90, 0.809),
        "stork": (1.25, 0.933),
        "human": (2.05, 0.993),
    }
    fig, ax = plt.subplots(figsize=(7, 5))
    species_order = ["elephant", "gannet", "stork", "human"]
    labels = ["Elefante", "Gannet", "Cegonha", "Humano"]
    values = [etas[s][0] for s in species_order]
    colors = [SPECIES_COLOR.get(s, HUMAN_REF) for s in species_order]
    pos = np.arange(len(species_order))
    bars = ax.bar(pos, values, color=colors, alpha=0.85, edgecolor="black")
    for p, v, sp in zip(pos, values, species_order):
        ax.text(p, v + 0.05, f"η = {v:.2f}\nR² = {etas[sp][1]:.2f}",
                ha="center", va="bottom", fontsize=9)

    # Régimes físicos: η = 1 (custo linear, walking/flying const v) e η = 2 (cinético)
    ax.axhline(1.0, color="grey", ls=":", alpha=0.6,
                label="η = 1 (custo linear: walking/flying const v)")
    ax.axhline(2.0, color="green", ls=":", alpha=0.6,
                label="η = 2 (custo cinético: ½ρv² const)")

    ax.set_xticks(pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"η  ( $\rho \sim (rf)^{-\eta}$ )")
    ax.set_ylim(0, 2.5)
    ax.set_title("Anchor Fig. 4 — Expoente da lei de visitação η por espécie")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig4_eta_visitation.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig4")


if __name__ == "__main__":
    fits = fig1()
    zetas = fig2()
    fig3(zetas)
    fig4()
    print(f"\n4 anchor figures em {OUT}")
