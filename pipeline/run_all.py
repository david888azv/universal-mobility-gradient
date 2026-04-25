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
run_all.py — drive the full pipeline (blocoA + blocoB + blocoD + bootstrap)
for an arbitrary subset of the 11 species in SPECIES_CONFIG.

Each block is launched as a separate Python process with the SPECIES env var
set, so its module-level state (set inside _helpers.py at import time) sees
the right configuration. Failures of one block on one species do not abort
the rest of the sweep.

Examples
--------
    # everything (default = all 11 species, all four steps)
    python run_all.py

    # only the new species, only blocoA + bootstrap
    python run_all.py --species albatross bat_scharf bat_abedi turtle_med \
                       turtle_pac zebra baboon gazelle \
                       --steps blocoA bootstrap

    # one species, all steps
    python run_all.py --species baboon
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

PIPELINE = Path(__file__).resolve().parent

# Order matters: blocoB after blocoA (cache reuse), bootstrap last.
ALL_SPECIES = [
    "elephant", "gannet", "stork",
    "albatross", "bat_scharf", "bat_abedi",
    "turtle_med", "turtle_pac", "zebra", "baboon", "gazelle",
]
ALL_STEPS = ["blocoA", "blocoB", "blocoC", "blocoD", "bootstrap"]


def run_step(species: str, step: str, log_dir: Path) -> tuple[bool, float, Path]:
    """Run a single (species, step) job. Returns (success, seconds, log_path)."""
    log_path = log_dir / f"{species}__{step}.log"
    env = {**os.environ, "SPECIES": species, "PYTHONUNBUFFERED": "1"}
    cmd = [sys.executable, str(PIPELINE / f"{step}.py")]
    t0 = time.time()
    with log_path.open("w") as fh:
        fh.write(f"# {' '.join(cmd)}\n# SPECIES={species}\n\n")
        fh.flush()
        ret = subprocess.run(cmd, env=env, stdout=fh, stderr=subprocess.STDOUT,
                              cwd=PIPELINE)
    dt = time.time() - t0
    return ret.returncode == 0, dt, log_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--species", nargs="+", choices=ALL_SPECIES,
                    default=ALL_SPECIES,
                    help="which species to run (default: all)")
    ap.add_argument("--steps", nargs="+", choices=ALL_STEPS,
                    default=ALL_STEPS,
                    help="which pipeline steps to run (default: all)")
    ap.add_argument("--log-dir", default="../figures/_run_logs",
                    help="directory for per-job log files")
    ap.add_argument("--stop-on-fail", action="store_true",
                    help="abort the sweep at the first failed job")
    args = ap.parse_args()

    log_dir = (PIPELINE / args.log_dir).resolve()
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"[run_all] {len(args.species)} species × {len(args.steps)} steps "
          f"= {len(args.species) * len(args.steps)} jobs")
    print(f"[run_all] logs in {log_dir}")
    print()

    summary = []
    t_total = time.time()
    for sp in args.species:
        for step in args.steps:
            print(f"  {sp:>14s}  {step:<10s} ", end="", flush=True)
            ok, dt, log = run_step(sp, step, log_dir)
            tag = "OK " if ok else "FAIL"
            print(f"  {tag}  {dt:6.1f}s   {log.name}")
            summary.append((sp, step, ok, dt, log))
            if not ok and args.stop_on_fail:
                print(f"\n[run_all] aborting on first failure (use --stop-on-fail to disable)")
                break
        else:
            continue
        break

    total = time.time() - t_total
    n_ok   = sum(1 for *_, ok, _, _ in [(s, st, o, d, l) for s, st, o, d, l in summary] if ok)
    n_bad  = len(summary) - n_ok
    print(f"\n[run_all] done in {total/60:.1f} min  —  {n_ok} ok, {n_bad} failed")
    if n_bad:
        print(f"\nFailed jobs (see logs):")
        for sp, step, ok, _, log in summary:
            if not ok:
                print(f"  {sp:>14s}  {step:<10s}  {log}")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
