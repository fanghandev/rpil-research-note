# Rim Streaks in Brain SPECT — Study Report

Oct 7, 2026 · @Fang

## Summary

The radial streaks at the rim of our brain SPECT MLEM reconstructions are a property of the system matrix, set off by specific sources in the poorly sampled rim zone; they are not truncation. All data in this study are noiseless and consistent (y = Hf), so classic truncation cannot occur.

| Claim | Evidence | Confidence |
| --- | --- | --- |
| The streak geometry comes from the SRM: lines from each voxel through the pinholes, strongest at the rim | Ideal LIR from H alone reproduces the MLEM LIR (far-field correlation 0.66–0.84) | High |
| MLEM shows the coupling only where the estimate holds activity | Compact phantoms show no streaks (E2, E5); linearised MLEM theory (Barrett et al. 1994) | High |
| A uniform object streaks only when its activity reaches the support edge | Hot ball to ≤ 104 mm: no long streaks; to 105 mm: streaks (E6, E7) | High (one object family, Gate SRM) |
| A larger modelled FOV with a uniform start (ε = 1) makes streaks worse; starting the extra shell at ε = 0.01 removes that part | E8 runs B, G, H; E9 runs B9, C9, E9c | High for the shell effect |
| Cold inserts the system cannot resolve, especially the rods, drive streaks at an object's own edge, whatever the support | E9 polar views; E9b insert ablation (stripe RMS 0.014 → 0.035) | Medium: one SRM, one slice, new metric |
| The bright ring just inside hot edges is the maximum-likelihood edge overshoot of Snyder et al. (1987) | Overshoot 11–15 %, saturating with iterations, ripple inside, removed by a 10 mm post-filter | Medium–high |

**What changed during review.** A first reading of E9 and E1b said streaks vanish when the object sits inside the FOV. A polar view of each object's own edge showed weaker streaks remain. The conclusions above are the corrected ones.

**For the 288 mm SRM.** Build it, because real heads put activity outside 210 mm. Reconstruct with ε ≈ 0.01 outside the body contour, not a uniform start over the whole sphere. A margin alone does not remove insert-driven streaks.

## Background

MLEM reconstructions of the hot-background ACR Jaszczak phantom on our brain system show radial streaks near the edge of the 210 mm FOV, growing with iterations and worst in the rod slab.

**The system.** 73 pinhole modules in 7 rings, at elevations from −37° to 90°. Each module has a 50 × 50 × 10 mm crystal of 25 × 25 pixels, so there are 45,625 detector bins. Pinhole centres lie on a sphere of radius 149.6 mm.

**The production system matrix (SRM), brain\_merged\_123.** Gate 10 Monte Carlo, 140 keV, 1.26 × 10¹³ primaries, 126–154 keV window, 210³ grid of 1 mm voxels, 1.50 × 10⁹ non-zeros. 4,944,385 voxels have sensitivity (the support), out to r = 105.8 mm.

**Sampling.** The effective number of modules seeing a voxel, N\_eff = 1 / Σ\_m w\_mj² with w\_mj = s\_mj / s\_j, falls from about 46 at the centre to 13–20 near r = 100 mm, and the views become one-sided. Total sensitivity stays smooth: median 1,479 counts within r < 50 mm and 1,063 at r = 104–105 mm.

**The two hypotheses.**

1. Truncation: the modelled FOV (210 mm) is too small, and a 288 mm SRM would fix it.
2. Angular sampling: rim voxels are seen by few modules from one side, so MLEM leaves errors free to spread along the poorly sampled direction.

## Methods

Every reconstruction is plain MLEM on noiseless data computed with the same matrix used to reconstruct, so the data are always consistent.

```latex
f_j^{(n+1)} = \frac{f_j^{(n)}}{s_j} \sum_i H_{ij} \frac{y_i}{(H f^{(n)})_i}, \qquad s_j = \sum_i H_{ij}, \qquad y = H f
```

**Two system matrices.**

| SRM | Voxels | Modelled FOV | Built by | Noise in entries |
| --- | --- | --- | --- | --- |
| Gate, brain\_merged\_123 | 1 mm, 210³ | r ≤ 105.8 mm | Gate 10 Monte Carlo, energy window | Poisson; 11–16 % in main entries when binned to 2 mm |
| Ray-traced (gammart) | 2 mm, 144³ | r ≤ 142 mm | OptiX ray tracer, primary photons only, 9 min on an RTX 3080 Ti | Sampling noise 7–11 % in main entries |

The ray-traced SRM matches Gate projections of 10 mm spheres pixel by pixel (correlation 0.9999 at the centre, 0.9997 off-centre); its totals are 3 % higher because it counts all first interactions.

**Terms.**

- **Support:** the voxels MLEM may put activity in. A voxel that starts at 0 stays at 0, so the start image sets the support.
- **Shell:** in the ray-traced model, the region 105 < r ≤ 142 mm. It is modelled but truly empty.
- **Start image and ε:** ε = 1 is the usual uniform start; ε = 0.01 ("near zero") starts the shell at 1 % of the object's level; ε = 0 is a hard support.
- **Contour support:** the object's outline grown by 4 mm, zero outside.
- **η:** the share of reconstructed activity left in the shell.

```latex
f_j^{(0)} = \begin{cases} 1 & r_j \le 105\,\text{mm (object region)} \\ \varepsilon & 105 < r_j \le 142\,\text{mm (shell)} \\ 0 & r_j > 142\,\text{mm (not modelled)} \end{cases} \qquad \eta^{(n)} = \frac{\sum_{j \in \text{shell}} f_j^{(n)}}{\sum_j f_j^{(n)}}
```

**Phantoms.**

| Phantom | Description | Used in |
| --- | --- | --- |
| Cold-sphere phantom | Hot ball, radius 32 mm, with four cold spheres (15.9, 12.7, 9.5, 6.4 mm) on a 16 mm ring; shifted in whole voxels | E2, E5, E6, E7 |
| Receivers | Uniform hot balls, radius 14 mm | E5 |
| Growing background | Cold spheres at the rim position P2 in a hot ball of radius 40–105 mm | E6, E7 |
| ACR Jaszczak (full and cropped) | Hot cylinder, radius 104.5 mm, cut by the 105 mm support; cropped to 80 or 95 mm in E1b | E1b, E8 |
| Shrunk ACR | Hot cylinder, radius 95 mm, height 79 mm, rims at r = 102.9 mm; the six ACR spheres (orbit 52.3 mm) and rods (28 mm long, outer rows dropped) | E9, E9b, E9c |

**Polar view.** Each slice is unwrapped around the object's own edge: distance from that edge against azimuth. Radial streaks show as vertical stripes. This is the view the corrected E9 conclusions rest on.

## Results

The streak pattern lives in the system matrix, but it shows up only when something in the rim zone excites it: activity at the support edge, a shell that starts full, or cold inserts the system cannot resolve.

| Test | What changes | Result |
| --- | --- | --- |
| E2 | Compact phantom moved to the rim | No streaks; the rim is sharper than the centre |
| E5 | Hot receivers on the coupling lines | Small shift and level change, no streaks |
| Ideal LIR | H alone: no object, no MLEM | Reproduces the MLEM streak pattern |
| E6 / E1b | Hot region grown out to the support edge | Uniform ball: streaks only when hot reaches 105 mm; cropped ACR: weaker streaks remain |
| E7 | Empty margin from 10 mm to 0 mm | Uniform ball: ≥ 2 mm of margin removes the streaks |
| E8 | Larger modelled FOV (142 mm), ray-traced SRM | Worse with ε = 1; fixed by ε = 0.01 |
| E9 | Shrunk ACR, ≥ 2 mm inside the FOV | Weaker streaks remain at its own edge |
| E9b | Shrunk ACR taken apart insert by insert | The cold inserts, mostly the rods, drive the edge streaks |
| E9c | Shrunk ACR with spheres only | Spheres reconstruct well; faint edge stripes remain |

### E2: a compact phantom at the rim

The cold-sphere phantom was moved to six positions, including P2, whose surface reaches r = 99.4 mm in the least-sampled direction (N\_eff = 13). No radial streaks appeared at any position (iterations 10–200). At iteration 100 the rim was sharper than the centre: contrast of the 15.9 mm sphere 0.76 at P2 and P3 against 0.65 at P0; background CoV 0.105–0.108 against 0.117. A fine speckle (CoV 0.10–0.13) grows with iterations everywhere; it is probably Monte Carlo noise in H.

### E5: hot receivers on the coupling lines

The coupling map c = HᵀH a / s (a = indicator of the cold spheres) is a star of bands along pinhole lines. A 14 mm hot receiver sat in the strongest band and a control in a gap with about 10× less coupling, 70–76 mm from the source. The source added a ±0.1 dipole at iteration 10, then a 1.5–2 % level rise. Ten times more coupling gave only 1.1–1.3× more effect, and no line-shaped streaks.

### Ideal local impulse response

R\_α e\_j = Hᵀ(HHᵀ + αI)⁻¹H e\_j, solved by conjugate gradients at five voxels, reproduces the MLEM LIR streak pattern. Far-field correlation (beyond 15 mm) is 0.66–0.84 at α = 10⁻³ λ\_max; smaller α adds speckle from Monte Carlo noise in H. The streaks lie on the voxel-to-pinhole lines. CG took 37–317 iterations, at most 70 s per solve.

### E6 and E1b: growing the hot region

Cold spheres stayed at P2 while the hot ball grew from 32 to 105 mm. Up to 100 mm there were no long streaks, only a bright band at the hot edge. At 105 mm, filling the support, the ACR streak pattern appeared. For the cropped ACR (80 and 95 mm), a polar view of its own edge shows weaker streaks remain; the first reading had missed them.

### E7: margin width

Hot ball radius 100–105 mm in 1 mm steps (uniform ball, Gate SRM). An empty margin of 2 mm or more gave no streaks; 1 mm gave faint blobs; 0 mm gave clear streaks. This holds for the uniform ball; E9 shows a margin is not enough for an object with inserts.

### E8: larger modelled FOV (ray-traced SRM)

Same object (hot ball to 105 mm), support 105 or 142 mm. With ε = 1 in the 142 mm support the streaks became stronger across the whole object; η was 33.8 % at iteration 10, 8.8 % at 200 and 3.0 % at 1000. With ε = 0.01, η stayed ≤ 1.1 % and the image was as clean as the tight support. The full ACR kept faint fine rim streaks in every variant.

### E9: the shrunk ACR, fully inside the FOV

Predictions were written down before running. Seven runs on both SRMs (contour support, ε = 1 and 0.01). In the polar view, the shrunk ACR shows streaks 10–25 mm deep from its own edge with every support, weaker than the full ACR's. With ε = 1 in the 142 mm support the object was pulled down with radial spokes early on (difference RMS 0.094 in the rod slice at iteration 10, 0.020 at 200; η 15.6 % → 0.65 %). Contour support with ε = 0.01 elsewhere matched a hard contour support (RMS difference ≈ 0.001).

### E9b: which part of the object makes the edge streaks

Same ray-traced SRM, support r ≤ 105 mm, ε = 1, iteration 200, sphere slice. Stripe RMS = RMS of the azimuthal high-pass of (recon − truth) in the band 3–20 mm inside the edge.

| Object | Stripe RMS |
| --- | --- |
| Cylinder only | 0.014 |
| + cold spheres | 0.024 |
| + cold rods | 0.029 |
| + spheres + rods | 0.035 |

The rods sit 30–60 mm below the measured slice, yet they add strong stripes there. The likely route is along oblique pinhole lines into the hot outer part of the slice; that route is an inference from the images, not traced.

### E9c: spheres only

Shrunk ACR with the six cold spheres and no rods, both SRMs, uniform start over the support. Contrast recovery on the Gate SRM:

| Sphere | Iteration 100 | Iteration 200 |
| --- | --- | --- |
| 31.8 mm | 0.82 | 0.86 |
| 25.4 mm | 0.76 | 0.82 |
| 19.1 mm | 0.64 | 0.72 |
| 15.9 mm | 0.54 | 0.63 |
| 12.7 mm | 0.39 | 0.48 |
| 9.5 mm | 0.23 | 0.31 |

The ray-traced SRM agrees within 0.02. Faint edge stripes remain (stripe RMS 0.024), and the coronal view shows horizontal bands that have not been investigated.

## Theory

Three linear-algebra views explain the results: the ideal LIR shows what the data can resolve, the linearised MLEM LIR shows what MLEM displays, and singular values explain why the streaks change with iterations.

### Ideal local impulse response

Put activity in one voxel j, project it, and invert the noiseless data as directly as the system allows. A perfect system returns one voxel; whatever spreads away from j is what the data cannot resolve. It uses only H.

```latex
R_\alpha e_j = H^\top (H H^\top + \alpha I)^{-1} H e_j = (H^\top H + \alpha I)^{-1} H^\top H e_j
```

Read in three steps: (1) y\_j = H e\_j simulates the data voxel j alone would produce; (2) (HHᵀ + αI) u = y\_j finds one weight per detector pixel, given how the pixels overlap; (3) Hᵀu back-projects the weights. (HHᵀ)\_ik = Σ\_j H\_ij H\_kj measures how strongly detector pixels i and k look at the same voxels; it is 45,625 × 45,625, against 45,625 × 4.94 million for H, so each CG step costs one forward and one back projection.

### Coupling map

c\_k = (HᵀH a)\_k / s\_k: forward project a source indicator a, back-project, and divide by sensitivity as MLEM does. A large c\_k means voxel k and the source share many detector pixels, so the data struggle to tell them apart. In a pinhole system the bands run along lines through the pinholes and cross the whole FOV. HHᵀ asks which detector pixels share voxels; HᵀH asks which voxels share detector pixels.

### Linearised MLEM response

```latex
\mathrm{LIR}_j^{(n)} = \sum_{m=0}^{n-1} (I - P F)^m P F e_j, \qquad P = \mathrm{diag}\!\left(\frac{\hat f_k}{s_k}\right), \qquad F = H^\top \mathrm{diag}(\bar y)^{-1} H
```

F (the Fisher information) couples voxel j to every voxel on its pinhole lines. P scales the response at voxel k by the current estimate, so where the estimate is zero no streak can appear. This is why compact objects in empty space show no streaks while the ACR, hot everywhere, shows every line.

**Source.** This is the EM linearisation of Barrett, Wilson & Tsui (1994), checked against the paper. They expand the log of the iterate to first order (their approximations 1 and 2) and obtain ε^(k+1) = B^(k) n + \[I − A^(k)\] ε^(k) (eqs. 26–28), U^(k+1) = B^(k) + \[I − A^(k)\] U^(k) (eq. 31), with A^(k) in eq. (A3). With A = diag(s)⁻¹ F diag(f̂) = diag(f̂)⁻¹ (PF) diag(f̂), a point perturbation n = H e\_j, and δ = diag(f̂) ε (their eq. 19), their recursion gives the formula above. Holding P fixed is our extra approximation; their A^(k) changes each iteration. The MLEM LIR in our figures was computed exactly by perturbation, so it does not depend on that approximation. Their eq. (A4) adds that for a large low-contrast object A ∝ HᵀH, the coupling-map operator.

### Singular values and iteration count

Write H = Σ\_k σ\_k u\_k v\_kᵀ. Large σ: the pattern v\_k shows strongly in the data. Small σ: fine structure, edges and one-sided views, poorly determined. In the linear regime MLEM recovers mode k by the factor 1 − (1 − σ\_k²)^n (for the weighted matrix D^½ H P^½), and the ideal LIR keeps it by σ\_k² / (σ\_k² + α). Iteration count and α both set a σ cut-off, which is why the ideal LIR can mimic the MLEM LIR at 200 iterations. Streaks would be slow, small-σ modes. No spectrum has been computed yet (eigendecomposing HHᵀ, about 8.3 GB, is an open step), so this part is interpretation. H has at most 45,625 non-zero σ against 4.94 million voxels; the streaks are small-but-non-zero modes, not null-space ones.

## Edge overshoot and Snyder et al. (1987)

The bright ring just inside hot edges is the maximum-likelihood edge overshoot that Snyder et al. describe: it appears with noiseless data, grows with iterations and levels off, and post-filtering removes it.

&#91;embedded content: extent\_series/analysis/edge\_overshoot.json (analyze\_edge\_overshoot.py) · grow\_R080–R105, 3-D radial profile, cold-sphere sector excluded\]

How the measurements match the paper:

- **Noiseless data still produce it.** Their Figs. 6 and 17 use mean-value data; all our data are noiseless.
- **Gibbs-like shape.** The peak is followed by an undershoot of −3 to −6 % and a weaker ripple further inside; the peak moves toward the edge with iterations (−11.5 → −5.5 mm) as finer detail is recovered.
- **Their remedy works.** They estimate a blurred version of the object, equivalent to post-filtering. At iteration 200 a 6 mm Gaussian halves our overshoot (5.3–7.3 %) and a 10 mm Gaussian removes it (0.8–1.6 %).
- **Kernel mismatch.** Their overshoot rises to about 30 % when the EM kernel is truncated relative to the data kernel. Our data and reconstruction share H, so there is no mismatch.

Beyond the paper: the overshoot is smaller and rises more slowly as the edge approaches the rim, and a ball that fills the support has none, because no edge lies inside the support. That is also the case that streaks.

### Why it is Gibbs-like: what is truncated

The truncation is not the voxel grid; it is the set of components the system passes strongly enough for MLEM to recover within n iterations.

- **Classic Gibbs.** Representing a step with only the frequencies below a sharp cut-off f\_c gives an overshoot of about 9 % of the jump and ringing with a period of about 1/f\_c. The sharpness of the cut-off causes it; a smooth roll-off blurs without ringing.
- **The system is the low-pass filter.** Pinhole apertures and detector blur pass coarse patterns strongly (large singular value σ) and fine ones weakly (small σ). Our system is not shift-invariant, so "frequency" means the singular-vector basis of H rather than literal Fourier modes.
- **MLEM sharpens the cut-off with iterations.** Component k is recovered by about 1 − (1 − σ\_k²)^n, which approaches a step: components with σ² ≳ 1/n are essentially recovered, those below mostly missing. More iterations make the cut-off sharper and move it to finer detail.
- **Non-negativity.** Snyder et al. attribute their 18 % (rather than about 9 %) to the non-negativity constraint: the ringing cannot swing below zero outside the object.

**Why not the voxel sampling.** The 1 mm grid's Nyquist limit is 0.5 cycles/mm; the recoverable bandwidth is about ten times lower (resolution about 10 mm FWHM at iteration 100). Read from the 95 mm profile at iteration 200 (approximate): peak about 5 mm inside the edge, undershoot about 15 mm, second bump about 27 mm, so a ripple period near 20 mm, a cut-off near 0.05 cycles/mm. The peak moves toward the edge with iterations (−11.5 → −5.5 mm), as a rising cut-off predicts and a fixed grid limit would not. A 10 mm Gaussian post-filter, which replaces the sharp cut-off with a smooth one, removes the overshoot. Both SRMs (1 mm and 2 mm voxels) show it.

**What sets the cut-off.** The design sets the ceiling; the reconstruction sets where the cut actually falls; and neither is one number for the whole image.

- **Design (the ceiling).** The system's resolution limit, fixed by the pinhole apertures (four sizes, 0.556–2.007 mm), the magnification, the detector's intrinsic resolution and 2 mm pixels (10 mm crystals, with parallax), and the angular coverage (how many modules see each voxel, from which directions). Together these fix the singular-value spectrum of H, the best resolution that could ever be recovered. Pixel pitch samples each projection and the module layout samples directions, so "sampling" enters here, not through the reconstruction grid.
- **Reconstruction (the actual cut).** Iteration count, data noise and the accuracy of H (including its Monte Carlo noise) decide how much of that spectrum a given image recovers. This is why the ripple moves with iterations while the system stays the same.
- **Position and direction.** The system is not shift-invariant, so the cut-off varies across the image. Near the rim, with fewer and one-sided views, it is lower and direction-dependent, which links the weaker, slower overshoot there to the streaks there.

**Edge position (C9).** Rim voxels are seen from fewer, one-sided directions, so their fine-detail components have smaller σ. The effective cut-off there is lower and rises more slowly, matching the smaller, slower overshoot near the rim. Consistent with the data, not tested; the spectrum of HHᵀ (X5) and a ripple-period-versus-iteration measurement would test it.

**Where it comes from.** The overshoot needs two things: a system with finite, decaying resolution (any real system, ours included) and a reconstruction that tries to undo that resolution without a smooth limit, which is unregularised maximum likelihood. It is not specific to the EM algorithm: Snyder et al. show it belongs to the ML estimate itself, so OSEM or any other ML solver would show it too. The geometry shapes it (how large, how fast, where), but the reconstruction choices control it: iteration count, post-filter, a resolution-limited estimate or a prior.

## Corrections and what failed

Two claims in earlier drafts were wrong and have been corrected: that streaks vanish once the object sits inside the FOV (E9, E1b), and an unverified citation.

- **E9 and E1b misread.** The first reading zoomed on the old phantom's rim position (r ≈ 100 mm) and called the new edge an overshoot band. In a polar view of each object's own edge, streaks remain, weaker. The E9 verdicts for runs G1, G2, A9 and D9 ("no rim streaks") were reversed. The E6/E7 verdict for uniform balls was rechecked the same way and holds.
- **Weaker effect than predicted.** E9 run B9 (ε = 1 to 142 mm) was predicted to streak across the object as in E8. The effect was the same kind but weaker and faded by iteration 200, because the shell drained about 5× faster (η 0.65 % against 3.3 % at iteration 200). A plausible reason, untested: the shrunk ACR's edge is 2–10 mm from r = 105 mm, so shell voxels are easier to tell apart from it.
- **Scalar streak metrics.** A structure-tensor "streak axis" measured anisotropic blur, not streaks. A tangential-over-radial gradient index was dominated by the surface roll-off. An angular-profile amplitude masked the sectors where the streaks are. An annulus azimuthal-variation measure scored the shrunk ACR higher than the full ACR. The E9b stripe RMS (recon − truth, azimuthal high-pass) ranks the cases as the images do, but it is new and checked only against images.
- **Citations.** The slides first cited Barrett et al. (1994) for the LIR formula without access to the paper. It has now been read: the linearisation and equation numbers are confirmed (Theory section). Snyder et al. (1987) was added after reading the paper.

## Conclusions

The SRM sets the geometry of the streaks; three sources set them off; and keeping the object inside the FOV removes only one of those sources.

1. **Geometry from the SRM.** Streaks follow voxel-to-pinhole lines and are strongest for poorly sampled rim voxels (low N\_eff, one-sided views). This is the sampling hypothesis.
2. **Visibility from the estimate.** MLEM shows them only where the estimate holds activity, real or spurious.
3. **Sources seen so far.**
   - Cold inserts the system cannot resolve, rods especially (E9, E9b).
   - Activity reaching the support edge (E6, E7).
   - A poorly sampled region that starts full (E8, E9 run B9).
4. **Truncation in the data-inconsistency sense played no role here.** All data were consistent.

**Implications for the 288 mm SRM.**

- Build it: real heads and necks put activity beyond 210 mm. That is true truncation, which this study did not test.
- Avoid a uniform start over the whole sphere; the extra shell is sampled even worse than today's rim.
- Start at ε ≈ 0.01 outside the body contour (CT, μ-map or a first pass) plus a few mm. In E9 this matched a hard contour support.
- A margin is not enough: insert-driven streaks belong to the system's sampling and remain with any support.

## Limitations and open questions

Everything here is noiseless, consistent MLEM to at most 200 iterations; whether the remaining streaks matter clinically is the biggest open question.

**Limitations.**

- Noiseless, consistent data: no Poisson noise, attenuation, scatter or model error.
- MLEM only, ≤ 200 iterations (1000 in one run); no OSEM or regularisation.
- Evidence is mostly visual, from single slices; scalar metrics largely failed.
- The ray-traced SRM is primary-only, 2 mm, with 7–11 % sampling noise; the Gate SRM has visible Monte Carlo speckle at 1 mm.
- E9b used one SRM, one slice and one new metric.
- The singular-value reading has no computed spectrum behind it yet.

**Open questions.**

- Do the remaining rim streaks matter at clinical counts and 20–50 iterations?
- Is the background speckle (CoV 0.10–0.13 with noiseless data) Monte Carlo noise in H?
- Do insert-driven errors really travel along oblique pinhole lines, as E9b suggests?
- Why is the shrunk ACR's streak weaker than the full ACR's: edge position (higher N\_eff), the missing support-edge source, or fewer rods?
- Why does the edge overshoot shrink and rise more slowly as the edge moves toward the rim?
- What are the horizontal bands in the coronal view of E9c?
- How small must ε be? Only 1, 0.01 and 0 were tried.
- Does a small ε really protect against a wrong body contour? No run had activity outside the assumed contour.

## References

Two papers were read in full (PDFs in dev/references/); four were checked against their PubMed abstracts only; one claim is from memory and marked so.

| Reference | Checked against | Used for |
| --- | --- | --- |
| H. H. Barrett, D. W. Wilson, B. M. W. Tsui, "Noise properties of the EM algorithm: I. Theory," Phys. Med. Biol. 39(5):833–846, 1994. [doi:10.1088/0031-9155/39/5/004](https://doi.org/10.1088/0031-9155/39/5/004) | Full paper | EM linearisation, eqs. 26–31, A3, A4 |
| D. L. Snyder, M. I. Miller, L. J. Thomas, D. G. Politte, "Noise and edge artifacts in maximum-likelihood reconstructions for emission tomography," IEEE Trans. Med. Imaging 6(3):228–238, 1987. [doi:10.1109/TMI.1987.4307831](https://doi.org/10.1109/TMI.1987.4307831) | Full paper | Edge overshoot of ML reconstruction |
| W. Wang, G. Gindi, "Noise analysis of MAP-EM algorithms for emission tomography," Phys. Med. Biol. 42(11):2215–2232, 1997. [PubMed 9394408](https://pubmed.ncbi.nlm.nih.gov/9394408/) | Abstract | Confirms Barrett's approach is a linearisation; extends it to MAP-EM |
| E. J. Soares, C. L. Byrne, S. J. Glick, "Noise characterization of block-iterative reconstruction algorithms: I. Theory," IEEE Trans. Med. Imaging 19(4):261–270, 2000. [PubMed 10909922](https://pubmed.ncbi.nlm.nih.gov/10909922/) | Abstract | Iteration-dependent mean and covariance for ML-EM and OS-EM |
| J. Qi, "A unified noise analysis for iterative image estimation," Phys. Med. Biol. 48(21):3505–3519, 2003. [PubMed 14653559](https://pubmed.ncbi.nlm.nih.gov/14653559/) | Abstract | Iteration-based linearised analysis for preconditioned gradient algorithms (MLEM's preconditioner is our P) |
| J. A. Fessler, W. L. Rogers, "Spatial resolution properties of penalized-likelihood image reconstruction: space-invariant tomographs," IEEE Trans. Image Process. 5(9):1346–1358, 1996. [PubMed 18285223](https://pubmed.ncbi.nlm.nih.gov/18285223/) | Abstract | Origin of the local impulse response |

**From memory, unverified:** Fessler & Rogers' linearised LIR has the form \[F + R\]⁻¹F e\_j; with an identity penalty and unit weights it would equal our ideal LIR. Check the paper before citing.

No paper found so far writes the slide formula Σ\_{m\<n} (I − PF)^m PF e\_j explicitly as an MLEM LIR. It is a short derivation from Barrett et al. (constant A, point perturbation, image domain).

## How the literature maps onto the two phenomena

Snyder et al. (1987) explains the edge overshoot directly; no reference found so far explains the rim streaks directly, but Barrett et al. (1994) supplies the mechanism we use for them, and the others supply tools to extend both analyses.

| Reference | Rim streaks (pinhole-line streaks at the rim) | Edge overshoot (bright ring inside hot edges) | Checked |
| --- | --- | --- | --- |
| Barrett, Wilson & Tsui 1994 | Supplies the mechanism: the linearised response at a voxel carries the factor f̂ (δ = a·ε, eq. 19), so coupling shows only where the estimate holds activity (C2). Eq. (A4), A ∝ HᵀH for a low-contrast object, ties the iteration to our coupling map. It treats noise, not streaks or pinhole geometry. | Not addressed. Its eq. (24) says the noise-free mean a^(k) is plain EM on noise-free data, so the overshoot belongs to the deterministic mean image, outside its noise theory. This fits our overshoot appearing with noiseless data. | Full paper |
| Snyder, Miller, Thomas & Politte 1987 | Indirect. Its explanation of the edge artifact is ill-posedness: a rapidly decaying eigenspectrum leaves high-frequency components unrecoverable. That is the small-σ picture we propose for the streaks (C11). It uses a 1-D shift-invariant kernel, so it cannot show pinhole-line streaks. | Direct explanation (C8): Gibbs-like overshoot with mean-value data, rising with iterations to about 16–18 % (about 30 % with a mismatched, truncated kernel), fundamental to unconstrained ML, suppressed by estimating a blurred version (equivalent to post-filtering). Matches our 11–15 % and the post-filter test. | Full paper |
| Wang & Gindi 1997 | Extends Barrett's iteration-to-iteration propagation of the mean and covariance to MAP-EM. Would predict how a smoothing prior changes the streaks. | Same tool: would predict how a prior changes the overshoot, an alternative to post-filtering (X9). | Abstract |
| Soares, Byrne & Glick 2000 | Iteration-dependent mean and covariance for ML-EM and OS-EM. Needed to carry the analysis to OSEM at clinical iteration counts (X1). | Same: the mean image, where the overshoot lives, under OSEM. | Abstract |
| Qi 2003 | Iteration-based linearised analysis for preconditioned gradient algorithms; MLEM is one, with preconditioner diag(f̂/s) = our P. The most general published form of our LIR recursion, and it links early-stopped and fixed-point results. | Indirect: the same framework covers the mean image, so it could say whether the overshoot persists at convergence. | Abstract |
| Fessler & Rogers 1996 | Defines the local impulse response; shows it is space-variant and object-dependent even for space-invariant systems. Our rim streaks are a strongly space-variant LIR. From memory (unverified): its linearised LIR \[F + R\]⁻¹F e\_j would equal our ideal LIR for an identity penalty. | Indirect: quadratic penalties that set the resolution are another way to trade the overshoot against contrast. | Abstract |

**Gap.** None of these treats stationary multi-pinhole SPECT, streaks along voxel-to-pinhole lines, cross-slice errors from unresolved inserts (C6, C7), or the dependence of the overshoot on edge position (C9). These are the targets for the literature search in the handoff section.

## Reproducibility

All code and outputs are in the qmirt-gate-10-sim repository under dev/python/ (branch brain-288mm-csg-production, uncommitted as of 2026-10-07); the running lab notes are dev/python/streak\_sampling\_study.md.

Run from dev/python in the `opengate` environment (`micromamba activate opengate`); gammart\_srm.py needs the `raytracing` environment and \~/Work/RPIL/QMIRT/pytorch-optix. GPU: one RTX 3080 Ti; a 1 mm Gate MLEM run of 200 iterations takes about 75 s, a 2 mm ray-traced run about 15 s.

| Experiment | Script | Outputs |
| --- | --- | --- |
| Sampling maps (N\_eff, direction tensor) | sampling\_coverage\_map.py | sampling\_brain\_merged\_123/ |
| E2 | cold\_sphere\_phantom.py, analyze\_cold\_sphere\_shift.py | cold\_sphere\_phantom/ |
| E5 | receiver\_coupling\_phantoms.py, analyze\_receiver\_coupling.py | receiver\_coupling/ |
| Ideal LIR | ideal\_lir.py | ideal\_lir/ |
| E6, E7, E1b | extent\_series\_phantoms.py, analyze\_extent\_series.py, analyze\_margin\_series.py | extent\_series/ |
| Ray-traced SRM | gammart\_srm.py | gammart\_srm/brain\_2mm\_r142.npz |
| E8 | gammart\_support\_test.py, gammart\_support\_followup.py | gammart\_srm/ |
| E9 | acr\_fit\_phantom.py, e9\_acr\_fit\_test.py | acr\_fit/ |
| E9b | e9b\_edge\_streaks.py | acr\_fit/e9b\_\* |
| E9c | e9c\_sphere\_only.py | acr\_fit/e9c\_\* |
| Edge overshoot vs Snyder | analyze\_edge\_overshoot.py | extent\_series/analysis/edge\_overshoot.\* |
| All reconstructions (Gate SRM) | fp\_jaszczak\_and\_recon.py --phantom \<npz> --iterations 10 20 50 100 200 | per-experiment runs/ folders |

**Write-ups.** dev/python/report/: streak\_artifacts\_report.pdf (initial observation), streak\_study\_report.pdf (E1b–E8; its E1b claim is outdated), fisher\_svd\_gram.pdf (theory; Barrett derivation updated 2026-10-07). Slides: the Rim Streaks deck (Claude artifact).

## Handoff for research planning

This section is the starting state for agents expanding the study into a research plan (Notion) and a literature review (Undermind); claims carry IDs so later work can cite, test or retire them.

**Goal of the next phase.** Decide how the 288 mm brain SRM should be reconstructed (support, start image, iterations, post-filter) so that rim streaks and edge overshoot are controlled on realistic, noisy data, and turn the insert-driven streak mechanism into a predictive metric for system design.

### Claim registry

| ID | Claim | Status | Evidence |
| --- | --- | --- | --- |
| C1 | Streak geometry is a property of H: voxel-to-pinhole lines, strongest at low N\_eff | Supported | Ideal LIR vs MLEM LIR, correlation 0.66–0.84 |
| C2 | MLEM displays coupling only where the estimate holds activity | Supported | E2, E5; Barrett 1994 linearisation |
| C3 | Uniform objects streak only when activity reaches the support edge | Supported (one object family) | E6, E7 |
| C4 | A shell started full adds streaks; ε = 0.01 removes them | Supported | E8 runs B, G, H; E9 runs B9, C9, E9c |
| C5 | Contour + ε = 0.01 elsewhere equals a hard contour support | Supported (noiseless, one object) | E9 run E9c vs D9, RMS ≈ 0.001 |
| C6 | Unresolvable cold inserts (rods) drive streaks at the object's own edge, with any support | Tentative | E9 polar views; E9b, one SRM, one slice |
| C7 | Insert errors reach other slices along oblique pinhole lines | Hypothesis | Image reading only |
| C8 | The bright edge ring is the Snyder (1987) ML edge overshoot | Supported | Overshoot 11–15 %, saturates, ripple, removed by a 10 mm post-filter |
| C9 | Edge overshoot is smaller and slower nearer the rim | Observed, unexplained | analyze\_edge\_overshoot.py |
| C10 | Margin alone removes rim streaks | Refuted for objects with inserts | E9 correction |
| C11 | Streaks are slow small-σ modes of H | Hypothesis | No spectrum computed |

### Candidate experiments

| ID | Question | Design | Tests | Cost |
| --- | --- | --- | --- | --- |
| X1 | Do rim streaks matter clinically? | Poisson noise at clinical counts, stop at 20–50 iterations, shrunk and full ACR | Clinical relevance of C3–C6 | \~1 day; Gate SRM, 75 s per run |
| X2 | Is the speckle Monte Carlo noise in H? | Repeat E2/E9c with a single-campaign SRM and with a lower-noise ray-traced SRM | Speckle source | \~1 day |
| X3 | Do insert errors travel along oblique lines? | Move the rod slab away from the sphere slice; vary rod size; overlay predicted voxel-to-pinhole lines on the error | C6, C7 | Hours (ray-traced, 15 s per run) |
| X4 | Why are shrunk-ACR streaks weaker? | Same insert set at edge radius 80, 95, 104 mm; with and without the support edge | C6, C9 | Hours |
| X5 | What is the spectrum of H? | Eigendecompose HHᵀ (45,625², \~8.3 GB); project phantoms on σ bands | C11 | \~1 day compute |
| X6 | How small must ε be, and is it safe with a wrong contour? | ε sweep (0, 10⁻³, 10⁻², 10⁻¹, 1); a phantom with activity outside the assumed contour | C4, C5 | Hours |
| X7 | 288 mm production SRM | Head phantom with scalp activity; contour support with ε = 0.01 vs uniform start | Implications | After the 288 mm Gate campaign |
| X8 | A streak metric that works | Matched filtering along predicted pinhole lines, validated on E6/E9 cases | All visual claims | Days |
| X9 | Edge overshoot control | Post-filter or resolution-kernel sieve (Snyder) vs iterations; trade-off with contrast recovery | C8, C9 | Hours |
| X10 | Which aperture pattern reduces rim streaks, compared with the current sequential cycle (four aperture sizes a₁ < a₂ < a₃ < a₄ repeated a₁…a₄ around each ring)? | Simulate each module with each of the four sizes once in gammart (73 × 4 blocks), then assemble any pattern from those rows without re-simulating; score from H alone (rim N\_eff map, ideal-LIR streak energy at rim voxels), then shrunk-ACR MLEM stripe RMS; confirm the best pattern with a Gate SRM | C1, C6; design metric (X8) | \~10 min SRM + minutes of scoring per pattern; Gate only for the finalist |

### Literature queries

- Local impulse response of MLEM or OSEM as a function of iteration number, linearised, emission tomography.
- Resolution and noise properties of multi-pinhole SPECT near the edge of the field of view; truncation and sampling completeness (Tuy, Orlov conditions) for stationary multi-pinhole systems.
- Edge (Gibbs) overshoot in resolution-modelled MLEM: dependence on position, iterations and post-filter; PSF-modelling artifacts in PET and SPECT.
- Support constraints and initial-image (start image) effects in MLEM; reconstruction with body-contour support.
- Streak and cross-talk artifacts from unresolved structures (rods) in multi-pinhole SPECT.
- Fast eigen-analysis of HHᵀ or the Fisher information for large tomographic systems.
- Aperture and pinhole-placement optimisation for stationary multi-pinhole SPECT: sampling-completeness, Fisher-information and task-based figures of merit.

### Working rules learned

- Write predictions down before running a test.
- Judge streaks at the object's own edge (polar view), not at a fixed radius.
- Trust images over scalar metrics until a metric is validated against images.
- Read a paper before citing it; mark memory-only citations.
- Distinguish edge overshoot (Snyder) from streaks; post-filtering treats the first, not the second.
