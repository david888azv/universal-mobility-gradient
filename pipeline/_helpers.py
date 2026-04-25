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

"""Helpers compartilhados, com suporte multi-espécie via env var SPECIES.

Each species in SPECIES_CONFIG declares:
    csv         — path to the unified CSV
    ref_lat,
    ref_lon     — reference centre for lat/lon → x/y projection (only used
                  when coord_mode == "latlon"). For planar datasets these
                  fields are ignored but kept for symmetry.
    label       — human-readable label used in figure titles
    coord_mode  — "latlon" (default; CSV has location-long / location-lat
                  columns and we project) or "planar" (CSV already has
                  x and y columns in metres).
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG_BASE = ROOT / "figures"

SPECIES_CONFIG = {
    # ---- original three species --------------------------------------------
    "elephant": {
        "csv": ROOT / "data" / "kruger_elephants_gps.csv",
        "ref_lat": -24.7, "ref_lon": 31.5,
        "label": "Kruger elephants",
        "coord_mode": "latlon",
    },
    "gannet": {
        "csv": ROOT / "data" / "gannet_gps.csv",
        "ref_lat": 46.82, "ref_lon": -54.18,
        "label": "Cape St Mary's gannets",
        "coord_mode": "latlon",
    },
    "stork": {
        "csv": ROOT / "data" / "stork_gps.csv",
        "ref_lat": 48.0, "ref_lon": 9.0,
        "label": "SW Germany white storks",
        "coord_mode": "latlon",
    },

    # ---- 2026 additions ----------------------------------------------------
    "albatross": {
        "csv": ROOT / "data" / "galapagos_albatross_gps.csv",
        "ref_lat": -1.4, "ref_lon": -89.7,            # Española I., Galápagos
        "label": "Galápagos albatross",
        "coord_mode": "latlon",
    },
    "bat_scharf": {
        "csv": ROOT / "data" / "eidolon_scharf_gps.csv",
        "ref_lat": 12.4, "ref_lon": -1.5,             # Burkina/Ghana central
        "label": "Eidolon helvum (Scharf 2019)",
        "coord_mode": "latlon",
    },
    "bat_abedi": {
        "csv": ROOT / "data" / "eidolon_abedi_gps.csv",
        "ref_lat": 5.6, "ref_lon": -0.2,              # Accra, Ghana
        "label": "Eidolon helvum (Abedi-Lartey 2016)",
        "coord_mode": "latlon",
    },
    "turtle_med": {
        "csv": ROOT / "data" / "loggerhead_med_gps.csv",
        "ref_lat": 38.5, "ref_lon": 14.0,             # Tyrrhenian / S. Italy
        "label": "Loggerhead turtle (Mediterranean)",
        "coord_mode": "latlon",
    },
    "turtle_pac": {
        "csv": ROOT / "data" / "loggerhead_pac_gps.csv",
        "ref_lat": 30.0, "ref_lon": 135.0,            # Japan / N. Pacific
        "label": "Loggerhead turtle (N. Pacific)",
        "coord_mode": "latlon",
    },
    "zebra": {
        "csv": ROOT / "data" / "zebra_gps.csv",
        "ref_lat": -19.4, "ref_lon": 23.5,            # N. Botswana / Okavango
        "label": "Burchell's zebra (Botswana)",
        "coord_mode": "latlon",
    },
    "baboon": {
        "csv": ROOT / "data" / "baboon_mpala_gps.csv",
        "ref_lat": 0.35, "ref_lon": 36.92,            # Mpala, Laikipia, Kenya
        "label": "Olive baboon (Mpala)",
        "coord_mode": "latlon",
    },
    "gazelle": {
        "csv": ROOT / "data" / "gazelle_planar.csv",
        "ref_lat": 0.0, "ref_lon": 0.0,               # ignored in planar mode
        "label": "Mongolian gazelle",
        "coord_mode": "planar",
    },
}

SPECIES = os.environ.get("SPECIES", "elephant")
if SPECIES not in SPECIES_CONFIG:
    raise SystemExit(f"unknown SPECIES={SPECIES}, choose from {list(SPECIES_CONFIG)}")
CFG = SPECIES_CONFIG[SPECIES]
DATA = CFG["csv"]
LABEL = CFG["label"]
COORD_MODE = CFG.get("coord_mode", "latlon")

REF_LAT = CFG["ref_lat"]
REF_LON = CFG["ref_lon"]
M_PER_DEG_LAT = 110_950.0
M_PER_DEG_LON = M_PER_DEG_LAT * np.cos(np.deg2rad(REF_LAT))


def fig_dir(block):
    """Pasta de figuras com sufixo da espécie."""
    out = FIG_BASE / f"{block}_{SPECIES}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def lonlat_to_xy(lon, lat):
    return ((lon - REF_LON) * M_PER_DEG_LON,
            (lat - REF_LAT) * M_PER_DEG_LAT)


_LATLON_COLS = ["timestamp", "location-long", "location-lat", "visible",
                "individual-local-identifier"]
_PLANAR_COLS = ["timestamp", "x", "y", "visible",
                "individual-local-identifier"]
CORE_COLS = _LATLON_COLS  # backward-compat alias


def _coerce_visible(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    return s.astype(str).str.lower().isin(("true", "1", "t"))


def load_data():
    """Load the canonical CSV for SPECIES and add x,y columns in metres.

    For latlon datasets we project around (REF_LAT, REF_LON); for planar
    datasets the CSV already has x and y in metres so we just pass them
    through. The downstream blocks all consume df['x'], df['y'], so they
    don't need to know which mode was used.
    """
    if COORD_MODE == "planar":
        df = pd.read_csv(DATA, usecols=_PLANAR_COLS, parse_dates=["timestamp"])
        df = df[_coerce_visible(df["visible"])].copy()
        df = df.dropna(subset=["x", "y"])
    else:
        df = pd.read_csv(DATA, usecols=_LATLON_COLS, parse_dates=["timestamp"])
        df = df[_coerce_visible(df["visible"])].copy()
        df = df.dropna(subset=["location-lat", "location-long"])
        df["x"], df["y"] = lonlat_to_xy(df["location-long"].values,
                                         df["location-lat"].values)
    df = df.sort_values(["individual-local-identifier",
                          "timestamp"]).reset_index(drop=True)
    return df


def per_indiv(df):
    for ind in sorted(df["individual-local-identifier"].unique()):
        sub = df[df["individual-local-identifier"] == ind].reset_index(drop=True)
        yield ind, sub


def log_bin_pdf(values, n_bins=40, vmin=None, vmax=None):
    v = np.asarray(values)
    v = v[v > 0]
    if len(v) == 0:
        return np.array([]), np.array([])
    if vmin is None:
        vmin = max(v.min(), 1e-3)
    if vmax is None:
        vmax = v.max()
    edges = np.logspace(np.log10(vmin), np.log10(vmax), n_bins + 1)
    counts, _ = np.histogram(v, bins=edges)
    widths = np.diff(edges)
    pdf = counts / (widths * counts.sum())
    centers = np.sqrt(edges[:-1] * edges[1:])
    mask = pdf > 0
    return centers[mask], pdf[mask]


def bootstrap_individuals(individuals, fn, n_boot=1000, rng=None):
    """Block-bootstrap by individual.

    fn(sampled_inds) -> scalar.  Returns (mean, sem, p2.5, p97.5).
    """
    if rng is None:
        rng = np.random.default_rng(42)
    N = len(individuals)
    inds = list(individuals)
    out = []
    for _ in range(n_boot):
        sample = list(rng.choice(inds, size=N, replace=True))
        try:
            v = fn(sample)
            if v is not None and np.isfinite(v):
                out.append(v)
        except Exception:
            continue
    if not out:
        return None, None, None, None
    out = np.array(out)
    return out.mean(), out.std(), np.percentile(out, 2.5), np.percentile(out, 97.5)


def clauset_mle(x, xmin_grid_n=80, min_tail=200):
    x = np.asarray(x); x = x[x > 0]
    if len(x) < min_tail:
        return None, None, None, None, len(x)
    pcts = np.linspace(50, 99.5, xmin_grid_n)
    candidates = np.unique(np.percentile(x, pcts))
    best = (None, None, 1.0, None, 0)
    for c in candidates:
        tail = x[x >= c]; n = len(tail)
        if n < min_tail:
            continue
        alpha = 1 + n / np.sum(np.log(tail / c))
        if not np.isfinite(alpha) or alpha <= 1:
            continue
        sorted_tail = np.sort(tail)
        emp = np.arange(1, n + 1) / n
        theo = 1 - (sorted_tail / c) ** (1 - alpha)
        ks = np.max(np.abs(emp - theo))
        if ks < best[2]:
            std_a = (alpha - 1) / np.sqrt(n)
            best = (alpha, c, ks, std_a, n)
    if best[0] is None:
        return None, None, None, None, len(x)
    alpha, xmin, ks, std_a, n_tail = best
    return alpha, xmin, std_a, ks, n_tail
