"""Symbolic (SymPy) and high-precision numeric (mpmath) validation of the square knife-edge pinhole formulas
of square_pinhole.md: §3.1 path length, §3.2 widths, §3.3 effective area, §3.7 expansions.  CPU only.

    micromamba run -n raytracing python sympy_check.py     (prints PASS/FAIL per check, writes sympy_check_results.json)

a. path length from the 8 half-planes of the double-sided square knife edge and the oblique ray (theta, phi);
b. effective area: strip and corner integrals done symbolically (corners: q = p s, p first, then piecewise in s with
   both breakpoint orderings as explicit cases), four-corner sum = the boxed closed form, = Metzler & Moore 2020
   eq. 22 as typed in crosscheck_tables.py (transcription not yet checked against the PDF);
c. theta -> 0 (Paix form) and the second-order series of §3.7;
d. widths from T = k T_max, the sqrt2 diagonal, Accorsi & Metzler 2004 eqs. 22, 25, 29;
e. 20 + 10 random zone-I points: closed forms vs mpmath.quad of the raw transmission and a numeric half-maximum
   search (both built from the half-planes, not from the formulas); raytrace_results.json.
"""

import json
import math
import multiprocessing
import os
import random
import sys
import time
from pathlib import Path

import mpmath as mpm
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import square_pinhole_model as model  # noqa: E402

RESULTS = []


def report(part, name, ok, residual, note=""):
    ok = bool(ok)
    RESULTS.append({"part": part, "check": name, "pass": ok, "residual": str(residual), "note": note})
    print(f"[{'PASS' if ok else 'FAIL'}] {part} {name}: residual = {residual}" + (f"  ({note})" if note else ""), flush=True)


def is_zero(expr):
    """Exact zero test: cancel/together first, simplify only if needed."""
    e = sp.cancel(sp.together(sp.expand(expr)))
    if e == 0:
        return True, e
    e = sp.simplify(e)
    return e == 0, e


# =================================================================================================== symbols
z = sp.Symbol("z", real=True)
a, p, q = sp.symbols("a p q", positive=True)  # a = w/2; p, q = offsets beyond an edge
xi1, xi2, eta1, eta2 = sp.symbols("xi1 xi2 eta1 eta2", positive=True)  # parametrise |x0| < a, |y0| < a
t1, t2, t = sp.symbols("t1 t2 t", positive=True)
tx, ty = sp.symbols("tau_x tau_y", real=True)  # in-plane slopes dx/dz, dy/dz of the ray
th, ph = sp.symbols("theta phi", real=True)
T_ = sp.Symbol("T", positive=True)  # tan(theta), theta in (0, pi/2)
w, mu, kap, k = sp.symbols("w mu kappa k", positive=True)
cth = sp.Symbol("c", positive=True)  # cos(theta)

# zone I: every coefficient of z met below must be one of these, and all of them are > 0
ZONE_I_GAPS = [t1 - tx, t1 + tx, t2 - tx, t2 + tx, t1 - ty, t1 + ty, t2 - ty, t2 + ty]


def gap_sign(c1):
    for g in ZONE_I_GAPS:
        if sp.expand(c1 - g) == 0:
            return 1
        if sp.expand(c1 + g) == 0:
            return -1
    raise AssertionError(f"coefficient {c1} is not +- a zone-I gap")


def known_sign(e):
    e = sp.factor(sp.together(e))
    if e.is_positive:
        return 1
    if e.is_negative:
        return -1
    raise AssertionError(f"sign of {e} not decidable")


# =================================================================================================== part a
def part_a():
    print("\n=== a. path length from the 8 half-planes ===")
    # Ray crossing the knife-edge plane at (x0, y0): x = x0 + tau_x z, y = y0 + tau_y z (z = 0 knife edge,
    # +z towards the object).  Wall '+x' = {x - a - t1 z >= 0} & {x - a + t2 z >= 0}, i.e. x >= a + t1 z for
    # z > 0 and x >= a + t2 |z| for z < 0; likewise '-x' (x -> -x), '+y', '-y'.  8 half-planes, 4 walls; the
    # tungsten is their union.
    coords = {"in": lambda off, e1, e2: a * (e1 - e2) / (e1 + e2), "+": lambda off, e1, e2: a + off,
              "-": lambda off, e1, e2: -a - off}

    def U_L(cls, tau):
        return (1 / (t1 - tau), 1 / (t2 + tau)) if cls == "+" else (1 / (t1 + tau), 1 / (t2 - tau))

    all_ok = True
    for cx in ("in", "+", "-"):
        for cy in ("in", "+", "-"):
            x0 = coords[cx](p, xi1, xi2)
            y0 = coords[cy](q, eta1, eta2)
            X, Y = x0 + tx * z, y0 + ty * z
            walls = {}
            for name, u, sg in (("+x", X, 1), ("-x", X, -1), ("+y", Y, 1), ("-y", Y, -1)):
                lo = hi = None
                c0s = set()
                for f in (sg * u - a - t1 * z, sg * u - a + t2 * z):
                    f = sp.expand(f)
                    c1, c0 = f.coeff(z, 1), f.coeff(z, 0)
                    c0s.add(sp.simplify(c0))
                    end = sp.simplify(-c0 / c1)
                    if gap_sign(c1) > 0:
                        assert lo is None
                        lo = end
                    else:
                        assert hi is None
                        hi = end
                assert lo is not None and hi is not None and len(c0s) == 1
                c0 = c0s.pop()
                # endpoint = -c0/c1 with c1 = +-gap: lo has the sign of -c0, hi the sign of c0
                walls[name] = (lo, hi, known_sign(c0) > 0)  # True: lo < 0 < hi (contains z = 0); False: hi < 0 < lo (empty)
            hit = {n: v for n, v in walls.items() if v[2]}
            expect_hit = ({"+x"} if cx == "+" else {"-x"} if cx == "-" else set()) | \
                         ({"+y"} if cy == "+" else {"-y"} if cy == "-" else set())
            ok = set(hit) == expect_hit
            # z-extent of the union (all hit intervals contain z = 0, so the union is one interval)
            if not hit:
                lam_expr, lam_claim = sp.Integer(0), sp.Integer(0)
            elif len(hit) == 1:
                (lo, hi, _), = hit.values()
                off, cls, tau = (p, cx, tx) if cx != "in" else (q, cy, ty)
                Uc, Lc = U_L(cls, tau)
                lam_expr, lam_claim = hi - lo, off * (Uc + Lc)
                ok &= is_zero(hi - off * Uc)[0] and is_zero(lo + off * Lc)[0]
            else:
                (lox, hix, _), (loy, hiy, _) = hit["+x" if cx == "+" else "-x"], hit["+y" if cy == "+" else "-y"]
                Ux, Lx = U_L(cx, tx)
                Uy, Ly = U_L(cy, ty)
                ok &= all(is_zero(e)[0] for e in (hix - p * Ux, lox + p * Lx, hiy - q * Uy, loy + q * Ly))
                lam_expr = sp.Max(hix, hiy) - sp.Min(lox, loy)
                lam_claim = sp.Max(p * Ux, q * Uy) + sp.Max(p * Lx, q * Ly)
            ok &= is_zero(lam_expr - lam_claim)[0] if len(hit) < 2 else True
            all_ok &= ok
            report("a", f"region x:{cx:>2} y:{cy:>2}", ok, 0 if ok else "mismatch",
                   f"walls hit {sorted(hit) or 'none'}; Lambda = {sp.simplify(lam_claim)}")
    # path length = Lambda * |d|/dz,  |d|/dz = sqrt(1 + tau_x^2 + tau_y^2) = 1/cos(theta)
    ident = sp.simplify((1 + (sp.tan(th) * sp.cos(ph)) ** 2 + (sp.tan(th) * sp.sin(ph)) ** 2) * sp.cos(th) ** 2 - 1)
    report("a", "|d|/dz = 1/cos(theta), so mu*DeltaL = kappa*Lambda, kappa = mu/cos(theta)", ident == 0, ident)
    report("a", "normal incidence: Lambda = p (1/t1 + 1/t2) = 2p/t_h", is_zero(
        (1 / t1 + 1 / t2) - 2 / (2 * t1 * t2 / (t1 + t2)))[0], 0)
    zl = math.degrees(math.atan(min(model.slopes(n)[1] for n in model.WIDTHS)))
    report("a", "zone-I limit along a side, theta < atan(min t2) = 43.8 deg (§3.1)", abs(zl - 43.8) < 0.05, f"{zl:.3f} deg")
    return all_ok


# =================================================================================================== part b
U, L, Lam, s = sp.symbols("U L Lambda s", positive=True)
Ux, Lx, Uy, Ly = sp.symbols("U_x L_x U_y L_y", positive=True)
sU, sL, dl = sp.symbols("s_U s_L delta", positive=True)


def corner_md(Ux_, Lx_, Uy_, Ly_, case):
    """kappa^2 I of §3.3 with the ordering given explicitly: case 1 = s_U <= s_L, case 2 = s_L < s_U."""
    sU_, sL_ = Ux_ / Uy_, Lx_ / Ly_
    if case == 1:
        sa, sb, al, be = sU_, sL_, Lx_, Uy_
    else:
        sa, sb, al, be = sL_, sU_, Ux_, Ly_
    return sa / (Ux_ + Lx_) ** 2 + 1 / (be * (al + be * sa)) - 1 / (be * (al + be * sb)) + 1 / (sb * (Uy_ + Ly_) ** 2)


def part_b():
    print("\n=== b. effective area ===")
    strip = sp.integrate(sp.exp(-kap * p * (U + L)), (p, 0, sp.oo))
    report("b", "strip: int_0^inf exp(-kappa p (U+L)) dp = 1/(kappa (U+L))", is_zero(strip - 1 / (kap * (U + L)))[0], 0,
           f"sympy: {strip}")
    inner = sp.integrate(p * sp.exp(-kap * p * Lam), (p, 0, sp.oo))
    report("b", "corner, q = p s, dq = p ds: int_0^inf p exp(-kappa p Lambda(1,s)) dp = 1/(kappa Lambda)^2",
           is_zero(inner - 1 / (kap * Lam) ** 2)[0], 0, "Lambda(p, ps) = p Lambda(1, s) for p > 0 (max is 1-homogeneous)")

    # piecewise s-integral; each case parametrised so that its ordering holds: Ux = sU Uy, Lx = sL Ly
    cases = {
        1: ({sL: sU + dl}, [(0, sU, Ux + Lx, ("Ux", "Lx")), (sU, sL, s * Uy + Lx, ("sUy", "Lx")),
                            (sL, sp.oo, s * (Uy + Ly), ("sUy", "sLy"))]),
        2: ({sU: sL + dl}, [(0, sL, Ux + Lx, ("Ux", "Lx")), (sL, sU, Ux + s * Ly, ("Ux", "sLy")),
                            (sU, sp.oo, s * (Uy + Ly), ("sUy", "sLy"))]),
    }
    for case, (order_sub, pieces) in cases.items():
        sub = {Ux: sU * Uy, Lx: sL * Ly}
        branch_ok = True
        total = 0
        for lo, hi, lam, (bu, bl) in pieces:
            # verify the branch of each max on [lo, hi]: chosen - other >= 0 at both ends (linear in s)
            for chosen, other in ((Ux if bu == "Ux" else s * Uy, s * Uy if bu == "Ux" else Ux),
                                  (Lx if bl == "Lx" else s * Ly, s * Ly if bl == "Lx" else Lx)):
                diff = sp.expand((chosen - other).subs(sub))
                for end in (lo, hi):
                    val = diff.coeff(s, 1) if end is sp.oo else diff.subs(s, end)
                    val = sp.factor(sp.expand(val.subs(order_sub)))
                    branch_ok &= bool(val.is_nonnegative)
            total += sp.integrate(1 / lam ** 2, (s, lo, hi))
        claim = corner_md(Ux, Lx, Uy, Ly, case)
        ok, res = is_zero((total - claim).subs(sub).subs(order_sub))
        report("b", f"corner case {case} ({'s_U <= s_L' if case == 1 else 's_L < s_U'}): branches of both max", branch_ok, 0)
        report("b", f"corner case {case}: kappa^2 I = §3.3 formula", ok, res)
    ok, res = is_zero((corner_md(Ux, Lx, Uy, Ly, 1) - corner_md(Ux, Lx, Uy, Ly, 2)).subs({Ux: sU * Uy, Lx: sU * Ly}))
    report("b", "cases 1 and 2 agree at s_U = s_L (continuity)", ok, res)

    # ---- symmetric slopes t1 = t2 = t: four strips and four corners
    def UL(cls, tau):
        return (1 / (t - tau), 1 / (t + tau)) if cls == "+" else (1 / (t + tau), 1 / (t - tau))

    strips = sum(1 / (sum(UL(c, tau))) for tau in (tx, ty) for c in "+-")
    ok, res = is_zero(strips - (2 * t ** 2 - tx ** 2 - ty ** 2) / t)
    report("b", "sum over 4 edges of 1/(U+L) = (2t^2 - tau_x^2 - tau_y^2)/t (any signs)", ok, res)

    cc, dd, ee = sp.symbols("c_ d_ e_", nonnegative=True)
    eep = sp.Symbol("e_p", positive=True)
    F_by_case = {}
    for case_name, par, (Mv, mv) in (("A: tau_x >= tau_y >= 0", {ty: cc, tx: cc + dd, t: cc + dd + eep}, (tx, ty)),
                                     ("B: tau_y >= tau_x >= 0", {tx: cc, ty: cc + dd, t: cc + dd + eep}, (ty, tx))):
        F = 0
        picked = []
        for cx in "+-":
            for cy in "+-":
                Ux_, Lx_ = UL(cx, tx)
                Uy_, Ly_ = UL(cy, ty)
                gap = sp.factor(sp.together((Lx_ / Ly_ - Ux_ / Uy_).subs(par)))
                if gap.is_nonnegative:
                    cs = 1
                elif gap.is_nonpositive:
                    cs = 2
                else:
                    raise AssertionError(f"ordering undecided for corner {cx}{cy}: {gap}")
                picked.append(f"{cx}{cy}:{cs}")
                F += corner_md(Ux_, Lx_, Uy_, Ly_, cs)
        M_, m_ = Mv / t, mv / t
        claim = t ** 2 * (1 - M_) * (3 * (1 - m_ ** 2) - (1 - M_) ** 2)
        ok, res = is_zero(F - claim)
        F_by_case[case_name[0]] = (F, M_, m_)
        report("b", f"four corners, case {case_name}: kappa^2 sum I = t^2 (1-M)[3(1-m^2) - (1-M)^2]", ok, res,
               "orderings " + ", ".join(picked))

    # ---- A_eff: derived (integrals) vs A_ours (§3.3 boxed) vs A_paper (crosscheck_tables.area_eff_mm2020)
    def A_ours(case):  # boxed formula, theta in (0, pi/2): tan = T, cos = 1/sqrt(1+T^2); phi in the case's octant
        c_ = 1 / sp.sqrt(1 + T_ ** 2)
        txv, tyv = T_ * sp.cos(ph), T_ * sp.sin(ph)
        M_, m_ = (txv / t, tyv / t) if case == "A" else (tyv / t, txv / t)
        return w ** 2 + w * c_ / (mu * t) * (2 * t ** 2 - T_ ** 2) + t ** 2 * c_ ** 2 / mu ** 2 * (1 - M_) * (
            3 * (1 - m_ ** 2) - (1 - M_) ** 2)

    tX, tY = sp.symbols("tan_theta_x tan_theta_y", nonnegative=True)

    def A_paper(case):  # crosscheck_tables.area_eff_mm2020 in Metzler-Moore variables; cos(theta) = (1+tX^2+tY^2)^-1/2
        c_ = 1 / sp.sqrt(1 + tX ** 2 + tY ** 2)
        M_, m_ = (tX / t, tY / t) if case == "A" else (tY / t, tX / t)
        strips_ = c_ * w / (mu * t) * (2 * t * t - tX * tX - tY * tY)
        corners_ = t * t * c_ * c_ / mu ** 2 * (1 - M_) * (3 * (1 - m_ * m_) - (1 - M_) ** 2)
        return w * w + strips_ + corners_

    for case in "AB":
        F, _, _ = F_by_case[case]
        # derived: w^2 + (w/kappa) sum 1/(U+L) + (1/kappa^2) F, kappa = mu/cos(theta)
        A_der = w ** 2 + w * cth / mu * strips + cth ** 2 / mu ** 2 * F
        A_der = A_der.subs({tx: T_ * sp.cos(ph), ty: T_ * sp.sin(ph), cth: 1 / sp.sqrt(1 + T_ ** 2)})
        ok1, r1 = is_zero(A_der - A_ours(case))
        report("b", f"case {case}: A_eff from the integrals == A_ours (§3.3 boxed)", ok1, r1)
        Ap = A_paper(case).subs({tX: T_ * sp.cos(ph), tY: T_ * sp.sin(ph)})
        diff = sp.simplify(A_ours(case) - Ap)
        report("b", f"case {case}: simplify(A_ours - A_paper) == 0 [A_paper = M&M 2020 eq. 22 as typed in "
                    f"crosscheck_tables.py; transcription not yet checked against the PDF]", diff == 0, diff)
    # normal incidence with t1 != t2: strips and corners give t_h
    th_h = 2 * t1 * t2 / (t1 + t2)
    st0 = 4 * (1 / (mu * (1 / t1 + 1 / t2)))
    co0 = 4 * corner_md(1 / t1, 1 / t2, 1 / t1, 1 / t2, 1) / mu ** 2
    ok, res = is_zero(w ** 2 + w * st0 + co0 - (w ** 2 + 2 * w * th_h / mu + 2 * th_h ** 2 / mu ** 2))
    report("b", "theta = 0, t1 != t2: A_eff = w^2 + 2 w t_h/mu + 2 t_h^2/mu^2 (§3.3)", ok, res)
    return F_by_case, A_ours


# =================================================================================================== part c
def part_c(A_ours):
    print("\n=== c. limits and expansions ===")
    paix = w ** 2 + 2 * w * t / mu + 2 * t ** 2 / mu ** 2
    for case in "AB":
        r = sp.simplify(A_ours(case).subs(T_, 0) - paix)
        report("c", f"case {case}: A_eff(theta = 0) = w^2 + 2wt/mu + 2t^2/mu^2 (Paix)", r == 0, r)
    claim = paix - th ** 2 * (w / mu * (t + 1 / t) + (2 * t ** 2 + 3) / mu ** 2)
    third = {}
    for case in "AB":
        expr = A_ours(case).subs(T_, sp.tan(th))
        ser = sp.series(expr, th, 0, 3).removeO()
        ok, res = is_zero(ser - claim)
        report("c", f"case {case}: series of A_eff to theta^2 = §3.7", ok, res)
        ser4 = sp.series(expr, th, 0, 4).removeO()
        third[case] = sp.factor(sp.simplify(ser4.coeff(th, 3)))
    report("c", "theta^3 coefficient (first phi-dependent order), case A", True, 0, f"{third['A']}  (> 0 for phi in [0, pi/4])")
    # widths, symmetric slopes: W_x = w + dL cos(th) (t - tan^2 cos^2(phi)/t)
    dL = sp.Symbol("DeltaL_k", positive=True)
    Wx = w + dL * sp.cos(th) * (t - sp.tan(th) ** 2 * sp.cos(ph) ** 2 / t)
    Wy = w + dL * sp.cos(th) * (t - sp.tan(th) ** 2 * sp.sin(ph) ** 2 / t)
    for nm, expr, cl in (("W_par (phi = 0, t = 1)", Wx.subs({ph: 0, t: 1}), w + dL * (1 - sp.Rational(3, 2) * th ** 2)),
                         ("W_perp (phi = 0, t = 1)", Wy.subs({ph: 0, t: 1}), w + dL * (1 - th ** 2 / 2)),
                         ("W_mean (t = 1)", ((Wx + Wy) / 2).subs(t, 1), w + dL * (1 - th ** 2))):
        ser = sp.series(expr, th, 0, 3).removeO()
        ok, res = is_zero(ser - cl)
        report("c", f"series of {nm} to theta^2 = §3.7", ok, res)
    gen = sp.series(Wx, th, 0, 3).removeO()
    ok, res = is_zero(gen - (w + dL * (t - th ** 2 * (t / 2 + sp.cos(ph) ** 2 / t))))
    report("c", "general t, phi: W_x ~ w + dL (t - theta^2 (t/2 + cos^2 phi / t))", ok, res)
    # numbers quoted in §3.7 (t = 1, mu = 3.63)
    MU, LN2 = 3.63, math.log(2)
    report("c", "§3.7 coefficients 0.551 w + 0.379", abs(2 / MU - 0.551) < 5e-4 and abs(5 / MU ** 2 - 0.379) < 5e-4,
           f"2/mu = {2 / MU:.4f}, 5/mu^2 = {5 / MU ** 2:.4f}")
    errw = 0.0
    for wv in model.WIDTHS.values():
        thv = math.radians(30)
        exact_par = wv + LN2 / MU * math.cos(thv) * (1 - math.tan(thv) ** 2)
        exact_perp = wv + LN2 / MU * math.cos(thv)
        errw = max(errw, abs(exact_par - (wv + LN2 / MU * (1 - 1.5 * thv ** 2))),
                   abs(exact_perp - (wv + LN2 / MU * (1 - 0.5 * thv ** 2))))
    wa = model.WIDTHS["A"]
    report("c", "§3.7 width expansions within 0.002 mm at 30 deg (to the quoted 3 decimals); A: 0.668 vs exact 0.666",
           round(errw, 3) <= 0.002, f"max error {errw:.4f} mm (strictly > 0.002); A: {wa + LN2 / MU * (1 - 1.5 * math.radians(30) ** 2):.4f} vs "
           f"{wa + LN2 / MU * math.cos(math.radians(30)) * (1 - math.tan(math.radians(30)) ** 2):.4f}")
    rel = {}
    for deg in (15, 30):
        thv = math.radians(deg)
        for n, wv in model.WIDTHS.items():
            approx = wv * wv + 2 * wv / MU + 2 / MU ** 2 - thv ** 2 * (2 * wv / MU + 5 / MU ** 2)
            rel[(deg, n)] = {phv: approx / model.area_eff_square(wv, 1.0, 1.0, thv, math.radians(phv), MU) - 1
                             for phv in (0, 15, 30, 45)}
    report("c", "§3.7 area expansion is low at every phi (positive cubic term)",
           all(v <= 0 for d in rel.values() for v in d.values()), "max rel. error "
           f"{max(v for d in rel.values() for v in d.values()):+.2e}")
    quoted = {(15, "A"): 0.3, (15, "D"): 0.0, (30, "A"): 3.2, (30, "D"): 0.3}
    at0 = all(abs(round(-100 * rel[key][0], 1) - val) < 1e-9 for key, val in quoted.items())
    report("c", "§3.7 quoted 'low by 0.0-0.3 % at 15 deg, 0.3 % (D) to 3.2 % (A) at 30 deg' reproduces at phi = 0", at0,
           ", ".join(f"{d} deg {n}: {-100 * rel[(d, n)][0]:.2f} %" for (d, n) in quoted))
    at45 = {key: -100 * rel[key][45] for key in quoted}
    report("c", "same claim at phi = 45 deg (quoted range does not cover it)", all(
        round(at45[key], 1) <= quoted[key] for key in quoted), ", ".join(f"{d} deg {n}: {v:.2f} %" for (d, n), v in at45.items()))
    return rel


# =================================================================================================== part d
def part_d():
    print("\n=== d. widths ===")
    pk = sp.Symbol("p_k", positive=True)
    sol = sp.solve(sp.Eq(sp.exp(-kap * pk * (U + L)), k), pk)
    dLk = -sp.log(k) / mu
    sol0 = sol[0].subs(kap, mu / cth)
    ok, res = is_zero(sp.expand_log(sol0 - dLk * cth / (U + L), force=True))
    report("d", "T = exp(-kappa p (U+L)) = k T_max (T_max = 1 in the opening, part a) => p_k = DeltaL_k cos(theta)/(U+L)",
           ok and len(sol) == 1, res, f"sympy: p_k = {sol[0]}")
    dL = sp.Symbol("DeltaL_k", positive=True)

    def W_general(tau, s1, s2):
        Un, Ln, Uf, Lf = 1 / (s1 - tau), 1 / (s2 + tau), 1 / (s1 + tau), 1 / (s2 - tau)
        return w + dL * cth * (1 / (Un + Ln) + 1 / (Uf + Lf))

    Wx_box = w + dL * sp.cos(th) * (t ** 2 - sp.tan(th) ** 2 * sp.cos(ph) ** 2) / t
    Wy_box = w + dL * sp.cos(th) * (t ** 2 - sp.tan(th) ** 2 * sp.sin(ph) ** 2) / t
    for nm, tau, box in (("W_x", sp.tan(th) * sp.cos(ph), Wx_box), ("W_y", sp.tan(th) * sp.sin(ph), Wy_box)):
        ok, res = is_zero(W_general(tau, t, t).subs(cth, sp.cos(th)) - box)
        report("d", f"{nm}: w + p_k(near) + p_k(far) = §3.2 boxed form (t1 = t2 = t)", ok, res)
    ok, res = is_zero(W_general(0, t1, t2) - (w + dL * cth * 2 * t1 * t2 / (t1 + t2)))
    report("d", "theta = 0, t1 != t2: W = w + DeltaL_k t_h (AM2004 eq. 29 with t -> t_h)", ok, res)
    # diagonal at normal incidence: corner ray p = q, Lambda = p (1/t1 + 1/t2); distance along the diagonal sqrt2 (a + p)
    pkd = sp.solve(sp.Eq(sp.exp(-mu * pk * (1 / t1 + 1 / t2)), k), pk)[0]
    Wd = sp.sqrt(2) * (2 * a + 2 * pkd)
    ok, res = is_zero(sp.expand_log(Wd - sp.sqrt(2) * (2 * a + dLk * 2 * t1 * t2 / (t1 + t2)), force=True))
    report("d", "diagonal, theta = 0: point-profile FWHM = sqrt2 (w + DeltaL_k t_h) = sqrt2 W", ok, res)
    W_mean = sp.simplify((Wx_box + Wy_box) / 2 - (w + dL * sp.cos(th) * (t - sp.tan(th) ** 2 / (2 * t))))
    report("d", "(W_x + W_y)/2 = w + DeltaL_k cos(theta)(t - tan^2/(2t)), phi-independent", W_mean == 0, W_mean)

    # ---- Accorsi & Metzler 2004 (theta_AM from the pinhole plane), transcribed from the PDF:
    # (22) d_re//  ~ d + DeltaL_k (tan^2(alpha/2) - cot^2 theta) cot(alpha/2) sin theta
    # (25) d_re_perp ~ sqrt( (d + DeltaL_k tan(alpha/2) sin theta)^2 - DeltaL_k^2 cos^2 theta )
    # (29) d_re = d + DeltaL_k tan(alpha/2)
    tam = sp.Symbol("theta_AM", positive=True)
    am22 = w + dL * (t ** 2 - sp.cot(tam) ** 2) * (1 / t) * sp.sin(tam)
    am25 = sp.sqrt((w + dL * t * sp.sin(tam)) ** 2 - dL ** 2 * sp.cos(tam) ** 2)
    am29 = w + dL * t
    W_par = Wx_box.subs(ph, 0)
    W_perp = Wy_box.subs(ph, 0)
    sub = {sp.tan(th): sp.cot(tam), sp.cos(th): sp.sin(tam)}  # theta = pi/2 - theta_AM
    ours_terms = sp.Add.make_args(sp.expand(W_par.subs(sub)))
    am_terms = sp.Add.make_args(sp.expand(am22))
    match = sorted(map(str, ours_terms)) == sorted(map(str, am_terms))
    report("d", "W_par with tan(theta) = cot(theta_AM), cos(theta) = sin(theta_AM) == AM2004 eq. 22 (d -> w), term by term",
           match, 0 if match else "terms differ", " + ".join(map(str, ours_terms)))
    full = sp.simplify(W_par.subs(th, sp.pi / 2 - tam) - am22)
    report("d", "same via theta = pi/2 - theta_AM (full substitution)", full == 0, full)
    d25 = sp.simplify(sp.expand(W_perp.subs(th, sp.pi / 2 - tam) ** 2 - am25 ** 2 - dL ** 2 * sp.cos(tam) ** 2))
    report("d", "W_perp^2 - AM25^2 = DeltaL_k^2 cos^2(theta_AM) = DeltaL_k^2 sin^2(theta): the only difference",
           d25 == 0, d25)
    r29 = sp.simplify(W_par.subs(th, 0) - am29)
    report("d", "theta = 0: W = AM2004 eq. 29", r29 == 0, r29)
    # numbers quoted in §2 at 30 deg (t = 1, mu = 3.63)
    MU, LN2 = 3.63, math.log(2)
    dl_ = LN2 / MU
    thv = math.radians(30)
    vals = {n: (wv + dl_ * math.cos(thv) * (1 - math.tan(thv) ** 2), wv + dl_ * math.cos(thv),
                model.d_re_perpendicular(wv, 1.0, thv, MU), math.sqrt(2) * (wv + dl_)) for n, wv in model.WIDTHS.items()}
    quoted = {"A": (0.666, 0.721, 0.715, 1.056), "B": (0.907, 0.962, 0.958, 1.397), "C": (1.325, 1.380, 1.377, 1.988),
              "D": (2.117, 2.172, 2.170, 3.108)}
    worst = max(abs(vals[n][i] - quoted[n][i]) for n in quoted for i in range(4))
    diffs = {deg: {n: wv + dl_ * math.cos(math.radians(deg)) - model.d_re_perpendicular(wv, 1.0, math.radians(deg), MU)
                   for n, wv in model.WIDTHS.items()} for deg in (30, 35)}
    report("d", "§2 numbers at 30 deg: W_par, W_perp, AM25, sqrt2 W (A-D), to 3 decimals", worst <= 0.0005 + 1e-12,
           f"max |computed - quoted| = {worst:.5f}")
    report("d", "claim 'W_perp - AM25 <= 0.003 mm here' (§2 table, §3.6)", max(diffs[30].values()) <= 0.003,
           "; ".join(f"{deg} deg: " + ", ".join(f"{n} {v:.4f}" for n, v in d.items()) + " mm" for deg, d in diffs.items()))
    return diffs


# =================================================================================================== part e
mpm.mp.dps = 25


def raw_walls(x0, y0, a_, s1, s2, tax, tay):
    """z-intervals of the ray in the 4 walls, straight from the 8 half-planes (no zone-I assumption)."""
    out = []
    for u0, tau, sg in ((x0, tax, 1), (x0, tax, -1), (y0, tay, 1), (y0, tay, -1)):
        lo, hi = -mpm.inf, mpm.inf
        c0 = sg * u0 - a_
        for c1 in (sg * tau - s1, sg * tau + s2):
            if c1 > 0:
                lo = max(lo, -c0 / c1)
            elif c1 < 0:
                hi = min(hi, -c0 / c1)
            elif c0 < 0:
                lo, hi = mpm.inf, -mpm.inf
        out.append((lo, hi))
    return out


def raw_T(x0, y0, P):
    ivs = sorted(iv for iv in raw_walls(x0, y0, P["a"], P["t1"], P["t2"], P["tx"], P["ty"]) if iv[1] > iv[0])
    tot, cur = mpm.mpf(0), None
    for lo, hi in ivs:  # length of the union
        if cur is None or lo > cur[1]:
            if cur is not None:
                tot += cur[1] - cur[0]
            cur = [lo, hi]
        else:
            cur[1] = max(cur[1], hi)
    if cur is not None:
        tot += cur[1] - cur[0]
    if tot == mpm.inf:
        return mpm.mpf(0)
    return mpm.exp(-P["mu"] * tot * P["sec"])


def kinks_y(x0, P):
    """y0 where the union's endpoints switch wall (endpoints are linear in y0: two raw evaluations locate them)."""
    a_ = P["a"]
    w4 = raw_walls(x0, 0, a_, P["t1"], P["t2"], P["tx"], P["ty"])
    xw = [iv for iv in w4[:2] if iv[1] > iv[0]]
    pts = []
    if not xw:
        return pts
    xlo, xhi = xw[0]
    for sg, idx_wall in ((1, 2), (-1, 3)):
        y1, y2 = sg * (a_ + 1), sg * (a_ + 2)
        e1 = raw_walls(x0, y1, a_, P["t1"], P["t2"], P["tx"], P["ty"])[idx_wall]
        e2 = raw_walls(x0, y2, a_, P["t1"], P["t2"], P["tx"], P["ty"])[idx_wall]
        for j, ref in ((0, xlo), (1, xhi)):
            f1, f2 = e1[j] - ref, e2[j] - ref
            if f2 != f1:
                yk = y1 - f1 * (y2 - y1) / (f2 - f1)
                if sg * (yk - sg * a_) > 0:
                    pts.append(yk)
    return pts


def area_quad(P):
    a_ = P["a"]

    def inner(x0):
        pts = sorted(set([-a_, a_] + kinks_y(x0, P)))
        return mpm.quad(lambda y0: raw_T(x0, y0, P), [-mpm.inf] + pts + [mpm.inf])

    return mpm.quad(inner, [-mpm.inf, -a_, a_, mpm.inf])


def halfmax_width(P, k_=mpm.mpf("0.5"), direction=(1, 0)):
    """Full width at k * T_max along a line through the centre (direction (1,0), (0,1), (1,1), (1,-1)); the
    distance is measured along the line."""
    dx, dy = direction
    tmax = raw_T(0, 0, P)
    big = P["a"] + 60 / P["mu"]

    def f(sv):
        return raw_T(sv * dx, sv * dy, P) - k_ * tmax

    sp_ = mpm.findroot(f, (P["a"], big), solver="anderson")
    sm_ = mpm.findroot(f, (-big, -P["a"]), solver="anderson")
    return (sp_ - sm_) * mpm.sqrt(dx * dx + dy * dy)


def closed_area(wv, s1, s2, thv, phv, muv):
    """General-slope closed form: w^2 + strips + corners with the §3.3 corner formula (case chosen explicitly)."""
    kv = muv / mpm.cos(thv)
    tax, tay = mpm.tan(thv) * mpm.cos(phv), mpm.tan(thv) * mpm.sin(phv)
    ex = ((1 / (s1 - tax), 1 / (s2 + tax)), (1 / (s1 + tax), 1 / (s2 - tax)))
    ey = ((1 / (s1 - tay), 1 / (s2 + tay)), (1 / (s1 + tay), 1 / (s2 - tay)))
    strips = sum(wv / (kv * (u + l)) for (u, l) in ex + ey)
    corners = 0
    for ux, lx in ex:
        for uy, ly in ey:
            cs = 1 if ux / uy <= lx / ly else 2
            sa, sb, al, be = (ux / uy, lx / ly, lx, uy) if cs == 1 else (lx / ly, ux / uy, ux, ly)
            corners += (sa / (ux + lx) ** 2 + 1 / (be * (al + be * sa)) - 1 / (be * (al + be * sb))
                        + 1 / (sb * (uy + ly) ** 2)) / kv ** 2
    return wv * wv + strips + corners


def boxed_area(wv, tv, thv, phv, muv):
    """§3.3 boxed form (t1 = t2 = t)."""
    muv = mpm.mpf(muv)  # a float mu would make mu**2 a float64 product
    c = mpm.cos(thv)
    ax, ay = abs(mpm.tan(thv) * mpm.cos(phv)), abs(mpm.tan(thv) * mpm.sin(phv))
    M, m = max(ax, ay) / tv, min(ax, ay) / tv
    return (wv * wv + wv * c / (muv * tv) * (2 * tv * tv - mpm.tan(thv) ** 2)
            + tv * tv * c * c / muv ** 2 * (1 - M) * (3 * (1 - m * m) - (1 - M) ** 2))


def widths_general(wv, s1, s2, thv, phv, muv, k_=mpm.mpf("0.5")):
    dl_ = -mpm.log(k_) / muv
    out = []
    for tau in (mpm.tan(thv) * mpm.cos(phv), mpm.tan(thv) * mpm.sin(phv)):
        un, ln, uf, lf = 1 / (s1 - tau), 1 / (s2 + tau), 1 / (s1 + tau), 1 / (s2 - tau)
        out.append(wv + dl_ * mpm.cos(thv) * (1 / (un + ln) + 1 / (uf + lf)))
    return out


def widths_boxed(wv, tv, thv, phv, muv, k_=mpm.mpf("0.5")):
    dl_ = -mpm.log(k_) / muv
    c, tt = mpm.cos(thv), mpm.tan(thv) ** 2
    return [wv + dl_ * c * (tv - tt * mpm.cos(phv) ** 2 / tv), wv + dl_ * c * (tv - tt * mpm.sin(phv) ** 2 / tv)]


def diag_widths(wv, s1, s2, thv, phv, muv, k_=mpm.mpf("0.5")):
    """Point-profile FWHM along the diagonals from Lambda = p [max(Ux,Uy) + max(Lx,Ly)] (§3.2): diag+ runs
    through the (+,+) and (-,-) corners, diag- through (+,-) and (-,+)."""
    dl_ = -mpm.log(k_) / muv
    tax, tay = mpm.tan(thv) * mpm.cos(phv), mpm.tan(thv) * mpm.sin(phv)
    E = {"x+": (1 / (s1 - tax), 1 / (s2 + tax)), "x-": (1 / (s1 + tax), 1 / (s2 - tax)),
         "y+": (1 / (s1 - tay), 1 / (s2 + tay)), "y-": (1 / (s1 + tay), 1 / (s2 - tay))}

    def pk(cx, cy):
        (ux, lx), (uy, ly) = E["x" + cx], E["y" + cy]
        return dl_ * mpm.cos(thv) / (max(ux, uy) + max(lx, ly))

    return {"diag+": mpm.sqrt(2) * (wv + pk("+", "+") + pk("-", "-")),
            "diag-": mpm.sqrt(2) * (wv + pk("+", "-") + pk("-", "+"))}


def make_points(rng, n, symmetric):
    pts = []
    while len(pts) < n:
        wv = rng.uniform(0.2, 3.0)
        if symmetric:
            s1 = s2 = rng.uniform(0.4, 2.0)
        else:
            s1, s2 = rng.uniform(0.4, 2.0), rng.uniform(0.4, 2.0)
        phv = rng.uniform(0, 2 * math.pi)
        lim = min(s1, s2) / max(abs(math.cos(phv)), abs(math.sin(phv)))
        thv = math.atan(rng.uniform(0, 0.97) * lim)
        pts.append((wv, s1, s2, thv, phv))
    return pts


MU_E = 3.63


def eval_point(item):
    """One random point: closed forms, mpmath.quad of the raw transmission, numeric half-maximum widths."""
    kind, (wv, s1, s2, thv, phv) = item
    mpm.mp.dps = 25
    wv, s1, s2, thv, phv = map(mpm.mpf, (wv, s1, s2, thv, phv))
    P = {"a": wv / 2, "t1": s1, "t2": s2, "tx": mpm.tan(thv) * mpm.cos(phv), "ty": mpm.tan(thv) * mpm.sin(phv),
         "mu": mpm.mpf(MU_E), "sec": 1 / mpm.cos(thv)}
    Aq = area_quad(P)
    Wq = [halfmax_width(P, direction=(1, 0)), halfmax_width(P, direction=(0, 1))]
    Dq = {"diag+": halfmax_width(P, direction=(1, 1)), "diag-": halfmax_width(P, direction=(1, -1))}
    if kind == "sym":
        Ac, Wc = boxed_area(wv, s1, thv, phv, MU_E), widths_boxed(wv, s1, thv, phv, MU_E)
    else:
        Ac, Wc = closed_area(wv, s1, s2, thv, phv, MU_E), widths_general(wv, s1, s2, thv, phv, MU_E)
    Dc = diag_widths(wv, s1, s2, thv, phv, MU_E)
    return kind, (wv, s1, s2, thv, phv), Ac, Aq, Wc, Wq, Dc, Dq


def part_e():
    print("\n=== e. numerics: mpmath.quad of the raw transmission, half-maximum search, model, ray trace ===")
    rng = random.Random(20261030)
    MU = MU_E
    sym = make_points(rng, 16, True)
    # special points: normal incidence, phi = 0, phi = 45 deg exactly (M = m), close to the zone-I border
    sym += [(0.556, 1.0, 1.0, 0.0, 0.0), (1.215, 1.0, 1.0, math.radians(30), 0.0),
            (0.797, 1.0, 1.0, math.radians(30), math.pi / 4), (2.0, 0.8, 0.8, math.atan(0.99 * 0.8), 0.0)]
    gen = make_points(rng, 10, False)
    TOL = 1e-10
    rows = []
    worst = {"area_sym": 0, "width_sym": 0, "diag_sym": 0, "area_gen": 0, "width_gen": 0, "diag_gen": 0,
             "model_area": 0, "model_width": 0}
    t0 = time.time()
    items = [("sym", pt) for pt in sym] + [("gen", pt) for pt in gen]
    nproc = max(1, int(os.environ.get("OMP_NUM_THREADS", "1")))
    with multiprocessing.Pool(nproc) as pool:
        for kind, (wv, s1, s2, thv, phv), Ac, Aq, Wc, Wq, Dc, Dq in pool.imap(eval_point, items):
            ra = abs(Ac / Aq - 1)
            rw = max(abs(Wc[i] / Wq[i] - 1) for i in range(2))
            rd = max(abs(Dc[kk] / Dq[kk] - 1) for kk in Dc)
            worst["area_" + kind] = max(worst["area_" + kind], ra)
            worst["width_" + kind] = max(worst["width_" + kind], rw)
            worst["diag_" + kind] = max(worst["diag_" + kind], rd)
            # numeric reference functions of square_pinhole_model.py (float64)
            fl = [float(v) for v in (wv, s1, s2, thv, phv)]
            Am = model.area_eff_square(fl[0], fl[1], fl[2], fl[3], fl[4], MU)
            Wm = model.fwhm_sides_square(fl[0], fl[1], fl[2], fl[3], fl[4], MU)
            worst["model_area"] = max(worst["model_area"], abs(Am / float(Ac) - 1))
            worst["model_width"] = max(worst["model_width"], max(abs(Wm[i] / float(Wc[i]) - 1) for i in range(2)))
            rows.append({"kind": kind, "w": fl[0], "t1": fl[1], "t2": fl[2], "theta_deg": math.degrees(fl[3]),
                         "phi_deg": math.degrees(fl[4]), "A_closed": float(Ac), "A_quad": float(Aq), "rel_A": float(ra),
                         "rel_W": float(rw), "rel_diag": float(rd)})
            print(f"  {kind} w={fl[0]:.3f} t1={fl[1]:.3f} t2={fl[2]:.3f} th={math.degrees(fl[3]):5.1f} "
                  f"ph={math.degrees(fl[4]):6.1f}  A={float(Ac):.10f} rel(A)={float(ra):.1e} rel(W)={float(rw):.1e} "
                  f"rel(diag)={float(rd):.1e}  [{time.time() - t0:.0f} s]", flush=True)
    report("e", f"area, boxed form vs mpmath.quad of raw T, {len(sym)} points t1 = t2 (tol {TOL:g})",
           worst["area_sym"] < TOL, f"{float(worst['area_sym']):.2e}")
    report("e", f"W_x, W_y boxed vs numeric half-maximum, {len(sym)} points", worst["width_sym"] < TOL,
           f"{float(worst['width_sym']):.2e}")
    report("e", "diagonal FWHM from Lambda = p[max U + max L] vs numeric half-maximum, t1 = t2",
           worst["diag_sym"] < TOL, f"{float(worst['diag_sym']):.2e}")
    report("e", f"area, general-slope case formulas vs mpmath.quad, {len(gen)} points t1 != t2",
           worst["area_gen"] < TOL, f"{float(worst['area_gen']):.2e}")
    report("e", f"W_x, W_y general (§3.2 bracket) vs half-maximum, {len(gen)} points t1 != t2",
           worst["width_gen"] < TOL, f"{float(worst['width_gen']):.2e}")
    report("e", "diagonals vs half-maximum, t1 != t2", worst["diag_gen"] < TOL, f"{float(worst['diag_gen']):.2e}")
    report("e", "square_pinhole_model.area_eff_square / fwhm_sides_square (float64) vs closed forms",
           max(worst["model_area"], worst["model_width"]) < 1e-12,
           f"area {worst['model_area']:.1e}, widths {worst['model_width']:.1e}")

    # ---- ray trace (exact CSG, finite b, real slopes t1 != t2, 4 um grid)
    tr = json.loads((HERE / "raytrace_results.json").read_text())
    dev = {"A_model_json": 0, "W_model_json": 0, "A_trace": 0, "W_trace": 0, "diag_trace": 0}
    trows = []
    for r in tr:
        s1, s2 = model.slopes(r["variant"])
        thv, phv = math.radians(r["theta_deg"]), math.radians(r["phi_deg"])
        Ac = float(closed_area(r["w"], s1, s2, thv, phv, model.MU_W))
        Wc = [float(v) for v in widths_general(r["w"], s1, s2, thv, phv, model.MU_W)]
        Dc = {kk: float(v) for kk, v in diag_widths(r["w"], s1, s2, thv, phv, model.MU_W).items()}
        fw = r["fwhm_aperture_plane"]
        dev["A_model_json"] = max(dev["A_model_json"], abs(r["A_eff_model"] / Ac - 1))
        dev["W_model_json"] = max(dev["W_model_json"], abs(r["model_fwhm_sides"]["x"] / Wc[0] - 1),
                                  abs(r["model_fwhm_sides"]["y"] / Wc[1] - 1))
        ra, rw = r["A_eff_trace"] / Ac - 1, max(abs(fw["x"] / Wc[0] - 1), abs(fw["y"] / Wc[1] - 1))
        rd = max(abs(fw[kk] / Dc[kk] - 1) for kk in Dc)
        dev["A_trace"] = max(dev["A_trace"], abs(ra))
        dev["W_trace"] = max(dev["W_trace"], rw)
        dev["diag_trace"] = max(dev["diag_trace"], rd)
        trows.append({"variant": r["variant"], "b": r["b"], "theta": r["theta_deg"], "phi": r["phi_deg"],
                      "A_closed": Ac, "A_trace": r["A_eff_trace"], "rel_A": ra, "W_closed": Wc,
                      "W_trace": [fw["x"], fw["y"]], "rel_W": rw, "diag_closed": Dc,
                      "diag_trace": {"diag+": fw["diag+"], "diag-": fw["diag-"]}, "rel_diag": rd})
    report("e", "raytrace_results.json model fields == closed forms (general t1, t2)",
           max(dev["A_model_json"], dev["W_model_json"]) < 1e-12,
           f"area {dev['A_model_json']:.1e}, widths {dev['W_model_json']:.1e}")
    report("e", f"exact CSG trace vs closed forms, {len(tr)} cases: A_eff (tol 1e-3, trace grid/finite b)",
           dev["A_trace"] < 1e-3, f"{dev['A_trace']:.1e}")
    report("e", "exact CSG trace vs closed forms: side FWHMs (tol 5e-4)", dev["W_trace"] < 5e-4, f"{dev['W_trace']:.1e}")
    # the trace's own noise on the diagonals: at theta = 0 diag+ and diag- must be equal by symmetry
    asym = max(abs(r["fwhm_aperture_plane"]["diag+"] / r["fwhm_aperture_plane"]["diag-"] - 1)
               for r in tr if r["theta_deg"] == 0)
    dev["diag_trace_self_asymmetry_theta0"] = asym
    report("e", f"exact CSG trace vs closed forms: both diagonals incl. oblique (tol 1.5 x the trace's own "
                f"diag+/diag- asymmetry at theta = 0 = {1.5 * asym:.1e})", dev["diag_trace"] < 1.5 * asym,
           f"{dev['diag_trace']:.1e}")
    return rows, trows, worst, dev


# =================================================================================================== main
if __name__ == "__main__":
    t_start = time.time()
    part_a()
    _, A_ours_fn = part_b()
    rel37 = part_c(A_ours_fn)
    am25_diffs = part_d()
    rows, trows, worst, dev = part_e()
    n_fail = sum(not r["pass"] for r in RESULTS)
    print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed, {n_fail} failed  ({time.time() - t_start:.0f} s)")
    (HERE / "sympy_check_results.json").write_text(json.dumps(
        {"checks": RESULTS, "random_points": rows, "raytrace": trows,
         "worst_rel": {kk: float(v) for kk, v in worst.items()}, "raytrace_worst_rel": dev,
         "s37_area_expansion_rel_err_by_phi": {f"{d}deg_{n}": v for (d, n), v in rel37.items()},
         "W_perp_minus_AM25_mm": am25_diffs,
         "versions": {"sympy": sp.__version__, "mpmath": mpm.__version__, "numpy": np.__version__}},
        indent=1, default=float) + "\n")
    sys.exit(1 if n_fail else 0)
