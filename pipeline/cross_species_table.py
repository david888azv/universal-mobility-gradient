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
cross_species_table.py — read the 11 bootstrap_<species>.md files and produce
a single tidy CSV (figures/cross_species_summary.csv) plus a Markdown table
(figures/cross_species_summary.md).

Run after run_all.py finishes the bootstrap step for every species. Missing
species are silently skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG_BASE = ROOT / "figures"

SPECIES_ALL = ["elephant", "gannet", "stork",
               "albatross", "bat_scharf", "bat_abedi",
               "turtle_med", "turtle_pac", "zebra", "baboon", "gazelle"]
SYMS = ["α", "ζ", "μ", "γ", "β", "η"]
CI_PAT = re.compile(r"\[([\-\d\.]+),\s*([\-\d\.]+)\]")


def load_one(species: str) -> dict:
    path = FIG_BASE / f"bootstrap_{species}.md"
    if not path.exists():
        return {}
    text = path.read_text()
    out = {}
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "Métrica" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 4:
            continue
        sym = cols[0].lstrip().split()[0] if cols[0].lstrip() else ""
        if sym not in SYMS:
            continue
        try:
            mean = float(cols[1]); se = float(cols[2])
            ci = CI_PAT.search(cols[3])
            lo = float(ci.group(1)) if ci else None
            hi = float(ci.group(2)) if ci else None
            out[sym] = (mean, se, lo, hi)
        except (ValueError, IndexError):
            pass
    return out


def main() -> None:
    rows = []
    for sp in SPECIES_ALL:
        d = load_one(sp)
        row = {"species": sp}
        for sym in SYMS:
            if sym in d:
                m, se, lo, hi = d[sym]
                row[f"{sym}_mean"]  = m
                row[f"{sym}_se"]    = se
                row[f"{sym}_ci_lo"] = lo
                row[f"{sym}_ci_hi"] = hi
            else:
                row[f"{sym}_mean"]  = None
                row[f"{sym}_se"]    = None
                row[f"{sym}_ci_lo"] = None
                row[f"{sym}_ci_hi"] = None
        rows.append(row)

    df = pd.DataFrame(rows)
    csv_path = FIG_BASE / "cross_species_summary.csv"
    df.to_csv(csv_path, index=False)
    print(f"wrote {csv_path}")

    # Compact markdown
    md_path = FIG_BASE / "cross_species_summary.md"
    with md_path.open("w") as f:
        header = ["species"] + SYMS
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "|".join(["---"] * len(header)) + "|\n")
        for _, r in df.iterrows():
            cells = [r["species"]]
            for sym in SYMS:
                m = r[f"{sym}_mean"]
                if pd.isna(m) or m is None:
                    cells.append("—")
                else:
                    lo = r[f"{sym}_ci_lo"]; hi = r[f"{sym}_ci_hi"]
                    if pd.notna(lo) and pd.notna(hi):
                        cells.append(f"{m:.2f} [{lo:.2f}, {hi:.2f}]")
                    else:
                        cells.append(f"{m:.2f}")
            f.write("| " + " | ".join(cells) + " |\n")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
