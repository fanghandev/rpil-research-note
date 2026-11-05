"""Figures for the weekly Brain SPECT update (30 Oct 2026), revision 1.

    CUDA_VISIBLE_DEVICES="" micromamba run -n raytracing env -u DISPLAY python scripts/make_figures.py

Every data figure reads its numbers from the files named below; schematics use the geometry in
ingredients/facts.md.  Numbers derived here are written to img/figure_numbers.json so the report can quote them
import os
from a file.  Most figures are drawn at the width at which the report shows them (text width 6.9 in), so the
font sizes below are the printed sizes (>= 7 pt).

Colours (Okabe-Ito; validated for colour-vision deficiency): GATE grey, gammart blue, reference black,
corrections vermilion / green.  Series that are neither GATE nor gammart (apertures A-D, scatter classes, map
types) use non-blue, non-grey hues.

Figures copied unchanged from earlier reports: WP0 spectra (rebuilding needs the GPU ray tracer), LIR profiles
(already in the house colours), the square-pinhole PSF (cropped to its middle column).  The terms-vs-b,
information, Phase 0, scorecard and WP2b figures are redrawn here from their data with the house colours.
"""

import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle  # noqa: E402
from scipy.ndimage import gaussian_filter, map_coordinates  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
IMG = HERE / "img"
IMG.mkdir(exist_ok=True)
Q = Path(f"{os.path.expanduser('~')}/Work/RPIL/QMIRT")
PO = Q / "pytorch-optix"
REP = Q / "qmirt-gate-10-sim/dev/reports"
ANA = REP / "2026-10-28_analytic_resolution"
sys.dont_write_bytecode = True  # imports from other folders must not leave caches there
sys.path.insert(0, str(PO / "examples"))

GATE, GAMMART, REF = "#6e6e6e", "#0072B2", "black"
VERM, GREEN, ORANGE, PURPLE = "#D55E00", "#009E73", "#E69F00", "#CC79A7"
APC = {"A": ORANGE, "B": PURPLE, "C": VERM, "D": GREEN}  # apertures A-D
TEXTW = 6.9  # text width of the report in inches
plt.rcParams.update({"font.size": 8.5, "axes.titlesize": 8.5, "axes.labelsize": 8.5, "legend.fontsize": 7.5,
                     "xtick.labelsize": 8, "ytick.labelsize": 8, "figure.dpi": 100, "savefig.dpi": 250,
                     "axes.spines.top": False, "axes.spines.right": False, "font.family": "DejaVu Sans",
                     "legend.frameon": False})
NUM = {}

N, V = 144, 2.0
AX = (np.arange(N) - (N - 1) / 2) * V


def save(fig, name):
    fig.savefig(IMG / name, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


# ----------------------------------------------------------------------------------------------- copies
COPIES = {
    "wp0_spectra.png": PO / "out/wp0/spectra_t2.png",
    "ideal_lir_profile.png": REP / "2026-10-28_brain_update/img/ideal_lir_profile.png",
}


def copies():
    for dst, src in COPIES.items():
        shutil.copy(src, IMG / dst)
        print("copied", dst)
    # square-pinhole PSF: keep only the middle column (point-profile cuts, incl. the diagonal)
    im = plt.imread(ANA / "derivation/img/psf_C.png")
    w = im.shape[1]
    plt.imsave(IMG / "psf_C_cuts.png", im[int(0.05 * im.shape[0]):, int(0.355 * w):int(0.655 * w)])
    print("wrote psf_C_cuts.png")


# ----------------------------------------------------------------------------------------------- schematics
def schematic_converging():
    """Side view of one module: pinhole, converging walls, edge strip; the same ray in parallel pixels."""
    fig, axs = plt.subplots(1, 2, figsize=(TEXTW, 3.5), sharey=True)
    s = np.array([25.0, 35.0])
    for ax, conv in zip(axs, (True, False)):
        ax.add_patch(Polygon([[-30, 6], [-0.6, 0], [-25, -22], [-30, -22]], color="0.85", lw=0))
        ax.add_patch(Polygon([[30, 6], [0.6, 0], [25, -22], [30, -22]], color="0.85", lw=0))
        ax.add_patch(Rectangle((-25, -35), 50, 10, fc="#f2f2f2", ec="k", lw=0.8))
        if conv:
            for j in range(26):
                ax.plot((j - 12.5) * (2 / 35) * s, -s, color="0.25", lw=0.5)
            for sg in (1, -1):
                ax.add_patch(Polygon([[sg * 17.857, -25], [sg * 25, -25], [sg * 25, -35]], fc=ORANGE, alpha=0.7, lw=0))
            ax.annotate("edge strip: 7.1 mm wide\nat the entrance, 0 at the exit", xy=(22.5, -28), xytext=(3, -47),
                        arrowprops=dict(arrowstyle="->", lw=0.7), ha="left")
            ax.set_title("converging pixels (walls aimed at the pinhole)")
        else:
            for x in np.arange(-25, 25.01, 2.0):
                ax.plot([x, x], [-25, -35], color="0.25", lw=0.5)
            ax.set_title("parallel 2 mm pixels (reference)")
        th = np.radians(30)
        ax.plot([0, 35 * np.tan(th)], [0, -35], color=VERM, lw=1.3)
        ax.plot([0, 0], [8, -38], color="0.5", lw=0.5, ls=":")
        ax.text(1.5, -16, "30°", color=VERM)
        ax.plot(0, 0, "k^", ms=4)
        ax.text(-2, 2.5, "pinhole", ha="right")
        ax.text(-24, -24, "entrance (25 mm)", va="bottom", fontsize=7.5)
        ax.text(-24, -36, "exit (35 mm)", va="top", fontsize=7.5)
        ax.set_xlim(-31, 31)
        ax.set_ylim(-50, 9)
        ax.set_aspect("equal")
        ax.set_xlabel("x across the crystal (mm)")
    axs[0].set_ylabel("distance from the pinhole (mm)")
    axs[1].text(-30, -46, "the 30° ray crosses 3–4 pixels\nwith depth: parallax", fontsize=7.5)
    fig.tight_layout()
    save(fig, "schematic_converging.png")


def box(ax, xy, w, h, title, body, fc):
    ax.add_patch(Rectangle(xy, w, h, fc=fc, ec="k", lw=0.8))
    ax.text(xy[0] + w / 2, xy[1] + h - 0.15, title, ha="center", va="top", fontsize=11, weight="bold")
    ax.text(xy[0] + w / 2, xy[1] + h - 0.62, body, ha="center", va="top", fontsize=6.9, linespacing=1.25)


def arrow(ax, a, b):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, lw=1.0, color="k"))


def schematic_forward_model():
    """x -> (A o H) -> K^T -> + s -> ybar_i, one symbol per box."""
    fig, ax = plt.subplots(figsize=(TEXTW, 1.75))
    ax.set_xlim(0, 16.3)
    ax.set_ylim(0.45, 2.75)
    ax.axis("off")
    W, H, y0 = 3.25, 2.0, 0.6
    xs = [0.0, 4.05, 8.1, 12.15]
    spec = [("x", "activity image\n144³ voxels of 2 mm\nρ ≤ 142 mm", "white"),
            ("Γ ∘ H", "attenuation factors Γ\ntimes first-interaction\nmatrix H\n(73 × 626 rows)", "#f3e0d2"),
            ("Kᵀ", "Compton-centroid\nkernel, 626 × 626,\npooled per\naperture size", "#f3e0d2"),
            ("+ s", "additive scatter:\nTEW from the side\nwindows, smoothed\nper module", "#d5efe5")]
    for x, (t, b, fc) in zip(xs, spec):
        box(ax, (x, y0), W, H, t, b, fc)
    for a, b in zip(xs[:-1], xs[1:]):
        arrow(ax, (a + W, y0 + H / 2), (b, y0 + H / 2))
    arrow(ax, (xs[-1] + W, y0 + H / 2), (16.25, y0 + H / 2))
    ax.text(16.3, y0 + H / 2 + 0.12, "ȳᵢ", fontsize=12, ha="right", va="bottom")
    save(fig, "schematic_forward_model.png")


def schematic_pinhole_terms():
    """Two cones from the detector to the object plane (not to scale): R_i = p b/f and R_g = d (b+f)/f."""
    fig, axs = plt.subplots(1, 2, figsize=(TEXTW, 2.9))
    b, f, d, p = 3.0, 1.0, 0.36, 0.36
    for ax, kind in zip(axs, ("det", "ap")):
        ax.plot([-1.6, 1.6], [b, b], color="0.6", lw=0.7, ls="--")
        ax.plot([-1.6, 1.6], [-f, -f], color="0.6", lw=0.7, ls="--")
        ax.add_patch(Rectangle((-1.6, -0.05), 1.6 - d / 2, 0.1, color="0.6"))
        ax.add_patch(Rectangle((d / 2, -0.05), 1.6 - d / 2, 0.1, color="0.6"))
        ax.text(1.62, b, "object", va="center")
        ax.text(1.62, 0, "pinhole", va="center")
        ax.text(1.62, -f, "detector", va="center")
        ax.annotate("", xy=(-1.75, 0), xytext=(-1.75, b), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(-1.8, b / 2, "b", ha="right", va="center", fontsize=10)
        ax.annotate("", xy=(-1.75, -f), xytext=(-1.75, 0), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(-1.8, -f / 2, "f", ha="right", va="center", fontsize=10)
        if kind == "det":
            ax.add_patch(Rectangle((-p / 2, -f - 0.08), p, 0.08, color=GAMMART))
            for sg in (-1, 1):
                ax.plot([sg * p / 2, -sg * p / 2 * b / f], [-f, b], color=GAMMART, lw=1.1)
            ax.annotate("", xy=(-p / 2 * b / f, b + 0.18), xytext=(p / 2 * b / f, b + 0.18),
                        arrowprops=dict(arrowstyle="<->", color=GAMMART, lw=1.0))
            ax.text(0, b + 0.28, r"detector term  $R_i = p\,b/f$", color=GAMMART, ha="center", fontsize=9)
            ax.text(0.3, -f - 0.22, "pixel p", color=GAMMART, ha="center", va="top")
        else:
            ax.plot(0, -f, "o", color=VERM, ms=4)
            for sg in (-1, 1):
                ax.plot([0, sg * d / 2 * (b + f) / f], [-f, b], color=VERM, lw=1.1)
            ax.annotate("", xy=(-d / 2 * (b + f) / f, b + 0.18), xytext=(d / 2 * (b + f) / f, b + 0.18),
                        arrowprops=dict(arrowstyle="<->", color=VERM, lw=1.0))
            ax.text(0, b + 0.28, r"aperture term  $R_g = d\,(b+f)/f$", color=VERM, ha="center", fontsize=9)
            ax.text(0.3, 0.12, "d", color=VERM, fontsize=10)
        ax.set_xlim(-2.1, 2.3)
        ax.set_ylim(-f - 0.45, b + 0.6)
        ax.axis("off")
    save(fig, "schematic_pinhole_terms.png")


def fwhm_of(x, y):
    h = y.max() / 2
    a = np.flatnonzero(y >= h)
    lo, hi = a[0], a[-1]
    xl = np.interp(h, [y[lo - 1], y[lo]], [x[lo - 1], x[lo]])
    xr = np.interp(h, [y[hi + 1], y[hi]], [x[hi + 1], x[hi]])
    return xr - xl


def schematic_box_vs_gauss():
    Rg, Ri = 9.20, 11.08
    x = np.linspace(-30, 30, 60001)
    dx = x[1] - x[0]
    b1 = (np.abs(x) <= Rg / 2).astype(float)
    b2 = (np.abs(x) <= Ri / 2).astype(float)
    conv = np.convolve(b1, b2, mode="same") * dx
    sig = np.hypot(Rg, Ri) / (2 * np.sqrt(2 * np.log(2)))
    g = np.exp(-x**2 / (2 * sig**2))
    fb, fg = fwhm_of(x, conv), fwhm_of(x, g)
    NUM["box_conv_fwhm_mm"] = round(float(fb), 2)
    NUM["gauss_quadrature_fwhm_mm"] = round(float(fg), 2)
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    ax.plot(x, b1, color=VERM, lw=0.9, ls=":", label=f"aperture term: box {Rg:.2f} mm")
    ax.plot(x, b2, color=GAMMART, lw=0.9, ls=":", label=f"detector term: box {Ri:.2f} mm")
    ax.plot(x, conv / conv.max(), color="k", lw=1.6, label=f"box ⊗ box: FWHM {fb:.1f} mm")
    ax.plot(x, g, color=PURPLE, lw=1.6, ls="--", label=f"quadrature √(R_g² + Rᵢ²): FWHM {fg:.1f} mm")
    ax.axhline(0.5, color="0.7", lw=0.5)
    ax.set_xlim(-16, 16)
    ax.set_ylim(0, 1.12)
    ax.set_xlabel("position at the object (mm)")
    ax.set_ylabel("response / peak")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    save(fig, "schematic_box_vs_gauss.png")


# ----------------------------------------------------------------------------------------------- WP1, WP3
def fig_wp1():
    d = json.loads((PO / "out/wp1/wp1_results.json").read_text())
    th = [0, 15, 30, 35]
    keys = [f"t{t}_p0_v2" for t in th]
    fig, axs = plt.subplots(1, 2, figsize=(TEXTW, 2.8), gridspec_kw={"width_ratios": [1.05, 1]})
    ax = axs[0]
    for pix, mk, ls, lab in (("conv", "o", "-", "converging"), ("para", "s", "--", "parallel 2 mm")):
        for code in ("gammart", "gate"):
            col = GAMMART if code == "gammart" else GATE
            y = [d[k]["spot"][code][f"fwhm_{pix}_rad"] for k in keys]
            ax.plot(th, y, ls=ls, marker=mk, color=col, ms=5 if code == "gammart" else 8,
                    mfc=col if code == "gammart" else "none", lw=1.2 if code == "gammart" else 0.8,
                    label=f"{lab}, {'gammart' if code == 'gammart' else 'GATE'}")
    ax.set_xlabel("incidence angle θ (deg)")
    ax.set_ylabel("radial spot FWHM at mid depth (mm)")
    ax.set_title("Spot width in the plane of incidence (w = 1.215 mm)")
    ax.legend()
    ax = axs[1]
    names, r, e = [], [], []
    for k, v in d.items():
        m = v["meta"]
        w = {0: "0.556", 2: "1.215"}[int(m["variant"])]
        names.append(f"θ {int(m['theta'])}°" + (f", φ {int(m['phi'])}°" if m["phi"] else "") + f", w = {w} mm")
        r.append(v["window"]["ratio_gate_over_gammart"])
        e.append(v["window"]["err"])
    yy = np.arange(len(names))[::-1]
    ax.errorbar(r, yy, xerr=e, fmt="o", color=GATE, ms=4, capsize=2)
    ax.axvline(1, color=REF, lw=0.7)
    ax.set_yticks(yy, names, fontsize=7.5)
    ax.set_xlabel("GATE / gammart (in-window counts, ±1σ)")
    ax.set_title(f"Window agreement, {len(names)} cases")
    NUM["wp1_cases"] = len(names)
    NUM["wp1_ratio_range"] = [round(min(r), 4), round(max(r), 4)]
    fig.tight_layout()
    save(fig, "wp1_spot_window.png")


def fig_wp3():
    d = json.loads((PO / "out/wp3/wp3_results.json").read_text())
    phs = ["jaszczak", "derenzo", "triple"]
    lab = {"jaszczak": "Jaszczak", "derenzo": "Derenzo", "triple": "triple line"}
    fig, axs = plt.subplots(1, 2, figsize=(TEXTW, 2.6))
    x = np.arange(3)
    ax = axs[0]
    for off, key, mk, name in ((-0.12, "gate_fluo_off_vs_gammart", "o", "fluorescence off"),
                               (0.12, "gate_fluo_on_vs_gammart", "s", "fluorescence on")):
        r = [d[p][key]["window_total"]["ratio"] for p in phs]
        e = [d[p][key]["window_total"]["ratio_err"] for p in phs]
        ax.errorbar(x + off, r, yerr=e, fmt=mk, color=GATE, mfc=GATE if mk == "o" else "none", ms=6, capsize=2, label=name)
    ax.axhline(1, color=REF, lw=0.7)
    ax.axhline(0.98, color=REF, lw=0.6, ls=":")
    ax.text(2.45, 0.9805, "0.98", va="bottom", ha="right")
    ax.set_xticks(x, [lab[p] for p in phs])
    ax.set_ylabel("GATE / gammart,\nin-window counts per photon")
    ax.legend(loc="center right")
    ax.set_title("Window totals")
    ax = axs[1]
    tg = [100 * d[p]["gate_fluo_off_vs_gammart"]["triangle"]["fraction_gate"] for p in phs]
    tm = [100 * d[p]["gate_fluo_off_vs_gammart"]["triangle"]["fraction_gammart"] for p in phs]
    ax.bar(x - 0.18, tg, 0.34, color=GATE, label="GATE")
    ax.bar(x + 0.18, tm, 0.34, color=GAMMART, label="gammart")
    for i in range(3):
        ax.text(x[i], max(tg[i], tm[i]) + 0.2, f"{tg[i]:.2f} / {tm[i]:.2f}", ha="center", fontsize=7.5)
    ax.set_xticks(x, [lab[p] for p in phs])
    ax.set_ylabel("edge strip (% of window events)")
    ax.set_ylim(0, 9)
    ax.legend(loc="upper left")
    ax.set_title("Edge strip (fluorescence off)")
    NUM["wp3_photopeak_band_off"] = {p: round(d[p]["gate_fluo_off_vs_gammart"]["spectrum_bands"]["126-154"]["ratio"], 4)
                                     for p in phs}
    fig.tight_layout()
    save(fig, "wp3_checkpoint.png")


# ----------------------------------------------------------------------------------------------- WP4
WIN = {"main": (126.0, 154.0), "lower": (120.4, 126.0), "upper": (154.0, 159.6)}
CLS = (("primary", VERM), ("phantom-scattered", ORANGE), ("pre-crystal scattered", PURPLE))


def fig_scatter_spectra():
    phs = ["jaszczak", "derenzo", "triple"]
    lab = {"jaszczak": "Jaszczak", "derenzo": "Derenzo", "triple": "triple line"}
    fig, axs = plt.subplots(1, 3, figsize=(TEXTW, 2.7), sharey=True)
    out = {}
    for ax, p in zip(axs, phs):
        t = np.load(PO / f"out/wp4/truth/{p}.npz")
        sp = t["spec"].sum(1)  # (3, 200), 1 keV bins of the blurred energy
        e = np.arange(200) + 0.5
        for c, (name, col) in enumerate(CLS):
            ax.step(e, np.where(sp[c] > 0, sp[c] / sp.sum(), np.nan), where="mid", color=col, lw=1.2, label=name)
        for w, (lo, hi) in WIN.items():
            ax.axvspan(lo, hi, color="0.9" if w == "main" else "#d5efe5", lw=0, zorder=0)
        ax.set_yscale("log")
        ax.set_xlim(100, 172)
        ax.set_ylim(1e-6, 0.1)
        ax.set_xlabel("blurred energy (keV)")
        ax.set_title(lab[p])
        frac = {}
        for w in WIN:
            m = t[w].sum((1, 2))
            frac[w] = {"primary": m[0] / m.sum(), "phantom": m[1] / m.sum(), "precrystal": m[2] / m.sum(), "total": m.sum()}
        tew = (t["lower"].sum() / (WIN["lower"][1] - WIN["lower"][0]) + t["upper"].sum() / (WIN["upper"][1] - WIN["upper"][0])) \
            * (WIN["main"][1] - WIN["main"][0]) / 2
        scat = t["main"][1:].sum()
        out[p] = {w: {k: (round(100 * v, 2) if k != "total" else float(v)) for k, v in frac[w].items()} for w in frac}
        out[p]["tew_total_over_true_scatter"] = round(float(tew / scat), 4)
        out[p]["upper_scatter_share_of_main_scatter_pct"] = round(100 * float(t["upper"][1:].sum() / scat), 2)
        out[p]["lower_scatter_share_of_main_scatter_pct"] = round(100 * float(t["lower"][1:].sum() / scat), 2)
        ax.text(140, 2.2e-6, "main", ha="center", fontsize=7.5)
        ax.text(123.2, 2.2e-6, "L", ha="center", fontsize=7.5)
        ax.text(156.8, 2.2e-6, "U", ha="center", fontsize=7.5)
    axs[0].set_ylabel("fraction per 1 keV\n(true E ≥ 100 keV)")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    NUM["truth_windows"] = out
    save(fig, "wp4_scatter_spectra.png")


def fig_kernel():
    from wp2_kernel import kernel
    old = np.load(PO / "out/wp2/mc_sphere_water.npz")
    new = np.load(PO / "out/wp4/kernel_sphere140.npz")
    empty = {}
    for name, d in (("old", old), ("new", new)):
        empty[name] = [int((kernel(d, v)[1][:625] == 0).sum()) for v in range(4)]
        empty[name + "_min_count"] = [int(kernel(d, v)[1][:625].min()) for v in range(4)]
    NUM["kernel_empty_rows"] = empty
    fig, axs = plt.subplots(1, 2, figsize=(5.2, 2.7))
    from matplotlib.colors import LogNorm
    ims = []
    for ax, d, t in zip(axs, (old, new), ("before (WP2): water sphere,\nr = 80 mm", "after (WP4): sphere in air,\nr = 140 mm")):
        n = kernel(d, 0)[1][:625].reshape(25, 25).astype(float)
        m = np.ma.masked_where(n == 0, n)
        cmap = plt.get_cmap("Greys").copy()
        cmap.set_bad(VERM)
        ims.append(ax.imshow(m.T, origin="lower", cmap=cmap, norm=LogNorm(1e1, 1e7), extent=(0.5, 25.5, 0.5, 25.5)))
        ax.set_title(t)
        ax.set_xlabel("pixel column")
        ax.text(13, -7.5, f"empty rows: {int((n == 0).sum())} of 625", ha="center",
                color=VERM if (n == 0).any() else "k")
    axs[0].set_ylabel("pixel row")
    fig.colorbar(ims[1], ax=axs, shrink=0.85, label="first interactions per pixel")
    save(fig, "wp4_kernel_coverage.png")


def load_rec(ph, step, ds, it):
    return np.load(PO / f"out/wp4/recon/{ph}_{step}_{ds}_it{it:02d}.npy").astype(np.float64).reshape(N, N, N)


def ksl(z0, z1):
    return np.flatnonzero((AX >= z0) & (AX <= z1))


POST_FWHM = 6.0  # mm, 3D Gaussian post-filter applied to every displayed image (metrics stay unfiltered)


def post(img):
    return gaussian_filter(img, POST_FWHM / (2 * np.sqrt(2 * np.log(2))) / V)


def jaszczak_cold_parts():
    sys.path.insert(0, str(Q / "qmirt-gate-10-sim/packages/phantom_studio/src"))
    from phantom_studio.core import models as pm
    sp = pm.Spec.from_dict(json.loads((PO / "out/wp3/specs/jaszczak.json").read_text()))
    parts, _ = pm.build(sp.phantom, sp.options)
    return [(sp.pose.to_world(np.array(p.center, float)), p.radius, p.role, getattr(p, "length", 0.0))
            for p in parts if p.role in ("sphere", "rod", "stem")]


def jaszczak_background(z0, cold):
    """Uniform background of the slice at z0: water (ρ < 62 mm) more than 3 mm from any rod or stem and more than
    6 mm from any sphere (the background definitions of wp3_metrics.jaszczak_metrics)."""
    X, Y = np.meshgrid(AX, AX, indexing="ij")
    d_cyl, d_sph = np.full(X.shape, 1e9), np.full(X.shape, 1e9)
    for c, r, role, L in cold:
        if role == "sphere":
            d_sph = np.minimum(d_sph, np.sqrt((X - c[0]) ** 2 + (Y - c[1]) ** 2 + (z0 - c[2]) ** 2) - r)
        elif abs(z0 - c[2]) <= L / 2:
            d_cyl = np.minimum(d_cyl, np.hypot(X - c[0], Y - c[1]) - r)
    return (X**2 + Y**2 < 62.0**2) & (d_cyl > 3.0) & (d_sph > 6.0)


COLS = [("air", "no correction"), ("ac_k", "AC + K"), ("ac_k_tew", "AC + K + TEW"), ("ac_k", "primary-only reference\n(AC + K)")]
ROWS = [("gate_on", "GATE (fluor. on)"), ("gammart", "gammart MC")]
VMAX = 1.3


def slices_figure(name, blocks, width=6.4):
    """blocks: (row title, getter(step, ds) -> 2D normalised image, half-width mm, scale-bar mm)."""
    nr = 2 * len(blocks)
    fig = plt.figure(figsize=(width, 1.45 * nr + 0.95))
    gs = fig.add_gridspec(nr + 1, 4, wspace=0.04, hspace=0.06, height_ratios=[1] * nr + [0.09])
    ext = (AX[0] - 1, AX[-1] + 1, AX[0] - 1, AX[-1] + 1)
    for b, (btitle, get, half, bar) in enumerate(blocks):
        for r, (ds, dsl) in enumerate(ROWS):
            for c, (st, stl) in enumerate(COLS):
                ax = fig.add_subplot(gs[2 * b + r, c])
                ax.set_xticks([])
                ax.set_yticks([])
                if b == 0 and r == 0:
                    ax.set_title(stl, fontsize=8.5)
                if c == 0:
                    ax.set_ylabel(dsl, fontsize=8.5)
                    if r == 0:
                        ax.text(-0.3, 0.0, btitle, transform=ax.transAxes, rotation=90, ha="center", va="center",
                                fontsize=9.5, weight="bold")
                if c == 3 and ds != "gammart":
                    for sp in ax.spines.values():
                        sp.set_visible(False)
                    ax.text(0.5, 0.5, "WP3 GATE run:\nno scatter labels\nstored", ha="center", va="center", transform=ax.transAxes,
                            fontsize=8, color="0.35")
                    continue
                img = get(st, "gammart_primary" if c == 3 else ds)
                im = ax.imshow(np.clip(img, 0, VMAX).T, origin="lower", cmap="gray", vmin=0, vmax=VMAX, extent=ext,
                               interpolation="nearest")
                ax.set_xlim(-half, half)
                ax.set_ylim(-half, half)
                if c == 0:
                    x0 = -half * 0.72
                    ax.plot([x0, x0 + bar], [-half * 0.86] * 2, color="w", lw=2.5)
                    ax.text(x0 + bar / 2, -half * 0.8, f"{bar} mm", color="w", ha="center", va="bottom", fontsize=7.5)
    cax = fig.add_subplot(gs[nr, 1:3])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("activity / background mean (6 mm FWHM post-filter, clipped at 1.3)", fontsize=8)
    save(fig, name)


def fig_slices():
    it = 64
    phd = np.load(Q / "qmirt-gate-10-sim/dev/python/design_scorecard/phantoms.npz")
    rods8 = phd["derenzo_sector_8_rods"]
    ks_d = ksl(-30, 30)
    ks_t = ksl(-20, 20)
    X2, Y2 = np.meshgrid(AX, AX, indexing="ij")
    near0 = np.hypot(X2, Y2) <= 5.0

    def der(st, ds):
        img2 = post(load_rec("derenzo", st, ds, it))[:, :, ks_d].mean(2)
        return img2 / map_coordinates(img2, [(rods8[:, 0] - AX[0]) / V, (rods8[:, 1] - AX[0]) / V], order=1).mean()

    def tri(st, ds):
        img2 = post(load_rec("triple", st, ds, it))[:, :, ks_t].mean(2)
        return img2 / img2[near0].max()

    cold = jaszczak_cold_parts()
    k_rod, k_sph = ksl(27.9, 30.1), ksl(-29.5, -26.5)  # z = 29 mm; z = -29 and -27 mm around the spheres at -28 mm
    bg_rod, bg_sph = jaszczak_background(29.0, cold), jaszczak_background(-28.0, cold)

    def jr(st, ds):
        img2 = post(load_rec("jaszczak", st, ds, it))[:, :, k_rod].mean(2)
        return img2 / img2[bg_rod].mean()

    def js(st, ds):
        img2 = post(load_rec("jaszczak", st, ds, it))[:, :, k_sph].mean(2)
        return img2 / img2[bg_sph].mean()

    NUM["slices"] = {"iterations": it, "post_filter_fwhm_mm": POST_FWHM,
                     "derenzo_z_mm": [float(AX[ks_d][0]), float(AX[ks_d][-1])],
                     "triple_z_mm": [float(AX[ks_t][0]), float(AX[ks_t][-1])],
                     "jaszczak_rod_z_mm": AX[k_rod].tolist(), "jaszczak_sphere_z_mm": AX[k_sph].tolist(),
                     "jaszczak_background_voxels": {"rods": int(bg_rod.sum()), "spheres": int(bg_sph.sum())},
                     "derenzo_norm_rods": int(len(rods8))}
    slices_figure("wp4_slices_derenzo_triple.png", [("Derenzo", der, 80, 20), ("triple line", tri, 14, 5)])
    slices_figure("wp4_slices_jaszczak.png", [("rods, z = 29 mm", jr, 72, 20), ("spheres, z = −28 mm", js, 72, 20)])


def fig_profile():
    it = 128
    X, Y, Z = np.meshgrid(AX, AX, AX, indexing="ij")
    r = np.hypot(X, Y)
    slab = (Z > -90) & (Z < -50)
    edges = np.arange(0, 60.01, 5)
    rc = (edges[:-1] + edges[1:]) / 2
    fig, ax = plt.subplots(figsize=(4.6, 2.7))
    out = {}
    for st, ds, col, ls, mk, lw, lab in (("air", "gate_on", GATE, ":", "o", 1.3, "GATE, no correction"),
                                         ("ac", "gate_on", GATE, "--", "s", 1.3, "GATE, AC"),
                                         ("ac_k_tew", "gate_on", VERM, "-", "D", 1.3, "GATE, AC + K + TEW"),
                                         ("ac_k", "gammart_primary", REF, "-", None, 0.8, "reference (primary only)")):
        img = load_rec("jaszczak", st, ds, it)
        norm = img[slab & (r < 60)].mean()
        prof = [img[slab & (r >= a) & (r < b)].mean() / norm for a, b in zip(edges[:-1], edges[1:])]
        ax.plot(rc, prof, ls=ls, marker=mk, color=col, ms=4, lw=lw, label=lab)
        out[f"{st}/{ds}"] = [round(float(v), 3) for v in prof]
    ax.axhline(1, color="0.7", lw=0.5)
    ax.set_xlabel("radius ρ from the axis (mm), 5 mm rings")
    ax.set_ylabel("ring mean / mean over ρ < 60 mm")
    ax.legend(fontsize=7)
    NUM["jaszczak_profile_it128"] = {"ring_centres_mm": rc.tolist(), **out}
    save(fig, "wp4_uniform_profile.png")


def fig_ladder():
    d = json.loads((PO / "out/wp4/wp4_results.json").read_text())
    steps = [("air", "none"), ("ac", "AC"), ("ac_k", "AC+K"), ("ac_k_tew", "+TEW"), ("ac_k_truth", "+true s")]
    panels = [("derenzo", "vp_5mm", "Derenzo V/P, 5 mm rods ↓"), ("derenzo", "vp_6mm", "Derenzo V/P, 6 mm rods ↓"),
              ("derenzo", "vp_7mm", "Derenzo V/P, 7 mm rods ↓"),
              ("jaszczak", "sphere_contrast.25.4", "25.4 mm sphere contrast ↑"),
              ("jaszczak", "rod_contrast.12.7", "12.7 mm rod contrast ↑"),
              ("jaszczak", "rod_contrast.9.5", "9.5 mm rod contrast ↑")]
    fig, axs = plt.subplots(2, 3, figsize=(TEXTW, 4.5))
    x = np.arange(len(steps))
    for ax, (ph, m, t) in zip(axs.ravel(), panels):
        T = d[ph]["it128"]
        ref = T["ac_k/gammart_primary"][m]["value"]
        for off, ds, col, mk, lab in ((-0.13, "gate_on", GATE, "o", "GATE (fluorescence on)"),
                                      (0.13, "gammart", GAMMART, "s", "gammart MC")):
            y = [T[f"{s}/{ds}"][m]["value"] for s, _ in steps]
            e = [T[f"{s}/split_sd"].get(m, 0) for s, _ in steps]
            ax.errorbar(x + off, y, yerr=e, fmt=mk, color=col, ms=5, capsize=2, lw=0.9, label=lab)
        ax.axhline(ref, color=REF, ls="--", lw=0.9, label="primary-only reference")
        ax.set_xticks(x, [s[1] for s in steps], fontsize=7.5)
        ax.set_title(t)
        ax.axvspan(2.5, 4.5, color="#d5efe5", alpha=0.6, lw=0, zorder=0)
    axs[0, 0].set_ylabel("valley / peak")
    axs[1, 0].set_ylabel("Jaszczak contrast")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, "wp4_ladder.png")


# ----------------------------------------------------------------------------------------------- resolution, apertures
def analytic_module():
    sys.path.insert(0, str(ANA))
    import analytic as A  # read-only import; nothing is written in that folder (dont_write_bytecode)
    return A


def fig_terms():
    """Redrawn from 2026-10-28_analytic_resolution/analytic.py fig_terms (same formulas), house colours."""
    A = analytic_module()
    widths, _, _, _ = A.geometry()
    b = np.linspace(50, 250, 200)
    fig, axes = plt.subplots(1, 2, figsize=(TEXTW, 2.9), sharey=True)
    for ax, (det, coef) in zip(axes, A.PITCH.items()):
        for name, w in zip(A.NAMES, widths):
            rg = A.d_res(w) * (b + A.F_MM) / A.F_MM
            ax.plot(b, np.hypot(rg, coef * b), color=APC[name], lw=1.6, label=f"{name} (w = {w:.3f} mm)")
            ax.plot(b, rg, color=APC[name], lw=0.9, ls=":")
        ax.plot(b, coef * b, color="k", lw=1.8, ls="--", label="detector term alone")
        ax.axvline(149.6, color="0.5", lw=0.7)
        if det.startswith("par"):
            ax.text(147, 21.0, "centre", color="0.4", ha="right")
        ax.set_title(f"{det} pixels (Rᵢ = {'2b/27' if det.startswith('par') else '2b/35'})")
        ax.set_xlabel("pinhole-to-point distance b (mm)")
        ax.set_ylim(0, 22)
    axes[0].set_ylabel("projection FWHM at the object (mm)")
    axes[1].legend(loc="upper left", fontsize=7)
    axes[0].text(250, 1.0, "dotted: aperture term alone", color="0.35", fontsize=7.5, ha="right")
    fig.tight_layout()
    save(fig, "terms_vs_b.png")


def fig_information():
    """Redrawn from analytic.py fig_information (same functions and point), house colours."""
    A = analytic_module()
    widths, variant, ph, rot = A.geometry()
    k, b, cos, r, phi = A.modules_seeing(np.array([60 * np.cos(np.radians(30)), 60 * np.sin(np.radians(30)), 25.5]), ph, rot)
    nus = np.linspace(0.005, 0.2, 200)
    fig, axes = plt.subplots(1, 2, figsize=(TEXTW, 2.9), sharey=True)
    for ax, model in zip(axes, ("gauss", "box")):
        coef = A.PITCH["converging"]
        curves = {}
        for name, w in list(zip(A.NAMES, widths)) + [("current mix", None)]:
            ww = widths[variant[k]] if w is None else np.full(len(k), w)
            rg, ri, R, g = A.terms(ww, b, cos, r, phi, coef, True)
            curves[name] = np.array([A.info(g, R, nu, rg, ri, model) for nu in nus])
        best = np.max([curves[n] for n in A.NAMES], axis=0)
        for name, c in curves.items():
            mix = name == "current mix"
            ax.plot(nus, c / best, color="k" if mix else APC[name], lw=2.0 if mix else 1.4, ls="--" if mix else "-",
                    label=name)
        for lab, nu in A.NU.items():
            ax.axvline(nu, color="0.85", lw=0.8)
            ax.text(nu + 0.001, 0.02, lab.replace(" rods", " rods"), color="0.35", ha="left", va="bottom", rotation=90, fontsize=7)
        ax.set_ylim(0, 1.1)
        ax.set_xlabel("spatial frequency (cycles/mm)")
        ax.set_title("Gaussian blur model" if model == "gauss" else "box model (aperture box ⊗ pixel box)")
    axes[0].set_ylabel("information / best pure design")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    save(fig, "information_vs_frequency.png")


def fig_phase0():
    """Redrawn from 2026-10-28_analytic_resolution/phase0/phase0.json (uniform designs, all points), with the
    sensitivity formula of Eq. (sens): ratio_mc_over_g_paix uses A_eff and cos(theta)/r^2."""
    rows = json.loads((ANA / "phase0/phase0.json").read_text())["rows"]
    u = [r for r in rows if r["design"] != "mix" and "ratio_mc_over_g_paix" in r]
    fig, ax = plt.subplots(1, 2, figsize=(TEXTW, 2.8))
    names = dict(zip(sorted({r["w"] for r in u}), "ABCD"))
    for wv, n in names.items():
        s = [r for r in u if r["w"] == wv]
        ax[0].scatter([r["theta_deg"] for r in s], [r["ratio_mc_over_g_paix"] for r in s], s=5, color=APC[n],
                      label=f"{n} (w = {wv:.3f} mm)")
        ax[1].scatter([r["Rg_formula_pen"] for r in s], [(r["Rg_mc_u"] + r["Rg_mc_v"]) / 2 for r in s], s=5, color=APC[n])
    ax[0].axhline(1, color="k", lw=0.6)
    ax[0].set_xlabel("incidence angle θ (deg)")
    ax[0].set_ylabel(r"gammart MC / $A_{eff}\cos\theta\,/\,4\pi r^2$")
    ax[0].legend(fontsize=7, markerscale=2)
    m = max(r["Rg_formula_pen"] for r in u)
    ax[1].plot([0, m], [0, m], "k", lw=0.6)
    ax[1].set_xlabel(r"formula $R_g = d_{re}\,(b+f)/f$ (mm)")
    ax[1].set_ylabel(r"gammart $R_g$ (mm)")
    fig.tight_layout()
    th = np.array([r["theta_deg"] for r in u])
    rr = np.array([r["ratio_mc_over_g_paix"] for r in u])
    lo, hi = th <= 37.0, th > 37.0
    NUM["phase0_sens_ratio"] = {"theta_max_deg": round(float(th.max()), 1),
                                "theta_le_37": [round(float(np.percentile(rr[lo], 1)), 3), round(float(np.percentile(rr[lo], 99)), 3)],
                                "theta_gt_37_min_max": [round(float(rr[hi].min()), 3), round(float(rr[hi].max()), 3)],
                                "n_modules_gt_37": int(hi.sum()), "n_total": int(len(rr))}
    save(fig, "phase0_sens_width.png")


SCL = {"uniform_0.556": ("all A", APC["A"], "-"), "uniform_0.797": ("all B", APC["B"], "-"),
       "uniform_1.215": ("all C", APC["C"], "-"), "uniform_2.007": ("all D", APC["D"], "-"),
       "current": ("current mix (index mod 4)", "k", "--"), "rings_mixed": ("rings B/C/D", "#882255", "-"),
       "assignment_best": ("best assignment (C, one B)", "#44AA99", ":")}


def fig_scorecard():
    """Redrawn from design_scorecard/r100_2026-10-26/*/scorecard.json (as 2026-10-28_brain_update fig_scorecards)."""
    sc = Q / "qmirt-gate-10-sim/dev/python/design_scorecard/r100_2026-10-26"
    cards = {n: json.loads((sc / n / "scorecard.json").read_text()) for n in SCL}
    fig, axs = plt.subplots(1, 3, figsize=(TEXTW, 2.8), sharey=True)
    for ax, rod in zip(axs, ("6", "7", "8")):
        for n, (lab, c, ls) in SCL.items():
            by = cards[n]["phantoms"]["derenzo"]["by_iteration"]
            its = sorted(by, key=int)
            ax.plot([100 * by[i][rod]["peak_cov"] for i in its], [by[i][rod]["vp_mean"] for i in its], ls=ls, color=c,
                    marker="o", ms=2.5, lw=1.1, label=lab)
        ax.axvline(2.5, color="0.4", lw=0.8, ls=(0, (2, 3)))
        ax.set_title(f"{rod} mm rods")
        ax.set_xlabel("rod-peak noise, CoV (%)")
        ax.set_xlim(0, 9.5)
    axs[0].set_ylabel("valley / peak ↓")
    axs[0].set_ylim(0, 1.25)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.08), fontsize=7)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, "scorecard_derenzo.png")


def fig_wp2b():
    d = json.loads((PO / "out/wp2b/scorecard/map_variation.json").read_text())
    m, sd = d["metrics"], d["between_map_sd"]["vp8"]
    groups = [("random (5)", [k for k in m if k.startswith("random")], "#999933"),
              ("annealed (3)", [k for k in m if k.startswith("annealed")], "#882255"),
              ("stratified (3)", [k for k in m if k.startswith("stratified")], PURPLE),
              ("index mod 4 (current)", ["current"], "k"),
              ("uniform C", ["uniform_1.215"], VERM)]
    fig, ax = plt.subplots(figsize=(5.0, 2.2))
    for k, (n, keys, c) in enumerate(groups):
        ax.plot([m[q]["vp8"] for q in keys], [k] * len(keys), "o", ms=7, color=c, mec="w", mew=1.0)
    ax.set_yticks(range(len(groups)), [g[0] for g in groups])
    ax.invert_yaxis()
    ax.axvspan(m["current"]["vp8"] - sd, m["current"]["vp8"] + sd, color="0.9", lw=0, zorder=0)
    ax.set_xlabel("V/P of the 8 mm rods at matched noise ↓")
    NUM["wp2b_between_map_sd_vp8"] = round(sd, 3)
    save(fig, "wp2b_maps.png")


if __name__ == "__main__":
    copies()
    schematic_converging()
    schematic_forward_model()
    schematic_pinhole_terms()
    schematic_box_vs_gauss()
    fig_wp1()
    fig_wp3()
    fig_scatter_spectra()
    fig_kernel()
    fig_ladder()
    fig_profile()
    fig_slices()
    fig_terms()
    fig_information()
    fig_phase0()
    fig_scorecard()
    fig_wp2b()
    for old in ("psf_C.png",):
        (IMG / old).unlink(missing_ok=True)
    (IMG / "figure_numbers.json").write_text(json.dumps(NUM, indent=1))
    print(json.dumps({k: v for k, v in NUM.items() if k not in ("jaszczak_profile_it128", "truth_windows")}, indent=1))
