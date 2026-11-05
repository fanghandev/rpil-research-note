// Compile from the repository root:
// typst compile brain_288mm_srm_production_study.typ
// Numbers in the statistics section are read from brain_288mm_srm_stats.json
// (dev/python/report/brain_288mm_srm_stats.py).

#set document(title: "Brain SPECT: SRM Production for a 288 mm Field of View", author: "Fang Han")
#set page(paper: "us-letter", margin: (x: 1.9cm, y: 1.9cm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#show figure.caption: set text(size: 9pt)
#show table.cell.where(y: 0): set text(weight: "bold")
#show table: set par(justify: false)
#show link: set text(fill: rgb("#1f4e9c"))

#let stats = json("brain_288mm_srm_stats.json")
#let fixed(x, d) = {
  let s = str(calc.round(x, digits: d))
  if d == 0 { return s }
  if not s.contains(".") { s += "." }
  let have = s.split(".").at(1).len()
  s + "0" * (d - have)
}
#let sci(x, digits: 3) = {
  let e = calc.floor(calc.log(x, base: 10))
  let m = x / calc.pow(10.0, e)
  if calc.round(m, digits: digits - 1) >= 10 { e += 1; m /= 10 }
  [#fixed(m, digits - 1) × 10#super[#str(e)]]
}
#let group(n) = {
  let s = str(int(calc.round(n)))
  let out = ""
  for (i, c) in s.clusters().enumerate() {
    if i > 0 and calc.rem(s.len() - i, 3) == 0 { out += "," }
    out += c
  }
  out
}
#let pending(body) = block(
  fill: rgb("#fff4d6"), stroke: (left: 2pt + rgb("#c98a00")), inset: 8pt, width: 100%, body,
)

#align(center)[
  #text(size: 17pt, weight: "bold")[Brain SPECT: System Response Matrix Production \ for a 288 mm Field of View]
  #v(4pt)
  Fang Han · 2026-10-05 · repository commit `773b819` (branch `brain-288mm-csg-production`)
]

#v(6pt)
#block(inset: (x: 1.2cm))[
  #set text(size: 9.5pt)
  *Summary.*
  We extend the Monte Carlo (MC) system response matrix (SRM) of a 73-pinhole brain
  SPECT system from a 210 mm to a 288 mm spherical field of view (FOV), the largest
  centred sphere that clears all hardware (289.14 mm). At the cost of the previous
  campaigns, the required statistics would take about 5.6 M core-hours; the available
  allocation is 0.75 M. Profiling shows that the cost is dominated by the faceted lead
  shield (an STL mesh of 186,772 facets) and by 73 per-module digitizer chains, not by
  the pixelated crystals. We replace the STL with an analytic constructive solid
  geometry (CSG) model whose parameters are measured from the STL, verify it
  geometrically and physically (crystal counts agree with the STL to +0.08 %), and merge
  the digitizer chains (identical singles). On the SDSC Expanse cluster this is 4.3×
  faster than the previous configuration. A further ≈3.3× comes from running one
  Gate process per NUMA domain; this is indicated by one test job and is being
  validated. With both, the full target of 1.0 × 10#super[14] primaries is projected at
  ≈0.47 M core-hours. The campaign is run in ten equal parts, each a complete SRM, and
  its size is corrected after the first two parts from the measured statistics.
]

#outline(depth: 2, indent: 1.2em)

= System and simulation model

The system has 73 pinhole modules in 7 rings with 10, 13, 18, 15, 11, 5 and 1 modules at
elevations −37°, −16°, 4.5°, 25°, 45.5°, 67° and 90°. The pinholes lie on a sphere of
radius 149.61 mm; the collimator nozzle tips reach r = 144.57 mm. Each module has a
50 × 50 × 10 mm CsI crystal, 25 mm behind the pinhole, divided into 25 × 25 pixels of
2 mm. The square back bore accepts a pyramid of 45° half-angle. Modules use four pinhole
diameters (0.556, 0.797, 1.215 and 2.007 mm), assigned in order: module $n$ (1-based)
uses variant $(n - 1) mod 4$. A lead shield (spherical shell, r = 145–155 mm, with a face
window and one aperture per module) surrounds the collimators.

Simulations use Gate 10 (opengate 10.1.0 in the production container, 10.1.1 on the
workstation; Geant4 multithreaded). The source emits 140 keV photons uniformly in the
FOV sphere. An SRM element is the number of accepted singles (energy window
126–154 keV) in a detector pixel from a source voxel, divided by the primaries emitted
in that voxel; SRMs are stored per module as sparse matrices (625 pixel rows × FOV
voxels) at 1 mm and 2 mm voxel size.

= Field of view <fov>

*Method.* `dev/python/brain_spect_max_fov.py` evaluates, on a 2 mm grid, how many modules
see each point: a straight ray from the point through the pinhole centre must land on the
crystal, within the bore's acceptance, without crossing the shield (voxelized exactly at
1 mm) or another module's collimator envelope. Points inside solid material are flagged.
Septal penetration is ignored, so this is the geometric detectable region.

*Result.* The largest centred sphere free of hardware is limited by the nozzle tips:
D = 2 × 144.57 = 289.14 mm. We use *D = 288 mm*. Every point within r ≈ 105 mm
(D = 211.6 mm, i.e. the previous 210 mm FOV) is seen by all 73 modules. Beyond that, the
coverage falls to a minimum of 24 modules and a mean of 43 near r = 143 mm, and the mean
geometric sensitivity to 0.38 of the centre (@fig-fov). Every point of the 288 mm sphere
is seen by at least 24 modules, so the whole sphere is reconstructable. An interactive 3D
check of the 288 mm sphere against the hardware is in
`dev/python/brain_fov_analysis/brain_fov_3d_overlap_check.html`, and Geant4's overlap
check of the 288 mm source volume reports no overlap.

#figure(
  image("figs/brain_fov_coverage_slices.png", width: 100%),
  caption: [Number of modules that see each point. Black dashed: previous 210 mm FOV;
    orange: largest hardware-free centred sphere (289.1 mm); red: region seen by all 73
    modules.],
) <fig-fov-slices>

#figure(
  image("figs/brain_fov_radial_profile.png", width: 100%),
  caption: [Coverage (mean and minimum number of modules) and mean geometric sensitivity
    on spherical shells. Dashed: r = 105 mm; orange: r = 144.57 mm (nozzle tips).],
) <fig-fov>

= Simulation cost

== Method

Cost is reported as wall time per primary per thread. Each configuration runs at two
sizes with the same seed, and the cost is the slope Δt/ΔN, so start-up (geometry
construction, physics tables, file setup) cancels. Workstation runs use an AMD
Threadripper PRO 3995WX (Zen 2, the same micro-architecture as the Expanse EPYC 7742),
64 threads pinned to physical cores, one simulation at a time (concurrent runs inflated
the per-primary cost ≈8×).

== Where the time goes (workstation)

- *Pixelated crystals:* replacing the 25 × 25 pixel repeater by one pixel changes the
  cost by 2 % (1.02$times$). The repeater is not the bottleneck.
- *Lead shield STL:* dominates, and much more under multithreading (cache-bound). With
  per-module actors at 64 threads: full STL 518 µs; merged actors and a 0.05 mm
  simplified STL 24–33 µs.
- *Digitizer:* 73 × 3 per-module actor chains replaced by one merged chain writing one
  tree (`--actor-layout merged`) gives identical singles and is ≈2.4× faster at 64
  threads.
- *With and without the shield* (@tab-noshield): with merged actors, removing the shield
  entirely gives 10.8 µs per primary per thread; the CSG shield gives ≈10 µs, i.e. no
  measurable cost, whereas the full STL adds ≈420 µs (40× the rest of the simulation)
  and even the simplified STL adds ≈22 µs (3×).
- *Rejected:* splitting the STL into pieces created stuck tracks at the cut faces
  (`GeomNav1002`) and lost ≈0.45 % of singles. Biasing the emission direction was not
  considered because the 73 modules cover most of 4π.

#figure(
  table(
    columns: 3,
    align: (left, right, right),
    [Shield], [per-module actors (µs)], [merged actors (µs)],
    [full STL (186,772 facets)], [518], [434],
    [STL simplified to 0.05 mm], [77.5], [32.6],
    [CSG tiles], [–], [≈10#super[d]],
    [no shield], [–], [10.8],
  ),
  caption: [Full production simulation (73 modules, 25 × 25 pixels, digitizer, 140 keV
    source in a 210 mm sphere) on the workstation, 64 threads: cost per primary per thread from the slope between
    two run sizes (2 × 10#super[5] and 6 × 10#super[5] primaries per thread for the full
    STL, 2 × 10#super[5] and 2 × 10#super[6] otherwise). #super[d] Measured separately
    with the same method (12 µs inside the production container). No shield-free run
    was made with per-module actors or on Expanse.],
) <tab-noshield>

= Analytic (CSG) lead shield

== Model and parameter extraction

The STL is described almost exactly by Geant4 primitives (@tab-csg). Parameters were
measured on the STL in the simulation frame:

- *Shell and cuts.* Vertex radii span exactly 145.0000–155.0000 mm. Facets whose plane
  contains the centre are cuts expressible by `G4Sphere` angles; their vertices give the
  window azimuths (zero spread) and elevations, and the bottom cut at
  −46.9964 ± 0.0091°.
- *Apertures.* For each module a 70 × 70 mm patch was voxelized at 0.05–0.1 mm in the
  module frame and the open square measured at depths −3.4 to +4.6 mm. All 72 ring
  apertures give the same law (residual ≤ 0.05 mm, the voxel size). The top aperture
  fits the same law after a 2.5° in-plane rotation.
- *Rounds.* Circle fits to sections perpendicular to each edge: 4.73 mm on inner edges,
  6.0 mm at window corners, 14.0 mm at the two window–bottom junctions. These are an
  optional patch in the manifold3d model only; they cannot yet be built in Gate 10
  (@limits).

#figure(
  table(
    columns: (auto, 1fr),
    align: (left, left),
    [Part], [Definition (world frame; azimuth from +x toward +y, 90° = face window)],
    [Shell], [r = 145.0–155.0 mm, elevation ≥ −47.0°],
    [Face window, upper], [azimuth 56.25–123.75°, elevation −26.5 to −5.75°],
    [Face window, lower], [azimuth 50.524–129.476°, elevation −47.0 to −26.5°],
    [Aperture (×73)], [module frame (z from the pinhole toward the centre): square of width
      27.528 − 1.5861 z mm for z ≤ 3.8 mm (`G4Trd`), then a 21.65 mm square lip
      (`G4Box`) through the inner surface; top aperture rotated 2.5°],
    [Rounds (optional)], [4.73 mm inner edges; 6.0 mm window corners; 14.0 mm window–bottom junctions],
  ),
  caption: [CSG shield parameters (`payload/python/brain_spect_shield_csg.py`, `SHIELD_CSG`).
    The window edges at −26.5° and −5.75° are the midpoints between the first three rings.],
) <tab-csg>

== Geometric comparison with the STL

Both solids are built in manifold3d (double precision; spheres with 720 segments) and
compared by exact boolean differences, an exact signed surface distance (every triangle
sampled at ≤ 0.5 mm, candidate triangles tested exactly), and radial lead-thickness maps
(ray casting on a 0.25° grid).

#figure(
  table(
    columns: 4,
    align: (left, right, right, right),
    [], [STL], [CSG sharp], [CSG rounded],
    [Volume (cm³)], [1721.62], [1722.73 (+1.11)], [1718.26 (−3.37)],
    [STL − CSG: sphere-facet film / other (cm³)], [], [20.75 / 1.47], [21.19 / 1.14],
    [CSG − STL: sphere-facet film / other (cm³)], [], [22.87 / 0.46], [18.50 / 0.46],
    [Directions with radial thickness differing by > 0.5 mm], [], [1.17 %], [0.30 %],
    [STL vertex to CSG surface: max (99.9th pct) (mm)], [], [3.36 (1.63)], [1.05 (0.55)],
  ),
  caption: [STL vs CSG. The largest differences are thin films over the spherical
    surfaces: the STL's flat facets lie up to 0.22 mm inside the true spheres, so the
    films measure the STL's faceting, not a CSG error.],
) <tab-geo>

Apart from the films, each aperture has the same small residual (≈15 mm³ only in the STL:
hole-corner fillets and a lip chamfer; ≈6 mm³ only in the CSG). The largest
non-film pieces are at the window corners (missing rounds, up to 74 mm³). Per-aperture
comparison pages (horizontal and vertical cuts, 12 slices perpendicular to each aperture
axis with its collimator) are in `dev/python/brain_shield_csg_comparison/apertures.pdf`.

#figure(
  image("figs/whole_thickness_maps.png", width: 100%),
  caption: [Radial lead thickness (r = 140–160 mm) of the STL (top) and the sharp CSG
    (middle), and their difference (bottom). Differences are confined to aperture rims
    and window corners.],
) <fig-thick>

#figure(
  image("figs/aperture_summary.png", width: 100%),
  caption: [Per-aperture residual volume excluding the sphere-facet films (top) and
    distance of STL vertices near each aperture to the CSG surface (bottom). The outliers
    (apertures 1, 10, 23, 25, 39, 40) border the face window and its rounded corners.],
) <fig-ap>

== Implementation in Gate 10

`add_csg_shield_to_gate_sim(sim, pl_df, layout="tiles")` builds 73 tiles: for each module,
a `G4Sphere` segment between the mid-azimuths to its neighbours and the mid-elevations to
the adjacent rings, minus that aperture (`G4Trd` ∪ `G4Box`). The window is where no tile is
placed. Each tile is a small boolean with a small bounding box. (The alternative, one
sphere minus two window segments minus 73 apertures, is 50× slower; @tab-bench.) opengate
passes a boolean's rotation to Geant4 as a passive rotation, so a component placed with
rotation $R$ is given $R^T$; this was verified by sampling surface points.

*Validation in Geant4.* Surface points (`GetPointOnSurface`) of the tiles lie on the
manifold3d CSG surface within 0.004 mm (points off it lie on internal tile boundaries
inside the lead). Geant4's volume estimate is 1723.9 cm³ (≈0.1 % MC noise) vs 1722.7 cm³.
`CheckOverlaps` reports no overlaps between tiles or with the 73 collimators, and no
`G4Exception` occurred in any run.

== Physics and timing benchmark

`dev/python/benchmark_brain_shield_models.py`, workstation, 64 threads.

*Shield-only scene:* shield plus a CsI dome detector at r = 160–170 mm (elevation
≥ −50°, so it also sees the window and bottom edges). *Production-like scene:* shield,
73 collimators and 73 crystals. Both use a uniform source in a 210 mm sphere for timing.
Counts are compared with the same seed (paired), which makes per-module differences far
smaller than independent Poisson noise.

#figure(
  table(
    columns: 3,
    align: (left, right, right),
    [Shield model], [shield only (µs)], [production-like (µs)],
    [STL, 186,772 facets], [329], [403],
    [STL simplified to 0.05 mm (previous production)], [23.8], [29.8],
    [CSG, single boolean], [96], [–],
    [CSG, 73 tiles], [≈2#super[a]], [9.0],
  ),
  caption: [Cost per primary per thread, 64 threads. #super[a] At the noise floor of the
    run sizes used.],
) <tab-bench>

#figure(
  table(
    columns: 5,
    align: (left, right, right, right, right),
    [Shield], [unscattered / primary], [photopeak / primary], [vs STL], [per module (std / max)],
    [STL], [5.6616e−4], [5.6898e−4], [], [],
    [STL simplified 0.05 mm], [5.6614e−4], [5.6896e−4], [−0.003 %], [0.08 % / 0.33 %],
    [CSG tiles], [5.6663e−4], [5.6943e−4], [+0.08 %], [0.77 % / 3.3 %],
  ),
  caption: [Photons entering the 73 crystals in the production-like scene, 1.28 × 10#super[8]
    primaries per model, same seed. About 990 photons per module per run.],
) <tab-phys>

In the shield-only scene the CSG passes 2.0 % more unscattered photons through the
apertures (the STL's lip opening is ≈0.08 mm narrower at the 99th percentile: fillets and
chamfer) and 0.14 % fewer at the window and bottom edges (missing rounds); scattered-photon
maps agree within noise. With the collimators in place, the collimators define the
acceptance and the total photopeak flux into the crystals agrees to +0.08 %.

*Conclusion.* The tiled CSG reproduces the STL's effect on the crystals to < 0.1 % in total
and costs 9 µs instead of 29.8 µs (simplified STL) or 403 µs (full STL) in the
production-like scene.

= Performance on SDSC Expanse <expanse>

== A/B benchmark

Configurations were run on Expanse at the production settings (127 threads, shared
partition, 288 mm FOV, 6.25 × 10#super[6] Bq for 1 s per chunk), each at 2 and 8 chunks
per job; cost is the slope (stamp `20261002T175708Z`;
`submit_slurm/launch_brain_expanse_shield_ab_benchmark.sh`,
`analyze_brain_shield_ab_benchmark.py`).

#figure(
  table(
    columns: 3,
    align: (left, right, right),
    [Configuration], [µs per primary per thread], [node throughput vs previous],
    [previous: per-module actors + full STL], [217], [1×],
    [merged actors + simplified STL], [55.9], [3.9×],
    [merged actors + CSG tiles, one Gate process], [50.6], [4.3×],
    [merged actors + CSG, 8 processes × 16 threads, `numactl`-pinned#super[b]], [≈15], [≈13×],
  ),
  caption: [Expanse benchmark. #super[b] One hand-written test job (54591702), not the
    two-size slope and not the production wrapper; see @sec-numa-status.],
) <tab-expanse>

The CSG gain on Expanse (4.3×) is far smaller than on the workstation, although the same
configuration runs at 10 µs on the workstation (12 µs inside the production container,
so the container is not the cause).

== NUMA effect

An Expanse node has two EPYC 7742 sockets configured as 8 NUMA domains of 16 cores. In a
Geant4 multithreaded process the master thread builds the geometry and physics tables
shared by all workers; with Linux first-touch allocation they reside in the master's
domain, and ≈111 of 127 workers read them across the inter-domain fabric at every step.
Photon transport is latency-bound (navigation and cross-section lookups), so once the CSG
makes geometry cheap, remote memory access dominates. The workstation is a single NUMA
domain and does not show the effect. Running one Gate process per domain, bound to its
cores and memory (`numactl --physcpubind --membind`), keeps all reads local, at the price
of 8 copies of the tables and 8 start-ups. *This explanation is consistent with the
measurements but has not been confirmed with hardware counters* (`numastat`, `perf`).

The production wrapper implements this split (`submit_slurm/numa_layout.py`,
`run_parallel_commands.sh`, `wrapper_brain_spect_sim_slurm.sh`, `NUMA_SPLIT=auto`): per
loop, one pinned Gate process per NUMA group (7 × 16 + 1 × 15 threads in a 127-CPU job),
each with its own seed and output folder; a loop fails if any process fails. It was tested
locally in the production container (forced split into 4 groups on the workstation):
correct CPU and memory binding of each process, distinct seeds, all outputs converted,
primaries in the combined SRM equal to the sum over processes, detection rate split vs
unsplit 358.5 ± 2.2 vs 363.0 ± 2.2 counts per 10#super[6] primaries (−1.5σ), correct
handling of an injected failure and of termination.

== Status <sec-numa-status>

#pending[
  *Pending validation.* The NUMA-split workflow has not yet run on Expanse. The validation
  benchmark (two-size slope; jobs 54678357 and 54678359, stamp `20261005T150124Z`) is
  queued behind the Expanse maintenance of 2026-10-05. Its result replaces the ≈15 µs
  figure, the per-loop cost and the projections in @sec-campaign.
]

Stuck tracks: the CSG run had 3 `GeomNav1002` warnings in 6.35 × 10#super[9] primaries,
all on a tile's inner surface next to an aperture lip (Geant4 moves the photon on);
≈5 × 10#super[−10] per primary, negligible for the SRM.

= Statistical target <stats>

== What other systems do

We found no commonly quoted target for counts per SRM element. Calibrated preclinical
pinhole systems measure a point source on a coarse grid and fit each projected response
with a parametric (e.g. 2D Gaussian) model, which removes counting noise and is
interpolated to the full voxel grid @vanderhave2008 @han2017. Clinical systems use
analytic or hybrid collimator-response models. Fully MC SRMs are noisy, and published work
reduces the noise with symmetries @rafecas2004, filtering @lazaro2005, or hybrid models;
an MC SRM for pinhole SPECT gave lower SNR than analytic and measured SRMs @aguiar2014.
The one fully 3D MC SPECT SRM with quoted statistics @lazaro2005 detected about 60 counts
per source voxel (7.5 × 10#super[10] primaries, 1.6 × 10#super[7] detected, 64#super[3]
grid of 3.125 mm), i.e. well below one count per element on average; increasing the
statistics from 10#super[9] to 10#super[10] primaries reduced mislocated activity from
24.9 % to 7.7 % and PCA filtering of the matrix reduced it further to 1.7 %. A literature
threshold therefore cannot set our target; it must come from our own reconstructions.

== Statistics of the 210 mm SRM

#let v = stats.variants
#let c1 = stats.variant0_centre_cores.at("1mm")
#let c2 = stats.variant0_centre_cores.at("2mm")
#let t = stats.target_288
The 210 mm merged SRM (`brain_merged_123`) has #sci(stats.simulated_primaries) primaries.
Counts per pixel (row sums of the SRM) depend only on the pinhole variant and the pixel
position (@tab-var, @fig-maps): within a variant, the module-to-module spread of the central
counts is below 0.1 %. The position dependence is explained by the incidence angle θ of
the pixel centre (ray from the pinhole to the pixel centre at 27 mm depth, i.e. ≈2 mm into
the crystal) and is nearly the same for all variants (@fig-theta).

#figure(
  table(
    columns: 5,
    align: (left, right, right, right, right),
    [Pinhole (mm)], [modules], [centre 3×3 counts per pixel], [range over modules], [module CV],
    ..v.map(r => (
      [#fixed(r.pinhole_mm, 3)], [#r.heads], [#group(r.centre3x3_counts_mean)],
      [#group(r.centre3x3_counts_min)–#group(r.centre3x3_counts_max)],
      [#fixed(100 * r.head_to_head_cv, 2) %],
    )).flatten(),
  ),
  caption: [Counts per central pixel in the 210 mm SRM, by pinhole variant.],
) <tab-var>

#figure(
  image("figs/brain_pixel_count_maps.png", width: 100%),
  caption: [Mean counts per pixel for each pinhole variant. White contours: θ = 30°
    (solid) and 35° (dashed).],
) <fig-maps>

#figure(
  image("figs/brain_pixel_counts_theta.png", width: 80%),
  caption: [Pixel counts relative to the central 3 × 3 pixels vs incidence angle, averaged
    over the modules of each variant. Dashed: θ = 30° and 35°.],
) <fig-theta>

*Central pixels.* We define the central region of a crystal by the incidence angle, which
(unlike a square ring) is what sets the counts: θ ≤ 30° contains
#stats.central_pixel_counts.theta_le_30 pixels with at least ≈35 % of the central counts;
θ ≤ 35° contains #stats.central_pixel_counts.theta_le_35 pixels with at least ≈20 %.
Beyond 45° counts fall below 2 % (the bore's acceptance).

*Per-element statistics.* For each SRM row we define its core as the fewest voxels holding
half of the row's counts. For the central 3 × 3 pixels of the smallest-pinhole (0.556 mm)
modules (#c1.rows rows), the median core is #group(c1.core_voxels_median) voxels with
#fixed(c1.core_counts_per_voxel_median, 1) counts each at 1 mm (relative noise
#fixed(100 * c1.core_relative_noise_median, 0) %), and #group(c2.core_voxels_median)
voxels with #fixed(c2.core_counts_per_voxel_median, 1) counts each at 2 mm
(#fixed(100 * c2.core_relative_noise_median, 0) %). The other variants have 1.6–6.7× more
counts.

*Scaling to 288 mm.* The full 288 mm target (#sci(t.primaries, digits: 2) primaries) has
#fixed(t.density_ratio_vs_210, 2)× the emission density of the 210 mm SRM. Counts from
the inner 210 mm sphere scale by this ratio: ≈#group(t.variant0_centre_counts_from_210_sphere)
per central pixel of a 0.556 mm module, and ≈#fixed(c1.core_counts_per_voxel_median * t.density_ratio_vs_210, 0)
(1 mm) or ≈#fixed(c2.core_counts_per_voxel_median * t.density_ratio_vs_210, 0) (2 mm)
counts per core voxel. The 210–288 mm shell adds further counts, which will be measured
from the first campaign parts.

= Campaign plan <sec-campaign>

#figure(
  table(
    columns: 2,
    align: (left, left),
    [Item], [Value],
    [Part], [64 tasks (one 127-CPU node each) × 5 loops × 40 chunks × 7.9375 × 10#super[8] = 1.016 × 10#super[13] primaries],
    [Full target], [10 parts = 1.016 × 10#super[14] primaries (3.1× the emission density of the 210 mm SRM)],
    [Settings], [288 mm FOV, CSG tiles, merged digitizer, `NUMA_SPLIT=auto`, no per-loop overlap check],
    [Projected cost#super[c]], [≈47 k core-hours per part; ≈0.47 M for the target (one process per node: ≈1.45 M; previous configuration: ≈5.6 M)],
    [Allocation], [0.75 M core-hours],
  ),
  caption: [288 mm campaign. #super[c] From the ≈15 µs NUMA-split figure, pending
    validation (@sec-numa-status).],
) <tab-campaign>

Every part is a complete SRM and parts combine by summation, so the campaign can stop
after any part. Because no published per-element target exists, the plan is to aim with
the full target and correct after measuring:

+ Validate the NUMA-split cost on Expanse (≈30 core-hours); set the per-loop cost.
+ Run parts 1–2 (2.0 × 10#super[13] primaries, ≈10 % of the budget at the projected cost).
+ Merge them and measure the central-pixel and core-voxel counts over the full 288 mm FOV.
  Split the merged SRM into fractions (1, ½, ¼, ⅛) and reconstruct the same phantom
  (independent projection data) with each, to find where contrast recovery and noise stop
  improving. Also test a denoised SRM (e.g. a fitted or smoothed response per pixel,
  exploiting the < 0.1 % variation between modules of a variant).
+ Continue, stop, or redistribute the remaining parts based on step 3; re-check at ≈50 %.

= Limitations and open items <limits>

- *NUMA split* is validated locally but not yet on Expanse (@sec-numa-status); the
  mechanism is inferred, not measured with hardware counters.
- *Rounds and aperture details.* The rounds need `G4Torus` and polycone or extruded
  solids that opengate does not expose; the aperture fillets and lip chamfer
  (≈15 mm³ per aperture) are not modelled. Their effect on crystal counts is < 0.1 % in
  total and up to 3.3 % for one module in paired runs.
- *SRM-level check.* CSG and STL were compared by crystal counts, not SRM rows per
  voxel. The 288 mm CSG campaign is kept separate from the STL-based 210 mm SRMs; they
  should not be merged without that check.
- *CSG tile timing* in the shield-only scene (≈2 µs) is at the noise floor of the run
  sizes used.
- *Statistics target.* The scaling in @stats covers the inner 210 mm sphere only; the
  outer shell and the reconstruction-based threshold come from parts 1–2.

= Reproducibility

#table(
  columns: (auto, 1fr),
  align: (left, left),
  [Topic], [Code and outputs (repository paths)],
  [FOV], [`dev/python/brain_spect_max_fov.py`, `plot_brain_spect_max_fov.py`, `plot_brain_spect_fov_3d.py`; `dev/python/brain_fov_analysis/`],
  [CSG model, comparison], [`payload/python/brain_spect_shield_csg.py`; `dev/python/brain_shield_csg.py`, `plot_brain_shield_csg_vs_stl.py [--rounded]`; `dev/python/brain_shield_csg_comparison[_rounded]/`],
  [Benchmarks], [`dev/python/benchmark_brain_shield_models.py`; `submit_slurm/launch_brain_expanse_shield_ab_benchmark.sh`, `analyze_brain_shield_ab_benchmark.py`],
  [Production], [`payload/python/gate_sim_brain_spect_boolean.py` (`--shield-model csg --actor-layout merged`); `submit_slurm/run_brain_expanse_127_production.sh`, `launch_brain_expanse_127_production_remote.sh`, `numa_layout.py`, `run_parallel_commands.sh`],
  [Statistics], [`dev/python/report/brain_288mm_srm_stats.py` → `brain_288mm_srm_stats.json`, `figs/`],
  [Notes], [`dev/python/brain_shield_csg.md` (full working notes)],
)

#bibliography("brain_288mm_refs.yml", title: "References", style: "ieee")
