# Figures

All figure files are available in both vector (PDF) and raster (300 dpi PNG) form. The **main/** and **extended_data/** subfolders reproduce the layout used in the submitted manuscript; **supplementary/** collects the per-species intermediate diagnostics produced by each of the four estimator blocks.

## `main/` — main-text figures (all redesigned for 11 species)

| File | Panel summary |
|---|---|
| `fig1_step_length` | (a–c) Pooled P(Δr) for three representatives of the gradient (Mongolian gazelle, white stork, olive baboon) with Clauset MLE overlays; (d) bar of the tail exponent α across all 11 species + human reference, sorted ascending. |
| `fig2_zipf_phase` | (a) ζ bar across all 11 species + human, sorted; (b) (ζ, η) phase space populated by all 12 points, with marker shape encoding ecological class. |
| `fig3_song_eta` | (a) Discrepancy ratios of Song's three scaling relations across the 11 species + human (log scale); (b) visitation exponent η bar with η = 1 and η = 2 reference lines. |
| `fig4_seasonal_unified` | (a) Stork tail exponent by seasonal phase (breeding matches human α); (b, c) unified-model predicted ζ and η scattered against measured ζ and η across all 11 species + human; the diagonal y = x marks perfect agreement. |

## `extended_data/` — Extended Data figures

| File | Content |
|---|---|
| `ext_fig1_containers` | Container effective size per grid level for the three benchmark species (Alessandretti hierarchy). |
| `ext_fig2_per_species_pdr` | Per-species P(Δr) overlay across all 11 species, raw and rescaled by the species' median step length. |
| `ext_fig3_master_forest` | Forest plot of all six exponents (α, ζ, μ, γ, β, η) across the 11 species + human, with 95 % bootstrap CI. |
| `ext_fig4_model_heatmaps` | Unified-model parameter-sweep heatmaps (model ζ and model η over (γ_CP, η_v)) with all 12 points overlaid; markers that share the same nearest-grid cell carry a small deterministic circular jitter so all are visible. |

## `supplementary/` — per-species intermediate results

Each species subfolder contains the full set of panels produced by the four estimator blocks of the pipeline:

| Prefix | Block | Source | What it shows |
|---|---|---|---|
| `blockA_fig1_step_length_pdf` | A | González 2008 | Raw P(Δr) with Clauset MLE fit |
| `blockA_fig2_rg_distribution` | A | González 2008 | Distribution of individual radius of gyration |
| `blockA_fig3_rg_of_t` | A | González 2008 | ⟨r_g(t)⟩ saturation curves per tercile |
| `blockA_fig4_return_probability` | A | González 2008 | F_pt(t) at multiple radii with circadian peaks |
| `blockA_fig5_zipf_locations` | A | González 2008 | Zipf rank–frequency at three grid sizes |
| `blockA_fig6_collapse` | A | González 2008 | P(Δr | r_g) collapse across terciles |
| `blockB_figB1_St_mu` | B | Song 2010 | S(t) with exponent μ |
| `blockB_figB2_Pnew_gamma` | B | Song 2010 | P_new(S) with exponent γ |
| `blockB_figB3_scaling_relations` | B | Song 2010 | Three Song scaling relations per species |
| `blockD_figD1_visitation_law` | D | Schläpfer 2021 | ρ(r,f) visitation law with fitted η |
| `blockD_figD2_invariant_distance` | D | Schläpfer 2021 | ⟨d⟩ invariance test |

The stork subfolder additionally contains `seasonal_comparison.png` (Fig. 4a precursor), and the root of `supplementary/` holds the cross-species overlay and the 2-D model-heatmap from the earlier analysis pass.
