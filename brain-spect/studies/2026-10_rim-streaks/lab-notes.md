# Streak artifacts at the FOV rim: truncation or angular sampling?

> Moved here from qmirt-gate-10-sim `dev/python/streak_sampling_study.md` on 2026-10-08.
> Paths in these notes (scripts, `acr_fit/`, `extent_series/`, `report/…`) are relative to
> qmirt-gate-10-sim `dev/python/`; the reports now live in `report/` and
> `earlier-writeups/` next to this file.

Status: planned, 2026-10-05. Background: `report/streak_artifacts_report.pdf` (working
notes, 2026-10-01) and `report/srm_recon_report.pdf`.

## Question

MLEM reconstructions of the hot-background ACR Jaszczak phantom on the 73-module brain
system (`brain_merged_123`, 210³ grid of 1 mm voxels, FOV sphere of radius 105 mm) show
radial streaks near the FOV edge. They grow with iteration count. Two explanations:

1. **Truncation.** The modelled FOV is too small, so a larger one (288 mm diameter
   instead of 210 mm) is needed.
2. **Angular sampling.** Voxels near the rim are seen by fewer modules, from a narrow
   range of directions (N_eff ≈ 44 modules at the centre and ≈ 18 at r = 90–105 mm,
   with a 5th percentile of about 10). MLEM then leaves errors free to spread along
   the poorly sampled direction.

## What the existing data already say

- **Truncation in its usual sense is excluded by construction.** The projections are
  noiseless and are computed with the same H as is used for reconstruction (y = Hf).
  Activity outside 105 mm never enters the data, so every count is explained by the
  model.
- **The streaks are a property of H.** The local impulse response (`report/figs/lir_acr.png`)
  of a point at r = 0 already has radial streaks across the slice at iteration 200.
  At r = 60–95 mm it becomes anisotropic.
- **Two forms of hypothesis 1 remain open:**
  - **1b: hot edge at the model boundary.** The ACR hot background reaches the 105 mm
    support, where some voxels have a sensitivity of 1 count. Such an edge could seed
    streaks without any data inconsistency.
  - **Real-patient truncation.** A real head and neck put activity outside the modelled
    sphere. This is a reason to build the 288 mm SRM, but it is a separate problem from
    the streaks seen here.
- **A larger FOV would not fix the sampling.** All 73 modules see only a sphere of
  about 212 mm diameter, and fewer than 48 modules see beyond 228 mm
  (`brain_fov_analysis/brain_fov_summary.json`). A 288 mm SRM would move the poorly
  sampled shell outward rather than remove it.

## Experiments

All experiments use the existing `brain_merged_123` SRM at 1 mm, noiseless forward
projections, and MLEM from a uniform start. Estimates are saved at iterations
10, 20, 50, 100 and 200. No new Gate simulation is needed.

### E1: separate the two kinds of truncation

| Run | Phantom | Reconstruction support | What it tests |
|---|---|---|---|
| E1a | Full ACR, projected with H | r ≤ 80 mm (and r ≤ 90 mm) | Real truncation: the activity in the 80–105 mm shell is outside the model |
| E1b | ACR cropped to r ≤ 80 mm | Full FOV (r ≤ 105 mm) | No activity at the model boundary |

- If E1b still has streaks at r = 60–80 mm, a boundary edge is not needed to produce them.
- If the E1a artifact (for example a hot rim or a global bias) looks different from the
  observed streaks, that weakens hypothesis 1 further.
- Needs a support-radius option in `fp_jaszczak_and_recon.py`.

### E2: rim-shift test with a small cold-sphere phantom (core experiment)

- **Phantom.** A small spherical phantom with a hot background, containing cold spheres
  whose sizes follow the small Jaszczak phantom. It always lies entirely inside
  r ≤ 100 mm, at least 5 mm clear of the low-sensitivity boundary voxels. See
  "Phantom design" below.
- **Positions:**
  - **P0:** centred. This is the reference.
  - **P1:** half-way to the rim.
  - **P2 and P3:** as far out as the 100 mm limit allows. P2 is in the direction with the
    **lowest** N_eff and P3 in the direction with the **highest**, at the same radius.
  - **P4:** at the same radius, displaced axially (+z or −z). The ring layout is not
    symmetric in elevation.
- **The discriminating comparison is P2 against P3.** Both sit at the same distance from
  the boundary.
  - Boundary or truncation predicts that P2 and P3 look the same.
  - Sampling predicts that P2 is clearly worse than P3, with streaks aligned to the
    dominant viewing direction.
- **Choosing the directions.** P2 and P3 come from a 3-D N_eff map computed from the
  per-module sensitivities. The report computed N_eff for slice z index 130 only.

### E3: Monte Carlo noise in H

- Repeat P2 with an SRM built from a single campaign instead of the merged 1+2+3.
- Edge columns of H have fewer counts, so noise in H also gets worse toward the rim.
- If the streak amplitude grows clearly as the statistics drop, noise in H is
  contributing.

### E4: clinical relevance (optional)

- Repeat P0 and P2 with Poisson noise at a realistic count level, stopping at about
  iteration 20–50.
- This checks whether the streaks matter at clinical iteration counts.

## Metrics

- **Shifted-reference difference.** The same discretised object is imaged at every
  position, because each position is P0 shifted by whole voxels. Each reconstruction
  can therefore be compared voxel by voxel with the P0 reconstruction shifted to the
  same place. The difference isolates the effect of position, so the Gaussian-blur
  reference is no longer needed.
- **Background CoV** inside the phantom, excluding each cold sphere plus a margin.
- **Contrast recovery** for each cold sphere.
- **Streak index:** radial-versus-tangential angular power of the error in rings around
  each sphere, and the orientation of the strongest component.
- **Per-sphere data points.** Each sphere at each position is one point of
  (position, N_eff, direction tensor, artifact). Comparing these points with the
  sampling metric is the step towards a predictive metric (step 2 of the streak report).

## Decision rules

- **Sampling confirmed:** E1b and P2 have streaks, P2 is worse than P3, the streaks align
  with the viewing direction, and E3 shows little change. Next: build the directional
  metric and use it for design work (steps 2, 4 and 5 of the streak report).
- **Boundary effect:** the streaks disappear in E1b and in all of E2. Next: restrict the
  reconstruction support or floor the small sensitivities (`sens_safe`).
- **Real truncation:** E1a reproduces the observed streak pattern. Then the 288 mm SRM is
  also needed for the streaks, not only for clinical data.

## Phantom design (decided 2026-10-05)

- **Shape.** A hot sphere (activity 1) of radius 32 mm. Its centre radius is limited to
  r_c ≤ 68 mm, so that every voxel centre lies within r ≤ 100 mm.
- **Cold spheres.** Activity 0. These are the four smallest sizes of the small Jaszczak
  phantom, on a 16 mm radius ring in the transverse plane through the phantom centre:
  15.9 mm on +x, 6.4 on +y, 12.7 on −x and 9.5 on −y. The two larger small-Jaszczak
  spheres (19.1 and 25.4 mm) were left out. With them the phantom grows to about
  106 mm diameter, and even when moved as far as possible it still covers half the FOV.
- **Spacing.** At least 9.9 mm of hot background between neighbouring spheres, and 8 mm
  between the 15.9 mm sphere and the phantom surface. The fitted reconstruction FWHM is
  about 10 mm at iteration 100.
- **Shifted, never rotated.** The centre is a whole number of mm (a voxel corner), so
  every position has an identical voxel pattern. The same binary voxelisation as
  `ACR_Jaszczak_digital_phantom.py` is used.
- **Outside the phantom** the activity is zero. The reconstruction support is the full FOV.

### E2 positions

Chosen with `sampling_coverage_map.py`. Mean N_eff is the mean over the phantom ball.
T is the direction tensor at the phantom centre, with eigenvalues λ1 ≥ λ2 ≥ λ3 and
dominant viewing direction v1.

| Label | Centre (mm) | r_c (mm) | Mean N_eff | N_eff p5 | Notes |
|---|---|---|---|---|---|
| P0 | (0, 0, 0) | 0 | 45.8 at the centre | | Reference |
| P1 | (33, −9, 0) | 34.2 | | | Half-way to P2, same direction |
| P2 | (65, −18, 0) | 67.4 | 27.5 | 15.9 | Lowest in the z = 0 plane (az 345°). v1 is radial (\|v1·r̂\| = 0.99); at r ≈ 98, T = (0.46, 0.33, 0.21) and N_eff = 13 |
| P3 | (58, 35, 0) | 67.7 | 35.3 | 29.0 | Highest in the z = 0 plane (az 31°). v1 is tangential at the centre |
| P4+ | (0, 0, 68) | 68 | 32.4 | 21.3 | Towards the vertex |
| P4− | (0, 0, −68) | 68 | 39.7 | 34.8 | Towards the neck; lower sensitivity but more even views |

In the z = 0 plane, the mean N_eff on the 68 mm shell varies between 27.5 and 35.3
with azimuth. The scores for every azimuth are in
`sampling_brain_merged_123/phantom_centre_scores_r68.json`.

## E2 results (2026-10-05)

Outputs are in `cold_sphere_phantom/analysis/`: `montage_XY.png`, `montage_XZ.png`,
`full_slices_it100.png`, `metrics_vs_iteration.png` and `metrics.csv`.

- **No radial streaks at any position or iteration (10–200).** This includes P2: its
  surface reaches r = 99.4 mm in the direction with the lowest N_eff (13 at the outer
  edge), and its views are the most one-sided. On the 0–0.1 scale, almost no activity
  appears outside the phantom.
- **The rim reconstructs better than the centre, not worse.** At iteration 100:
  - Contrast recovery of the 15.9 mm sphere is 0.76 at P2 and P3, against 0.65 at P0.
  - Background CoV is 0.105–0.108 at P2, P3 and P4+, against 0.117 at P0.

  This fits higher resolution closer to the pinholes.
- **The background CoV is about 0.10–0.13 everywhere, even with noiseless data.** It comes
  from a fine speckle that grows with iteration count and does not depend on position.
  It is probably Monte Carlo noise in H (the question E3 would answer). This speckle is
  what dominates `bg_cov` and `diff_rms`.
- **The "minus P0" images mainly show differences in resolution** (sharper sphere edges,
  a ring at the phantom surface, and banding along z at P4+), plus the speckle.
  - The structure-tensor "streak axis" is radial at P2, P3 and P4+, but its anisotropy is
    small (at most 0.07). It most likely measures anisotropic blur (resolution differs
    between the radial and tangential directions), not streaks. It should not be read as
    streak evidence.
  - Its anisotropy does follow the mean N_eff ranking at iterations 20–50:
    P2 > P4+ > P3 > P4− ≈ P1.
- **Isolated hot voxels at the FOV boundary** (for example at about (92, 55, 0) mm in the
  P3 slice) appear even where there is no activity. These are the low-sensitivity
  boundary speckles described in the streak report.

**Interpretation (revised 2026-10-05).** E2 does not refute hypothesis 2. It shows that a
compact object produces no streaks, and there is a mechanism that explains why.

- **Streaks follow voxel-to-pinhole lines.** In an earlier session, the ACR LIR streaks
  were overlaid on the line from the voxel to each of the 73 pinholes, and the streaks
  lie along those lines. That coupling comes from H^T H, which depends only on the
  system, and it extends across the whole FOV.
- **But MLEM can only show the coupling where the estimate has activity.** The MLEM
  update is multiplicative, so its linearised response at voxel k is scaled by the
  current estimate x̂_k. Where the true activity is 0, x̂_k → 0, and no streak can
  appear there.
  - In the ACR, the hot background fills the FOV, so the lines show up everywhere.
  - In E2, everything outside the small phantom was empty. Inside the phantom, each line
    crosses at most 64 mm of activity, where blur dominates.
- **Two related distinctions:**
  - The Fisher column H^T diag(1/ȳ) H e_j depends on the object only through the
    weights 1/ȳ.
  - The MLEM LIR in `lir_acr.png` was computed around the ACR estimate, so the LIR
    depends strongly on the object.

Next is E5 (below): put hot activity where the coupling lines from the cold spheres land.
E1b (the ACR cropped to r ≤ 95 mm and r ≤ 80 mm) remains the test for the boundary-edge
form of hypothesis 1 (1b).

## E5: hot receivers on the coupling lines (2026-10-05)

The theory is in `report/fisher_svd_gram.pdf`.

**Setup:**
- **Source:** the cold-sphere phantom, at the centre (0, 0, 0) and at the rim P2
  (65, −18, 0).
- **Coupling map:** c = HᵀH a / s, where a is the indicator of the source's cold spheres.
  It is a star of broad bands along pinhole directions that crosses the whole FOV
  (`receiver_coupling/coupling_maps.png`).
- **Receivers:** two uniform hot spheres of radius 14 mm, in the source plane, 70–76 mm
  from the source centre. The coupled receiver sits in the strongest band; the control
  sits at the same distance in a gap, with about 10× less coupling.

| Source | Coupled receiver (c) | Control receiver (c) |
|---|---|---|
| Centre | (70, −12, 0), c = 1639 | (−64, −40, 0), c = 143 |
| Rim P2 | (−4, −6, 0), c = 1566 | (2, −58, 0), c = 161 |

**Measurement:** reconstruct source + receivers (SR) and receivers alone (R). Then
SR − R inside each receiver is what the source adds there. Outputs are in
`receiver_coupling/analysis/`.

**Results:**
- **The source does change distant receivers.** At iteration 10 the difference is a
  dipole, about ±0.1: lower on the side facing the source and higher on the far side,
  as if the receiver moved away from the source. By iteration 50–200 the dipole fades
  into speckle and a mean offset of +0.015–0.02 (SR receivers are 1.5–2% hotter).
- **The effect barely follows the coupling map.** The control receivers show the same
  dipole with similar amplitude. The RMS of SR − R at iteration 100 is:
  - centre source: 0.064 coupled against 0.056 control;
  - rim source: 0.077 against 0.061.

  That is 1.1–1.3× for 10× more coupling.
- **No line-shaped streaks** appear in any receiver. The orientation of the difference
  pattern does not consistently follow the source-to-receiver direction.

**Interpretation:**
- The long-range interaction MLEM produces between separate objects is a low-order
  effect (a shift and a level change), not pinhole-line streaks. Its size is set mostly
  by distance and direction relative to the source, not by the HᵀH band strength.
- The coupling bands are broad, 15–25 mm, because the 6–16 mm cold spheres sum many
  lines. Fine streaks would need edges that are sharp compared with a line's width, and
  a continuous hot medium in which many lines overlap. The ACR has both: a hot
  background with many edges, filling the FOV out to the boundary.
- Neither E2 nor E5 reproduces the ACR streaks. What the ACR has and these phantoms lack
  is a large, continuous hot background reaching the support boundary.

**Next:** a "growing background" series. Keep the cold spheres at the P2 position,
replace the 32 mm hot sphere with uniform hot spheres centred on the FOV, of radius 60,
80, 95, 100 and 105 mm, and see at which extent the streaks appear. Together with E1b
this separates "large hot extent" from "activity at the boundary".

## E6, E1b and the ideal LIR (2026-10-05)

### E6: growing background

The cold spheres stay at P2. The hot region is the P2 ball joined with a FOV-centred
ball of radius R = 32 (E2), 40, 60, 80, 95, 100 or 105 mm. Outputs are in
`extent_series/analysis/e6_montage.png`.

- **For R ≤ 100 mm, no radial streaks at any iteration (50–200).** This holds even when
  the hot region fills the FOV up to 100 mm. Each phantom shows only a bright overshoot
  ring at its own surface, and speckle.
- **For R = 105 mm (hot over the whole support, up to the model boundary), clear radial
  streaks appear at the rim.** They are strongest near the cold spheres, and they are the
  same pattern as the ACR streaks.

### E1b: cropped ACR

Outputs are in `extent_series/analysis/e1b_montage.png`.

- ACR cropped to r ≤ 80 mm or r ≤ 95 mm: no radial streaks in the sphere slice.
- The full ACR, which is hot up to the support boundary: the streaks of the report.

In the rod slab the cropped versions still show the rod and sector structure, but not
the streaky edge.

**The radial-streak index** (tangential over radial gradient energy,
`extent_series/analysis/metrics.csv`) cannot tell these cases apart. Wherever the hot
region stops inside the support, the blurred surface adds radial gradient beyond the
6 mm margin, which pushes the index below 1. It is above 1 only in grow_R105 and
acr_full (1.1–1.2 at r ≥ 70 mm), consistent with the images, but the images are the
evidence.

### Ideal LIR

`ideal_lir.py` computes R_α e_j = Hᵀ(HHᵀ + αI)⁻¹H e_j by conjugate gradients, at the
five voxels of `lir_acr.png`. Output: `ideal_lir/ideal_vs_mlem_lir.png`.

- **It reproduces the MLEM LIR streaks almost line for line.** This needs only H: no
  object, no positivity, no MLEM.
- **Far-field correlation** with the MLEM LIR (beyond 15 mm, in the slice) is 0.66–0.84
  at α = 10⁻³ λ_max, the best of the three values tried.
- **Smaller α adds speckle,** which is Monte Carlo noise in H.
- **CG cost:** 37–317 iterations, at most 70 s per solve.

### Conclusion

Both hypotheses are partly right.

1. **The shape of the streaks is a property of the SRM.** That is the sampling mechanism
   of hypothesis 2. The system's own point response already has the pinhole-line
   streaks, so they do not come from MLEM or from the object.
2. **What makes them appear in an image is activity reaching the edge of the modelled
   support.** That is the boundary form of hypothesis 1 (1b), and it is not data
   inconsistency, since all of these data are consistent.
   - Leaving even a 5 mm empty margin inside the support (grow_R100, acr_r095) removes
     the streaks.
   - A plausible reading is that the empty, known-zero margin acts as a support
     constraint, as in interior and truncated tomography: MLEM's multiplicative update
     pins it near 0, which fixes the poorly determined components there. When activity
     runs up to the boundary, the low-N_eff, low-sensitivity boundary shell has no
     such constraint.

**For the 288 mm SRM:** this prediction was tested in E8 and turned out to be wrong as
stated. A larger modelled FOV helps only if the empty space in it starts near zero; see
below.

## E7: margin width (2026-10-05)

Hot ball to R = 100, 101, 102, 103 and 104 mm (the same cold spheres at P2), in the Gate
SRM's 105 mm support. Outputs are in `extent_series/analysis/`: `margin_montage.png` and
`margin_zoom.png`.

- **Empty margin of 2 mm or more:** no streaks. The hot edge shows a bright, speckled
  overshoot band.
- **1 mm:** the band fades, and faint blobs and streaks start between the 15.9 mm sphere
  and the edge.
- **0 mm (R = 105):** clear streaks.

**Support facts.** The support's outermost voxel centre is at r = 105.8 mm. The median
sensitivity is 1,479 counts within r < 50 mm, 1,310 at r = 100–101 mm, 1,273 at
102–103 mm, and 1,063 at 104–105 mm.

**The angular streak amplitude in `analyze_margin_series.py` failed.** It masks the
cold-sphere sectors, which is exactly where the streaks are, and it ranks grow_R105
lowest. Do not use it. The visual comparison is the result.

## E8: a larger modelled FOV with a gammart SRM (2026-10-05)

**The gammart SRM.** `gammart_srm.py` builds it with the OptiX ray tracer
(~/Work/RPIL/QMIRT/pytorch-optix, `raytracing` env).

- 2 mm voxels, 144³ grid, modelled to r = 142 mm: 1,499,344 voxels and 615 M
  non-zeros, built in 542 s on the RTX 3080 Ti.
- It models primary photons only: the first interaction in the crystal, including
  collimator and shield penetration. Rays are sampled from each voxel through a disc
  around each pinhole, with sunflower points.
- **Validation against the Gate SRM.** Projections of r = 10 mm spheres at the centre and
  at (60, 0, 20) mm agree per pixel with correlation 0.9999 and 0.9997. The gammart
  totals are 3% higher (all first interactions, against Gate's energy window). Head
  order matches.

`gammart_support_test.py` and `gammart_support_followup.py` run noiseless MLEM with this
one matrix, varying only the support and the start image. Each 200-iteration run takes
about 15 s. Outputs are in `gammart_srm/`.

| Run | Object | Support (mm) | Start | Result |
|---|---|---|---|---|
| A | fill105 | 105 | uniform | mild streaks near the cold spheres at the edge |
| B | fill105 | 142 | uniform | strong radial streaks over the whole object, dark rim |
| C | fill101 | 105 | uniform | clean |
| D | ACR to 105 | 105 | uniform | rim streaks |
| E | ACR to 105 | 142 | uniform | stronger rim streaks |
| F | fill105 | 110 | uniform | clean, bright edge band |
| G | fill105 | 142 | uniform, 1000 it | streaks persist; noisy by it 1000 |
| H | fill105 | 142 | 0.01 beyond 105 | clean |
| I | fill101 | 142 | uniform | streaks |
| J | ACR to 105 | 110 | uniform | fine rim streaks |
| K | ACR to 105 | 142 | 0.01 beyond 105 | fine rim streaks, weaker than E |
| L | ACR to 95 | 105 | uniform | mostly clean, faint fine rim streaks |
| M | ACR to 95 | 142 | 0.01 beyond 95 | faint fine rim streaks |

**Share of reconstructed activity in the empty shell r > 105 mm:**
- G (uniform start in the 142 mm support): 33.8% at iteration 10, 8.8% at 200, and 3.0%
  at 1000.
- H (shell started at 0.01): 1.1% at iteration 10 and 0.5% at 200.

The large, poorly sampled empty shell empties slowly. The activity it still holds is
compensated along the pinhole lines through the object, which gives streaks.

## Conclusion (revised after E7 and E8)

1. **The SRM sets the geometry of the streaks.** They are its slowly converging,
   pinhole-line components (ideal LIR). They are strongest for rim voxels, which have
   low N_eff and one-sided views.
2. **The image shows them where the estimate has activity, and they need a source.**
   The sources seen here are:
   - object edges;
   - true activity in the poorly sampled rim zone;
   - spurious activity that MLEM still has to remove from a poorly sampled empty region
     that started non-zero.
3. **Neither hypothesis is right as first stated.**
   - The data are consistent throughout, so "truncation" in the data-inconsistency sense
     plays no part.
   - A larger FOV alone does not fix the streaks, and with a uniform start it makes them
     worse.
   - Sampling explains their shape and why the rim is where they appear.
4. **With the Gate SRM, a 2 mm or larger empty margin inside the support removed the
   streaks for the sphere phantom.** With the gammart SRM, faint fine rim streaks remain
   for the ACR even with margins or a near-zero start. The 1 mm Gate SRM has more
   speckle, which may hide them. The gammart SRM is *not* noise-free: building it with
   two seeds gives 7–11% sampling noise in the main entries, against 11–16% Poisson
   noise for the Gate SRM binned to 2 mm (see the report, section 2.3).
5. **For the 288 mm SRM:** reconstruct with an object-informed support or start image
   (the body contour plus a few mm, near zero beyond it), not a uniform start over the
   whole sphere. The larger FOV is still needed for real data with activity beyond
   210 mm, which was not tested here.

The full report is `report/streak_study_report.pdf`.

## E9: a shrunk ACR phantom as a test of the conclusion (2026-10-07)

**Purpose.** Test the conclusion above on an ACR-like object, not a sphere. Every
earlier ACR run had the hot background cut by the support boundary.

**Phantom** (`acr_fit_phantom.py`, `acr_fit/acr_fit.npz`):
- Hot cylinder of radius 95 mm, height 79 mm. Its face rims are at r = 102.9 mm, so
  every hot voxel is at least 2 mm inside the 105 mm FOV; the equator is 10 mm inside.
- The six ACR spheres keep their diameters, on an orbit scaled by 95/104.5 (52.3 mm),
  at z = +22.5 mm.
- The ACR rod sectors are rebuilt for the 95 mm cylinder, with the apex radii scaled
  and outer rows dropped; rods are 28 mm long (z = -35.5 ... -7.5 mm).
- Slice z = -0.5 mm is uniform background, between the inserts.

**Terms used below.**
- *Support*: the voxels MLEM may put activity in. A voxel that starts at 0 stays at 0,
  so the support is set by the start image f⁽⁰⁾.
- *Shell*: the voxels of the support outside the object region: here
  105 < r ≤ 142 mm in the gammart model.
- *Near-zero start*: f⁽⁰⁾ = 0.01 in the shell, against 1 elsewhere, so the shell starts
  with 1% of the object's activity level instead of 100%.
- *Contour support*: the phantom's outer cylinder grown by 4 mm (radius 99 mm,
  half-height 43.5 mm), intersected with the model support; 0 outside.

**Runs and predictions (written before running).**

| Run | SRM | Support / start | Prediction |
|---|---|---|---|
| G1 | Gate 1 mm | full SRM support (105.8 mm), uniform | no rim streaks (margin ≥ 2 mm, E7) |
| G2 | Gate 1 mm | contour support | no rim streaks, like G1 |
| A9 | gammart 2 mm | sphere r ≤ 105 mm, uniform | mostly clean; faint fine rim streaks possible (as run L) |
| B9 | gammart 2 mm | r ≤ 142 mm, uniform | streaks across the object; shell share several % at it 200 (as run I) |
| C9 | gammart 2 mm | r ≤ 142 mm, 1 to 105 mm, 0.01 beyond | streaks of B9 gone; shell share ≈ 1% |
| D9 | gammart 2 mm | contour support, 0 outside | as clean as A9 or cleaner |
| E9c | gammart 2 mm | contour + 0.01 in the rest of r ≤ 142 mm | like C9 and D9 |

The reference is the full ACR (acr_full for Gate, acr105 for gammart), which streaks.

**Streak measure, in addition to the images.** In the uniform slice z = -0.5 mm, the
mean over 80 ≤ r_xy ≤ 92 mm is taken per 1° of azimuth. Radial streaks survive this
radial average; speckle mostly averages out. The measure is the standard deviation of
that angular profile over its mean. It is the same object in every run, so the cold
rods 7 mm below add the same amount to each run.

### E9 results (2026-10-07)

Outputs are in `acr_fit/`: `e9_gate.png`, `e9_gammart.png`, `e9_differences.png`
(each run minus the contour-support run, same object and matrix), `e9_slides.png`, and
the JSON files. Script: `e9_acr_fit_test.py`.

| Run | Prediction | Observed | Verdict |
|---|---|---|---|
| G1 | no rim streaks | no rim streaks; bright speckled band at the hot edge, as in E7 | as predicted |
| G2 | like G1 | like G1; G1 − G2 is a smooth level offset early on, then rings at the hot edge | as predicted |
| A9 | mostly clean, faint fine edge ripples possible | faint fine ripples at the hot edge only | as predicted |
| B9 | streaks across the object, shell share several % at it 200 | object pulled down with radial spokes early (B9 − D9 RMS in the rod slice 0.094 at it 10, 0.041 at 50, 0.020 at 200); shell share 15.6% at it 10, 0.65% at 200 | mechanism as predicted, much weaker than predicted |
| C9 | B9's effect gone, shell ≈ 1% | C9 − D9 ≈ A9 − D9 (≈ 0.01 RMS by it 50); shell 0.27% → 0.07% | as predicted |
| D9 | as clean as A9 or cleaner | clean | as predicted |
| E9c | like C9 and D9 | E9c − D9 RMS ≈ 0.001 at every iteration | as predicted |

- **No run with the object at least 2 mm inside the FOV shows the ACR rim streaks.**
  The references (acr_full on Gate, acr105 on gammart) do, with the same matrices.
- **A near-zero shell start is as good as a perfect contour support**: E9c and D9 are
  practically identical.
- **B9 is weaker than E8 run I** (hot ball to 101 mm, same support and start). The
  shell drains about 5× faster (0.65% against 3.3% at it 200). A plausible reason: here
  the hot edge is 2–10 mm from r = 105 mm, so shell voxels share fewer detector bins
  with the object's rim and are easier to tell apart. Not tested.
- **The remaining differences in A9, C9 and G1** come from the empty space inside
  105 mm (above and below the cylinder, and the 10 mm at the equator). It starts at 1
  in those runs and at 0 in the contour runs. It gives a smooth level offset that
  decays by iteration 50, then rings at the hot edge. It does not give streaks.
- **The scalar streak measure failed again.** The acr_fit runs score higher (0.043–0.050)
  than acr_full (0.035), which clearly streaks. The overshoot band at the 95 mm edge
  and the cold rods 7 mm below dominate the 80–92 mm annulus. Do not use it. The
  difference maps against the contour run are the useful quantitative view.

### Correction (2026-10-07): streaks remain at the object's own edge

The E9 verdicts above for G1, G2, A9 and D9 ("no rim streaks") were wrong. They came from
zooms and slices that looked at the old phantom's rim (r ≈ 100 mm), not at the shrunk
ACR's own edge (r = 95 mm). The same mistake affects the E1b verdict for the cropped ACR.

**Polar view.** Each slice is unwrapped around the object's own edge: distance from the
edge against azimuth. Radial streaks show as vertical stripes. Figures:
`acr_fit/e9_polar_edge.png`, `acr_fit/e9_polar_slides.png` and
`extent_series/analysis/polar_edge_e1b.png` / `polar_edge_grow.png`.
- **Shrunk ACR, ray-traced SRM** (A9, and D9 with the contour support): clear stripes run
  10–25 mm inward from the edge, mostly at azimuths 100–300°. They are weaker and shorter
  than the full ACR's, but they are the same kind.
- **Shrunk ACR, Gate SRM** (G1, G2): the same stripes, partly hidden by the Monte Carlo
  speckle.
- **Cropped ACR on Gate** (acr_r095): stripes at its own edge, weaker than acr_full.
- **Uniform balls on Gate** (grow_R080 … R104): only an overshoot band with short,
  radially elongated texture; long stripes only for grow_R105. The E6/E7 verdict holds
  for a uniform object.

### E9b: what makes the edge streaks (2026-10-07)

`e9b_edge_streaks.py`. Ray-traced SRM, support r ≤ 105 mm, ε = 1, 200 iterations,
object-by-object. "Stripe RMS" = RMS of the azimuthal high-pass of (recon − truth) in the
band 3–20 mm inside the edge, sphere slice. Truth is subtracted so the inserts' own
structure does not count.

| Object | Stripes in the polar view (sphere slice) | Stripe RMS, it 200 |
|---|---|---|
| Cylinder only | none; a ring at the edge | 0.014 |
| + cold spheres | some, near the spheres | 0.024 |
| + cold rods (30–60 mm below this slice) | strong, at 100–300° | 0.029 |
| + spheres + rods (shrunk ACR) | strongest | 0.035 |

- **The inserts drive the edge streaks**, and the rods do so from another slab. Errors
  from structure the system cannot resolve (the dense small rods) spread along oblique
  voxel-to-pinhole lines into other slices, and appear where those lines cross hot
  activity, here the outer part of the sphere slice.
- **This fits the ideal-LIR picture.** The geometry is set by H; the source here is
  insert structure, not the support edge.
- **The stripe RMS in the rod slice is not usable**: there it is dominated by the
  unresolved rods themselves (0.18–0.20).

### Conclusion (revised after E9b)

1. **The SRM sets the geometry of the streaks**: voxel-to-pinhole lines, strongest for
   poorly sampled (rim) voxels. Unchanged.
2. **Sources seen so far:**
   - cold inserts the system cannot resolve, rods especially; their errors cross into
     other slices along oblique lines (E9b);
   - activity reaching the support edge (E6, E7: uniform ball at 104 vs 105 mm);
   - a poorly sampled shell that starts full (E8, E9 run B9).
3. **Keeping the object inside the FOV removes only the support-edge source.** The ACR's
   rods still produce streaks at the object's edge with any support (A9, D9, G1, G2).
4. **Weaker for the shrunk ACR than for the full ACR.** Possible reasons: the edge is at
   95 mm instead of 104.5 mm (higher N_eff), the support-edge source is gone, and there
   are fewer rods. Not separated.
5. **For the 288 mm SRM**, the start-image recommendation (ε ≈ 0.01 outside the
   contour) still holds. But it will not remove insert-driven streaks; those belong to
   the system's sampling.

## Edge overshoot compared with Snyder et al. 1987 (2026-10-07)

`analyze_edge_overshoot.py` measures the bright band inside the hot edge of the Gate-SRM
uniform balls (grow_R080 … R105). It uses the 3-D radial profile around each ball's own
edge, excluding a 50° cone around the P2 cold spheres. Overshoot = peak within 15 mm inside
the edge over the plateau 25–40 mm inside. Outputs: `extent_series/analysis/edge_overshoot.png`
and `.json`. Reference: `dev/references/` (Snyder, Miller, Thomas & Politte, IEEE TMI
6:228, 1987).

| Edge at | it 20 | it 50 | it 200 | Undershoot it 200 | it 200 + 6 mm filter | + 10 mm filter |
|---|---|---|---|---|---|---|
| 80 mm | 14.8 % | 15.1 % | 14.2 % | −5.6 % | 7.3 % | 1.6 % |
| 95 mm | 10.8 % | 12.9 % | 12.8 % | −3.5 % | 6.0 % | 1.0 % |
| 100 mm | 6.7 % | 9.9 % | 11.6 % | −2.7 % | 5.3 % | 0.8 % |
| 105 mm (fills the support) | 0.2 % | 0.3 % | 0.6 % | −0.1 % | — | — |

**What matches Snyder et al.**
- The overshoot appears with noiseless, consistent data.
- It grows with iterations and then levels off at 11–15 % (theirs: about 16–18 % in 1-D).
- It is followed by a weaker undershoot and ripple further inside, like a Gibbs overshoot.
- Its peak moves toward the edge as iterations proceed (−11.5 → −5.5 mm), as finer
  detail is recovered.
- Post-filtering removes it: a 6 mm Gaussian halves it, and a 10 mm Gaussian removes it
  (≤ 1.6 %). This is their remedy of estimating a blurred version of the object.

**What their paper does not cover.**
- **The overshoot depends on the edge position.** It is smaller and rises more slowly
  the closer the edge is to the rim (80 → 100 mm). This fits the slower convergence of
  poorly sampled voxels, but that is not tested.
- **A ball that fills the support has no overshoot.** There is no edge inside the
  support for MLEM to represent. That is also the case that streaks.
- **Their overshoot grows with kernel mismatch** (~30 % with a truncated EM kernel).
  Here the data and the reconstruction use the same H, so there is no mismatch.

## Implementation

- `sampling_coverage_map.py`: 3-D maps of the sensitivity, N_eff and direction tensor T,
  in one pass over the module SRMs, saved to `sampling_brain_merged_123/sampling_1mm.npz`.
  It checks the axis convention: every module's sensitivity centroid must lie on its
  pinhole's side. It also scores candidate phantom centres.
- `cold_sphere_phantom.py --center-mm X Y Z`: writes
  `cold_sphere_phantom/cold_sphere_phantom_x{X}_y{Y}_z{Z}.npz`, plus a JSON layout and a
  slice plot. It refuses a centre that is not a whole number of voxels, or a phantom
  reaching beyond 100 mm.
- Reconstruction, using the existing script unchanged. One run takes about 75 s on the
  RTX 3080 Ti (compact-gpu engine):
  `python fp_jaszczak_and_recon.py --phantom cold_sphere_phantom/<stem>.npz --iterations 10 20 50 100 200 --output-dir cold_sphere_phantom/runs/<stem>`
- `analyze_cold_sphere_shift.py`: writes the metrics (JSON and CSV), the XY and XZ
  montages, whole-slice views and metric-versus-iteration plots to
  `cold_sphere_phantom/analysis/`.
- Not yet: `--support-radius-mm` in `fp_jaszczak_and_recon.py` (E1a), E3 and E4.
