I've written the weekly report and rendered `report.pdf`. `build.sh` regenerates the figures and renders the PDF in one run, with no warnings and no unresolved citations.

**Page count:** 18 pages. The main text is pages 1–14, with the one-page summary and five decisions first. The appendix is pages 15–17 and the references pages 17–18. To get the main text to 14 pages I moved the square-pinhole derivation, the Phase 0 figure and two resolution figures into the appendix.

**Figures (20):**
- **Drawn from the geometry (4):** converging pixels with the edge strip; the forward-model block diagram; the two pinhole resolution terms; box ⊗ box vs Gaussian quadrature.
- **Regenerated from the data (8):** WP1 spot width and window agreement; WP3 checkpoint; scatter spectra by class; kernel coverage before and after the fix; the correction ladder; Jaszczak uniform-section profile; Derenzo and triple-line slices; Jaszczak slices.
- **Copied unchanged from the 28 Oct reports (8):** WP0 spectra, terms vs b, information vs frequency, Phase 0, square pinhole PSF, point-response profiles, scorecard, WP2b maps.

**Unresolved items** (all in `ingredients/draft_log.md`):
- **WP1 case count:** facts.md says 13 cases, but `wp1_results.json` and the paper-2 plan have 10. The report uses 10.
- **Dropped citations:** Lai & Meng 2018 and Mandot 2025 because their titles could not be verified (web search was not permitted). Seven citation-only and two web-snippet entries were dropped under the brief's rule, including the original TEW, GATE and OSEM papers.
- **Hutton review kept:** it is marked citation-only, but facts.md names it as the general scatter reference, so it is cited for background only.
- **Removed claims:** three statements I had written without a source.
- **Bibliography style:** no `ieee.csl` was on disk, so I used Typst's built-in IEEE style.
- **Noisy reference profile:** the primary-only reference in the Jaszczak profile is noisy at 128 iterations; it is shown as computed and the caption says why.
- **WP0 compute cost:** no source gives it, so it is not in the compute table.
- **Cardiac comparison:** only qualitative, from the plan; no cardiac numbers were found.
