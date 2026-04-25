# Preregistration — N6 Cross-species mobility universality

**Template:** OSF Standard Pre-Data Collection / Pre-Analysis (adapted for secondary data analysis)
**Date:** 2026-04-24
**Authors:** [TBD]
**Project:** Cross-species test of human mobility scaling laws
**Working title:** *Universal phenomenology, divergent mechanism: a behavioral gradient of human-and-animal mobility from foraging to commute*

---

## 1. Background and rationale

Three scaling laws from human mobility (González 2008 *Nature* 453:779; Song 2010 *Nat. Phys.* 6:818; Schläpfer 2021 *Nature* 593:522) plus the hierarchical container framework (Alessandretti 2020 *Nature* 587:402) have been derived from datasets of 10⁵–10⁷ humans and treated as human-specific. We test whether they are:
- (U) phenomenologically universal across species (same functional form, taxon-specific exponents);
- (M) mechanistically universal (Song's preferential return Π_i = f_i and Schläpfer's η = 2 budget hold cross-species);
- (G) graduated along a behavioral axis of central-place strength.

The single most relevant precedent is Tikhonov & Strijkers 2023 (*PLoS ONE* 18:e0286239) which tested human mobility scaling in 11 European Herring Gulls. We extend their work in three critical dimensions: (i) three species spanning behavioral gradient from no-CP (elephant) → strict-CP (stork), (ii) all four laws (González + Song + Alessandretti + Schläpfer) — they tested only Zipf and S(t), (iii) bootstrap by individual to provide CIs.

Hu Yan-Q et al. 2010 (arXiv:1008.4394) proposed a general model with home-return constraint where exponents 1–2 emerge naturally; we provide the empirical cross-species validation that Hu et al. could not perform.

---

## 2. Hypotheses (pre-registered, falsifiable)

### H1 — Phenomenology is universal

**Statement:** All three species exhibit (a) truncated power-law P(Δr) tail with KS-distance ≤ 0.10, (b) logarithmic saturation of ⟨r_g(t)⟩, (c) hierarchical containers with at least 4 levels and Δr|level lognormal at KS ≤ 0.15, (d) circadian peaks in F_pt(t) at 24/48/72/96 h.

**Falsified if:** any of the four phenomenological signatures fails the KS criterion in ≥ 1 species.

### H2 — Mechanism follows a graduated, falsifiable order

**Statement:** Song's three relations (μ ≈ β/(1+γ), ζ ≈ 1+γ, β ≈ μζ) are progressively better satisfied as ζ_pooled grows, with discrepancy ratio ≤ 1.5 for ζ ≥ 0.7 and ratio ≥ 2.0 for ζ ≤ 0.4.

**Falsified if:** the ratio-vs-ζ relationship is non-monotonic across the 3 species, or if humans (ζ ≈ 1) show ratio > 1.5.

### H3 — Visitation η splits at η = 2 by transport regime

**Statement:** Animals using locomotion at near-constant velocity (walking, soaring) have η ≤ 1.3; humans (motorized) have η ≥ 1.8. Storks (mixed migration + breeding) lie between (1.0 ≤ η ≤ 1.5).

**Falsified if:** any animal species has η ≥ 1.7 or any human dataset has η ≤ 1.5.

### H4 — Stork *breeding-only* approaches human values

**Statement:** Filtering stork data to breeding-season nest-area only (Apr-Aug, lat > 40°N) produces P(Δr) tail exponent α_breed approaching the human value, with |α_breed − 1.75| < 0.5 (i.e., within 0.5 of human α = 1.75).

**Falsified if:** stork breeding α ≥ 2.5 or ≤ 1.0.

---

## 3. Data sources (pre-specified)

| Dataset | DOI | License | N indiv | Period | Sampling |
|---|---|---|---|---|---|
| Loxodonta africana, Kruger NP | 10.5441/001/1.403h24q5 | CC0 1.0 | 14 | 2007–2009 | 30 min |
| Morus bassanus, Cape St Mary's | 10.5441/001/1.5km7v2s3 | CC0 1.0 | 25 | 2019–2022 (breed.) | 1 min |
| Ciconia ciconia, SW Germany | 10.5441/001/1.ck04mn78 | CC0 1.0 | 92 | 2013–2023 | ~30 min |

**Human reference values:** taken verbatim from published papers; not re-analyzed here.

---

## 4. Pre-specified analysis pipeline

All code in `pipeline/` directory of project repo.

### 4.1 Pre-processing
1. Filter `visible == TRUE`.
2. Drop NaN GPS coords.
3. Project lat/lon → x/y meters via equirectangular at species-specific reference latitude.
4. Sort by individual + timestamp.

### 4.2 Block A — González 2008 (file `blocoA.py`)
- P(Δr) tail: MLE Clauset (Clauset, Shalizi, Newman 2009) with auto x_min, KS goodness-of-fit.
- P(rg): one rg per indiv; CCDF in log-log.
- ⟨rg(t)⟩: cumulative variance per indiv; group by tercile of final rg.
- F_pt(t): R ∈ {500, 2000, 3000} m; bin 1 h, smooth 3-h kernel; report values at 24/48/72/96 h.
- P(L) Zipf: grid g ∈ {200, 500, 1000} m; rank-frequency on top 50 ranks (pooled across indiv).
- P(Δr|rg) collapse: terciles, rescale by α_resc = 1.2 (González convention).

### 4.3 Block B — Song 2010 (file `blocoB.py`)
- S(t) per indiv on 500 m grid; fit S ~ t^μ in t ∈ [1 h, max].
- P_new(S) per indiv via binned exploration rate; fit P_new ~ S^(-γ).
- Waiting time Δt: sequence of cell-stays; MLE Clauset on Δt > 1 min.
- Test 3 scaling relations: μ = β/(1+γ), ζ = 1+γ, β = μζ; report ratio.

### 4.4 Block C — Alessandretti 2020 (file `blocoC.py`)
- Multi-scale grid: {100, 500, 2000, 10000, 50000} m.
- Per level: P(Δr|same-cell-at-this-level); KS-test against lognormal MLE.
- Per level: container effective size = p95 of intra-cell distances.

### 4.5 Block D — Schläpfer 2021 (file `blocoD.py`)
- Grid 1 km; T = 4 months periods (Schläpfer convention).
- For each indiv: home cell = modal cell.
- For each (cell, indiv): r = home→cell distance, f = mean visits per period.
- Pool (rf, density(rf)); fit ρ ∝ (rf)^(-η) via log-log regression on inner [10, 90] percentile.
- Invariance test: ⟨d⟩_i vs N_visitors → expected slope ≈ 0, R² < 0.05.

### 4.6 Bootstrap (file `bootstrap.py`)
- Block-bootstrap by individual: resample N indiv with replacement, recompute metric.
- N_BOOT = 500 (elephant, gannet, < 1M rows); 50 (stork, > 5M rows).
- Report mean, SE, [2.5%, 97.5%] percentile CI per metric.

---

## 5. Pre-specified statistical decisions

- **Power-law fit:** Clauset MLE, x_min via grid search minimizing KS distance over 60–99.5 percentile candidates.
- **Significance:** None tested via NHST; we use effect sizes (ratios, KS distances) with bootstrap CI.
- **Multiple comparisons:** No correction needed since each H is tested with a single bootstrap CI.
- **Outliers:** Use only `visible == TRUE` rows (Movebank's outlier flag); no further outlier removal.
- **Missing data:** Drop rows with NaN GPS; no imputation.

---

## 6. Specific predictions (sharpening hypotheses)

| Quantity | Elephant | Gannet | Stork | Human (ref) |
|---|---|---|---|---|
| α (P(Δr) tail, Clauset) | 2.5–4.0 | 2.0–3.5 | 3.0–4.0 (full) / 1.5–2.0 (breeding) | 1.75 ± 0.15 |
| ζ (Zipf top-50, pooled) | 0.10–0.40 | 0.7–1.0 | 0.7–1.1 | ~1.0 |
| η | 0.8–1.2 | 0.8–1.2 | 1.0–1.5 | 2.05 ± 0.02 |
| Song μ=β/(1+γ) ratio | > 2.0 | < 1.5 | < 1.5 | ~1.0 |
| Hierarchical levels | 4–5 | 4–5 | 4–5 | 4–5 |

**If all 5 quantities fall within these ranges, the gradient hypothesis (G) is corroborated.**

---

## 7. What would refute the entire framework

The framework would be falsified if either:
1. **No phenomenological universality:** ≥ 2 of (P(Δr), rg(t), containers, F_pt) fail KS in ≥ 1 species — would invalidate H1 globally.
2. **No gradient:** Song-relation discrepancy *increases* with ζ (i.e., humans worse than elephants at preferential return), or the 4-species ranking on ζ changes order under bootstrap — would invalidate H2.
3. **No regime split for η:** any animal η ≥ 1.8 or any human η ≤ 1.5 — would invalidate H3.

---

## 8. Deviations from the plan

To be reported transparently in any final manuscript. Major foreseeable deviations:
- Stork bootstrap N_BOOT may need to be lowered if compute becomes prohibitive.
- ζ aggregation: we report both *pooled-across-individuals* and *per-individual-mean* because they capture different aspects of CP behavior; both are pre-registered.
- The unified Song-Alessandretti-Schläpfer model (`unified_model.py`) is exploratory, not confirmatory, and its parameter fits are illustrative.

---

## 9. Reproducibility

- Code: `pipeline/` (Python 3.13, numpy 2.4, pandas 3.0, scipy 1.17, matplotlib 3.10).
- Data: Movebank Data Repository handles + DOIs above.
- All processed outputs in `figures/` and tables in `cross_species_summary.md`, `n6_movebank_survey.md`.
- License of generated code: MIT.
- License of underlying data: CC0 1.0 (all 3 species).

---

## 10. Authorship and conflicts

[TBD] — to be filled at submission. No funding-driven conflicts of interest anticipated since data are publicly archived under CC0.

---

This preregistration is a draft for OSF submission. After submission, it will receive a fixed timestamp and DOI; deviations from this plan in the final paper will be marked as exploratory rather than confirmatory.
