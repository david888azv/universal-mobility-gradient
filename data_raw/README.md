# `data_raw/` — instructions for downloading the eleven raw datasets

The eleven raw GPS / Argos tracking datasets are **not redistributed in this repository** because some of them are several MB to a few hundred MB in size and they are already canonically hosted under permissive Creative Commons licences at the Movebank Data Repository (DSpace) or the Dryad Digital Repository. This file documents how to fetch them so that any reviewer can reproduce the entire pipeline end-to-end on their own machine.

All eleven datasets are licensed **CC0 1.0 Universal** (public domain dedication). No registration or licence handshake is required for the seven that are deposited at the Movebank Data Repository public DSpace endpoint; the four hosted on Movebank's main system or on Dryad require the steps noted below.

---

## Quick start with the helper script

The repository ships with `pipeline/download_movebank.py`, a self-contained Python helper that downloads every Movebank-Data-Repository (MDR) dataset without authentication and lists the exact bitstream sizes before download. It also implements the licence-MD5 acceptance flow for the legacy Movebank main-system endpoint.

```bash
# (One-time) install dependencies and clone the repo
pip install -r requirements.txt

# (Optional) probe sizes before downloading
python pipeline/download_movebank.py --mdr-probe \
    10.5441/001/1.3hp3s250 \
    10.5441/001/1.k8n02jn8 \
    10.5441/001/1.44183438 \
    10.5441/001/1.1f1h87r8 \
    10.5441/001/1.m3c90703 \
    10.5441/001/1.f3550b4f \
    10.5441/001/1.kn0816jn

# Download all seven CC0 MDR datasets in one shot, skipping accelerometer
# bitstreams (which we do not use), into the local data_raw/ folder
python pipeline/download_movebank.py --mdr \
    10.5441/001/1.3hp3s250 \
    10.5441/001/1.k8n02jn8 \
    10.5441/001/1.44183438 \
    10.5441/001/1.1f1h87r8 \
    10.5441/001/1.m3c90703 \
    10.5441/001/1.f3550b4f \
    10.5441/001/1.kn0816jn \
    --gps-only --yes \
    --out data_raw
```

The `--gps-only` flag skips the large accelerometer bitstreams attached to the two *Eidolon helvum* records (which together total ≈ 1.6 GB and are not used in this analysis). End-of-run disk usage in `data_raw/` should be around **115 MB** for the seven MDR datasets together.

---

## Full table of datasets

| # | Species | Repository | DOI / handle | License | Approx. raw size (this analysis only) |
|---|---|---|---|---|---|
| 1 | African elephant — *Loxodonta africana* | Movebank | handle `10255/move.342` (Slotow et al.) | CC0 1.0 | ≈ 30 MB |
| 2 | Northern gannet — *Morus bassanus* | Movebank | handle `10255/move.1592` (d'Entremont et al.) | CC0 1.0 | ≈ 5 MB |
| 3 | White stork — *Ciconia ciconia* | Movebank | handle `10255/move.1685` (Cheng, Fiedler, Wikelski & Flack 2019) | CC0 1.0 | ≈ 1.3 GB |
| 4 | Galápagos albatross — *Phoebastria irrorata* | MDR | [10.5441/001/1.3hp3s250](https://doi.org/10.5441/001/1.3hp3s250) | CC0 1.0 | ≈ 5 MB |
| 5 | *Eidolon helvum* (Scharf 2019) | MDR | [10.5441/001/1.k8n02jn8](https://doi.org/10.5441/001/1.k8n02jn8) | CC0 1.0 | ≈ 4 MB GPS (1.2 GB ACC skipped) |
| 6 | *Eidolon helvum* (Abedi-Lartey 2016) | MDR | [10.5441/001/1.44183438](https://doi.org/10.5441/001/1.44183438) | CC0 1.0 | ≈ 1 MB GPS (404 MB ACC skipped) |
| 7 | Loggerhead turtle — Mediterranean | MDR | [10.5441/001/1.1f1h87r8](https://doi.org/10.5441/001/1.1f1h87r8) | CC0 1.0 | ≈ 4 MB |
| 8 | Loggerhead turtle — N. Pacific | MDR | [10.5441/001/1.m3c90703](https://doi.org/10.5441/001/1.m3c90703) | CC0 1.0 | ≈ 5 MB |
| 9 | Burchell's zebra — *Equus quagga burchellii* | MDR | [10.5441/001/1.f3550b4f](https://doi.org/10.5441/001/1.f3550b4f) | CC0 1.0 | ≈ 15 MB |
| 10 | Olive baboon — *Papio anubis* (Mpala) | MDR | [10.5441/001/1.kn0816jn](https://doi.org/10.5441/001/1.kn0816jn) | CC0 1.0 | ≈ 77 MB (zipped) |
| 11 | Mongolian gazelle — *Procapra gutturosa* | Dryad | [10.5061/dryad.45157](https://doi.org/10.5061/dryad.45157) | CC0 1.0 | ≈ 0.5 MB |

---

## Datasets requiring an extra step

### 1, 2, 3 — three benchmark datasets (Movebank main system)

These three are CC0-licensed but live on the Movebank main system (not the DSpace MDR). To fetch them you need a free Movebank account and to accept each licence once:

```bash
# Place credentials in env vars or in ~/.movebank_credentials (chmod 600)
export MOVEBANK_USER="your_username"
export MOVEBANK_PASS="your_password"
python pipeline/download_movebank.py --download <study_id> --out data_raw
```

The corresponding study IDs can be looked up from each Movebank handle URL.

### 11 — Mongolian gazelle (Dryad, requires a manual click)

Dryad serves CC0 datasets through an Anubis anti-bot challenge that blocks plain `curl`/`wget`. The single CSV (≈ 0.5 MB) needs one manual download via a browser:

1. Open [https://datadryad.org/dataset/doi:10.5061/dryad.45157](https://datadryad.org/dataset/doi:10.5061/dryad.45157).
2. Click **Download Dataset** at the bottom of the page.
3. Save the file `data_semiVarianceToIdentifyingMovementModes.csv` into:

   ```
   data_raw/dryad_45157_mongolian_gazelle/data_semiVarianceToIdentifyingMovementModes.csv
   ```

After that, `pipeline/ingest_new_species.py gazelle` converts it to the Movebank-compatible CSV consumed by the pipeline.

---

## Re-running the full pipeline

Once `data_raw/` has been populated:

```bash
# 1. Convert the eight 2026-sweep raw files into the unified Movebank format
python pipeline/ingest_new_species.py

# 2. Run the four estimator blocks + bootstrap on every species
python pipeline/run_all.py

# 3. Build the cross-species summary table
python pipeline/cross_species_table.py

# 4. Re-render the Nature-style figures
python pipeline/nature_figures.py

# 5. (optional) Re-export the figure-level CSVs that ship under data/
python pipeline/export_csv.py
```

The bootstrap is deterministic (seeded with `numpy.random.default_rng(42)`), so the resulting exponents are identical to the values reported in the manuscript and in `data/cross_species/master_table_all_exponents.csv`.

---

For any download or licence question, contact David L. Azevedo, Instituto de Física, Universidade de Brasília, [david888azv@unb.br](mailto:david888azv@unb.br) (ORCID [0000-0002-3456-554X](https://orcid.org/0000-0002-3456-554X)).
