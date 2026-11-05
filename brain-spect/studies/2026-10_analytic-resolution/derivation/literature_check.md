# Literature check for `square_pinhole.md` and `crosscheck_tables.py`

Checked 30 October 2026 against the six PDFs in
`pytorch-optix/references/pinhole-collimator/`, each read in full (page images, every page including the
reference lists). Page numbers are journal page numbers. Abbreviations: **MM2020** = Metzler & Moore, IEEE TMI
39(4):833–843, 2020; **AM2004** = Accorsi & Metzler, IEEE TMI 23(6):750–763, 2004; **M2002** = Metzler, Bowsher,
Greer, Jaszczak, IEEE TMI 21(8):878–887, 2002; **MA2005** = Metzler & Accorsi, PMB 50:5005–5017, 2005;
**J2016** = Johnson, Moore, Metzler, PMB 61:2003–2013, 2016; **Mo2016** = Moore et al., Med Phys
43(12):6336–6346, 2016.

Angle conventions differ: MM2020 measures $\theta_x,\theta_y$ from the pinhole **axis** (projected angles in the
$xz$ and $yz$ planes), like our $\theta$; AM2004, M2002 and MA2005 measure $\theta$ from the pinhole **plane**
($\theta_{AM} = \pi/2 - \theta_{ours}$). All $\alpha$ are **full** acceptance angles except in Mo2016, where
$\alpha$ is the **half** opening angle.

## 1. Verdict table

| # | Claim (where) | Verdict | Evidence |
|---|---|---|---|
| 1a | MM2020 eq. (22) is the closed-form rectangular penetrative sensitivity; our §3.3 $A_{eff}(\theta,\varphi)$ equals it (§0.2, §2, §3.3, `crosscheck_tables.py`) | **confirmed**, with two wording fixes | Eq. (22), p. 838, transcribed in §2.1. Term-by-term equal to `area_eff_mm2020` (see §2.2). Fixes: (i) $\tau$ does not appear in eq. (22); it is the tapering function of eq. (29), which reduces to (22) for $\tau_x=\tau_y=1$; (ii) eq. (22) is $g_{pen}$ only, so $A_{eff} = w^2 + g_{pen}\,4\pi h^2/\cos^3\theta$ (the code does this, the §3.3 sentence omits the $w^2$) |
| 1b | MM2020 eq. (25) gives $A_{eff} = w_xw_y + \frac{w_x}{\mu}\tan\frac{\alpha_y}{2} + \frac{w_y}{\mu}\tan\frac{\alpha_x}{2} + \frac{2}{\mu^2}\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}$, = Paix form for the square (§2 row 2, §3.3, §4 item 4) | **confirmed** | Eq. (25), p. 838 (both lines transcribed in §2.1). For $w_x=w_y=w$, $\alpha_x=\alpha_y$: $w^2+2wt/\mu+2t^2/\mu^2$ |
| 1c | MM2020 geometry: eight half-planes, double-sided, no channel; source at $h(\tan\theta_x,\tan\theta_y,1)$ (§4 item 4) | **confirmed** | p. 834: "a rectangular-aperture pinhole collimator can be modeled as eight half planes … that intersect in a rectangle of dimensions $w_x$ and $w_y$"; planes 1–4 for $z\ge0$, 5–8 for $z\le0$; Fig. 2: $\vec r_0 = h(\tan\theta_x,\tan\theta_y,1)$. The same $\alpha_x$ ($\alpha_y$) is used above and below the plane, so asymmetric slopes $t_1\ne t_2$ are outside the model. Keel edges are mentioned only as future work (p. 842). Finite thicknesses $T_A$, $T_B$ enter only through the penumbra tapering (Fig. 4, eqs. 26–28) |
| 2a | MM2020 contains no resolution / FWHM formula (§4 item 4) | **confirmed** | No resolution equation anywhere. Resolution only qualitative: p. 833 "The resolution is determined by the aperture size and the amount of penetration"; p. 842 discusses separable resolutions and cites J2016 |
| 2b | MM2020 eqs. (26)–(29) penumbra tapering near the FOV edge (§4 item 4) | **confirmed** | Eqs. (26)–(29), p. 839, transcribed in §2.1 |
| 2c | Validated to 0.16 % (normal) and 0.29 % ($\theta_x=\theta_y=27°$) for $\mu=4$ mm⁻¹, $w=1$ mm (§4 item 4) | **confirmed** | p. 841: "for $\mu$ = 4 mm⁻¹ … and for $w_x = w_y$ = 1 mm, agreement to within 0.16% for normal incidence and 0.29% for $\theta_x = \theta_y$ = 27° (i.e., 90% of the way to the edge of the FOV in both x and y)". Context: $\alpha_x=\alpha_y=60°$, $h=40$ mm (Figs. 5–6); compared against numerical integrals of eq. (12) |
| 3a | AM2004 eqs. (4)–(5): round effective area / Paix diameter; $A_{eff}=\frac\pi4(d^2+2dt/\mu+2t^2/\mu^2)$ for the disk (§3.3) | **confirmed** | p. 751, §2.3. Round only (the integrand is $2\pi r'\,dr'$) |
| 3b | AM2004 eq. (22) $d_{re\parallel}$ and eq. (25) $d_{re\perp}$ as written in our §2 table and §3.2 | **confirmed** (exact transcription) | p. 753, §2.3. Our conversion of (25) to axis-measured $\theta$, $\sqrt{(d+\Delta L_k t\cos\theta)^2-\Delta L_k^2\sin^2\theta}$, is correct |
| 3c | AM2004 eq. (29) is exact for a parallel beam (§0.1, §2) | **confirmed** | p. 754: "the diameters take on the common form (in this case exact)", $d_{re}=d+\Delta L_k\tan\frac\alpha2$; normal incidence was derived with $\rho/h=0$, "which is exact for $h\to\infty$" |
| 3d | AM2004 formulas concern round knife edges only (§4 item 1) | **confirmed** | Fig. 1 / M2002 geometry: "two infinite back-to-back cones"; every $\Delta L$ is for a cone |
| 3e | AM2004 §V says the method "can be immediately applied to other pinhole edge shapes, provided that the appropriate formula for $\Delta L$ is used", "which is what §3 does" (§4 item 1) | **quote confirmed; reading should be softened** | p. 761, §V: "The equations developed apply only to knife-edge pinholes. However, the technique used to derive the resolution-equivalent diameters can be immediately applied to other pinhole edge shapes, provided that the appropriate formula for $\Delta L$ is used. For the important case of a keel-edge (channelized) pinhole …". "Edge shapes" means edge *profiles* (knife vs keel), not the aperture *outline*. Applying the method to a square outline is our extension, in its spirit but not their statement |
| 3f | AM2004 Appendix II is the 2-D parallel-plane calculation (§3.2) | **confirmed** | p. 761–762, "Derivation of the exact formula for the parallel resolution-equivalent diameter in the Cartesian plane", eqs. (53)–(62) |
| 3g | AM2004 (43)–(46): $d_{re} <$ Anger $<$ Paix at normal incidence for $k=0.5$ (§2 table, row "Anger / Paix") | **corrected (condition missing)** | Paix $>$ $d_{re}$ holds for all $\mu,d,\alpha$ if $k>1/e$ (eq. 45), and Paix $>$ Anger always (eq. 46). But $d_{re}<$ Anger only when $d(1+\ln k)>\frac{\ln^2k\tan(\alpha/2)}{2\mu}$ (eq. 43), i.e. $d>0.216$ mm for $t=1$, $\mu=3.63$ mm⁻¹. True for A–D ($w\ge0.556$ mm), but not unconditional |
| 4a | M2002 PRF with penetration eq. (6) (§4 item 2) | **confirmed** | p. 879, transcribed in §2.3. Round aperture; imaging plane parallel to the aperture plane |
| 4b | M2002 RMS definitions (7)–(8) (§2 table, §4 item 2) | **confirmed** | p. 880 |
| 4c | M2002 eq. (25): geometric RMS $=R/2$ (= $d/4$ per axis in the aperture plane) (§2 table, §3.5) | **confirmed** | p. 882; $R=d(h+b)/(2h)$ is the *image-plane* radius (eq. 9), so $R/2$ maps to $d/4$ in the aperture plane |
| 4d | M2002 eq. (2): projection scale factor $(h+b)/h$ (§3.2) | **confirmed** | p. 879 |
| 4e | M2002 p. 886: any aperture shape gives a geometric PRF of the same shape; AR angle-dependent (§4 item 2) | **confirmed** | p. 886, quoted in §2.3 |
| 4f | M2002 eq. (33) AR $<1$ (§3.5) | **confirmed** | p. 883; for $d=0$, AR $=(1-\gamma)^{1/2}$, $\gamma=\cot^2(\alpha/2)\cot^2\theta$ |
| 5a | MA2005 eqs. (5)–(6) are AM2004 (22) and (25) (§4 item 3) | **confirmed** | p. 5007, identical to AM2004 (22), (25) |
| 5b | MA2005 appendix A.1–A.3: $\theta$-dependent Paix/Anger forms; A.1 used in our §3.4 | **confirmed** | p. 5017; our §3.4 transcription of A.1 is exact |
| 5c | MA2005 experiment: $d_{re}$ confirmed for ⁵⁷Co and ¹³¹I, 1 and 3 mm apertures; Paix overestimates; Anger better but $\theta$-independent (§4 item 3) | **confirmed, one caveat to add** | Abstract and §5 (p. 5005, 5016): "(a) $d_{re}$ provides the best estimates of the experimental FWHM as a function of $\theta$ and of the direction in the plane of the pinhole, (b) Paix's expression for $d_e$ tends to overestimate the FWHM, (c) Anger's is a better approximation, but still cannot predict the dependence on $\theta$, and (d) the FWHM decreases with decreasing $\theta$". Caveat (p. 5016): "the ⁵⁷Co, d = 1 mm, data are less conclusive … there seems to be a systematic error of approximately 0.1 mm in this case". Apertures: W, $d=1.0$ mm / $\alpha=100°$ and $d=3.0$ mm / $\alpha=102.3°$ |
| 5d | MA2005 p. 5016: quadrature exact for Gaussians; box ⊗ box FWHM = max (§0.4, §2) | **confirmed** | p. 5016: "This approach is exact for Gaussian distributions. However, in the case of a rectangular distribution, which is often a good model for the geometric PSF of a pinhole since there are no penetrative tails, its convolution with an identical (or smaller) rectangular function will not change the FWHM. … In contrast, in all cases, the variance was increased" |
| 5e | MA2005 detector normal to the source line → $\sin\theta$ minification of the parallel direction (§3.2) | **confirmed** | p. 5008: "the data acquired with this experimental setup are minified in the parallel direction by a factor of $\sin\theta$" |
| 6a | J2016: ray-traced projections, geometric-mean FWHM over 0–45°, sensitivity with penetration, $\mu=3.64$ mm⁻¹, $\alpha=10$–$50°$, 0.3/0.5/1 mm (§3.6, §4 item 6) | **confirmed, needs precision** | §2.3, p. 2008–2009: one point source 25 mm from the pinhole centre (on axis), detector at 100 mm (M = 4), no detector blur; "profiles were formed along directions described by angles from 0 to 45 degrees with respect to the flat-to-flat direction by summing along the perpendicular direction. This is equivalent to calculating the Radon transform"; "The geometric means of the FWHM and FWTM values across all angles … were … used as estimates of spatial resolution". So: a Radon projection of a **normal-incidence** point-source projection (= LSF of a line source), angle = **in-plane profile direction**, not incidence angle. The plane in which widths are quoted is not stated. Sensitivity (§2.2.2.1): W, 3.64 mm⁻¹, 20 mm thick ($T_L=T_U=10$ mm), path-length attenuation per ray |
| 6b | J2016 gives no closed-form resolution formula (§4 item 6) | **confirmed** | The only equation in the paper is eq. (1), the normalized solid angle (FOV metric, no penetration) |
| 6c | J2016: 0.364 vs 0.414 mm for a 0.3 mm square at $\alpha=10°$ (§3.6, §4 item 6); "11–12 % sharper" (§3.6) | **confirmed; 11–12 % only from figure** | p. 2011: "for the 0.3 mm edge-length aperture with an acceptance angle of 10°, the FWHMs were 0.364, 0.387, and 0.414 mm for roundedness values of 0 (square), 0.5, and 1 (circle), respectively". Conditions: circle **sensitivity-matched** to within 0.1 % (including packing fraction; edge length enlarged, Fig. 9) and **FOV-matched** to within 0.5 % ($\alpha$ enlarged, Fig. 7). 0.364/0.414 = 0.879 (12 % narrower). Other sizes only in Fig. 11 (≈ 11–12 % by eye) |
| 6d | J2016: "no side/diagonal statement" (§4 item 6) | **corrected** | Fig. 6(c), p. 2009, plots FWHM and FWTM vs profile angle $\phi=0$–45° for a 0.5-roundedness example: FWHM falls from ≈1.4 mm (flat-to-flat) to ≈1.2 mm (45°). No text statement, but the graphical result exists and agrees with our §3.2 (LSF narrower across the diagonal) |
| 7a | Mo2016 eqs. (1)–(3) (§0.4, §2, §4 item 9) | **confirmed** | p. 6339, transcribed in §2.6. Eq. (2) cites AM2004 (their ref. 27); (1) and (3) cite Anger 1967 (ref. 26) |
| 7b | Mo2016 applies $d_{eff}=d+\ln2\tan\alpha/\mu$ to the square side (§4 item 9) | **confirmed** | p. 6339: "Using the formulas above, it was straightforward to show that a square-aperture hole size of 0.3 mm for the closest pinhole satisfies this constraint in both the axial and transaxial directions." |
| 7c | Mo2016 $\alpha$ = half-opening angle "in the direction considered" (§4 item 9) | **confirmed as half-angle; per-direction use implied, not stated** | p. 6339: "$\alpha$ is the aperture's half-opening angle described above"; p. 6338 describes "half-opening angles of the insert had to be 17.1° in the transaxial direction and 14.9° in the axial direction". The text never writes the formula per direction; it evaluates "both the axial and transaxial directions". $\mu_{PtIr}=4.56$ mm⁻¹. The reported resolutions (0.70–0.98 mm transverse, 0.71–1.09 mm axial) come from ray-traced point-source simulations including DOI, not from eqs. (1)–(3) |
| 8 | "No paper gives a closed-form resolution (FWHM) formula for a square knife edge with penetration" (§4 closing paragraph) | **supported for these six papers; not yet established for the literature** | See §3: none of the six has one; the reference lists contain unread candidates (Metzler/Moore/Park 2012, Xia 2013, Williams 2003, Zheng 2007), and the slit-slat literature (straight knife edges) is the most likely place for an equivalent of our side formula |

Other small points found while reading:

- §4 item 4, ref. status: MM2020 has now been read in full here; it can be upgraded from **[agent]** to **[full]**.
- MM2020's own reference [24] mixes two titles ("Preliminary investigation of imaging properties for
  sub-millimeter square pinholes", Med. Phys. 42(12):6933–6944, 2015); the Med. Phys. paper is titled
  "Investigation of imaging properties for submillimeter rectangular pinholes" (as Mo2016 ref. 21 and our
  §4 item 7 have it). Our citation is right.

## 2. Exact transcriptions

### 2.1 Metzler & Moore 2020

**Geometry and definitions** (pp. 834–835).
- Aperture: rectangle $w_x\times w_y$ in the plane $z=0$; "full-acceptance angles $\alpha_x$ and $\alpha_y$ in the
  $x$ and $y$ directions". Planes 1–4 for $z\ge0$, 5–8 for $z\le0$; normals, eq. (1):
  $\hat N_{1,3}=\big(\mp\cos\frac{\alpha_x}{2},0,\sin\frac{\alpha_x}{2}\big)$,
  $\hat N_{2,4}=\big(0,\mp\cos\frac{\alpha_y}{2},\sin\frac{\alpha_y}{2}\big)$,
  $\hat N_{5,7}=\big(\mp\cos\frac{\alpha_x}{2},0,-\sin\frac{\alpha_x}{2}\big)$,
  $\hat N_{6,8}=\big(0,\mp\cos\frac{\alpha_y}{2},-\sin\frac{\alpha_y}{2}\big)$; points of symmetry, eq. (2):
  $\vec P_{1,5}=(\frac{w_x}{2},0,0)$, $\vec P_{2,6}=(0,\frac{w_y}{2},0)$, $\vec P_{3,7}=(-\frac{w_x}{2},0,0)$,
  $\vec P_{4,8}=(0,-\frac{w_y}{2},0)$.
- Source: $\vec r_0 = h(\tan\theta_x,\tan\theta_y,1)$ (Fig. 2); $h$ is the perpendicular height above the aperture
  plane; $\theta_x$ is the angle from the $z$ axis in the $xz$ profile (Fig. 2), $\theta_y$ likewise.
- $\beta_{\pm u} = 1\pm\dfrac{\tan\theta_u}{\tan\frac{\alpha_u}{2}}$ (7).
- $\Lambda = h/|\vec v| \approx \big[1+\tan^2\theta_x+\tan^2\theta_y\big]^{-1/2}$ (10), "analogous to $\cos\theta$";
  $\Delta L = h\Lambda^{-1}\Delta t$ (11). Path lengths are kept to leading order in $1/h$ (eqs. 6, 9: "Dropping
  non-leading-order terms in $1/h$").
- $\mu$: linear attenuation coefficient. Sensitivity integral over the $z=0$ plane *excluding the aperture*:
  $$g_{pen}=\int\frac{\Lambda^3}{4\pi h^2}e^{-\mu\Delta L}\,dA \qquad (12)$$
- $\tau$: **not in eq. (22)**; it is the tapering function $\tau(\theta,h)$ of eq. (28), used only in eq. (29).

**Eq. (22)** (p. 838; the step after eq. 21, "Appendix III … shows in (48) that this simplifies to"):
$$
g_{pen}\approx\frac{\big[1+\tan^2\theta_x+\tan^2\theta_y\big]^{-2}}{4\pi h^2\mu}
\Big[w_x\Big(\tan^2\frac{\alpha_y}{2}-\tan^2\theta_y\Big)\cot\frac{\alpha_y}{2}
    +w_y\Big(\tan^2\frac{\alpha_x}{2}-\tan^2\theta_x\Big)\cot\frac{\alpha_x}{2}\Big]
$$
$$
+\frac{\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}\Big(1-\max\Big(\frac{\tan\theta_x}{\tan\frac{\alpha_x}{2}},\frac{\tan\theta_y}{\tan\frac{\alpha_y}{2}}\Big)\Big)}
       {4\pi h^2\mu^2\big[1+\tan^2\theta_x+\tan^2\theta_y\big]^{5/2}}
\Big[3\Big(1-\min\Big(\frac{\tan^2\theta_x}{\tan^2\frac{\alpha_x}{2}},\frac{\tan^2\theta_y}{\tan^2\frac{\alpha_y}{2}}\Big)\Big)
    -\Big(1-\max\Big(\frac{\tan\theta_x}{\tan\frac{\alpha_x}{2}},\frac{\tan\theta_y}{\tan\frac{\alpha_y}{2}}\Big)\Big)^2\Big].
\qquad (22)
$$
(The unsimplified line before it, p. 837, has the prefactor $\frac{\Lambda^4}{4\pi h^2\mu}\big(w_x\beta_{+y}\beta_{-y}\tan\frac{\alpha_y}{2}+w_y\beta_{+x}\beta_{-x}\tan\frac{\alpha_x}{2}\big)$ and $\frac{\Lambda^5}{4\pi h^2\mu^2}\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}(\dots)$.)

**Eq. (25)** (p. 838, §II-G, "at normal incidence (i.e., $\theta_x=\theta_y=0$)"):
$$
\frac{A_{eff}}{4\pi h^2}\approx\frac{w_xw_y}{4\pi h^2}+\frac{w_x\mu^{-1}\tan\frac{\alpha_y}{2}+w_y\mu^{-1}\tan\frac{\alpha_x}{2}}{4\pi h^2}
+\frac{2\mu^{-2}\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}}{4\pi h^2},
$$
$$
A_{eff}\approx\Big(w_x+\mu^{-1}\tan\frac{\alpha_x}{2}\Big)\Big(w_y+\mu^{-1}\tan\frac{\alpha_y}{2}\Big)+\mu^{-2}\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}.
\qquad (25)
$$

**Penumbra / tapering** (pp. 838–839). Penumbra region entered "for $\tan\theta_x>\tan\frac{\alpha_x}{2}-\frac{w_x}{2h}$
or $\tan\theta_y>\tan\frac{\alpha_y}{2}-\frac{w_y}{2h}$". Aperture thicknesses $T_A$ (above) and $T_B$ (below), Fig. 4:
$$\Delta=\frac{h}{h+T_B}\Big[\frac{w}{2}+T_B\Big(\tan\frac{\alpha}{2}-\tan\theta\Big)\Big]\qquad(26)$$
for $\tan\frac\alpha2-\frac{w}{2h}\le\tan\theta\le\tan\frac\alpha2+\frac{w}{2T_B}$; $\Delta=\frac w2$ for smaller $\tan\theta$, 0 otherwise.
$$\Delta'=\Big(\frac{h}{h-T_A}\Big)\Big[\frac w2+T_A\Big(\tan\frac\alpha2-\tan\theta\Big)\Big]\qquad(27)$$
for $\tan\frac\alpha2+\frac{w}{2h}\le\tan\theta\le\tan\frac\alpha2+\frac{w}{2T_A}$ (as printed); $\frac w2$ for smaller $\tan\theta$, 0 otherwise.
$$\tau(\theta,h)=\frac1w\big(\Delta+\Delta'\big)\qquad(28)$$
"for an aperture with parameters $\alpha$, $T_A$, and $T_B$ and for $h>T_A$". Eq. (29) is eq. (22) with $w_x\to w_x\tau_x$,
$w_y\to w_y\tau_y$ (the corner term is unchanged).

**Validity and geometry of eqs. (22)/(25).**
- Leading order in $1/h$ (parallel beam); the paper attributes its 0.16–0.29 % residuals "primarily … from dropping
  higher order terms in $1/h$" (p. 841).
- Eq. (22) has no tapering: the source must be outside the penumbra,
  $\tan\theta_u\le\tan\frac{\alpha_u}{2}-\frac{w_u}{2h}$ for $u=x,y$. Beyond the FOV edge
  ($\tan\theta_u>\tan\frac{\alpha_u}{2}$) the factor $(1-\max(\dots))$ turns negative and the formula is meaningless.
  The authors: "(22) offers identical results except near the edge of the field of view" (p. 842) and the
  agreement is excellent "except at the corner of the field of view" (p. 841).
- Written for $\theta_x,\theta_y\ge0$ (the first-quadrant integration regions of Fig. 3; no absolute values in eq. 22).
  Other quadrants follow by the symmetry of the aperture.
- The derivation sums 4 aligned (1–5, 2–6, 3–7, 4–8) and 8 adjacent plane pairs (Tables I, II, IV); "the other
  four combinations of opposed planes do not have a valid path length within the FOV" (p. 835).
- Geometry: double-sided, channel-less knife edge (eight half-planes meeting at the aperture rectangle), **same**
  $\alpha_x$ above and below the plane and same $\alpha_y$ above and below. Validation plots: $\alpha=60°/60°$, $h=40$ mm,
  $T_A=T_B=40$ mm; $\alpha=60°/90°$, $h=20$ mm, $T_A=T_B=5$ mm; $\mu=1$–32 mm⁻¹ (pp. 839–840).

### 2.2 `crosscheck_tables.py` against eq. (22): symbol-by-symbol

`area_eff_mm2020(w, t, theta, phi, mu)`, lines 29–37, returns $A_{eff}=w^2+g_{pen}\cdot4\pi h^2/\cos^3\theta$
with eq. (22) for $w_x=w_y=w$, $\tan\frac{\alpha_x}2=\tan\frac{\alpha_y}2=t$:

| eq. (22) | code | check |
|---|---|---|
| $\tan\theta_x$, $\tan\theta_y$ | `tx = tan(theta) cos(phi)`, `ty = tan(theta) sin(phi)` | correct: for $\vec r_0=h(\tan\theta_x,\tan\theta_y,1)$, $\tan^2\theta=\tan^2\theta_x+\tan^2\theta_y$ and the azimuth is $\varphi$ |
| $[1+\tan^2\theta_x+\tan^2\theta_y]^{-2}$ | $\cos^4\theta$, divided by $\cos^3\theta$ → `c` | correct |
| $w_x(\tan^2\frac{\alpha_y}2-\tan^2\theta_y)\cot\frac{\alpha_y}2+w_y(\tan^2\frac{\alpha_x}2-\tan^2\theta_x)\cot\frac{\alpha_x}2$, over $\mu$ | `c * w / (mu * t) * (2 t t - tx tx - ty ty)` | correct (equal for a square) |
| $\tan\frac{\alpha_x}2\tan\frac{\alpha_y}2$, $[\dots]^{-5/2}/\cos^3\theta$ | `t * t * c * c / mu**2` | correct ($\cos^5/\cos^3=\cos^2$) |
| $1-\max(\tan\theta_x/\tan\frac{\alpha_x}2,\tan\theta_y/\tan\frac{\alpha_y}2)$ | `1 - M`, `M = max(|tx|,|ty|)/t` | correct; the code's absolute values extend the first-quadrant formula by symmetry (the paper has none) |
| $\min(\tan^2\theta_x/\tan^2\frac{\alpha_x}2,\tan^2\theta_y/\tan^2\frac{\alpha_y}2)$ | `mm*mm`, `mm = min(|tx|,|ty|)/t` | correct |
| $3(1-\min)-(1-\max)^2$ | `3 * (1 - mm*mm) - (1 - M)**2` | correct |
| geometric term | `w * w` | correct ($w_xw_y\Lambda^3/(4\pi h^2)\times4\pi h^2/\cos^3\theta$) |

**No transcription error.** Differences are presentational only:
1. Docstring line 30 and §3.3 of `square_pinhole.md` say "eq. (22) with $\tau_x=\tau_y=1$"; $\tau$ belongs to eq. (29).
   Say "eq. (22) (= eq. (29) with $\tau_x=\tau_y=1$)".
2. The code is eq. (22) rearranged into the same variables as our derivation, not a literal transcription. The
   comparison is still independent, because `square_pinhole_model.area_eff_square` sums the piecewise strip and
   corner integrals (`_corner_integral`) and does not use the closed form. If you want the check to show the
   paper's form explicitly, add a literal transcription in $\tan\theta_x$, $\tan\theta_y$, $\tan\frac{\alpha_x}2$,
   $\tan\frac{\alpha_y}2$, $h$. I wrote one (`/tmp/mm22_check.py`) but could not run it in this session (no
   permission to run Python). The algebraic identity above is checked by hand.
3. Both the code and MM2020 assume one slope per axis; our CSG has $t_1\ne t_2$ (object/detector side). Using
   $t=1$ (or $t_h$) is our approximation, outside MM2020's model.

### 2.3 Accorsi & Metzler 2004

$\theta$ from the pinhole plane, $\alpha$ full opening angle, $h$ the source height, $d$ the diameter.
$$g=\frac{d^2\sin^3\theta}{16h^2}\qquad(1)\qquad\qquad g=\frac{d_e^2\sin^3\theta}{16h^2}\qquad(2)\qquad\qquad
d_e=\sqrt{d\Big(d+\frac2\mu\tan\frac\alpha2\Big)}\qquad(3)\quad\text{(Anger)}$$
$$\frac\pi4d_e^2=\frac\pi4d^2+\int_{d/2}^{\infty}2\pi r'e^{-2\mu(r'-\frac d2)\cot(\frac\alpha2)}dr'\qquad(4)$$
$$d_e=\sqrt{d\Big(d+\frac2\mu\tan\frac\alpha2\Big)+\frac2{\mu^2}\tan^2\frac\alpha2}\qquad(5)\quad\text{(Paix)}$$
$$\lambda_g=d\Big(1+\frac1M\Big)\quad(6)\qquad\lambda_s=\sqrt{\lambda_g^2+\lambda_i^2}=\sqrt{d^2\Big(1+\frac1M\Big)^2+\frac{FWHM_i^2}{M^2}}\quad(7)\qquad
e^{-\mu\Delta L}=k\quad(8)\qquad\Delta L=\Delta L_k\equiv-\frac{\ln k}\mu\quad(9)$$
(p. 751; eq. 4 is the parallel-ray, normal-incidence sensitivity argument of Smith & Jaszczak; round only.)
$$d_{re\parallel}\approx d+\Delta L_k\Big(\tan^2\frac\alpha2-\cot^2\theta\Big)\cot\frac\alpha2\sin\theta\qquad(22)\ \text{(p. 753)}$$
$$d_{re\perp}\approx\sqrt{\Big(d+\Delta L_k\tan\frac\alpha2\sin\theta\Big)^2-\Delta L_k^2\cos^2\theta}\qquad(25)\ \text{(p. 753)}$$
$$d_{re}=d+\Delta L_k\tan\frac\alpha2\qquad(29)\ \text{(p. 754, normal incidence, "in this case exact")}$$
$$d(1+\ln k)>\frac{\ln^2k\tan\frac\alpha2}{2\mu}\quad(43)\qquad d>\frac{\ln^2k\tan\frac\alpha2}{2\mu(1+\ln k)}\quad(44)$$
$$(5)^2-(29)^2=2d\frac{1+\ln k}\mu\tan\frac\alpha2+\frac{2-\ln^2k}{\mu^2}\tan^2\frac\alpha2\quad(45)\qquad
(5)^2-(3)^2=\frac2{\mu^2}\tan^2\frac\alpha2>0\quad(46)$$
(p. 760). Validity of (22), (25): zone I of Fig. 3, $\tan\frac\alpha2\ge\cot\theta+\frac d{2h}$ (18), and
$\rho/h\to0$ (parallel beam). All for the round knife edge ("two back-to-back cones").

§V (p. 761), verbatim: "The equations developed apply only to knife-edge pinholes. However, the technique used to
derive the resolution-equivalent diameters can be immediately applied to other pinhole edge shapes, provided that
the appropriate formula for $\Delta L$ is used. For the important case of a keel-edge (channelized) pinhole and
parallel beam at $\theta=90°$, however, exact knowledge of $\Delta L$ is not necessary to predict that the
full-width remains unchanged for channel heights shorter than $\Delta L_k$."

§V also: "Stating the resolution of a pinhole system cannot accurately be done with a single number since the
effective diameter depends on incidence angle and direction" (p. 760), and the remark that the widest chord need
not be a diameter (§IV).

### 2.4 Metzler et al. 2002

$\theta$ from the aperture plane; imaging plane parallel to the aperture plane, a distance $b$ below it.
$$\vec g(t)=\vec S+\frac{h+b}h\vec D=\frac{h+b}h\vec f(t)-\frac bh\vec S\qquad(2)$$
$$\mathrm{PRF}=\begin{cases}\dfrac{\sin^3\theta}{4\pi(h+b)^2}, & r\le\dfrac{d(h+b)}{2h}\\[2ex]
\dfrac{\sin^3\theta}{4\pi(h+b)^2}e^{-\mu\Delta L}, & r>\dfrac{d(h+b)}{2h}\end{cases}\qquad(6)\ \text{(p. 879; }\Delta L\text{ from eq. 5)}$$
$$\mathrm{RMS(longitudinal)}=\sqrt{\overline{x^2}-\bar x^2},\qquad\mathrm{RMS(transverse)}=\sqrt{\overline{y^2}-\bar y^2}\qquad(7)$$
$$\mathrm{RMS(longitudinal)}=\sqrt{\frac{\int_0^\infty dr\int_0^{2\pi}d\beta\,\mathrm{PRF}(r,\beta)r^3\cos^2\beta}{\int_0^\infty dr\int_0^{2\pi}d\beta\,\mathrm{PRF}(r,\beta)r}}=\sqrt{\frac{I^1_{x^2}+I^2_{x^2}}{N^1_{x^2}+N^2_{x^2}}}\qquad(8)\ \text{(p. 880)}$$
$$\mathrm{RMS}=\sqrt{\frac{I^1_{x^2}}{N^1_{x^2}}}=\sqrt{\frac{I^1_{y^2}}{N^1_{y^2}}}=\frac R2,\quad R=\frac{d(h+b)}{2h}\qquad(25)\ \text{(p. 882, infinite attenuation)}$$
p. 886, verbatim: "The AR of the PRF has geometric and penetrative components. The geometric component is constant
and depends only on the shape of the aperture. For circular apertures, the projection onto a parallel imaging plane
is always circular, independent of angle. The retention of the aperture shape is independent of the shape used so
that any other aperture shape would result in the geometric PRF having the same shape as the aperture. The AR of
the penetrative component is dependent on angle."

### 2.5 Metzler & Accorsi 2005

$$d_{re\parallel}=d+\Delta L_k\Big(\tan^2\frac\alpha2-\cot^2\theta\Big)\cot\frac\alpha2\sin\theta\qquad(5)$$
$$d_{re\perp}=\sqrt{\Big(d+\Delta L_k\tan\frac\alpha2\sin\theta\Big)^2-\Delta L_k^2\cos^2\theta}\qquad(6)\ \text{(p. 5007)}$$
with $\Delta L_k=\Delta L_{0.5}=-\ln0.5/\mu=(\ln2)/\mu$ for FWHM. Appendix (p. 5017):
$$\frac{d^2\sin^3\theta}{16h^2}+\frac{\sin^5\theta\tan^2\frac\alpha2}{8h^2\mu^2}\Big(1-\frac{\cot^2\theta}{\tan^2\frac\alpha2}\Big)^{\frac12}
\Big[1-\frac{\cot^2\theta}{\tan^2\frac\alpha2}+\mu d\csc\theta\cot\frac\alpha2\Big]=\frac{d_{se}^2\sin^3\theta}{16h^2}\qquad(A.1)$$
$$d_{se}=\Big\{d^2+2\mu^{-2}\sin^2\theta\tan^2\frac\alpha2\Big(1-\frac{\cot^2\theta}{\tan^2\frac\alpha2}\Big)^{\frac12}
\Big[1-\frac{\cot^2\theta}{\tan^2\frac\alpha2}+\mu d\csc\theta\cot\frac\alpha2\Big]\Big\}^{\frac12}\qquad(A.2)$$
$$d_{se}=\Big\{d^2+2\mu^{-2}\sin^2\theta\tan^2\frac\alpha2\Big(1-\frac{\cot^2\theta}{\tan^2\frac\alpha2}\Big)^{\frac12}\mu d\csc\theta\cot\frac\alpha2\Big\}^{\frac12}\qquad(A.3)$$
(A.3 from A.2 with $\mu d\csc\theta\cot\frac\alpha2\gg1$; both reduce to (2) and (3) at $\theta=\pi/2$.)

### 2.6 Moore et al. 2016 (p. 6339)

$$\mathrm{res}_{pin}=d_{eff}\frac{M+1}M\qquad(1)\qquad M=(r_{det}-r_{pin})/r_{pin}$$
$$d_{eff}=d+\frac{\ln(2)\tan\alpha}\mu\qquad(2)$$
"where $d$ is the actual hole size to be determined as described below, $\alpha$ is the aperture's half-opening angle
described above, and $\mu$ is the linear attenuation coefficient of the PtIr alloy (4.56 mm⁻¹)."
$$\mathrm{res}_{sys}=\sqrt{\mathrm{res}_{pin}^2+(\mathrm{res}_{int}/M)^2}\qquad(3)$$
("approximately"; $\mathrm{res}_{int}\approx3.5$ mm FWHM). Eq. (2) with half-angle $\alpha$ is AM2004 (29) with
$\tan(\alpha_{full}/2)$. Half-angles 17.1° transaxial, 14.9° axial (p. 6338); 87 inserts with 0.3 mm square apertures.

### 2.7 Johnson et al. 2016

Only equation: $\mathrm{NSA}=\dfrac{A}{4\pi|\vec r|^3}(\vec r\cdot\hat z)$ (1), the normalized solid angle used as a
FOV metric, "No penetration was included in this calculation". Resolution is purely numerical (§2.3, quoted in
row 6a).

## 3. Absence claim

**Claim (§4 closing paragraph):** "No paper gives a closed-form *resolution* (FWHM) formula for a square knife
edge with penetration; the Metzler group applies the AM2004 normal-incidence formula to the side length (ref. 9)
and otherwise ray-traces (ref. 6)."

**Within the six papers: supported.**
- MM2020: sensitivity only (eqs. 22, 25, 29); no width formula.
- AM2004, M2002, MA2005: round knife edge only.
- J2016: square and rounded-square apertures, resolution by ray-traced projections only.
- Mo2016: square apertures, normal-incidence $d_{eff}=d+\ln2\tan\alpha/\mu$ (AM2004 eq. 29) applied to the side,
  with the half-angle of each direction; no oblique-incidence form.

**In the wider literature: not established.** The reference lists contain square/rectangular-pinhole papers that
were not read (abstract or nothing). Candidates, most likely first:

1. Metzler SD, Moore SC, Park M-A. Design of a new small-animal SPECT system based on rectangular pinhole aperture.
   *2012 IEEE NSS/MIC Conf. Rec.*, Anaheim, pp. 3815–3820. (MM2020 [28], J2016, Mo2016 [17].) The design paper of
   the rectangular-pinhole system; the most likely place for a per-direction rectangular $d_{re}$, possibly
   oblique.
2. Xia D, Park M-A, Moore SC, Metzler SD. Preliminary investigation of imaging properties for sub-millimeter square
   pinholes. *2013 IEEE NSS/MIC Conf. Rec.*, pp. 1–5. doi:10.1109/NSSMIC.2013.6829173. (J2016.)
3. Xia D, Moore SC, Park M-A, Cervo M, Metzler SD. Investigation of imaging properties for submillimeter rectangular
   pinholes. *Med Phys* 2015;42(12):6933–6944. doi:10.1118/1.4935200. (MM2020 [24], Mo2016 [21].) Our §4 item 7
   relies on the Undermind agent ("no $\mu$-explicit sensitivity or resolution formula"); worth a direct read.
4. Williams MB, Stolin AV, Kundu BK. Investigation of efficiency and spatial resolution using pinholes with small
   pinhole angle. *IEEE Trans Nucl Sci* 2003;50(5):1562–1568. doi:10.1109/TNS.2003.817380 (DOI from memory).
   (MA2005, MM2020 [23], Mo2016 [20].) Cited by MA2005 for the $\theta$ dependence of the width.
5. Williams MB et al. Square cross-section pinhole collimators for small animal SPECT. Academy of Molecular Imaging
   meeting, Madrid, 2003. (MM2020 [27].) Abstract only; tungsten-polymer square pinholes, MC vs experiment.
6. Zheng Y, Li H, Wang J, Stolin AV, Pole J, Williams MB. Image reconstruction for small animal SPECT with two
   opposing half cones. *Proc SPIE* 6498, Computational Imaging V, 649804 (2007). (J2016.) First documented square
   pinholes (0.5, 0.75, 1 mm, tungsten-epoxy).
7. Metzler SD, Xia D, Moore SC. Analytic determination of rectangular-pinhole sensitivity with penetration.
   *2014 IEEE NSS/MIC Conf. Rec.*, pp. 1–5. (MM2020 [32].) Conference version of MM2020, sensitivity only; low
   priority.
8. Moore SC, Park M-A, Xia D, Metzler SD. Dual-resolution microSPECT mouse imaging using a triple-head SPECT system.
   *2013 IEEE NSS/MIC Conf. Rec.*, M25-1. (Mo2016 [23].) Likely the same eqs. (1)–(3) as Mo2016.
9. Deprez K, Pato LRV, Vandenberghe S, Van Holen R. Characterization of a SPECT pinhole collimator for optimal
   detector usage (the lofthole). *Phys Med Biol* 2013;58(4):859–885. (MM2020 [29], J2016.) Round aperture with
   rectangular windows; has analytic resolution/sensitivity, reportedly without penetration.

Round-aperture references in the lists, for completeness, not candidates: Smith & Jaszczak, *PMB* 1998;43:761–775
(M2002 [26]); Wang, Jaszczak, Coleman, *IEEE TNS* 1996;43(6):3272–3277 (M2002 [25]); Metzler et al., *IEEE TMI*
2001;20(8):730–741; Smith & Jaszczak, *Med Phys* 1997;24(11):1701–1709.

**Outside the six reference lists, a closer prior-art risk: slit-slat collimation.** A slit is a straight,
translation-invariant knife edge, which is exactly the situation of our square *side* (§3.2: "a straight edge is
translation-invariant along $x$"). The Metzler/Accorsi group derived slit resolution with penetration at oblique
incidence by the same $\Delta L_k$ method. If their transverse slit formula is
$w+\Delta L_k(\tan^2\frac\alpha2-\cot^2\theta_{AM})\cot\frac\alpha2\sin\theta_{AM}$-type, our side formulas $W_x$,
$W_y$ are already published for slits, and the novelty is only in applying it to the two sides of a square, plus
the corners, diagonal and effective area. Candidates (citations from memory, **not** from these PDFs; verify before
quoting):
- Metzler SD, Accorsi R, Novak JR, Ayan AS, Jaszczak RJ. On-axis sensitivity and resolution of a slit-slat
  collimator. *J Nucl Med* 2006;47(11):1884–1890.
- Accorsi R, Novak JR, Ayan AS, Metzler SD. Derivation and validation of a sensitivity formula for slit-slat
  collimation. *IEEE Trans Med Imaging* 2008;27(5):709–722.
- Novak JR, Ayan AS, Accorsi R, Metzler SD. Verification of the sensitivity and resolution dependence on the
  incidence angle for slit-slat collimation. *Phys Med Biol* 2008;53:953–966. (Listed among the publisher's related
  articles on the MA2005 cover page.)

**Suggested wording for §4** until these are checked: "None of the papers we read gives a closed-form FWHM for a
square or rectangular knife edge with penetration at oblique incidence. The Metzler group applies the AM2004
normal-incidence formula to the side length with the half-angle of each direction (Moore et al. 2016) and otherwise
ray-traces (Johnson et al. 2016). Straight-edge (slit) resolution formulas from the slit-slat literature may
coincide with our side formulas and have not been checked."

## 4. Corrections for `square_pinhole.md` and `crosscheck_tables.py`

1. §3.3 (and `crosscheck_tables.py` docstring, line 30): "Metzler & Moore 2020 eq. (22) (with $\tau_x=\tau_y=1$, …)
   multiplied by $4\pi h^2/\cos^3\theta$" → "$w^2$ plus Metzler & Moore 2020 eq. (22) (their penetrative
   $g_{pen}$; eq. (29) with $\tau_x=\tau_y=1$), for $w_x=w_y$, $\alpha_x=\alpha_y$, multiplied by
   $4\pi h^2/\cos^3\theta$". Add the validity condition: outside the penumbra,
   $\tan\theta_{x,y}\le\tan\frac\alpha2-\frac w{2h}$, leading order in $1/h$.
2. §2 table, row "Anger / Paix as resolution widths": add the condition of AM2004 eq. (43): $d_{re}<$ Anger only for
   $d>\ln^2k\tan\frac\alpha2/[2\mu(1+\ln k)]=0.216$ mm here (met by A–D); Paix $>d_{re}$ holds for every $d$ when
   $k>1/e$.
3. §4 item 1: AM2004 §V speaks of other edge *profiles* (its example is the keel edge). Rephrase: "§V notes the
   method carries over to other edge shapes given the right $\Delta L$; §3 applies it to a square outline."
4. §4 item 3: add MA2005's caveat that the ⁵⁷Co, 1 mm data are "less conclusive" (≈0.1 mm systematic offset).
5. §4 item 4: status **[full]**. Geometry note: same $\alpha$ above and below the aperture plane (our $t_1\ne t_2$ is
   outside the model).
6. §4 item 6 and §3.6: J2016 widths are Radon projections (line-source profiles) of an **on-axis** point source,
   averaged geometrically over the in-plane profile direction 0–45°, no detector blur, circle enlarged to match
   sensitivity (incl. packing fraction) and FOV. Replace "no side/diagonal statement" with "Fig. 6(c) shows the
   FWHM falling from the flat-to-flat to the 45° direction (≈1.4 → 1.2 mm, rounded example), no closed form".
   "11–12 %" is read from Fig. 11; only 0.364/0.414 mm (0.3 mm, 10°) is in the text.
7. §4 item 9: "($\alpha$ the half-opening angle in the direction considered)" → "($\alpha$ the half-opening angle,
   17.1° transaxial / 14.9° axial; applied in both directions)". The paper's reported resolutions are ray-traced, not
   from eqs. (1)–(3).
8. §4 closing paragraph: soften as in §3 above, pending the candidate list and the slit-slat papers.

No numerical result in `square_pinhole.md` or `crosscheck_tables.py` changes: every equation transcription
(MM2020 22, 25; AM2004 1, 4–7, 9, 22, 25, 29; M2002 2, 6–8, 25; MA2005 5–6, A.1–A.3; Mo2016 1–3) is correct.

## 4. Wider search for a closed-form square / slit resolution with penetration (2026-10-30)

Undermind deep search "Closed-form resolution of square, rectangular and slit knife-edge apertures with penetration"
(workspace "GPU Monte Carlo & System Response Matrix", 34 relevant papers), plus targeted reads.

**Search summary:**
- **Round pinholes:** analytic penetrative resolution exists (AM2004, Acc05 asymmetric knife edge, Metzler 2002).
- **Rectangular pinholes:** analytic penetrative sensitivity exists (M&M 2020, Metzler 2014 conference version). No closed-form resolution was found.
- **Slit-slit:** sensitivity with effective penetrative slit widths (Ayan 2010).
- **Slit-slat:** geometric PSF and resolution (Li 2009).
- The search found no square or rectangular oblique-incidence penetrative resolution formula. It cannot prove absence.

**Read in full:**
- **Xia et al. 2015 (Med Phys 42:6933):** no resolution formula of any kind. It covers sensitivity and FOV only; resolution is mentioned qualitatively.
- **Li et al. 2009 (PMB 54:1469):** a geometric slit-slat resolution, R_tr = sqrt(((h+f)w/f)^2 + (h R_i/f)^2), eq. 51. For penetration it says to substitute an effective slit width w_eff = w + 2/(μκ), eq. 21, with κ from the edge path-length factor (ΔL = κ(|x| − w/2)), citing Accorsi et al. 2008 and Novak et al. 2008. That w_eff is the slit analogue of a sensitivity-effective width (the 2/(μκ) integral). The FWHM analogue would be w + 2 ln2/(μκ) per pair of edges, which is our side formula when κ is evaluated for our edge geometry. **So the slit literature contains the same building block (a straight knife edge with an incidence-dependent κ).** Our square side widths should be presented as the square-aperture application of that straight-edge result and of AM2004, not as an entirely new formula.

**Still unread (paywalled, most important first):**
1. Novak JR, Ayan AS, Accorsi R, Metzler SD. Verification of the sensitivity and resolution dependence on the incidence angle for slit-slat collimation. *Phys Med Biol* 2008;53(4):953-966. doi:10.1088/0031-9155/53/4/009. This is likely the slit resolution with penetration vs incidence angle.
2. Accorsi R, Novak JR, Ayan AS, Metzler SD. Derivation and validation of a sensitivity formula for slit-slat collimation. *IEEE TMI* 2008;27(5):709-722. doi:10.1109/TMI.2007.912395. It defines the slit κ and w_eff.
3. Accorsi R, Metzler SD. Resolution-effective diameters for asymmetric-knife-edge pinhole collimators. *IEEE TMI* 2005;24(12):1637-1646. doi:10.1109/TMI.2005.857229.
4. Metzler SD, Moore SC, Park M-A. Design of a new small-animal SPECT system based on rectangular pinhole aperture. *2012 IEEE NSS/MIC* 3815-3820. doi:10.1109/NSSMIC.2012.6551876.

**Recommended wording now:** "The sensitivity follows Metzler & Moore (2020). For the resolution we apply the straight-knife-edge penetration model (as used for slits, Accorsi et al. 2008; Novak et al. 2008) and Accorsi & Metzler (2004) to the four edges of the square, giving per-side widths at oblique incidence and the √2 diagonal. To our knowledge, this combination has not been written out for square apertures." Re-check after reading items 1-4.

## 5. Slit-slat and asymmetric knife-edge papers (2026-10-30)

Items 1–4 of the §4 list, each read in full from the page images (every page, including the reference lists).
Abbreviations: **N2008** = Novak, Ayan, Accorsi, Metzler, *PMB* 53:953–966, 2008; **A2008** = Accorsi, Novak, Ayan,
Metzler, *IEEE TMI* 27(5):709–722, 2008; **AM2005b** = Accorsi & Metzler, *IEEE TMI* 24(12):1637–1646, 2005
(asymmetric knife edge; "b" to keep it apart from MA2005); **MMP2012** = Metzler, Moore, Park, *2012 IEEE NSS/MIC
Conf. Rec.*, M21-43, pp. 3815–3820. Numbers below: $\mu = 3.63$ mm⁻¹, $t = 1$, $\theta = 30°$ (ours, from the axis),
$\varphi = 0$, $\Delta L_{0.5} = \ln2/\mu = 0.19095$ mm, knife-edge plane.

### 5.1 Closed-form widths with penetration (Q1)

| paper | straight edge (slit) | square / rectangle | oblique incidence | closed form with penetration |
|---|---|---|---|---|
| N2008 | yes: eq. (7), taken over from AM2004 eq. (22), not derived | no | yes, one angle | yes |
| A2008 | yes: eqs. (26)–(27) $\Delta L$, (30) $w_{se}$, (31) $w_{re}$, derived | no | yes, two angles ($\theta$, $\phi_0$) | yes |
| AM2005b | no: round aperture, asymmetric cones | no | yes | yes: ∥ eqs. (14), (33); ⊥ eqs. (17), (38)–(39) |
| MMP2012 | no | square; no equation in the paper | no | no |

**N2008** (p. 956):
$$R(\text{transaxial})=\left[R_g^2+\left(\frac{h}{f}R_i\right)^2\right]^{\frac12}=\left[w^2\frac{(h+f)^2}{f^2}+\left(\frac{h}{f}R_i\right)^2\right]^{\frac12}\qquad(5)$$
$$w_{\rm re}=w-\frac{\ln k}{\mu}\sin\theta\cot\frac{\alpha}{2}\left(\tan^2\frac{\alpha}{2}-\cot^2\theta\right)\qquad(7)$$
- Definitions: "$k$ describes the fraction $k$ of the maximum of the PSF used in the definition of resolution (i.e.
  $k = 0.5$ for FWHM), $\alpha$ is the full acceptance angle and $\mu$ is the linear attenuation coefficient".
- $\theta$ is "the angle formed by the line from the photon source to the center of the slit and the plane of the
  slit" (abstract, p. 953).
- $R_g$: geometric FWHM. $R_i$: intrinsic FWHM. $f$: focal length. $h$: source height above the slit plane.
- Status (p. 956): "Accorsi and Metzler (2004) derived a $\theta$-dependent, resolution-effective diameter that
  accounts for penetration for a double-knife edge pinhole collimator. A reasonable choice is to apply this effective
  diameter $w_{re}$ in the transaxial direction for slit–slat". So it is borrowed, not derived.
- Experiment: tungsten slit "arranged at a 90° acceptance angle" ($t = 1$, like ours); $w = 2.03$, 4.06 mm; ⁵⁷Co;
  $h = 45.1$, 62.6, 80.1 mm; $58° < \theta < 122°$. The source was "centered over the axial extent of the slit", so
  only in-plane incidence was tested.
- Result (p. 965): "(5) using $w_{re}$ agrees well with the MC data"; the experimental data are "about 10% higher"
  (cause not identified); "slit penetration may be a secondary effect for slit–slat transaxial resolution".

**A2008** (p. 713):
$$\Delta L=2\frac{\cot\frac{\alpha}{2}}{\sin\phi}\,\frac{|x|-\frac{w}{2}}{1-\left(\cot\theta-\frac{x}{h}\right)^2\cot^2\frac{\alpha}{2}}\qquad(26)$$
for $|x|\ge w/2$ and 0 otherwise ("This result is exact"). With the parallel-beam hypothesis ($x/h = 0$):
$$\Delta L\approx\frac{2}{\sin\phi_0}\,\frac{\cot\frac{\alpha}{2}}{1-\cot^2\frac{\alpha}{2}\cot^2\theta}\left(|x|-\frac{w}{2}\right)\qquad(27)$$
$$(\dots)=(y_2-y_1)\frac{h}{H}\left[w+\frac{\sin\phi_0}{\mu}\left(1-\cot^2\frac{\alpha}{2}\cot^2\theta\right)\tan\frac{\alpha}{2}\right]\qquad(28)$$
$$w_{se}=\left[w+\frac{1}{\mu}\left(1-\cot^2\frac{\alpha}{2}\cot^2\theta\right)\sin\phi_0\tan\frac{\alpha}{2}\right]\qquad(30)$$
$$w_{re}=w-\frac{\ln k}{\mu}\sin\phi_0\cot\frac{\alpha}{2}\left(\tan^2\frac{\alpha}{2}-\cot^2\theta\right)\qquad(31)$$
$$R=\sqrt{w^2\left(1+\frac{h}{f}\right)^2+R_i^2\left(\frac{h}{f}\right)^2}\qquad(32)$$

Definitions and geometry (p. 710):
- The slit lies along $y$ in the plane $z = 0$, has width $w$ and "is considered infinite in the $y$ direction".
  The source is at $P(x_P = h\cot\theta,\ y_P,\ z_P = h)$, so $\theta$ is the incidence angle **projected on the
  transaxial ($xz$) plane**, measured from the slit plane; eq. (14) gives $\cot\theta = (x_P - x_0)/H$.
- $\phi$ is "the angle between the $xy$ plane and the photon path", i.e. the true incidence angle from the slit
  plane. $\phi_0$ (eq. 11) is that angle for the ray through the slit centre.
- $\alpha$ is the full acceptance angle of a symmetric double knife edge (Fig. 1). $k$ and $\Delta L_k$ are as in
  AM2004.

Assumptions:
- $w_{se}$: "the photon flux can be treated as constant over the area of the slit that passes photons and … all
  photons have the same incidence angle $\phi_0$".
- $w_{re}$: "the width that a (hypothetic) slit not affected by penetration must have to result in the same
  full-width at $k$ maximum (FW$k$M) … measured in the direction perpendicular to the slit … The profile … is given
  by $\exp[-\mu\Delta L(x)]$, with $\Delta L(x)$ given by (27)."
- p. 713, verbatim: "In the case $y_0 = y_P$, for which $\phi_0 = \theta$, the geometry becomes planar and identical
  to that of the resolution-effective diameter of a double-knife edge pinhole in the parallel direction [16].
  Correctly, under these conditions, (31) is identical in the two cases. For the same reason, it is expected that the
  expression of $w_{re}$ for slits with asymmetric profiles will be the same as the literature expression of $w_{re}$
  in the parallel direction for asymmetric profiles of the pinhole [18]." ([16] = AM2004, [18] = AM2005b.)

Validation (§IV-E, Figs. 7–8, p. 715–717):
- MC with path-length weighting, $\alpha = 90°$, ⁹⁹ᵐTc ($\mu = 3.40$ mm⁻¹, "exclusive of coherent scattering") and
  ¹³¹I ($0.401$ mm⁻¹).
- Runs: $w = 0$–5 mm at normal incidence; $w = 2$ mm at $\theta = 50$–90°, which is the planar case $\phi_0 = \theta$
  ($y_P = 0$).
- "maximum deviation of less than 1% for ⁹⁹ᵐTc and 5% for ¹³¹I".
- The $\phi_0 \ne \theta$ dependence of eq. (31) is not separately validated.

**AM2005b** (round aperture; $\theta$ from the pinhole plane; $\alpha^+$ above, $\alpha^-$ below the plane $z = 0$,
Fig. 3; zone I, eq. 8, $\tan\frac\alpha2 > \cot\theta + \frac{d}{2h}$; first order in $\rho/h$):
- Eqs. (5) and (6) (p. 1639) are AM2004 eqs. (22) and (25).
- Single knife edge, parallel and perpendicular (p. 1639–1640):
  $$d^{SKE}_{re//}\approx\rho_0+\rho_\pi=d+2\Delta L_k\sin\theta\tan\frac{\alpha}{2}\quad(14)$$
  $$d^{SKE}_{re\perp}=2\rho\approx\sqrt{(d^{SKE}_{re//})^2-4\Delta L_k^2\cos^2\theta}\quad(17)$$
- Asymmetric knife edge, parallel direction (p. 1643):
$$d^{AKE}_{re//}=d+2\Delta L_k\sin\theta\,\frac{\tan\frac{\alpha^+}{2}\tan\frac{\alpha^-}{2}-\cot^2\theta}{\tan\frac{\alpha^+}{2}+\tan\frac{\alpha^-}{2}}\qquad(33)$$
- The perpendicular AKE diameter, eqs. (34)–(39), is a quartic-root expression in
  $a_{2\pm} = 1/(\tan^2\frac{\alpha^\pm}{2} - \cot^2\theta)$, $a_{1\pm} = \frac d2\tan\frac{\alpha^\pm}{2}a_{2\pm}$
  and $a_{3\pm} = \frac{d^2}{4}\cot^2\theta\,a_{2\pm}^2$.
  - Eq. (38) holds for $\alpha^+ \ne \alpha^-$. Eq. (39), $(d^{AKE}_{re\perp})^2 = [2b_1 - b_3(d\cot\theta)^2]/b_2$,
    is the symmetric (DKE) limit.
  - Every $\cot^2\theta$ term with a $d$ in it comes from the curvature of the cone. A straight edge has none.
- p. 1643: "Substitution of $\alpha = \alpha^+ = \alpha^-$ into (33) and (39) gives the literature perpendicular and
  parallel effective diameters". SKE is the case $\alpha^+ = \pi$.
- Validation: exact numerical solution of the $\Delta L = \Delta L_k$ contour, $d = 1$ mm, $\alpha = 106°$,
  $h = 10$ and 30 mm, 140 and 365 keV (Tables I–III).

**MMP2012**: there is no equation in the paper (§5.3).

### 5.2 Comparison with our $W_x$, $W_y$ (Q2)

**Notation map** (ours ↔ theirs):
- **Incidence angle.** Our $\theta$ is the 3-D angle from the pinhole axis.
  - A2008: $\sin\phi_0 = \cos\theta$.
  - N2008: $\sin\theta_N = \cos\theta$, if $\theta_N$ is the 3-D angle of its abstract.
  - AM2004/AM2005b: $\sin\theta_{AM} = \cos\theta$, for incidence in the plane normal to the edge.
- **Projected slope.** Our $\tau_x = \tan\theta\cos\varphi$ (projected slope normal to the $x$ edges) is A2008's
  $\cot\theta$, and AM2004/AM2005b's $\cot\theta_{AM}$ in the plane of incidence. N2008's $\cot\theta_N$ equals it
  only for in-plane incidence.
- **Edge slope.** $t = \tan\frac\alpha2$, so $\cot\frac\alpha2 = 1/t$. Our $t_1$, $t_2$ (object and detector side)
  are AM2005b's $\tan\frac{\alpha^+}{2}$, $\tan\frac{\alpha^-}{2}$; the formulas are symmetric in the two.
- **Double knife edge.** A2008's prefactor "2" with one $\alpha$ is the symmetric double wedge, i.e. our $t_1 = t_2$.
- **The symbol κ means different things.** Ours ($\kappa = \mu/\cos\theta$, §3.1 of `square_pinhole.md`) is an
  attenuation per unit $\Lambda$. Li 2009's $\kappa_{Li}$ is geometric: $\Delta L = \kappa_{Li}(|x| - w/2)$, so
  $\kappa_{Li} = (U+L)/\cos\theta$ in our symbols, and $\mu\kappa_{Li} = \kappa_{ours}(U+L)$.

**Path length.** Our side-only $\Delta L = p(U+L)/\cos\theta$ with $U+L = 2t/(t^2-\tau_x^2)$ is
$2tp/[(t^2-\tau_x^2)\cos\theta]$. A2008 eq. (27) is
$\frac{2}{\sin\phi_0}\cdot\frac{1/t}{1-\tau_x^2/t^2}\,p = \frac{2tp}{(t^2-\tau_x^2)\cos\theta}$.
- The two are **identical**, for both projected angles at once.
- Eq. (26) is the finite-$h$ form. Our ray trace (§3.8) shows the parallel-beam form is exact to trace precision
  for $b \ge 53$ mm.

**Widths.** A2008 eq. (31) becomes
$w + \Delta L_k\cos\theta\,\frac1t(t^2-\tau_x^2)$, which is our boxed $W_x$.
- **Identical**, including the $\varphi$ dependence. A2008 already carries both angles, so ours is neither a
  generalisation nor a special case of it.
- $W_y$ is eq. (31) for the other pair of edges ($\tau_y = \tan\theta\sin\varphi$).
- Across the tilt ($\cot\theta_{A2008} = 0$, $\sin\phi_0 = \cos\theta$), eq. (31) gives
  $W_\perp = w + \Delta L_k t\cos\theta$. This is a special case A2008 writes down but never tests (its Fig. 8 is
  $\phi_0 = \theta$ only).

**Asymmetric slopes.** Our bracket with $t_1 \ne t_2$ is
$\frac{(t_1-\tau)(t_2+\tau)+(t_1+\tau)(t_2-\tau)}{t_1+t_2} = \frac{2(t_1t_2-\tau^2)}{t_1+t_2}$, so
$W_x = w + 2\Delta L_k\cos\theta\,(t_1t_2-\tau_x^2)/(t_1+t_2)$.
- In the plane of incidence this is AM2005b eq. (33) term by term, as A2008 "expected".
- The general slit form, $w + 2\Delta L_k\sin\phi_0(\tan\frac{\alpha^+}{2}\tan\frac{\alpha^-}{2}-\cot^2\theta)/(\tan\frac{\alpha^+}{2}+\tan\frac{\alpha^-}{2})$
  with $\phi_0 \ne \theta$, does not appear in any paper read. It follows from our §3.1.
- It is negligible here: A at 30°, CSG slopes 1.0103/0.9889, gives 0.6661 vs 0.6662 mm for $t = 1$; the trace gives
  0.6662.

**N2008 eq. (7)** is AM2004 eq. (22) with $d \to w$ and a single angle.
- With the source in the plane normal to the edge (their experiment) it equals our $W_\parallel$.
- For a source displaced along the edge, eq. (7) is ambiguous, and both readings are wrong:
  - with $\theta_N$ the 3-D angle (as their abstract defines it), it returns the $W_\parallel$ value;
  - with $\theta_N$ the transaxial angle (90°), it returns the normal-incidence value.
- A2008 eq. (31) is the correct form.

| quantity | expression (ours) | A, $w = 0.556$ | C, $w = 1.215$ | difference from ours |
|---|---|---|---|---|
| $W_\parallel$ ($x$ sides, $\varphi = 0$) | $w + \Delta L_k\cos\theta(t^2-\tan^2\theta)/t$ | 0.6662 | 1.3252 | — |
| A2008 (31), $\cot\theta = \tan30°$, $\sin\phi_0 = \cos30°$; = N2008 (7) = AM2004 (22) = AM2005b (33) with $\alpha^+=\alpha^-$ | | 0.6662 | 1.3252 | 0 (identical) |
| $W_\perp$ ($y$ sides, $\varphi = 0$) | $w + \Delta L_k t\cos\theta$ | 0.7214 | 1.3804 | — |
| A2008 (31), $\cot\theta = 0$, $\sin\phi_0 = \cos30°$ | | 0.7214 | 1.3804 | 0 (identical) |
| N2008 (7) for $W_\perp$, $\theta_N$ = 3-D angle | | 0.6662 | 1.3252 | −0.0551 (−7.6 %, −4.0 %) |
| N2008 (7) for $W_\perp$, $\theta_N$ = transaxial angle (90°) | | 0.7469 | 1.4059 | +0.0256 (+3.5 %, +1.9 %) |
| AM2004 (25) = AM2005b (6), round, ⊥ | | 0.7150 | 1.3771 | −0.0063, −0.0033 (cone curvature) |
| normal incidence (every paper) | $w + \Delta L_k t$ | 0.7469 | 1.4059 | 0 |
| exact CSG trace (§3.8), ∥ / ⊥ | | 0.6662 / 0.7213 | 1.3252 / 1.3803 | ≤ 0.0001 |

**Sensitivity strip term.** A2008 eq. (30) gives $w_{se}-w = \frac1\mu\cos\theta\,t(1-\tau_x^2/t^2) = \cos\theta(t^2-\tau_x^2)/(\mu t)$.
That is twice our per-edge strip width $1/[\kappa(U+L)]$.
- So our $A_{strips} = w[(w_{se,x}-w)+(w_{se,y}-w)] = \frac{w\cos\theta}{\mu t}(2t^2-\tan^2\theta)$ is **identical**
  to the slit result.
- Li 2009's $w_{eff} = w + 2/(\mu\kappa_{Li})$ with $\kappa_{Li}$ from A2008 (27) is the same expression. Li 2009 was
  not re-read here; this follows §4.
- At 30°, $\varphi = 0$: $w_{se,x} = 0.7150$ / 1.3740 mm and $w_{se,y} = 0.7946$ / 1.4536 mm (A / C).

**What the slit result lacks: the corners.**
- At 30°, $\varphi = 0$, $w_{se,x}w_{se,y} = 0.5682$ / 1.9973 mm², against $A_{eff} = 0.5981$ / 2.0272 mm².
  The product is short by 0.0299 mm² (5.0 % / 1.5 %).
- At normal incidence the shortfall is exactly $t^2/\mu^2 = 0.0759$ mm² (9.9 % / 3.3 %). This is MM2020 eq. (25)'s
  extra term: $A_{eff} = (w + t/\mu)^2 + t^2/\mu^2$.
- So the corner term comes from MM2020 eq. (22) and our §3.3, not from the slit papers.

**Resolution analogue.** Eq. (31) gives $w_{re} - w = 2\ln2/(\mu\kappa_{Li})$, which confirms the §4 statement.
- Eqs. (30)–(31) together give $(w_{re}-w) = -\ln k\,(w_{se}-w)$ exactly, at every $(\theta, \phi_0)$, for a straight
  edge.
- A2008 does not state this identity.

### 5.3 MMP2012: the rectangular-pinhole resolution model (Q3)

The paper contains no equation. Three ingredients:

1. **Geometric ratio** (§II-C, Table II, p. 3816). "We determined the sensitivity ratio of square to circular
   apertures using an analytic model that did not consider aperture penetration or detector blurring … for matched
   resolution using three different metrics, each of which was averaged over the direction of measurement."
   - Table II, as printed: RMS $3/\pi = 0.96$; FWHM $3\pi/8 = 1.12$; FWTM $3\pi/8 = 1.12$.
   - $3\pi/8 = 1.178$, so the FWHM and FWTM rows are internally inconsistent.
   - For comparison, the average over 0–45° of a square's point-profile FWHM is
     $\frac4\pi\ln(1+\sqrt2)\,w = 1.122\,w$, which may be where the 1.12 comes from.
   - The model itself is not given.
2. **With penetration: numerical.** PtIr, $\mu = 4.56$ mm⁻¹, $R_i = 3.5$ mm. Full acceptance angle 28° for the
   square and 31.4° for the circle (solid-angle matched).
   - Simulation: point-source projections at detector distances of 140, 170 and 200 mm; aperture size in 0.02 mm
     steps; 0.6 mm pixels; each projection "rotated from 0.0° to 45.0° … in 2.5° steps in order to average the
     resolution over direction". "Oblique-path incidence on the detector was not considered".
   - Fig. 5 ratio ≈ 1 (p. 3819): "For FWHM and FWTM, the circular shows a slight sensitivity advantage whereas RMS
     resolution suggests a slight advantage for square apertures."
3. **System performance curves** (§II-E, p. 3817). "the geometric parameters were calculated from the system
   resolution using the magnification of the center pinhole, … the acceptance angles calculated from the FOV, and the
   linear attenuation coefficient for PtIr in the resolution-effective diameters. These geometric parameters were
   then utilized to calculate the sensitivity-effective diameters. The sensitivity-effective diameters were used in
   Anger's sensitivity formula".
   - No formula is written. The only resolution reference is AM2004 ([10]).
   - So this is the round-pinhole $d_{re}$ / $d_{se}$ applied to the square at the centre pinhole (normal incidence),
     the same practice as Mo2016. There is no per-side or oblique form.

Reported resolution (0.37 mm transaxial, 0.29 mm axial; 0.33 mm squares, 20 MLEM iterations, ray-traced system
matrix with DOI) is numerical.

### 5.4 Novelty verdict (Q4)

**Already published:**
1. **§3.1, path length beyond a side.** Straight double knife edge, oblique in both directions, parallel beam:
   A2008 eq. (27); the exact finite-$h$ form is eq. (26). For asymmetric slopes in the plane of incidence: AM2005b
   (the planar cross-section is the same as a cone's, A2008 p. 713).
2. **§3.2, boxed $W_x$, $W_y$.** A2008 eq. (31), applied to each pair of sides; $W_\perp$ is its $\cot\theta = 0$
   case.
   - $W_\parallel$ also appears as AM2004 eq. (22) (round) and N2008 eq. (7) (slit).
   - Validated for slits: N2008 Fig. 7 (MC); A2008 Fig. 8 (⁹⁹ᵐTc < 1 %, ¹³¹I < 5 %).
   - Normal incidence is AM2004 eq. (29). It is applied to square sides by Mo2016 eq. (2) and, implicitly, by
     MMP2012.
3. **$t_1 \ne t_2$ in the plane of incidence:** AM2005b eq. (33).
4. **§3.3.** The strip term is A2008 eq. (30) (= Li 2009 eq. 21). The full oblique $A_{eff}$ with corners is MM2020
   eqs. (22) and (25); ours is an independent re-derivation.
5. **Metric dependence of square vs circle:** MMP2012 Table II and Fig. 5, numerical and direction-averaged; J2016.
   J2016 Fig. 6(c) also shows the width's dependence on direction.

**Not found in any of the ten papers read.** These are modest consequences, not new physics:
- (a) **Each side of the square behaves exactly like a slit.** The square's point-profile FWHM along each side
  equals the slit $w_{re}$ of that pair of edges at any $(\theta, \varphi)$, and the corners do not enter.
  - Explicit per-side widths $W_x(\theta,\varphi)$, $W_y(\theta,\varphi)$ with $\tau = \tan\theta\cos\varphi$,
    $\tan\theta\sin\varphi$.
  - Checked against an exact CSG ray trace to $10^{-4}$ mm.
  - Present this as an application of A2008 eq. (31), not as a new formula.
- (b) **The $\varphi$-average** $\bar W = w + \Delta L_k\cos\theta(t - \tan^2\theta/2t)$, which is
  $\varphi$-independent, and the second-order forms of §3.7.
- (c) **The diagonal.**
  - The point-profile FWHM is exactly $\sqrt2(w + \Delta L_k t)$ at normal incidence, with penetration, because
    beyond a corner $\Lambda \propto \max(p,q)$ and the $k$-contour stays a square.
  - The LSF across the diagonal is ≈ $W/\sqrt2$.
  - No paper gives either. J2016 shows only a numerical direction dependence for a rounded square.
- (d) **Straight edge vs cone across the tilt.** AM2004 (25)'s $-\Delta L_k^2\sin^2\theta$ is cone curvature
  (≤ 0.006 mm here). This is implicit in A2008 (31) vs AM2004 (25), but nobody states it.
- (e) **The general asymmetric oblique slit width** ($t_1 \ne t_2$, $\phi_0 \ne \theta$). A2008 only "expects" the
  planar case. It is numerically irrelevant here.
- (f) **The exact ratio $-\ln k$ between the resolution and sensitivity increments** of a straight edge.
  - Outside §3.2: the closed-form square RMS with penetration (§3.5) is not in these papers either; Metzler 2002
    covers round apertures only.

**Consequence for `square_pinhole.md` §3.2 and §4.**
- Cite A2008 eq. (31) (and N2008) next to AM2004 eq. (22). Call $W_x$, $W_y$ "identical to the resolution-effective
  slit width".
- The closing absence claim stays true only in the narrow sense that nobody has written out the square's widths. The
  side formula itself is published.

**Suggested paragraph for paper 2:**

> For the square knife-edge apertures we model penetration with the straight-edge path length of Accorsi et al.
> (2008, eqs. 26–27). The FWHM of the point-source profile along a side then equals the resolution-effective slit
> width of that pair of edges, $W = w + (\ln 2/\mu)\cos\theta\,(t^2 - \tau^2)/t$ (Accorsi et al. 2008, eq. 31), where
> $t = \tan(\alpha/2)$, $\theta$ is the incidence angle from the pinhole axis and $\tau$ is the tangent of its
> projection onto the plane normal to the edges ($\tau = \tan\theta\cos\varphi$ and $\tan\theta\sin\varphi$ for the
> two pairs). In the plane of incidence this is the parallel resolution-equivalent diameter of a round knife edge
> (Accorsi and Metzler 2004, eq. 22; asymmetric profiles: Accorsi and Metzler 2005, eq. 33), as applied to slit-slat
> collimators by Novak et al. (2008). Across the plane of incidence the straight edge lacks the curvature term of the
> round-pinhole perpendicular diameter (Accorsi and Metzler 2004, eq. 25). At normal incidence the width reduces to
> $w + \ln 2\,t/\mu$, which Moore et al. (2016) applied to square pinholes. The corners do not affect the profiles
> along the sides. Along the diagonal the point-profile width is $\sqrt2$ times larger, exactly at normal incidence,
> with or without penetration. For the sensitivity we use the closed-form penetrative effective area of Metzler and
> Moore (2020, eqs. 22 and 25), whose edge strips are the sensitivity-effective slit widths of Accorsi et al. (2008,
> eq. 30). An exact ray trace of our collimator geometry reproduces the side widths to $10^{-4}$ mm and the effective
> area to 0.03 % for $\theta \le 40°$.
