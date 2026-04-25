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
ingest_new_species.py — convert the 8 newly-downloaded raw datasets into the
Movebank-canonical format that the existing pipeline (_helpers.load_data) reads.

Outputs go to ../data/<species>_gps.csv with the columns:
    timestamp, location-long, location-lat, visible, individual-local-identifier

Special case: the Mongolian gazelle (Dryad) is in projected (azimuthal-equidistant
metres). It is written to ../data/gazelle_planar.csv with columns:
    timestamp, x, y, visible, individual-local-identifier
The pipeline reads it via the "planar" coord_mode added to _helpers.

Subsampling: the baboon dataset is 1 Hz (10M events, 26 individuals). It is
down-sampled to 1 fix per minute per individual at ingestion time, which keeps
26 × 14 × 12 × 60 ≈ 260 k events — comparable in size and cadence to the
other species and small enough for the bootstrap to run in a few minutes.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

ROOT     = Path(__file__).resolve().parents[1]
RAW      = ROOT / "data_raw"
OUT      = ROOT / "data"
OUT.mkdir(exist_ok=True)


def _write_movebank(df: pd.DataFrame, path: Path) -> None:
    cols = ["timestamp", "location-long", "location-lat", "visible",
            "individual-local-identifier"]
    df = df[cols].copy()
    df.to_csv(path, index=False)
    print(f"  wrote {path.name}: {len(df):,} rows, {df['individual-local-identifier'].nunique()} indiv")


def _passthrough(src: Path, dst: Path,
                 visible_default: bool = True) -> None:
    """Read a Movebank-format CSV and pass it through, normalising the
    column set + adding `visible` if missing."""
    df = pd.read_csv(src, low_memory=False)
    if "visible" not in df.columns:
        df["visible"] = visible_default
    df = df[df["visible"].astype(str).str.lower().isin(("true", "1", "t"))]
    df = df.dropna(subset=["location-long", "location-lat",
                           "individual-local-identifier", "timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    _write_movebank(df, dst)


# ---------------------------------------------------------------------------
def ingest_albatross():
    src = RAW / "10.5441_001_1.3hp3s250" / "Galapagos Albatrosses.csv"
    _passthrough(src, OUT / "galapagos_albatross_gps.csv")


def ingest_bat_scharf():
    src = (RAW / "10.5441_001_1.k8n02jn8" /
           "Straw-colored fruit bats (Eidolon helvum) in Africa 2009-2014-gps.csv")
    _passthrough(src, OUT / "eidolon_scharf_gps.csv")


def ingest_bat_abedi():
    src = (RAW / "10.5441_001_1.44183438" /
           "Long-distance seed dispersal by straw-coloured fruit bats "
           "(data from Abedi-Lartey et al. 2016)-gps.csv")
    _passthrough(src, OUT / "eidolon_abedi_gps.csv")


def ingest_turtle_med():
    src = (RAW / "10.5441_001_1.1f1h87r8" /
           "Satellite Tracking of Oceanic Loggerhead Turtles in the Mediterranean.csv")
    _passthrough(src, OUT / "loggerhead_med_gps.csv")


def ingest_turtle_pac():
    src = (RAW / "10.5441_001_1.m3c90703" /
           "Post-nesting migrations of loggerhead sea turtles nesting in Japan.csv")
    _passthrough(src, OUT / "loggerhead_pac_gps.csv")


def ingest_zebra():
    src = (RAW / "10.5441_001_1.f3550b4f" /
           "Migratory Burchell's zebra (Equus burchellii) in northern Botswana.csv")
    _passthrough(src, OUT / "zebra_gps.csv")


def ingest_baboon(subsample_seconds: int = 60) -> None:
    """Strandburg-Peshkin 2015: 1 Hz × 26 indiv × 14 d ≈ 10 M events. We
    keep one fix per minute per individual to match other species' cadence."""
    src_zip = (RAW / "10.5441_001_1.kn0816jn" /
               "Collective movement in wild baboons "
               "(data from Strandburg-Peshkin et al. 2015).csv.zip")
    print(f"  reading {src_zip.name} (this can take a moment)...")
    with zipfile.ZipFile(src_zip) as z:
        member = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(member) as fh:
            df = pd.read_csv(fh)
    print(f"  raw: {len(df):,} rows")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "location-long", "location-lat"])
    df["individual-local-identifier"] = df["individual-local-identifier"].astype(str)
    # Subsample: floor timestamp to nearest `subsample_seconds`, then take
    # the first row per (indiv, bucket).
    bucket = df["timestamp"].astype("int64") // (subsample_seconds * 10**9)
    df["__bucket"] = bucket
    df = df.sort_values(["individual-local-identifier", "timestamp"])
    df = df.drop_duplicates(subset=["individual-local-identifier", "__bucket"],
                             keep="first")
    df = df.drop(columns="__bucket")
    df["visible"] = True
    print(f"  after {subsample_seconds}s subsample: {len(df):,} rows")
    _write_movebank(df, OUT / "baboon_mpala_gps.csv")


def ingest_gazelle():
    """Mongolian gazelle (Fleming et al. Dryad). Native format is planar
    (azimuthal-equidistant m). We forge a synthetic timestamp from the
    `time` column (seconds since first fix per individual, anchored at
    2010-01-01) so that the timestamp-based pipeline machinery still works.
    Output is x/y in metres + the synthetic timestamp."""
    src = (RAW / "dryad_45157_mongolian_gazelle" /
           "data_semiVarianceToIdentifyingMovementModes.csv")
    if not src.exists():
        print(f"  ! gazelle source not found at {src} — run the manual download first")
        return
    df = pd.read_csv(src)
    df = df.rename(columns={"gazelle": "individual-local-identifier",
                              "time": "_time_sec"})
    epoch = pd.Timestamp("2010-01-01")
    df["timestamp"] = epoch + pd.to_timedelta(df["_time_sec"], unit="s")
    df["visible"]   = True
    out_path = OUT / "gazelle_planar.csv"
    cols = ["timestamp", "x", "y", "visible", "individual-local-identifier"]
    df[cols].to_csv(out_path, index=False)
    print(f"  wrote {out_path.name}: {len(df):,} rows, "
          f"{df['individual-local-identifier'].nunique()} indiv (planar mode)")


# ---------------------------------------------------------------------------
INGEST = [
    ("albatross",   ingest_albatross),
    ("bat-scharf",  ingest_bat_scharf),
    ("bat-abedi",   ingest_bat_abedi),
    ("turtle-med",  ingest_turtle_med),
    ("turtle-pac",  ingest_turtle_pac),
    ("zebra",       ingest_zebra),
    ("baboon",      ingest_baboon),
    ("gazelle",     ingest_gazelle),
]


if __name__ == "__main__":
    import sys
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    for name, fn in INGEST:
        if only and name not in only:
            continue
        print(f"\n[ingest] {name}")
        try:
            fn()
        except Exception as exc:
            print(f"  ! FAILED: {exc}", file=sys.stderr)
    print("\nDone.")
