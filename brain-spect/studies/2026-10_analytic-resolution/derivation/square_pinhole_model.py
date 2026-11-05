"""Analytic model of a SQUARE knife-edge (pyramidal, double-sided) pinhole with penetration, and the
classic ROUND-pinhole formulas for comparison.  CPU / numpy only.

Geometry (knife-edge coordinates): square opening of side w = 2a at z = 0; the opening half-width grows
as a + z t1 on the object side (z > 0) and a + |z| t2 on the detector side (z < 0); t = tan(alpha/2).
A ray from a distant source at polar angle theta from the module axis and azimuth phi (in-plane direction
of the tilt, phi = 0 along +x, the source on the +x/+y side) has in-plane slopes
    tau_x = tan(theta) cos(phi),  tau_y = tan(theta) sin(phi)      (dx/dz along the ray).
Parallel-beam approximation (rho/b -> 0, Accorsi & Metzler 2004 Sec. II; verified by raytrace_pyramid.py).

A ray crossing the knife-edge plane at (x0, y0) with p = |x0| - a > 0 is inside the x-wedge for
z in [-p L, +p U], with   near edge (towards the source): U = 1/(t1 - tau_x), L = 1/(t2 + tau_x)
                         far edge:                       U = 1/(t1 + tau_x), L = 1/(t2 - tau_x)
(likewise for y).  The material is the UNION of the two wedges, so the z-extent of material along the ray
is  Lambda = max(p_x U_x, p_y U_y) + max(p_x L_x, p_y L_y)  and the path length is Lambda / cos(theta).

Conventions: theta is measured from the pinhole AXIS (our convention); Accorsi-Metzler measure theta_AM
from the pinhole PLANE, theta_AM = pi/2 - theta, so sin(theta_AM) = cos(theta), cot(theta_AM) = tan(theta).
"""

import numpy as np

LN2 = np.log(2.0)


# ----------------------------------------------------------------------------------------------- square
def edge_coeffs(t1, t2, tau):
    """(U, L) of the near edge and of the far edge for in-plane slope tau >= 0 (zone I: tau < min(t1, t2))."""
    if tau >= min(t1, t2):
        raise ValueError("outside zone I (grazing): tau = %.3f >= min(t1, t2)" % tau)
    return (1.0 / (t1 - tau), 1.0 / (t2 + tau)), (1.0 / (t1 + tau), 1.0 / (t2 - tau))


def path_length_square(x0, y0, w, t1, t2, theta, phi):
    """Path length through tungsten (mm) of the parallel-beam ray crossing the knife-edge plane at (x0, y0)."""
    a = 0.5 * w
    tau_x, tau_y = np.tan(theta) * np.cos(phi), np.tan(theta) * np.sin(phi)
    (Uxn, Lxn), (Uxf, Lxf) = edge_coeffs(t1, t2, tau_x)
    (Uyn, Lyn), (Uyf, Lyf) = edge_coeffs(t1, t2, tau_y)
    px, py = np.maximum(np.abs(x0) - a, 0.0), np.maximum(np.abs(y0) - a, 0.0)
    Ux, Lx = np.where(x0 > 0, Uxn, Uxf), np.where(x0 > 0, Lxn, Lxf)
    Uy, Ly = np.where(y0 > 0, Uyn, Uyf), np.where(y0 > 0, Lyn, Lyf)
    lam = np.maximum(px * Ux, py * Uy) + np.maximum(px * Lx, py * Ly)
    return lam / np.cos(theta)


def transmission_square(x0, y0, w, t1, t2, theta, phi, mu):
    return np.exp(-mu * path_length_square(x0, y0, w, t1, t2, theta, phi))


def fwhm_sides_square(w, t1, t2, theta, phi, mu, k=0.5):
    """Full width at fraction k of the maximum, in the knife-edge plane, along x and along y.
    Each edge adds dL_k cos(theta) / (U + L):  W = w + dL_k cos(theta) [1/(U_near+L_near) + 1/(U_far+L_far)]."""
    dLk = -np.log(k) / mu
    out = []
    for tau in (np.tan(theta) * np.cos(phi), np.tan(theta) * np.sin(phi)):
        (Un, Ln), (Uf, Lf) = edge_coeffs(t1, t2, tau)
        out.append(w + dLk * np.cos(theta) * (1.0 / (Un + Ln) + 1.0 / (Uf + Lf)))
    return tuple(out)


def fwhm_sides_square_symmetric(w, t, theta, phi, mu, k=0.5):
    """Same with t1 = t2 = t (closed form):  W_x = w + dL_k cos(theta) (t - tan^2(theta) cos^2(phi) / t)."""
    dLk = -np.log(k) / mu
    tt = np.tan(theta) ** 2
    return (w + dLk * np.cos(theta) * (t - tt * np.cos(phi) ** 2 / t),
            w + dLk * np.cos(theta) * (t - tt * np.sin(phi) ** 2 / t))


def _corner_integral(Ux, Lx, Uy, Ly, kappa):
    """I = int_0^inf int_0^inf exp(-kappa [max(p Ux, q Uy) + max(p Lx, q Ly)]) dp dq  (closed form).
    With q = p s:  I = int_0^inf ds / (kappa Lambda(1, s))^2,  Lambda(1, s) piecewise linear in s."""
    sU, sL = Ux / Uy, Lx / Ly
    sa, sb = min(sU, sL), max(sU, sL)
    if sU <= sL:
        alpha, beta = Lx, Uy  # for sa < s < sb: max(Ux, sUy) = sUy, max(Lx, sLy) = Lx
    else:
        alpha, beta = Ux, Ly
    val = sa / (Ux + Lx) ** 2
    val += 1.0 / (beta * (alpha + beta * sa)) - 1.0 / (beta * (alpha + beta * sb))
    val += 1.0 / (sb * (Uy + Ly) ** 2)
    return val / kappa ** 2


def area_eff_square(w, t1, t2, theta, phi, mu):
    """Penetration-aware effective area (mm^2) of the square pinhole in the knife-edge plane,
    A_eff = w^2 + sum_edges w/(kappa (U+L)) + sum_corners I_corner,  kappa = mu / cos(theta).
    The sensitivity is g = A_eff cos(theta) / (4 pi r^2) = A_eff cos^3(theta) / (4 pi b^2)."""
    kappa = mu / np.cos(theta)
    tau_x, tau_y = np.tan(theta) * np.cos(phi), np.tan(theta) * np.sin(phi)
    ex = edge_coeffs(t1, t2, tau_x)  # ((Un, Ln), (Uf, Lf))
    ey = edge_coeffs(t1, t2, tau_y)
    strips = sum(w / (kappa * (U + L)) for (U, L) in ex) + sum(w / (kappa * (U + L)) for (U, L) in ey)
    corners = sum(_corner_integral(Ux, Lx, Uy, Ly, kappa) for (Ux, Lx) in ex for (Uy, Ly) in ey)
    return w * w + strips + corners


def area_eff_square_numeric(w, t1, t2, theta, phi, mu, step=0.002, margin=3.0):
    """Brute-force 2-D integral of the model transmission over the knife-edge plane (check of the closed form)."""
    h = 0.5 * w + margin
    x = np.arange(-h, h + step / 2, step)
    X, Y = np.meshgrid(x, x, indexing="ij")
    T = transmission_square(X, Y, w, t1, t2, theta, phi, mu)
    return T.sum() * step * step


def paix_form(w, t, mu):
    """sqrt(w^2 + 2 w t/mu + 2 t^2/mu^2): for the square at normal incidence this is exactly sqrt(A_eff)."""
    return np.sqrt(w * w + 2 * w * t / mu + 2 * t * t / mu ** 2)


def anger_form(w, t, mu):
    return np.sqrt(w * w + 2 * w * t / mu)


def rms_square_normal(w, t, mu):
    """RMS width (one axis) of the square-pinhole PSF in the knife-edge plane at normal incidence, with
    penetration T = exp(-c (max(|x|,|y|) - a)_+), c = 2 mu / t:
        <x^2> = [w^4/12 + 2w^3/(3c) + 4w^2/c^2 + 16w/c^3 + 32/c^4] / [w^2 + 4w/c + 8/c^2]."""
    c = 2 * mu / t
    num = w ** 4 / 12 + 2 * w ** 3 / (3 * c) + 4 * w ** 2 / c ** 2 + 16 * w / c ** 3 + 32 / c ** 4
    den = w * w + 4 * w / c + 8 / c ** 2
    return np.sqrt(num / den)


def rms_round_normal(d, t, mu):
    """RMS width (one axis) of the round-pinhole PSF at normal incidence, T = exp(-c (rho - R)_+), R = d/2:
        <x^2> = <rho^2>/2 = [R^4/4 + R^3/c + 3R^2/c^2 + 6R/c^3 + 6/c^4] / [R^2 + 2R/c + 2/c^2]."""
    c = 2 * mu / t
    R = 0.5 * d
    num = R ** 4 / 4 + R ** 3 / c + 3 * R ** 2 / c ** 2 + 6 * R / c ** 3 + 6 / c ** 4
    den = R * R + 2 * R / c + 2 / c ** 2
    return np.sqrt(num / den)


def moments_square_numeric(w, t1, t2, theta, phi, mu, step=0.002, margin=3.0):
    """Numeric RMS widths (x, y) and the FWHM along x, y and the two diagonals of the model transmission."""
    h = 0.5 * w + margin
    x = np.arange(-h, h + step / 2, step)
    X, Y = np.meshgrid(x, x, indexing="ij")
    T = transmission_square(X, Y, w, t1, t2, theta, phi, mu)
    s = T.sum()
    mx, my = (T * X).sum() / s, (T * Y).sum() / s
    rx, ry = np.sqrt((T * (X - mx) ** 2).sum() / s), np.sqrt((T * (Y - my) ** 2).sum() / s)
    c = len(x) // 2
    prof = {"x": T[:, c], "y": T[c, :], "diag+": np.diagonal(T), "diag-": np.diagonal(np.fliplr(T))}
    fw = {}
    for key, p in prof.items():
        scale = step * (np.sqrt(2.0) if key.startswith("diag") else 1.0)
        fw[key] = full_width(p, 0.5) * scale
    return (rx, ry), fw


def full_width(profile, level):
    """Full width (in samples) of a profile at `level` x max, linear interpolation at the crossings."""
    p = np.asarray(profile, float)
    thr = level * p.max()
    above = np.where(p >= thr)[0]
    i0, i1 = above[0], above[-1]
    left = i0 if i0 == 0 else i0 - (thr - p[i0]) / (p[i0 - 1] - p[i0])  # crossing between i0-1 and i0
    right = i1 if i1 == len(p) - 1 else i1 + (p[i1] - thr) / (p[i1] - p[i1 + 1])
    return right - left


# ----------------------------------------------------------------------------------------------- round
def d_e_paix(d, t, mu):
    """Accorsi & Metzler 2004 eq. (5) (Paix 1967)."""
    return np.sqrt(d * (d + 2 * t / mu) + 2 * t * t / mu ** 2)


def d_e_anger(d, t, mu):
    """Accorsi & Metzler 2004 eq. (3) (Anger 1967)."""
    return np.sqrt(d * (d + 2 * t / mu))


def d_re_normal(d, t, mu, k=0.5):
    """Accorsi & Metzler 2004 eq. (29): normal incidence, exact for a parallel beam."""
    return d + (-np.log(k) / mu) * t


def d_re_parallel(d, t, theta, mu, k=0.5):
    """Accorsi & Metzler 2004 eq. (22), theta from the AXIS (their sin(theta_AM) = cos(theta), cot = tan)."""
    dLk = -np.log(k) / mu
    return d + dLk * (t * t - np.tan(theta) ** 2) / t * np.cos(theta)


def d_re_perpendicular(d, t, theta, mu, k=0.5):
    """Accorsi & Metzler 2004 eq. (25)."""
    dLk = -np.log(k) / mu
    return np.sqrt((d + dLk * t * np.cos(theta)) ** 2 - dLk ** 2 * np.sin(theta) ** 2)


def area_eff_round_metzler2001(d, t, theta, mu):
    """Effective area (mm^2) of a round knife-edge pinhole at incidence theta (from the axis), from the
    angle-dependent sensitivity of Metzler et al. 2001 as quoted in Metzler & Accorsi 2005 eq. (A.1):
    g = d^2 sin^3 th/(16 h^2) + sin^5 th tan^2(a/2)/(8 h^2 mu^2) (1 - cot^2 th/tan^2(a/2))^(1/2)
        [1 - cot^2 th/tan^2(a/2) + mu d csc th cot(a/2)],  th = theta_AM.  Divide by sin^3 th/(4 pi h^2)."""
    s, cot = np.cos(theta), np.tan(theta)  # sin(theta_AM), cot(theta_AM)
    q = 1 - cot ** 2 / t ** 2
    pen = s * s * t * t / (8 * mu ** 2) * np.sqrt(q) * (q + mu * d / s / t) * 4 * np.pi
    return np.pi * d * d / 4 + pen


# ----------------------------------------------------------------------------------------------- tables
WIDTHS = {"A": 0.556, "B": 0.797, "C": 1.215, "D": 2.007}
L_TOP = {"A": 10.74, "B": 11.00, "C": 11.46, "D": 12.33}
H_NOZZLE = {"A": 5.04, "B": 5.02, "C": 5.00, "D": 4.96}
H_BODY, L_BOTTOM_INNER = 25.0, 50.0
MU_W, F_MM, B_CENTRE = 3.63, 27.0, 149.6


def slopes(name):
    """(t1, t2): object-side and detector-side tan(alpha/2) of the pyramidal nozzle of variant `name`."""
    w = WIDTHS[name]
    return (L_TOP[name] - w) / (2 * H_NOZZLE[name]), (L_BOTTOM_INNER - w) / (2 * H_BODY)


if __name__ == "__main__":
    np.set_printoptions(precision=4)
    print("variant  w      t1      t2      t_eff=2/(1/t1+1/t2)")
    for n in WIDTHS:
        t1, t2 = slopes(n)
        print(f"{n}  {WIDTHS[n]:.3f}  {t1:.4f}  {t2:.4f}  {2 / (1 / t1 + 1 / t2):.4f}")

    print("\nclosed-form vs numeric effective area (mm^2), and FWHM sides, theta = 0/15/30 deg, phi = 0/45 deg")
    for n in WIDTHS:
        w = WIDTHS[n]
        t1, t2 = slopes(n)
        for th in (0, 15, 30):
            for ph in (0, 45):
                theta, phi = np.radians(th), np.radians(ph)
                A = area_eff_square(w, t1, t2, theta, phi, MU_W)
                An = area_eff_square_numeric(w, t1, t2, theta, phi, MU_W)
                Wx, Wy = fwhm_sides_square(w, t1, t2, theta, phi, MU_W)
                (rx, ry), fw = moments_square_numeric(w, t1, t2, theta, phi, MU_W)
                print(f"{n} th={th:2d} ph={ph:2d}  A_eff={A:.5f} num={An:.5f}  Wx={Wx:.4f} Wy={Wy:.4f} "
                      f"num x={fw['x']:.4f} y={fw['y']:.4f} diag={fw['diag+']:.4f}/{fw['diag-']:.4f}  rms x={rx:.4f} y={ry:.4f}")
        print(f"   normal-incidence closed forms: Paix form {paix_form(w, 1.0, MU_W):.4f}  rms {rms_square_normal(w, 1.0, MU_W):.4f}")
