// Compile from the repository root:
// typst compile fisher_svd_gram.typ

#set document(title: "Fisher Column, SVD and Gram Matrix", author: "Fang Han")
#set page(paper: "us-letter", margin: (x: 1.9cm, y: 1.8cm), numbering: "1")
#set text(size: 10.5pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")
#show figure.caption: set text(size: 9pt)
#show table.cell.where(y: 0): set text(weight: "bold")

#align(center)[
  #text(size: 16pt, weight: "bold")[Fisher Column, SVD and Gram Matrix: \ Three Views of What the SRM Determines]
  #v(4pt)
  Fang Han · 2026-10-05 · working notes, companion to `streak_artifacts_report`
]

#block(fill: luma(245), inset: 8pt, radius: 3pt)[
  *Summary.* The Fisher column $F bold(e)_j$ is one column of the weighted Gram matrix
  $H^top D H$. It shows which voxels share detector bins with voxel $j$, and for a
  pinhole system these voxels lie on the lines from $j$ through every pinhole. It costs
  one forward and one back projection, and it depends on the object only through the
  weights $D$. Early-stopped MLEM shows that coupling only where the current estimate has
  activity, because its linearised response carries a factor $hat(f)_k \/ s_k$. That is
  why the compact cold-sphere phantom (E2) showed no streaks. The SVD gives the global
  picture: which image components converge slowly and which are never seen. This matters
  here because the 1 mm problem has at most 45,625 measurements for 4.94 million voxels.
  The SVD is affordable only through the small data-space Gram matrix $H H^top$
  (45,625#super[2], 8.3 GB).
]

= Setup and notation

The data are Poisson, $bold(y) tilde "Poisson"(macron(bold(y)))$, with mean
$macron(bold(y)) = H bold(f)$:

- $H in RR^(M times N)$ is the system matrix, with $M = "45,625"$ detector bins
  (73 modules × 625 pixels).
- The support has $N = "4,944,385"$ voxels: the 1 mm voxels inside the 105 mm FOV sphere.
- $s_j = sum_i H_(i j)$ is the sensitivity, $bold(s) = H^top bold(1)$.
- $D = "diag"(macron(bold(y)))^(-1)$ holds the inverse Poisson variances.

The Poisson log-likelihood and its derivatives are

$ L(bold(f)) = sum_i y_i log macron(y)_i - macron(y)_i, quad
  nabla L = H^top (bold(y) / macron(bold(y)) - bold(1)), quad
  -EE[nabla^2 L] = H^top D H equiv F. $ <fisher>

= The Fisher column

== Definition and physical meaning

The entries of the Fisher information matrix are

$ F_(k j) = sum_i (H_(i j) H_(i k)) / macron(y)_i. $ <fkj>

$F_(k j)$ is large when voxels $j$ and $k$ send counts to the same detector bins. Those
bins cannot tell the two voxels apart, so they are confusable. The Fisher column for
voxel $j$ is

$ F bold(e)_j = H^top D H bold(e)_j : $

forward project a point at $j$, weight each bin by $1 \/ macron(y)_i$, and back project.
It costs one forward projection and one back projection.

== Why the coupling runs along pinhole lines

For a pinhole module $m$, the counts from voxel $j$ land in a small spot of pixels.
Every voxel $k$ that projects into the same spot lies on the cone from that spot back
through the pinhole. That cone is a thin line through $j$ toward pinhole $m$, and it
continues across the FOV on both sides of $j$. $F bold(e)_j$ is therefore a star of up
to 73 lines, one per module, each weighted by how much that module sees $j$.

@fig-lines shows this: the streaks of the MLEM local impulse response (LIR) lie on the
voxel-to-pinhole lines. The coupling is long-range by construction. Its strength along a
line does not fall off with distance from $j$; it is modulated only by the sensitivity.

#figure(
  image("figs/lir_pinhole_lines.png", width: 92%),
  caption: [MLEM LIR at iteration 200 for the ACR phantom (top), with the line from the
    voxel to each of the 73 pinholes overlaid (bottom). The streaks follow the lines.],
) <fig-lines>

== Dependence on the object

$F$ depends on the object only through $D$, the expected counts per bin. Changing the
phantom reweights the 73 lines but does not move them. The unweighted version
($D = I$, the image-space Gram matrix $H^top H$, @gram) depends on the system only. The
coupling map used to place the E5 receivers, $H^top H bold(a) \/ bold(s)$, is a sum of
such columns over the cold-sphere voxels $bold(a)$.

== From Fisher to MLEM: the factor $hat(f)_k \/ s_k$

The Fisher column is not what MLEM shows. The MLEM update is

$ f_j^((n+1)) = f_j^((n)) / s_j sum_i H_(i j) y_i / (sum_k H_(i k) f_k^((n))). $

Perturb the data, $bold(y) -> bold(y) + bold(delta y)$, and linearise about the
iterate. With consistent data near a fixed point ($H hat(bold(f)) approx bold(y)$,
so $y_i \/ (H hat(bold(f)))_i^2 approx 1 \/ macron(y)_i$):

$ bold(delta)^((n+1)) approx bold(delta)^((n))
    + P (H^top D bold(delta y) - F bold(delta)^((n))),
  quad P = "diag"(hat(f)_k / s_k). $ <lin>

For a point perturbation, $bold(delta y) = H bold(e)_j$, so $H^top D bold(delta y) = F bold(e)_j$.
Starting from $bold(delta)^((0)) = bold(0)$,

$ "LIR"_j^((n)) = sum_(m=0)^(n-1) (I - P F)^m P F bold(e)_j,
  quad "LIR"_j^((1)) = P F bold(e)_j. $ <lir>

This is the EM linearisation of Barrett, Wilson and Tsui (1994), written for the image
instead of its logarithm and applied to a point perturbation instead of noise. They
expand $ln hat(bold(f))^((k))$ to first order (their approximations 1 and 2) and obtain
$bold(epsilon)^((k+1)) = B^((k)) bold(n) + [I - A^((k))] bold(epsilon)^((k))$ (their
eqs. 26–28) and $U^((k+1)) = B^((k)) + [I - A^((k))] U^((k))$ (eq. 31), with $A^((k))$ in
component form in their eq. (A3). In our notation $A = "diag"(bold(s))^(-1) F P'$ and
$B bold(n) = "diag"(bold(s))^(-1) H^top D bold(n)$, where $P' = "diag"(hat(bold(f)))$, so
$A = P'^(-1) (P F) P'$. Setting $bold(n) = H bold(e)_j$ and $bold(delta) = P' bold(epsilon)$
(their eq. 19) gives @lir. Here $P$ is held fixed; their $A^((k))$ changes with the
iteration. In the low-contrast limit their eq. (A4) gives $A prop H^top H$. Two
consequences matter here:

+ *The response at voxel $k$ carries the factor $hat(f)_k \/ s_k$.* Where the estimate is
  zero, MLEM cannot show the long-range coupling, however strong $F_(k j)$ is. In the ACR
  phantom the hot background fills the FOV, so the pinhole lines show everywhere. In E2
  everything outside the small phantom was empty, so the lines ran into regions where
  $hat(f) approx 0$. E5 puts hot receivers on the lines to test this directly.
+ *The response depends on the iteration count through $(I - P F)^m$.* Components that
  $P F$ shrinks only a little are still changing late in the iterations. This is the
  spectral picture of @svd.

The linearisation assumes small perturbations near a fixed point. The LIR in
`lir_acr.png` was computed exactly, by perturbing the data and reconstructing again, so
it does not rely on @lin.

= SVD view <svd>

== Weighted SVD and filter factors

Define the scaled matrix $tilde(H) = D^(1\/2) H P^(1\/2)$ with SVD
$tilde(H) = U Sigma V^top$, singular values $sigma_1 >= sigma_2 >= dots$. Then

$ P F = P^(1\/2) tilde(H)^top tilde(H) P^(-1\/2)
      = P^(1\/2) V Sigma^2 V^top P^(-1\/2), $

so the iteration matrix in @lir is diagonal in the basis $P^(1\/2) bold(v)_k$:

$ (I - P F)^n = P^(1\/2) V (I - Sigma^2)^n V^top P^(-1\/2). $

With noiseless, consistent data, the error after $n$ iterations, in the linear regime,
keeps a fraction $(1 - sigma_k^2)^n$ of each component $k$ (for $sigma_k^2 <= 1$). The
reconstruction applies the filter factor

$ phi_k (n) = 1 - (1 - sigma_k^2)^n $

to each component, as in Landweber iteration. Large-$sigma$ components are recovered in a
few iterations. Small-$sigma$ components are recovered slowly, and their partial
recovery is what changes with iteration count. An object with sharp edges has more
energy in the small-$sigma$ components. This gives a natural reading of the streak
observations: streaks grow with iterations, depend on the object's edges, and persist
with noiseless data.

== The 1 mm problem is heavily underdetermined

$ "rank"(H) <= M = "45,625" << N = "4,944,385". $

At least 99.1% of the image space is in the null space of $H$: no data, however
noiseless, constrain those components. MLEM still returns a definite image. Positivity,
the uniform start image and early stopping select it, not the data. Two points follow:

- Per-voxel *sampling completeness* (N_eff, the direction tensor, Tuy-type conditions)
  describes which *directions* a voxel is seen from. It does not address the global
  count deficit, which is the same everywhere.
- Null-space components do not appear in the linearised response @lir, because @lir lies
  in the range of $P F$. Streaks along pinhole lines are therefore row-space structure.
  They are slow, small-$sigma$ components, not null-space ones. The null space affects
  which image MLEM settles on, not the streak pattern.

= Gram matrix view <gram>

There are two Gram matrices.

#table(
  columns: (auto, 1fr, 1fr),
  stroke: 0.4pt,
  inset: 5pt,
  [], [Image space $H^top H$ ($N times N$)], [Data space $H H^top$ ($M times M$)],
  [Entry],
  [$sum_i H_(i j) H_(i k)$: bins shared by voxels $j$ and $k$],
  [$sum_j H_(i j) H_(i' j)$: voxels shared by bins $i$ and $i'$],
  [Meaning],
  [Unweighted Fisher matrix; columns are the coupling stars of @fig-lines],
  [Overlap of detector responses: multiplexing between pinhole images, crosstalk between neighbouring pixels],
  [Size at 1 mm],
  [$4.9 times 10^6$ squared: never formed; columns only, by FP + BP],
  [$"45,625"^2 = 2.1 times 10^9$ entries, 8.3 GB in float32: fits in memory],
)

The two share their non-zero spectrum. If $H H^top = U Sigma^2 U^top$, then

$ bold(v)_k = H^top bold(u)_k \/ sigma_k, $

so the full SVD of $H$ comes from the eigendecomposition of the small data-space Gram
matrix:

- Forming $H H^top$ costs about $sum_j "nnz"_j^2$ operations, about $5 times 10^11$
  (on average 304 non-zeros per column).
- A dense symmetric eigendecomposition of size 45,625 is about $10^14$ flops, which is
  practical on the 128-core workstation.

The weighted version uses $D^(1\/2) H H^top D^(1\/2)$. Including $P$ needs a specific
estimate $hat(bold(f))$, so it is object-dependent like the LIR.

== The resolution operator: an object-independent LIR

With the data-space Gram matrix, the Tikhonov-regularised resolution operator is

$ R_alpha = H^top (H H^top + alpha I)^(-1) H, quad
  R_alpha bold(e)_j = H^top (H H^top + alpha I)^(-1) H bold(e)_j. $

$R_alpha bold(e)_j$ is the point response of the regularised minimum-norm
reconstruction:

- It depends on the system only, plus one parameter $alpha$.
- It needs one forward projection, one solve of size $M$, and one back projection.
- It is the system's own "ideal LIR". Comparing it with the MLEM LIR separates what the
  SRM forces from what the MLEM path ($P$ and the iteration count) adds.
- Its diagonal, $(R_alpha)_(j j)$, is a per-voxel measure of how well voxel $j$ can be
  resolved at all.

= Comparison

#table(
  columns: (auto, 1fr, 1fr, 1fr),
  stroke: 0.4pt,
  inset: 5pt,
  align: left,
  [], [Fisher column $F bold(e)_j$], [SVD of $tilde(H)$ or $H$], [Gram $H H^top$ and $R_alpha$],
  [Answers], [Which voxels are confusable with $j$, and along which lines],
    [Which global image components converge slowly or never],
    [Detector overlap; the route to the SVD; the ideal point response $R_alpha bold(e)_j$],
  [Locality], [Local to one voxel], [Global; singular vectors spread over the FOV],
    [$R_alpha bold(e)_j$ is local; the spectrum is global],
  [Object dependence], [Weights $D$ only], [None for $H$; through $D$ and $P$ for $tilde(H)$],
    [None ($D = I$) or through $D$],
  [Cost at 1 mm], [One FP + BP (seconds)], [Via $H H^top$: forming plus an $M^3$ eigensolve (hours)],
    [8.3 GB matrix; each $R_alpha bold(e)_j$ is one solve],
  [What it misses], [MLEM's factor $hat(f)_k \/ s_k$ and the iteration dependence],
    [Locality; positivity; MLEM is not linear far from the fixed point],
    [Positivity; MLEM's path],
  [Use in this study], [Coupling map that places the E5 receivers],
    [Explains growth with iterations and the null-space share],
    [Ideal LIR to compare with the MLEM LIR],
)

= Results (2026-10-05)

== The ideal LIR reproduces the MLEM streaks

$R_alpha bold(e)_j$ was computed by conjugate gradients on $H H^top + alpha I$:

- 37–317 iterations per solve, each one forward and one back projection on the GPU;
- at most 70 s per solve;
- for $alpha = 10^(-2), 10^(-3), 10^(-4) lambda_max (H H^top)$.

At $alpha = 10^(-3) lambda_max$ it reproduces the streaks of the MLEM LIR almost line for
line, with the same positions and signs at all five radii (@fig-ideal). Beyond 15 mm from
the voxel, the correlation with the MLEM LIR is 0.66–0.84. Smaller $alpha$ adds speckle,
which is Monte Carlo noise in $H$ being amplified. The streak pattern is therefore a
property of the SRM. MLEM and the ACR object only scale it, through $P$ and the
iteration count.

#figure(
  placement: auto,
  image("figs/ideal_vs_mlem_lir.png", width: 100%),
  caption: [Ideal LIR $R_alpha bold(e)_j$ (system only) for three $alpha$, against the
    MLEM LIR at iteration 200 around the ACR phantom (right column). Slice z index 130,
    colour ±5% of the peak.],
) <fig-ideal>

== The streaks appear only when activity reaches the support boundary

The streaky response is present everywhere in $H$, yet compact phantoms (E2, E5) showed
no streaks. Two series of noiseless reconstructions, with data computed from the same $H$
(so fully consistent), locate the trigger:

- *E6, growing background.* The same cold spheres sit in a hot region that grows from a
  32 mm ball to the whole FOV. The result:
  - no streaks for any hot extent up to r = 100 mm;
  - streaks only when the hot region fills the whole support out to 105 mm.
- *E1b, cropped ACR.* The same pattern (@fig-e1b): no streaks when the ACR is cropped to
  r ≤ 80 or 95 mm; the streaks of the report when it is uncropped.

#figure(
  placement: auto,
  image("figs/e1b_montage.png", width: 100%),
  caption: [ACR phantom cropped to r ≤ 80 mm (top) and r ≤ 95 mm (middle), and
    uncropped (bottom). Sphere slice at iterations 50, 100 and 200 (grey scale 0.6–1.3),
    and the rod slab at iteration 100.],
) <fig-e1b>

So $H$ supplies the shape of the streaks, and they become visible when the object
reaches the edge of the modelled support. A plausible reading: an empty margin inside the
support acts as a known-zero region. MLEM's multiplicative update pins it near zero, which
fixes the poorly determined components there, as a support constraint does in interior
and truncated tomography. When activity runs to the boundary, the low-sensitivity,
low-$N_"eff"$ boundary shell has no such constraint. This explanation is not yet proven.

= Next computations

+ *Margin width.* Hot to r = 100, 102, 103 and 104 mm: how much empty margin is needed.
  This bears directly on the 288 mm SRM, which leaves such a margin around a head that
  fits inside 210 mm.
+ *Data-space Gram matrix.* Form $H H^top$ (8.3 GB) and eigendecompose it. Report:
  - the spectrum $sigma_k$;
  - the effective rank at a few thresholds;
  - the share of small-$sigma$ components in the ACR and cold-sphere phantoms
    ($||V_k^top bold(f)||$ by band of $sigma$).
+ *Support constraint.* Run the same series with the edge shell excluded from the
  reconstruction support, to test the support-constraint reading directly.

#v(6pt)
*References.*
H. H. Barrett, D. W. Wilson, B. M. W. Tsui, "Noise properties of the EM algorithm: I.
Theory," _Phys. Med. Biol._ 39:833–846, 1994.
J. A. Fessler, W. L. Rogers, "Spatial resolution properties of penalized-likelihood image
reconstruction," _IEEE Trans. Image Process._ 5(9):1346–1358, 1996.
P. C. Hansen, _Rank-Deficient and Discrete Ill-Posed Problems_, SIAM, 1998.
D. L. Snyder, M. I. Miller, L. J. Thomas, D. G. Politte, "Noise and edge artifacts in
maximum-likelihood reconstructions for emission tomography," _IEEE Trans. Med. Imaging_
6(3):228–238, 1987.
_Barrett et al. and Snyder et al. were checked against the papers (dev/references/); the
other citation details are from memory and should be checked before reuse._
