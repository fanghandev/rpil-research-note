# Square knife-edge pinholes: resolution and sensitivity with penetration

Derivation note for the brain SPECT helmet (square pyramidal apertures A–D), checking the formulas used in
`../analytic.py` against Accorsi & Metzler 2004, Metzler et al. 2002 and Metzler & Accorsi 2005, deriving the
square-aperture versions, and verifying them numerically against an exact ray trace of our collimator CSG.
Fang Han, 28 October 2026. Scripts: `square_pinhole_model.py` (closed forms + brute-force integrals),
`raytrace_pyramid.py` (exact CSG trace, `raytrace_results.json`), `crosscheck_tables.py` (`tables.md`,
`tables.json`), `figures_lsf.py` (`img/psf_C.png`, `lsf.json`). All CPU, numpy only.

## Verification status (2026-10-30)

- **SymPy** (`sympy_check.py`, `sympy_check.md`): 62 of 64 checks pass. Proven symbolically (residual 0):
  - the path length through the 8 half-planes (zone I);
  - the strip and corner integrals, both orderings;
  - the §3.3 closed form;
  - the θ = 0 Paix limit;
  - the §3.7 series;
  - W_x, W_y and √2 W;
  - reduction to AM2004 eq. 22.

  Numerics agree with mpmath to 4e-26 and with the ray trace to 1e-3 to 1e-4. The 2 failures are quoted numbers, corrected below.
- **Literature** (`literature_check.md`, all six PDFs read in full):
  - every transcription is correct;
  - M&M 2020 eq. 22 as implemented in `crosscheck_tables.py` matches the paper term by term, so `simplify(A_ours − A_MM22) = 0` is a symbolic proof of agreement with the published formula.
- **Corrections applied below:**
  - W⊥ − AM2004(25) is up to 0.0063 mm at 30° (0.0085 at 35°), not ≤ 0.003;
  - the area expansion is 3.9 % low for A at φ = 45° (3.2 % at φ = 0);
  - the width-expansion error is 0.0022 mm;
  - the cubic φ dependence enters through M³ and 3Mm²;
  - eq. 22 of M&M 2020 is the penetration term only (τ is their tapering function, eq. 28-29);
  - AM2004 §V refers to edge profiles, so the square is our extension;
  - the d_re < Anger ordering needs d > 0.216 mm (AM2004 eq. 43; A-D satisfy it);
  - the Johnson 2016 and Moore 2016 wording.
- **Novelty (closed, `literature_check.md` §5).**
  - **Published:** the side widths W_x, W_y are identical to the slit resolution width of Accorsi, Novak, Ayan & Metzler, IEEE TMI 2008;27:709, eq. 31 (zero difference at 30°). The strip sensitivity is their eq. 30. The full area is M&M 2020.
  - **Not found in the ten papers read:** that each side of the square behaves exactly like a slit, with the corners playing no part; the √2 diagonal with penetration; the φ-average.
  - **Framing:** present this as a verified application of published results, not as new formulas.

## 0. Summary

1. **Resolution-effective width.** The form used now, $d_{re} = w + \ln 2\,\tan(\alpha/2)/\mu$, is Accorsi &
   Metzler 2004 eq. (29) (normal incidence, exact for a parallel beam). For a *square* knife-edge aperture it is
   **exactly** the FWHM of the point profile along either side at normal incidence (derived in §3.2). At oblique
   incidence $\theta$ (from the module axis) with the tilt at azimuth $\varphi$ to the square's $x$ side,
   $$W_x = w + \Delta L_k\cos\theta\Big(t - \frac{\tan^2\theta\cos^2\varphi}{t}\Big),\qquad
     W_y = w + \Delta L_k\cos\theta\Big(t - \frac{\tan^2\theta\sin^2\varphi}{t}\Big),\qquad
     \Delta L_k=\frac{\ln 2}{\mu},\; t=\tan\frac{\alpha}{2}.$$
   The side along the tilt reproduces AM2004 eq. (22) with $d\to w$ *identically*; the side across the tilt is
   AM2004 eq. (25) without its small $-\Delta L_k^2\sin^2\theta$ term. The point-profile FWHM along the diagonal
   is $\sqrt2\,W$ (exactly, at normal incidence); the line-spread FWHM along the diagonal is *narrower* than along
   a side ($w/\sqrt2$ geometrically). The RMS width is isotropic.
2. **Sensitivity.** The Paix form used for the counts, $w_s^2 = w^2 + 2wt/\mu + 2t^2/\mu^2$, is **exactly** the
   penetration-aware effective area of the square at normal incidence (§3.3; it is also Metzler & Moore 2020
   eq. 25). Off-axis the effective area falls (by 22 % for A and 7 % for D at 30°) and is given in closed form
   (§3.3, identical to Metzler & Moore 2020 eq. 22 to machine precision).
3. **One error in `analytic.py`:** $g = w_s^2\cos^3\theta/(4\pi r^2)$ with $r$ the *slant* distance double-counts
   the obliquity. Mallard–Myers/Anger (AM2004 eq. 1) is $g = d^2\sin^3\theta_{AM}/(16h^2)$ with $h = b$, i.e.
   $g = A\cos^3\theta/(4\pi b^2) = A\cos\theta/(4\pi r^2)$ with $b = r\cos\theta$ the perpendicular distance and
   $A$ the (effective) aperture area. The current counts are low by
   $\cos^2\theta$ (0.93 at 15°, 0.75 at 30°) for every oblique module. Net effect of the fix plus the angular
   effective area: $g$ rises by 1–5 % at 15° and 4–24 % at 30° (A→D). Nothing changes at the helmet centre.
4. **System resolution.** $R = \sqrt{R_g^2 + R_i^2}$ with $R_g = d_{re}(b+f)/f$, $R_i = p\,b/f$ is AM2004 eq. (7)
   with $M = f/b$; Moore et al. 2016 use the same two equations for their square pinholes. It is exact for
   Gaussian components only; for two box-like components the FWHM of the convolution is $\max(R_g, R_i)$ and the
   RMS adds in quadrature (Metzler & Accorsi 2005, p. 5016). Keep eq. (7) as the convention but read it as a
   Gaussian-equivalent upper bound.
5. **Square ↔ round.** Same geometric area: $d = 2w/\sqrt\pi = 1.128\,w$; with penetration at 140 keV the
   equal-area round diameter is $1.15$–$1.21\,w$ (the four corners penetrate more than an arc). Same FWHM along a
   side: $d = w$ exactly (same penetration increment). Same RMS: $d = 2w/\sqrt3 = 1.155\,w$ geometric. There is no
   single mapping; the "right" one depends on the metric.

## 1. Our aperture, from the GATE / gammart CSG

`gate_sim_brain_spect_boolean.py` (`construct_collimator_geometry`) and `gammart/scene/brain_spect.py`
(`collimator_definition`, `collimator_solid`) build the same solid: outer frustum A (G4Trd, square cross-section,
height $h_{nozzle}+h_{body}$) minus frustum B (the nozzle opening, half-width $w/2$ at the knife edge growing to
$l_{top}/2$ over $h_{nozzle}$ on the object side) minus frustum C (the body opening, half-width $w/2$ at the knife
edge growing to $l_{bottom,inner}/2 = 25$ mm over $h_{body} = 25$ mm on the detector side), plus the hollow box
around the crystal. B and C are extended by $\delta_z = 0.1$ mm with their widths adjusted along their own slopes,
so both have half-width exactly $w/2$ at $z_k = (h_{body} - h_{nozzle})/2$ and the opening is the *union* of two
pyramids meeting at a sharp edge: a **double-sided (channel-less) square knife edge**.

| variant | $w$ (mm) | $l_{top}$ | $h_{nozzle}$ | object-side slope $t_1 = \frac{l_{top}-w}{2h_{nozzle}}$ | detector-side slope $t_2 = \frac{50-w}{50}$ | $t_h = \frac{2t_1t_2}{t_1+t_2}$ | full angles |
|---|---|---|---|---|---|---|---|
| A | 0.556 | 10.74 | 5.04 | 1.0103 | 0.9889 | 0.9995 | 90.6° / 89.4° |
| B | 0.797 | 11.00 | 5.02 | 1.0162 | 0.9841 | 0.9999 | 90.9° / 89.1° |
| C | 1.215 | 11.46 | 5.00 | 1.0245 | 0.9757 | 0.9995 | 91.4° / 88.6° |
| D | 2.007 | 12.33 | 4.96 | 1.0406 | 0.9599 | 0.9986 | 92.3° / 87.7° |

The two half-angles differ by 1–2° but, as shown in §3, only the harmonic mean $t_h$ enters at normal incidence,
and $t_h = 1.000 \pm 0.001$: **$t = \tan(\alpha/2) = 1$ is accurate to 0.1 %** for all four. Tungsten
$\mu = 3.63$ mm$^{-1}$ at 140.5 keV (the script's value; Johnson et al. 2016 use 3.64, Van Audenhaege et al. 2015
use 3.6). $f = 27$ mm, $b = 53$–$247$ mm ($149.6$ mm at the centre), $\theta \lesssim 35°$.

**Conventions.** $\theta$ is measured from the module axis (pinhole normal) here and in `analytic.py`.
Accorsi–Metzler measure $\theta_{AM}$ from the pinhole *plane*: $\theta_{AM} = \pi/2 - \theta$, so
$\sin\theta_{AM} = \cos\theta$, $\cot\theta_{AM} = \tan\theta$, $\csc\theta_{AM} = 1/\cos\theta$. $h$ (AM) $= b$
(ours) is the perpendicular distance of the source from the aperture plane; $r = b/\cos\theta$ is the slant
distance. Knife-edge plane $z = 0$, $+z$ towards the object, $x,y$ along the sides of the square, $a = w/2$.

## 2. Cross-check of the equations used by `analytic.py`

| quantity | `analytic.py` / qmd | paper and equation | verdict | consequence for A, B, C, D |
|---|---|---|---|---|
| geometric sensitivity | $g = w_s^2\cos^3\theta/(4\pi r^2)$, $r$ = slant distance | AM2004 (1): $g = d^2\sin^3\theta_{AM}/(16h^2)$ with $h = b$; i.e. $g = A\cos^3\theta/(4\pi b^2) = A\cos\theta/(4\pi r^2)$ | **wrong obliquity factor**: $\cos^3\theta/r^2 = \cos^5\theta/b^2$ | $g$ low by $\cos^2\theta$: ×0.933 at 15°, ×0.750 at 30°, same for all widths; exact at $\theta = 0$ |
| sensitivity-effective width | $w_s = \sqrt{w^2 + 2wt/\mu + 2t^2/\mu^2}$ ("Paix") | AM2004 (5) = Paix 1967 (= M&A 2005 eq. 2); (3) is Anger's without the $2t^2/\mu^2$ term | **correct and exact** for the square at normal incidence: $A_{eff} = w_s^2$ (§3.3, Metzler & Moore 2020 eq. 25). Round pinhole: $A_{eff} = \pi d_e^2/4$ | $w_s = 0.876, 1.107, 1.516, 2.299$ mm; $A_{eff}(0) = 0.767, 1.226, 2.297, 5.286$ mm²; at 30° $A_{eff} = 0.600, 1.022, 2.029, 4.896$ (−22, −17, −12, −7 %) |
| angular dependence of the penetrative sensitivity | none (Paix at all $\theta$) | Metzler et al. 2001 (quoted as M&A 2005 eq. A.1) for round; Metzler & Moore 2020 eq. 22 for rectangular | **approximate**: $A_{eff}$ falls with $\theta$ | with the obliquity fix, net $g$ change +0.9/+2.5/+3.9/+5.2 % at 15°, +4.3/+11.2/+17.8/+23.5 % at 30° |
| resolution-effective width, normal incidence | $d_{re} = w + \ln2\,t/\mu = w + 0.191$ mm | AM2004 (29) $d_{re} = d + \Delta L_k\tan(\alpha/2)$, $\Delta L_k = -\ln k/\mu$ (9), $k = 0.5$; exact for a parallel beam | **correct**; for the square it is the exact FWHM of the point profile along a side (§3.2); Moore et al. 2016 eq. (2) use the same for square sides | $0.747, 0.988, 1.406, 2.198$ mm (unchanged). Diagonal cut: $\sqrt2\times$: $1.056, 1.397, 1.988, 3.108$ |
| oblique incidence, parallel direction | not used | AM2004 (22): $d_{re\parallel} = d + \Delta L_k(\tan^2\tfrac\alpha2 - \cot^2\theta_{AM})\cot\tfrac\alpha2\sin\theta_{AM}$ | square side along the tilt: **identical** with $d \to w$ (§3.2) | at 30°: $W_\parallel = 0.666, 0.907, 1.325, 2.117$ (−0.081 mm vs now) |
| oblique incidence, perpendicular direction | not used | AM2004 (25): $d_{re\perp} = \sqrt{(d + \Delta L_k\tan\tfrac\alpha2\sin\theta_{AM})^2 - \Delta L_k^2\cos^2\theta_{AM}}$ | square side across the tilt: $W_\perp = w + \Delta L_k t\cos\theta$, i.e. (25) **without the last term** (≤ 0.003 mm here) | at 30°: $W_\perp = 0.721, 0.962, 1.380, 2.172$ (−0.026 mm); AM (25) would give 0.715, 0.958, 1.377, 2.170 |
| Anger / Paix as resolution widths | not used for $R_g$ (the deck's slide 11 did) | AM2004 (43)–(46): $d_{re} < $ Anger (3) $<$ Paix (5) at normal incidence for $k = 0.5$ | ordering confirmed | Anger $0.785, 1.036, 1.465, 2.266$; Paix $0.876, 1.107, 1.516, 2.299$; $d_{re}$ $0.747, 0.988, 1.406, 2.198$ |
| geometric resolution at the object | $R_g = d_{re}(b+f)/f$ | AM2004 (6): $\lambda_g = d(1 + 1/M)$, $M = f/h$ | **correct** ($M = f/b$) | at the centre $(b+f)/f = 6.541$: $R_g = 4.89, 6.46, 9.20, 14.38$ mm |
| intrinsic term and combination | $R_i = p\,b/f$, $R = \sqrt{R_g^2 + R_i^2}$ | AM2004 (7): $\lambda_s = \sqrt{d_e^2(1 + 1/M)^2 + FWHM_i^2/M^2}$; Moore et al. 2016 eq. (3); Van Audenhaege 2015 eq. (10) | **correct as the literature convention**; exact only for Gaussian components (M&A 2005 p. 5016). Two boxes: FWHM $= \max(R_g, R_i)$; RMS adds in quadrature | centre, C, parallel pixels: quadrature 14.4 mm; box-max 11.1 mm; RMS-equivalent Gaussian FWHM 10.5 mm (§5.3) |
| FWHM vs RMS | FWHM throughout | Metzler et al. 2002 (7)–(8): RMS $= \sqrt{\overline{x^2} - \bar x^2}$ of the PRF; (25): geometric RMS $= R/2 = d/4$ per axis for a disk | definitions consistent; **penetration affects the RMS far more than the FWHM** (§3.5) | square RMS per axis (knife-edge plane): geometric $w/\sqrt{12} = 0.161, 0.230, 0.351, 0.579$; with penetration $0.327, 0.376, 0.476, 0.687$ (×2.0, 1.6, 1.4, 1.2); FWHM only ×1.34, 1.24, 1.16, 1.10 |

The numbers in the last column are for $t = 1$, $\mu = 3.63$ mm$^{-1}$, in the knife-edge plane (multiply by
$(b+f)/f$ for the object); full tables in `tables.md`.

## 3. Derivation for the square aperture

### 3.1 Path length through a double wedge

Parallel-beam approximation (AM2004 §II, "$\rho/h \to 0$"): all rays from the source have the in-plane slopes
$$\tau_x = \tan\theta\cos\varphi,\qquad \tau_y = \tan\theta\sin\varphi \qquad (dx/dz,\ dy/dz \text{ along the ray}),$$
with the source on the $+x,+y$ side. A ray crossing the knife-edge plane at $(x_0, y_0)$ is $x(z) = x_0 + \tau_x z$.
The $+x$ wall ("near" edge, on the source side) occupies $x \ge a + t_1 z$ for $z > 0$ and $x \ge a + t_2|z|$
for $z < 0$. With $p = x_0 - a > 0$ the ray is inside this wall for
$$-p\,L_x^{n} \le z \le p\,U_x^{n},\qquad U^{n} = \frac{1}{t_1 - \tau_x},\quad L^{n} = \frac{1}{t_2 + \tau_x}.$$
For the $-x$ wall ("far" edge, $x_0 = -a - p$): $U^{f} = 1/(t_1 + \tau_x)$, $L^{f} = 1/(t_2 - \tau_x)$. The same
holds for the $y$ walls with $\tau_y$. Both intervals contain $z = 0$, so for a ray beyond a corner
($p_x = |x_0| - a > 0$ and $p_y = |y_0| - a > 0$) the material along the ray, which is the **union** of the $x$ and
$y$ walls, spans
$$\Lambda = \max(p_xU_x,\ p_yU_y) + \max(p_xL_x,\ p_yL_y),\qquad \Delta L = \Lambda/\cos\theta,$$
and the transmission is $T = e^{-\mu\Delta L} = e^{-\kappa\Lambda}$ with $\kappa = \mu/\cos\theta$. Beyond a side
only ($p_y = 0$): $\Lambda = p_x(U_x + L_x)$. Validity ("zone I" of AM2004 Fig. 3): $|\tau_x|, |\tau_y| < \min(t_1, t_2)$,
i.e. $\tan\theta|\cos\varphi| < 0.96$; along a side this is $\theta < 43.8°$, comfortably above our 35°.

At normal incidence $\Lambda = p(1/t_1 + 1/t_2) = 2p/t_h$ with $t_h = 2t_1t_2/(t_1+t_2)$, which is why only the
harmonic mean of the two slopes matters there (AM2004 Fig. 4a: $\Delta L/2 = (\rho - d/2)\cot(\alpha/2)$ for a cone
is the same statement).

### 3.2 Point-spread function and FWHM

The PRF on the detector is the knife-edge-plane transmission map projected by the point source: a scale factor
$(b+f)/b$ in both in-plane directions because aperture and detector planes are parallel (Metzler et al. 2002
eq. 2). Referred to the object at depth $b$ this becomes $(b+f)/f$, as in AM2004 eq. (6). So every width below is
a knife-edge-plane width $W$, and $R_g = W(b+f)/f$ in both directions. (The Metzler & Accorsi 2005 set-up had a
$\sin\theta$ minification of the parallel direction because their detector was normal to the source line; ours
is not.)

**Along a side ($y_0 = 0$).** $T(p) = e^{-\kappa p(U+L)}$, so the width at fraction $k$ of the maximum gets, from
each edge, $p_k = \Delta L_k\cos\theta/(U+L)$ with $\Delta L_k = -\ln k/\mu$ (AM2004 eq. 9). Hence
$$W_x = w + \Delta L_k\cos\theta\left[\frac{1}{U_x^{n}+L_x^{n}} + \frac{1}{U_x^{f}+L_x^{f}}\right].$$
With $t_1 = t_2 = t$: $1/(U^{n}+L^{n}) = 1/(U^{f}+L^{f}) = (t^2 - \tau_x^2)/(2t)$ and
$$\boxed{W_x = w + \Delta L_k\cos\theta\,\frac{t^2 - \tan^2\theta\cos^2\varphi}{t}},\qquad
  \boxed{W_y = w + \Delta L_k\cos\theta\,\frac{t^2 - \tan^2\theta\sin^2\varphi}{t}}.$$
Side along the tilt ($\varphi = 0$): $W_\parallel = w + \Delta L_k(t^2 - \tan^2\theta)\cos\theta/t$. Substituting
$\tan\theta = \cot\theta_{AM}$, $\cos\theta = \sin\theta_{AM}$ gives AM2004 eq. (22),
$d + \Delta L_k(\tan^2\tfrac\alpha2 - \cot^2\theta_{AM})\cot\tfrac\alpha2\sin\theta_{AM}$, term by term: in the
plane of the tilt a cone and a wedge have the same 2-D cross-section (AM2004 Appendix II is exactly this
calculation). Side across the tilt ($\varphi = 0$, $y$ edges, $\tau_y = 0$): $W_\perp = w + \Delta L_k\,t\cos\theta$.
AM2004 eq. (25) is $\sqrt{(d + \Delta L_k t\cos\theta)^2 - \Delta L_k^2\sin^2\theta}$: the extra term comes from
the curvature of the cone (the ray crossing at $(0, \rho)$ sees a surface that recedes along $x$); a straight edge
is translation-invariant along $x$ and has none. Normal incidence: $W = w + \Delta L_k t_h$, AM2004 eq. (29). The
$\varphi$-average of the two sides is $\varphi$-independent:
$$\bar W = \tfrac12(W_x + W_y) = w + \Delta L_k\cos\theta\Big(t - \frac{\tan^2\theta}{2t}\Big).$$

**Along the diagonal** ($x_0 = y_0$). Beyond the corner $p_x = p_y = p$ and
$\Lambda = p[\max(U_x,U_y) + \max(L_x,L_y)]$; at normal incidence this is $p(U+L)$, the same decay as along a
side, but the distance along the diagonal is $p\sqrt2$, so the point-profile FWHM along the diagonal is
$\sqrt2\,(w + \Delta L_k t) = \sqrt2\,W$ exactly. The square's "widest direction" (AM2004 §IV) is its diagonal,
41 % wider than the sides, geometrically and with penetration alike. At oblique incidence the two diagonals differ
slightly (table in §3.8).

**Line-spread function.** A rod or line source sees the PSF integrated along the line. For the geometric box
the LSF across a line parallel to a side is a rect of width $w$ (FWHM $w$), across a line along the diagonal a
triangle of base $w\sqrt2$ (FWHM $w/\sqrt2$). With penetration (numbers from `figures_lsf.py`, knife-edge plane,
normal incidence):

| aperture | $w$ | PSF cut, side | PSF cut, diagonal | LSF, line ∥ side | LSF, line ∥ diagonal | LSF geometric: $w$, $w/\sqrt2$ |
|---|---|---|---|---|---|---|
| A | 0.556 | 0.747 | 1.056 | 0.824 | 0.588 | 0.556, 0.393 |
| B | 0.797 | 0.988 | 1.397 | 1.045 | 0.759 | 0.797, 0.564 |
| C | 1.215 | 1.406 | 1.988 | 1.445 | 1.055 | 1.215, 0.859 |
| D | 2.007 | 2.198 | 3.108 | 2.223 | 1.614 | 2.007, 1.419 |

So "the FWHM of a square pinhole" is ambiguous by a factor 2 ($\sqrt2 W$ for a point profile on the diagonal,
$\approx W/\sqrt2$ for a line on the diagonal). For Derenzo-type rods, which are lines, the side-parallel LSF
width ($\approx W + 0.02$–$0.08$ mm) is the conservative number and $W$ along the side is the right
$d_{re}$-type quantity; the diagonal only helps.

### 3.3 Effective area and sensitivity

Define the penetration-aware effective area in the knife-edge plane, $A_{eff} = \iint T\,dx_0\,dy_0$ (the
analogue of AM2004 eq. 4 and of Metzler & Moore 2020 eq. 12 divided by the solid-angle factor). Split the plane
into the opening ($w^2$), four strips beyond the sides, and four corner quadrants:

*Strips.* $\int_0^\infty e^{-\kappa p(U+L)}dp \times w = \dfrac{w}{\kappa(U+L)}$ per edge. With $t_1 = t_2 = t$
and $\kappa = \mu/\cos\theta$,
$$A_{strips} = \frac{w\cos\theta}{\mu t}\left[(t^2 - \tau_x^2) + (t^2 - \tau_y^2)\right]
             = \frac{w\cos\theta}{\mu t}\,(2t^2 - \tan^2\theta),$$
which is $\varphi$-independent.

*Corners.* $I = \int_0^\infty\!\!\int_0^\infty e^{-\kappa[\max(pU_x, qU_y) + \max(pL_x, qL_y)]}dp\,dq$. Substituting
$q = ps$ ($dq = p\,ds$) and integrating over $p$ first,
$$I = \int_0^\infty\frac{ds}{\kappa^2\Lambda(1,s)^2},\qquad \Lambda(1,s) = \max(U_x, sU_y) + \max(L_x, sL_y),$$
which is piecewise linear in $s$ with breakpoints $s_U = U_x/U_y$ and $s_L = L_x/L_y$. With
$s_a = \min(s_U, s_L)$, $s_b = \max(s_U, s_L)$, and $(\alpha,\beta) = (L_x, U_y)$ if $s_U \le s_L$ else $(U_x, L_y)$,
$$\kappa^2 I = \frac{s_a}{(U_x+L_x)^2} + \frac{1}{\beta(\alpha + \beta s_a)} - \frac{1}{\beta(\alpha + \beta s_b)} + \frac{1}{s_b(U_y+L_y)^2}.$$
Summing the four corners (near/far in $x$ × near/far in $y$) gives $A_{corners}$; the code is
`square_pinhole_model.area_eff_square`.

*Normal incidence.* $U = L = 1/t$ for every edge, $\kappa = \mu$: $A_{strips} = 4\cdot\frac{wt}{2\mu} = \frac{2wt}{\mu}$,
and each corner is $I = \int\!\!\int e^{-(2\mu/t)\max(p,q)}dp\,dq = 2\int_0^\infty p\,e^{-2\mu p/t}dp = \frac{t^2}{2\mu^2}$,
so
$$\boxed{A_{eff}(0) = w^2 + \frac{2wt}{\mu} + \frac{2t^2}{\mu^2} = w_s^2\ (\text{Paix form})}.$$
With $t_1 \ne t_2$ the same holds with $t \to t_h$. This is Metzler & Moore 2020 eq. (25) for $w_x = w_y$,
$\alpha_x = \alpha_y$. For the round pinhole AM2004 eq. (4)–(5) give $A_{eff} = \frac{\pi}{4}(d^2 + 2dt/\mu + 2t^2/\mu^2)$:
the Paix form is the exact normal-incidence effective area of *both* shapes, with $w$ a side and $d$ a diameter.
The square's penetration excess is in the corners: $2t^2/\mu^2 = 0.152$ mm² against $\frac\pi4\cdot 2t^2/\mu^2 = 0.119$ mm²
for the disk.

*Oblique incidence, closed form.* Writing $M = \max(|\tau_x|, |\tau_y|)/t$, $m = \min(|\tau_x|, |\tau_y|)/t$, the
corner sum reduces to
$$A_{corners} = \frac{t^2\cos^2\theta}{\mu^2}\,(1 - M)\left[3(1 - m^2) - (1 - M)^2\right],$$
so that
$$\boxed{A_{eff}(\theta,\varphi) = w^2 + \frac{w\cos\theta}{\mu t}(2t^2 - \tan^2\theta)
  + \frac{t^2\cos^2\theta}{\mu^2}(1-M)\left[3(1-m^2) - (1-M)^2\right]}.$$
This is $w^2$ plus Metzler & Moore 2020 eq. (22), which is the penetration term $g_{pen}$ only (for $w_x = w_y$, $\alpha_x = \alpha_y$; their $\tau$ is the penumbra tapering function of eqs. 28-29, not used here; valid outside the penumbra, to leading order in $1/h$), multiplied by
$4\pi h^2/\cos^3\theta$: their $(1 + \tan^2\theta_x + \tan^2\theta_y)^{-2} = \cos^4\theta$ and
$(\dots)^{-5/2} = \cos^5\theta$, $\tan\theta_x = \tau_x$, $\tan\theta_y = \tau_y$. I did not use their expression
to derive mine; `crosscheck_tables.py` evaluates both on a grid ($w$ = A–D, $\theta = 0$–$40°$, $\varphi = 0$–$45°$)
and the largest relative difference is $2\times10^{-16}$. Numerically $A_{eff}$ depends on $\varphi$ by $<1$ %
(0.5981 vs 0.6026 mm² for A at 30°), so a $\varphi$-averaged value is adequate.

*Sensitivity.* The fraction of emitted photons transmitted is the projected effective area over the sphere:
$$\boxed{g = \frac{A_{eff}(\theta,\varphi)\cos\theta}{4\pi r^2} = \frac{A_{eff}\cos^3\theta}{4\pi b^2}},$$
Mallard–Myers/Anger (AM2004 eqs. 1–2) with $\pi d^2/4 \to A_{eff}$. The exact trace (§3.8) returns
$g_{trace}/g_{model} = 0.9997$–$1.0001$ at every angle, which also confirms that the obliquity is $\cos\theta/r^2$
and not the script's $\cos^3\theta/r^2$.

### 3.4 Round-pinhole angular sensitivity, for comparison

Metzler et al. 2001 (as reproduced in Metzler & Accorsi 2005 eq. A.1) give for the round knife edge
$$g = \frac{d^2\sin^3\theta_{AM}}{16h^2} + \frac{\sin^5\theta_{AM}\tan^2\frac\alpha2}{8h^2\mu^2}
      \Big(1 - \frac{\cot^2\theta_{AM}}{\tan^2\frac\alpha2}\Big)^{1/2}
      \Big[1 - \frac{\cot^2\theta_{AM}}{\tan^2\frac\alpha2} + \mu d\csc\theta_{AM}\cot\frac\alpha2\Big].$$
Dividing by $\sin^3\theta_{AM}/(4\pi h^2)$ gives an effective area; for $d = w$ at 30°: $0.462, 0.791, 1.580,
3.826$ mm² (A–D), 23–27 % below the square's $0.600, 1.022, 2.029, 4.896$, mostly the geometric $\pi/4$. Its angular
fall-off is similar to the square's (C: ×0.876 vs ×0.883 from 0 to 30°).

### 3.5 RMS widths

At normal incidence $T = e^{-c(\max(|x|,|y|) - a)_+}$, $c = 2\mu/t$. Integrating over square shells (perimeter
$8s$, $\oint x^2 dl = 16s^3/3$ on the shell of half-side $s$):
$$\overline{x^2}_{\square} = \frac{\frac{w^4}{12} + \frac{2w^3}{3c} + \frac{4w^2}{c^2} + \frac{16w}{c^3} + \frac{32}{c^4}}
                                {w^2 + \frac{4w}{c} + \frac{8}{c^2}},\qquad
  \overline{x^2}_{\bigcirc} = \frac{\frac{R^4}{4} + \frac{R^3}{c} + \frac{3R^2}{c^2} + \frac{6R}{c^3} + \frac{6}{c^4}}
                                {R^2 + \frac{2R}{c} + \frac{2}{c^2}}\ (R = d/2),$$
(the round one from $\overline{x^2} = \overline{\rho^2}/2$; its $c\to\infty$ limit $R/2$ is Metzler et al. 2002
eq. 25). The denominators are $A_{eff}/1$ and $A_{eff}/\pi$ respectively. By symmetry $\overline{xy} = 0$ and
$\overline{x^2} = \overline{y^2}$, so the RMS of the square is **isotropic** even with penetration (geometrically
$w/\sqrt{12}$ in every direction). Values (knife-edge plane): square $0.327, 0.376, 0.476, 0.687$ mm vs geometric
$0.161, 0.230, 0.351, 0.579$; the exponential tails ($1/c = 0.138$ mm) dominate the second moment of the small
apertures. At 30° the RMS *decreases* (less penetration along the tilt; C: 0.413 ∥, 0.447 ⊥), in line with the
aspect ratio $< 1$ of Metzler et al. 2002 eq. (33). These closed forms agree with the brute-force moments to
$10^{-3}$ (the residual is $t_1 \ne t_2$).

### 3.6 Square ↔ round equivalents (normal incidence, $t = 1$, 140 keV in W)

| aperture | $w$ | equal area, geometric $2w/\sqrt\pi$ | equal area with penetration | equal FWHM along a side | equal RMS, geometric $2w/\sqrt3$ | equal RMS with penetration |
|---|---|---|---|---|---|---|
| A | 0.556 | 0.627 | 0.674 | 0.556 | 0.642 | 0.804 |
| B | 0.797 | 0.899 | 0.943 | 0.797 | 0.920 | 1.046 |
| C | 1.215 | 1.371 | 1.413 | 1.215 | 1.403 | 1.499 |
| D | 2.007 | 2.265 | 2.304 | 2.007 | 2.317 | 2.391 |

Equal area with penetration solves $\frac\pi4 d_e(d)^2 = A_{eff,\square}(w)$ with Paix's $d_e$. Equal point-profile
FWHM along a side is $d = w$ for every $\theta$ in the parallel direction (identical formulas) and to 0.006 mm (A, 30°; 0.0085 mm at 35°) in
the perpendicular one. A round pinhole matching the square's diagonal cut would need $d = \sqrt2 W$. For a line
source parallel to a side the geometric LSF FWHMs are $w$ (square) and $\frac{\sqrt3}{2}d$ (disk), so
$d = 1.155\,w$, the same factor as for the RMS. Johnson et al. 2016 (sensitivity- and FOV-matched, geometric-mean
LSF FWHM over 0–45°) find the square about 11–12 % sharper (read off their figure; the text gives 0.364 vs 0.414 mm) than the circle (0.364 vs 0.414 mm for a 0.3 mm square at
$\alpha = 10°$), consistent with these mappings: at equal area the circle's LSF is $0.977\,w$ wide, the square's
$0.71$–$1.0\,w$ depending on direction.

### 3.7 Simple first-order forms

Expanding the closed forms to second order in $\theta$ (radians), with $t = 1$ for the widths:
$$W_\parallel \approx w + \Delta L_k\big(1 - \tfrac32\theta^2\big),\qquad
  W_\perp \approx w + \Delta L_k\big(1 - \tfrac12\theta^2\big),\qquad
  \bar W \approx w + \Delta L_k\big(1 - \theta^2\big),$$
with errors $\le 0.002$ mm at 30° (A: $W_\parallel = 0.668$ vs the exact 0.666 mm). For the area, the strip
term gives $-\theta^2 (w/\mu)(t + 1/t)$ and the corner term $-\theta^2(2t^2 + 3)/\mu^2$ at *every* $\varphi$ (the
$\varphi$ dependence only enters at third order, through the $M^3$ and $3Mm^2$ terms), so
$$A_{eff}(\theta) \approx A_{eff}(0) - \theta^2\left[\frac{w}{\mu}\Big(t + \frac1t\Big) + \frac{2t^2 + 3}{\mu^2}\right]
  \;=\; w_s^2 - \theta^2\,(0.551\,w + 0.379)\ \text{mm}^2 \quad (t = 1,\ \mu = 3.63\ \text{mm}^{-1}),$$
which is low by 0.0–0.3 % at 15° and by 0.3 % (D) to 3.2 % (A) at 30° and $\varphi = 0$ (3.9 % for A at $\varphi = 45°$) because the neglected cubic term is
positive. Use the closed form of §3.3 (four lines of code) when 30° matters; the expansion is for reading the
trend: the small apertures lose sensitivity fastest with angle because their penetration share is largest.

### 3.8 Numerical verification

Two independent checks of the closed forms:

1. **Brute-force integration of the model** (`square_pinhole_model.py`, 2 µm grid): $A_{eff}$ agrees to
   $< 10^{-5}$ mm², side FWHMs to $10^{-4}$ mm, at $\theta = 0, 15, 30°$ and $\varphi = 0, 45°$ for A–D.
2. **Exact ray trace of the collimator CSG** (`raytrace_pyramid.py`): the same G4Trd solids as the GATE builder
   (frustum A − B − C, plus the hollow box, with the $\delta_z$ extensions), a point source at finite $b$, rays to a
   4 µm grid on the detection plane $z = -f$, tungsten path length by half-space clipping of the source–detector
   segment, sensitivity $= \sum T\cos\psi/(4\pi\,\text{dist}^2)\,dA$. Results at $b = 149.6$ mm
   (`raytrace_results.json`, widths scaled to the knife-edge plane):

| case | FWHM $x$ trace / model | FWHM $y$ trace / model | diagonals (trace) | RMS $x$, $y$ (trace) | $A_{eff}$ trace / model | $g_{trace}/g_{model}$ | $g_{script}/g_{trace}$ |
|---|---|---|---|---|---|---|---|
| A, 0° | 0.7469 / 0.7469 | 0.7469 / 0.7469 | 1.056 / 1.056 | 0.327, 0.327 | 0.7669 / 0.7669 | 0.9999 | 1.0005 |
| A, 30°, $\varphi$=0 | 0.6662 / 0.6661 | 0.7213 / 0.7213 | 0.925 / 0.925 | 0.239, 0.283 | 0.5978 / 0.5978 | 1.0000 | 0.9625 |
| A, 30°, $\varphi$=45° | 0.6937 / 0.6937 | 0.6937 / 0.6937 | 0.981 / 0.925 | 0.262, 0.262 | 0.6024 / 0.6024 | 1.0000 | 0.9553 |
| C, 0° | 1.4058 / 1.4059 | 1.4058 / 1.4059 | 1.988 / 1.986 | 0.476, 0.476 | 2.2965 / 2.2969 | 0.9998 | 1.0004 |
| C, 15°, $\varphi$=0 | 1.3861 / 1.3861 | 1.3993 / 1.3994 | 1.939 / 1.939 | 0.459, 0.468 | 2.2266 / 2.2269 | 0.9999 | 0.9627 |
| C, 30°, $\varphi$=0 | 1.3252 / 1.3252 | 1.3803 / 1.3803 | 1.857 / 1.857 | 0.413, 0.447 | 2.0268 / 2.0269 | 1.0000 | 0.8501 |
| C, 30°, $\varphi$=0, $b$ = 53 | 1.3251 / 1.3252 | 1.3802 / 1.3803 | 1.857 / 1.857 | 0.413, 0.447 | 2.0266 / 2.0269 | 0.9999 | 0.8502 |
| C, 40°, $\varphi$=0 | 1.2583 / 1.2582 | 1.3612 / 1.3612 | 1.776 / 1.776 | 0.372, 0.429 | 1.8296 / 1.8295 | 1.0000 | 0.7369 |
| D, 0° | 2.1976 / 2.1977 | 2.1976 / 2.1977 | 3.108 / 3.106 | 0.687, 0.687 | 5.2822 / 5.2837 | 0.9997 | 1.0007 |
| D, 30°, $\varphi$=45° | 2.1445 / 2.1446 | 2.1445 / 2.1446 | 3.033 / 2.976 | 0.650, 0.650 | 4.8967 / 4.8970 | 0.9999 | 0.8096 |

The parallel-beam model is exact to the precision of the trace for $b \ge 53$ mm (finite-distance effects are
$< 0.1$ % in area, $< 0.02$ in the transmission map). The last column is the current script's $g$ (Paix area and
$\cos^3\theta/r^2$) over the truth: right at the centre, 4–19 % low at 30° and 7–33 % low at 40°, with two
opposite errors partly cancelling (the missing $\cos^2\theta$ and the missing angular decrease of $A_{eff}$).

![PSF of aperture C from the exact trace at 0° and 30°: transmission map, point-profile cuts, line-spread functions](img/psf_C.png)

## 4. Literature on square / rectangular pinholes

Search: Undermind (workspace "GPU Monte Carlo & System Response Matrix", semantic + metadata lookup) and web.
Status: **[full]** = read in full by me from the PDF; **[agent]** = full text read by the Undermind PDF agent on
my questions, with the equations transcribed and, where stated, re-verified here; **[abstract]** = abstract or
citation only.

1. Accorsi R, Metzler SD. Analytic determination of the resolution-equivalent effective diameter of a pinhole
   collimator. *IEEE Trans Med Imaging* 2004;23(6):750–763. doi:10.1109/TMI.2004.826951. **[full]** Source of
   $d_{re}$, eqs. (22), (25), (29); round knife edge only; §V says the method "can be immediately applied to
   other pinhole edge shapes, provided that the appropriate formula for $\Delta L$ is used", which is what §3 does.
2. Metzler SD, Bowsher JE, Greer KL, Jaszczak RJ. Analytic determination of the pinhole collimator's point-spread
   function and RMS resolution with penetration. *IEEE Trans Med Imaging* 2002;21(8):878–887.
   doi:10.1109/TMI.2002.803129. **[full]** PRF with penetration (eq. 6), RMS definitions (7)–(8), limits (25)–(29).
   Notes (p. 886) that any aperture shape gives a geometric PRF of the same shape, and that the AR is angle dependent.
3. Metzler SD, Accorsi R. Resolution- versus sensitivity-effective diameter in pinhole collimation: experimental
   verification. *Phys Med Biol* 2005;50(21):5005–5017. doi:10.1088/0031-9155/50/21/004. **[full]** Confirms
   $d_{re}$ (eqs. 5–6) against measured FWHM for 57Co and 131I, 1 and 3 mm apertures; Paix overestimates, Anger
   better but $\theta$-independent; appendix A.1–A.3 gives the $\theta$-dependent Paix/Anger forms.
4. Metzler SD, Moore SC. Analytic determination of rectangular-pinhole sensitivity with penetration. *IEEE Trans
   Med Imaging* 2020;39(4):833–843. doi:10.1109/TMI.2019.2936187. **[full, 2026-10-30]** The direct reference for our
   geometry: rectangular aperture, eight half-planes (double-sided, no channel), acceptance angles $\alpha_x$,
   $\alpha_y$, source at $h(\tan\theta_x, \tan\theta_y, 1)$. Eq. (12) sensitivity integral, eq. (22) closed form,
   eq. (25) normal incidence $A_{eff} = w_xw_y + \frac{w_x}{\mu}\tan\frac{\alpha_y}{2} + \frac{w_y}{\mu}\tan\frac{\alpha_x}{2}
   + \frac{2}{\mu^2}\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}$, eqs. (26)–(29) penumbra tapering near the FOV
   edge; validated to 0.16 % (normal) and 0.29 % ($\theta_x = \theta_y = 27°$) against numerical integration for
   $\mu = 4$ mm$^{-1}$, $w = 1$ mm. No resolution formula. Eq. (22) equals §3.3 to machine precision.
5. Metzler SD, Xia D, Moore SC. Analytic determination of rectangular-pinhole sensitivity with penetration.
   *2014 IEEE NSS/MIC Conf. Rec.*, pp. 1–5. doi:10.1109/NSSMIC.2014.7431000. **[abstract]** Conference version of 4
   (aligned-plane paths only).
6. Johnson LC, Moore SC, Metzler SD. Effect of pinhole shape on projection resolution. *Phys Med Biol*
   2016;61(5):2003–2013. doi:10.1088/0031-9155/61/5/2003. **[full, 2026-10-30]** Square vs rounded-square vs circular
   apertures, 0.3/0.5/1 mm, $\alpha = 10$–$50°$, tungsten $\mu = 3.64$ mm$^{-1}$; resolution by ray-traced
   projections (geometric mean of LSF FWHM over 0–45°), sensitivity by numerical path sums with penetration.
   Perfect square gives the best FWHM at matched sensitivity and FOV (0.364 vs 0.414 mm, 0.3 mm, 10°); FWTM barely
   changes. No closed-form resolution formula; no side/diagonal statement.
7. Xia D, Moore SC, Park M-A, Cervo M, Metzler SD. Investigation of imaging properties for submillimeter
   rectangular pinholes. *Med Phys* 2015;42(12):6933–6944. doi:10.1118/1.4935200. **[agent]** 18 Pt/Ir inserts
   with 0.33 mm square apertures; sensitivity fitted as $A\sin^q\theta/(4\pi h^2)$ with effective edge
   $w_e = \sqrt A = 0.38 \pm 0.02$ mm and $q = 10.8 \pm 1.8$ (MC: $q = 7.7$); penumbra FOV formula (eqs. 8–10). No
   $\mu$-explicit sensitivity or resolution formula.
8. Xia D, Park M-A, Moore SC, Metzler SD. Preliminary investigation of imaging properties for sub-millimeter
   square pinholes. *2013 IEEE NSS/MIC*. doi:10.1109/NSSMIC.2013.6829173. **[abstract]**
9. Moore SC, Park M-A, Liu Z, Lyon MC, Johnson LC, Lushear VH, Westberg JG, Metzler SD. Design of a dual-resolution
   collimator for preclinical cardiac SPECT with a stationary triple-detector system. *Med Phys*
   2016;43(12):6336–6346. doi:10.1118/1.4966697. **[full, 2026-10-30]** 87 Pt/Ir 0.3 mm square pinholes
   ($\mu = 4.56$ mm$^{-1}$, half-angles 17.1°/14.9°). Uses, for the square side, exactly our pair of equations:
   eq. (2) $d_{eff} = d + \ln 2\tan\alpha/\mu$ (they give the two half-angles, 17.1° and 14.9°, and evaluate both directions; the phrase "in the direction considered" is ours),
   eq. (1) $res_{pin} = d_{eff}(M+1)/M$, eq. (3) $res_{sys} \approx \sqrt{res_{pin}^2 + (res_{int}/M)^2}$. No
   square/round equivalence stated.
10. Deprez K, Pato LRV, Vandenberghe S, Van Holen R. Characterization of a SPECT pinhole collimator for optimal
    detector usage (the lofthole). *Phys Med Biol* 2013;58(4):859–885. doi:10.1088/0031-9155/58/4/859.
    **[abstract]** (PDF not retrievable.) The lofthole is a *round* aperture with rectangular entrance/exit
    windows, so its projections tile a detector; it is not a square knife edge and its formulas exclude penetration.
    Not applicable here beyond the tiling argument.
11. Van Audenhaege K, Van Holen R, Vandenberghe S, Vanhove C, Metzler SD, Moore SC. Review of SPECT collimator
    selection, optimization, and fabrication for clinical and preclinical imaging. *Med Phys*
    2015;42(8):4796–4813. doi:10.1118/1.4927061. **[agent]** Eqs. (8)–(14) restate Paix (9), AM2004 (12)–(14) and
    the quadrature system resolution (10) with $m = f/h$; $\mu_W = 3.6$ mm$^{-1}$ at 140.5 keV. Nothing specific to
    square pinholes.
12. Metzler SD, Bowsher JE, Smith MF, Jaszczak RJ. Analytic determination of pinhole collimator sensitivity with
    penetration. *IEEE Trans Med Imaging* 2001;20(8):730–741. doi:10.1109/42.938241. **[abstract]** Round
    knife-edge angular sensitivity; its result is reproduced as M&A 2005 eq. (A.1) (read in full) and used in §3.4.
13. Smith MF, Jaszczak RJ. The effect of gamma ray penetration on angle-dependent sensitivity for pinhole
    collimation in nuclear medicine. *Med Phys* 1997;24(11):1701–1709. doi:10.1118/1.597957. **[abstract]**
    Derivation of Anger's $d_e$ from a parallel-beam sensitivity argument (AM2004 §I).
14. Paix D. Pinhole imaging of gamma rays. *Phys Med Biol* 1967;12(4):489–500. doi:10.1088/0031-9155/12/4/004.
    **[abstract]** Eq. (5) of AM2004.
15. Anger HO. Radioisotope cameras. In: Hine GJ (ed.), *Instrumentation in Nuclear Medicine*, vol. 1, Academic
    Press, 1967, pp. 485–552. **[citation]** Eqs. (2)–(3), (6)–(7) of AM2004.
16. Mallard JR, Myers MJ. The performance of a gamma camera for the visualization of radioactive isotopes in
    vivo. *Phys Med Biol* 1963;8:165–182. **[citation]** Eq. (1) of AM2004, the $\sin^3\theta_{AM}/(16h^2)$ law.
17. Tenney CR, Tornai MP, Smith MF, Turkington TG, Jaszczak RJ. Uranium pinhole collimators for 511-keV photon
    SPECT imaging of small volumes. *IEEE Trans Nucl Sci* 2001;48(4):1483–1489. doi:10.1109/23.958384.
    **[abstract]** Round pinholes, high energy; not used.
18. Bal G, Acton PD. Analytical derivation of the point spread function for pinhole collimators. *Phys Med Biol*
    2006;51(19):4923–4950. doi:10.1088/0031-9155/51/19/013. **[abstract]** Round apertures; not used.

No paper gives a closed-form *resolution* (FWHM) formula for a square knife edge with penetration; the Metzler
group applies the AM2004 normal-incidence formula to the side length (ref. 9) and otherwise ray-traces (ref. 6).
§3.2 supplies the oblique-incidence forms and shows the parallel one coincides with AM2004 eq. (22).

## 5. Recommendations for `analytic.py`

### 5.1 Formulas

With $t = 1$, $\Delta L_k = \ln 2/\mu = 0.1909$ mm, $\theta$ from the module axis, $\varphi$ the azimuth of the tilt
in the module frame ($\cos\varphi = (\mathbf d\cdot\mathbf u)/\sqrt{(\mathbf d\cdot\mathbf u)^2 + (\mathbf d\cdot\mathbf v)^2}$,
already available in `modules_seeing`):

$$W_u = w + \Delta L_k\cos\theta\Big(t - \frac{\tan^2\theta\cos^2\varphi}{t}\Big),\quad
  W_v = w + \Delta L_k\cos\theta\Big(t - \frac{\tan^2\theta\sin^2\varphi}{t}\Big),\quad
  R_{g,u} = W_u\frac{b+f}{f},\ R_{g,v} = W_v\frac{b+f}{f}.$$
Single number: $\bar W = w + \Delta L_k\cos\theta\,(t - \tan^2\theta/2t)$ (or the larger of the two if a
worst-case along the sides is wanted; multiply by $\sqrt2$ for the worst point-profile direction, the diagonal).

$$g = \frac{A_{eff}(\theta,\varphi)\cos\theta}{4\pi r^2},\qquad
  A_{eff} = w^2 + \frac{w\cos\theta}{\mu t}(2t^2 - \tan^2\theta) + \frac{t^2\cos^2\theta}{\mu^2}(1-M)\big[3(1-m^2)-(1-M)^2\big],$$
$M = \max(|\tan\theta\cos\varphi|, |\tan\theta\sin\varphi|)/t$, $m = \min(\dots)/t$. At $\theta = 0$ this is
$w_s^2$, so `paix(w)**2` stays correct there. Python:

```python
LN2, MU, T = np.log(2), 3.63, 1.0

def widths(w, theta, phi):                      # knife-edge plane, along the two sides
    c, tt = np.cos(theta), np.tan(theta) ** 2
    return (w + LN2 / MU * c * (T - tt * np.cos(phi) ** 2 / T),
            w + LN2 / MU * c * (T - tt * np.sin(phi) ** 2 / T))

def area_eff(w, theta, phi):                    # Metzler & Moore 2020 eq. 22 == derivation/square_pinhole.md 3.3
    c = np.cos(theta)
    tx, ty = np.abs(np.tan(theta) * np.cos(phi)), np.abs(np.tan(theta) * np.sin(phi))
    M, m = np.maximum(tx, ty) / T, np.minimum(tx, ty) / T
    return (w * w + w * c / (MU * T) * (2 * T * T - tx * tx - ty * ty)
            + T * T * c * c / MU ** 2 * (1 - M) * (3 * (1 - m * m) - (1 - M) ** 2))

def sensitivity(w, theta, phi, r):              # r = slant distance; equals A cos^3 / (4 pi b^2)
    return area_eff(w, theta, phi) * np.cos(theta) / (4 * np.pi * r ** 2)
```
Keep $R_i = p\,b/f$ and $R = \sqrt{R_g^2 + R_i^2}$ (AM2004 eq. 7; Moore et al. 2016 eq. 3), labelled as the
Gaussian-equivalent convention; see §5.3.

### 5.2 Numbers, A–D at $\theta = 0, 15, 30°$ (knife-edge plane; $R_g$ at the centre distance $b = 149.6$ mm, $(b+f)/f = 6.541$; $g$ per emitted photon)

| ap. | $\theta$ | $W_\parallel$ | $W_\perp$ | $\bar W$ | $R_{g,\parallel}$ | $R_{g,\perp}$ | $R_g$ now | $A_{eff}$ ($\varphi$-avg) | $\sqrt{A_{eff}}$ | $w_s$ now | $g\times10^6$ | $g\times10^6$ now | ratio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 0 | 0.747 | 0.747 | 0.747 | 4.89 | 4.89 | 4.89 | 0.7673 | 0.876 | 0.876 | 2.728 | 2.728 | 1.000 |
| A | 15 | 0.727 | 0.740 | 0.734 | 4.76 | 4.84 | 4.89 | 0.7224 | 0.850 | 0.876 | 2.315 | 2.294 | 1.009 |
| A | 30 | 0.666 | 0.721 | 0.694 | 4.36 | 4.72 | 4.89 | 0.6003 | 0.775 | 0.876 | 1.386 | 1.329 | 1.043 |
| B | 0 | 0.988 | 0.988 | 0.988 | 6.46 | 6.46 | 6.46 | 1.2261 | 1.107 | 1.107 | 4.360 | 4.360 | 1.000 |
| B | 15 | 0.968 | 0.981 | 0.975 | 6.33 | 6.42 | 6.46 | 1.1721 | 1.083 | 1.107 | 3.756 | 3.666 | 1.025 |
| B | 30 | 0.907 | 0.962 | 0.935 | 5.93 | 6.29 | 6.46 | 1.0222 | 1.011 | 1.107 | 2.361 | 2.124 | 1.112 |
| C | 0 | 1.406 | 1.406 | 1.406 | 9.20 | 9.20 | 9.20 | 2.2974 | 1.516 | 1.516 | 8.169 | 8.169 | 1.000 |
| C | 15 | 1.386 | 1.399 | 1.393 | 9.07 | 9.15 | 9.20 | 2.2276 | 1.492 | 1.516 | 7.138 | 6.869 | 1.039 |
| C | 30 | 1.325 | 1.380 | 1.353 | 8.67 | 9.03 | 9.20 | 2.0294 | 1.425 | 1.516 | 4.687 | 3.979 | 1.178 |
| D | 0 | 2.198 | 2.198 | 2.198 | 14.38 | 14.38 | 14.38 | 5.2856 | 2.299 | 2.299 | 18.794 | 18.794 | 1.000 |
| D | 15 | 2.178 | 2.191 | 2.185 | 14.25 | 14.33 | 14.38 | 5.1858 | 2.277 | 2.299 | 16.618 | 15.803 | 1.052 |
| D | 30 | 2.117 | 2.172 | 2.145 | 13.85 | 14.21 | 14.38 | 4.8962 | 2.213 | 2.299 | 11.308 | 9.155 | 1.235 |

"now" = `analytic.py` as it stands ($d_{re} = w + 0.191$ mm at all angles; $g = w_s^2\cos^3\theta/(4\pi r^2)$).
Changes: (i) **nothing at the helmet centre** (all modules at $\theta = 0$): $d_{re}$, $w_s$, $R_g$, $g$ and the
counts ratios are unchanged; (ii) off-centre $R_g$ drops by up to 0.08 mm × $(b+f)/f$ in the parallel direction
(0.5 mm at the centre distance, 0.3–0.8 mm over $b = 53$–$247$ mm) and 0.03 mm × $(b+f)/f$ in the perpendicular
direction; (iii) $g$ of oblique modules rises by 1–5 % at 15° and 4–24 % at 30° (A→D); since the large apertures
gain most, the count-weighted combination $R_{comb}$ moves slightly *up* and the information tables slightly
towards D. Worst point-profile direction: multiply $R_g$ by $\sqrt2$ (diagonal); line sources: §3.2.

### 5.3 Notes on the metric

- The quadrature $R = \sqrt{R_g^2 + R_i^2}$ is the literature convention (AM2004 eq. 7, Moore 2016 eq. 3,
  Van Audenhaege 2015 eq. 10) and is what "analytical resolution" means in those papers; keep it for
  comparability. It is exact for Gaussians. The aperture PSF (box with exponential skirts) convolved with a
  2 mm pixel box has FWHM $\approx \max(R_g, R_i)$ (a trapezoid's half-maximum sits at the larger half-width),
  e.g. C at the centre with parallel pixels: 11.1 mm instead of 14.4 mm. The RMS combination is exact:
  $\sigma^2 = \sigma_g^2 + \sigma_i^2$ with $\sigma_g = 0.476\times6.541 = 3.11$ mm (C, penetration included) and
  $\sigma_i = 11.08/\sqrt{12} = 3.20$ mm, giving $2.355\,\sigma = 10.5$ mm Gaussian-equivalent FWHM. The three
  readings span 10.5–14.4 mm for the same module; the qmd should say which it uses (it uses the quadrature).
- Penetration changes the RMS of the small apertures by ×2 but their FWHM by ×1.3; any RMS- or
  variance-based figure of merit (Fisher information, CRB) should use the penetration RMS of §3.5, not
  $d_{re}/\sqrt{12}$.
- All formulas assume zone I ($\tan\theta|\cos\varphi| < t_2 \approx 0.96$) and the parallel beam
  ($b \gg w$), both satisfied; the lead shield's vignetting at large $\theta$ is a separate geometric cut
  (not modelled, as stated in the qmd).

## 6. Files in this folder

- `square_pinhole_model.py` — closed forms (§3), brute-force checks; `python square_pinhole_model.py` prints the
  comparison for A–D.
- `raytrace_pyramid.py` — exact CSG trace (§3.8), writes `raytrace_results.json`.
- `crosscheck_tables.py` — Metzler & Moore 2020 cross-check, round equivalents, recommendation tables; writes
  `tables.md`, `tables.json`.
- `figures_lsf.py` — LSF widths (`lsf.json`) and `img/psf_C.png`.
