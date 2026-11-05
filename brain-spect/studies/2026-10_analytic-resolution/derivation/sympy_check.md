# Symbolic validation of the square knife-edge pinhole formulas

Check of `square_pinhole.md` (§3.1 path length, §3.2 widths, §3.3 effective area, §3.7 expansions), 30 October 2026.
Script: `sympy_check.py`, run with `micromamba run -n raytracing python sympy_check.py` (sympy 1.14.0, mpmath 1.3.0,
CPU only, about 100 s on 16 cores). Full console log: `sympy_check_output.txt`. Machine-readable results:
`sympy_check_results.json`.

**Result: 62 of 64 checks pass.** Every formula in §3.1–§3.3 and §3.7 is proven symbolically and reproduced
by high-precision quadrature to a relative error of at most 4e-26. The two failures are not formula errors: both are
small numerical *statements* in `square_pinhole.md` that are too optimistic (see "Discrepancies"). As instructed,
`square_pinhole.md` is unchanged.

## What each check proves

### a. Path length (§3.1)
- **Construction.**
  - Wall `+x` is the intersection of the two half-spaces $x - a - t_1z \ge 0$ and $x - a + t_2z \ge 0$, i.e.
    $x \ge a + t_1z$ for $z>0$ and $x \ge a + t_2|z|$ for $z<0$. The other three walls are built the same way.
  - That gives 8 half-planes and 4 walls; the tungsten is the union of the walls.
  - The ray is $x = x_0 + \tau_xz$, $y = y_0 + \tau_yz$.
- **Method.** For each half-space, SymPy extracts the linear condition $c_0 + c_1z \ge 0$ along the ray.
- **Zone I, stated explicitly.**
  - Every coefficient $c_1$ is checked to be $\pm$ one of the eight gaps
    $t_{1,2} \pm \tau_{x,y}$.
  - Zone I is the assumption that all eight gaps are positive, i.e. $\max(|\tau_x|, |\tau_y|) < \min(t_1, t_2)$
    (= §3.1's $|\tau_x|, |\tau_y| < \min(t_1,t_2)$).
  - Under that assumption each wall gives exactly one lower and one upper bound in $z$. The sign of the
    shared $c_0$ decides whether the wall interval contains $z=0$ or is empty.
- **All nine regions of the knife-edge plane** (inside / beyond $+$ / beyond $-$ edge, in $x$ and in $y$):
  - the opening: no wall is hit, so $\Lambda=0$ and $T_{max}=1$;
  - beyond one side: only that wall is hit, the opposite wall is provably missed, and
    $\Lambda = p(U+L)$ with $U^n = 1/(t_1-\tau)$, $L^n = 1/(t_2+\tau)$, $U^f = 1/(t_1+\tau)$, $L^f = 1/(t_2-\tau)$;
  - beyond a corner: exactly the two adjacent walls are hit. Both intervals contain $z=0$, so the union is
    one interval and $\Lambda = \max(pU_x, qU_y) + \max(pL_x, qL_y)$ (all four corners).
- **Path factor.** $|d|/dz = \sqrt{1+\tau_x^2+\tau_y^2} = 1/\cos\theta$ (trig identity), so $\mu\Delta L = \kappa\Lambda$ with
  $\kappa = \mu/\cos\theta$. At normal incidence $\Lambda = 2p/t_h$.
- **Zone-I limit.** Along a side the limit is $\arctan(\min t_2) = 43.83°$ (§3.1 says 43.8°).
- **Not covered.** The walls are infinite double wedges (no outer body, no channel), the beam is parallel, and
  the attenuation is pure exponential (no scatter). The ray trace in (e) covers the finite CSG and a finite $b$.

### b. Effective area (§3.3)
- **Strips.** SymPy integrates $\int_0^\infty e^{-\kappa p(U+L)}dp = 1/(\kappa(U+L))$.
  - The sum of $1/(U+L)$ over the four edges is $(2t^2-\tau_x^2-\tau_y^2)/t$ for any signs of $\tau$.
- **Corners, setup.** With $q = ps$, $\Lambda(p,ps) = p\Lambda(1,s)$ (1-homogeneous), and
  $\int_0^\infty p\,e^{-\kappa p\Lambda}dp = 1/(\kappa\Lambda)^2$.
- **Corners, both orderings as explicit cases (no `Max`).**
  - Case 1 ($s_U \le s_L$) uses the parametrisation $U_x = s_UU_y$, $L_x = s_LL_y$, $s_L = s_U+\delta$, $\delta > 0$.
  - Case 2 ($s_L < s_U$) is the same with $s_U = s_L+\delta$.
  - On each of the three $s$-segments the chosen branch of both maxima is verified (chosen − other ≥ 0 at both
    segment ends; it is linear in $s$).
  - The three integrals then equal the §3.3 formula for $\kappa^2I$ exactly, in both cases. The two cases agree
    at $s_U = s_L$.
- **Four-corner sum for $t_1=t_2=t$.**
  - The ordering of each corner is decided symbolically, in sector A ($\tau_x\ge\tau_y\ge0$) and in sector B
    ($\tau_y\ge\tau_x\ge0$).
  - Sector A: corners ++ and +− are case 2, −+ and −− are case 1. Sector B: ++ case 1, +− case 2, −+ case 1,
    −− case 2.
  - In both sectors the sum equals $t^2(1-M)[3(1-m^2)-(1-M)^2]$ (rational identity, residual 0).
  - Other azimuths follow from the mirror symmetries $x\to-x$, $y\to-y$, $x\leftrightarrow y$; the numerics in (e)
    use $\varphi$ over all four quadrants.
- **$A_{eff}$.** Assembled from the integrals, it equals the §3.3 boxed form (residual 0, both sectors).
  - With $t_1 \ne t_2$ at $\theta=0$ it is $w^2 + 2wt_h/\mu + 2t_h^2/\mu^2$ (residual 0).
- **`simplify(A_ours − A_paper) == 0` holds in both sectors.**
  - A_paper is Metzler & Moore 2020 eq. 22 as typed in `crosscheck_tables.area_eff_mm2020`, written in their
    variables ($\tan\theta_x$, $\tan\theta_y$, $\cos\theta = (1+\tan^2\theta_x+\tan^2\theta_y)^{-1/2}$).
  - **Transcription not yet checked against the PDF.** M&M 2020 is not in `pytorch-optix/references/`.
  - Caveat: the expression in `crosscheck_tables.py` is already typed in the same algebraic shape as ours. This
    identity therefore proves only the variable change ($\tan^2\theta = \tan^2\theta_x+\tan^2\theta_y$, the cosine
    powers). It is not independent evidence until eq. 22 is compared with the paper.

### c. Limits and expansions (§3.3, §3.7)
- **Normal incidence.** $A_{eff}(\theta=0) = w^2 + 2wt/\mu + 2t^2/\mu^2$ (Paix), both sectors.
- **Area series.** `series(A_eff, θ, 0, 3)` equals $A_{eff}(0) - \theta^2[\frac{w}{\mu}(t+\frac1t) + \frac{2t^2+3}{\mu^2}]$
  in both sectors, so the $\theta^2$ term does not depend on $\varphi$.
- **First $\varphi$-dependent order.** The $\theta^3$ coefficient is
  $\cos\varphi(2-\cos2\varphi)/(\mu^2t) = (\cos^3\varphi + 3\cos\varphi\sin^2\varphi)/(\mu^2 t) > 0$ (sector A).
- **Width series.** $W_\parallel \approx w + \Delta L_k(1-\frac32\theta^2)$, $W_\perp \approx w + \Delta L_k(1-\frac12\theta^2)$ and
  $\bar W \approx w + \Delta L_k(1-\theta^2)$ ($t=1$) are reproduced exactly.
  - The general form is $W_x \approx w + \Delta L_k[t - \theta^2(t/2 + \cos^2\varphi/t)]$.
- **Numbers quoted in §3.7.**
  - $2/\mu = 0.551$, $5/\mu^2 = 0.379$: correct.
  - The area expansion is low at every $\varphi$: correct.
  - For the quoted percentages and the "≤ 0.002 mm" width error, see "Discrepancies".

### d. Widths (§3.2) and Accorsi & Metzler 2004
- **Edge offset.** `solve(exp(−κp(U+L)) = k)` gives $p_k = \Delta L_k\cos\theta/(U+L)$ with $\Delta L_k = -\ln k/\mu$.
  - $T_{max} = 1$ comes from (a).
  - The profile is monotone beyond each edge, so the crossing is unique.
- **Side widths.** $w + p_k^n + p_k^f$ equals the §3.2 boxed $W_x$ and $W_y$ for $t_1=t_2=t$.
  - At $\theta=0$ with $t_1\ne t_2$: $W = w + \Delta L_k t_h$.
  - $(W_x+W_y)/2 = w + \Delta L_k\cos\theta(t - \tan^2\theta/2t)$, independent of $\varphi$.
- **Diagonal, normal incidence.** The point-profile FWHM is $\sqrt2(w + \Delta L_kt_h) = \sqrt2W$ exactly.
- **AM2004, transcribed from the PDF** (`pytorch-optix/references/pinhole-collimator/Analytic_determination_of_the_resolution-equivalent_effective_diameter_of_a_pinhole_collimator.pdf`,
  p. 753–754; $\theta$ there is $\theta_{AM}$, measured from the pinhole plane):
  - eq. (22): $d_{re/\!/} \approx d + \Delta L_k\left(\tan^2\frac\alpha2 - \cot^2\theta\right)\cot\frac\alpha2\,\sin\theta$
  - eq. (25): $d_{re\perp} \approx \sqrt{\left(d + \Delta L_k\tan\frac\alpha2\sin\theta\right)^2 - \Delta L_k^2\cos^2\theta}$
  - eq. (29): $d_{re} = d + \Delta L_k\tan\frac\alpha2$

  These match the forms quoted in `square_pinhole.md` §2 and in `square_pinhole_model.py`.
- **Eq. 22, term by term.** Substituting $\tan\theta = \cot\theta_{AM}$ and $\cos\theta = \sin\theta_{AM}$ in $W_\parallel$
  ($\varphi=0$), with $d\to w$ and $\tan\frac\alpha2 = t$, gives the same three terms as AM2004 eq. 22:
  $w + \Delta L_k t\sin\theta_{AM} - \Delta L_k\sin\theta_{AM}\cot^2\theta_{AM}/t$.
  - The full substitution $\theta = \pi/2-\theta_{AM}$ also gives residual 0.
- **Eq. 25.** $W_\perp^2 - (\text{AM25})^2 = \Delta L_k^2\cos^2\theta_{AM} = \Delta L_k^2\sin^2\theta$ exactly. The cone-curvature
  term inside the root is the only difference.
- **Eq. 29.** At $\theta = 0$, $W$ equals AM2004 eq. 29.
- **§2 table numbers at 30°** ($W_\parallel$, $W_\perp$, AM25, $\sqrt2W$ for A–D) are reproduced to 3 decimals
  (max deviation 0.0004).

### e. Numerics
- **Test points.**
  - 20 points with $t_1=t_2$: 16 random points ($w\in[0.2,3]$, $t\in[0.4,2]$, $\varphi\in[0,2\pi)$, $\theta$ up to 97 % of
    the zone-I limit, $\theta$ up to 64°) plus normal incidence, $\varphi=0$, $\varphi=45°$ exactly ($M=m$), and 99 %
    of the zone-I limit.
  - 10 further random points with $t_1\ne t_2$.
  - $\mu = 3.63$ mm⁻¹, mpmath at 25 digits, seed fixed.
- **Raw references, independent of every closed form.**
  - Area: `mpmath.quad` of the transmission computed straight from the 8 half-planes (interval intersection per
    wall, union length, no zone-I assumption).
  - Quadrature breakpoints: the edges, plus the corner kinks located from two raw evaluations of the linear
    interval endpoints.
  - Widths and both diagonals: half-maximum root search on the raw transmission.

| comparison | points | max relative difference |
|---|---|---|
| boxed $A_{eff}$ vs mpmath.quad | 20 ($t_1=t_2$) | 2.6e-26 |
| boxed $W_x$, $W_y$ vs half-maximum search | 20 | 2.6e-26 |
| diagonal FWHM from $\Lambda = p[\max U + \max L]$ vs half-maximum | 20 | 3.9e-26 |
| general-slope area (§3.3 corner formula, case chosen per corner) vs quad | 10 ($t_1\ne t_2$) | 2.6e-26 |
| general $W_x$, $W_y$ (§3.2 bracket) vs half-maximum | 10 | 2.6e-26 |
| diagonals vs half-maximum | 10 | 2.6e-26 |
| `square_pinhole_model.area_eff_square`, `fwhm_sides_square` (float64) vs closed forms | 30 | 2.2e-16 |

**Ray trace** (`raytrace_results.json`, 34 cases: exact CSG of the GATE collimator with the real slopes
$t_1\ne t_2$, $b = 53$–$247$ mm, 4 µm grid). Closed forms evaluated with the general slopes:

| quantity | max relative difference | limit set by |
|---|---|---|
| JSON `A_eff_model`, `model_fwhm_sides` vs closed forms | 2.2e-16 | float64 |
| $A_{eff}$ trace vs closed form | 8.3e-4 (C, θ = 0, b = 53 mm; 1.8e-4 at b = 149.6) | finite b and grid |
| side FWHMs trace vs closed form | 1.2e-4 | grid |
| both diagonals (incl. oblique) trace vs closed form | 1.1e-3 (C, θ = 0) | the trace's own diag+/diag− asymmetry at θ = 0, 1.03e-3, which symmetry says must be 0 |

The diagonal closed form at oblique incidence is not stated in `square_pinhole.md` as a formula. It is
$W_{diag\pm} = \sqrt2\,[w + \Delta L_k\cos\theta \sum_{\text{2 corners}} 1/(\max(U_x,U_y)+\max(L_x,L_y))]$, which follows from §3.2's
$\Lambda = p[\max(U_x,U_y)+\max(L_x,L_y)]$. It matches the trace's oblique diagonals (e.g. A, 30°, φ = 45°:
0.9811 / 0.9246 trace, 0.9811 / 0.9247 closed form) and the raw half-maximum search to 4e-26.

## Discrepancies found in `square_pinhole.md` (not fixed there)

1. **"W⊥ is AM2004 eq. 25 without the last term (≤ 0.003 mm here)" (§2 table) and "to 0.003 mm in the
   perpendicular one" (§3.6) are too small for the narrow apertures.**
   - The identity itself is exact (d above).
   - The size of the difference $W_\perp - d_{re\perp}$ at $t=1$, $\mu = 3.63$:

     | θ | A | B | C | D |
     |---|---|---|---|---|
     | 30° | 0.0063 mm | 0.0047 mm | 0.0033 mm | 0.0021 mm |
     | 35° | 0.0085 mm | 0.0063 mm | 0.0044 mm | 0.0028 mm |

   - The §2 table's own numbers already show this: $W_\perp$ = 0.721 vs AM25 = 0.715 for A.
   - Correct wording: "≤ 0.006 mm at 30° (A), 0.002 mm (D)", or "≤ 0.009 mm up to 35°". The conclusion
     ("small") is unaffected.
2. **§3.7 area expansion: "low by 0.0–0.3 % at 15° and by 0.3 % (D) to 3.2 % (A) at 30°" holds at φ = 0 only.**
   - At φ = 0 the errors are 0.26 / 0.03 % (15°) and 3.15 / 0.32 % (30°), as quoted.
   - At φ = 45° they are 0.34 / 0.04 % and **3.88 / 0.41 %** (A / D).
   - The text should say "at φ = 0; up to 3.9 % (A) at φ = 45°".
3. **Minor, stated to rounding only.**
   - §3.7 width expansions: the error at 30° is 0.0022 mm for every aperture (A: 0.6684 vs 0.6662), quoted as
     "≤ 0.002 mm". The check passes at the quoted 3 decimals.
   - §3.7 also says the φ dependence enters at third order "through $M^3$". The cubic term is
     $(t^2\cos^2\theta/\mu^2)(M^3 + 3Mm^2)$, so $3Mm^2$ contributes as well. Wording only; the formula in §3.3 is
     correct.
4. **Not a discrepancy, but a limit of this check.**
   - The Metzler & Moore 2020 eq. 22 comparison is only as good as its transcription in `crosscheck_tables.py`,
     which has not been compared with the PDF (see b).
   - §0 item 2 and §3.3 ("identical to Metzler & Moore 2020 eq. 22") should stay marked as pending until the
     literature check reads eq. 22 from the paper.

No formula in §3.1–§3.3 or §3.7 was found wrong.

## What this does not cover
- The modelling assumptions themselves:
  - parallel beam (checked against the finite-$b$ trace, < 0.1 %);
  - infinite double wedge and pure exponential attenuation (no scatter, no K-fluorescence);
  - the FWHM threshold model for resolution;
  - zone I (θ ≲ 43.8° along a side for our slopes).
- The RMS formulas of §3.5, the round-pinhole comparison (§3.4), the line-spread functions and the
  sensitivity/obliquity statements of §0 item 3 were outside this task and are not checked here.
