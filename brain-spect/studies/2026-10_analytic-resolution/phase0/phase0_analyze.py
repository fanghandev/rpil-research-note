"""Phase 0 analysis: gammart (MC + deterministic) vs the classic formulas, module by module. Reads out/p0/*.json, out/p0/det.npz.
Writes phase0.json, phase0.md, phase0_sens.png, phase0_width.png.  Uses analytic.py (imported, not edited) for geometry and formulas."""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent)); sys.path.insert(0, str(HERE))
import analytic as A
import p0lib as P

widths, variant, ph, rot = A.geometry()
OUTD = HERE / "out" / "p0"
det = np.load(OUTD / "det.npz")
LSF = json.loads((HERE.parent / "derivation/lsf.json").read_text())
names = list(det["names"])
res = {"points": {}}
rows = []
for pn in names:
    ip = names.index(pn)
    pt = np.array(P.POINTS[pn])
    k, b, cos, r, phi = A.modules_seeing(pt, ph, rot)
    for des in P.DESIGNS:
        f = OUTD / f"mc_{des}_{pn.replace(' ', '_').replace('=', '')}.json"
        if not f.exists():
            continue
        mc = json.loads(f.read_text())
        w = widths[variant[k]] if des == "mix" else np.full(len(k), widths[P.DESIGNS[des]])
        dpar = det[f"{des}_parallel_pix"][ip].reshape(73, -1).sum(1)
        dcv = det[f"{des}_conv_pix"][ip].reshape(73, -1).sum(1) + det[f"{des}_conv_outside"][ip]
        for i, m in enumerate(k):
            e = mc["modules"].get(str(m))
            g_pen = A.area_square(w[i], cos[i], phi[i]) * cos[i] / (4 * np.pi * r[i]**2)   # A cos^3 / (4 pi b^2)
            g_nom = w[i]**2 * cos[i] / (4 * np.pi * r[i]**2)
            g_old = A.paix(w[i])**2 * cos[i]**3 / (4 * np.pi * r[i]**2)
            rec = {"point": pn, "design": des, "module": int(m), "w": float(w[i]), "b": float(b[i]), "theta_deg": float(np.degrees(np.arccos(cos[i]))),
                   "g_paix": g_pen, "g_nominal": g_nom, "g_old_cos3_over_r2": g_old, "cos": float(cos[i]), "det_parallel": float(dpar[m]), "det_conv": float(dcv[m])}
            rec["ratio_det_par_over_g_paix"] = rec["det_parallel"] / g_pen
            rec["ratio_det_par_over_g_nom"] = rec["det_parallel"] / g_nom
            if e and "raw" in e:
                rec["mc_p_fi"] = e["p_fi"]; rec["mc_p_win"] = e["p_win"]; rec["mean_s"] = e["mean_s"]
                rec["ratio_mc_over_g_paix"] = e["p_fi"] / g_pen
                rec["ratio_mc_over_g_nom"] = e["p_fi"] / g_nom
                mag = b[i] / e["mean_s"]          # detector -> object
                rg = A.width_square(w[i], cos[i]) * (b[i] + A.F_MM) / A.F_MM
                lsf = LSF["ABCD"[int(np.argmin(abs(widths - w[i])))]]
                rec["Rg_lsf_side"] = lsf["lsf_fwhm_side"] * (b[i] + A.F_MM) / A.F_MM   # normal-incidence line-spread FWHM (marginal of the PSF), object-referred
                rec["Rg_lsf_diag"] = lsf["lsf_fwhm_diag"] * (b[i] + A.F_MM) / A.F_MM
                rec["ratio_mc_over_g_old"] = e["p_fi"] / g_old
                rgn = w[i] * (b[i] + A.F_MM) / A.F_MM
                ri_p, ri_c = 2.0 * b[i] / e["mean_s"], 2.0 * b[i] / 35.0
                rec["Rg_formula_pen"], rec["Rg_formula_nom"] = rg, rgn
                rec["Rg_side_projected_nom"] = rgn   # box side projected on the detector, referred to the object
                rec["Rg_mc_u"] = e["norm"]["u"]["fwhm"] * mag; rec["Rg_mc_v"] = e["norm"]["v"]["fwhm"] * mag
                rec["Rg_mc_diag"] = 0.5 * (e["norm"]["d1"]["fwhm"] + e["norm"]["d2"]["fwhm"]) * mag
                rec["Rg_mc_rms_u"] = e["norm"]["u"]["rms"] * mag
                rec["aniso_side_over_diag"] = 0.5 * (e["norm"]["u"]["fwhm"] + e["norm"]["v"]["fwhm"]) / (0.5 * (e["norm"]["d1"]["fwhm"] + e["norm"]["d2"]["fwhm"]))
                rec["R_formula_par"] = float(np.hypot(rg, ri_p)); rec["R_formula_conv"] = float(np.hypot(rg, ri_c))
                for tag, key, unit in (("par", "readout_pa_prim", 1.0), ("conv", "readout_cv_prim", 1.0)):
                    rec[f"R_mc_{tag}_u"] = e[key]["u"]["fwhm"] * mag; rec[f"R_mc_{tag}_v"] = e[key]["v"]["fwhm"] * mag
                    rec[f"R_mc_{tag}_rms"] = 0.5 * (e[key]["u"]["rms"] + e[key]["v"]["rms"]) * mag
                rec["bin_fi_par_fwhm"] = 0.5 * (e["bin_fi_parallel"]["u"]["fwhm"] + e["bin_fi_parallel"]["v"]["fwhm"]) * mag
                rec["bin_fi_conv_fwhm"] = 0.5 * (e["bin_fi_conv"]["u"]["fwhm"] + e["bin_fi_conv"]["v"]["fwhm"]) * mag
                rec["f_eff"] = e["mean_s"]; rec["depth_sd"] = e["depth_sd"]
            rows.append(rec)
res["rows"] = rows
(HERE / "phase0.json").write_text(json.dumps(res, indent=1))

def agg(sel, key):
    v = np.array([r[key] for r in sel if key in r and np.isfinite(r[key])])
    return (v.mean(), v.std(), len(v)) if len(v) else (np.nan, np.nan, 0)

L = ["# Phase 0: gammart vs classic formulas", "",
     "Ratios are gammart / formula, mean +- SD over the modules that see the point (n). g_paix = w_s^2 cos^3 / (4 pi r^2) with the Paix width, g_nom with the nominal w. "
     "`det` = deterministic first-interaction probability (parallel pixel scene, summed over pixels); `MC` = gammart MC primary first-interaction probability. "
     "Rg(MC) = FWHM of first-interaction positions carried to the mean-depth plane x b / f_eff (continuous, no pixels), vs d_re (b+f)/f (pen.) and w (b+f)/f (nominal). R = FWHM of the in-window primary readout events binned in the real pixels x b / f_eff, vs sqrt(Rg^2 + Ri^2).", ""]
for pn in names:
    sel0 = [r for r in rows if r["point"] == pn]
    if not sel0:
        continue
    L += [f"## {pn}", "", "| design / aperture w | n | det/g | det/g_nom | MC/g | MC/g_nom | Rg MC (side) | Rg MC (diag) | side/diag (LSF pred. in text) | Rg formula PSF-cut / LSF side / LSF diag | Rg MC side / LSF side | R MC par | R formula par | R MC conv | R formula conv | f_eff |", "|---" * 16 + "|"]
    for lab, wv in [(l, w_) for l in ("uniform", "mix") for w_ in sorted({r["w"] for r in sel0})]:
        sel = [r for r in sel0 if r["w"] == wv and ((r["design"] == "mix") == (lab == "mix"))]
        if not sel:
            continue
        a = lambda k: agg(sel, k)
        f = lambda k, p=2: f"{a(k)[0]:.{p}f}"
        n = a("det_parallel")[2]
        L.append(f"| {lab} {wv:.3f} | {n} | {f('ratio_det_par_over_g_paix', 3)} | {f('ratio_det_par_over_g_nom', 3)} | {f('ratio_mc_over_g_paix', 3)} | {f('ratio_mc_over_g_nom', 3)} | "
                 f"{(a('Rg_mc_u')[0] + a('Rg_mc_v')[0]) / 2:.2f} | {f('Rg_mc_diag')} | {f('aniso_side_over_diag', 3)} | {f('Rg_formula_pen')} / {f('Rg_lsf_side')} / {f('Rg_lsf_diag')} | "
                 f"{(a('Rg_mc_u')[0] + a('Rg_mc_v')[0]) / 2 / a('Rg_lsf_side')[0]:.3f} | {(a('R_mc_par_u')[0] + a('R_mc_par_v')[0]) / 2:.2f} | {f('R_formula_par')} | "
                 f"{(a('R_mc_conv_u')[0] + a('R_mc_conv_v')[0]) / 2:.2f} | {f('R_formula_conv')} | {f('f_eff')} |")
    L.append("")
L += ["## Pixel-binned first interactions, phase-averaged (8 grid shifts), object-referred FWHM / RMS vs formula", "",
      "| point | w | R par bin FWHM | R par formula (quadrature) | R conv bin FWHM | R conv formula | RMS-equivalent check: sqrt(RMS_cont^2 + p^2/12) vs binned RMS (par, detector plane, ratio) |", "|---" * 7 + "|"]
for pn in names:
    for wv in sorted({r["w"] for r in rows}):
        sel = [r for r in rows if r["point"] == pn and r["w"] == wv and r["design"] != "mix" and "bin_fi_par_fwhm" in r]
        if sel:
            L.append(f"| {pn} | {wv:.3f} | {agg(sel,'bin_fi_par_fwhm')[0]:.2f} | {agg(sel,'R_formula_par')[0]:.2f} | {agg(sel,'bin_fi_conv_fwhm')[0]:.2f} | {agg(sel,'R_formula_conv')[0]:.2f} | |")
(HERE / "phase0.md").write_text("\n".join(L) + "\n")
print("\n".join(L[:60]))

# figures: sensitivity ratio and width vs formula, all uniform-design points
u = [r for r in rows if r["design"] != "mix" and "ratio_mc_over_g_paix" in r]
if u:
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for wv, c in zip(sorted({r["w"] for r in u}), A.COL.values()):
        s = [r for r in u if r["w"] == wv]
        ax[0].scatter([r["theta_deg"] for r in s], [r["ratio_mc_over_g_paix"] for r in s], s=8, color=c, label=f"w = {wv:.3f} mm")
        ax[1].scatter([r["Rg_formula_pen"] for r in s], [(r["Rg_mc_u"] + r["Rg_mc_v"]) / 2 for r in s], s=8, color=c)
    ax[0].axhline(1, color="k", lw=0.6); ax[0].set_xlabel("theta (deg)"); ax[0].set_ylabel("gammart MC / (w_s^2 cos^3 / 4 pi r^2)"); ax[0].legend(fontsize=8)
    m = max(r["Rg_formula_pen"] for r in u); ax[1].plot([0, m], [0, m], "k", lw=0.6)
    ax[1].set_xlabel("formula R_g = d_re (b+f)/f (mm)"); ax[1].set_ylabel("gammart R_g (first-interaction FWHM x b/f_eff) (mm)")
    fig.tight_layout(); fig.savefig(HERE / "phase0_sens_width.png", dpi=130)
