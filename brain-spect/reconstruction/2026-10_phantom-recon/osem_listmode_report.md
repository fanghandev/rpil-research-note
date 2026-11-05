# OSEM, list-mode MLEM and list-mode OSEM for the brain SPECT phantom reconstruction

2026-10-14, unattended session (brief: `osem_listmode_task.md`; context: `NOTES.md`, "Convergence").
Data: small Jaszczak, 15 mCi, 900 s (`full_small_jaszczak_15mCi_20261009T225845Z`). Unless stated otherwise:
2 mm Gate SRM, support = air-SRM sensitivity > 1000, attenuation corrected
(`small_jaszczak_2mm_factors_gammart.npy`), as in `doc_2026-10-14/run_all.sh`. Every number below is scored
with `make_jaszczak_doc_figures.run_metrics` (the write-up's definitions).

## Summary

- **Binned OSEM works and gives the expected speed-up.** An OSEM iteration over S module subsets costs
  the same as one MLEM iteration (0.196–0.201 s vs 0.197 s), and k OSEM iterations reproduce MLEM at
  k·S iterations closely: contrasts within ~0.01–0.02, accuracy and rim/centre close, the same images
  (figures below). OSEM 12 reaches the MLEM-400 state in 32 iterations (6.5 s instead of 79 s).
- **OSEM fixes the global scale much earlier.** Accuracy (mean/true in the uniform section) is 0.99–1.05
  after the first OSEM iteration, whereas MLEM needs ~400 iterations to reach 0.99; the activity outside
  the phantom drops to < 0.4 % after one OSEM iteration (MLEM: 5.5 % at 12 iterations). That is
  where most of OSEM's head start in likelihood comes from early on.
- **Where OSEM departs from MLEM (limit cycle / noise growth).** Past ~400 updates, OSEM's
  log-likelihood falls behind MLEM's at equal updates and the noise is higher: at 1200 updates CoV
  0.202 / 0.211 / 0.226 (S = 4 / 8 / 12) vs 0.190 for MLEM, likelihood 0.8 / 1.2 / 2.1 × 10³ below
  MLEM 1200, rim/centre lower for S = 12 (0.922 vs 0.940). The gap grows with S. It does not show
  below ~200 updates. On `full_tew` the same, larger (CoV 0.344 vs 0.289 at 1200 updates for S = 12).
- **List-mode MLEM = binned MLEM** (max relative difference 1.4 × 10⁻⁶ after one iteration, 9.8 × 10⁻⁵
  after 400; GPU run-to-run noise is of the same order), at 0.202 s per iteration.
- **List-mode OSEM gains nothing here.** With time-ordered (or random) event subsets each subset is a
  thinned copy of the whole acquisition, so an LM-OSEM sub-update is almost exactly an MLEM iteration
  (the tables agree with MLEM at equal updates to ~0.001), and each sub-update costs a full matrix pass
  (0.195 s), because 80 M events hit essentially every one of the 45,625 rows in every subset. Per
  wall-clock second LM-OSEM equals MLEM; binned OSEM is S times faster. Time vs random interleaving
  makes no difference (static phantom). List mode only pays when events are far fewer than bins or
  carry information the bins lose (sub-pixel position, depth of interaction, energy, timing).
- **Streaming engine (1.5 / 1 mm)**: OSEM done and validated too (S = 1 = MLEM to 2 × 10⁻⁶); OSEM 8 at
  1 mm reaches 400 updates in 52 s instead of ~7.4 min, same pattern as at 2 mm, except a higher
  outside share at 1 mm (0.43 vs 0.19 %).
- **Recommendation for the study**: binned OSEM with 8 subsets for exploration (400 updates in
  10 s, nearly MLEM-like); for final numbers either MLEM, or OSEM with ≤ 400 updates, or (next step)
  OSEM to convergence followed by a few MLEM iterations / a penalised method so the result does not
  depend on S and the stopping point.

## What was implemented

### Engine (`dev/python/compact_gpu_mlem.py`)

`CompactGpuMLEM` (the 2 mm engine, matrix resident on the GPU as int32 columns + float16 values):

- `rows_per_group` (driver: 625, one detector module): no row chunk spans two modules, so a module
  subset is a list of chunks, and the exact column sums of every module are computed on the CPU at
  construction (`group_sens`, float64 sums stored as float32; 73 × 3.0 M voxels, 0.9 GB host memory).
- `reconstruct_osem(iterations, subsets)`: per sub-update b, only the subset's rows are projected:

  ```
  λ_j ← λ_j / s_j^(b) · Σ_{i∈b} H_ij · y_i / (Σ_k H_ik λ_k + ε),   s_j^(b) = Σ_{i∈b} H_ij
  ```

  H is the attenuated SRM when AC is on (the module blocks are scaled before the engine is built, so
  `s^(b)` is attenuated too). Voxels outside the support (air SRM) or with `s^(b) = 0` are not updated.
- `reconstruct_listmode(iterations, event_rows, subsets, weights=None, order="time"|"random")`:
  events are int32 row indices (`head * 625 + pixel`) on the GPU, no row copies per event.
  Per sub-update: forward-project the rows of the modules the subset's events hit, gather each event's
  denominator by its row index, scatter `w_e / denominator` back onto the rows (float64 index_add),
  backproject:

  ```
  λ_j ← λ_j / (s_j / S) · Σ_{e∈b} w_e H_{r(e) j} / (Σ_k H_{r(e) k} λ_k + ε)
  ```

  S = 1 is list-mode MLEM with s_j the full sensitivity; S > 1 uses `s_j / S` per subset (Reader et
  al. 2002 convention; exact when every subset is a statistically equal share of the acquisition).
  Subsets: consecutive chunks of equal event count in time order (the standard), or the same cut of a
  random permutation (`order="random"`, seed 0). Unit weights unless given.
- `_run` records `wall_s` (seconds since the start, GPU synchronised) at every saved iteration.
- **Sensitivity fix.** `self.sens` was `csr.sum(axis=0)`, which for float32 data accumulates in
  float32 (checked: up to ~1 × 10⁻⁵ relative error on a test matrix), though the docstring says
  "exact". It is now a float64 `np.bincount` over 100 M-non-zero slices. Effect on MLEM (old vs new,
  `in_fov_primary`): max relative voxel difference 7.7 × 10⁻⁶ at iteration 1, 7.4 × 10⁻⁴ at 100,
  4.4 × 10⁻³ at 400 (99th percentile 1.4 × 10⁻³): invisible in the metrics, but the existing runs in
  `doc_2026-10-14/*` were made with the old sensitivity and were not redone. The support mask is
  computed by the driver (`system_matrix.sum(axis=0) > 1000`) and did not change.

`StreamingCompactMLEM` (1.5 / 1 mm, stretch goal): `keep_block_sensitivity=True` keeps each module
block's column sums on the host (float32; 2 GB at 1.5 mm, 7 GB at 1 mm) and `reconstruct_osem` runs
the streaming pass over only the subset's blocks (resident ones first, streamed ones double-buffered,
as before) with the subset's sensitivity (pinned host memory, copied into one GPU buffer per
sub-update). MLEM through this engine is unchanged; it now also records `wall_s`.

### Balanced module subsets (`module_subsets` in `recon_brain_phantom_projections.py`)

The 73 modules sit in 7 rings (10 / 13 / 18 / 15 / 11 / 5 / 1 modules, −37° to 90° elevation;
`geometry_provenance.json` of `brain_288mm_csg_102t_20261005T211647Z_01`). Modules are ordered ring by
ring (bottom to top) and by azimuth within a ring, then dealt round-robin with one counter over all
rings: subset k gets positions k, k + S, k + 2S, … So every subset has every S-th module of each ring
(all elevations, spread over azimuth) and the sizes differ by at most one: S = 4 → 19/18/18/18,
S = 8 → 10/9/…, S = 12 → 7/6/…/6. With S = 12 the 5-module ring and the top module cannot be in every
subset. Subsets are visited in order 0, 1, …, S − 1 every iteration. (73 is prime, so no S divides it
evenly; 4, 8, 12 were used as in the brief.) The lists are saved in each output (`subset_modules`) and
printed in the logs, e.g. S = 4:
`[2, 6, 8, 13, 17, 22, 23, 27, 31, 35, 37, 44, 48, 55, 57, 61, 64, 71, 72], [3, 7, 9, 10, 14, …], …`

### List-mode events (`dev/python/phantom_listmode_events.py`)

The merge (`payload/python/merge_phantom_listmode.py`) draws random numbers (decay thinning with
seed + 1, energy blur with seed), so the binned events can only be reproduced by replaying the jobs in
the merge's order with the same generators. `extract()` takes the job order (the 1,800 `job_list`
entries of the merged meta; 80 more job directories in `jobs/` are resubmission leftovers the merge did
not use), seed, FWHM, FOV radius and decay rule from the merged meta, checks each job's singles count,
seed and keep probability against it, and keeps the main-window events (126.46–154.56 keV after blur)
as `row` (int32), `time_s` (absolute, float32; the job files already store absolute times), `primary`
(no phantom scatter), `in_fov` (decay inside the 144 mm sphere), sorted by time (stable). 103.8 M
events, cached as `dev/python/brain_phantom_recon/listmode/<campaign>_main_window_events.npz` (1.0 GB,
gitignored; extraction 20 s). Data sets: `in_fov_primary` = in_fov & primary, `in_fov_total` = in_fov,
`full_total` = all. `full_tew` has no list-mode form (a subtraction of binned windows).

### Driver (`dev/python/recon_brain_phantom_projections.py`)

`--algorithm {mlem,osem,lm-mlem,lm-osem}` (default `mlem`, unchanged chunking), `--subsets N`,
`--listmode-dir` (default `<campaign>/jobs`), `--lm-subset-order {time,random}`, `--geometry`
(rings for the subsets). `osem` works with both engines. List mode is compact-engine only and refuses
`full_tew` (said in `--help`);
it runs the histogram check before reconstructing and stops if any pixel differs. `--iterations` counts
full passes over all subsets. Outputs keep the npz format and add `algorithm`, `subsets`, `updates`
(iterations × subsets), `wall_s`, `subset_modules`, `lm_subset_order`.

### Tests (`dev/python/test_recon_algorithms.py`, CPU torch, 9 tests, all pass)

Tiny random integer matrix (6 groups × 5 rows × 40 voxels), dense numpy references: chunks respect
groups; OSEM with one subset = MLEM; subset sensitivities sum to the sensitivity; OSEM = reference
OSEM; list-mode MLEM on expanded counts (any order) = binned MLEM; LM-OSEM = a literal per-event
reference; weighted events and random order; the support mask; `module_subsets` balance and coverage.

## Validation

All in `doc_2026-10-14/algorithms/validation.json` (`compare_estimates.py`; relative difference over
voxels above 10⁻³ of the maximum).

| check | iteration 1 | 5 | 20 | 100 | 400 |
|---|---|---|---|---|---|
| histogram of selected events vs binned (`in_fov_primary`, `in_fov_total`, `full_total`) | identical: 80,402,994 / 103,811,936 / 103,811,936 counts, 0 pixels differ | | | | |
| OSEM S = 1 vs MLEM (same engine version), max rel. | 1.5 × 10⁻⁶ | 2.9 × 10⁻⁶ | 7.0 × 10⁻⁶ | 2.9 × 10⁻⁵ | – |
| LM-MLEM vs binned MLEM (`in_fov_primary`, AC), max rel. | 1.4 × 10⁻⁶ | 2.9 × 10⁻⁶ | 5.2 × 10⁻⁶ | 2.2 × 10⁻⁵ | 9.8 × 10⁻⁵ |
| MLEM vs a second MLEM run (GPU atomics), max rel. | 1.0 × 10⁻⁶ | 1.8 × 10⁻⁶ | 3.0 × 10⁻⁶ | 6.2 × 10⁻⁶ | 1.8 × 10⁻⁵ |
| streaming OSEM S = 1 vs existing streaming MLEM, 1.5 mm | 1.1 × 10⁻⁶ | 2.3 × 10⁻⁶ | 4.9 × 10⁻⁶ | – | – |
| streaming OSEM S = 1 vs existing streaming MLEM, 1 mm | 1.8 × 10⁻⁶ | 3.2 × 10⁻⁶ | 7.9 × 10⁻⁶ | – | – |
| new MLEM (exact sensitivity) vs existing `2mm_step3_ac` | 7.7 × 10⁻⁶ | 3.8 × 10⁻⁵ | 1.5 × 10⁻⁴ | 7.4 × 10⁻⁴ | 4.4 × 10⁻³ |

The first OSEM S = 1 attempt computed the subset sensitivity on the GPU from the float16 values and
differed from MLEM by 3 × 10⁻⁴ per iteration; the second still differed by 8 × 10⁻⁶ per iteration
because MLEM's own sensitivity was float32-accumulated (see the fix above). Both runs are kept as
`algorithms/osem_s1_*_superseded`. The table compares like with like.

## Results (`in_fov_primary`, the unscattered data)

Runs: `doc_2026-10-14/algorithms/<run>/` (`run_algorithms.py`), metrics `algorithms/metrics.json`
(`algorithm_metrics.py`, `run_metrics` layout), timings `algorithms/timing.json`, Poisson
log-likelihood of every saved estimate `algorithms/likelihood.json` (`algorithm_likelihood.py`),
all tables `algorithms/tables.md` and figures `algorithms/figures/` (`algorithm_tables.py`). The MLEM
reference (`algorithms/mlem`) runs to 1600 iterations and saves every update count the OSEM runs
save. ΔlogL: log-likelihood minus MLEM at 1600 iterations, in thousands.

### Against MLEM at 400 iterations

| algorithm | iter | updates | wall s | matched by | rod 7.9 | rod 6.4 | rod 4.8 | sph 25.4 | sph 12.7 | sph 9.5 | accuracy | rim/centre | CoV vox | outside % | ΔlogL (10³) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MLEM | 400 | 400 | 79.2 | reference | 0.449 | 0.269 | 0.143 | 0.811 | 0.581 | 0.388 | 0.994 | 0.953 | 0.104 | 0.15 | −4.9 |
| OSEM 4 | 100 | 400 | 19.8 | updates | 0.447 | 0.266 | 0.144 | 0.806 | 0.572 | 0.386 | 1.006 | 0.938 | 0.108 | 0.09 | −4.2 |
| OSEM 8 | 50 | 400 | 10.1 | updates | 0.464 | 0.264 | 0.146 | 0.807 | 0.569 | 0.372 | 1.005 | 0.947 | 0.112 | 0.11 | −4.7 |
| OSEM 12 | 32 | 384 | 6.5 | updates | 0.455 | 0.281 | 0.145 | 0.809 | 0.568 | 0.395 | 1.005 | 0.937 | 0.114 | 0.12 | −5.7 |
| MLEM | 384 | 384 | 76.0 | (for OSEM 12) | 0.445 | 0.265 | 0.142 | 0.809 | 0.579 | 0.386 | 0.993 | 0.953 | 0.102 | 0.16 | −5.2 |
| OSEM 4 | 400 | 1600 | 78.6 | wall time | 0.583 | 0.398 | 0.187 | 0.835 | 0.615 | 0.465 | 1.005 | 0.929 | 0.242 | 0.14 | −0.8 |
| OSEM 8 | 200 | 1600 | 39.7 | wall time (max run) | 0.597 | 0.397 | 0.187 | 0.834 | 0.613 | 0.455 | 1.003 | 0.937 | 0.254 | 0.16 | −1.2 |
| OSEM 12 | 100 | 1200 | 20.1 | wall time (max run) | 0.569 | 0.392 | 0.187 | 0.834 | 0.602 | 0.445 | 1.003 | 0.922 | 0.226 | 0.17 | −2.9 |
| LM-MLEM | 400 | 400 | 80.9 | updates | 0.449 | 0.269 | 0.143 | 0.811 | 0.581 | 0.388 | 0.994 | 0.953 | 0.104 | 0.15 | −4.9 |
| LM-OSEM 4 (time) | 100 | 400 | 78.7 | updates ≈ wall time | 0.449 | 0.268 | 0.143 | 0.810 | 0.580 | 0.388 | 0.994 | 0.952 | 0.104 | 0.15 | −5.0 |
| LM-OSEM 8 (time) | 50 | 400 | 78.3 | updates ≈ wall time | 0.449 | 0.268 | 0.143 | 0.810 | 0.580 | 0.388 | 0.994 | 0.952 | 0.104 | 0.15 | −5.1 |
| LM-OSEM 12 (time) | 32 | 384 | 75.0 | updates ≈ wall time | 0.445 | 0.264 | 0.142 | 0.809 | 0.577 | 0.387 | 0.993 | 0.953 | 0.102 | 0.15 | −5.5 |
| LM-OSEM 12 (random) | 32 | 384 | 75.0 | updates ≈ wall time | 0.445 | 0.265 | 0.142 | 0.810 | 0.579 | 0.386 | 0.993 | 0.956 | 0.102 | 0.15 | −5.5 |

"wall time": the saved iteration closest to MLEM-400's 79 s; OSEM 8 and 12 runs stop earlier (200 and
100 iterations), so their last iteration is shown. At equal wall time OSEM is simply further along the
same path: OSEM 4 at 79 s ≈ MLEM 1600 (rod 7.9 0.583 vs 0.580, CoV 0.242 vs 0.226).

### Equal updates (selection; all levels in `tables.md`)

| algorithm | updates | wall s | rod 7.9 | rod 6.4 | rod 4.8 | sph 25.4 | sph 12.7 | sph 9.5 | accuracy | rim/centre | CoV vox | outside % | ΔlogL (10³) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MLEM | 48 | 9.7 | 0.225 | 0.137 | 0.077 | 0.636 | 0.387 | 0.258 | 0.908 | 0.888 | 0.032 | 1.22 | −100.5 |
| OSEM 4 | 48 | 2.5 | 0.213 | 0.134 | 0.074 | 0.629 | 0.370 | 0.242 | 0.999 | 0.847 | 0.033 | 0.05 | −26.4 |
| OSEM 8 | 48 | 1.3 | 0.219 | 0.134 | 0.075 | 0.636 | 0.383 | 0.243 | 0.997 | 0.867 | 0.036 | 0.06 | −23.9 |
| OSEM 12 | 48 | 0.9 | 0.227 | 0.144 | 0.076 | 0.641 | 0.376 | 0.257 | 0.996 | 0.869 | 0.036 | 0.06 | −25.6 |
| LM-OSEM 12 (time) | 48 | 9.5 | 0.226 | 0.136 | 0.077 | 0.636 | 0.386 | 0.259 | 0.908 | 0.887 | 0.032 | 1.22 | −100.4 |
| MLEM | 192 | 38.1 | 0.369 | 0.212 | 0.124 | 0.780 | 0.542 | 0.361 | 0.977 | 0.953 | 0.070 | 0.26 | −12.0 |
| OSEM 4 | 192 | 9.6 | 0.364 | 0.209 | 0.122 | 0.773 | 0.528 | 0.349 | 1.005 | 0.926 | 0.072 | 0.05 | −7.0 |
| OSEM 8 | 192 | 4.9 | 0.378 | 0.207 | 0.124 | 0.775 | 0.526 | 0.335 | 1.004 | 0.937 | 0.075 | 0.06 | −7.2 |
| OSEM 12 | 192 | 3.4 | 0.379 | 0.225 | 0.123 | 0.778 | 0.527 | 0.363 | 1.004 | 0.933 | 0.076 | 0.07 | −8.0 |
| LM-OSEM 12 (time) | 192 | 37.6 | 0.370 | 0.211 | 0.124 | 0.780 | 0.540 | 0.362 | 0.977 | 0.953 | 0.070 | 0.26 | −12.2 |
| MLEM | 800 | 158.1 | 0.520 | 0.332 | 0.161 | 0.826 | 0.603 | 0.423 | 1.000 | 0.947 | 0.150 | 0.13 | −2.0 |
| OSEM 4 | 800 | 39.4 | 0.520 | 0.330 | 0.164 | 0.825 | 0.597 | 0.424 | 1.006 | 0.938 | 0.158 | 0.12 | −2.5 |
| OSEM 8 | 800 | 19.9 | 0.536 | 0.329 | 0.166 | 0.824 | 0.594 | 0.413 | 1.004 | 0.946 | 0.165 | 0.13 | −3.0 |
| OSEM 12 | 768 | 12.9 | 0.528 | 0.347 | 0.169 | 0.827 | 0.591 | 0.425 | 1.004 | 0.931 | 0.171 | 0.16 | −4.1 |
| MLEM | 768 | 151.7 | 0.516 | 0.328 | 0.160 | 0.825 | 0.602 | 0.421 | 1.000 | 0.947 | 0.147 | 0.13 | −2.2 |
| MLEM | 1200 | 236.9 | 0.557 | 0.371 | 0.173 | 0.832 | 0.612 | 0.445 | 1.002 | 0.940 | 0.190 | 0.12 | −0.8 |
| OSEM 4 | 1200 | 59.0 | 0.559 | 0.370 | 0.178 | 0.831 | 0.608 | 0.448 | 1.005 | 0.934 | 0.202 | 0.13 | −1.6 |
| OSEM 8 | 1200 | 29.8 | 0.573 | 0.369 | 0.178 | 0.830 | 0.605 | 0.438 | 1.004 | 0.941 | 0.211 | 0.15 | −2.0 |
| OSEM 12 | 1200 | 20.1 | 0.569 | 0.392 | 0.187 | 0.834 | 0.602 | 0.445 | 1.003 | 0.922 | 0.226 | 0.17 | −2.9 |
| LM-OSEM 12 (time) | 1200 | 234.0 | 0.557 | 0.370 | 0.173 | 0.831 | 0.611 | 0.446 | 1.002 | 0.940 | 0.190 | 0.12 | −1.0 |

### First 5 iterations (the usual clinical OSEM regime)

| algorithm | iter | updates | rod 7.9 | rod 4.8 | sph 25.4 | sph 12.7 | sph 9.5 | accuracy | rim/centre | CoV vox | outside % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OSEM 12 | 1 | 12 | 0.100 | 0.017 | 0.386 | 0.164 | 0.090 | 0.998 | 0.733 | 0.027 | 0.38 |
| MLEM | 12 | 12 | 0.098 | 0.013 | 0.361 | 0.159 | 0.083 | 0.819 | 0.722 | 0.018 | 5.50 |
| OSEM 12 | 3 | 36 | 0.199 | 0.065 | 0.595 | 0.333 | 0.224 | 0.994 | 0.842 | 0.032 | 0.09 |
| MLEM | 36 | 36 | 0.198 | 0.065 | 0.587 | 0.341 | 0.222 | 0.890 | 0.862 | 0.029 | 1.71 |
| OSEM 12 | 5 | 60 | 0.250 | 0.084 | 0.672 | 0.406 | 0.280 | 0.997 | 0.887 | 0.040 | 0.05 |
| MLEM | 60 | 60 | 0.247 | 0.086 | 0.670 | 0.421 | 0.284 | 0.922 | 0.906 | 0.036 | 0.94 |

Five OSEM-12 iterations (1.2 s) give contrasts a long way from MLEM-400 (rod 7.9 0.25 vs 0.45, sphere
12.7 0.41 vs 0.58): with this system and this phantom, "a few OSEM iterations" is under-converged;
the 400-update level needs ~32 OSEM-12 iterations.

### `full_tew` (TEW-subtracted, binned only)

| algorithm | updates | wall s | rod 7.9 | rod 6.4 | rod 4.8 | sph 25.4 | sph 12.7 | sph 9.5 | accuracy | rim/centre | CoV vox | outside % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MLEM | 400 | 79.1 | 0.433 | 0.254 | 0.160 | 0.814 | 0.585 | 0.331 | 1.007 | 0.923 | 0.149 | 0.17 |
| OSEM 4 | 400 | 19.7 | 0.433 | 0.254 | 0.162 | 0.810 | 0.584 | 0.332 | 1.020 | 0.908 | 0.155 | 0.00 |
| OSEM 8 | 400 | 10.0 | 0.447 | 0.249 | 0.160 | 0.810 | 0.582 | 0.334 | 1.018 | 0.916 | 0.160 | 0.01 |
| OSEM 12 | 384 | 6.4 | 0.440 | 0.268 | 0.162 | 0.814 | 0.583 | 0.340 | 1.012 | 0.918 | 0.160 | 0.02 |
| MLEM | 1200 | 236.9 | 0.541 | 0.348 | 0.207 | 0.839 | 0.613 | 0.382 | 1.009 | 0.917 | 0.289 | 0.20 |
| OSEM 4 | 1200 | 58.8 | 0.543 | 0.354 | 0.213 | 0.836 | 0.617 | 0.395 | 1.017 | 0.907 | 0.312 | 0.02 |
| OSEM 8 | 1200 | 29.7 | 0.554 | 0.344 | 0.208 | 0.834 | 0.620 | 0.415 | 1.015 | 0.908 | 0.324 | 0.02 |
| OSEM 12 | 1200 | 20.0 | 0.552 | 0.371 | 0.218 | 0.841 | 0.614 | 0.410 | 1.008 | 0.913 | 0.344 | 0.03 |

Same picture as for the unscattered data; OSEM's accuracy sits 1–2 % higher than MLEM's (1.012–1.020
vs 1.007 at 400 updates) and its outside share is ~0, while MLEM keeps 0.2 % outside. The
log-likelihood for `full_tew` (in `likelihood.json`) is computed with the subtracted, clipped data,
which are not Poisson, so it is only a relative convergence indicator there.

### Streaming engine, 1.5 and 1 mm SRMs (stretch goal)

OSEM 8 (`osem_s8_1p5mm`, `osem_s8_1mm`; support 421.875 / 125, the 1.5 / 1 mm attenuation factors, as
in `run_all.sh`) against the existing MLEM runs `1p5mm_step3_ac` / `1mm_step3_ac` at 400 iterations
(those have no wall times; MLEM speed from the S = 1 validation runs: 0.444 and 1.105 s per iteration).

| run | data set | iter | updates | wall s | rod 7.9 | rod 6.4 | rod 4.8 | sph 25.4 | sph 12.7 | sph 9.5 | accuracy | rim/centre | CoV vox | outside % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OSEM 8, 1.5 mm | in_fov_primary | 50 | 400 | 19.7 | 0.461 | 0.256 | 0.139 | 0.803 | 0.559 | 0.375 | 1.006 | 0.948 | 0.124 | 0.25 |
| MLEM, 1.5 mm | in_fov_primary | 400 | 400 | ~178 | 0.447 | 0.261 | 0.137 | 0.805 | 0.572 | 0.391 | 0.994 | 0.955 | 0.114 | 0.17 |
| OSEM 8, 1.5 mm | full_tew | 50 | 400 | 19.5 | 0.445 | 0.246 | 0.153 | 0.807 | 0.574 | 0.337 | 1.019 | 0.918 | 0.184 | 0.06 |
| MLEM, 1.5 mm | full_tew | 400 | 400 | ~178 | 0.432 | 0.251 | 0.153 | 0.810 | 0.578 | 0.337 | 1.007 | 0.928 | 0.167 | 0.17 |
| OSEM 8, 1 mm | in_fov_primary | 50 | 400 | 51.7 | 0.462 | 0.262 | 0.148 | 0.798 | 0.558 | 0.369 | 1.005 | 0.945 | 0.162 | 0.43 |
| MLEM, 1 mm | in_fov_primary | 400 | 400 | ~442 | 0.448 | 0.266 | 0.145 | 0.795 | 0.571 | 0.386 | 0.993 | 0.946 | 0.149 | 0.19 |
| OSEM 8, 1 mm | full_tew | 50 | 400 | 51.6 | 0.448 | 0.249 | 0.163 | 0.801 | 0.571 | 0.324 | 1.017 | 0.913 | 0.256 | 0.32 |
| MLEM, 1 mm | full_tew | 400 | 400 | ~442 | 0.434 | 0.254 | 0.161 | 0.802 | 0.577 | 0.331 | 1.005 | 0.919 | 0.224 | 0.22 |

The same pattern as at 2 mm (rod 7.9 +0.013 to +0.014, sphere 12.7 −0.004 to −0.013, CoV +9–14 %), at
about 1/8 of the time per update (OSEM 8: 0.39 s and 1.03 s per iteration). One difference: at 1 mm the
outside share is *higher* with OSEM (0.43 % vs 0.19 % for `in_fov_primary`, 0.32 vs 0.22 % for
`full_tew`), the only place where OSEM puts more activity outside the phantom than MLEM. A plausible
cause (not checked) is large per-subset steps in low-sensitivity voxels of the wider 1 mm support
(threshold 125); look at a MIP before using OSEM at 1 mm. The first 1 mm OSEM-8 run ran out of GPU memory (8 subset sensitivities of 96 MB each next
to 7 GiB of resident blocks); they now stay in pinned host memory and are copied into one GPU
buffer per sub-update (the failed run is kept as `osem_s8_1mm_oom_superseded`).

### Timing (RTX 3080 Ti, 2 mm, 1.43 × 10⁹ non-zeros on the GPU)

| algorithm | s / iteration | s / update | note |
|---|---|---|---|
| MLEM | 0.197 | 0.197 | |
| OSEM 4 / 8 / 12 | 0.196 / 0.198 / 0.201 | 0.049 / 0.025 / 0.017 | each module once per iteration; per-subset overhead negligible |
| LM-MLEM | 0.202 | 0.202 | + 0.3 GB event rows on the GPU, gather / scatter of 80 M events |
| LM-OSEM 4 / 8 / 12 | 0.786 / 1.563 / 2.340 | 0.195 | every subset touches all 73 modules: one full pass per update |
| MLEM / OSEM 8, 1.5 mm (streaming) | 0.444 / 0.391 | 0.444 / 0.049 | |
| MLEM / OSEM 8, 1 mm (streaming) | 1.105 / 1.033 | 1.105 / 0.129 | |

Setup per run (SRM load, attenuation, upload, exact sensitivities, saving): about 40–55 s from the
logs, the same for list-mode runs (event cache load and histogram check included).

## Figures (`doc_2026-10-14/algorithms/figures/`)

- `osem_in_fov_primary.png`, `osem_full_tew.png`: contrast (rod 7.9 / 4.8, sphere 12.7), CoV,
  accuracy and log-likelihood against updates, MLEM vs OSEM 4 / 8 / 12. The OSEM curves lie on MLEM's
  except accuracy (OSEM at 1 from the start) and, past ~400 updates, CoV (higher) and log-likelihood
  (lower, flattening: the limit cycle).
- `wall_time_in_fov_primary.png`: the same against wall time, with LM-OSEM (on top of MLEM).
- `lmosem_in_fov_primary.png`, `osem_vs_lmosem.png`: LM-OSEM (time / random) against MLEM and OSEM.
- `rods_equal_updates.png`, `spheres_equal_updates.png`: rod / sphere planes of MLEM, OSEM 12 and
  LM-OSEM 12 at 12–768 updates (each panel scaled to its water level). No subset artifacts are
  visible; OSEM 12 at 768 updates is slightly noisier than MLEM.

## Caveats

- One noise realisation; differences of ~0.01 in contrast between algorithms at equal updates are
  below the statistical SE established with the 4 sub-acquisitions for some inserts (NOTES.md:
  ±0.003–0.07) and should not be over-read. The CoV / likelihood trends are systematic (monotone in S).
- OSEM's per-subset sensitivity uses the module rows of the subset; with S = 12 a subset holds
  6–7 modules and some voxels near the FOV edge may have small subset sensitivity (largest
  per-update steps there). Not seen in the images or outside share at 2 mm with support 1000.
- The `s / S` LM-OSEM sensitivity is approximate (exact in expectation); with 6.7 M events per subset
  it is exact to well below the noise.
- The list-mode path needs the per-job files and the merge's RNG order; a merged list-mode file
  (`merge_phantom_listmode.py --listmode`) was not written for this campaign.
- Existing runs under `doc_2026-10-14/` (other than `algorithms/`) use the old float32-accumulated
  sensitivity (≤ 0.44 % voxel difference at 400 iterations); not redone.
- The scatter model `y ~ Hλ + s` decided in NOTES.md is still not implemented in the engines; OSEM
  and LM would take the additive term in the same way (the denominator), list mode per event.

## Files and how to reproduce

Code: `dev/python/compact_gpu_mlem.py`, `recon_brain_phantom_projections.py`, `phantom_listmode_events.py`,
`test_recon_algorithms.py` (`python -m pytest test_recon_algorithms.py -q` from `dev/python`).
Runs, from `dev/python` (all under `brain_phantom_recon/doc_2026-10-14/algorithms/`):

```
python phantom_listmode_events.py --projections <campaign>/merged/projections.npz \
    --report brain_phantom_recon/doc_2026-10-14/algorithms/histogram_check.json   # events + check
python brain_phantom_recon/doc_2026-10-14/algorithms/run_algorithms.py           # all runs, skips existing
python brain_phantom_recon/doc_2026-10-14/algorithms/algorithm_metrics.py        # metrics.json, timing.json
python brain_phantom_recon/doc_2026-10-14/algorithms/algorithm_likelihood.py     # likelihood.json (GPU, 2 mm)
python brain_phantom_recon/doc_2026-10-14/algorithms/algorithm_tables.py         # tables.md, figures/
python brain_phantom_recon/doc_2026-10-14/algorithms/compare_estimates.py A.npz B.npz --json validation.json --key K
```

(`run_algorithms.sh` wraps `run_algorithms.py`.) Logs in `algorithms/logs/`. Directories named
`*_superseded` are kept failed or replaced attempts (GPU float16 subset sensitivity, float32 MLEM
sensitivity, a run cut off by a tool time limit, the 1 mm OOM); `algorithm_metrics.py` skips them.
`explore_listmode.py` is the scratch script used to inspect the job files. No existing run or
`doc_2026-10-14/metrics.json` was modified.

## Next steps

1. Use binned OSEM (S = 8) for routine exploration; report final numbers at a fixed number of updates
   (e.g. 400), or OSEM-then-MLEM (e.g. 50 OSEM-8 iterations + a few MLEM) to leave the limit cycle.
2. Penalised likelihood (e.g. a relative-difference prior, OSL / BSREM with the same module subsets)
   so numbers stop depending on the stopping iteration; BSREM converges, unlike OSEM.
3. Additive scatter term (`Hλ + s`, smoothed TEW) in all engines; then OSEM on `full_total` with
   the scatter model vs `full_tew`.
4. List mode only if the model gains per-event information (sub-pixel position or depth via a finer
   SRM, energy-dependent rows); otherwise drop it for this system.
