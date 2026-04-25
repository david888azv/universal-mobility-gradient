# Universal Phenomenology, Divergent Mechanism: A Behavioural Gradient of Mobility from Foraging to Commute

[![Status](https://img.shields.io/badge/Status-Submitted-orange)](https://www.nature.com/nature)
[![Journal](https://img.shields.io/badge/Journal-Nature-blue)](https://www.nature.com/nature)
[![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)](LICENSE)
[![Data](https://img.shields.io/badge/Data-CC0%201.0-green)](https://www.datarepository.movebank.org/)
[![Preregistered](https://img.shields.io/badge/Preregistered-OSF-purple)](paper/preregistration.md)

## 📄 Manuscript Status

**This single-author manuscript has been submitted to [*Nature*](https://www.nature.com/nature) as an Article and is under editorial consideration. Companion files (manuscript PDF, cover letter, preregistration and a master table of all fitted exponents with 95% bootstrap confidence intervals) are provided in [`paper/`](paper/).**

---

## 👤 Author

| Author | Affiliation | Contact |
|---|---|---|
| **Prof. David L. Azevedo** | Instituto de Física, Universidade de Brasília (UnB), Campus Darcy Ribeiro, 70910-900 Brasília-DF, Brazil | 📧 david888azv@unb.br |

---

## 📋 Abstract (short form)

Three influential scaling laws of human mobility — the truncated power law of step lengths and bounded radius of gyration [1], the universal visitation law ρ ∝ (rf)^−2 [2], and the hierarchical-container architecture [3] — were established on datasets of 10⁵–10⁷ humans and have been treated as a human-specific phenomenology. Animal-movement ecology has developed in parallel around a different paradigm based on Lévy-flight foraging [4–6], optimal foraging theory [7] and home-range allometry. Here I apply a single estimator battery to GPS records of **14 African elephants, 25 Northern gannets and 92 white storks** tracked for up to a decade and compare with the published human values.

### Key findings

- ✅ **Phenomenology is universal.** All three species exhibit truncated power-law step lengths, logarithmic saturation of ⟨r_g(t)⟩, four to five hierarchically nested lognormal containers and circadian peaks of return.
- ⚙️ **Mechanism is graded, not universal.** Song's preferential-return relations [8] hold only as the Zipf exponent ζ approaches 1, defining a gradient ζ = 0.28 (elephant) → 0.86–0.89 (stork, gannet) → 1.0 (human).
- 🚗 **Transport-regime split.** Schläpfer's η = 2 is a regime: near-constant-velocity animals return η ≈ 1; motorised humans return η = 2. The split is by velocity heterogeneity, not phylogeny.
- 🐣 **Falsifiable test passes.** Restricting the stork record to the obligate-CP breeding window yields α = 1.70 ± 0.05, coinciding with the published human value 1.75 ± 0.15.
- 📐 **Two-parameter unification.** A minimal generative model with central-place strength γ_CP and velocity heterogeneity η_v places all four species on a continuous (γ_CP, η_v) diagonal.

### What this reshapes

The result reconciles Christaller's central-place theory with Charnov's marginal-value theorem under a single conserved-effort principle, offers a testable prediction for how "15-minute city" planning should shift urban η towards 1, and reinterprets the long-running Lévy-flight controversy as an artefact of fitting a single power law to a hierarchical-container mixture.

---

## 🗂️ Repository structure

```
universal-mobility-gradient/
├── paper/                       # Submitted manuscript, cover letter, preregistration, BibTeX
│   ├── manuscript.pdf
│   ├── cover_letter.pdf
│   ├── preregistration.md
│   └── references.bib
├── figures/
│   ├── main/                    # Figures 1–4 of the main text (PDF + PNG, 300 dpi)
│   ├── extended_data/           # Extended Data Figure 1 (container hierarchy)
│   └── supplementary/           # Per-species intermediate-block outputs
│       ├── elephant/            #   – Block A–D partial results
│       ├── gannet/              #   – Block A–D partial results
│       └── stork/               #   – Block A–D partial results + seasonal split
├── data/                        # Figure-level CSV exports (tidy)
│   ├── elephant/                #   – one CSV per figure, named fig<N>_<quantity>_<species>.csv
│   ├── gannet/
│   ├── stork/
│   └── cross_species/           #   – master table and unified-model sweep
├── assets/logos/                # Institutional logos used in acknowledgements
├── LICENSE                      # CC BY 4.0
└── README.md                    # You are here
```

### Data folder — naming convention

Every CSV lives in `data/<species>/` and follows the pattern

```
fig<figure_number>_<quantity>_<species>.csv
```

so a reviewer can locate the numerical content of any panel from its filename alone. For example:

| File | Content |
|---|---|
| `data/elephant/fig1_step_length_elephant.csv` | Log-binned P(Δr) for 14 elephants (Fig. 1a) |
| `data/gannet/fig2_zipf_rank_frequency_gannet.csv` | Top-50 pooled rank–frequency pairs (Fig. 2a) |
| `data/stork/fig3_bootstrap_exponents_stork.csv` | α, ζ, μ, γ, β, η with bootstrap SE and 95% CI (Fig. 3) |
| `data/stork/fig4a_seasonal_alpha_stork.csv` | Stork tail exponent per seasonal phase (Fig. 4a) |
| `data/cross_species/master_table_all_exponents.csv` | Table 1 of the manuscript, all species + human reference |
| `data/cross_species/fig4bc_unified_model_sweep.csv` | 9 × 7 (γ_CP, η_v) sweep producing Fig. 4b,c |
| `data/<species>/extdata1_containers_<species>.csv` | Container effective sizes per grid level (Extended Data Fig. 1) |

### Figures folder

- `figures/main/` — publication versions of Figures 1–4 (vector PDF and 300 dpi PNG on Nature's double-column width of 183 mm).
- `figures/extended_data/` — hierarchical-container plot cited in §2.5 of the manuscript.
- `figures/supplementary/<species>/` — intermediate results from each of the four estimator blocks (A — González; B — Song; C — Alessandretti; D — Schläpfer). Reviewers can use these to verify how the headline exponents emerge from the raw data per species.

### Paper folder

- `manuscript.pdf` — submitted LaTeX-compiled manuscript (17 pages including methods, references and figures).
- `cover_letter.pdf` — cover letter addressed to *Nature*'s editors.
- `preregistration.md` — OSF-style preregistration of the four falsifiable hypotheses (H1–H4), pre-specified pipeline, and explicit refutation criteria.
- `references.bib` — BibTeX database of all 40 citations.

### Scripts

The full analysis pipeline (Python 3.13 — NumPy 2.4, pandas 3.0, SciPy 1.17, Matplotlib 3.10) can be obtained **on request from the corresponding author** (david888azv@unb.br). The pipeline is structured as four modular blocks:
- **Block A** (González 2008): P(Δr) tail fitting, r_g distribution, return probability, Zipf.
- **Block B** (Song 2010): S(t), P_new(S), waiting times, three scaling relations.
- **Block C** (Alessandretti 2020): multi-scale container grid + lognormal KS test.
- **Block D** (Schläpfer 2021): ρ(r,f) visitation regression on 4-month windows.
Plus a block-bootstrap by individual, a stork seasonal split, and a two-parameter unified simulator.

---

## 📊 Master summary

| Metric | Elephant (n=14) | Gannet (n=25) | White stork (n=92) | Human (literature) |
|---|---|---|---|---|
| **α** — P(Δr) tail exponent | 3.40 ± 0.18 | 2.83 ± 0.32 | 3.48 ± 0.12 | 1.75 ± 0.15 [1] |
| **α (breeding subset)** | — | — | **1.70 ± 0.05** | 1.75 ± 0.15 [1] |
| **ζ** — Zipf rank–frequency | 0.28 ± 0.07 | 0.89 ± 0.05 | 0.86 ± 0.04 | ≈ 1.0 [1] |
| **η** — visitation law | 1.03 ± 0.04 | 0.65 ± 0.07 | 1.09 ± 0.05 | 2.05 ± 0.02 [2] |

All animal entries are mean ± 95% bootstrap CI by individual (N_boot = 500 elephant/gannet, 50 stork). Full table in [`data/cross_species/master_table_all_exponents.csv`](data/cross_species/master_table_all_exponents.csv).

---

## 🔗 Primary data sources

All three GPS tracking datasets are hosted by the [**Movebank Data Repository**](https://www.datarepository.movebank.org/) and licensed under **CC0 1.0 Universal** (public domain dedication). I gratefully acknowledge the original data owners for making the records publicly available:

| Species | Location and period | DOI / Handle | Depositors |
|---|---|---|---|
| *Loxodonta africana* (African elephant) | Kruger NP, South Africa, 2007–2009 | [10.5441/001/1.403h24q5](https://doi.org/10.5441/001/1.403h24q5) | R. Slotow, M. Thaker & A. T. Vanak |
| *Morus bassanus* (Northern gannet) | Cape St Mary's, Newfoundland, 2019–2022 | Movebank handle [10255/move.1592](https://www.movebank.org/) | K. J. N. d'Entremont, G. K. Davoren & W. A. Montevecchi |
| *Ciconia ciconia* (white stork) | SW Germany breeding grounds, 2013–2023 | Movebank handle [10255/move.1685](https://www.movebank.org/) | Y. Cheng, W. Fiedler, M. Wikelski & A. Flack [9] |

Human reference values are drawn directly from refs. [1,2,3,8]; no proprietary human data were analysed.

---

## 🔑 Keywords

`human mobility` · `animal movement ecology` · `scaling laws` · `Lévy flight` · `central-place foraging` · `Zipf law` · `visitation law` · `hierarchical containers` · `preferential return` · `Movebank` · `statistical physics`

---

## 🙏 Acknowledgements

<p align="center">
  <img src="assets/logos/cnpq.png"  alt="CNPq"  height="60"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/logos/fapdf.png" alt="FAPDF" height="60"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/logos/unb.png"   alt="UnB"   height="60"/>
</p>

D. L. Azevedo acknowledges financial and infrastructural support from the **Fundação de Apoio à Pesquisa do Distrito Federal (FAPDF)** under calls 04/2017 and 09/2022, and from the **Conselho Nacional de Desenvolvimento Científico e Tecnológico (CNPq)** through research productivity fellowship 306456/2025-7 (PQ-C). Computational resources were provided by the **Centro Nacional de Processamento de Alto Desempenho em São Paulo (CENAPAD-SP)**.

The author is also grateful to the **Movebank Data Repository** and to the data owners listed above for making the three GPS tracking datasets publicly available under the CC0 1.0 licence.

---

## 📖 Citation

If you use this repository in your research, please cite both the preprint and the underlying Movebank datasets.

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

The analysis outputs and manuscript are released under the [**Creative Commons Attribution 4.0 International License**](https://creativecommons.org/licenses/by/4.0/). The underlying GPS tracking data remain under their original CC0 1.0 Universal terms as deposited on Movebank.

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

Full bibliography in [`paper/references.bib`](paper/references.bib).
