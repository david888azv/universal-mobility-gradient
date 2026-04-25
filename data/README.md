# Data — figure-level CSV exports

Every CSV in this folder is the tidy numerical content of a panel (or a set of panels) of the submitted manuscript. Reviewers can reproduce the visual elements of any figure by loading the matching CSV, without needing to re-run the pipeline on the raw GPS tracks.

## Naming convention

```
fig<figure_number>_<quantity>_<species>.csv
```

For Extended Data figures we use the prefix `extdata<N>_`, and cross-species master files live under `cross_species/`.

## Folder layout

```
data/
├── elephant/       # 14 individuals, Kruger NP (2007–2009)
├── gannet/         # 25 individuals, Cape St Mary's (2019–2022)
├── stork/          # 92 individuals, SW Germany (2013–2023)
├── albatross/      # 28 Galápagos albatrosses (Española I., 2008)
├── bat_scharf/     # 63 Eidolon helvum (Burkina/Ghana, 2009–2014)
├── bat_abedi/      # 28 Eidolon helvum (Ghana, 2016 seed-dispersal study)
├── turtle_med/     # 11 loggerhead turtles (Mediterranean, 2017+)
├── turtle_pac/     # 12 loggerhead turtles (Japan / N. Pacific, 2016+)
├── zebra/          # 7 Burchell's zebras (Botswana, 2007–2009)
├── baboon/         # 26 olive baboons, single troop (Mpala, Kenya, 2012)
├── gazelle/        # 36 Mongolian gazelles (Eastern Steppe, 2007–2010)
└── cross_species/
    ├── master_table_all_exponents.csv      # All 11 species + human reference
    └── fig4bc_unified_model_sweep.csv      # 9 × 7 (γ_CP, η_v) model grid
```

Each species subfolder carries the four canonical files:

- `fig1_step_length_<sp>.csv` — pooled P(Δr) (log-binned)
- `fig2_zipf_rank_frequency_<sp>.csv` — top-50 pooled rank–frequency
- `fig3_bootstrap_exponents_<sp>.csv` — α, ζ, μ, γ, β, η with bootstrap SE and 95% CI
- `extdata1_containers_<sp>.csv` — Alessandretti container effective size per grid level (only for the three benchmark species; the eight additions inherit the same diagnostic qualitatively)

The stork subfolder carries an additional `fig4a_seasonal_alpha_stork.csv`, holding α per seasonal phase (the cornerstone of Fig. 4a).

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
Resampling is block-bootstrap by individual; N_boot = 500 for every species except stork (50, owing to the 13 M-row dataset).

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

Only the three benchmark species (elephant, gannet, stork) currently carry this CSV; the eight additions inherit the same qualitative pattern (see Methods, Block C).

### `master_table_all_exponents.csv` — Master table
One row per species (all 11 + the human literature reference) with all six exponents and their bootstrap 95% CI as a formatted `[lo, hi]` string.
