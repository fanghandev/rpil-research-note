"""Exact ray integration of the attenuated transmission through the brain-SPECT collimator CSG
(frustum A minus frusta B and C, plus the hollow box; the same G4Trd parameters as
qmirt-gate-10-sim/payload/python/gate_sim_brain_spect_boolean.py), for a point source at finite distance.
Gives the transmission map on the detection plane (z = -f), its FWHM along x, y and the diagonals, its RMS
widths, and the sensitivity; compares them with square_pinhole_model.py.  CPU / numpy only.

    micromamba run -n opengate python raytrace_pyramid.py          (writes raytrace_results.json)

Coordinates: knife-edge plane z = 0, +z towards the object, x/y along the sides of the square.
Source at S = b (tan(theta) cos(phi), tan(theta) sin(phi), 1).
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import square_pinhole_model as m  # noqa: E402

OUT = Path(__file__).resolve().parent
L_BOTTOM_OUTER, H_BOX, W_WALL, DELTA_Z = 56.064, 23.5, 2.03, 0.1


class Trd:
    """G4Trd: half-widths dx1 (at z = zc - dz) -> dx2 (at z = zc + dz); square cross-section (dy = dx)."""

    def __init__(self, dx1, dx2, dz, zc):
        self.dx1, self.dx2, self.dz, self.zc = dx1, dx2, dz, zc
        self.s = (dx2 - dx1) / (2 * dz)  # d(half-width)/dz
        self.c = dx1 - self.s * (zc - dz)  # half-width(z) = c + s z

    def interval(self, P, D):
        """Segment P + lam D, lam in [0, 1] (source to detection point): (lam0, lam1) of the intersection,
        empty when lam0 > lam1. P (3,), D (..., 3). Clipping to [0, 1] matters: the infinite line would
        continue past the detection plane into the hollow-box side walls (|x| > 26 mm at z < -45 mm)."""
        lo = np.zeros(D.shape[:-1])
        hi = np.ones(D.shape[:-1])
        # half-spaces n.X <= c:  z <= zc+dz ; -z <= -(zc-dz) ; +-x - s z <= c ; +-y - s z <= c
        planes = [((0, 0, 1), self.zc + self.dz), ((0, 0, -1), -(self.zc - self.dz)),
                  ((1, 0, -self.s), self.c), ((-1, 0, -self.s), self.c),
                  ((0, 1, -self.s), self.c), ((0, -1, -self.s), self.c)]
        for n, c in planes:
            n = np.asarray(n, float)
            nd = D @ n
            np_ = P @ n
            with np.errstate(divide="ignore", invalid="ignore"):
                lam = (c - np_) / nd
            pos = nd > 0  # entering constraint: lam <= lam_plane
            hi = np.where(pos, np.minimum(hi, lam), hi)
            neg = nd < 0
            lo = np.where(neg, np.maximum(lo, lam), lo)
            zero = nd == 0
            bad = zero & (np_ > c)
            lo = np.where(bad, np.inf, lo)
        return lo, hi


def length(iv):
    return np.maximum(iv[1] - iv[0], 0.0)


def intersect(a, b):
    return np.maximum(a[0], b[0]), np.minimum(a[1], b[1])


def collimator(name):
    """The four Trd's and the two boxes of variant `name` in knife-edge coordinates."""
    w, lt, hn = m.WIDTHS[name], m.L_TOP[name], m.H_NOZZLE[name]
    hb = m.H_BODY
    zk = 0.5 * (hb - hn)  # knife edge in the frustum-A-centred frame
    dxy_b = (lt - w) / hn * DELTA_Z * 0.5
    dxy_c = (w - m.L_BOTTOM_INNER) / hb * DELTA_Z * 0.5
    A = Trd(L_BOTTOM_OUTER / 2, lt / 2, (hn + hb) / 2, -zk)
    B = Trd(w / 2 - dxy_b, lt / 2 + dxy_b, hn / 2 + DELTA_Z, hb / 2 - zk)
    C = Trd(m.L_BOTTOM_INNER / 2 - dxy_c, w / 2 + dxy_c, hb / 2 + DELTA_Z, -hn / 2 - zk)
    zbox = -0.5 * (hn + hb + H_BOX) - zk
    box_a = Trd(L_BOTTOM_OUTER / 2, L_BOTTOM_OUTER / 2, H_BOX / 2, zbox)
    box_b = Trd(L_BOTTOM_OUTER / 2 - W_WALL, L_BOTTOM_OUTER / 2 - W_WALL, H_BOX / 2 + 1.0, zbox)
    return A, B, C, box_a, box_b


def path_length(solids, P, D):
    """Tungsten path length (mm) along rays P + lam D, lam in [0, 1]: |A| - |A&B| - |A&C| + |A&B&C| + |box_a| - |box_a&box_b|."""
    A, B, C, ba, bb = solids
    iA, iB, iC = A.interval(P, D), B.interval(P, D), C.interval(P, D)
    iAB, iAC = intersect(iA, iB), intersect(iA, iC)
    iABC = intersect(iAB, iC)
    iba, ibb = ba.interval(P, D), bb.interval(P, D)
    lam = length(iA) - length(iAB) - length(iAC) + length(iABC) + length(iba) - length(intersect(iba, ibb))
    return lam * np.linalg.norm(D, axis=-1)


def trace(name, b, theta_deg, phi_deg, f=m.F_MM, mu=m.MU_W, step=0.004, margin=2.5, chunk=200):
    """Transmission map on the detection plane z = -f for a point source at (b, theta, phi)."""
    w = m.WIDTHS[name]
    solids = collimator(name)
    theta, phi = np.radians(theta_deg), np.radians(phi_deg)
    S = np.array([b * np.tan(theta) * np.cos(phi), b * np.tan(theta) * np.sin(phi), b])
    Xc = -S[:2] * f / b  # projection of the pinhole centre
    half = 0.5 * w * (b + f) / b + margin
    x = Xc[0] + np.arange(-half, half + step / 2, step)
    y = Xc[1] + np.arange(-half, half + step / 2, step)
    T = np.empty((len(x), len(y)))
    flux = np.empty_like(T)
    for i0 in range(0, len(x), chunk):
        X, Y = np.meshgrid(x[i0:i0 + chunk], y, indexing="ij")
        Q = np.stack([X, Y, np.full_like(X, -f)], axis=-1)
        D = Q - S
        L = path_length(solids, S, D)
        T[i0:i0 + chunk] = np.exp(-mu * L)
        dist2 = (D * D).sum(-1)
        flux[i0:i0 + chunk] = (f + b) / np.sqrt(dist2) / (4 * np.pi * dist2)  # cos(angle to detector normal)/(4 pi dist^2)
    return x, y, T, flux, S, Xc


def analyse(name, b, theta_deg, phi_deg, **kw):
    w = m.WIDTHS[name]
    t1, t2 = m.slopes(name)
    f, mu = m.F_MM, m.MU_W
    x, y, T, flux, S, Xc = trace(name, b, theta_deg, phi_deg, **kw)
    step = x[1] - x[0]
    scale = b / (b + f)  # detector plane -> knife-edge plane
    ix, iy = np.argmin(np.abs(x - Xc[0])), np.argmin(np.abs(y - Xc[1]))
    fw = {"x": m.full_width(T[:, iy], 0.5) * step * scale, "y": m.full_width(T[ix, :], 0.5) * step * scale,
          "diag+": m.full_width(np.diagonal(T), 0.5) * step * np.sqrt(2) * scale,
          "diag-": m.full_width(np.diagonal(np.fliplr(T)), 0.5) * step * np.sqrt(2) * scale}
    P = T * flux
    s = P.sum()
    X, Y = np.meshgrid(x, y, indexing="ij")
    mx, my = (P * X).sum() / s, (P * Y).sum() / s
    rms = {"x": np.sqrt((P * (X - mx) ** 2).sum() / s) * scale, "y": np.sqrt((P * (Y - my) ** 2).sum() / s) * scale}
    g = s * step * step  # per emitted photon
    theta, phi = np.radians(theta_deg), np.radians(phi_deg)
    r = b / np.cos(theta)
    A_model = m.area_eff_square(w, t1, t2, theta, phi, mu)
    g_model = A_model * np.cos(theta) / (4 * np.pi * r * r)
    g_current = m.paix_form(w, 1.0, mu) ** 2 * np.cos(theta) ** 3 / (4 * np.pi * r * r)  # analytic.py (cos^3 / r^2)
    g_geom = w * w * np.cos(theta) / (4 * np.pi * r * r)
    Wx, Wy = m.fwhm_sides_square(w, t1, t2, theta, phi, mu)
    # transmission map of the parallel-beam model on the same rays (knife-edge-plane crossing points)
    x0 = (S[0] * f + X * b) / (b + f)
    y0 = (S[1] * f + Y * b) / (b + f)
    Tm = m.transmission_square(x0, y0, w, t1, t2, theta, phi, mu)
    return {"variant": name, "w": w, "b": b, "theta_deg": theta_deg, "phi_deg": phi_deg,
            "fwhm_aperture_plane": fw, "model_fwhm_sides": {"x": Wx, "y": Wy},
            "rms_aperture_plane": rms,
            "model_rms_normal": m.rms_square_normal(w, 2 / (1 / t1 + 1 / t2), mu),
            "g_trace": g, "g_model": g_model, "g_current_script": g_current, "g_geometric": g_geom,
            "A_eff_trace": g / (np.cos(theta) / (4 * np.pi * r * r)), "A_eff_model": A_model,
            "max_abs_T_diff_model": float(np.abs(T - Tm).max()), "grid_step": step, "n": T.shape}


def main():
    runs = []
    for name in "ABCD":
        for th in (0, 15, 30):
            for ph in (0, 45):
                runs.append((name, m.B_CENTRE, th, ph))
    runs += [("C", 53.0, 30, 0), ("C", 247.0, 30, 0), ("C", 53.0, 0, 0), ("A", 53.0, 30, 0),
             ("C", m.B_CENTRE, 40, 0), ("A", m.B_CENTRE, 40, 0), ("D", m.B_CENTRE, 40, 0),
             ("C", m.B_CENTRE, 40, 45), ("C", m.B_CENTRE, 30, 20), ("A", m.B_CENTRE, 30, 20)]
    res = []
    for name, b, th, ph in runs:
        r = analyse(name, b, th, ph)
        res.append(r)
        fw, mf, rm = r["fwhm_aperture_plane"], r["model_fwhm_sides"], r["rms_aperture_plane"]
        print(f"{name} b={b:5.1f} th={th:2d} ph={ph:2d} | FWHM x {fw['x']:.4f} (model {mf['x']:.4f})  y {fw['y']:.4f} "
              f"(model {mf['y']:.4f})  diag {fw['diag+']:.4f}/{fw['diag-']:.4f} | rms x {rm['x']:.4f} y {rm['y']:.4f} "
              f"(model n.i. {r['model_rms_normal']:.4f}) | A_eff trace {r['A_eff_trace']:.4f} model {r['A_eff_model']:.4f} "
              f"| g trace/model {r['g_trace'] / r['g_model']:.4f}  g current/trace {r['g_current_script'] / r['g_trace']:.4f} "
              f"| max|T-Tm| {r['max_abs_T_diff_model']:.4f}", flush=True)
    (OUT / "raytrace_results.json").write_text(json.dumps(res, indent=1, default=float) + "\n")


if __name__ == "__main__":
    main()
