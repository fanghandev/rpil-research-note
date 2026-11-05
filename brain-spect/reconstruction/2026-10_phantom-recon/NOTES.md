# Phantom reconstruction: notes and decisions

Working notes for the small-Jaszczak reconstruction study (brain SPECT, 288 mm Gate SRM). The
slides are `quarto/slides.qmd` (display only: numbers from the analysis JSON files, figures
pre-rendered by `dev/python/make_deck_extras.py`).

## Decided

### Scatter: model it, do not subtract it (2026-10-14)

Use the TEW estimate `s` as an additive term in the MLEM model, comparing the data `y` with
`H λ + s`, instead of subtracting it from the data and comparing `y − s` with `H λ`:

```
λ_j ← λ_j / Σ_i H_ij · Σ_i H_ij · y_i / (Σ_j' H_ij' λ_j' + s_i)
```

Why (measured on the simulated acquisition, where phantom scatter is tagged):

- Subtraction breaks the Poisson statistics MLEM assumes and roughly doubles the per-pixel relative
  noise (median 0.084 → 0.194); the TEW reconstructions have CoV 0.15 vs 0.10 for the
  scatter-free data at iteration 400.
- 3,463 of 45,326 pixels go negative and are clipped to 0, a positive bias in low-count pixels.
- The TEW estimate itself is right on average (25.1 M vs 23.4 M true scatter, 7 % high) and
  follows the scatter pattern (correlation 0.997), but is very noisy per pixel (estimate / true
  0.42–3.75, 10th–90th percentile): a typical pixel has about 23 counts in the lower window and
  1 in the upper.

Also planned: smooth `s` across neighbouring pixels of a module before use (scatter varies
slowly), which cuts its noise. Status: not implemented yet; today `measured_sets()` in
`dev/python/recon_brain_phantom_projections.py` subtracts and clips (`full_tew`).

## Open

- **Attenuation model vs the GATE SRM (2026-10-15).** `dev/python/ac_pixel_residuals.py` (CPU, no
  reconstruction): true phantom forward-projected through H and H·A vs the unscattered data. 2 mm: modules
  0.995–1.020, Pearson std 1.88; pixels with transmission 0.25–0.55 (93 % of counts) within 0.995–1.002,
  extremes (grazing rays / longest water paths) up to +20 %. 1 mm: modules 0.995–1.007, all bins 0.97–1.01,
  Pearson std 1.09. So the single voxel→pinhole-centre ray is adequate (collimator-penetration paths are
  not a measurable error); the 2 mm misfit is grid sampling at the phantom's surfaces (activity and/or
  attenuation). Next: 2 mm factors averaged over each voxel (e.g. from the 1 mm factors) to see whether
  the attenuation part alone explains it. In the deck: two check slides after the AC slides.

- **Rod background definition.** "footprint" (water within 1.5 rod pitches, the current default in
  `analyze_jaszczak_recon.masks`) vs "hull" (water inside the convex hull of the sector's rods).
  The hull lowers the small-rod contrasts (2 mm, TEW + AC, iteration 400: 4.8 mm 0.16 → 0.05,
  6.4 mm 0.25 → 0.18, 7.9 mm 0.43 → 0.40; 9.5–12.7 mm unchanged); grids still agree within 0.01.
  Comparison: `extras/rod_background_compare.json`.
- **Statistical uncertainty (done 2026-10-14).** 4 independent sub-acquisitions (jobs sorted by time,
  dealt 1, 5, 9, …), each merged and reconstructed (TEW + AC, 2 and 1 mm SRMs):
  `dev/python/brain_phantom_recon/doc_2026-10-14/subsets/`; statistics by
  `dev/python/subset_contrast_stats.py` → `extras/subset_stats.json`. SE at full counts = SD/√4.
  At iteration 400: rods ±0.003–0.016, spheres 12.7–25.4 mm ±0.006–0.022, spheres 6.4 and 9.5 mm
  ±0.06–0.07. Paired 2 − 1 mm differences ≤ 0.015 for every insert (both backgrounds); only the
  25.4 mm sphere exceeds its SE (+0.014 vs ±0.006, 2 mm higher). Caveat: SDs from K = 4 are
  uncertain by about ±40 %. In the deck: section 4, three slides.
- **Projector speed (2026-10-16, `dev/python/compact_gpu_mlem_performance.md`).** 1000 OSEM iterations take
  198 s on the RTX 3080 Ti and 180 s on the ERIS L40S: the projector is bound by its own memory traffic
  (~45 B per non-zero per iteration: fp16 -> fp32 staging copies, a row-index array, gathered temporaries,
  atomic `index_add_`). Planned: fused CSR forward/back kernels at the same 8.1 GB (fits the 3080 Ti),
  ~12 B per non-zero, expected ~2.5-3x on the L40S; a transposed CSC copy (no atomics, ~16 GB) only on
  48 GB GPUs. Not implemented; develop and benchmark on ERIS.
- **Convergence.** MLEM is far from converged at 400 iterations (45,625 measurements vs 1.6 M
  unknowns at 2 mm; AC slows it further). Next: OSEM with module subsets; later penalised
  likelihood or long MLEM + post-filter, so numbers do not depend on the stopping iteration.
  **OSEM / list mode (2026-10-14, `osem_listmode_report.md`):** `--algorithm {mlem,osem,lm-mlem,lm-osem}`
  in the driver. Binned OSEM with balanced module subsets (every S-th module of each ring) costs the
  same per iteration as MLEM and k iterations ≈ MLEM at k·S iterations (OSEM 8: 400 updates in 10 s
  vs 79 s); it fixes the global scale at once (accuracy ≈ 1.0 from iteration 1). Past ~400 updates it
  falls behind MLEM in likelihood and is noisier at equal updates (CoV 0.226 vs 0.190 at 1200 updates,
  S = 12): the limit cycle. List-mode MLEM = binned MLEM (≤ 10⁻⁴); list-mode OSEM gives no gain here
  (every event subset hits all rows: one full pass per update, ≈ MLEM per second). Also fixed: the
  compact engine's sensitivity was float32-accumulated (≤ 0.44 % voxel effect at 400 iterations;
  older runs not redone). Still open: penalised likelihood / OSEM-then-MLEM so numbers stop
  depending on S and the stopping point.
  **OSEM reference (2026-10-15, `osem_reference.md`):** OSEM 8 on `in_fov_primary` to 8000 updates,
  20 bootstrap copies for noise, post-filters 0–10 mm. Unfiltered nothing settles (noise CoV 1.07 at
  8000); with 8 mm every contrast changes ≤ 0.015 over 4000 → 8000 (noise 0.10), with 10 mm < 1 SD.
  Recovery 0.999–1.005 at every setting. Proposed reference: 8000 updates + 8 mm. Rod contrast rises
  with distance from the axis; edge overshoot band at r 60–67 mm unfiltered.
- **Error budget of the unscattered reconstruction (planned 2026-10-16, `error_budget_plan.md`).**
  Which factors keep the reconstruction from the truth: 2 mm grid, system resolution and sampling,
  algorithm, discretisation mismatch, counting noise, model mismatch. Ladder A–E (truth on the grid →
  noise-free inverse crime → noise-free from the 1 mm SRM → 20 Poisson draws → Gate data), one factor
  per step, OSEM 8 to 8000 updates; system what-ifs with gammart SRMs afterwards. Step D also does the
  bootstrap validation below. **Steps A–E run 2026-10-16 (ERIS gpu-l40s), analysed 2026-10-19 (CPU):
  `error_budget_analysis.py`, `error_budget_figures.py`, deck `quarto/error_budget.qmd`.** At 8000 updates
  + 8 mm the filter takes almost all contrast (rods 7.9 mm: PV truth 0.89 → filtered 0.32 → E 0.29);
  unfiltered, system + algorithm costs 0.09–0.48 (rods); discretisation, attenuation inside a voxel and
  noise bias ≤ 0.03; bootstrap CoV = independent-draw CoV within 2 % (except unfiltered 8000: +22 %);
  χ² per pixel 1.18, module totals ±0.25 % by ring; 15.9 mm sphere 2–3 σ low in E. Open: noise-free
  B/C roughen with updates (CoV 0.16 at 8000, 0.42 MLEM 20,000; fp16 SRM vs underdetermined system not
  separated); point-response resolution and SRM-noise steps not run. Note the truth level of C is a
  concentration in both bases (no ×8 between 1 mm and 2 mm).
- **Validate the bootstrap error bars (to do, deferred 2026-10-15).** The bootstrap SDs of
  `osem_reference.md` rest on theory (consistency for smooth statistics, delta method) and on
  literature (Haynor & Woods 1989, Buvat 2002, Dahlbom 2002: ~10 % agreement with repeated scans),
  not on a test for this system. Known weak points: low-count pixels (467 at 0, 12,462 < 10 counts;
  median 94, mean 1,762) cannot fluctuate in the copies, so noise there is underestimated; per-voxel
  SDs at high unfiltered updates (CoV ~1) are past the linear regime; 20 copies → SD ±16 %. Test:
  forward-project the true phantom (ȳ), draw ~20 independent Poisson data sets around ȳ, reconstruct
  them as in `osem_reference_runs.py` (their spread = true noise), bootstrap one of them, and compare
  the SDs (contrasts, uniform-section CoV, noise maps) at 400 / 1600 / 8000 updates, 0 and 8 mm.
  Pass: agreement within ~20 %. ~1.5 h GPU. Optional analytic cross-check: Barrett, Wilson & Tsui
  1994 (EM noise propagation). Citations from memory: check before formal use.

## Deck sections

- **Section 2 opens with the bare reconstruction (2026-10-15).** Four slides on `2mm_unscattered_u0_raw`
  (no support threshold, no AC: all 1,610,118 voxels of the 144³ grid with non-zero sensitivity, i.e. those
  intersecting the 288 mm source sphere; 1,386 voxels that only graze it got no counts): whole-FOV slices,
  phantom planes, line profiles along the longest rod row of each sector and radially through each
  sphere (iterations 20, 100, 400). Figures by `make_deck_extras.py --only bare` (CPU only).
  Decided: no 210 mm support test. The flipped phantom at z = −25 mm reaches r = 121 mm (5.9 % of the
  activity outside r = 105 mm), and real data always contain activity outside the nominal FOV, so we
  model the whole 288 mm grid. Note the 1000-count "support restriction" freezes 27,012 of those voxels (1,583,106 updated),
  all at the sphere's surface; it is not a smaller support.
- **Section 2, unscattered data (2026-10-14).** Runs `2mm_unscattered_u0_raw`, `2mm_unscattered_u1_support`
  (`run_unscattered.sh`) and the `in_fov_primary` set of `2mm_step3_ac`; metrics merged into
  `metrics.json`, figures and FWHM fits by `make_deck_extras.py --only unscattered`. At iteration 400:
  support changes nothing inside the phantom (outside share 91 % → 9 %); AC gives accuracy 0.25× → 0.99×,
  rim / centre 1.69 → 0.95, outside 0.2 %. Contrast is higher without AC at the same iteration but the
  image is wrong; the FWHM fit is reported for AC only (sloped background without AC).
- HTML (reveal.js) is the only format maintained for now; Typst / pptx settings left in place, not checked.
