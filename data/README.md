# Data — figure-level CSV exports

Every CSV in this folder is the tidy numerical content of a panel (or a set of panels) of the submitted manuscript. Reviewers can reproduce the visual elements of any figure by loading the matching CSV, without needing to re-run the pipeline on the raw GPS tracks.

## Naming convention

```
fig<figure_number>_<quantity>_<species>.csv
```

For the Extended Data figure we use the prefix `extdata<N>_`, and for the master table cross-species file lives under `cross_species/`.

## Folder layout

```
data/
├── elephant/                      # 14 individuals, Kruger NP (2007–2009)
│   ├── fig1_step_length_elephant.csv
│   ├── fig2_zipf_rank_frequency_elephant.csv
│   ├── fig3_bootstrap_exponents_elephant.csv
│   └── extdata1_containers_elephant.csv
├── gannet/                        # 25 individuals, Cape St Mary's (2019–2022)
│   └── ... (same four files)
├── stork/                         # 92 individuals, SW Germany (2013–2023)
│   ├── ... (same four files)
│   └── fig4a_seasonal_alpha_stork.csv      # seasonal breakdown of α
└── cross_species/                 # cross-species / model outputs
    ├── master_table_all_exponents.csv      # Table 1 of the manuscript
    └── fig4bc_unified_model_sweep.csv      # 9 × 7 (γ_CP, η_v) model grid
```

## Data dictionary

### `fig1_step_length_<species>.csv` — pooled P(Δr)
| Column | Unit | Description |
|---|---|---|
| `delta_r_m` | m | Geometric bin centre (log-binning) |
| `bin_low_m`, `bin_high_m` | m | Bin edges |
| `count` | — | Raw step-length count per bin |
| `pdf` | 1/m | Normalised probability density |

### `fig2_zipf_rank_frequency_<species>.csv` — Zipf P(L)
| Column | Description |
|---|---|
| `rank` | Rank (1–50) of the grid cell in pooled visit-count ordering |
| `frequency` | Number of pooled visits to the cell at that rank |

Grid size = 500 m (matches the González convention).

### `fig3_bootstrap_exponents_<species>.csv` — bootstrap exponents
One row per exponent α, ζ, μ, γ, β, η with:
`exponent`, `exponent_name`, `mean`, `standard_error`, `ci_lo_2.5`, `ci_hi_97.5`.
Resampling is block-bootstrap by individual; N_boot = 500 for elephant/gannet, 50 for stork.

### `fig4a_seasonal_alpha_stork.csv` — seasonal split
| Column | Description |
|---|---|
| `phase` | All / Migration / Wintering / Breeding |
| `months`, `latitude` | Criteria used to define the phase |
| `alpha`, `alpha_se` | Tail exponent and bootstrap SE |
| `notes` | Contextual note (e.g. human-matching for breeding) |

### `fig4bc_unified_model_sweep.csv` — unified model
9 × 7 = 63 rows. Columns: `gamma_CP`, `eta_v`, `model_zeta`, `model_eta`. See §2.6 and Methods §4.5 of the manuscript.

### `extdata1_containers_<species>.csv` — Alessandretti containers
| Column | Description |
|---|---|
| `grid_level_m` | Nested grid scale (100, 500, 2000, 10 000, 50 000 m) |
| `container_effective_size_m_95pct` | 95th-percentile intra-cell distance at this level |

### `master_table_all_exponents.csv` — Table 1 of the manuscript
One row per species (elephant, gannet, stork, and the human literature reference) with all six exponents plus their bootstrap 95% CI as a formatted `[lo, hi]` string.
