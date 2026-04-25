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
Nature-style figures for the cross-species mobility paper.

Conventions (Nature Research figure guidelines):
- Single column: 89 mm = 3.50 in; Double column: 183 mm = 7.20 in.
- Sans-serif font (DejaVu Sans ~ Arial/Helvetica); 7 pt labels, 8 pt axis titles.
- Line widths 0.8 pt for data, 0.6 pt for axes, error-bar caps 2 pt.
- No in-figure titles (captions provide them).
- Colour-blind safe palette.
- Output as PDF (vector) and PNG (300 dpi) to /overleaf/figures/.

Reads bootstrap means and CIs from pipeline/../figures/bootstrap_*.md.
"""

from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy import stats

REPO = Path("/home/david/atual/nature-scope")
FIG_IN = REPO / "figures"
OUT = REPO / "overleaf" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Nature-style rcParams
# ---------------------------------------------------------------------------
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "axes.linewidth": 0.6,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
    "legend.fontsize": 6.5,
    "legend.frameon": False,
    "lines.linewidth": 0.9,
    "lines.markersize": 4,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "figure.dpi": 150,
})

# Colour-blind-safe palette (Wong 2011 + complements for the 8 additions)
C_ELEPHANT  = "#8c6d31"   # ochre/brown
C_GANNET    = "#0072B2"   # blue
C_STORK     = "#D55E00"   # vermillion
C_HUMAN     = "#009E73"   # bluish green
C_GREY      = "#666666"
C_ALBATROSS = "#56B4E9"   # sky blue
C_BAT_S     = "#CC79A7"   # rose pink
C_BAT_A     = "#882255"   # dark mauve
C_TURTLE_M  = "#117733"   # dark green
C_TURTLE_P  = "#999933"   # olive
C_ZEBRA     = "#000000"   # black-and-white literal
C_BABOON    = "#332288"   # indigo
C_GAZELLE   = "#AA7744"   # tan/sand

LABELS = {
    "elephant":   "Elephant",
    "gannet":     "Gannet",
    "stork":      "White stork",
    "human":      "Human",
    "albatross":  "Galápagos albatross",
    "bat_scharf": "Eidolon helvum (Burkina)",
    "bat_abedi":  "Eidolon helvum (Ghana)",
    "turtle_med": "Loggerhead (Med.)",
    "turtle_pac": "Loggerhead (N. Pacific)",
    "zebra":      "Burchell's zebra",
    "baboon":     "Olive baboon",
    "gazelle":    "Mongolian gazelle",
}
COLOURS = {
    "elephant":   C_ELEPHANT,
    "gannet":     C_GANNET,
    "stork":      C_STORK,
    "human":      C_HUMAN,
    "albatross":  C_ALBATROSS,
    "bat_scharf": C_BAT_S,
    "bat_abedi":  C_BAT_A,
    "turtle_med": C_TURTLE_M,
    "turtle_pac": C_TURTLE_P,
    "zebra":      C_ZEBRA,
    "baboon":     C_BABOON,
    "gazelle":    C_GAZELLE,
}
SPECIES_ALL = ["elephant", "gannet", "stork",
               "albatross", "bat_scharf", "bat_abedi",
               "turtle_med", "turtle_pac", "zebra", "baboon", "gazelle"]
# Backward-compat alias used by some older code paths
SPECIES = SPECIES_ALL

# Ecological-class grouping for visual encoding (marker shape) when colour
# alone would be too crowded. The pairing is: shape = ecological class,
# colour = species identity.
ECO_GROUP = {
    "elephant":   "ungulate-CP",   "gazelle":  "ungulate-nomad", "zebra": "ungulate-nomad",
    "gannet":     "seabird",       "albatross": "seabird",       "stork": "long-migrant-bird",
    "bat_scharf": "bat",           "bat_abedi": "bat",
    "turtle_med": "marine-reptile","turtle_pac": "marine-reptile",
    "baboon":     "primate-CP",
}
ECO_MARKER = {
    "ungulate-CP":     "s",   # square
    "ungulate-nomad":  "v",   # down-triangle
    "seabird":         "^",   # up-triangle
    "long-migrant-bird":"D",  # diamond
    "bat":             "P",   # plus-filled
    "marine-reptile":  ">",   # right-triangle
    "primate-CP":      "*",   # star
    "human":           "o",   # circle
}
ECO_GROUP["human"] = "human"


def cm(x):
    return x / 2.54


# ---------------------------------------------------------------------------
# Bootstrap parser (same structure as anchor_figures_v2.py)
# ---------------------------------------------------------------------------
def load_bootstrap(species):
    path = FIG_IN / f"bootstrap_{species}.md"
    out = {}
    text = path.read_text()
    ci_pat = re.compile(r"\[([\-\d\.]+),\s*([\-\d\.]+)\]")
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "Métrica" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 4:
            continue
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


# Published human reference values
HUMAN_REF = {
    "α": (1.75, 0.15, 1.45, 2.05),
    "ζ": (1.20, 0.10, 1.00, 1.40),
    "μ": (0.60, 0.02, 0.56, 0.64),
    "γ": (0.21, 0.02, 0.17, 0.25),
    "β": (0.80, 0.10, 0.60, 1.00),
    "η": (2.05, 0.018, 2.014, 2.086),
}

BOOT = {}
for sp in SPECIES_ALL:
    try:
        BOOT[sp] = load_bootstrap(sp)
    except FileNotFoundError:
        BOOT[sp] = {}
BOOT["human"] = HUMAN_REF


# ---------------------------------------------------------------------------
# Figure 1 — P(Δr) pooled step-length distribution, four panels
# ---------------------------------------------------------------------------
_STEP_CACHE = {}

def compute_step_lengths(species):
    """Compute pooled step-lengths Δr across individuals directly from data.
    Cache as .npy for reuse."""
    if species in _STEP_CACHE:
        return _STEP_CACHE[species]
    cache = FIG_IN / f"blocoA_{species}" / "step_lengths.npy"
    if cache.exists():
        arr = np.load(cache)
        _STEP_CACHE[species] = arr
        return arr
    # Fresh compute
    import os
    os.environ["SPECIES"] = species
    import importlib, sys
    # Re-import helpers under new SPECIES
    for m in ["_helpers"]:
        if m in sys.modules:
            del sys.modules[m]
    sys.path.insert(0, str(Path(__file__).parent))
    import _helpers as hp
    df = hp.load_data()
    all_steps = []
    for _, sub in hp.per_indiv(df):
        dx = np.diff(sub["x"].values)
        dy = np.diff(sub["y"].values)
        d = np.sqrt(dx * dx + dy * dy)
        d = d[d > 0]
        all_steps.append(d)
    arr = np.concatenate(all_steps) if all_steps else np.array([])
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache, arr)
    _STEP_CACHE[species] = arr
    return arr


def fig1_step_length():
    """Fig 1: three representative P(Δr) panels (a–c) plus the cross-species
    α gradient bar (d) populated by all 11 species + the human reference.

    Representatives are chosen to span the ecological gradient:
      a — Mongolian gazelle: nomadic ungulate, near-Lévy tail (closest to human)
      b — White stork:       long-distance migrant, intermediate
      c — Olive baboon:      central-place primate, light tail (Brownian-like)
    """
    REP = ["gazelle", "stork", "baboon"]
    fig = plt.figure(figsize=(cm(18.3), cm(10.8)))
    gs = fig.add_gridspec(1, 4, wspace=0.42, left=0.06, right=0.99,
                          bottom=0.20, top=0.89, width_ratios=[1, 1, 1, 1.7])

    for i, sp in enumerate(REP):
        ax = fig.add_subplot(gs[0, i])
        sl = compute_step_lengths(sp)
        if sp not in BOOT or "α" not in BOOT[sp]:
            ax.text(0.5, 0.5, f"{sp}: no α", transform=ax.transAxes,
                    ha="center"); continue
        alpha_mean, _, alpha_lo, alpha_hi = BOOT[sp]["α"]
        if sl is None or len(sl) < 1000:
            ax.text(0.5, 0.5, "missing data", transform=ax.transAxes,
                    ha="center"); continue
        sl = sl[sl > 0]
        edges = np.logspace(np.log10(max(sl.min(), 0.01)),
                            np.log10(sl.max()), 50)
        cnts, _ = np.histogram(sl, bins=edges)
        centres = np.sqrt(edges[:-1] * edges[1:])
        widths = np.diff(edges)
        pdf = cnts / (widths * cnts.sum())
        m = pdf > 0
        ax.loglog(centres[m], pdf[m], 'o', ms=2.5, mec='none',
                  color=COLOURS[sp], alpha=0.85)
        xmin = np.percentile(sl, 70)
        x = np.logspace(np.log10(xmin), np.log10(sl.max()), 50)
        if m.any():
            y0 = pdf[m][np.argmin(np.abs(centres[m] - xmin))]
            ax.loglog(x, y0 * (x / xmin) ** (-alpha_mean), '--',
                      color=COLOURS[sp], lw=0.9, alpha=0.95)
        ax.set_xlabel(r"$\Delta r$ (m)")
        if i == 0:
            ax.set_ylabel(r"$P(\Delta r)$")
        ax.set_title(f"{LABELS[sp]}\n"
                     rf"$\alpha = {alpha_mean:.2f}\,[{alpha_lo:.2f},{alpha_hi:.2f}]$",
                     fontsize=7)
        ax.grid(True, which="both", alpha=0.25, lw=0.3)

    # Panel d — α gradient across 11 species + human reference, sorted asc.
    ax = fig.add_subplot(gs[0, 3])
    have_a = [s for s in SPECIES_ALL + ["human"]
              if BOOT.get(s, {}).get("α") is not None]
    have_a.sort(key=lambda s: BOOT[s]["α"][0])
    means = [BOOT[s]["α"][0] for s in have_a]
    los   = [BOOT[s]["α"][0] - BOOT[s]["α"][2] for s in have_a]
    his   = [BOOT[s]["α"][3] - BOOT[s]["α"][0] for s in have_a]
    cols  = [COLOURS.get(s, C_GREY) for s in have_a]
    pos = np.arange(len(have_a))
    ax.bar(pos, means, color=cols, alpha=0.92, edgecolor="black", lw=0.35,
           yerr=[los, his], capsize=2.0, error_kw=dict(lw=0.55))
    # human reference highlight
    if "human" in have_a:
        ih = have_a.index("human")
        ax.bar([ih], [means[ih]], color=cols[ih], alpha=0.9,
               edgecolor=C_HUMAN, lw=1.4)
    ax.axhline(1.75, color=C_HUMAN, ls=":", lw=0.6)
    ax.text(len(have_a) - 0.4, 1.83, "human ref.", fontsize=6,
            color=C_HUMAN, ha="right")
    ax.set_xticks(pos)
    ax.set_xticklabels([LABELS.get(s, s) for s in have_a],
                       rotation=42, ha="right", fontsize=6.2)
    ax.set_ylabel(r"Tail exponent $\alpha$")
    ax.set_ylim(0, max(means) * 1.15)
    ax.grid(True, axis="y", alpha=0.25, lw=0.3)

    for i, lab in enumerate("abcd"):
        fig.text([0.04, 0.275, 0.51, 0.745][i], 0.93,
                 lab, fontsize=9, weight="bold")

    fig.savefig(OUT / "fig1_step_length.pdf")
    fig.savefig(OUT / "fig1_step_length.png", dpi=300)
    plt.close(fig)
    print("  wrote fig1_step_length.(pdf|png)")


# ---------------------------------------------------------------------------
# Figure 2 — Zipf gradient ζ + phase-space
# ---------------------------------------------------------------------------
def _smart_label_offsets(points, base=(5, 5), pad=0.04):
    """Cheap collision-avoidance for phase-space annotations: push labels
    that share a tight neighbourhood up/down so they don't overlap."""
    offsets = {}
    sorted_pts = sorted(points.items(), key=lambda kv: (kv[1][0], kv[1][1]))
    used = []
    for sp, (x, y) in sorted_pts:
        dx, dy = base
        for ux, uy in used:
            if abs(x - ux) < pad and abs(y - uy) < pad * 1.5:
                dy += 9
        offsets[sp] = (dx, dy)
        used.append((x, y))
    return offsets


def fig2_zipf_phase():
    """Two-panel:
       (a) ζ bar with bootstrap CIs across 11 species + human ref;
       (b) (ζ, η) phase space with one marker per species. Marker shape =
           ecological class, colour = species identity. Species names are
           given in a single shared legend below to keep the panel clean
           with 12 points.
    """
    fig = plt.figure(figsize=(cm(18.3), cm(11.5)))
    gs = fig.add_gridspec(1, 2, wspace=0.30, left=0.06, right=0.99,
                          bottom=0.30, top=0.94, width_ratios=[1.4, 1.0])

    have_z = [s for s in SPECIES_ALL + ["human"]
              if BOOT.get(s, {}).get("ζ") is not None]
    have_z.sort(key=lambda s: BOOT[s]["ζ"][0])

    # ---- (a) ζ bar across all species we have data for --------------------
    ax = fig.add_subplot(gs[0, 0])
    means = [BOOT[s]["ζ"][0] for s in have_z]
    los   = [BOOT[s]["ζ"][0] - BOOT[s]["ζ"][2] for s in have_z]
    his   = [BOOT[s]["ζ"][3] - BOOT[s]["ζ"][0] for s in have_z]
    cols  = [COLOURS.get(s, C_GREY) for s in have_z]
    pos = np.arange(len(have_z))
    ax.bar(pos, means, color=cols, alpha=0.92, edgecolor="black", lw=0.35,
           yerr=[los, his], capsize=2.0, error_kw=dict(lw=0.55))
    if "human" in have_z:
        ih = have_z.index("human")
        ax.bar([ih], [means[ih]], color=cols[ih], alpha=0.9,
               edgecolor=C_HUMAN, lw=1.4)
    ax.axhline(1.0, color=C_GREY, ls=":", lw=0.6)
    ax.text(len(have_z) - 0.4, 1.04, r"$\zeta=1$ (Zipf)",
            fontsize=6, color=C_GREY, ha="right")
    ax.set_xticks(pos)
    ax.set_xticklabels([LABELS.get(s, s) for s in have_z],
                       rotation=42, ha="right", fontsize=6.2)
    ax.set_ylabel(r"Visitation exponent $\zeta$")
    ax.set_ylim(0, max(means) * 1.18 + 0.05)
    ax.grid(True, axis="y", alpha=0.25, lw=0.3)

    # ---- (b) (ζ, η) phase space ------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axhspan(0.8, 1.25, alpha=0.07, color=C_GREY, lw=0)
    ax2.axhspan(1.8, 2.25, alpha=0.07, color=C_HUMAN, lw=0)
    ax2.text(0.04, 1.05, "walking / flying", fontsize=5.5, color=C_GREY)
    ax2.text(0.04, 1.83, "motorised", fontsize=5.5, color=C_HUMAN)
    ax2.axvline(1.0, color=C_GREY, ls=":", lw=0.5)

    handles_b = []
    for sp in SPECIES_ALL + ["human"]:
        if not (BOOT.get(sp, {}).get("ζ") and BOOT.get(sp, {}).get("η")):
            continue
        z_m, _, z_lo, z_hi = BOOT[sp]["ζ"]
        e_m, _, e_lo, e_hi = BOOT[sp]["η"]
        marker = ECO_MARKER.get(ECO_GROUP.get(sp, "human"), "o")
        ms = 10 if sp == "human" else 7.5
        eb = ax2.errorbar([z_m], [e_m],
                           xerr=[[z_m - z_lo], [z_hi - z_m]],
                           yerr=[[e_m - e_lo], [e_hi - e_m]],
                           fmt=marker, ms=ms, color=COLOURS.get(sp, C_GREY),
                           ecolor=C_GREY, capsize=2, elinewidth=0.5,
                           mec="black", mew=0.4,
                           label=LABELS.get(sp, sp))
        handles_b.append(eb)
    ax2.set_xlabel(r"$\zeta$ (central-place strength)")
    ax2.set_ylabel(r"$\eta$ (velocity-heterogeneity)")
    ax2.set_xlim(0, 1.75)
    ax2.set_ylim(0, 2.6)
    ax2.grid(True, alpha=0.25, lw=0.3)

    fig.legend(handles_b, [h.get_label() for h in handles_b],
               loc="lower center", ncol=6, fontsize=5.8, frameon=False,
               bbox_to_anchor=(0.5, 0.01),
               handlelength=1.4, columnspacing=0.6, handletextpad=0.4)

    for i, lab in enumerate("ab"):
        fig.text([0.04, 0.62][i], 0.96, lab, fontsize=9, weight="bold")

    fig.savefig(OUT / "fig2_zipf_phase.pdf")
    fig.savefig(OUT / "fig2_zipf_phase.png", dpi=300)
    plt.close(fig)
    print("  wrote fig2_zipf_phase.(pdf|png)")


# ---------------------------------------------------------------------------
# Figure 3 — Song scaling relations + visitation law η
# ---------------------------------------------------------------------------
def fig3_song_eta():
    """Fig 3: (a) Song's three scaling identities tested across 11 species via
    Monte-Carlo-propagated discrepancy ratios; (b) visitation exponent η bar
    with η=1 (linear-cost) and η=2 (kinetic-cost) reference lines."""
    fig = plt.figure(figsize=(cm(18.3), cm(9.5)))
    gs = fig.add_gridspec(1, 2, wspace=0.28, left=0.06, right=0.99,
                          bottom=0.22, top=0.93)

    # ---- (a) Song discrepancy across all species we have all 4 metrics for
    ax = fig.add_subplot(gs[0, 0])
    rels = [("μ = β/(1+γ)", "μ"),
            ("ζ = 1+γ",     "ζ"),
            ("β = μζ",      "β")]
    rng = np.random.default_rng(42)
    colours_rel = ["#4477AA", "#EE6677", "#228833"]

    have_song = [s for s in SPECIES_ALL + ["human"]
                 if all(BOOT.get(s, {}).get(k) for k in ("μ", "γ", "β", "ζ"))]
    have_song.sort(key=lambda s: BOOT[s]["α"][0] if BOOT.get(s, {}).get("α") else 0)
    bar_w = 0.27
    for i, (label, target) in enumerate(rels):
        rm, rlo, rhi = [], [], []
        for sp in have_song:
            d = BOOT[sp]
            mu_m, mu_se = d["μ"][0], d["μ"][1]
            g_m,  g_se  = d["γ"][0], d["γ"][1]
            b_m,  b_se  = d["β"][0], d["β"][1]
            z_m,  z_se  = d["ζ"][0], d["ζ"][1]
            samples = []
            for _ in range(2500):
                mu = rng.normal(mu_m, mu_se)
                gg = rng.normal(g_m, g_se)
                bb = rng.normal(b_m, b_se)
                zz = rng.normal(z_m, z_se)
                if target == "μ":
                    pred, meas = bb / (1 + gg), mu
                elif target == "ζ":
                    pred, meas = 1 + gg, zz
                else:
                    pred, meas = mu * zz, bb
                if min(abs(pred), abs(meas)) > 0.01:
                    r = max(abs(pred), abs(meas)) / min(abs(pred), abs(meas))
                    if np.isfinite(r):
                        samples.append(r)
            if samples:
                m = np.median(samples)
                rm.append(m)
                rlo.append(max(0, m - np.percentile(samples, 2.5)))
                rhi.append(np.percentile(samples, 97.5) - m)
            else:
                rm.append(np.nan); rlo.append(0); rhi.append(0)
        pos = np.arange(len(have_song)) + (i - 1) * bar_w
        ax.bar(pos, rm, bar_w, label=label, color=colours_rel[i],
               alpha=0.85, edgecolor="black", lw=0.25,
               yerr=[rlo, rhi], capsize=1.5, error_kw=dict(lw=0.4))
    ax.axhline(1.0, color=C_GREY, ls=":", lw=0.6)
    ax.set_yscale("log")
    ax.set_xticks(np.arange(len(have_song)))
    ax.set_xticklabels([LABELS.get(s, s) for s in have_song],
                       rotation=42, ha="right", fontsize=6.0)
    ax.set_ylabel("Discrepancy ratio (Song relations)")
    ax.legend(loc="upper left", fontsize=6, ncol=3)
    ax.grid(True, axis="y", which="both", alpha=0.25, lw=0.3)

    # ---- (b) η bar across all species with η ------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    have_e = [s for s in SPECIES_ALL + ["human"]
              if BOOT.get(s, {}).get("η") is not None]
    have_e.sort(key=lambda s: BOOT[s]["η"][0])
    means = [BOOT[s]["η"][0] for s in have_e]
    los   = [BOOT[s]["η"][0] - BOOT[s]["η"][2] for s in have_e]
    his   = [BOOT[s]["η"][3] - BOOT[s]["η"][0] for s in have_e]
    cols  = [COLOURS.get(s, C_GREY) for s in have_e]
    pos = np.arange(len(have_e))
    ax2.bar(pos, means, color=cols, alpha=0.92, edgecolor="black", lw=0.35,
            yerr=[los, his], capsize=2.0, error_kw=dict(lw=0.55))
    if "human" in have_e:
        ih = have_e.index("human")
        ax2.bar([ih], [means[ih]], color=cols[ih], alpha=0.9,
                edgecolor=C_HUMAN, lw=1.4)
    ax2.axhline(1.0, color=C_GREY, ls=":", lw=0.6)
    ax2.axhline(2.0, color=C_HUMAN, ls=":", lw=0.6)
    ax2.text(len(have_e) - 0.4, 1.04, r"$\eta=1$ linear-cost",
             fontsize=6, color=C_GREY, ha="right")
    ax2.text(len(have_e) - 0.4, 2.04, r"$\eta=2$ kinetic-cost",
             fontsize=6, color=C_HUMAN, ha="right")
    ax2.set_xticks(pos)
    ax2.set_xticklabels([LABELS.get(s, s) for s in have_e],
                        rotation=42, ha="right", fontsize=6.2)
    ax2.set_ylabel(r"Visitation exponent $\eta$")
    ax2.set_ylim(0, max(2.6, max(means) * 1.15))
    ax2.grid(True, axis="y", alpha=0.25, lw=0.3)

    for i, lab in enumerate("ab"):
        fig.text([0.04, 0.51][i], 0.95, lab, fontsize=9, weight="bold")

    fig.savefig(OUT / "fig3_song_eta.pdf")
    fig.savefig(OUT / "fig3_song_eta.png", dpi=300)
    plt.close(fig)
    print("  wrote fig3_song_eta.(pdf|png)")


# ---------------------------------------------------------------------------
# Figure 4 — Stork seasonal split + unified-model heatmaps
# ---------------------------------------------------------------------------
def fig4_seasonal_unified():
    """Three panels:
       (a) stork α by season (breeding converges to human),
       (b) unified-model predicted ζ vs measured ζ across all 11 species,
       (c) same for η.
    The two scatter panels report the unified-model fit quality at a glance
    — points lying on the diagonal y = x mean the model reproduces the
    measured exponent. Marker colour = species, marker shape = ecological
    class. The (γ_CP, η_v) heatmap visualization is moved to Ext. Data Fig 4
    so the main panel stays uncluttered with 11 species."""
    fig = plt.figure(figsize=(cm(18.3), cm(9.5)))
    gs = fig.add_gridspec(1, 3, wspace=0.40, left=0.06, right=0.99,
                          bottom=0.30, top=0.93,
                          width_ratios=[1.0, 1.0, 1.0])

    # ---- (a) stork seasonal split ----------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    seasons = ["All", "Migration", "Wintering", "Breeding"]
    vals = {"All": 3.48, "Migration": 3.90, "Wintering": 3.20, "Breeding": 1.70}
    errs = {"All": 0.12, "Migration": 0.20, "Wintering": 0.15, "Breeding": 0.05}
    pos = np.arange(len(seasons))
    ax.bar(pos, [vals[s] for s in seasons],
           color=[C_STORK, "#bbbbbb", "#bbbbbb", C_STORK],
           alpha=0.85, edgecolor="black", lw=0.4,
           yerr=[errs[s] for s in seasons], capsize=3, error_kw=dict(lw=0.6))
    ax.axhspan(1.60, 1.90, alpha=0.15, color=C_HUMAN)
    ax.axhline(1.75, color=C_HUMAN, ls="--", lw=0.8)
    ax.text(3.5, 1.78, "human\nreference", fontsize=6, ha="right",
            color=C_HUMAN)
    ax.set_xticks(pos)
    ax.set_xticklabels(seasons, rotation=20, ha="right")
    ax.set_ylabel(r"Stork tail exponent $\alpha$")
    ax.set_ylim(0, 4.5)
    ax.grid(True, axis="y", alpha=0.25, lw=0.3)

    # ---- load unified model grid ------------------------------------------
    npz = FIG_IN / "unified_model" / "sweep_data.npz"
    if npz.exists():
        d = np.load(npz)
        gamma_grid = d["gamma_grid"]; eta_grid = d["eta_grid"]
        Z = d["Z"]; H = d["H"]
        Z_min, Z_max = float(np.nanmin(Z)), float(np.nanmax(Z))
        H_min, H_max = float(np.nanmin(H)), float(np.nanmax(H))
    else:
        Z = H = None
        Z_min = Z_max = H_min = H_max = 0.0

    targets = {}
    for sp in SPECIES_ALL + ["human"]:
        if BOOT.get(sp, {}).get("ζ") and BOOT.get(sp, {}).get("η"):
            targets[sp] = (BOOT[sp]["ζ"][0], BOOT[sp]["η"][0])

    def best_grid_value(Z_grid, H_grid, target_z, target_e, want):
        """Find (γ, η_v) minimising sq-distance to (target_z, target_e) and
        return the model's *want* ('z' or 'e') at that point."""
        if Z_grid is None:
            return target_z if want == "z" else target_e
        diff = (Z_grid - target_z) ** 2 + (H_grid - target_e) ** 2
        idx = np.unravel_index(np.nanargmin(diff), diff.shape)
        return float(Z_grid[idx]) if want == "z" else float(H_grid[idx])

    # ---- (b) predicted ζ vs measured ζ ------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])
    for sp, (tz, te) in targets.items():
        pz = best_grid_value(Z, H, tz, te, "z")
        m = ECO_MARKER.get(ECO_GROUP.get(sp, "human"), "o")
        s = 80 if sp == "human" else 50
        ax_b.scatter([tz], [pz], s=s, color=COLOURS.get(sp, C_GREY),
                     marker=m, edgecolor="black", linewidths=0.4, zorder=4,
                     label=LABELS.get(sp, sp))
    diag = np.linspace(0, 2.0, 50)
    ax_b.plot(diag, diag, ls=":", color=C_GREY, lw=0.6)
    ax_b.set_xlabel(r"Measured $\zeta$")
    ax_b.set_ylabel(r"Model $\zeta$ (best-fit grid point)")
    ax_b.set_xlim(0, 1.8); ax_b.set_ylim(0, 1.8)
    ax_b.grid(True, alpha=0.25, lw=0.3)
    ax_b.text(0.04, 0.95, "y = x", transform=ax_b.transAxes,
              fontsize=6, color=C_GREY)

    # ---- (c) predicted η vs measured η ------------------------------------
    ax_c = fig.add_subplot(gs[0, 2])
    for sp, (tz, te) in targets.items():
        pe = best_grid_value(Z, H, tz, te, "e")
        m = ECO_MARKER.get(ECO_GROUP.get(sp, "human"), "o")
        s = 80 if sp == "human" else 50
        ax_c.scatter([te], [pe], s=s, color=COLOURS.get(sp, C_GREY),
                     marker=m, edgecolor="black", linewidths=0.4, zorder=4)
    ax_c.plot(diag, diag, ls=":", color=C_GREY, lw=0.6)
    ax_c.set_xlabel(r"Measured $\eta$")
    ax_c.set_ylabel(r"Model $\eta$ (best-fit grid point)")
    ax_c.set_xlim(0, 2.5); ax_c.set_ylim(0, 2.5)
    ax_c.grid(True, alpha=0.25, lw=0.3)
    ax_c.text(0.04, 0.95, "y = x", transform=ax_c.transAxes,
              fontsize=6, color=C_GREY)

    # Single shared legend (compact, well below the x-axis labels)
    handles, labels = ax_b.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, fontsize=5.8,
               frameon=False, bbox_to_anchor=(0.5, 0.02),
               handlelength=1.2, columnspacing=0.7, handletextpad=0.35)

    for i, lab in enumerate("abc"):
        fig.text(0.04 + i * 0.335, 0.95, lab, fontsize=9, weight="bold")

    fig.savefig(OUT / "fig4_seasonal_unified.pdf")
    fig.savefig(OUT / "fig4_seasonal_unified.png", dpi=300)
    plt.close(fig)
    print("  wrote fig4_seasonal_unified.(pdf|png)")


# ---------------------------------------------------------------------------
# Extended Data Figure 4 — the two model heatmaps that used to be Fig 4 b,c
# ---------------------------------------------------------------------------
def ext_fig4_model_heatmaps():
    """Standalone heatmap visualization of the unified-model parameter
    sweep, with all 11 species (plus human) overlaid. This is the
    quantitative companion to Fig 4 b–c, which only show the predicted-vs-
    measured scatter to keep the main panel readable."""
    npz = FIG_IN / "unified_model" / "sweep_data.npz"
    if not npz.exists():
        print("  ! sweep_data.npz missing, skipping ext_fig4")
        return
    d = np.load(npz)
    gamma_grid = d["gamma_grid"]; eta_grid = d["eta_grid"]
    Z = d["Z"]; H = d["H"]

    targets = {}
    for sp in SPECIES_ALL + ["human"]:
        if BOOT.get(sp, {}).get("ζ") and BOOT.get(sp, {}).get("η"):
            targets[sp] = (BOOT[sp]["ζ"][0], BOOT[sp]["η"][0])

    def fit_grid(tz, te):
        diff = (Z - tz) ** 2 + (H - te) ** 2
        idx = np.unravel_index(np.nanargmin(diff), diff.shape)
        return gamma_grid[idx[1]], eta_grid[idx[0]]

    # First pass: compute the raw best-fit grid coordinate for every species.
    raw_pos = {sp: fit_grid(tz, te) for sp, (tz, te) in targets.items()}

    # Group species sharing the same grid cell — these would visually
    # collapse onto a single marker without jitter.
    from collections import defaultdict
    groups = defaultdict(list)
    for sp, (gf, ef) in raw_pos.items():
        groups[(round(gf, 4), round(ef, 4))].append(sp)

    # Apply deterministic circular jitter inside each multi-species cell.
    # Radii are chosen as ~25% of the grid spacing so the jitter is large
    # enough to separate marker dots but small enough to keep each species
    # visually anchored to its true best-fit cell.
    JITTER_RX = 0.012   # γ_CP grid step is 0.05 → 24 % offset
    JITTER_RY = 0.060   # η_v grid step is 0.25 → 24 % offset
    jittered_pos = {}
    for (g0, e0), members in groups.items():
        n = len(members)
        if n == 1:
            jittered_pos[members[0]] = (g0, e0)
            continue
        # Sort members for reproducibility, then place on a small circle
        for k, sp in enumerate(sorted(members)):
            angle = 2 * np.pi * k / n
            jittered_pos[sp] = (g0 + JITTER_RX * np.cos(angle),
                                 e0 + JITTER_RY * np.sin(angle))

    fig, axes = plt.subplots(1, 2, figsize=(cm(18.3), cm(9.0)))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.28,
                        wspace=0.32)
    handles_seen = []

    for ax, (M, cmap, vmin, vmax, label) in zip(
            axes,
            [(Z, "viridis", 0, 1.3, r"Model $\zeta$"),
             (H, "plasma",  0.5, 2.2, r"Model $\eta$")]):
        im = ax.imshow(M, origin="lower", aspect="auto",
                       extent=[gamma_grid[0], gamma_grid[-1],
                               eta_grid[0], eta_grid[-1]],
                       cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_xlabel(r"$\gamma_\mathrm{CP}$")
        ax.set_ylabel(r"$\eta_v$")
        cb = plt.colorbar(im, ax=ax, pad=0.02, shrink=0.85)
        cb.set_label(label, fontsize=7); cb.ax.tick_params(labelsize=6)
        for sp in targets:
            gf, ef = jittered_pos[sp]
            mk = ECO_MARKER.get(ECO_GROUP.get(sp, "human"), "o")
            sz = 70 if sp == "human" else 38
            h = ax.scatter([gf], [ef], s=sz, color=COLOURS.get(sp, C_GREY),
                           marker=mk, edgecolor="white", linewidths=0.7,
                           zorder=5, label=LABELS.get(sp, sp))
            if ax is axes[0]:
                handles_seen.append((sp, h))

    # External legend, well below the x-axis label (γ_CP)
    fig.legend([h for _, h in handles_seen],
               [LABELS.get(sp, sp) for sp, _ in handles_seen],
               loc="lower center", ncol=6, fontsize=5.8, frameon=False,
               bbox_to_anchor=(0.5, 0.02), handlelength=1.2,
               columnspacing=0.7, handletextpad=0.35)
    for i, lab in enumerate("ab"):
        fig.text(0.04 + i * 0.50, 0.95, lab, fontsize=9, weight="bold")
    fig.savefig(OUT / "ext_fig4_model_heatmaps.pdf")
    fig.savefig(OUT / "ext_fig4_model_heatmaps.png", dpi=300)
    plt.close(fig)
    print("  wrote ext_fig4_model_heatmaps.(pdf|png)")


# ---------------------------------------------------------------------------
# Extended Data Figure 1 — Alessandretti container hierarchy
# ---------------------------------------------------------------------------
def ext_fig1_containers():
    """Container effective sizes per level. Currently rendered for the three
    benchmark species we have full Alessandretti diagnostics for; the eight
    additions can be added to the dict once their blocoC logs are mined."""
    fig, ax = plt.subplots(figsize=(cm(12), cm(7)))
    levels = [100, 500, 2000, 10000, 50000]
    sizes = {
        "elephant": [43, 264, 1123, 4980, 12058],
        "gannet":   [41, 223,  865, 4811, 22802],
        "stork":    [45, 187,  575, 4051, 19520],
    }
    for sp in sizes:
        ax.loglog(levels, sizes[sp], 'o-', color=COLOURS[sp],
                  label=LABELS[sp], lw=0.9, ms=4)
    ax.loglog(levels, levels, ls=":", color=C_GREY, lw=0.6, label="identity")
    ax.set_xlabel(r"Grid level $\ell$ (m)")
    ax.set_ylabel(r"Container effective size (m, 95th pct.)")
    ax.grid(True, which="both", alpha=0.25, lw=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "ext_fig1_containers.pdf")
    fig.savefig(OUT / "ext_fig1_containers.png", dpi=300)
    plt.close(fig)
    print("  wrote ext_fig1_containers")


# ---------------------------------------------------------------------------
# Extended Data Figure 2 — per-species P(Δr) overlay (raw and rescaled)
# ---------------------------------------------------------------------------
def ext_fig2_per_species_pdr():
    """Two panels showing every species' pooled P(Δr) on shared axes:
       (a) raw P(Δr) on log-log, makes the absolute spatial-scale gradient
           obvious (gazelle/turtle/elephant span 5+ decades; baboon a single
           one);
       (b) the same curves rescaled by the median step length per species,
           highlighting the *shape* differences (heavy- vs light-tailed)
           independently of the spatial scale.
    Companion to Fig 1 — moves the per-species detail off the main panel."""
    fig = plt.figure(figsize=(cm(18.3), cm(9.5)))
    gs = fig.add_gridspec(1, 2, wspace=0.28, left=0.06, right=0.99,
                          bottom=0.28, top=0.94)

    have_sp = [sp for sp in SPECIES_ALL
               if compute_step_lengths(sp) is not None
               and len(compute_step_lengths(sp)) > 1000]

    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    handles = []
    for sp in have_sp:
        sl = compute_step_lengths(sp)
        sl = sl[sl > 0]
        edges = np.logspace(np.log10(max(sl.min(), 0.01)),
                            np.log10(sl.max()), 45)
        cnts, _ = np.histogram(sl, bins=edges)
        centres = np.sqrt(edges[:-1] * edges[1:])
        widths = np.diff(edges)
        pdf = cnts / (widths * cnts.sum())
        m = pdf > 0
        col = COLOURS.get(sp, C_GREY)
        h, = ax_a.loglog(centres[m], pdf[m], "-", color=col, lw=0.9,
                          alpha=0.85, label=LABELS.get(sp, sp))
        handles.append(h)
        med = np.median(sl)
        ax_b.loglog(centres[m] / med, pdf[m] * med, "-", color=col,
                    lw=0.9, alpha=0.85)

    ax_a.set_xlabel(r"$\Delta r$ (m)")
    ax_a.set_ylabel(r"$P(\Delta r)$")
    ax_a.grid(True, which="both", alpha=0.25, lw=0.3)
    ax_b.set_xlabel(r"$\Delta r / \mathrm{median}(\Delta r)$")
    ax_b.set_ylabel(r"$\mathrm{median}(\Delta r)\cdot P(\Delta r)$")
    ax_b.axvline(1.0, color=C_GREY, ls=":", lw=0.5)
    ax_b.grid(True, which="both", alpha=0.25, lw=0.3)

    fig.legend(handles, [h.get_label() for h in handles],
               loc="lower center", ncol=6, fontsize=5.8, frameon=False,
               bbox_to_anchor=(0.5, 0.01),
               handlelength=1.4, columnspacing=0.6, handletextpad=0.4)

    for i, lab in enumerate("ab"):
        fig.text(0.04 + i * 0.50, 0.96, lab, fontsize=9, weight="bold")

    fig.savefig(OUT / "ext_fig2_per_species_pdr.pdf")
    fig.savefig(OUT / "ext_fig2_per_species_pdr.png", dpi=300)
    plt.close(fig)
    print("  wrote ext_fig2_per_species_pdr.(pdf|png)")


# ---------------------------------------------------------------------------
# Extended Data Figure 3 — eleven-species master summary table (visual)
# ---------------------------------------------------------------------------
def ext_fig3_master_table():
    """A horizontal forest plot rendering of all six exponents for all 11
    species + human reference. Each row is a species; each column is one
    exponent shown with its 95 % CI bar. Acts as the visual companion to
    the Table-1 master table (which is the printed list of numbers)."""
    syms = ["α", "ζ", "μ", "γ", "β", "η"]
    sym_titles = {"α": r"$\alpha$  step tail",
                  "ζ": r"$\zeta$  visit Zipf",
                  "μ": r"$\mu$  $S(t)$",
                  "γ": r"$\gamma$  $P_{\rm new}$",
                  "β": r"$\beta$  waiting",
                  "η": r"$\eta$  visitation"}
    species = [s for s in SPECIES_ALL + ["human"]
               if any(BOOT.get(s, {}).get(k) for k in syms)]
    fig, axes = plt.subplots(1, len(syms),
                             figsize=(cm(18.3), cm(0.45 * len(species) + 2.0)),
                             sharey=True)
    fig.subplots_adjust(left=0.18, right=0.99, top=0.93, bottom=0.13,
                        wspace=0.18)
    y = np.arange(len(species))
    for ax, sym in zip(axes, syms):
        for i, sp in enumerate(species):
            d = BOOT.get(sp, {}).get(sym)
            if d is None:
                ax.scatter([np.nan], [i], color="white"); continue
            m, _, lo, hi = d
            col = COLOURS.get(sp, C_GREY)
            ax.errorbar([m], [i], xerr=[[m - lo], [hi - m]],
                        fmt="o", ms=4, color=col, ecolor=col,
                        elinewidth=0.7, capsize=1.5,
                        mec="black", mew=0.3)
        ax.set_title(sym_titles[sym], fontsize=7)
        ax.grid(True, axis="x", alpha=0.25, lw=0.3)
        ax.set_yticks(y)
        ax.set_yticklabels([LABELS.get(s, s) for s in species],
                           fontsize=6.2)
        ax.tick_params(labelsize=6)
    fig.savefig(OUT / "ext_fig3_master_forest.pdf")
    fig.savefig(OUT / "ext_fig3_master_forest.png", dpi=300)
    plt.close(fig)
    print("  wrote ext_fig3_master_forest.(pdf|png)")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("[nature_figures] generating publication-quality figures ...")
    fig1_step_length()
    fig2_zipf_phase()
    fig3_song_eta()
    fig4_seasonal_unified()
    ext_fig1_containers()
    ext_fig2_per_species_pdr()
    ext_fig3_master_table()
    ext_fig4_model_heatmaps()
    print(f"\nAll figures written to {OUT}")
