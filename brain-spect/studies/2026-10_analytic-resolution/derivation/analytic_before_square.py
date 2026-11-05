"""Analytical (classic pinhole) resolution of the brain SPECT system, worked out step by step, and the
information argument for the aperture size. Writes analytic.json and the figures used by analytic_baseline.qmd.

Formulas (per module k that sees the point; same as dev/python/resolution_theory.py):
    b      distance of the point from the aperture plane, along the module axis
    f      pinhole to mean interaction depth = 27 mm (entrance face 25 mm + ~2 mm mean depth at 140 keV)
    R_g    = d_e (b + f) / f                  geometric (aperture) term, referred to the object
    R_i    = p b / f                          detector term: pixel pitch p back-projected to the object
    R      = sqrt(R_g^2 + R_i^2)              projection FWHM of module k at the point
    g      = w_s^2 cos^3(theta) / (4 pi r^2)  geometric sensitivity, square aperture
d_e: nominal width w, or with penetration the resolution-effective width of Accorsi & Metzler (2004,
normal incidence, first order) d_re = w + ln2 tan(a/2) / mu for R_g; the counts g use the Paix
sensitivity-effective width w_s (resolution_theory.py used Paix for both: an upper bound). Detectors: parallel 2 mm pixels (p = 2 mm at depth f), or converging pixels whose pitch
grows with the distance s from the pinhole, p(s) = 2 s / 35 mm, so p b / f = 2 b / 35 at every depth.
Combination over the modules: best single module, and the information-weighted combination
    R_comb = (sum g R^-2 / sum g)^(-1/2)
(the per-count Fisher information of a Gaussian blur goes as R^-2).

Information per head at spatial frequency nu (Gaussian blur): I_k(nu) = g_k * MTF_k(nu)^2,
MTF = exp(-(pi R nu)^2 / (4 ln 2)). A box model (aperture box x pixel box, |sinc|^2) is the check.

    micromamba run -n opengate env -u DISPLAY python analytic.py
"""

import getpass
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROV = Path(f"/data/{getpass.getuser()}/opengate_sim/data/brain_spect/brain_288mm_csg_102t_20261005T211647Z_01/geometry_provenance.json")
OUT = Path(__file__).resolve().parent
IMG = OUT / "img"
F_MM, MU_W, TAN_HALF, HALF_CRYSTAL = 27.0, 3.63, 1.0, 25.0
PITCH = {"parallel 2 mm": 2.0 / F_MM, "converging": 2.0 / 35.0}  # R_i = coefficient * b
NAMES = "ABCD"
NU = {"8 mm rods": 1 / 16, "6 mm rods": 1 / 12, "5 mm rods": 1 / 10, "4 mm rods": 1 / 8}
INK, INK2, GRID = "#1d1d1f", "#6e6e73", "#e5e5ea"
COL = {"A": "#93c5fd", "B": "#3b82f6", "C": "#1d4ed8", "D": "#0b1f5c", "current mix": "#ea580c"}


def paix(w):
    return np.sqrt(w**2 + 2 * w * TAN_HALF / MU_W + 2 * TAN_HALF**2 / MU_W**2)


def d_res(w):
    return w + np.log(2) * TAN_HALF / MU_W


def geometry():
    p = json.loads(PROV.read_text())
    g = p["analytic_geometry"]
    widths = np.array([v["w_pinhole"] for v in p["pinhole_pattern"]["collimator_variants"]])
    variant = np.asarray(g["parts"]["collimator"]["variant_index"])
    ph = np.asarray(g["modules"]["pinhole_mm"])
    rot = np.asarray(g["modules"]["rotation"]).reshape(-1, 3, 3)
    return widths, variant, ph, rot


def modules_seeing(point, ph, rot):
    """b, theta, r of every module whose crystal the point projects onto (shield not modelled)."""
    out = []
    for k in range(len(ph)):
        u, v, n = rot[k][:, 0], rot[k][:, 1], rot[k][:, 2]
        d = point - ph[k]
        b = d @ n
        if b <= 0:
            continue
        hit = -d * F_MM / b
        if abs(hit @ u) > HALF_CRYSTAL or abs(hit @ v) > HALF_CRYSTAL:
            continue
        r = np.linalg.norm(d)
        out.append((k, b, b / r, r))
    k, b, cos, r = (np.array(x) for x in zip(*out))
    return k.astype(int), b, cos, r


def terms(w, b, cos, r, coef, pen=True, intrinsic=True):
    de, ws = (d_res(w), paix(w)) if pen else (w, w)
    rg = de * (b + F_MM) / F_MM
    ri = coef * b if intrinsic else 0 * b
    R = np.hypot(rg, ri)
    g = ws**2 * cos**3 / (4 * np.pi * r**2)  # sensitivity-effective width for the counts
    return rg, ri, R, g


def combine(R, g):
    return float((np.sum(g / R**2) / g.sum()) ** -0.5)


def info(g, R, nu, rg=None, ri=None, model="gauss"):
    if model == "gauss":
        mtf = np.exp(-((np.pi * R * nu) ** 2) / (4 * np.log(2)))
    else:  # aperture box x pixel box
        mtf = np.abs(np.sinc(rg * nu) * np.sinc(ri * nu))
    return float(np.sum(g * mtf**2))


def lir_half_max():
    """Half-max width of the ideal LIR (alpha = 1e-3 lambda_max, 1 mm voxels; dev/python/ideal_lir/ideal_lir_slices.npz)
    along 12 directions in the slice through the peak (bilinear profiles, 0.25 mm steps): min, mean, max over directions."""
    from scipy.ndimage import map_coordinates

    d = np.load(OUT.parent.parent / "python/ideal_lir/ideal_lir_slices.npz")
    t = np.arange(-30, 30.01, 0.25)
    c = len(t) // 2
    out = {}
    for rr in (0, 30, 60, 80, 95):
        a = d[f"r{rr:03d}_a0.001"].astype(float)
        iy, ix = np.unravel_index(np.argmax(a), a.shape)
        ws = []
        for ang in np.radians(np.arange(0, 180, 15)):
            v = map_coordinates(a, [iy + t * np.sin(ang), ix + t * np.cos(ang)], order=1)
            v = v / v[c]
            w = 0.0
            for step in (1, -1):
                i = c
                while v[i] >= 0.5:
                    i += step
                j = i - step
                w += (abs(j - c) + (v[j] - 0.5) / (v[j] - v[i])) * 0.25
            ws.append(w)
        out[f"LIR r={rr}"] = {"min": float(min(ws)), "mean": float(np.mean(ws)), "max": float(max(ws))}
    return out


def main():
    IMG.mkdir(exist_ok=True)
    widths, variant, ph, rot = geometry()
    res = {"assumptions": {"f_mm": F_MM, "mu_W_per_mm": MU_W, "tan_half_acceptance": TAN_HALF,
                           "widths_mm": widths.tolist(), "paix_mm": paix(widths).tolist(), "d_res_mm": d_res(widths).tolist(),
                           "inventory": np.bincount(variant).tolist(), "pinhole_sphere_radius_mm": float(np.linalg.norm(ph, axis=1).mean())}}

    # 1. worked example: the centre of the helmet (all 73 modules at the same b, theta = 0)
    k, b, cos, r = modules_seeing(np.zeros(3), ph, rot)
    b0 = float(b.mean())
    rows = []
    for name, w in zip(NAMES, widths):
        for pen in (False, True):
            de, ws = (d_res(w), paix(w)) if pen else (w, w)
            rg = de * (b0 + F_MM) / F_MM
            row = {"aperture": name, "w": float(w), "penetration": pen, "d_e": float(de), "w_s": float(ws), "R_g": float(rg),
                   "g_rel_A_nominal": float(ws**2 / widths[0] ** 2)}
            for det, coef in PITCH.items():
                row[f"R_i {det}"] = float(coef * b0)
                row[f"R {det}"] = float(np.hypot(rg, coef * b0))
            rows.append(row)
    cur = {}
    for det, coef in PITCH.items():
        for pen in (False, True):
            rg, ri, R, g = terms(widths[variant[k]], b, cos, r, coef, pen)
            cur[f"{det}, {'pen' if pen else 'nominal'}"] = {"best": float(R.min()), "combined": combine(R, g),
                                                          "geometric_only_combined": combine(rg, g)}
    res["centre"] = {"n_modules": int(len(k)), "b_mm": b0, "magnification_f_over_b": F_MM / b0, "per_aperture": rows,
                     "current_mix": cur}

    # 2. the LIR points (slice z = +25.5 mm, 30 deg ray) and the uniform plane of resolution_theory.py
    pts = {f"LIR r={rr}": np.array([rr * np.cos(np.radians(30)), rr * np.sin(np.radians(30)), 25.5]) for rr in (0, 30, 60, 80, 95)}
    pts.update({f"uniform r={rr}": np.array([rr, 0.0, -70.0]) for rr in (0, 35, 65)})
    res["points"] = {}
    for name, p in pts.items():
        k, b, cos, r = modules_seeing(p, ph, rot)
        w = widths[variant[k]]
        d = {"n_modules": int(len(k)), "b_min": float(b.min()), "b_median": float(np.median(b)), "b_max": float(b.max())}
        for det, coef in PITCH.items():
            rg, ri, R, g = terms(w, b, cos, r, coef, True)
            rgn, _, Rn, gn = terms(w, b, cos, r, coef, False)
            d[det] = {"best_pen": float(R.min()), "best_nom": float(Rn.min()), "comb_pen": combine(R, g), "comb_nom": combine(Rn, gn),
                      "median_module_pen": float(np.median(R)), "geometric_only_best_nom": float(rgn.min()),
                      "geometric_only_comb_pen": combine(rg, g)}
        res["points"][name] = d

    # 3. the information argument: pure designs vs the current mix, at the centre and at LIR r = 60
    res["information"] = {}
    for pname, p in (("centre", np.zeros(3)), ("LIR r=60", pts["LIR r=60"])):
        k, b, cos, r = modules_seeing(p, ph, rot)
        tab = {}
        for det, coef in PITCH.items():
            designs = {n: np.full(len(k), w) for n, w in zip(NAMES, widths)}
            designs["current mix"] = widths[variant[k]]
            t = {}
            for dn, w in designs.items():
                rg, ri, R, g = terms(w, b, cos, r, coef, True)
                t[dn] = {lab: {"gauss": info(g, R, nu), "box": info(g, R, nu, rg, ri, "box")} for lab, nu in NU.items()}
                t[dn]["sensitivity"] = float(g.sum())
            tab[det] = t
        res["information"][pname] = tab

    res["lir_half_max_mm"] = lir_half_max()
    (OUT / "analytic.json").write_text(json.dumps(res, indent=1) + "\n")
    tables(res)
    fig_terms(widths)
    fig_information(widths, variant, ph, rot)
    print(json.dumps(res["centre"], indent=1)[:3000])


def tables(res):
    """Markdown tables included by analytic_baseline.qmd (every number in the document comes from analytic.json)."""
    t = OUT / "_tables"
    t.mkdir(exist_ok=True)
    c = res["centre"]
    b0 = c["b_mm"]
    lines = ["| aperture | w (mm) | d_re (mm) | w_s (mm) | R_g = d_re (b+f)/f | R_i, parallel = 2 b / 27 | R, parallel | "
             "R_i, converging = 2 b / 35 | R, converging | counts vs A |", "|---" * 10 + "|"]
    for row in c["per_aperture"]:
        if not row["penetration"]:
            continue
        lines.append(f"| {row['aperture']} | {row['w']:.3f} | {row['d_e']:.3f} | {row['w_s']:.3f} | {row['R_g']:.2f} | "
                     f"{row['R_i parallel 2 mm']:.2f} | **{row['R parallel 2 mm']:.2f}** | {row['R_i converging']:.2f} | "
                     f"**{row['R converging']:.2f}** | {(row['w_s'] / c['per_aperture'][1]['w_s']) ** 2:.2f} |")
    (t / "centre.md").write_text("\n".join(lines) + "\n")
    lines = ["| aperture | R_g nominal width | R_g with penetration |", "|---|---|---|"]
    for k in range(0, len(c["per_aperture"]), 2):
        a, p = c["per_aperture"][k], c["per_aperture"][k + 1]
        lines.append(f"| {a['aperture']} | {a['w']:.3f} x {(b0 + F_MM) / F_MM:.3f} = {a['R_g']:.2f} | {p['d_e']:.3f} x {(b0 + F_MM) / F_MM:.3f} = {p['R_g']:.2f} |")
    (t / "geometric.md").write_text("\n".join(lines) + "\n")
    lines = ["| detector | best module | information-weighted, all 73 | aperture term only, weighted |", "|---|---|---|---|"]
    for k, v in c["current_mix"].items():
        lines.append(f"| {k} | {v['best']:.1f} | {v['combined']:.1f} | {v['geometric_only_combined']:.1f} |")
    (t / "centre_mix.md").write_text("\n".join(lines) + "\n")
    lines = ["| point | b min / median / max (mm) | best module, parallel | weighted, parallel | best module, converging | weighted, converging |",
             "|---" * 6 + "|"]
    for k, v in res["points"].items():
        pa, cv = v["parallel 2 mm"], v["converging"]
        lines.append(f"| {k.replace('LIR', 'slice z = 25.5 mm,').replace('uniform', 'uniform slice z = -70 mm,')} | {v['b_min']:.0f} / {v['b_median']:.0f} / {v['b_max']:.0f} | "
                     f"{pa['best_pen']:.1f} | {pa['comb_pen']:.1f} | {cv['best_pen']:.1f} | {cv['comb_pen']:.1f} |")
    (t / "points.md").write_text("\n".join(lines) + "\n")
    lines = ["| r (mm) | reconstructed point response, half-max: mean (min-max over directions) | best module | ratio | weighted | ratio |",
             "|---" * 6 + "|"]
    for k, v in res["lir_half_max_mm"].items():
        pa = res["points"][k]["parallel 2 mm"]
        lines.append(f"| {k.split('=')[1]} | **{v['mean']:.1f}** ({v['min']:.1f}-{v['max']:.1f}) | {pa['best_pen']:.1f} | {pa['best_pen'] / v['mean']:.2f} | "
                     f"{pa['comb_pen']:.1f} | **{pa['comb_pen'] / v['mean']:.2f}** |")
    (t / "ratios.md").write_text("\n".join(lines) + "\n")
    lines = ["| design | counts (rel. to all A) | " + " | ".join(NU) + " |", "|---" * (2 + len(NU)) + "|"]
    for pname in ("centre", "LIR r=60"):
        tt = res["information"][pname]["converging"]
        sA = tt["A"]["sensitivity"]
        lines.append(f"| *{'centre' if pname == 'centre' else 'r = 60 mm'}* |" + " |" * (1 + len(NU)))
        for dn, v in tt.items():
            cells = []
            for lab in NU:
                best = max(tt[q][lab]["gauss"] for q in NAMES)
                bestb = max(tt[q][lab]["box"] for q in NAMES)
                cells.append(f"{v[lab]['gauss'] / best:.2f} / {v[lab]['box'] / bestb:.2f}")
            lines.append(f"| {dn} | {v['sensitivity'] / sA:.2f} | " + " | ".join(cells) + " |")
    (t / "information.md").write_text("\n".join(lines) + "\n")


def fig_terms(widths):
    """R_g, R_i and R against b, per aperture: the detector term sets a floor that no pinhole size removes."""
    b = np.linspace(50, 250, 200)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, (det, coef) in zip(axes, PITCH.items()):
        for name, w in zip(NAMES, widths):
            rg = d_res(w) * (b + F_MM) / F_MM
            ax.plot(b, np.hypot(rg, coef * b), color=COL[name], lw=1.8, label=f"{name} ({w:.2f} mm): total")
            ax.plot(b, rg, color=COL[name], lw=1.0, ls=":")
        ax.plot(b, coef * b, color=INK, lw=2.2, ls="--", label="detector term alone (floor)")
        ax.axvline(149.6, color=INK2, lw=0.8)
        ax.text(151, 1.0, "centre", color=INK2, fontsize=9)
        ax.set_title(f"{det} pixels" + (" (p b / f = 2 b / 27)" if det.startswith("par") else " (p b / f = 2 b / 35)"), fontsize=11)
        ax.set_xlabel("pinhole-to-point distance b (mm)")
        ax.grid(True, color=GRID)
    axes[0].set_ylabel("projection FWHM at the object (mm)")
    axes[0].legend(fontsize=8.5, loc="upper left")
    axes[1].text(155, 2.0, "dotted: aperture term alone\n(resolution-effective width)", fontsize=9, color=INK2)
    for ax in axes:
        ax.set_ylim(0, 22)
    fig.tight_layout()
    fig.savefig(IMG / "terms_vs_b.png", dpi=150)


def fig_information(widths, variant, ph, rot):
    """Information per frequency at r = 60 mm (LIR slice), pure designs and the current mix (Gaussian and box models)."""
    k, b, cos, r = modules_seeing(np.array([60 * np.cos(np.radians(30)), 60 * np.sin(np.radians(30)), 25.5]), ph, rot)
    nus = np.linspace(0.005, 0.2, 200)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    for ax, model in zip(axes, ("gauss", "box")):
        coef = PITCH["converging"]
        ref = None
        curves = {}
        for name, w in list(zip(NAMES, widths)) + [("current mix", None)]:
            ww = widths[variant[k]] if w is None else np.full(len(k), w)
            rg, ri, R, g = terms(ww, b, cos, r, coef, True)
            curves[name] = np.array([info(g, R, nu, rg, ri, model) for nu in nus])
        best = np.max([curves[n] for n in NAMES], axis=0)
        for name, c in curves.items():
            ax.plot(nus, c / best, color=COL[name], lw=2.4 if name == "current mix" else 1.6,
                    ls="--" if name == "current mix" else "-", label=name)
        for lab, nu in NU.items():
            ax.axvline(nu, color=GRID, lw=1)
            ax.text(nu, 1.03, lab.replace(" rods", ""), fontsize=8, color=INK2, ha="center")
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("spatial frequency (cycles / mm)")
        ax.set_title("Gaussian blur model" if model == "gauss" else "box model (aperture box x pixel box)", fontsize=11)
        ax.grid(True, color=GRID)
    axes[0].set_ylabel("information / best pure design")
    axes[0].legend(fontsize=9)
    fig.suptitle("Point at r = 60 mm, converging pixels: information = sum over heads of sensitivity x MTF^2 (analytic models only)", fontsize=11)
    fig.tight_layout()
    fig.savefig(IMG / "information_vs_frequency.png", dpi=150)


if __name__ == "__main__":
    main()
