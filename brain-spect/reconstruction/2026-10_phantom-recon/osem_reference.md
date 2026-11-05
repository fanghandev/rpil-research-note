# OSEM reference reconstruction of the unscattered data: contrast, noise and recovery

2026-10-15. Goal: a reconstruction of the small Jaszczak that can be cited, i.e. one whose numbers do
not depend on where the iterations stop, and the spatial distribution of its quality metrics.
Context: `NOTES.md` ("Convergence"), `osem_listmode_report.md` (OSEM implementation and validation).

## Setup

- **Data**: `in_fov_primary` of `full_small_jaszczak_15mCi_20261009T225845Z` (unscattered main-window
  counts, 80,402,994; all activity lies inside the FOV). The base of the study: data and model agree
  (the Gate SRM has no phantom scatter), so differences come from the reconstruction alone.
- **Reconstruction**: OSEM, 8 balanced module subsets (`module_subsets`; which modules are in which
  subset: `subsets/subsets_8_table.md`, `subsets_8_map.png`, `subsets_8_3d*.png`), 2 mm Gate SRM, support =
  air sensitivity > 1000, attenuation corrected (gammart factors), 1000 iterations = 8000 updates,
  28 saved iterations (log-spaced). Uniform start inside the support.
- **Post-filter**: 3D Gaussian, FWHM 0 (none), 4, 6, 8, 10 mm, applied to the saved estimates.
- **Noise**: Poisson bootstrap. 20 copies of the data, each a multinomial draw of the measured total
  over the 45,625 bins with probabilities y / Σy (identical to resampling the events with replacement;
  Buvat 2002, Phys. Med. Biol. 47:1761; Dahlbom 2002, IEEE TNS 49:2062), each reconstructed exactly as
  the measured data. Per voxel: bootstrap mean m and SD s.
- **Metrics** (definitions of `make_jaszczak_doc_figures` / `analyze_jaszczak_recon`, footprint rod
  background):
  - contrast = 1 − mean(insert) / mean(local background) for the 6 rod sectors and 6 spheres, plus every
    single rod against its sector's background;
  - recovery = mean in the uniform section (z −80 to −60 mm, r < 50 mm) / true concentration;
    rim / centre in that section;
  - noise: ensemble CoV = √(mean s²) / mean m over the uniform section (the proper noise), and the
    spatial CoV of one image (the earlier metric, which also contains non-uniformity);
  - statistical error of every contrast = its SD over the bootstrap copies.
- **Spatial distribution**: m / truth (recovery) and s / m (noise) per voxel, azimuthally averaged
  around the phantom axis into (r, z) maps over the "background water" (water > 4 mm from any wall,
  rod, sphere or plate), radial profiles in the uniform section, and slices through the uniform,
  sphere and rod planes.
- **Stability criterion**: over each doubling of the updates (8 → 16 → … → 4000 → 8000), the change of a
  metric divided by its bootstrap SD. A metric is "stable from N updates" when every later doubling
  changes it by less than 1 SD.

Code (dev/python): `osem_reference_runs.py` (reconstructions), `osem_reference_analysis.py` (metrics,
maps), `osem_reference_figures.py` (figures, `tables.md`, `stability.json`), `plot_osem_subsets.py`.
Outputs: `dev/python/brain_phantom_recon/osem_reference_2026-10-15/` (`analysis/`, `subsets/`).

Check: the measured-data reconstruction reproduces the earlier OSEM-8 run
(`doc_2026-10-14/algorithms/osem_s8`) to 2 × 10⁻⁵ (max relative voxel difference at 200 iterations,
GPU run-to-run level).

## Results

All numbers: `analysis/tables.md` (every filter, 80–8000 updates, ± bootstrap SD), `analysis/stability.json`;
figures in `analysis/figures/`. Every figure with a log axis also exists with linear axes (`*_linear.png`;
in `stability_linear.png` the y axis is cut at 5 SD).

### Summary

- **Without a post-filter nothing settles.** From 400 to 8000 updates rod 7.9 mm goes 0.46 → 0.67 and the
  12.7 mm sphere 0.57 → 0.65, while the ensemble noise goes 0.11 → 1.07 (voxel SD ≈ mean at 8000).
  The unfiltered image at any stopping point is a point on a moving trade-off, not a reference.
- **With a post-filter the contrasts level off**, and the wider the filter the earlier
  (`contrast_*_vs_updates.png`, `stability.png`). Change over the last doubling (4000 → 8000 updates),
  all inserts except the 6.4 mm sphere:

  | filter | largest change, rods | largest change, spheres ≥ 9.5 mm | noise at 8000 |
  |---|---|---|---|
  | none | +0.039 (6.4 mm) | +0.053 | 1.07 |
  | 4 mm | +0.031 | +0.046 | 0.29 |
  | 6 mm | +0.019 | +0.031 | 0.17 |
  | 8 mm | +0.009 | +0.015 | 0.10 |
  | 10 mm | +0.004 | +0.007 | 0.06 |

  With 8 mm every change is ≤ 1.5 SD of the statistical error; with 10 mm all are below 1 SD
  except the 6.4 mm rods (+0.004, SD 0.003).
- **The price is contrast.** At 8000 updates, 8 mm filter vs none: rod 7.9 mm 0.29 vs 0.67, rod 12.7 mm
  0.53 vs 0.82, sphere 25.4 mm 0.66 vs 0.85. A filtered reference reports contrast *at a stated
  resolution* (the filter), which is what makes it reproducible.
- **Activity recovery is right and stable at any setting**: 0.999–1.005 in the uniform section for every
  filter and every update count from 80 on (SD 0.002); stable from 256 updates.
- **Contrast against noise** (`contrast_noise_rods.png`, `contrast_noise_spheres.png`): at low noise all
  filters lie on one curve; at a given noise level, less filtering with fewer updates gives at least as
  much contrast as more filtering with more updates for every insert. Late updates combined with a wide
  filter buy stability, not contrast per noise.
- **The 6.4 mm sphere is not measurable** at these counts (SD 0.03–0.23, larger than most differences);
  the 9.5 mm sphere is marginal (SD 0.02–0.12). The 6.4 mm rods keep rising even at 10 mm: that sector
  is just being resolved.

### Spatial distribution

- **Contrast depends on the rod's distance from the axis** (`rod_contrast_vs_radius.png`): within a
  sector, rods further out have higher contrast. At 400 updates, unfiltered: 6.4 mm rods ≈ 0.18–0.20 at
  r 30–45 mm vs 0.25–0.37 at r 55–65 mm; 7.9 mm rods 0.35 at r 21 mm vs 0.52–0.57 at r 62 mm. The same
  at 8000 updates and with the 8 mm filter. This fits resolution improving toward the pinholes; it means
  a sector's contrast depends on where its rods sit, and the sectors are not directly comparable by
  diameter alone.
- **Recovery** (`radial_uniform_section.png`, `rz_recovery_f*.png`): flat at 1.00 ± 0.03 from the axis to
  r ≈ 55 mm, then a bright band just inside the wall (r 60–67 mm), 1.15–1.25 unfiltered, growing with
  updates: the edge overshoot already measured (`dev/python/streak_sampling_study.md`, Snyder 1987). With
  8 mm the band is gone; the drop in the last 5 mm is the filter blurring the wall. At 8000 updates a
  small rise near the axis (≈ 1.08 for r < 5 mm, also with 8 mm) appears; its cause (ripple inside the
  edge focusing on the axis, or the few voxels at small r) is not checked.
- **Noise** (`rz_noise_f*.png`, `slice_*_noise.png`): unfiltered, it rises from the axis to the wall (at
  1600 updates 0.21 → 0.44). Filtered, the pattern reverses: with 8 mm at 8000 updates 0.12 near the axis
  vs 0.05 at the wall. Axially, noise is highest at the bottom of the phantom (z < −80 mm), the lower edge
  of the FOV.
- **Rim / centre** keeps falling with updates (unfiltered 0.947 at 400 → 0.911 at 8000) and is not a
  useful number with a filter (the rim ring r 60–70 mm then includes the blurred wall).

### Proposed reference

OSEM, 8 subsets, **8000 updates (1000 iterations), 8 mm FWHM Gaussian post-filter**, on this system
model (2 mm SRM, AC, support 1000):

- numbers move by ≤ 0.015 over the last doubling (≤ 1.5 SD), recovery 1.002 ± 0.002, noise 0.10;
- report every contrast with its bootstrap SD, and drop or flag the 6.4 mm sphere;
- 3.3 min on the RTX 3080 Ti; the doubling check (4000 vs 8000) is part of the reference.

If the reference must be strictly converged, use 10 mm (every change < 1 SD) at a further loss of
contrast. For comparisons between methods (voxel size, scatter handling, priors) use the
contrast-vs-noise curves, not single points.

## Caveats

- The bootstrap SD is the noise of resampling the measured data; with 20 copies an SD is uncertain by
  about ±16 %. It is not checked against independent full-count acquisitions (none exist). The bootstrap
  is consistent, not unbiased: low-count pixels (467 at 0, 12,462 < 10 counts) cannot fluctuate in the
  copies, and per-voxel SDs at high unfiltered updates are past the linear regime. The copies' mean
  stays within 0.5 SD of the measured-data values for every insert. A validation against independent
  Poisson data is planned (NOTES.md, "Validate the bootstrap error bars").
- One subset count (8) and one subset ordering (`subsets/`: some subsets leave 150–160° of azimuth
  empty). OSEM's limit cycle at high update counts depends on both; at 8000 updates the result is not
  a maximum-likelihood image.
- Unscattered data: a best case. Scattered data (with the scatter model) will be noisier.
- The stability criterion in units of the SD is lenient for noisy inserts (their SD grows with
  updates); the table of absolute changes is the stricter view.

## Next

- Validate the bootstrap SDs against ~20 independent Poisson data sets around the forward-projected
  true phantom (deferred; plan in NOTES.md).

- The same analysis for the scatter tiers (`full_total` with the true scatter as `s`, then smoothed TEW).
- BSREM with a relative-difference prior: a converged image without a post-filter, compared on the
  same contrast-vs-noise axes.
- A subset ordering that minimises each subset's azimuth gap, compared with the current one at 8000 updates.
