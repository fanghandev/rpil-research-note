# Error budget of the unscattered reconstruction: study plan

2026-10-16. Status: **plan, nothing run yet; on hold until the gammart optimisation is done**
(step C′ and the SRM-noise steps added 2026-10-16). Question: in the reconstruction of the unscattered
simulated data (`in_fov_primary`, not forward-projected noise-free data), how much of the gap to the
truth comes from each factor: the system's intrinsic resolution (apertures, pixels, module placement;
crystal efficiency and readout taken as perfect, and identical in SRM and data), the reconstruction
algorithm, discretisation, counting noise and model mismatch?

Builds on `osem_reference.md` (OSEM 8 reference, bootstrap noise) and the earlier synthetic runs
(`dev/python/brain_phantom_recon/doc_2026-10-14/synthetic_*`, `convergence/synthetic_noisefree_*_2000it`,
made by `make_jaszczak_test_projections.py`).

## Factors

| # | factor | mechanism |
|---|---|---|
| 1 | 2 mm voxel grid | partial volume of small rods and sphere edges before any physics |
| 2 | system (intrinsic resolution, sampling) | aperture widths (0.556–2.007 mm), 2 mm pixels, minification b/f ≈ 2–9, 73-module layout; 45,625 measurements for 1.6 M unknowns (null space) |
| 3 | algorithm | finite updates, OSEM limit cycle, positivity, support mask, edge ringing; the ML solution itself is not the truth |
| 4 | discretisation mismatch | continuous phantom vs the 2 mm voxel basis of the model |
| 5 | counting noise | 80.4 M counts; noise forces early stopping or a post-filter, which costs resolution |
| 6a | remaining model mismatch | attenuation (gammart factors vs Gate transport), other physics differences between the SRM and phantom simulations |
| 6b | SRM noise | Poisson noise of the Gate Monte Carlo SRM itself (~11–16 % per element at 2 mm, memory: gammart-raytraced-srm); enters every step that reconstructs with a Gate SRM, including the inverse crime |

## Ladder (one factor added per step)

Common settings: OSEM 8 subsets, 2 mm Gate SRM, support 1000, gammart attenuation factors, uniform
start; saved at the reference study's 28 iterations (to 8000 updates); post-filters 0–10 mm in the
analysis.

| step | data | reconstruction | adds | status / cost |
|---|---|---|---|---|
| A | truth on the 2 mm grid (activity_volume; also the partial-volume version: fraction of each voxel inside the water, from a 0.25 mm sampling) | none | 1 | new; CPU, minutes |
| B | noise-free, H₂ · truth₂ (same SRM as the reconstruction: "inverse crime") | H₂, to 8000 updates; plus a long MLEM run for the converged limit | 2 + 3 | new; ~5 min GPU |
| C | noise-free, H₁ · truth₁ (1 mm SRM, finer object), scaled to 80.4 M counts | H₂ | 4 | exists for MLEM (`synthetic_noisefree_2mm`, `convergence/…_2000it`); redo with OSEM 8, ~5 min |
| C′ | as C | H₂′ = 2 mm model aggregated from the 1 mm attenuated SRM, H₂′(i, J) = Σ_{k ∈ J} H₁(i, k) A₁(m, k) (exact sensitivity weighting of the attenuation inside each 2 mm voxel) | splits 4 into its attenuation part (C → C′) and its activity-voxelisation part (what C′ leaves) | new; CPU to build H₂′ (check first that H₁ and H₂ come from the same Gate events), ~5 min GPU |
| D | 20 independent Poisson draws of C's expected counts at 80.4 M | H₂, each as in `osem_reference_runs.py` | 5 | new; ~70 min. Also the bootstrap validation (NOTES.md): bootstrap one draw and compare SDs with the spread over the 20 |
| E | Gate unscattered data (`in_fov_primary`) | H₂ | 6 | done (`osem_reference_2026-10-15/replicate_00`, bootstrap SDs) |

SRM-noise steps (factor 6b), with the deterministic gammart SRM (`gammart_srm.py --rule gauss`, no
sampling noise; same geometry, primary-only physics) as the noise-free reference system:

| step | data | reconstruction | adds | status / cost |
|---|---|---|---|---|
| B_g | noise-free, G₂ · truth₂ (G = gammart SRM) | G₂ (inverse crime without SRM noise) | B − B_g = 6b on the inverse crime | needs G₂ with attenuation; ~5 min GPU |
| X1 | noise-free, G₁ · truth₁ | H₂ (Gate) | Gate SRM noise and physics against a smooth "truth system" | ~5 min |
| X2 | noise-free, H₁ · truth₁ (= C's data) | G₂ | the reverse; X1 vs X2 separates SRM noise from the G–H physics difference | ~5 min |
| H̄ | as C | H₂ from more or fewer events (e.g. merged p01-10 vs a half: noise scales as 1/√events) | dose–response of 6b without gammart | optional |

Caveat: G and H differ in physics as well as noise. G is the first interaction in the crystal with no
energy window; H is singles in 126–154 keV after option4 transport (fluorescence on), per-pixel
readout and 14 keV FWHM blur. Measured 2026-10-16 for point sources: ~5.5 % in total and ~9 % per
pixel (pytorch-optix `docs/literature_review_2026-10.md` §3.1). X1/X2 mix the two until gammart has
the detector-response kernel; B_g alone is clean (data and model both G).

Differences between neighbouring steps are the factors' contributions. Note: the synthetic data (C, D)
use the same gammart attenuation factors as the reconstruction, so attenuation mismatch appears only in
E; the "continuous" object of C is the 1 mm voxelisation (activity_volume, nearest voxel), not a true
continuum.

Direct check of factor 6 without reconstruction: Gate data vs C's expected counts per pixel, as
(y − ȳ) / √ȳ; a χ² per degree of freedom above 1 is mismatch beyond Poisson noise (per module, per
radius; cf. the open item on the attenuation model, `ac_pixel_residuals.py`).

## Separating system (2) from algorithm (3)

- **Algorithm-free limit**: the Tikhonov point response R_α e_j = Hᵀ(HHᵀ + αI)⁻¹H e_j
  (`ideal_lir.py`, depends only on H) against the OSEM point response at the same positions and
  matched noise.
- **Convergence**: B at increasing updates, MLEM vs OSEM 8 vs (later) BSREM; what remains at
  convergence is the system's, what changes with the stopping point is the algorithm's.
- **System what-ifs** (second stage, after A–E): gammart ray-traced SRMs (`gammart_srm.py`, ~9 min
  per geometry) for step B with one system parameter changed at a time: all apertures 0.556 mm;
  ideal (point) aperture; 1 mm pixels; a different pinhole radius. Splits factor 2 into aperture vs
  pixel vs placement. Classic theory (`osem_reference_2026-10-15/resolution/resolution_theory.md`)
  predicts the 2 mm pixels dominate (≈ 11 mm back-projected at the centre vs ≈ 3.6 mm from the
  smallest aperture). Each what-if needs the gammart SRM validated against Gate for the reference
  geometry first (done for the current system, memory: gammart-raytraced-srm).

## Metrics (each step, against updates and at the reference setting: 8000 updates, 8 mm)

- Contrast of every insert and of every single rod (`osem_reference_analysis.py` definitions), recovery,
  rim/centre.
- Image error against the truth over the water and per region (rods, spheres, uniform section):
  NRMSE, split into bias² (from the noise-free steps and the mean over D) and variance (D, and the
  bootstrap for E).
- Resolution: point-response FWHM at a few positions (centre, r 30 / 50 / 65 mm, rod and sphere
  planes) by the perturbation method (reconstruct with and without a weak point source added to the
  noise-free data); a rod-sector fit (true layout blurred by a Gaussian, free σ and levels) as a
  secondary measure. Edge and rod fits are biased by the ringing (`osem_reference.md`, resolution
  discussion), so the point response is the primary resolution number.

## Caveats to state with the results

- The factors interact; steps do not add exactly, and the order matters. Report each step's change and
  the order used.
- B is an inverse crime (optimistic); C is the realistic noise-free reference.
- Gaussian-equivalent widths understate the true FWHM when the response rings.

## Deliverables

- Code (dev/python): `error_budget_runs.py` (steps B–D, reusing `make_jaszczak_test_projections.py`
  and the reference-run engine setup), `error_budget_analysis.py`.
- Outputs: `dev/python/brain_phantom_recon/error_budget_<date>/`.
- Report: `dev/reports/2026-10_phantom_recon/error_budget.md` (table of each factor's share for every
  insert, figures), pointer in NOTES.md.
