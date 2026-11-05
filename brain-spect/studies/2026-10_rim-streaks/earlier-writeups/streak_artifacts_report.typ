// Compile from the repository root:
// typst compile streak_artifacts_report.typ

#set document(title: "Streak Artifacts in Stationary Multi-Pinhole Brain SPECT", author: "Fang Han")
#set page(paper: "us-letter", margin: (x: 1.8cm, y: 1.8cm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#show figure.caption: set text(size: 9pt)
#show table.cell.where(y: 0): set text(weight: "bold")

#align(center)[
  #text(size: 17pt, weight: "bold")[Streak Artifacts in Stationary Multi-Pinhole \ Brain SPECT: Problem, Literature, and Next Steps]
  #v(4pt)
  Fang Han · 2026-10-01 · working notes
]

#block(fill: luma(245), inset: 8pt, radius: 3pt)[
  *Summary.* MLEM reconstructions of a hot-background Jaszczak phantom on the 73-module
  brain SPECT system show radial streaks near the edge of the field of view (FOV).
  The data are noiseless and are computed with the same system matrix used for
  reconstruction. The sensitivity map $s = H^T bold(1)$ is smooth and shows no streaks,
  so the streaks cannot be traced to the sensitivity normalisation. Splitting the
  sensitivity by module shows that peripheral voxels draw their counts from fewer
  modules than central ones. This points to angular under-sampling at the edge of the FOV.
  Compared with a blurred copy of the phantom, the reconstruction still shows radial
  streaks near the FOV edge. These are largest in the cold-rod slab, which is sampled
  about as well as the sphere slice but has many more object edges. Many of the
  straight lines visible in the rod slab are real (sector gaps and rod rows), not
  artifacts.
  The mathematics of limited-angle streaks is well established. A per-voxel metric that
  predicts these artifacts for a stationary multi-pinhole system with a realistic
  (Monte Carlo) system matrix and early-stopped MLEM has not been established. That gap
  is the possible research contribution.
]

= Observation

*Setup.* Brain SPECT system with 73 pinhole modules of 25 × 25 pixels each (45,625
detector bins). The system matrix (SRM) $H$ is from Monte Carlo simulation (subdir
`brain_merged_123`) on a 210#super[3] grid of 1 mm voxels and has
1.50 × 10#super[9] non-zero entries. The FOV is a sphere of radius 105 mm (4,944,385
voxels with non-zero sensitivity). A digital Jaszczak phantom with a uniform hot
background and cold spheres was forward projected with $H$ (noiseless, $y = H f$) and
reconstructed with MLEM from a uniform start on the FOV support
(`fp_jaszczak_and_recon.py`, package `mlem_sparse`).

*Artifact.* The axial slice through the spheres (z index 130, z ≈ 25 mm) shows radial
streaks in the background near the edge of the FOV (@fig-iters). They are faint at
iteration 10 and grow with iteration count. A crude measure of background roughness
(standard deviation of voxels > 0.9, which excludes the cold spheres) is shown in
@tab-rough. The outer ring is 1.5–2.7× rougher than the centre at every iteration.

#figure(
  image("figs/recon_axial_z130_iterations.png", width: 100%),
  caption: [Axial slice z index 130 (z ≈ 25 mm) of the MLEM reconstruction at
    iterations 10, 50, 100 and 200, with a shared grey scale of 0.6–1.3 (true background = 1).
    Radial streaks start near the FOV edge and strengthen with iterations.],
) <fig-iters>

#figure(
  table(
    columns: 5,
    align: (left, right, right, right, right),
    [Region], [It. 10], [It. 50], [It. 100], [It. 200],
    [Centre, r < 20 mm], [0.007], [0.017], [0.024], [0.032],
    [Periphery, 75 ≤ r < 95 mm], [0.019], [0.030], [0.038], [0.047],
  ),
  caption: [Standard deviation of the background (true value 1) in slice z index 130.
    Preliminary: the measure mixes streaks with other texture.],
) <tab-rough>

*Cold-rod region: separating structure from artifact.* In the cold-rod slab
(z index 61–71, z ≈ −44 to −34 mm; @fig-rods) the image is full of straight lines.
Most of them are real: the phantom's six rod sectors are separated by hot radial gaps,
and unresolved rows of the hexagonal rod lattice blur into dark bands. To isolate the
artifacts, the reconstruction is compared with the phantom blurred by the 3-D Gaussian
that fits it best inside r < 85 mm (@fig-residual). The best fits at iteration 100
have FWHM 11.2 mm (rods) and 10.0 mm (spheres). The RMS residuals are 0.063 and
0.041 respectively.

The residual shows two kinds of artifact:
+ *Radial streaks of alternating sign, concentrated at the FOV edge.* These are
  strongest on the left and bottom of the rod slab, where large rods and sector gaps
  meet the edge, and also appear at the edge of the sphere slice. They match the
  edge under-sampling hypothesis.
+ *Overshoot rings around spheres and rods.* This is the usual MLEM edge behaviour,
  which a Gaussian blur cannot model. It is not a sampling artifact.

The centre of the FOV has small residuals in both slabs. The rod slab has the larger
residual, consistent with its many more object edges. A single, spatially invariant
Gaussian is a crude reference, however (resolution varies across the FOV), so this
comparison is qualitative.

#figure(
  image("figs/recon_rods_z61-71_iterations.png", width: 100%),
  caption: [Cold-rod slab, mean over z index 61–71, at iterations 10, 20, 50 and 100.
    The colour scale tops out at the 99.5th percentile of each image (arrow on the
    colour bar). The few hot voxels at the FOV boundary would otherwise compress
    everything else into a narrow band. Many straight features are the phantom's
    sector gaps and rod rows, not artifacts; see @fig-residual.],
) <fig-rods>

#figure(
  image("figs/residual_it100.png", width: 100%),
  caption: [Iteration 100 compared with the phantom blurred by the best-fit
    Gaussian. Top: cold-rod slab. Bottom: sphere slice. Right column: residual
    (red = reconstruction too high). Radial streaks remain near the FOV edge after the
    real structure is removed. The rings around spheres and rods are MLEM edge
    overshoot.],
) <fig-residual>

*Display note.* The FOV boundary contains a few voxels with tiny sensitivity (as low
as 1 count). MLEM drives them to very large values, which earlier set the colour
scale (for example a maximum of 43 instead of about 1 in the rod slab, and about 1600
in the full-volume side views). All plotting scripts now clip the colour scale at the
99.5th percentile by default (`--clip_percentile`). The data are unchanged.

= The sensitivity map and why it shows no streaks

*Sensitivity is used.* `SparseMLEMReconstructor` computes $s_j = sum_i H_(i j)$ (a
single pass over the non-zero entries, about 4 s for the whole matrix) and applies the standard update
$x_j <- x_j \/ s_j dot sum_i H_(i j) y_i \/ (H x)_i$. Voxels with $s_j = 0$ are never
updated. Voxels with very small $s_j$ (minimum 1 count) are divided without a floor. That
is a separate issue (hot speckles at the FOV boundary), not the streaks.

*Why the sum hides the problem.* $s_j$ adds counts over every module and every pixel, so
the direction each count came from is lost. Each module on its own is very uneven: it is
bright only near the part of the FOV boundary closest to its pinhole (@fig-coverage,
right). A measure of how many modules contribute comparably to voxel $j$ is the
effective number of modules
$ N_"eff" (j) = 1 \/ sum_m w_(m j)^2, quad w_(m j) = s_(m j) \/ s_j, $
where $s_(m j)$ is the sensitivity from module $m$ alone. Every module records at least one count in almost every voxel
(penetration and scatter in the Monte Carlo SRM), so a plain "non-zero" count says
nothing, and $N_"eff"$ is used instead.

#figure(
  image("figs/coverage_z130.png", width: 100%),
  caption: [Slice z index 130. Left: total sensitivity, smooth with no streaks. Middle:
    effective number of modules, which falls toward the FOV edge. Right: one module
    (head 52), whose sensitivity is concentrated near its own side of the FOV.],
) <fig-coverage>

#figure(
  table(
    columns: 3,
    align: (left, right, right),
    [Radius (mm)], [Spheres, z idx 130], [Rods, z idx 61–71],
    [0–25], [43.6 (41.3)], [44.4 (42.1)],
    [25–50], [39.9 (35.9)], [40.2 (34.1)],
    [50–70], [33.6 (27.5)], [33.8 (24.7)],
    [70–90], [25.8 (17.7)], [26.9 (15.6)],
    [90–105 / 90–100], [18.0 (10.9)], [20.8 (9.2)],
  ),
  caption: [Effective number of modules by radius: median (5th percentile), out of
    73 modules. The two slabs are sampled similarly.],
) <tab-neff>

*Working hypothesis.* Peripheral voxels are dominated by a few nearby pinholes that view
them from a narrow range of directions. MLEM determines such a voxel well across those
directions and poorly along them. Errors therefore spread along the dominant viewing
direction, which is roughly radial at the edge of the FOV. Edges in the object (the
cold spheres and the boundary of the hot background) seed the streaks. Because the data
are consistent, more iterations do not remove them. They can grow, as poorly
determined components drift.

*Not yet excluded.*
+ *Truncation at the FOV boundary.* The hot background reaches the 105 mm sphere, where the model ends.
+ *Monte Carlo noise in $H$.* Each column is a noisy estimate, which affects conditioning even though the data are consistent.
+ *Discretisation and pixelisation* of the phantom edges.
+ *$N_"eff"$ ignores direction.* Two modules on the same side count as two views. It is only a stand-in for angular coverage.

= Literature review <sec-lit>

== Theory: data sufficiency and where streaks appear
- *Orlov (parallel beam) and Tuy (cone beam) conditions* [1] say when a voxel can be recovered exactly from complete, noiseless line integrals. A pinhole is a cone-beam source, so Tuy applies.
- *Microlocal analysis.* Quinto, and Frikel & Quinto [2, 3], explain which edges are reconstructed with limited angles (those tangent to some sampled line). They also show that added streaks lie along lines at the ends of the sampled angular range, through edges of the object. The results are proven for FBP-type inversion, not for iterative methods.
- *Zeng & Gullberg* [4] compared cone-beam artifacts under FBP and iterative EM.

== Pinhole SPECT: per-voxel sampling completeness
- *Metzler, Bowsher & Jaszczak* [5] showed the Orlov and Tuy criteria are geometrically similar and gave a numerical algorithm for per-voxel sampling completeness in pinhole SPECT. This is the closest established relative of ASCI.
- *Helical pinhole SPECT* (Metzler et al.) [6] and *multipinhole helical scan design* (Yao et al.) [7]: circular pinhole orbits leave sampling artifacts, and helical orbits remove them.

== Stationary multi-pinhole brain SPECT
- *AdaptiSPECT-C* (Zeraatkar, King, Furenlid et al.) [8, 9, 10] is the closest system to ours. They assess axial and angular sampling sufficiency (Tuy, Metzler) with XCAT and Defrise phantoms. They find that more angular views and temporally shuttered apertures improve images and reduce multiplexing artifacts. The assessment is mainly by simulation and visual or task-based image quality, not a predictive per-voxel metric.

== Per-voxel image quality for MLEM
- *Local impulse response (LIR) and Fisher information.* Fessler & Rogers [11] (cited from memory, not re-checked) and Vunckx, Nuyts et al. [12] use $F = H^T "diag"(1 \/ macron(y)) H$ to predict each voxel's linearised local impulse response and covariance. The LIR's shape shows which directions are poorly determined. The predictions are for post-smoothed or regularised MLEM, not for early-stopped MLEM. Fisher-matrix methods for pinhole SPECT have been evaluated further [13]. For collimator design methods in general, see the review [14].

== Our prior work
- *Angular Sampling Completeness Index (ASCI)* [15]. It gives, per pixel, the percentage of 360° covered by projection-probability-density-function strips at a chosen strip width (FWHM). It was applied to a 2-D self-collimation SPECT system and correlates with reconstructed resolution.

= What is established and what is open

#table(
  columns: (1fr, 1.4fr),
  align: (left, left),
  [Established], [Open],
  [Exact-reconstruction (yes/no) sampling conditions for ideal line integrals (Orlov, Tuy).],
  [A graded, direction-dependent measure for a finite, blurred system matrix, where
    "complete" becomes a question of conditioning.],

  [Where limited-angle streaks occur for FBP-type inversion (microlocal analysis).],
  [The same prediction for nonlinear, positivity-constrained, *early-stopped* MLEM.],

  [Linearised per-voxel LIR and covariance from Fisher information.],
  [A cheap, map-wide metric that is validated against the LIR and against the streaks
    actually observed, at practical iteration counts.],

  [Fixing sampling by hardware: helical orbits, bed motion, shuttering.],
  [Characterising and predicting the artifacts of a *fixed* stationary design before
    building it, using a realistic Monte Carlo SRM.],
)

Reasons the gap has persisted:
- *The theory answers a yes/no question.* It assumes ideal lines, whereas real pinholes have finite apertures, penetration and multiplexing.
- *Early-stopped MLEM has no closed-form analysis.*
- *Streaks depend on the object*, not only on the system.
- *Full Fisher or singular-value analysis is too expensive* at this scale ($46"k" times 9.3"M"$).
- *Groups have usually changed the hardware* (orbits, bed motion, shutters) instead of building a predictive theory.

= Proposed next steps

+ *Ground truth per voxel (LIR).* For about 20 voxels along a radius in slice 130, compute
  $F e_j = H^T "diag"(1 \/ macron(y)) H e_j$, which costs one forward projection and one
  backprojection each. Measure the anisotropy and principal direction of each LIR. Test
  whether edge voxels stretch radially, along the streaks.
+ *Directional coverage metric (3-D ASCI for pinholes).* For each voxel, weight the
  voxel→pinhole directions (`modules.pinhole_mm` in `geometry_provenance.json`) by the
  per-module sensitivity $s_(m j)$. Compute (a) in-plane angular coverage over 180° at a
  chosen threshold and (b) the eigenvalues of the weighted direction tensor
  $T_j = sum_m w_(m j) bold(u)_(m j) bold(u)_(m j)^T$. Its anisotropy and principal axis
  are a cheap stand-in for the LIR. Then refine using the pixel rows of the SRM instead
  of the pinhole centres.
+ *Rule out the alternatives.*
  + *Truncation:* a phantom whose activity ends well inside the FOV (e.g. a radius of 80 mm).
  + *Noise in $H$:* compare reconstructions using SRMs with fewer simulated events (subsets of the merged batches).
  + *Object dependence:* point and line sources, a Defrise phantom, and a smooth brain phantom.
+ *Quantify the artifacts.* Use a streak index, for example the angular (radial versus
  tangential) power spectrum of the background error in rings. Track it against
  iteration count and correlate it with the metrics from steps 1–2.
+ *Act on the design.* Use the metric to compare module subsets, added rotation
  or tilt steps, or shuttered pinholes. Predict artifact reduction before simulating,
  then verify by reconstruction.
+ *Fix the reconstruction.* Floor $s_j$ (the reconstructor already computes
  `sens_safe` but does not use it) or restrict the support to voxels with adequate
  sensitivity, which removes the hot speckles at the boundary.

= Could this become a paper?

Yes, if it is framed as a *validated predictive metric* and not as another
simulation showing that sampling matters. A plausible contribution:

#block(inset: (left: 10pt))[
  _A per-voxel directional sampling metric for stationary multi-pinhole SPECT, computed
  from a Monte Carlo system matrix, that predicts the location and orientation of
  streak artifacts in MLEM. It is validated against Fisher-information local impulse
  responses and against reconstructions, and applied to design choices._
]

*Strengths of the current setup.*
- *Exact system matrix:* the Monte Carlo SRM is the real system model, not an idealised ray model.
- *Clean test bed:* noiseless, consistent data isolate sampling from noise and model mismatch.
- *Existing tools:* reconstruction, forward projection and geometry provenance are already built.
- *Prior work:* ASCI gives a head start.

*What reviewers will ask for.*
- *Comparison with Metzler's completeness algorithm* and with LIR or Fisher-information methods.
- *Results with noise* (Poisson data), not only noiseless data.
- *More than one phantom and more than one design*, to show the metric generalises.
- *Clear exclusion of truncation and Monte Carlo noise in $H$* as causes.

*Possible venues.* A conference abstract or record first (IEEE NSS/MIC, SNMMI), then a
full paper in _IEEE Transactions on Radiation and Plasma Medical Sciences_, _Physics in
Medicine & Biology_ or _Medical Physics_.

*Before claiming novelty, check:*
- *Barrett & Myers* on null functions and the measurement and null spaces.
- *Interior and truncated tomography* (Defrise, Noo, Clackdoyle, Kudo).
- *Recent AdaptiSPECT-C papers*, the *G-SPECT and U-SPECT* literature, and any 3-D extensions of ASCI.

= References

#set text(size: 9pt)
+ H. K. Tuy, "An inversion formula for cone-beam reconstruction," _SIAM J. Appl. Math._ 43(3):546–552, 1983.
+ J. Frikel and E. T. Quinto, "Characterization and reduction of artifacts in limited angle tomography," _Inverse Problems_ 29:125007, 2013.
+ L. Borg, J. Frikel, J. S. Jørgensen, E. T. Quinto, "Analyzing reconstruction artifacts from arbitrary incomplete X-ray CT data," arXiv:1707.03055 (related: "A paradigm for the characterization of artifacts in tomography," arXiv:1409.4103).
+ G. L. Zeng and G. T. Gullberg, "A study of reconstruction artifacts in cone beam tomography using filtered backprojection and iterative EM algorithms," _IEEE Trans. Nucl. Sci._ 37(2):759–767, 1990.
+ S. D. Metzler, J. E. Bowsher, R. J. Jaszczak, "Geometrical similarities of the Orlov and Tuy sampling criteria and a numerical algorithm for assessing sampling completeness," _IEEE Trans. Nucl. Sci._ 50(5):1550–1555, 2003.
+ S. D. Metzler, K. L. Greer, R. J. Jaszczak, "Helical pinhole SPECT for small-animal imaging: a method for addressing sampling completeness," _IEEE Trans. Nucl. Sci._ 50(5), 2003.
+ R. Yao et al., "Multipinhole SPECT helical scan parameters and imaging volume," _Med. Phys._ 42(11), 2015. doi:10.1118/1.4933421
+ N. Zeraatkar et al., "Preliminary investigation of axial and angular sampling in multi-pinhole AdaptiSPECT-C with XCAT phantoms," IEEE NSS/MIC, 2018.
+ "Investigation of axial and angular sampling in multi-detector pinhole-SPECT brain imaging," PubMed 32763850, 2020.
+ N. Zeraatkar et al., "Improvement in sampling and modulation of multiplexing with temporal shuttering of adaptable apertures in a brain-dedicated multi-pinhole SPECT system," PMC9893699.
+ J. A. Fessler and W. L. Rogers, "Spatial resolution properties of penalized-likelihood image reconstruction: space-invariant tomographs," _IEEE Trans. Image Process._ 5(9), 1996.
+ K. Vunckx, D. Bequé, M. Defrise, J. Nuyts, "Single and multipinhole collimator design evaluation method for small animal SPECT," _IEEE Trans. Med. Imaging_ 27(1), 2008.
+ "Evaluation of Fisher information matrix-based methods for fast assessment of image quality in pinhole SPECT," _IEEE Trans. Med. Imaging_, 2015.
+ K. Van Audenhaege et al., "Review of SPECT collimator selection, optimization, and fabrication for clinical and preclinical imaging," _Med. Phys._ 42(8):4796–4813, 2015.
+ F. Han, H. Tripathi, T. Methuku, T. Ma, R. Yao, "Angular sampling completeness index and width of projection probability density function strips as spatial resolution metrics in self-collimation single photon emission tomography," _J. Nucl. Med._ 66(suppl. 1):251903, 2025.

#text(size: 8.5pt, style: "italic")[References 3, 6, 9, 11 and 13 have incomplete or
unverified details (authors, volume, year) and should be checked before reuse.]
