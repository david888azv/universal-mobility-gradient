# Universal Phenomenology, Divergent Mechanism: A Behavioural Gradient of Mobility from Foraging to Commute

[![Status](https://img.shields.io/badge/Status-Submitted-orange)](https://www.nature.com/nature)
[![Journal](https://img.shields.io/badge/Journal-Nature-blue)](https://www.nature.com/nature)
[![Species](https://img.shields.io/badge/Species-11_animals_+_human-brightgreen)](#-master-summary)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](LICENSE)
[![Data](https://img.shields.io/badge/Data-CC0%201.0-green)](https://www.datarepository.movebank.org/)
[![Preregistered](https://img.shields.io/badge/Preregistered-OSF-purple)](#-manuscript-status)

## 📄 Manuscript Status

<p align="justify">
<strong>This single-author manuscript has been submitted to <a href="https://www.nature.com/nature"><em>Nature</em></a> as an Article and is currently under editorial consideration.</strong> While the paper is in peer review, the manuscript text, the cover letter and the preregistration are not redistributed here; this repository hosts only the <em>figures</em> and the <em>figure-level numerical data</em> (CSV) needed to inspect, verify or re-plot the published results. The full text and supporting documents will be linked here upon acceptance. In the meantime, the corresponding author can supply them on reasonable request.
</p>

---

## 👤 Author

| Author | Affiliation | Contact |
|---|---|---|
| **Prof. David L. Azevedo** | Instituto de Física, Universidade de Brasília (UnB), Campus Darcy Ribeiro, 70910-900 Brasília-DF, Brazil | 📧 david888azv@unb.br |

---

## 📋 Abstract (short form)

<p align="justify">
Three influential scaling laws of human mobility — the truncated power law of step lengths and the bounded radius of gyration [1], the universal visitation law ρ ∝ (rf)<sup>−2</sup> [2], and the hierarchical-container architecture [3] — were established on datasets of 10<sup>5</sup>–10<sup>7</sup> humans and have since been treated as a human-specific phenomenology. Animal-movement ecology has developed in parallel around a different paradigm based on Lévy-flight foraging [4–6], optimal-foraging theory [7] and home-range allometry. Here I apply a single estimator battery to GPS records of <strong>eleven vertebrate species</strong> spanning a behavioural-energetic gradient — nomadic ungulates (Mongolian gazelle, Burchell's zebra), home-ranging and central-place mammals (African elephant, olive baboon), seabirds and migrants (Northern gannet, Galápagos albatross, white stork), bats (<em>Eidolon helvum</em>, two studies), and marine reptiles (loggerhead turtle, Mediterranean and North-Pacific populations) — and compare the results with the published human values.
</p>

<p align="justify">
The phenomenological architecture is universal across all eleven species; the underlying microscopic mechanism is not. The Song preferential-return relations [8] hold closely only when the visitation Zipf exponent ζ approaches unity, defining a continuous gradient: from low-CP nomadism (ζ ≈ 0.3 for nomadic gazelles, oceanic turtles, and elephants), through migratory and seabird regimes (ζ ≈ 0.7–0.9), to strict central-place colonial life (ζ ≈ 1.6 for olive baboons and Galápagos albatrosses), bracketing the human value ζ ≈ 1.0 from both sides. The Schläpfer η = 2 [2] is a regime rather than a universal: all eleven non-human species sit at η ∈ [0.35, 1.13] (linear-cost regime), whereas humans on motorised infrastructure return η ≈ 2 (kinetic-cost regime). The Mongolian gazelle, a fully nomadic ungulate, exhibits the heaviest tail among non-human animals (α = 2.29 ± 0.11) — the closest non-human approach to the human Lévy reference α = 1.75 ± 0.15. Restricting the stork record to the obligate-CP breeding window yields α<sub>breed</sub> = 1.70 ± 0.05, statistically indistinguishable from the human value. Humans are therefore not a separate class of mobile organism but the extremum of a continuous behavioural-energetic axis.
</p>

### Key findings

- ✅ **Phenomenology is universal across 11 species.** Truncated power-law step lengths, logarithmic saturation of ⟨r_g(t)⟩, four to five hierarchically nested lognormal containers and circadian peaks of return are observed in every species, from nomadic gazelles to colonial baboons.
- 📈 **A continuous gradient in central-place strength.** ζ spans an unbroken interval ζ ∈ [0.26, 1.64] across the eleven species, bracketing the human value ζ ≈ 1.0 from both sides.
- 🐺 **Mongolian gazelle is the heaviest-tailed non-human.** α = 2.29 ± 0.11 is the closest non-human approach to the human Lévy reference α = 1.75 ± 0.15.
- 🚗 **Transport-regime split.** All eleven animal species sit at η ∈ [0.35, 1.13] (linear-cost regime); only humans on motorised infrastructure return η ≈ 2 (kinetic-cost regime). The split is governed by velocity heterogeneity, not phylogeny.
- 🐣 **Falsifiable test passes.** Restricting the stork record to the obligate-CP breeding window yields α = 1.70 ± 0.05, coinciding with the published human value 1.75 ± 0.15.
- 📐 **Two-parameter unification.** A minimal generative model with central-place strength γ_CP and velocity heterogeneity η_v places all twelve points (eleven species + human reference) on a continuous (γ_CP, η_v) diagonal.

### What this reshapes

<p align="justify">
The result reconciles Christaller's central-place theory with Charnov's marginal-value theorem under a single conserved-effort principle, offers a testable prediction for how "15-minute city" planning should shift urban η towards 1, and reinterprets the long-running Lévy-flight controversy as an artefact of fitting a single power law to a hierarchical-container mixture.
</p>

---

## 🗂️ Repository structure

```
universal-mobility-gradient/
├── figures/
│   ├── main/                    # Figures 1–4 of the main text (PDF + PNG, 300 dpi)
│   ├── extended_data/           # Extended Data Figures 1–4
│   └── supplementary/           # Per-species intermediate-block outputs
├── data/                        # Figure-level CSV exports (tidy)
│   ├── elephant/                #   – one CSV per figure, named fig<N>_<quantity>_<species>.csv
│   ├── gannet/
│   ├── stork/
│   ├── albatross/               #   ── new species (2026 sweep) ──
│   ├── bat_scharf/
│   ├── bat_abedi/
│   ├── turtle_med/
│   ├── turtle_pac/
│   ├── zebra/
│   ├── baboon/
│   ├── gazelle/
│   └── cross_species/           # master table + unified-model sweep
├── assets/logos/                # Institutional logos used in acknowledgements
├── LICENSE                      # CC BY 4.0
└── README.md                    # You are here
```

> 📝 **Note.** The full manuscript PDF, the cover letter, the preregistration and the BibTeX file are intentionally **not** included while the paper is in peer review. They will be added (or linked to the published *Nature* DOI) once the editorial process is complete.

### Data folder — naming convention

<p align="justify">
Every CSV lives in <code>data/&lt;species&gt;/</code> and follows the pattern <code>fig&lt;figure_number&gt;_&lt;quantity&gt;_&lt;species&gt;.csv</code>, so a reviewer can locate the numerical content of any panel from its filename alone. For example:
</p>

| File | Content |
|---|---|
| `data/gazelle/fig1_step_length_gazelle.csv` | Log-binned P(Δr) for 36 Mongolian gazelles |
| `data/baboon/fig2_zipf_rank_frequency_baboon.csv` | Top-50 pooled rank–frequency (Mpala troop) |
| `data/albatross/fig3_bootstrap_exponents_albatross.csv` | α, ζ, μ, γ, β, η with bootstrap SE and 95% CI |
| `data/stork/fig4a_seasonal_alpha_stork.csv` | Stork tail exponent per seasonal phase (Fig. 4a) |
| `data/cross_species/master_table_all_exponents.csv` | Master table — all 11 species + human reference |
| `data/cross_species/fig4bc_unified_model_sweep.csv` | 9 × 7 (γ_CP, η_v) sweep producing Fig. 4b,c & Ext. Fig. 4 |
| `data/<species>/extdata1_containers_<species>.csv` | Container effective sizes per grid level (Ext. Fig. 1) |

### Figures folder

- `figures/main/` — publication versions of Figures 1–4 (vector PDF and 300 dpi PNG on Nature's double-column width of 183 mm). All four main figures now incorporate the eleven-species sweep.
- `figures/extended_data/` — four Extended Data figures:
  - **Ext. Fig. 1** — Alessandretti hierarchical containers (three benchmark species).
  - **Ext. Fig. 2** — Per-species P(Δr) overlay, raw and rescaled by the median step length.
  - **Ext. Fig. 3** — Forest plot of all six exponents across the eleven species + human.
  - **Ext. Fig. 4** — Unified-model parameter-sweep heatmaps with all twelve points overlaid.
- `figures/supplementary/<species>/` — intermediate results from each of the four estimator blocks (A — González; B — Song; C — Alessandretti; D — Schläpfer).

### Manuscript and supporting documents

<p align="justify">
The submitted manuscript, the cover letter, the OSF-style preregistration (four falsifiable hypotheses H1–H4 with explicit refutation criteria) and the BibTeX database are withheld from public release while peer review is in progress at <em>Nature</em>. They are available on reasonable request from the corresponding author and will be linked from this repository once the manuscript is accepted or made publicly available as a preprint.
</p>

### Scripts

<p align="justify">
The full analysis pipeline (Python 3.13 — NumPy 2.4, pandas 3.0, SciPy 1.17, Matplotlib 3.10) can be obtained <strong>on request from the corresponding author</strong> (david888azv@unb.br). The pipeline is structured as four modular blocks:
</p>

- **Block A** (González 2008): P(Δr) tail fitting, r_g distribution, return probability, Zipf.
- **Block B** (Song 2010): S(t), P_new(S), waiting times, three scaling relations.
- **Block C** (Alessandretti 2020): multi-scale container grid + lognormal KS test.
- **Block D** (Schläpfer 2021): ρ(r,f) visitation regression on 4-month windows.

<p align="justify">
The pipeline also includes a block-bootstrap by individual, a stork seasonal split, a two-parameter unified simulator, and a multi-species sweep driver (<code>run_all.py</code>) that loops over all eleven species automatically.
</p>

---

## 📊 Master summary

<p align="justify">
Mean ± standard error from bootstrap by individual (N<sub>boot</sub> = 500 for every species except white stork at N<sub>boot</sub> = 50). Full confidence intervals are listed in <a href="data/cross_species/master_table_all_exponents.csv"><code>data/cross_species/master_table_all_exponents.csv</code></a>.
</p>

| Species (n indiv) | α | ζ | μ | γ | β | η |
|---|---|---|---|---|---|---|
| Mongolian gazelle (n=36) | **2.29 ± 0.11** | 0.38 ± 0.06 | 0.92 ± 0.02 | −0.11 ± 0.04 | 1.56 ± 1.19 | 0.53 ± 0.09 |
| Loggerhead turtle, N. Pacific (n=12) | 2.72 ± 0.20 | 0.29 ± 0.06 | 0.94 ± 0.05 | −0.01 ± 0.04 | 2.33 ± 0.42 | 1.13 ± 0.34 |
| Northern gannet (n=25) | 2.83 ± 0.32 | 0.89 ± 0.05 | 0.93 ± 0.04 | −0.13 ± 0.05 | 1.20 ± 0.89 | 0.65 ± 0.07 |
| *Eidolon helvum*, Burkina (n=63) | 3.24 ± 0.38 | 0.71 ± 0.07 | 0.76 ± 0.08 | −0.42 ± 0.07 | 0.71 ± 0.03 | 0.77 ± 0.08 |
| African elephant (n=14) | 3.40 ± 0.18 | 0.28 ± 0.07 | 0.82 ± 0.03 | 0.09 ± 0.03 | 1.89 ± 0.70 | 1.03 ± 0.04 |
| White stork (n=92) | 3.48 ± 0.12 | 0.86 ± 0.04 | 1.98 ± 0.11 | −0.56 ± 0.02 | 1.06 ± 0.60 | 1.09 ± 0.05 |
| ↳ stork, breeding subset only | **1.70 ± 0.05** | — | — | — | — | — |
| Loggerhead turtle, Mediterranean (n=11) | 3.56 ± 0.27 | 0.26 ± 0.06 | 0.91 ± 0.04 | 0.02 ± 0.05 | — | 0.44 ± 0.20 |
| Galápagos albatross (n=28) | 3.90 ± 0.36 | 1.64 ± 0.09 | 1.35 ± 0.15 | −0.15 ± 0.13 | 1.14 ± 0.23 | 0.96 ± 0.12 |
| *Eidolon helvum*, Ghana (n=28) | 4.29 ± 1.11 | 0.97 ± 0.10 | 0.84 ± 0.15 | −0.57 ± 0.16 | 0.78 ± 0.05 | 0.67 ± 0.09 |
| Olive baboon, Mpala (n=26) | 4.35 ± 0.08 | 1.58 ± 0.02 | 0.50 ± 0.03 | — | 3.15 ± 4.69 | 0.35 ± 0.09 |
| Burchell's zebra (n=7) | 5.74 ± 1.59 | 0.56 ± 0.10 | 0.97 ± 0.06 | −0.09 ± 0.08 | 3.37 ± 0.65 | 0.75 ± 0.11 |
| Human (literature) | 1.75 ± 0.15 [1] | ≈ 1.0 [1] | 0.60 [8] | 0.21 [8] | 0.80 [8] | 2.05 ± 0.02 [2] |

<p align="justify">
Bold entries mark the values that lie closest to the published human reference: the Mongolian gazelle has the heaviest non-human tail (closest to the human α), and the stork's breeding-window subset coincides with the human α to within 0.05.
</p>

---

## 🔗 Primary data sources

<p align="justify">
All eleven GPS tracking datasets are hosted in public repositories under permissive Creative Commons licences (<strong>CC0 1.0</strong> in every case). I gratefully acknowledge the original data owners for making the records publicly available:
</p>

| Species (common name) | Location and period | Repository / DOI | Depositors |
|---|---|---|---|
| *Loxodonta africana* (African elephant) | Kruger NP, South Africa, 2007–2009 | [10.5441/001/1.403h24q5](https://doi.org/10.5441/001/1.403h24q5) | R. Slotow, M. Thaker & A. T. Vanak |
| *Morus bassanus* (Northern gannet) | Cape St Mary's, Newfoundland, 2019–2022 | Movebank handle [10255/move.1592](https://www.movebank.org/) | K. J. N. d'Entremont, G. K. Davoren & W. A. Montevecchi |
| *Ciconia ciconia* (white stork) | SW Germany breeding grounds, 2013–2023 | Movebank handle [10255/move.1685](https://www.movebank.org/) | Y. Cheng, W. Fiedler, M. Wikelski & A. Flack |
| *Phoebastria irrorata* (Galápagos albatross) | Española Island, Galápagos, 2008 | [10.5441/001/1.3hp3s250](https://doi.org/10.5441/001/1.3hp3s250) | F. H. Cruz, P. D. Proaño, D. J. Anderson, K. P. Huyvaert, M. Wikelski |
| *Eidolon helvum* (straw-coloured fruit bat) — Scharf et al. 2019 | Burkina Faso / Ghana, 2009–2014 | [10.5441/001/1.k8n02jn8](https://doi.org/10.5441/001/1.k8n02jn8) | A. Scharf, J. Fahr, M. Abedi-Lartey, K. Safi, D. K. N. Dechmann, M. Wikelski, M. T. O'Mara |
| *Eidolon helvum* (straw-coloured fruit bat) — Abedi-Lartey 2016 | Ghana, 2016 (seed-dispersal study) | [10.5441/001/1.44183438](https://doi.org/10.5441/001/1.44183438) | M. Abedi-Lartey, D. K. N. Dechmann, M. Wikelski, A. Scharf, J. Fahr |
| *Caretta caretta* (loggerhead sea turtle) — Mediterranean | Western Mediterranean Sea, 2017+ | [10.5441/001/1.1f1h87r8](https://doi.org/10.5441/001/1.1f1h87r8) | S. Hochscheid |
| *Caretta caretta* (loggerhead sea turtle) — N. Pacific | Japan / North Pacific, 2016+ | [10.5441/001/1.m3c90703](https://doi.org/10.5441/001/1.m3c90703) | J. Okuyama et al. |
| *Equus quagga burchellii* (Burchell's zebra) | Okavango / Makgadikgadi, Botswana, 2007–2009 | [10.5441/001/1.f3550b4f](https://doi.org/10.5441/001/1.f3550b4f) | H. L. A. Bartlam-Brooks & S. Harris |
| *Papio anubis* (olive baboon) | Mpala Research Centre, Kenya, August 2012 | [10.5441/001/1.kn0816jn](https://doi.org/10.5441/001/1.kn0816jn) | M. C. Crofoot, R. Kays, M. Wikelski (Strandburg-Peshkin et al. 2015) |
| *Procapra gutturosa* (Mongolian gazelle) | Eastern Mongolian Steppe, 2007–2010 | Dryad [10.5061/dryad.45157](https://doi.org/10.5061/dryad.45157) | C. H. Fleming, J. M. Calabrese, T. Mueller, K. A. Olson, P. Leimgruber, W. F. Fagan |

<p align="justify">
Human reference values are taken directly from refs. [1, 2, 3, 8]; no proprietary human data were analysed.
</p>

---

## 🔑 Keywords

`human mobility` · `animal movement ecology` · `scaling laws` · `Lévy flight` · `central-place foraging` · `Zipf law` · `visitation law` · `hierarchical containers` · `preferential return` · `Movebank` · `Dryad` · `cross-species synthesis` · `statistical physics`

---

## 🙏 Acknowledgements

<p align="center">
  <img src="assets/logos/cnpq.png"  alt="CNPq"  height="60"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/logos/fapdf.png" alt="FAPDF" height="60"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/logos/unb.png"   alt="UnB"   height="60"/>
</p>

<p align="justify">
D. L. Azevedo acknowledges financial and infrastructural support from the <strong>Fundação de Apoio à Pesquisa do Distrito Federal (FAPDF)</strong> under calls 04/2017 and 09/2022, and from the <strong>Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPq)</strong> through research-productivity fellowship 306456/2025-7 (PQ-C). Computational resources were provided by the <strong>Centro Nacional de Processamento de Alto Desempenho em São Paulo (CENAPAD-SP)</strong>.
</p>

<p align="justify">
This work would not have been possible without the eleven public datasets that the original investigators chose to release under CC0 1.0; the author thanks them and the curators of the <strong>Movebank Data Repository</strong> (Max Planck Institute of Animal Behavior) and the <strong>Dryad Digital Repository</strong> for sustaining the long-term infrastructure that makes cross-species synthesis tractable. Specific dataset depositors are listed in the table above.
</p>

---

## 📖 Citation

<p align="justify">
If you use this repository in your research, please cite both the manuscript (currently under review) and the underlying public datasets.
</p>

```bibtex
@article{Azevedo2026Mobility,
  author  = {Azevedo, David L.},
  title   = {Universal phenomenology, divergent mechanism:
             a behavioural gradient of mobility from foraging to commute},
  journal = {Nature},
  year    = {2026},
  note    = {Submitted}
}
```

---

## 📜 License

<p align="justify">
The analysis outputs and the manuscript are released under the <a href="https://creativecommons.org/licenses/by/4.0/"><strong>Creative Commons Attribution 4.0 International License</strong></a>. The underlying GPS tracking data remain under their original CC0 1.0 Universal terms as deposited on Movebank and Dryad.
</p>

---

## 📬 Contact

For questions, pipeline requests, or collaboration enquiries:

**Prof. David L. Azevedo**
Instituto de Física, Universidade de Brasília (UnB)
📧 [david888azv@unb.br](mailto:david888azv@unb.br)

---

## 🔖 Key references

1. González, Hidalgo & Barabási. *Nature* **453**, 779 (2008).
2. Schläpfer et al. *Nature* **593**, 522 (2021).
3. Alessandretti, Aslak & Lehmann. *Nature* **587**, 402 (2020).
4. Viswanathan et al. *Nature* **381**, 413 (1996).
5. Sims et al. *Nature* **451**, 1098 (2008).
6. Humphries et al. *Nature* **465**, 1066 (2010).
7. Charnov. *Theor. Popul. Biol.* **9**, 129 (1976).
8. Song, Koren, Wang & Barabási. *Nat. Phys.* **6**, 818 (2010).
9. Cheng, Fiedler, Wikelski & Flack. *Ecol. Evol.* **9**, 8945 (2019).

<p align="justify">
The full bibliography is included in the submitted manuscript and will be linked here upon publication.
</p>
