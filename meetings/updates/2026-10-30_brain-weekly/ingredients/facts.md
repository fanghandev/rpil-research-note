# Facts sheet (verified numbers and their sources)

Paths are relative to `~/Work/RPIL/QMIRT/`. `PLAN` = `pytorch-optix/docs/paper2_plan.md`. Read the cited sections in full before writing; they contain more detail than listed here.

## System (internal)
- **Modules and pinholes:** 73 modules; pinholes on a sphere of radius 149.6 mm, all aimed at the centre. Square double-sided knife-edge pinholes, 45° on both sides.
- **Aperture widths:** A/B/C/D = 0.556 / 0.797 / 1.215 / 2.007 mm. Current inventory 19/18/18/18; the annealed map uses 18/18/18/19.
- **Distances:** pinhole to crystal entrance 25 mm; mean interaction depth gives f = 27 mm (gammart Phase 0: 27.0-27.4 mm).
- **Crystal:** CsI:Tl block, 50 × 50 × 10 mm. Energy resolution 11.8 % FWHM at 140 keV. Main window 126-154 keV.
- **Converging LIOB pixels:** 25 × 25, pitch 1.4286 mm at the entrance and 2.0 mm at the exit; walls converge on the pinhole.
- **Edge strip:** the outer walls are at ±17.9 mm at the entrance and ±25 mm at the exit. The strip is CsI outside the outermost wall, 7.1 mm wide at the entrance and 0 at the exit.
- **Sources:**
  - `pytorch-optix/gammart/readout.py`
  - `gammart/scene/brain_converging.py`
  - `qmirt-gate-10-sim/dev/reports/2026-10-28_analytic_resolution/analytic_baseline.qmd` (section "The formulas and the constants")

## WP0: spectrum mismatch (FINAL). Source: PLAN "WP0 results (2026-10-28)"; out/wp0/bands_t2.json; figure out/wp0/spectra_t2.png
- **Air world:** the GATE/gammart ratio is 3.76 ± 0.10 at 60-90 keV, caused by backscatter from GATE's default air world. Vacuum: 1.39 ± 0.06. Standard physics (no Doppler): 0.96 ± 0.05.
- **Photopeak window:** within 1 % for all four variants.
- **Adopted settings:** vacuum world and option4 physics. gammart omits Doppler broadening, which affects the below-window spectrum only.

## WP1: single module (FINAL). Source: PLAN "WP1 and WP2 results (2026-10-28)"; out/wp1/wp1_results.json, figures out/wp1/*.png
- **Agreement:** window ratio 0.9991-1.0035 over 13 cases; pull rms 0.95-1.19.
- **Radial spot FWHM:**

  | incidence | 0° | 15° | 30° | 35° |
  |---|---|---|---|---|
  | converging (mm) | 1.91 | 1.89 | 1.83 | 1.81 |
  | parallel (mm) | 1.73 | 1.90 | 2.17 | 2.25 |

- **Fluorescence (GATE):** −1.7 to −2.0 % in-window at 0-30°, −16 % at 45°.
- **Edge strip, single-module beam:** 27 % of window events at 35°, 91 % at 45°.

## WP2: gammart full-system model (PROVISIONAL). Source: PLAN, same section
- **Speed:** full-system MC of 4e9 photons in about 1 min.
- **Deterministic converging matrix vs MC:** within 0.4-1.1 % on 5 modules; the top module is off by 3.5 % (unexplained).
- **Pre-crystal scatter:** 2.3-4.4 %.

## WP2b: aperture placement (PROVISIONAL: parallel pixels, no scatter). Source: PLAN "WP2b map-to-map variation", final "Conclusion (supersedes ...)" paragraph only
- **Between-map spread:** the SD of the 8 mm V/P across random maps is about 0.04.
- **Annealed maps:** a small repeatable gain (V/P 7 mm −0.035, CRC +0.4 %, NRMSE −0.2 %).
- **Uniform 1.215 mm** is ahead of all 12 mixed maps on every metric.
- **Scorecard** (28 Oct deck, `qmirt-gate-10-sim/dev/reports/2026-10-28_brain_update/update.md` scorecard table): uniform C vs the current mix, 8 mm V/P 0.41 vs 0.48 (±0.02).

## WP3: full-system GATE anchor (FINAL; checkpoint passed). Source: PLAN "WP3 results (2026-10-29)"; out/wp3/wp3_results.json, wp3_recon_results.json, figures out/wp3/*.png
- **Setup:** annealed map, vacuum, option4, fluorescence on and off. Phantoms in water: small Jaszczak, Derenzo, triple line.
- **GATE/gammart in-window counts per photon,** fluorescence off: 1.0022 / 1.0027 / 1.0032. Fluorescence costs a uniform 2.0 % (on/off 0.980).
- **Module and pixel pull rms:** 0.97-1.20.
- **Spectra:** the photopeak band agrees to 0.3 %. No edge-ring excess (no side leak).
- **Edge strip, extended phantoms:** 6.2 % of window events for the Jaszczak, 7.5 % for the triple line, 0.4 % for the Derenzo; worst module 22 % (triple line). The point source gives 0.12-0.16 %. For paper 2 the strip is its own element in data and model (consistent).
- **Reconstructions:** Derenzo V/P GATE vs gammart within 0.003. Triple-line FWHM within 0.08 mm.
- **Cost:** 19 SU charged on Expanse (production on the uncharged preempt partition, plus about 9 K core-h on OSPool); 6.2 GPU-h.
- **Open:** the fluorescence-off GATE excess of 0.2-0.3 %; the Jaszczak 25.4 mm sphere with fluorescence on (0.831 vs 0.864).
- **Correction:** the WP3 Jaszczak "uniformity_cov" used z −5..45 mm, which contains the cold rods. Invalid.

## WP4: reconstruction with corrections. Source: PLAN "WP4 results (2026-10-29)"; out/wp4/wp4_results.json/.md (wp4_analysis.py); images out/wp4/recon/<phantom>_<step>_<dataset>_it<NN>.npy (144^3, 2 mm, C order x slowest, centre at index 71.5)
- **Model:** ybar = K^T (A ∘ H) x + s.
  - H: first-interaction converging matrix, 144³ × 2 mm, r ≤ 142 mm, nnz 4.4e8.
  - A: attenuation per module and voxel.
  - K: Compton-centroid kernel.
  - s: smoothed TEW scatter estimate, as an additive term.
  - OSEM with 8 subsets.
- **Truth MC main-window composition** (primary / phantom-scattered / pre-crystal):

  | phantom | primary | phantom-scattered | pre-crystal |
  |---|---|---|---|
  | Jaszczak | 76.3 % | 22.4 % | 1.3 % |
  | Derenzo | 69.2 % | 29.4 % | 1.4 % |
  | triple line | 71.6 % | 27.1 % | 1.3 % |

- **Attenuation factors:** the median ratio to the exact analytic path is 1.0005-1.0008.
- **TEW totals (Derenzo):** plain TEW +5.4 % vs the truth. TEW with the primary tail removed −18 %, because the upper window holds almost no scatter at 140 keV and the primary tail compensates.
- **Kernel bug:** the WP2 water-sphere kernel left 104-156 of 625 rows empty (outer ring). Refitted from a uniform r = 140 mm sphere in air; every row has ≥ 3000 first interactions; efficiency 0.937.
- **Ladder at 128 iterations:** see the PLAN table. Key numbers:

  | data and model | Derenzo V/P 6 mm | Jaszczak 25.4 mm sphere contrast |
  |---|---|---|
  | reference (primary only) | 0.108 | 0.995 |
  | gammart ac_k, no scatter correction | 0.213 | 0.921 |
  | gammart + TEW | 0.145 | 0.999 |
  | gammart + true scatter | 0.145 | 0.997 |
  | GATE + TEW | 0.112 | 0.991 |

- **Cupping** (uniform section, centre/annulus): 0.86 without AC → 1.01 with AC.
- **TEW equals the true-scatter oracle** within 1 split SD in every metric.
- **Remaining gap = counting noise:** GATE has 26× the counts of gammart and reaches the reference.
- **Jaszczak uniform section:** z −90..−50 mm world. The water spans z −100..50; spheres at z ≥ −40.7; rods at 10.8-46.8.
- **Model-based scatter: PARKED.** The design and the acceleration ideas (forced detection, superpixels, fewer passes) are in PLAN.

## Resolution analysis. Source: `qmirt-gate-10-sim/dev/reports/2026-10-28_analytic_resolution/` (analytic_baseline.qmd + .html, analytic.json, _tables/*.md, img/*.png, phase0/phase0.md, lir/lir.md, derivation/square_pinhole.md)
- **Classic formula at the centre:** b = 149.6 mm and (b+f)/f = 6.541.
  - Detector term: parallel 2 × 149.6/27 = 11.08 mm; converging 8.55 mm.
  - Aperture term for C: 1.406 × 6.541 = 9.20 mm.
  - Module C, parallel: sqrt(9.20² + 11.08²) = 14.40 mm.
  - Best module at the centre: 12.1 mm. Count-weighted over all 73: 15.5 mm.
- **"About 7 mm"** is the aperture term alone (C, nominal: 7.95 mm at the centre) or the best module 35-60 mm off-centre.
- **"2-2.5x":** count-weighted analytic vs about 6 mm reconstructed gives 2.0-2.5× within 60 mm of the centre.
  - Source of the rule: Feng et al. (DC-SPECT, arXiv 2212.14505): about 10 mm calculated vs 4.5 mm reconstructed = 2.2× (our arithmetic).
- **Box ⊗ box caveat:** the same module C reads 14.4 mm in quadrature, 10.5 mm as an RMS-Gaussian equivalent, and 11.1 mm as the true FWHM.
- **Square pinhole:**
  - d_re = w + ln2·t/μ = w + 0.191 mm, exact along the sides at normal incidence (AM2004 eq. 29).
  - The Paix width equals the square's effective area at normal incidence (Metzler & Moore 2020 eq. 25).
  - The off-axis area is from Metzler & Moore eq. 22.
  - **Corrected error:** g = A cos³θ/(4π b²), not over r². The old form undercounted oblique modules by cos²θ.
  - Side/diagonal FWHM ratio √2. Equivalent round diameters: 1.13w for equal area, w for equal side FWHM, 1.155w for equal RMS.
- **Phase 0 (gammart):**
  - Sensitivity 0.975-0.989 of the formula, flat in θ and b.
  - Aperture spot width within 1 % at the centre.
  - The quadrature R is 15-30 % high at the centre; off-centre with parallel pixels the formula is too low (parallax).
- **Point response (LIR):**
  - The earlier GATE-matrix value of 6.4 mm was narrowed by Monte Carlo noise; the GATE matrix entries are 1-6 counts.
  - Noiseless gammart: 10.9 mm at the centre, and α-dependent. Withdrawn as an absolute resolution.
  - As a design comparison: converging pixels sharpen it by 1-2 mm; uniform C ≤ the current mix (lir/lir.md).
- **Phantom resolution:** the Derenzo separates 6 mm rods and 5 mm partly; sphere edges 5.3-6.7 mm; the triple line at 3.5 mm is the 2 mm-grid floor (28 Oct deck §6).

## Literature findings (quote with care; see the lit notes for verification levels)
- **Zannoni, Yang, Meng, IEEE TMI 2021** (full text):
  - Designs: uniform 1 mm vs a 0.5/1.5/3 mm mix.
  - FIM FWHM 20 vs 26 mm. Rods resolved at 20:1: 4 vs 6 mm.
  - Quotes in `lit_notes_meng_sabet_resolution.md`, with section numbers.
- **Meng & Clinthorne 2004 (MUCRB):** one size matched to the target resolution. **Meng & Li 2009:** finer detector pixels are the lever.
- **Rentmeester & Beekman 2008** (abstract): with detectors coarser than 1 mm, magnification is optimal.
- **Feng et al. 2022** (DC-SPECT, arXiv 2212.14505, full): see above. **DB-SPECT** (Feng et al., NSS/MIC 2022, abstract only): mixed 0.5-2 mm, compared only with a dual-head camera. Use neutral wording.
- **Scatter literature:** `lit_notes_scatter.md` (web, abstracts only). Use the Hutton/Buvat/Beekman 2011 review as the general citation.

## ACCESS (one paragraph)
- **Request:** a supplement for <account> asking for 700,000 ACCESS credits on NCSA Delta GPU (about 10,500 GPU-h at 66.67 credits/GPU-h), A40 RT-core GPUs for ray tracing.
- **Usage to date:** 509,166 / 700,000 Expanse SUs.
- **Source:** `pytorch-optix/docs/access_supplement/progress_report.qmd`
