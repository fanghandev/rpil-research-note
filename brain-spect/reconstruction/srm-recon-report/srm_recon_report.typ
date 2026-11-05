// Figures: full-resolution PNGs in figs/ (the originals). build.sh compiles the PDF from
// re-encoded copies: typst compile --input figdir=_build/figs --input ext=.jpg …
#let figdir = sys.inputs.at("figdir", default: "figs")
#let ext = sys.inputs.at("ext", default: ".png")

// Compile from the repository root:
// typst compile srm_recon_report.typ

#set document(title: "Cardiac and Brain SPECT: SRMs and Phantom Reconstructions", author: "Fang Han")
#set page(paper: "us-letter", margin: (x: 1.8cm, y: 1.8cm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#show figure.caption: set text(size: 9pt)
#show table.cell.where(y: 0): set text(weight: "bold")

#let stats = json("brain_srm_stats.json")
// fixed number of decimals, keeping trailing zeros
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
  // thousands separators for integers
  let s = str(n)
  let out = ""
  for (i, c) in s.clusters().enumerate() {
    if i > 0 and calc.rem(s.len() - i, 3) == 0 { out += "," }
    out += c
  }
  out
}
#let pad2(i) = if i < 10 { "0" + str(i) } else { str(i) }

#align(center)[
  #text(size: 17pt, weight: "bold")[Cardiac and Brain SPECT: \ SRMs and Phantom Reconstructions]
  #v(4pt)
  Fang Han · 2026-09-25
]

All reconstructions below use MLEM on *noiseless* projections computed with the same
SRM that is used for reconstruction. They test the SRM and the angular sampling. They
do not measure image quality under realistic noise.

= Cardiac SPECT: ACR Jaszczak reconstruction

A digital ACR Jaszczak phantom with a hot background was forward projected through 20
cardiac modules (heads 41–60) and reconstructed with MLEM on a 210#super[3] grid of
1 mm voxels. Heads 41–60 lie on a single partial ring around the FOV. The phantom
contains cold spheres (9.5–31.8 mm diameter, at z ≈ 22 mm) and six sectors of cold
rods (4.8–12.7 mm diameter, from z ≈ −105 to −17 mm).

#figure(
  image(figdir + "/cardiac_jaszczak_reconstruction_iteration_100_x0-210_y0-210_z71-81" + ext, width: 100%),
  caption: [Cardiac system, 20 modules, MLEM iteration 100. Left: sum over the rod
    slab z ∈ [−34, −24] mm. Middle and right: sums over the full y and x ranges.],
)

#pagebreak()

= Brain SPECT

The brain system has 73 pinhole modules in 7 rings (10, 13, 18, 15, 11, 5 and 1 modules
at elevations of −37°, −16°, 4.5°, 25°, 45.5°, 67° and 90°). Each module has a
50 × 50 × 10 mm crystal divided into 25 × 25 pixels. The modules use four pinhole
diameters (0.556, 0.797, 1.215 and 2.007 mm), assigned in order: head $n$ uses
pinhole $(n - 1) mod 4$. The SRMs come from the merged campaign `brain_merged_123`.

== SRM statistics

The simulation emits 140 keV gammas uniformly from a 210 mm diameter spherical FOV.
Raw singles are all crystal hits. Accepted singles are the hits inside the energy
window (default 126–154 keV, 20 % around 140 keV) and inside the SRM grid. Accepted
singles are the entries of the SRM. Sensitivity is accepted singles divided by
primaries.

#figure(
  table(
    columns: 5,
    align: (left, right, right, right, right),
    stroke: 0.4pt,
    [Campaign], [Jobs], [Primaries], [Raw singles], [Accepted singles],
    ..stats.campaigns
      .map(c => (
        raw(c.name),
        str(c.inputs),
        sci(c.primaries),
        sci(c.raw),
        sci(c.accepted),
      ))
      .flatten(),
    table.hline(stroke: 0.8pt),
    [*Total*], [*#stats.inputs*], [*#sci(stats.primaries)*], [*#sci(stats.raw)*], [*#sci(stats.accepted)*],
  ),
  caption: [Simulation totals. System sensitivity (all 73 heads):
    #sci(stats.accepted / stats.primaries). Non-zero SRM entries at 1 mm
    (45,625 × 9,261,000 system matrix): #sci(stats.nnz_total).],
)

#let variant-rows = (0.556, 0.797, 1.215, 2.007).map(w => {
  let hs = stats.heads.filter(h => h.pinhole == w)
  let mean = hs.map(h => h.sens).sum() / hs.len()
  let base = stats.heads.filter(h => h.pinhole == 0.556).map(h => h.sens).sum() / stats.heads.filter(h => h.pinhole == 0.556).len()
  (str(w), str(hs.len()), sci(mean), fixed(mean / base, 2))
})

#figure(
  table(
    columns: 4,
    align: center,
    stroke: 0.4pt,
    [Pinhole (mm)], [Heads], [Mean sensitivity per head], [Relative],
    ..variant-rows.flatten(),
  ),
  caption: [Sensitivity by pinhole size. It grows less than the aperture area
    (13× from 0.556 to 2.007 mm), consistent with penetration through the
    aperture edge.],
)

#let head-table(hs) = table(
  columns: 5,
  align: (center, center, center, right, right),
  stroke: 0.3pt,
  inset: 3pt,
  [Head], [Ring], [Pinhole], [Accepted], [Sensitivity],
  ..hs.map(h => (str(h.head), str(h.ring), str(h.pinhole), group(h.counts), sci(h.sens))).flatten(),
)

#figure(
  text(size: 7.5pt, grid(
    columns: 2,
    column-gutter: 10pt,
    head-table(stats.heads.slice(0, 37)),
    head-table(stats.heads.slice(37)),
  )),
  caption: [Per-head statistics (1 mm SRM). Pinhole diameters in mm.],
)

== Per-head SRM plots

Each plot shows one head's sensitivity map (the SRM summed over its 625 pixels) as
three projections of the 3D volume: summed along z (XY), along y (XZ) and along x
(YZ). The overlays show the heads of the same ring: crystals in red and collimator
outer envelopes in blue. The green dashed line runs from the FOV centre through the
pinhole of the head being plotted. Each panel has its own colour scale. Heads that
differ only in pinhole size look alike, but their colorbar maxima differ by up to
about 7×.

#for i in range(1, 74) {
  block(breakable: false, below: 8pt,
    image(figdir + "/modules/SRM_Head_" + pad2(i) + ext, width: 100%))
}

#pagebreak(weak: true)

== NEMA triple-line reconstruction

Three hot line sources parallel to z (NEMA NU 1 layout, 184 mm long, one voxel wide),
rotated 30° in-plane, were forward projected through all 73 heads and reconstructed
with MLEM.

#figure(
  image(figdir + "/nema_triple_line_phantom_reconstruction_iteration_50_x45-165_y55-155_z55-155" + ext, width: 100%),
  caption: [Brain system, MLEM iteration 50. Left: XY sum over z ∈ [−50, 50] mm.
    Middle and right: side views of the three lines.],
)

The lines are recovered at the correct positions and along their full length. The
in-plane FWHM is 1.4–1.5 mm at iteration 50 and falls to 1.05 mm (one voxel) by
iteration 200. Because the data are noiseless and made with the same SRM, this shows
convergence and is not the system resolution.

== ACR Jaszczak reconstruction

The same hot-background Jaszczak phantom as in Section 1 was reconstructed with all
73 brain heads.

#figure(
  image(figdir + "/jaszczak_phantom_hot_volume_reconstruction_iteration_100_x0-210_y0-210_z71-81" + ext, width: 100%),
  caption: [Brain system, 73 heads, MLEM iteration 100. Left: sum over the rod slab
    z ∈ [−34, −24] mm. Middle and right: sums over the full y and x ranges.],
)

#figure(
  image(figdir + "/jaszczak_phantom_hot_volume_reconstruction_iteration_100_x0-210_y0-210_z130-131" + ext, width: 100%),
  caption: [Brain system, 73 heads, MLEM iteration 100. Left: sum over the spheres, 1 mm z slice ]
)



