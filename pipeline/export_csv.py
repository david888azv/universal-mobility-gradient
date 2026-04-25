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
Export figure-level CSV data for each species to the GitHub repo.

Every CSV is named `figN_<quantity>_<species>.csv` so reviewers can locate the
underlying numbers of any panel directly from the filename.

Outputs land in /home/david/atual/nature-scope/github-repo/data/<species>/
plus a master cross_species_summary.csv.
"""

from pathlib import Path
import os, sys
import numpy as np
import pandas as pd

REPO = Path("/home/david/atual/nature-scope/github-repo")
OUT_ROOT = REPO / "data"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, "/home/david/atual/nature-scope/pipeline")

SPECIES_INFO = {
    "elephant":   {"n": 14, "label": "Loxodonta africana"},
    "gannet":     {"n": 25, "label": "Morus bassanus"},
    "stork":      {"n": 92, "label": "Ciconia ciconia"},
    "albatross":  {"n": 28, "label": "Phoebastria irrorata"},
    "bat_scharf": {"n": 63, "label": "Eidolon helvum (Scharf 2019)"},
    "bat_abedi":  {"n": 28, "label": "Eidolon helvum (Abedi-Lartey 2016)"},
    "turtle_med": {"n": 11, "label": "Caretta caretta (Mediterranean)"},
    "turtle_pac": {"n": 12, "label": "Caretta caretta (N. Pacific)"},
    "zebra":      {"n":  7, "label": "Equus quagga burchellii"},
    "baboon":     {"n": 26, "label": "Papio anubis (Mpala)"},
    "gazelle":    {"n": 36, "label": "Procapra gutturosa"},
}


def _load_species(sp):
    """Fresh helpers under the given SPECIES env var."""
    os.environ["SPECIES"] = sp
    for m in ["_helpers"]:
        if m in sys.modules:
            del sys.modules[m]
    import _helpers as hp
    return hp


# -------------------------------------------------------------------------
# Fig 1 — pooled step lengths
# -------------------------------------------------------------------------
def export_step_lengths():
    for sp in SPECIES_INFO:
        cache = Path(f"/home/david/atual/nature-scope/figures/blocoA_{sp}/step_lengths.npy")
        if not cache.exists():
            hp = _load_species(sp)
            df = hp.load_data()
            all_steps = []
            for _, sub in hp.per_indiv(df):
                dx = np.diff(sub["x"].values)
                dy = np.diff(sub["y"].values)
                d = np.sqrt(dx * dx + dy * dy)
                all_steps.append(d[d > 0])
            steps = np.concatenate(all_steps) if all_steps else np.array([])
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.save(cache, steps)
        else:
            steps = np.load(cache)

        # Bin on a log grid so the CSV is compact
        steps = steps[steps > 0]
        edges = np.logspace(np.log10(max(steps.min(), 1e-3)),
                            np.log10(steps.max()), 60)
        cnt, _ = np.histogram(steps, bins=edges)
        centres = np.sqrt(edges[:-1] * edges[1:])
        widths = np.diff(edges)
        pdf = cnt / (widths * cnt.sum())
        df = pd.DataFrame({
            "delta_r_m": centres,
            "bin_low_m": edges[:-1],
            "bin_high_m": edges[1:],
            "count":     cnt,
            "pdf":       pdf,
        })
        out = OUT_ROOT / sp / f"fig1_step_length_{sp}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out, index=False)
        print(f"  wrote {out.relative_to(REPO)} ({len(df)} bins from {len(steps)} steps)")


# -------------------------------------------------------------------------
# Fig 2 — Zipf rank-frequency (top 50 pooled) + cross-species ζ
# -------------------------------------------------------------------------
def export_zipf():
    GRID = 500.0
    for sp in SPECIES_INFO:
        hp = _load_species(sp)
        df = hp.load_data()
        cells = []
        for _, sub in hp.per_indiv(df):
            cx = (sub["x"].values // GRID).astype(np.int64)
            cy = (sub["y"].values // GRID).astype(np.int64)
            cells.extend(list(zip(cx, cy)))
        counts = pd.Series(cells).value_counts().values[:50]
        df_out = pd.DataFrame({
            "rank":      np.arange(1, len(counts) + 1),
            "frequency": counts,
        })
        out = OUT_ROOT / sp / f"fig2_zipf_rank_frequency_{sp}.csv"
        df_out.to_csv(out, index=False)
        print(f"  wrote {out.relative_to(REPO)}")


# -------------------------------------------------------------------------
# Fig 3 + master summary table — read from bootstrap markdowns
# -------------------------------------------------------------------------
def parse_bootstrap(sp):
    import re
    path = Path(f"/home/david/atual/nature-scope/figures/bootstrap_{sp}.md")
    if not path.exists():
        return {}
    text = path.read_text()
    ci_pat = re.compile(r"\[([\-\d\.]+),\s*([\-\d\.]+)\]")
    out = {}
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
            lo, hi = (float(ci.group(1)), float(ci.group(2))) if ci else (np.nan, np.nan)
            out[sym] = (mean, se, lo, hi)
        except (ValueError, IndexError):
            pass
    return out


HUMAN_REF = {
    "α": (1.75, 0.15, 1.45, 2.05),
    "ζ": (1.20, 0.10, 1.00, 1.40),
    "μ": (0.60, 0.02, 0.56, 0.64),
    "γ": (0.21, 0.02, 0.17, 0.25),
    "β": (0.80, 0.10, 0.60, 1.00),
    "η": (2.05, 0.018, 2.014, 2.086),
}


def export_exponents():
    """Per-species CSV of all six bootstrap exponents + master cross-species table."""
    symbol_to_name = {"α": "alpha", "ζ": "zeta", "μ": "mu", "γ": "gamma",
                      "β": "beta", "η": "eta"}
    master_rows = []

    for sp, info in SPECIES_INFO.items():
        boot = parse_bootstrap(sp)
        rows = []
        for sym, (mean, se, lo, hi) in boot.items():
            rows.append({
                "exponent":        sym,
                "exponent_name":   symbol_to_name[sym],
                "mean":            mean,
                "standard_error":  se,
                "ci_lo_2.5":       lo,
                "ci_hi_97.5":      hi,
            })
        df_sp = pd.DataFrame(rows)
        out = OUT_ROOT / sp / f"fig3_bootstrap_exponents_{sp}.csv"
        df_sp.to_csv(out, index=False)
        print(f"  wrote {out.relative_to(REPO)}")

        master_rows.append({
            "species":        info["label"],
            "common_name":    sp,
            "n_individuals":  info["n"],
            **{symbol_to_name[sym]: f"{boot[sym][0]:.3f}" for sym in boot},
            **{f"{symbol_to_name[sym]}_ci": f"[{boot[sym][2]:.3f},{boot[sym][3]:.3f}]"
               for sym in boot},
        })

    # Add human reference
    master_rows.append({
        "species":        "Homo sapiens (literature)",
        "common_name":    "human",
        "n_individuals":  "10^5-10^7 (multi-study)",
        **{"alpha": HUMAN_REF["α"][0], "zeta": HUMAN_REF["ζ"][0],
           "mu": HUMAN_REF["μ"][0],    "gamma": HUMAN_REF["γ"][0],
           "beta": HUMAN_REF["β"][0],  "eta": HUMAN_REF["η"][0]},
        **{f"alpha_ci": "[1.45,2.05]", "zeta_ci": "[1.00,1.40]",
           "mu_ci": "[0.56,0.64]",   "gamma_ci": "[0.17,0.25]",
           "beta_ci": "[0.60,1.00]", "eta_ci": "[2.014,2.086]"},
    })

    pd.DataFrame(master_rows).to_csv(
        OUT_ROOT / "cross_species" / "master_table_all_exponents.csv", index=False)
    print(f"  wrote data/cross_species/master_table_all_exponents.csv")


# -------------------------------------------------------------------------
# Fig 4a — stork seasonal breakdown
# -------------------------------------------------------------------------
def export_stork_seasonal():
    # Values as reported in stork_seasonal_results.md
    rows = [
        {"phase": "All seasons", "months": "Jan-Dec", "latitude": "11-48 N",
         "alpha": 3.48, "alpha_se": 0.12, "notes": "pooled"},
        {"phase": "Migration",  "months": "Sep-Oct; Feb-Mar", "latitude": "varies",
         "alpha": 3.90, "alpha_se": 0.20, "notes": ""},
        {"phase": "Wintering",  "months": "Nov-Jan", "latitude": "< 30 N",
         "alpha": 3.20, "alpha_se": 0.15, "notes": "sub-Saharan"},
        {"phase": "Breeding",   "months": "Apr-Aug", "latitude": "> 40 N",
         "alpha": 1.70, "alpha_se": 0.05,
         "notes": "chicks anchor adults; matches human alpha = 1.75 +/- 0.15"},
    ]
    out = OUT_ROOT / "stork" / "fig4a_seasonal_alpha_stork.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"  wrote {out.relative_to(REPO)}")


# -------------------------------------------------------------------------
# Fig 4b,c — unified model sweep
# -------------------------------------------------------------------------
def export_unified_sweep():
    npz = Path("/home/david/atual/nature-scope/figures/unified_model/sweep_data.npz")
    if not npz.exists():
        print("  skip: unified sweep data not found")
        return
    d = np.load(npz)
    rows = []
    for j, g in enumerate(d["gamma_grid"]):
        for i, ev in enumerate(d["eta_grid"]):
            rows.append({
                "gamma_CP": float(g),
                "eta_v":    float(ev),
                "model_zeta": float(d["Z"][i, j]),
                "model_eta":  float(d["H"][i, j]),
            })
    out = OUT_ROOT / "cross_species" / "fig4bc_unified_model_sweep.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"  wrote {out.relative_to(REPO)}")


# -------------------------------------------------------------------------
# Alessandretti containers (Extended Data Fig 1)
# -------------------------------------------------------------------------
def export_containers():
    levels = [100, 500, 2000, 10000, 50000]
    sizes = {
        "elephant": [43,  264, 1123, 4980, 12058],
        "gannet":   [41,  223,  865, 4811, 22802],
        "stork":    [45,  187,  575, 4051, 19520],
    }
    for sp, sz in sizes.items():
        df = pd.DataFrame({
            "grid_level_m":           levels,
            "container_effective_size_m_95pct": sz,
        })
        out = OUT_ROOT / sp / f"extdata1_containers_{sp}.csv"
        df.to_csv(out, index=False)
        print(f"  wrote {out.relative_to(REPO)}")


if __name__ == "__main__":
    print("[export_csv] Fig 1 — step lengths ...")
    export_step_lengths()
    print("[export_csv] Fig 2 — Zipf rank frequency ...")
    export_zipf()
    print("[export_csv] Fig 3 — bootstrap exponents & master table ...")
    export_exponents()
    print("[export_csv] Fig 4a — stork seasonal ...")
    export_stork_seasonal()
    print("[export_csv] Fig 4b,c — unified-model sweep ...")
    export_unified_sweep()
    print("[export_csv] Extended Data Fig 1 — containers ...")
    export_containers()
    print("\nAll CSVs exported.")
