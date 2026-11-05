"""Cross-checks and the numeric tables of square_pinhole.md.  CPU / numpy only.

1. Metzler & Moore 2020 (IEEE TMI 39:833, eq. 22 with tau = 1 and eq. 25) against the closed form of
   square_pinhole_model.py (independent derivation) on a grid of angles.
2. Round-pinhole equivalents of each square width (area, FWHM, RMS).
3. The cross-check table of the equations used by analytic.py (theta = 0 and 30 deg).
4. The recommended R_g (per direction) and g for A-D at theta = 0, 15, 30 deg, and the change vs the
   current analytic.py numbers.

    micromamba run -n opengate python crosscheck_tables.py   (writes tables.md and tables.json)
"""

import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import square_pinhole_model as m  # noqa: E402

OUT = Path(__file__).resolve().parent
MU, T, F, B0 = m.MU_W, 1.0, m.F_MM, m.B_CENTRE
DLK = np.log(2) / MU  # Delta L_k for k = 0.5, Accorsi & Metzler 2004 eq. (9)
MAG = (B0 + F) / F


def area_eff_mm2020(w, t, theta, phi, mu):
    """Metzler & Moore 2020 eq. (22) (tau_x = tau_y = 1) for a square (w, alpha) converted to an effective area
    A_eff = w^2 + g_pen 4 pi h^2 / cos^3(theta); theta from the axis, tan(theta_x) = tan(theta) cos(phi)."""
    tx, ty = np.tan(theta) * np.cos(phi), np.tan(theta) * np.sin(phi)
    c = np.cos(theta)
    strips = c * w / (mu * t) * (2 * t * t - tx * tx - ty * ty)  # (1+tx^2+ty^2)^-2 = cos^4; / cos^3 -> cos
    M, mm = max(abs(tx), abs(ty)) / t, min(abs(tx), abs(ty)) / t
    corners = t * t * c * c / mu ** 2 * (1 - M) * (3 * (1 - mm * mm) - (1 - M) ** 2)
    return w * w + strips + corners


def mm2020_check():
    worst = 0.0
    rows = []
    for w in m.WIDTHS.values():
        for th in (0, 10, 20, 30, 40):
            for ph in (0, 15, 30, 45):
                theta, phi = np.radians(th), np.radians(ph)
                mine = m.area_eff_square(w, T, T, theta, phi, MU)
                theirs = area_eff_mm2020(w, T, theta, phi, MU)
                rel = theirs / mine - 1
                worst = max(worst, abs(rel))
                if ph in (0, 45) and th in (0, 30, 40):
                    rows.append((w, th, ph, mine, theirs, rel))
    return worst, rows


def round_equivalents(w):
    """Round diameters equivalent to a square of side w (t = 1, 140 keV W): same effective area, same FWHM
    along a side, same RMS width (one axis); each with and without penetration."""
    A_sq = m.area_eff_square(w, T, T, 0.0, 0.0, MU)
    d_area_geo = 2 * w / np.sqrt(np.pi)
    d_area_pen = brentq(lambda d: np.pi / 4 * m.d_e_paix(d, T, MU) ** 2 - A_sq, 1e-6, 10)
    d_rms_geo = 4 * w / np.sqrt(12)  # d/4 = w/sqrt(12)
    d_rms_pen = brentq(lambda d: m.rms_round_normal(d, T, MU) - m.rms_square_normal(w, T, MU), 1e-6, 10)
    return {"A_eff_square": A_sq, "d_area_geo": d_area_geo, "d_area_pen": d_area_pen, "d_fwhm_side": w,
            "d_rms_geo": d_rms_geo, "d_rms_pen": d_rms_pen, "rms_square_pen": m.rms_square_normal(w, T, MU),
            "rms_square_geo": w / np.sqrt(12)}


def recommended(w, th_deg, phi_deg=None):
    """Recommended widths (knife-edge plane) and effective area at theta; phi = None -> side-averaged forms."""
    theta = np.radians(th_deg)
    c, tt = np.cos(theta), np.tan(theta) ** 2
    W_par = w + DLK * c * (T * T - tt) / T  # side along the tilt (= AM2004 eq. 22 with d -> w)
    W_perp = w + DLK * c * T  # side across the tilt
    W_mean = w + DLK * c * (T - tt / (2 * T))  # phi-independent mean of the two sides
    phis = np.radians([0, 15, 30, 45]) if phi_deg is None else np.radians([phi_deg])
    A = float(np.mean([m.area_eff_square(w, T, T, theta, p, MU) for p in phis]))
    A0, A45 = (m.area_eff_square(w, T, T, theta, p, MU) for p in (0.0, np.pi / 4))
    return {"W_par": W_par, "W_perp": W_perp, "W_mean": W_mean, "W_diag": np.sqrt(2) * W_perp,
            "A_eff": A, "A_eff_phi0": A0, "A_eff_phi45": A45}


def main():
    worst, rows = mm2020_check()
    lines = ["## Metzler & Moore 2020 eq. (22) vs this derivation (t = 1, mu = 3.63 /mm)", "",
             f"Largest relative difference over w = A-D, theta = 0-40 deg, phi = 0-45 deg: {worst:.2e}", "",
             "| w (mm) | theta | phi | A_eff this work (mm^2) | A_eff MM2020 eq. 22 | rel. diff |", "|---|---|---|---|---|---|"]
    for w, th, ph, mine, theirs, rel in rows:
        lines.append(f"| {w:.3f} | {th} | {ph} | {mine:.5f} | {theirs:.5f} | {rel:+.1e} |")

    lines += ["", "## Round-pinhole equivalents of the square (normal incidence, t = 1, 140 keV, W)", "",
              "| aperture | w | A_eff square | d: same area, geometric 2w/sqrt(pi) | d: same area with penetration (Paix) | "
              "d: same FWHM along a side | RMS square: geometric w/sqrt(12) | RMS square with penetration | d: same RMS, geometric 2w/sqrt(3) | d: same RMS with penetration |",
              "|---" * 10 + "|"]
    eq = {}
    for n, w in m.WIDTHS.items():
        e = round_equivalents(w)
        eq[n] = e
        lines.append(f"| {n} | {w:.3f} | {e['A_eff_square']:.4f} | {e['d_area_geo']:.3f} | {e['d_area_pen']:.3f} | {e['d_fwhm_side']:.3f} | "
                     f"{e['rms_square_geo']:.3f} | {e['rms_square_pen']:.3f} | {e['d_rms_geo']:.3f} | {e['d_rms_pen']:.3f} |")

    lines += ["", "## Equations of analytic.py at theta = 0 and 30 deg (knife-edge plane, mm; areas mm^2)", "",
              "| aperture | w | d_re current = w + ln2 t/mu | W_par(30) | W_perp(30) | W_diag(0) = sqrt2 W | w_s current (Paix) | sqrt(A_eff(0)) | "
              "A_eff(0) | A_eff(30, phi=0) | A_eff(30, phi=45) | cos^2(30) error of the current g | "
              "g recommended / g current at 30 deg |", "|---" * 13 + "|"]
    tab = {}
    for n, w in m.WIDTHS.items():
        r0, r30 = recommended(w, 0), recommended(w, 30)
        cur_ws = m.paix_form(w, T, MU)
        ratio30 = r30["A_eff"] / (cur_ws ** 2 * np.cos(np.radians(30)) ** 2)
        tab[n] = {"w": w, "d_re_current": m.d_res_current(w) if hasattr(m, "d_res_current") else w + DLK * T,
                  "r0": r0, "r30": r30, "ws_current": cur_ws, "g_ratio_30": ratio30}
        lines.append(f"| {n} | {w:.3f} | {w + DLK * T:.3f} | {r30['W_par']:.3f} | {r30['W_perp']:.3f} | {r0['W_diag']:.3f} | {cur_ws:.3f} | "
                     f"{np.sqrt(r0['A_eff']):.3f} | {r0['A_eff']:.4f} | {r30['A_eff_phi0']:.4f} | {r30['A_eff_phi45']:.4f} | "
                     f"{np.cos(np.radians(30)) ** 2:.3f} | {ratio30:.3f} |")

    lines += ["", f"## Recommended numbers, A-D at theta = 0, 15, 30 deg (b = {B0} mm, f = {F} mm, (b+f)/f = {MAG:.3f})", "",
              "R_g = W (b+f)/f referred to the object; g = A_eff cos(theta) / (4 pi r^2) = A_eff cos^3(theta) / (4 pi b^2); "
              "g_current = w_s^2 cos^3(theta) / (4 pi r^2) with r = b / cos(theta).", "",
              "| aperture | theta | W_par | W_perp | W_mean | R_g,par | R_g,perp | R_g current | A_eff (phi-avg) | "
              "g x 1e6 (b = 149.6) | g current x 1e6 | g rec / g current |", "|---" * 12 + "|"]
    rec = {}
    for n, w in m.WIDTHS.items():
        rec[n] = {}
        for th in (0, 15, 30):
            r = recommended(w, th)
            theta = np.radians(th)
            rr = B0 / np.cos(theta)
            g = r["A_eff"] * np.cos(theta) / (4 * np.pi * rr ** 2)
            g_cur = m.paix_form(w, T, MU) ** 2 * np.cos(theta) ** 3 / (4 * np.pi * rr ** 2)
            Rg_cur = (w + DLK * T) * MAG
            rec[n][th] = {**r, "R_g_par": r["W_par"] * MAG, "R_g_perp": r["W_perp"] * MAG, "R_g_current": Rg_cur,
                          "g": g, "g_current": g_cur}
            lines.append(f"| {n} | {th} | {r['W_par']:.3f} | {r['W_perp']:.3f} | {r['W_mean']:.3f} | {r['W_par'] * MAG:.2f} | "
                         f"{r['W_perp'] * MAG:.2f} | {Rg_cur:.2f} | {r['A_eff']:.4f} | {g * 1e6:.3f} | {g_cur * 1e6:.3f} | {g / g_cur:.3f} |")

    # round pinhole of the same side (d = w) for comparison: AM2004 eqs. 22/25/29, Paix, Anger, Metzler-2001 area
    lines += ["", "## Round knife-edge pinhole with d = w, for comparison (AM2004 eqs. 3, 5, 22, 25, 29; Metzler 2001 area via M&A 2005 eq. A.1)", "",
              "| aperture | d = w | Anger d_e (3) | Paix d_e (5) | d_re(0) (29) | d_re,par(30) (22) | d_re,perp(30) (25) | pi d_e^2/4 (Paix area) | "
              "A_round(30) Metzler 2001 | A_square(30) this work |", "|---" * 10 + "|"]
    for n, w in m.WIDTHS.items():
        th = np.radians(30)
        lines.append(f"| {n} | {w:.3f} | {m.d_e_anger(w, T, MU):.3f} | {m.d_e_paix(w, T, MU):.3f} | {m.d_re_normal(w, T, MU):.3f} | "
                     f"{m.d_re_parallel(w, T, th, MU):.3f} | {m.d_re_perpendicular(w, T, th, MU):.3f} | {np.pi / 4 * m.d_e_paix(w, T, MU) ** 2:.4f} | "
                     f"{m.area_eff_round_metzler2001(w, T, th, MU):.4f} | {recommended(w, 30)['A_eff']:.4f} |")

    (OUT / "tables.md").write_text("\n".join(lines) + "\n")
    (OUT / "tables.json").write_text(json.dumps({"mm2020_worst_rel_diff": worst, "round_equivalents": eq, "recommended": rec},
                                                indent=1, default=float) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
