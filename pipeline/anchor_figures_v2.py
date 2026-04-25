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
Versão final das 4 figuras-âncora com IC bootstrap incluídos.

Pré-condição: rodar bootstrap.py para 3 espécies (gera bootstrap_*.md).
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re

from _helpers import FIG_BASE

OUT = FIG_BASE / "anchor"
OUT.mkdir(parents=True, exist_ok=True)

SPECIES_LIST = ["elephant", "gannet", "stork"]
SPECIES_COLOR = {"elephant": "#8B4513", "gannet": "#1f77b4", "stork": "#d62728"}
SPECIES_LABEL = {"elephant": "Elefante", "gannet": "Gannet", "stork": "Cegonha"}
HUMAN_COLOR = "#2ca02c"


def load_bootstrap(species):
    path = FIG_BASE / f"bootstrap_{species}.md"
    out = {}
    text = path.read_text()
    ci_pat = re.compile(r"\[([\-\d\.]+),\s*([\-\d\.]+)\]")
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "Métrica" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 4:
            continue
        # First column starts with the Greek symbol
        sym = cols[0].lstrip().split()[0] if cols[0].lstrip() else ""
        if sym not in "αζμγβη":
            continue
        try:
            mean = float(cols[1]); se = float(cols[2])
            ci = ci_pat.search(cols[3])
            if ci:
                lo, hi = float(ci.group(1)), float(ci.group(2))
                out[sym] = (mean, se, lo, hi)
        except (ValueError, IndexError):
            pass
    return out


# Human reference values (from published papers)
HUMAN_REF = {
    "α": (1.75, 0.15, 1.45, 2.05),    # González 2008 (β=1.75, treated as α here)
    "ζ": (1.20, 0.10, 1.0, 1.40),     # Song 2010 / Gonzalez 2008 (1/L → 1)
    "μ": (0.60, 0.02, 0.56, 0.64),    # Song 2010
    "γ": (0.21, 0.02, 0.17, 0.25),    # Song 2010
    "β": (0.80, 0.10, 0.6, 1.0),      # Song 2010
    "η": (2.05, 0.018, 2.014, 2.086), # Schläpfer 2021
}

print("loading bootstraps ...")
boot = {sp: load_bootstrap(sp) for sp in SPECIES_LIST}
boot["human"] = HUMAN_REF


# ---------- Anchor Fig 2 v2: ζ gradient with CI ------------------------
def fig2_v2():
    """ζ as bar plot with error bars, ordered by behavioral CP-strength."""
    fig, ax = plt.subplots(figsize=(7.5, 5))
    species_order = ["elephant", "gannet", "stork", "human"]
    labels = ["Elefante", "Gannet", "Cegonha", "Humano"]
    colors = [SPECIES_COLOR.get(s, HUMAN_COLOR) for s in species_order]

    means, errs_lo, errs_hi = [], [], []
    for sp in species_order:
        m, _, lo, hi = boot[sp]["ζ"]
        means.append(m); errs_lo.append(m - lo); errs_hi.append(hi - m)

    pos = np.arange(len(species_order))
    bars = ax.bar(pos, means, color=colors, alpha=0.85, edgecolor="black",
                   yerr=[errs_lo, errs_hi], capsize=8)
    for p, v in zip(pos, means):
        ax.text(p, v + 0.05, f"{v:.2f}", ha="center", va="bottom", fontsize=10)

    ax.axhline(1.0, color="grey", ls=":", alpha=0.5,
                label=r"$\zeta = 1$ (Zipf clean)")

    ax.set_xticks(pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$\zeta$  ( $P(L) \sim L^{-\zeta}$, top-50 ranks )")
    ax.set_ylim(0, max(means) * 1.25)
    ax.set_title("Anchor Fig. 2 — Gradiente Zipf ζ por espécie (IC 95% bootstrap)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig2_v2_zipf_ci.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig2_v2 (ζ with CI)")


# ---------- Anchor Fig 3 v2: Song validity with CI ----------------------
def fig3_v2():
    """Song's 3 relations: ratio with bootstrap propagation."""
    species_order = ["elephant", "gannet", "stork", "human"]
    labels = ["Elefante", "Gannet", "Cegonha", "Humano"]

    rels = ["μ = β/(1+γ)", "ζ = 1+γ", "β = μζ"]
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    pos = np.arange(len(species_order))
    bar_w = 0.25

    rng = np.random.default_rng(0)

    for i, rel in enumerate(rels):
        ratios_mean, ratios_lo, ratios_hi = [], [], []
        for sp in species_order:
            d = boot[sp]
            mu_m, mu_se = d["μ"][0], d["μ"][1]
            g_m, g_se = d["γ"][0], d["γ"][1]
            b_m, b_se = d["β"][0], d["β"][1]
            z_m, z_se = d["ζ"][0], d["ζ"][1]
            # Propagate via Monte Carlo
            samples = []
            for _ in range(2000):
                mu = rng.normal(mu_m, mu_se)
                g = rng.normal(g_m, g_se)
                b = rng.normal(b_m, b_se)
                z = rng.normal(z_m, z_se)
                if rel.startswith("μ"):
                    pred = b / (1 + g) if (1 + g) != 0 else np.nan
                    meas = mu
                elif rel.startswith("ζ"):
                    pred = 1 + g
                    meas = z
                else:
                    pred = mu * z
                    meas = b
                if min(abs(pred), abs(meas)) > 0.01:
                    r = max(abs(pred), abs(meas)) / min(abs(pred), abs(meas))
                    if np.isfinite(r):
                        samples.append(r)
            if samples:
                ratios_mean.append(np.median(samples))
                ratios_lo.append(np.median(samples) - np.percentile(samples, 2.5))
                ratios_hi.append(np.percentile(samples, 97.5) - np.median(samples))
            else:
                ratios_mean.append(np.nan)
                ratios_lo.append(0); ratios_hi.append(0)
        ax.bar(pos + (i - 1) * bar_w, ratios_mean, bar_w, label=rel,
                yerr=[ratios_lo, ratios_hi], capsize=4, error_kw=dict(lw=0.8))

    ax.axhline(1.0, color="green", ls="--", alpha=0.6, label="Song holds (ratio=1)")
    ax.set_yscale("log")
    ax.set_xticks(pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel("ratio = max(pred, meas) / min(pred, meas)")
    ax.set_title("Anchor Fig. 3 — Validade das relações de Song por espécie (IC 95%)")
    ax.grid(True, axis="y", which="both", alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig3_v2_song_ci.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig3_v2 (Song with CI)")


# ---------- Anchor Fig 4 v2: η visitation with CI ----------------------
def fig4_v2():
    species_order = ["elephant", "gannet", "stork", "human"]
    labels = ["Elefante", "Gannet", "Cegonha", "Humano"]
    colors = [SPECIES_COLOR.get(s, HUMAN_COLOR) for s in species_order]

    means, errs_lo, errs_hi = [], [], []
    for sp in species_order:
        m, _, lo, hi = boot[sp]["η"]
        means.append(m); errs_lo.append(m - lo); errs_hi.append(hi - m)

    fig, ax = plt.subplots(figsize=(7.5, 5))
    pos = np.arange(len(species_order))
    ax.bar(pos, means, color=colors, alpha=0.85, edgecolor="black",
            yerr=[errs_lo, errs_hi], capsize=8)
    for p, v in zip(pos, means):
        ax.text(p, v + 0.07, f"η = {v:.2f}", ha="center", va="bottom", fontsize=10)

    ax.axhline(1.0, color="grey", ls=":", alpha=0.6,
                label=r"$\eta = 1$ (custo linear; v const)")
    ax.axhline(2.0, color="green", ls=":", alpha=0.6,
                label=r"$\eta = 2$ (custo cinético; ½ρv²)")

    ax.set_xticks(pos)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$\eta$  ( $\rho \sim (rf)^{-\eta}$ )")
    ax.set_ylim(0, 2.5)
    ax.set_title("Anchor Fig. 4 — Expoente da lei de visitação η (IC 95% bootstrap)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig4_v2_eta_ci.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig4_v2 (η with CI)")


# ---------- Anchor Fig 5 (NEW): 2D parameter space (ζ, η) -------------
def fig5_2d_space():
    """Sketch the 2D phase diagram: η vs ζ; place 4 species."""
    fig, ax = plt.subplots(figsize=(7.5, 6))

    species_order = ["elephant", "gannet", "stork", "human"]
    species_labels = ["Elefante", "Gannet", "Cegonha", "Humano"]
    colors = [SPECIES_COLOR.get(s, HUMAN_COLOR) for s in species_order]

    for sp, label, col in zip(species_order, species_labels, colors):
        d = boot[sp]
        z_m, _, z_lo, z_hi = d["ζ"]
        e_m, _, e_lo, e_hi = d["η"]
        ax.errorbar([z_m], [e_m],
                     xerr=[[z_m - z_lo], [z_hi - z_m]],
                     yerr=[[e_m - e_lo], [e_hi - e_m]],
                     fmt="o", ms=14, color=col, ecolor="grey",
                     capsize=6, elinewidth=1.5, label=label)
        ax.annotate(label, (z_m, e_m), xytext=(8, 8),
                     textcoords="offset points", fontsize=11)

    # Behavioral regime regions (visual annotations)
    ax.axhspan(0.7, 1.25, alpha=0.05, color="grey")
    ax.axhspan(1.75, 2.25, alpha=0.05, color="green")
    ax.text(0.05, 1.1, "regime walking/flying\n(η ≈ 1)", fontsize=8, color="grey")
    ax.text(0.05, 2.1, "regime motorizado\n(η ≈ 2)", fontsize=8, color="green")
    ax.text(0.95, 0.5, "no-CP", ha="right", fontsize=8, color="grey")
    ax.text(1.0, 0.5, "obligate-CP", ha="left", fontsize=8, color="grey")

    ax.set_xlabel(r"$\zeta$  (CP-strength)")
    ax.set_ylabel(r"$\eta$  (velocity-heterogeneity)")
    ax.set_title("Anchor Fig. 5 — Espaço de fase comportamental (ζ, η)")
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 2.5)
    ax.grid(True, alpha=0.3)
    ax.axvline(1.0, color="grey", ls=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(OUT / "anchor_fig5_phase_space.png", dpi=160)
    plt.close(fig)
    print("  wrote anchor_fig5 (2D phase space)")


if __name__ == "__main__":
    fig2_v2()
    fig3_v2()
    fig4_v2()
    fig5_2d_space()
    print(f"\n5 figs em {OUT}")
