// Compile from the repository root:
// typst compile streak_study_report.typ

#set document(title: "Rim Streaks in Brain SPECT MLEM", author: "Fang Han")
#set page(paper: "us-letter", margin: (x: 1.9cm, y: 1.8cm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")
#show figure.caption: set text(size: 9pt)
#show table.cell.where(y: 0): set text(weight: "bold")
#show link: set text(fill: rgb("#1c5cab"))

#align(center)[
  #text(size: 17pt, weight: "bold")[Rim Streaks in Stationary Multi-Pinhole Brain SPECT: \
    Truncation, Sampling, and the Modelled Support]
  #v(4pt)
  Fang Han · 2026-10-05 · study report \
  #text(size: 9pt)[Follows `streak_artifacts_report.pdf` (2026-10-01). Theory details:
  `fisher_svd_gram.pdf`. Working notes: `dev/python/streak_sampling_study.md`.]
]

#block(fill: luma(245), inset: 9pt, radius: 3pt)[
  *Summary.* MLEM reconstructions of the hot-background ACR Jaszczak phantom on the
  73-module brain system show radial streaks near the edge of the 210 mm FOV. Two
  explanations were proposed:
  - the FOV modelled by the SRM is too small, which a 288 mm SRM would fix
    (*truncation*);
  - the rim is seen from too few directions (*sampling*).

  Eight sets of noiseless, fully consistent reconstructions were run, with the Monte
  Carlo SRM and with a new ray-traced SRM that models the FOV out to r = 142 mm. The
  findings:

  + *The SRM determines the shape of the streaks.* The system's own regularised point
    response, $H^top (H H^top + alpha I)^(-1) H bold(e)_j$, reproduces the streaks of
    the MLEM local impulse response almost line for line. They lie on the lines from
    the voxel through the pinholes, and they are strongest at the rim, where voxels are
    seen from few, one-sided directions. This is the sampling mechanism.
  + *Streaks need a source, and they show only where there is activity.* A compact
    phantom anywhere in the FOV, even at r = 100 mm in the least-sampled direction,
    reconstructs without streaks. Streaks appeared in three cases:
    - activity reaches the edge of the modelled support (an empty margin of 2 mm or
      more removes them, for a sphere phantom with the Monte Carlo SRM);
    - the object has many edges in the rim zone;
    - MLEM must empty a large, poorly sampled region that started non-zero.
  + *A larger modelled FOV is not a fix by itself.* With the ray-traced SRM and the
    usual uniform start, extending the support from 105 to 142 mm made the streaks
    *stronger*. At iteration 200, 8.8% of all reconstructed activity was still in the
    empty shell. Starting the shell near zero removed this effect.

  *Recommendation.* Build the 288 mm SRM: it is still needed for real heads with
  activity outside 210 mm, which this study did not test. But reconstruct with an
  object-informed support or start image (the body contour plus a few mm, near zero
  outside), not a uniform start over the whole sphere. With the current SRM, keep
  evaluation phantoms at least a few mm inside the 105 mm edge.
]

#outline(depth: 2, indent: 1.2em)

= Question and background

== The system

The brain SPECT system has 73 pinhole modules in 7 rings, at elevations of −37° to 90°.
Each module has a 50 × 50 × 10 mm crystal of 25 × 25 pixels, which gives $M = "45,625"$
detector bins. There are four pinhole sizes, 0.556–2.007 mm. The pinhole centres lie on
a sphere of radius 149.6 mm, and the collimator nozzle tips start at r = 144.6 mm. The
production system matrix (SRM, `brain_merged_123`) is a Gate 10 Monte Carlo simulation:

- 140 keV photons from a uniform 105 mm-radius sphere;
- $1.26 times 10^13$ primaries;
- 126–154 keV energy window;
- binned on a $210^3$ grid of 1 mm voxels;
- $1.50 times 10^9$ non-zero entries;
- $N = "4,944,385"$ voxels with sensitivity (the *support*), whose outermost voxel
  centre is at r = 105.8 mm.

== The observation

The ACR Jaszczak phantom with a hot background was forward projected through the SRM and
reconstructed with MLEM from those noiseless data. The phantom has six cold spheres and
six rod sectors, and its hot volume fills the support. Radial streaks appear in the
background near the FOV edge (@fig-obs). They grow with iteration count, and they are
largest in the rod slab.

#figure(
  placement: auto,
  image("figs/recon_axial_z130_iterations.png", width: 100%),
  caption: [The observation that started this study: ACR phantom, sphere slice
    (z index 130), MLEM iterations 10, 50, 100 and 200, grey scale 0.6–1.3. Radial
    streaks start near the FOV edge.],
) <fig-obs>

== Two hypotheses

+ *Truncation.* The modelled FOV (210 mm diameter) is too small; a 288 mm SRM is needed.
+ *Sampling.* Rim voxels are seen by fewer modules, from a narrow range of directions,
  so MLEM leaves errors free to spread along the poorly sampled direction.

All data in this study are *noiseless and consistent*: they are computed with the same
matrix that is used to reconstruct them. Truncation in its usual sense, activity outside
the model adding unexplained counts, therefore cannot occur. What remains testable is
whether the *edge of the modelled support* matters, and whether a larger support helps.

= Methods

== Reconstruction

MLEM, $f_j^((n+1)) = f_j^((n)) / s_j sum_i H_(i j) y_i \/ (H bold(f)^((n)))_i$, with
sensitivity $s_j = sum_i H_(i j)$:

- noiseless data $bold(y) = H bold(f)$;
- a start image of 1 on the support and 0 elsewhere, unless stated otherwise;
- estimates saved at iterations 10, 20, 50, 100 and 200;
- run on an RTX 3080 Ti with a compact GPU implementation (`compact_gpu_mlem.py`).

A 1 mm run of 200 iterations takes about 75 s. Voxels that start at 0 stay at 0, so
restricting the start image is equivalent to restricting the support.

== Sampling maps

`sampling_coverage_map.py` accumulates three maps per voxel in one pass over the module
SRMs:

- the sensitivity;
- the effective number of modules
  $N_"eff" (j) = 1 \/ sum_m w_(m j)^2$, with $w_(m j) = s_(m j) \/ s_j$;
- the direction tensor $T_j = sum_m w_(m j) bold(u)_(m j) bold(u)_(m j)^top$, where
  $bold(u)$ points from the voxel to the pinhole.

The largest eigenvector of $T$ is the dominant viewing direction, and its eigenvalue
spread measures how one-sided the views are. The script checks that each module's
sensitivity centroid lies on its own pinhole's side, which confirms the axis convention.

== Ray-traced SRM for a larger FOV

`gammart_srm.py` builds a second system matrix with the OptiX ray tracer `gammart`. It
uses the same brain geometry, with the analytic (CSG) shield. Each column is the
probability that a 140 keV photon emitted in the voxel has its *first* interaction in
each crystal pixel, with collimator and shield penetration included. Scatter is not
modelled and no energy window is applied.

The sampling, per voxel and per module:
- 512 rays from points jittered inside the voxel;
- aimed at a disc around the pinhole, of radius equal to the aperture half-diagonal plus
  1 mm, with sunflower (quasi-random) points on the disc;
- each ray weighted by its exact solid angle.

*It is not fully deterministic.* The attenuation along each ray is computed exactly, with
no random photon interactions. But the integral over the voxel and the pinhole disc is
estimated from sampled rays: the starting points inside the voxel are random, and each
voxel and module gets a random rotation of the disc pattern. The generator is seeded, so
a build can be repeated. Building the same 2,000 columns with two seeds gives this
sampling noise:

#table(
  columns: (auto, auto, auto),
  stroke: 0.4pt,
  inset: 4pt,
  [Entry size (share of its column's maximum)], [Ray-traced, sampling noise],
    [Gate at 2 mm, Poisson noise (median counts)],
  [0.5–1], [7.9%], [10.6% (89)],
  [0.1–0.5], [7.4%], [15.8% (40)],
  [0.01–0.1], [11.0%], [32.2% (10)],
  [0.001–0.01], [38.8%], [92.3% (1)],
)

- Totals are much more stable: 0.85% per voxel, and 1.5% per voxel and module.
- The Gate column is the Poisson noise the Gate SRM would have with the same entries
  binned to 2 mm (its 1 mm entries are 8 times noisier in count terms).
- The ray-traced matrix is therefore 1.3–3 times less noisy per entry, *not noise-free*.

Two other approximations: rays outside the pinhole disc (penetration more than 1 mm
beyond the aperture edge) are not traced, and entries below $10^(-3)$ of their column's
maximum are dropped.

The matrix has 2 mm voxels, a $144^3$ grid, and is modelled to r = 142 mm: 1,499,344
voxels and 615 M non-zeros, built in 9 minutes. A 200-iteration MLEM run with it takes
about 15 s.

*Validation (@fig-val).* Spheres of radius 10 mm, at the centre and at (60, 0, 20) mm,
were projected through both matrices. The projections agree pixel by pixel with
correlation 0.9999 and 0.9997, and per head essentially exactly. The ray-traced totals
are 3% higher, as expected: they count all first interactions, while Gate counts only
events in the energy window.

#figure(
  image("figs/e8_validation.png", width: 92%),
  caption: [The ray-traced SRM against the Gate SRM: share of counts per head for a
    10 mm sphere at the centre (left) and off-centre (right).],
) <fig-val>

== Phantoms

#figure(
  table(
    columns: (auto, 1fr, auto),
    stroke: 0.4pt,
    inset: 4.5pt,
    align: (left, left, left),
    [Name], [Description], [Used in],
    [Cold-sphere phantom],
    [Hot sphere (radius 32 mm, activity 1) with cold spheres of 15.9, 6.4, 12.7 and
      9.5 mm (the four smallest of the small Jaszczak phantom) on a 16 mm ring in its
      transverse mid-plane. Shifted in whole voxels, never rotated, so every position has
      the same voxel pattern. Zero activity outside.],
    [E2, E5, E6, E7],
    [Receivers], [Uniform hot spheres, radius 14 mm, no cold spots], [E5],
    [Growing background],
    [The cold spheres at the rim position P2, inside a hot region that is the P2 ball
      joined with a FOV-centred ball of radius R = 40–105 mm],
    [E6, E7],
    [ACR Jaszczak], [The hot-volume ACR phantom of the earlier report, uncropped or cropped to r ≤ 80 or 95 mm], [E1b, E8],
  ),
  caption: [Phantoms. All are binary (activity 0 or 1) on the reconstruction grid; the
    ACR is block-averaged when resampled to 2 mm.],
)

= Theory in brief

Details and derivations are in `fisher_svd_gram.pdf`.

*The Fisher information matrix.* For Poisson data it is $F = H^top D H$, with
$D = "diag"(macron(bold(y)))^(-1)$. Its column $F bold(e)_j$ (one forward and one back
projection) shows which voxels share detector bins with voxel $j$. For a pinhole system
these voxels lie on the lines from $j$ through every pinhole, across the whole FOV.
$F$ depends on the object only through the weights $D$.

*The MLEM response.* Linearising MLEM about its iterate gives the local impulse response

$ "LIR"_j^((n)) = sum_(m=0)^(n-1) (I - P F)^m P F bold(e)_j, quad P = "diag"(hat(f)_k / s_k). $ <lir>

Two consequences:

- *The response at voxel $k$ is scaled by $hat(f)_k$.* MLEM cannot show coupling where
  the estimate is zero, which is why compact phantoms show no long streaks. It does show
  coupling wherever the estimate holds activity, real or spurious.
- *In the SVD of $D^(1\/2) H P^(1\/2)$, component $k$ is recovered by the factor
  $1 - (1 - sigma_k^2)^n$.* Small-$sigma$ components converge slowly, so their partial
  recovery changes with iteration count.

*The null space.* $"rank"(H) <= "45,625"$, against 4.94 million voxels: at least 99% of
the 1 mm image space is not constrained by the data at all. Positivity, the start image
and early stopping decide what MLEM returns there.

*The ideal LIR.* The data-space Gram matrix $H H^top$ has size $"45,625"^2$. It gives
the Tikhonov-regularised resolution operator
$R_alpha = H^top (H H^top + alpha I)^(-1) H$. Its point response $R_alpha bold(e)_j$
depends only on the system: no object, no positivity, no MLEM.

= Results

== Sampling at the rim

$N_"eff"$ falls from about 46 at the centre to 13–20 near r = 100 mm (@fig-cov), and it
depends on direction. Phantom-averaged values on a 68 mm shell, for the positions used
later:

#figure(
  table(
    columns: 5,
    stroke: 0.4pt,
    inset: 4pt,
    [Position], [Centre (mm)], [Mean $N_"eff"$], [5th pct.], [Direction tensor at the centre],
    [P0], [(0, 0, 0)], [45.8 (centre)], [–], [eigenvalues 0.40, 0.37, 0.23],
    [P2, lowest in plane], [(65, −18, 0)], [27.5], [15.9], [dominant view radial ($|bold(v)_1 dot hat(bold(r))| = 0.99$)],
    [P3, highest in plane], [(58, 35, 0)], [35.3], [29.0], [dominant view tangential],
    [P4+, toward vertex], [(0, 0, 68)], [32.4], [21.3], [–],
    [P4−, toward neck], [(0, 0, −68)], [39.7], [34.8], [most even views],
  ),
  caption: [Sampling at the phantom positions. At the outer edge of P2 (r ≈ 98 mm),
    $N_"eff" = 13$ and the tensor eigenvalues are 0.46, 0.33 and 0.21.],
)

#figure(
  image("figs/coverage_z130.png", width: 80%),
  caption: [Sensitivity and effective number of modules in one slice (from the earlier
    report). The total sensitivity is smooth; $N_"eff"$ falls toward the rim.],
) <fig-cov>

== E2: a compact phantom moved to the rim shows no streaks

The cold-sphere phantom was reconstructed at P0, P1, P2, P3, P4+ and P4−
(@fig-e2). No radial streaks appear at any position or iteration (10–200), including
P2, whose surface reaches r = 99.4 mm in the least-sampled direction. The rim
reconstructs *better* than the centre at iteration 100:

- contrast recovery of the 15.9 mm sphere is 0.76 at P2 and P3, against 0.65 at P0;
- background CoV is 0.105–0.108, against 0.117.

Every position shows a fine speckle that grows with iterations, with background CoV
about 0.10–0.13 even with noiseless data. It is consistent with Monte Carlo noise in the
SRM.

#figure(
  placement: auto,
  image("figs/e2_montage_xy.png", width: 92%),
  caption: [E2: XY slice through the phantom centre at six positions and five iterations
    (grey scale 0–1.3), and the difference from P0 at iteration 100. Yellow dashed circles:
    true cold spheres, with radius in mm. Arrow: outward radial direction.],
) <fig-e2>

== E5: hot receivers on the coupling lines

The theory says MLEM can show coupling only where there is activity. So uniform hot
receivers were placed 70–76 mm from the cold-sphere source: one in the strongest band
of the coupling map $H^top H bold(a) \/ bold(s)$ (where $bold(a)$ is the indicator of
the cold spheres), and a control at the same distance in a gap with about 10× less
coupling. The source sat either at the centre or at P2. Comparing source plus receivers
against receivers alone (@fig-e5):

- the source shifts distant receivers: a ±0.1 dipole at iteration 10, then speckle and a
  1.5–2% rise in level;
- receivers in the band are consistently more affected, but only 1.1–1.5× more for 10×
  more coupling;
- no line-shaped streaks appear in any receiver.

Between separate compact objects, the long-range interaction is a low-order effect, not
streaks.

#figure(
  placement: auto,
  image("figs/e5_centre.png", width: 100%),
  caption: [E5, centre source. Top: coupling map, the two reconstructions and their
    difference at iteration 100. Bottom: the difference in the coupled receiver (blue)
    and the control (orange) over iterations.],
) <fig-e5>

== The ideal LIR: the streak pattern belongs to the SRM

$R_alpha bold(e)_j$ was computed at the five voxels of the earlier LIR figure by
conjugate gradients on $H H^top + alpha I$:

- 37–317 iterations per solve, each one forward and one back projection;
- at most 70 s per solve;
- three values of $alpha$ relative to $lambda_max (H H^top)$.

At $alpha = 10^(-3) lambda_max$ it reproduces the MLEM LIR streaks almost line for line,
with the same positions and signs (@fig-ideal). Beyond 15 mm from the voxel the
correlation is 0.66–0.84. Smaller $alpha$ adds speckle, which is Monte Carlo noise in $H$
being amplified.

#figure(
  placement: auto,
  image("figs/ideal_vs_mlem_lir.png", width: 92%),
  caption: [Ideal LIR $R_alpha bold(e)_j$ for three $alpha$ (system only) against the MLEM
    LIR at iteration 200 around the ACR phantom (right). Slice z index 130, colour ±5% of
    the peak. Third column: lines from the voxel to each pinhole.],
) <fig-ideal>

== E6 and E1b: streaks appear when activity reaches the edge of the support

*E6, growing background.* The cold spheres stayed at P2, and the hot background grew
from a 32 mm ball to the whole support (@fig-e6). There are no streaks for any hot
extent up to r = 100 mm. Clear rim streaks appear only when the hot region fills the
support to 105 mm.

*E1b, cropped ACR.* The ACR cropped to r ≤ 80 or 95 mm shows no streaks; the uncropped
phantom shows the streaks of the report (@fig-e1b).

#figure(
  placement: auto,
  image("figs/e6_montage.png", height: 88%),
  caption: [E6: transverse slice z = 0.5 mm, iterations 50, 100 and 200, grey scale
    0.6–1.3. The hot region grows from the 32 mm P2 ball (top) to the whole support
    (bottom).],
) <fig-e6>

#figure(
  placement: auto,
  image("figs/e1b_montage.png", width: 100%),
  caption: [E1b: ACR phantom cropped to r ≤ 80 mm (top) and 95 mm (middle), and
    uncropped (bottom). Sphere slice at iterations 50, 100 and 200, and the rod slab at
    iteration 100.],
) <fig-e1b>

== E7: about 2 mm of empty margin is enough with the Monte Carlo SRM

The hot ball's radius was set to 100–105 mm in 1 mm steps (@fig-e7):

- *an empty margin of 2 mm or more:* no streaks; the hot edge shows a bright, speckled
  overshoot band;
- *1 mm:* faint blobs and streaks start between the 15.9 mm sphere and the edge;
- *0 mm:* clear streaks.

The sensitivity at the support edge is not dramatically low: the median is 1,063 counts
at r = 104–105 mm, against 1,479 at the centre. What changes is whether the
poorly sampled shell holds activity.

#figure(
  placement: auto,
  image("figs/e7_margin_zoom.png", width: 100%),
  caption: [E7: zoom on the cold spheres near the rim, grey scale 0.8–1.2. Columns: hot
    radius 95–105 mm (empty margin 10 to 0 mm). Rows: iterations 50 and 200. Blue dashed:
    support edge; yellow dotted: hot edge.],
) <fig-e7>

== E8: a larger modelled FOV with the ray-traced SRM

All runs below use the one ray-traced matrix; only the support and the start image
change.

#figure(
  table(
    columns: (auto, auto, auto, auto, 1fr),
    stroke: 0.4pt,
    inset: 4pt,
    [Run], [Object], [Support (mm)], [Start], [Result],
    [A], [hot to 105 + spheres], [105], [uniform], [mild streaks near the spheres at the edge],
    [B], [hot to 105 + spheres], [142], [uniform], [*strong* radial streaks over the whole object, dark rim],
    [C], [hot to 101 + spheres], [105], [uniform], [clean],
    [D], [ACR to 105], [105], [uniform], [rim streaks],
    [E], [ACR to 105], [142], [uniform], [stronger rim streaks],
    [F], [hot to 105 + spheres], [110], [uniform], [clean, bright edge band],
    [G], [hot to 105 + spheres], [142], [uniform, 1000 it], [streaks persist; noisy by it 1000],
    [H], [hot to 105 + spheres], [142], [0.01 beyond 105 mm], [clean],
    [I], [hot to 101 + spheres], [142], [uniform], [streaks],
    [J], [ACR to 105], [110], [uniform], [fine rim streaks],
    [K], [ACR to 105], [142], [0.01 beyond 105 mm], [fine rim streaks, weaker than E],
    [L], [ACR to 95], [105], [uniform], [mostly clean, faint fine rim streaks],
    [M], [ACR to 95], [142], [0.01 beyond 95 mm], [faint fine rim streaks],
  ),
  caption: [E8 runs (2 mm, noiseless MLEM; results read at iterations 100–200).],
) <tab-e8>

*Why the larger support made things worse.* The shell from 105 to 142 mm holds more
voxels than the object, it is the least-sampled part of the model, and a uniform start
fills it with activity. MLEM empties it slowly. With a uniform start (G), the share of
reconstructed activity in that empty shell was:

- 33.8% at iteration 10;
- 8.8% at iteration 200;
- 3.0% at iteration 1000.

The counts this leftover activity predicts are taken away from the object along the
pinhole lines, which produces streaks across the object (@fig-e8a). Starting the shell
at 0.01 (H) keeps the share at 0.5–1.1% and removes the streaks for the sphere phantom
(@fig-e8b).

*The ACR keeps faint, fine rim streaks* in the ray-traced matrix: with a 5 mm margin
(J), with a near-zero shell start (K), and even when cropped to 95 mm (L, M). They are
much weaker than with the uniform start. The ray-traced matrix has less speckle than the
1 mm Gate SRM, which may be why they show here; in the Gate images (E1b) the speckle
could hide streaks of this size. This is not settled, since the ray-traced matrix still
has 7–11% sampling noise in its main entries.

#figure(
  placement: auto,
  image("figs/e8_support_test.png", width: 82%),
  caption: [E8 runs A–E: iterations 50, 100 and 200, and a zoom at iteration 100. Yellow:
    object edge (105 mm); blue: support edge. Spheres slice z = 1 mm; ACR slice z = 25 mm.],
) <fig-e8a>

#figure(
  placement: auto,
  image("figs/e8_support_followup.png", height: 86%),
  caption: [E8 follow-up runs F–M, with the share of reconstructed activity beyond 105 mm
    (right).],
) <fig-e8b>

= Discussion

== What causes the streaks

The experiments fit one picture.

+ *Geometry from the SRM.* The streaks are the SRM's slowly converging, small-$sigma$
  components. Each is a set of voxel-to-pinhole lines, and rim voxels, with low
  $N_"eff"$ and one-sided views, carry the strongest. The ideal LIR, computed without
  any object or MLEM, already has them. This is the sampling hypothesis, and it explains
  why the rim is where streaks appear.
+ *Visibility from the estimate.* By @lir, MLEM can only show them where the current
  estimate has activity. That is why E2 and E5, compact objects in empty space, showed
  none.
+ *Excitation by a source of error in the poorly sampled zone.* The sources seen here
  are:
  - true activity running into the rim shell (E6, E7, and A against C);
  - spurious activity MLEM has not yet removed from a large, poorly sampled region (B,
    G, I);
  - many object edges near the rim (the ACR, J–M).

  An empty margin works when it is thin, or starts near zero. In those cases it is
  emptied fast and then acts as a known-zero region next to the object.

*Truncation*, in the sense of activity the model cannot represent, played no role: every
data set was consistent. The FOV boundary matters only as the place where the support
either cuts through rim activity (A, D, E6, E7) or adds a large, poorly sampled empty
region that must be emptied (B, E, G, I).

== Implications for the 288 mm SRM

- *Still worth building.* Real heads and necks put activity outside the 210 mm sphere,
  which is true truncation, and it was not tested here. A larger model is the
  straightforward fix for it.
- *But a larger FOV alone does not remove the streaks, and with a uniform start it makes
  them worse.* The extra shell, out to 144 mm, is sampled even more poorly than the
  current rim: fewer than 48 modules see beyond 228 mm diameter.
- *Reconstruct with an object-informed support or start image.* Use the body contour
  (from CT or the attenuation map, or a thresholded first pass) plus a few mm, and set
  the start near zero beyond it. In E8 this made the 142 mm model as good as the tight
  one (H against A) for the sphere phantom.
- *Expect faint fine rim streaks for complex objects* even then (K–M). Their size under
  realistic noise and iteration counts is not known yet.

== What did not work

- *The scalar streak metrics.*
  - The structure-tensor "streak axis" in E2 measured anisotropic blur, not streaks.
  - The radial-streak index (tangential over radial gradient energy) was dominated by
    surface roll-off.
  - The angular-profile amplitude (E7) masked the cold-sphere sectors, where the streaks
    are.

  The conclusions here rest on images, with shared grey scales and reference panels.
- *The coupling map as a predictor of where streaks land* (E5): it predicted the
  direction of the effect but not its size.

== Limitations

- *Noiseless, consistent data only.* There is no Poisson noise, attenuation or scatter,
  and there are no model errors.
- *The Monte Carlo SRM has visible speckle at 1 mm.* The ray-traced SRM is primary-only
  (no scatter, no energy window), at 2 mm, and has 7–11% sampling noise in its main
  entries.
- *Evidence is mostly visual*, from single transverse slices, with three phantom
  families.
- *Iterations stop at 200* (1000 in one run). No regularisation or ordered subsets were
  tried.

= Recommendations and next steps

+ *For the 288 mm production,* plan the reconstruction support and start image together
  with the SRM. Test with the 288 mm SRM, or the ray-traced one, using:
  - a head-shaped phantom with activity in the scalp;
  - a support taken from a body contour, against a uniform start.
+ *For the current 210 mm SRM,* keep evaluation phantoms at least 2–5 mm inside the
  105 mm edge. The ACR phantom as used in the earlier report fills the support and will
  always streak.
+ *Add Poisson noise* at realistic counts and stop at clinical iteration counts (E4).
  Decide whether the remaining fine rim streaks matter.
+ *Monte Carlo noise in H* (E3) explains the speckle. A ray-traced SRM with stratified
  (deterministic) sampling, or more rays, would give a near noise-free reference for
  separating the two. The one used here still has 7–11% sampling noise in its main
  entries.
+ *Theory:*
  - eigendecompose $H H^top$ (8.3 GB; the spectrum, effective rank, and the share of
    slow components in each phantom);
  - map the diagonal of $R_alpha$ as a per-voxel resolvability;
  - relate streak strength to $N_"eff"$ and the direction tensor, toward the predictive
    metric proposed in the earlier report.
+ *A streak metric that works:* for example matched filtering along the predicted
  voxel-to-pinhole lines, or comparison with a reference reconstruction under clean
  conditions.

= Reproducibility

All scripts are in `dev/python` and run in the `opengate` environment, except
`gammart_srm.py`, which runs in `raytracing`. Every reconstruction uses
`fp_jaszczak_and_recon.py --phantom <npz> --iterations 10 20 50 100 200 --output-dir <dir>`.

#table(
  columns: (auto, 1fr, auto),
  stroke: 0.4pt,
  inset: 4pt,
  [Script], [Purpose], [Output],
  [`sampling_coverage_map.py`], [$N_"eff"$, direction tensor, phantom position scores], [`sampling_brain_merged_123/`],
  [`cold_sphere_phantom.py`], [Cold-sphere phantom at a whole-mm centre], [`cold_sphere_phantom/`],
  [`analyze_cold_sphere_shift.py`], [E2 montages and metrics], [`cold_sphere_phantom/analysis/`],
  [`receiver_coupling_phantoms.py`], [E5 coupling maps and receiver placement], [`receiver_coupling/`],
  [`analyze_receiver_coupling.py`], [E5 analysis], [`receiver_coupling/analysis/`],
  [`ideal_lir.py`], [$R_alpha bold(e)_j$ by CG, against the MLEM LIR], [`ideal_lir/`],
  [`extent_series_phantoms.py`], [E6, E7 and E1b phantoms], [`extent_series/`],
  [`analyze_extent_series.py`], [E6 and E1b montages, streak index (unreliable)], [`extent_series/analysis/`],
  [`analyze_margin_series.py`], [E7 montage (its amplitude metric is unreliable)], [`extent_series/analysis/`],
  [`gammart_srm.py`], [Ray-traced SRM, 2 mm, to 142 mm], [`gammart_srm/brain_2mm_r142.npz`],
  [`gammart_support_test.py`], [Validation against Gate; E8 runs A–E], [`gammart_srm/`],
  [`gammart_support_followup.py`], [E8 runs F–M], [`gammart_srm/`],
)

#v(6pt)
*References.*
H. H. Barrett, D. W. Wilson, B. M. W. Tsui, "Noise properties of the EM algorithm: I.
Theory," _Phys. Med. Biol._ 39:833–846, 1994.
J. A. Fessler, W. L. Rogers, "Spatial resolution properties of penalized-likelihood image
reconstruction," _IEEE Trans. Image Process._ 5(9):1346–1358, 1996.
S. D. Metzler, J. E. Bowsher, R. J. Jaszczak, "Geometrical similarities of the Orlov and
Tuy sampling criteria and a numerical algorithm for assessing sampling completeness,"
_IEEE Trans. Nucl. Sci._ 50(5):1550–1555, 2003.
P. C. Hansen, _Rank-Deficient and Discrete Ill-Posed Problems_, SIAM, 1998.
_Citation details are from memory and should be checked before reuse._
