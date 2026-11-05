"""New figures for the 2026-10-28 brain SPECT update (img/).

Run (no GPU, no display):
    micromamba run -n raytracing env -u DISPLAY python make_figures.py

Every number plotted is read from an analysis file or copied from a document; the source is given in
the comment of each figure function. Schematics (pipeline, helmet, module, PSF, MTF, surrogate) carry no
measured numbers and say so in their caption.
CONFIDENTIALITY: no geometry, no aperture map and no per-aperture widths are drawn (system is going commercial);
the four pinhole sizes are called A < B < C < D.
"""
import os
import json
import re
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle, Circle

HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)
ROOT = Path(f"{os.path.expanduser('~')}/Work/RPIL/QMIRT")
PY = ROOT / "qmirt-gate-10-sim/dev/python"
PO = ROOT / "pytorch-optix"

BLUE, ORANGE, AQUA, PURPLE, RED = "#2a78d6", "#eb6834", "#1baf7a", "#8a5cd1", "#d03a3a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 14, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.titlesize": 15, "axes.titleweight": "bold",
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
                     "lines.linewidth": 2})


def save(fig, name, dpi=150):
    fig.savefig(OUT / name, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def box(ax, xy, w, h, text, fc="#eaf1fb", ec=BLUE, fs=12, bold=False):
    ax.add_patch(FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.6))
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color=INK)


def arrow(ax, p, q, color=INK2):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=18, lw=1.8, color=color))


# ------------------------------------------------------------------------------------------------ pipeline
def fig_pipeline():
    """Schematic: how data and model are made (no numbers)."""
    fig, ax = plt.subplots(figsize=(15, 6.2))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    # top row: data
    ax.text(0.1, 5.85, "DATA  (what the scanner would measure)", fontsize=13, color=ORANGE, fontweight="bold")
    box(ax, (0.2, 4.3), 2.6, 1.2, "Phantom\n(Jaszczak, Derenzo,\ntriple line, XCAT)", "#fdece4", ORANGE)
    box(ax, (3.6, 4.3), 3.2, 1.2, "GATE 10 Monte Carlo\nOSPool / Expanse / ERIS\n15 mCi, 15 min", "#fdece4", ORANGE)
    box(ax, (7.6, 4.3), 3.0, 1.2, "List-mode events\nmain window, 140 keV\n(unscattered tag)", "#fdece4", ORANGE)
    arrow(ax, (2.8, 4.9), (3.6, 4.9), ORANGE)
    arrow(ax, (6.8, 4.9), (7.6, 4.9), ORANGE)
    # bottom row: model
    ax.text(0.1, 3.0, "MODEL  (system response matrix, SRM)", fontsize=13, color=BLUE, fontweight="bold")
    box(ax, (0.2, 1.3), 3.0, 1.3, "GATE SRM, 1e14 primaries\n4.9e5 core-hours\n(reference)", "#eaf1fb", BLUE)
    box(ax, (3.9, 1.3), 3.0, 1.3, "gammart SRM (OptiX)\ndeterministic, 1.35 min\n(new)", "#e3f6ee", AQUA)
    box(ax, (7.6, 1.3), 3.0, 1.3, "Attenuation factors\n(ray-traced, per phantom)", "#eaf1fb", BLUE)
    # recon
    box(ax, (11.2, 2.6), 3.6, 1.6, "OSEM, 8 module subsets\nattenuation in the model\npost-filter", "#efe7fa", PURPLE, bold=True)
    arrow(ax, (10.6, 4.7), (11.6, 4.2), ORANGE)
    arrow(ax, (3.2, 1.95), (3.9, 1.95), BLUE)
    arrow(ax, (10.6, 1.95), (11.6, 2.6), BLUE)
    ax.text(5.4, 0.85, "same matrix layout: the two SRMs are interchangeable in the reconstruction", fontsize=11, color=INK2, ha="center")
    arrow(ax, (6.9, 1.95), (7.6, 1.95), AQUA)
    box(ax, (11.2, 0.4), 3.6, 1.3, "Image: contrast, noise,\nFWHM, V/P, recovery", "#fcfcfb", INK2)
    arrow(ax, (13.0, 2.6), (13.0, 1.7), PURPLE)
    save(fig, "pipeline.png")


# ------------------------------------------------------------------------------------------------ helmet
def fig_helmet():
    """Schematic only (not the real layout): modules around a head, four sizes of pinhole."""
    fig, axs = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1.0, 1.2]})
    ax = axs[0]
    ax.set_aspect("equal")
    ax.axis("off")
    th = np.linspace(-20, 200, 17)
    cols = [BLUE, ORANGE, AQUA, PURPLE]
    ax.add_patch(plt.Circle((0, 0), 1.0, fc="#f1ece4", ec=INK2, lw=1.5))
    ax.text(0, 0, "head", ha="center", va="center", color=INK2)
    for i, t in enumerate(th):
        a = np.deg2rad(t)
        c, s = np.cos(a), np.sin(a)
        # crystal plate and pinhole
        p0 = np.array([2.3 * c, 2.3 * s])
        n = np.array([-s, c])
        tpt = np.array([c, s])
        pts = [p0 + n * 0.28 + tpt * 0.15, p0 - n * 0.28 + tpt * 0.15, p0 - n * 0.28 - tpt * 0.15, p0 + n * 0.28 - tpt * 0.15]
        ax.add_patch(Polygon(pts, fc=cols[i % 4], ec=INK, lw=0.8, alpha=0.9))
        pin = np.array([1.8 * c, 1.8 * s])
        ax.plot(*pin, "o", color=INK, ms=3)
        ax.plot([p0[0] - tpt[0] * 0.15, pin[0]], [p0[1] - tpt[1] * 0.15, pin[1]], color=cols[i % 4], lw=0.6, alpha=0.6)
    ax.set_xlim(-2.8, 2.8)
    ax.set_ylim(-1.5, 2.9)
    ax.set_title("A helmet of pinhole modules (schematic)")
    ax.text(0, -1.25, "colour = pinhole size A, B, C, D; real system: 73 modules", ha="center", fontsize=11, color=INK2)

    ax = axs[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("One module (schematic, not to scale)")
    # source, pinhole plate, crystal
    ax.add_patch(Polygon([[1.0, 5.2], [3.7, 5.2], [3.7, 4.0], [4.6, 4.0], [4.6, 4.2], [5.4, 4.2], [5.4, 4.0], [6.3, 4.0], [6.3, 5.2], [9.0, 5.2],
                          [9.0, 4.9], [1.0, 4.9]], fc="none", ec="none"))
    ax.add_patch(Polygon([[2.2, 3.3], [4.5, 3.3], [5.0, 3.0], [5.5, 3.3], [7.8, 3.3], [7.8, 2.6], [2.2, 2.6]], fc="#cfd5dc", ec=INK2))
    ax.text(0.0, 2.0, "tungsten knife-edge\ncollimator", fontsize=11, color=INK2, va="center")
    ax.add_patch(Rectangle((2.8, 0.7), 4.4, 0.6, fc="#dbe8f8", ec=BLUE, lw=1.6))
    for k in range(26):
        ax.plot([2.8 + 4.4 * k / 25] * 2, [0.7, 1.3], color=BLUE, lw=0.4)
    ax.text(0.0, 1.0, "CsI(Tl)\n25 x 25 pixels", fontsize=11, color=BLUE, va="center")
    ax.plot(5.0, 3.0, "o", color=INK, ms=7)
    ax.text(5.15, 3.15, "pinhole", fontsize=11)
    ax.plot(6.2, 5.3, "o", color=ORANGE, ms=11)
    ax.text(6.4, 5.4, "emitting voxel", color=ORANGE, fontsize=12)
    ax.plot([6.2, 3.8], [5.3, 0.9], color=ORANGE, lw=1.8)
    ax.annotate("", xy=(3.8, 0.75), xytext=(3.8, 0.75))
    ax.annotate("", xy=(8.2, 5.3), xytext=(8.2, 3.0), arrowprops=dict(arrowstyle="<->", color=INK2))
    ax.text(8.4, 4.1, "b", fontsize=14, color=INK2)
    ax.annotate("", xy=(8.2, 3.0), xytext=(8.2, 1.0), arrowprops=dict(arrowstyle="<->", color=INK2))
    ax.text(8.4, 1.9, "f", fontsize=14, color=INK2)
    ax.text(0.2, -0.2, "image on the detector: inverted, scaled by f / b.\nLarger b = wider field of view, smaller image of a point.",
            fontsize=10.5, color=INK2)
    save(fig, "helmet_schematic.png")


# ------------------------------------------------------------------------------------------------ classic formulas
def fig_classic():
    """Classic projection resolution against radius, parsed from resolution_theory.md (table, 'uniform' plane).
    Columns: best single module (nominal / with penetration), count-weighted (nominal / with penetration)."""
    p = PY / "brain_phantom_recon/osem_reference_2026-10-15/resolution/resolution_theory.md"
    rows = []
    for ln in p.read_text().splitlines():
        c = [x.strip() for x in ln.strip("|").split("|")]
        if len(c) >= 9 and c[0] == "uniform":
            rows.append([float(c[1])] + [float(c[i]) for i in (4, 5, 6, 7)])
    r = np.array(rows)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(r[:, 0], r[:, 1], "o--", color=BLUE, label="best single module, nominal")
    ax.plot(r[:, 0], r[:, 2], "o-", color=BLUE, label="best single module, + penetration")
    ax.plot(r[:, 0], r[:, 3], "s--", color=ORANGE, label="count-weighted, nominal")
    ax.plot(r[:, 0], r[:, 4], "s-", color=ORANGE, label="count-weighted, + penetration")
    ax.set_xlabel("distance from the axis (mm)")
    ax.set_ylabel("projection resolution FWHM (mm)")
    ax.set_ylim(0, 17)
    ax.grid(True, color=GRID)
    ax.legend(fontsize=11, loc="center right")
    ax.set_title("Classic formula, uniform plane (no SRM, no recon)")
    save(fig, "classic_resolution.png")
    return r


# ------------------------------------------------------------------------------------------------ WP0
def fig_wp0():
    """GATE / gammart singles ratio per energy band and GATE variant: paper2_plan.md 'WP0 results' table
    (data out/wp0/bands_t2.json)."""
    bands = ["34-50 keV", "60-90 keV", "90-100 keV", "126-154 keV\n(photopeak window)"]
    data = {"air world, option4": ([0.877, 3.76, 1.94, 1.003], [0.016, 0.10, 0.04, 0.003]),
            "vacuum, option4": ([0.891, 1.39, 0.95, 1.007], [0.016, 0.06, 0.03, 0.003]),
            "vacuum, Livermore": ([0.918, 1.57, 0.94, 1.000], [0.017, 0.06, 0.03, 0.003]),
            "vacuum, Standard (no Doppler)": ([0.964, 0.96, 0.95, 1.010], [0.017, 0.05, 0.03, 0.003])}
    cols = [RED, BLUE, PURPLE, AQUA]
    fig, ax = plt.subplots(figsize=(10.5, 5))
    x = np.arange(4)
    for k, ((n, (v, e)), c) in enumerate(zip(data.items(), cols)):
        ax.errorbar(x + (k - 1.5) * 0.15, v, yerr=e, fmt="o", color=c, capsize=3, label=n)
    ax.axhline(1, color=INK2, lw=1)
    ax.set_xticks(x, bands)
    ax.set_yscale("log")
    ax.set_yticks([0.8, 1, 2, 4], ["0.8", "1", "2", "4"])
    ax.set_ylabel("GATE / gammart singles")
    ax.grid(True, axis="y", color=GRID)
    ax.legend(fontsize=11, loc="upper left")
    ax.set_title("WP0: the excess below the window is room air and Doppler")
    save(fig, "wp0_ratios.png")


# ------------------------------------------------------------------------------------------------ WP2b map variation
def fig_wp2b():
    """V/P 8 mm per aperture-placement map: paper2_plan.md, 'WP2b map-to-map variation' table (ERIS 6162111, 6138007)."""
    groups = [("random p05-p95 (5)", [0.506, 0.532, 0.478, 0.438, 0.527], INK2),
              ("annealed (3)", [0.509, 0.471, 0.483], BLUE),
              ("stratified (3)", [0.534, 0.478, 0.510], PURPLE),
              ("index mod 4 (current)", [0.484], ORANGE),
              ("uniform (one size, C)", [0.414], AQUA)]
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    for k, (n, v, c) in enumerate(groups):
        ax.plot(v, [k] * len(v), "o", ms=11, color=c, mec=SURF, mew=1.5)
    ax.set_yticks(range(len(groups)), [g[0] for g in groups])
    ax.invert_yaxis()
    ax.set_xlabel("V/P of the 8 mm rods at matched noise (lower is better); shaded: +-1 between-map SD (0.039) around index mod 4")
    ax.grid(True, axis="x", color=GRID)
    ax.axvspan(0.484 - 0.039, 0.484 + 0.039, color=ORANGE, alpha=0.12)
    ax.set_title("WP2b: where the sizes sit matters little; uniform beats every mixed map")
    save(fig, "wp2b_maps.png")


# ------------------------------------------------------------------------------------------------ resolution measures
def fig_resolution_measures():
    """Measured numbers of resolution_consistency_plan.md (table 'Measured so far'); ranges are min-max of the quoted values."""
    items = [  # label, lo, hi, colour, note
        ("Triple line, 2D Gaussian fit (centre, 200 -> 1000 it)", 0.5, 1.4, AQUA),
        ("Triple line, NEMA FWHM (grid floor, 50-1000 it)", 3.5, 3.5, AQUA),
        ("Jaszczak cold spheres, fitted FWHM (1600 -> 200 it)", 5.3, 10.4, ORANGE),
        ("Derenzo, equivalent Gaussian (4-7 mm sectors, 1000 -> 200 it)", 4.3, 7.0, BLUE),
        ("Ideal LIR half-max, noiseless matrix (alpha-dependent; r = 95 -> 0)", 6.7, 10.9, PURPLE),
        ("Classic formula: best single module (+ penetration)", 7.6, 8.4, INK2),
        ("Classic formula: count-weighted", 12.5, 14.0, INK2),
    ]
    fig, ax = plt.subplots(figsize=(12, 5.6))
    for k, (n, lo, hi, c) in enumerate(items):
        if hi - lo < 0.05:
            ax.plot([lo], [k], "D", ms=11, color=c)
        else:
            ax.barh(k, hi - lo, left=lo, height=0.55, color=c, alpha=0.85)
        ax.text(hi + 0.25, k, f"{lo:g}" if hi == lo else f"{lo:g}-{hi:g}", va="center", fontsize=11, color=INK2)
    ax.set_yticks(range(len(items)), [i[0] for i in items], fontsize=11.5)
    ax.invert_yaxis()
    ax.set_xlabel("FWHM (mm)")
    ax.set_xlim(0, 16)
    ax.grid(True, axis="x", color=GRID)
    ax.set_title("Seven ways to say 'resolution': they measure different things")
    save(fig, "resolution_measures.png")


# ------------------------------------------------------------------------------------------------ ideal LIR profile
def fig_ideal_lir():
    """Ideal LIR (alpha = 1e-3 lambda_max), current mix, parallel pixels, at r = 0 and 60 mm: GATE matrix (Monte Carlo
    counts of 1-6 per entry), noiseless gammart matrix, and gammart Poisson-resampled to the GATE counts. Profiles are the
    mean over 12 directions through the voxel. Data: 2026-10-28_analytic_resolution/lir (lir_build.py, lir.json)."""
    from scipy.ndimage import map_coordinates

    lir = PY.parent / "reports/2026-10-28_analytic_resolution/lir"
    src = {"GATE matrix (MC counts 1-6 per entry)": (np.load(PY / "ideal_lir/ideal_lir_slices.npz"), INK2, "-"),
           "gammart matrix, noiseless": (np.load(lir / "out/current_parallel/lir_slices.npz"), BLUE, "-"),
           "gammart + GATE-like counting noise": (np.load(lir / "out_noise/current_parallel/lir_slices.npz"), ORANGE, "--")}
    vox = {0: (104, 104), 60: (156, 134)}
    width = json.load(open(lir / "lir.json"))
    keys = {"GATE matrix (MC counts 1-6 per entry)": "GATE SRM (ideal_lir.py)", "gammart matrix, noiseless": "(iv) current mix, parallel",
            "gammart + GATE-like counting noise": "(iv) current mix, parallel + GATE-like MC noise"}
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    t = np.arange(-25, 25.01, 0.25)
    for ax, r in zip(axs, vox):
        v = vox[r]
        for lab, (d, c, ls) in src.items():
            a = d[f"r{r:03d}_a0.001"].astype(float)
            prof = np.mean([map_coordinates(a / a[v], [v[0] + t * np.sin(g), v[1] + t * np.cos(g)], order=1)
                            for g in np.radians(np.arange(0, 180, 15))], 0)
            w = width[keys[lab]][f"r={r}"]["alpha=0.001"]["mean"]
            ax.plot(t, prof, ls, color=c, lw=2, label=f"{lab}: half-max {w:.1f} mm")
        ax.axhline(0.5, color=GRID, lw=1)
        ax.set_title(f"r = {r} mm", fontsize=12)
        ax.set_xlabel("distance from the point (mm)")
        ax.grid(True, color=GRID)
        ax.legend(fontsize=9.5, loc="upper right")
    axs[0].set_ylabel("response / peak (mean of 12 directions)")
    save(fig, "ideal_lir_profile.png")


# ------------------------------------------------------------------------------------------------ core + base schematic
def fig_core_base():
    """SCHEMATIC with invented widths: a point response with a sharp core on a broad base (core 3.5 mm FWHM, base 14 mm
    FWHM, 60/40 weights; chosen for illustration only) blurring (i) an isolated thin line and (ii) a rod pattern with
    rod = gap (Derenzo-like). The measured values are on the following slides."""
    n = 400
    x = np.linspace(-30, 30, n)
    dx = x[1] - x[0]

    def g(f):
        s = f / 2.355
        k = np.exp(-0.5 * (x / s) ** 2)
        return k / k.sum()

    psf = 0.6 * g(3.5) + 0.4 * g(14.0)
    def fwhm(y):
        y = y / y.max()
        i = np.where(y >= 0.5)[0]
        return (i[-1] - i[0] + 1) * dx
    line = np.zeros(n)
    line[n // 2] = 1
    rods = np.zeros(n)
    d = 6.0
    for c in (-3 * d, -2 * d, -d, 0, d, 2 * d, 3 * d):
        pass
    for c in np.arange(-18, 19, 12.0):
        rods[np.abs(x - c) <= 3.0] = 1
    fig, axs = plt.subplots(2, 3, figsize=(15, 7.4), gridspec_kw={"width_ratios": [1, 1.4, 1.4], "hspace": 0.55})
    ax = axs[0, 0]
    ax.semilogy(x, psf / psf.max(), color=INK)
    ax.semilogy(x, 0.6 * g(3.5) / psf.max(), "--", color=BLUE, label="core")
    ax.semilogy(x, 0.4 * g(14.0) / psf.max(), "--", color=ORANGE, label="broad base")
    ax.set_ylim(1e-3, 1.5)
    ax.set_title("point response (log)", fontsize=13)
    ax.legend(fontsize=10)
    axs[1, 0].plot(x, psf / psf.max(), color=INK)
    axs[1, 0].set_title("point response (linear)", fontsize=13)
    for ax in axs[:, 0]:
        ax.set_xlim(-30, 30)
    for ax, truth, name in ((axs[0, 1], line, "isolated thin line"), (axs[0, 2], rods, "rods, width = gap")):
        pass
    # line
    blur = np.convolve(line, psf, mode="same")
    ax = axs[0, 1]
    ax.plot(x, line / line.max() * 0.0 + 0, color=INK2, lw=0)
    ax.vlines(x[n // 2], 0, 1, color=INK2, lw=3, alpha=0.5, label="true line")
    ax.plot(x, blur / blur.max(), color=BLUE, label="blurred")
    ax.axhline(0.5, color=INK2, lw=0.8, ls=":")
    ax.set_title(f"thin line: FWHM = {fwhm(blur):.1f} mm (the core)", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_xlim(-30, 30)
    # rods
    blur2 = np.convolve(rods, psf, mode="same")
    ax = axs[0, 2]
    ax.fill_between(x, rods, step="mid", color=INK2, alpha=0.3, label="true rods (6 mm)")
    ax.plot(x, blur2 / blur2.max(), color=ORANGE, label="blurred")
    pk = blur2[np.abs(x - 6.0) < 1].max()
    va = blur2[np.abs(x - 0.0) < 0.5].min()
    ax.set_title(f"6 mm rods: valley/peak = {va / pk:.2f}", fontsize=13)
    ax.legend(fontsize=10, loc="lower right")
    ax.set_xlim(-30, 30)
    # same peak: rods of different size
    ax = axs[1, 1]
    for dd, c in ((3.0, ORANGE), (4.0, PURPLE), (6.0, BLUE), (8.0, AQUA)):
        r = np.zeros(n)
        for cc in np.arange(-6, 7) * 2 * dd:
            r[np.abs(x - cc) <= dd / 2] = 1
        b = np.convolve(r, psf, mode="same")
        c0 = np.abs(x) < 0.5 * dd
        mid = np.where(c0)[0]
        pkv = b[np.abs(x - 0) <= dd / 2].max()
        vav = b[np.abs(x - dd) <= 0.5].min()
        ax.plot([dd], [vav / pkv], "o", ms=12, color=c)
    ax.set_xlabel("rod size = gap (mm)")
    ax.set_ylabel("valley / peak")
    ax.set_title("valley/peak by rod size", fontsize=13)
    ax.grid(True, color=GRID)
    ax.set_ylim(0, 1.1)
    # text panel
    ax = axs[1, 2]
    ax.axis("off")
    ax.text(0, 0.9, "Why one number cannot describe both", fontsize=14, fontweight="bold")
    ax.text(0, 0.45, "The line is alone: only the core shows up in its width.\nThe rods are neighbours: each rod\nalso receives the base of its neighbours,\nso the valleys fill up.\n\n(illustration with invented widths;\nmeasured numbers follow)", fontsize=12, va="center")
    for ax in axs[:, 1:].ravel():
        ax.grid(True, color=GRID)
    for ax in (axs[0, 1], axs[0, 2]):
        ax.set_xlabel("position (mm)")
    save(fig, "core_base_schematic.png")


# ------------------------------------------------------------------------------------------------ info adds (MTF)
def fig_info_adds():
    """SCHEMATIC: Gaussian MTFs for four sizes (the large size has the most counts but the lowest MTF).
    Information at a frequency ~ sensitivity x MTF^2; the sum over heads is shown for all-C and a mix; illustrative widths."""
    f = np.linspace(0.01, 0.35, 200)  # cycles/mm
    size = {"A": (3.0, 0.08), "B": (4.5, 0.3), "C": (6.5, 1.0), "D": (10.0, 2.6)}  # (blur FWHM mm, relative sensitivity)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
    cols = {"A": "#86b6ef", "B": "#3987e5", "C": "#1c5cab", "D": "#0d366b"}
    info = {}
    for k, (w, s) in size.items():
        sig = w / 2.355
        mtf = np.exp(-2 * (np.pi * sig * f) ** 2)
        info[k] = s * mtf ** 2
        axs[0].plot(f, info[k], color=cols[k], label=f"all {k}")
    mix = np.mean([info[k] for k in "ABCD"], axis=0)
    axs[0].plot(f, mix, color=ORANGE, lw=3, label="mixed (A,B,C,D equally)")
    axs[0].set_xlabel("spatial frequency (cycles / mm)")
    axs[0].set_ylabel("information per head (arbitrary)")
    axs[0].set_title("Mixing: between the pure designs", fontsize=13)
    axs[0].legend(fontsize=11)
    axs[0].grid(True, color=GRID)
    # which size is best per frequency
    best = np.array([np.argmax([info[k][i] for k in "ABCD"]) for i in range(len(f))])
    axs[1].step(f, best, color=INK, where="mid")
    axs[1].set_yticks(range(4), list("ABCD"))
    axs[1].set_xlabel("spatial frequency (cycles / mm)")
    axs[1].set_ylabel("best size at this frequency")
    axs[1].set_title("One band, one winner (illustrative)", fontsize=13)
    axs[1].axvspan(0.045, 0.075, color=ORANGE, alpha=0.15)
    axs[1].text(0.08, 2.4, "band of the 7-8 mm rods\n(position illustrative)", fontsize=11, color=INK2)
    axs[1].grid(True, color=GRID)
    save(fig, "info_adds.png")


# ------------------------------------------------------------------------------------------------ surrogate concept
def fig_surrogate():
    """SCHEMATIC of the surrogate idea; the numbers in the boxes are from docs/design_surrogate/_variables.yml."""
    fig, ax = plt.subplots(figsize=(15, 6.4))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.text(0.1, 6.0, "1. Teach: exact physics labels one module", fontsize=13, color=BLUE, fontweight="bold")
    box(ax, (0.2, 4.2), 3.2, 1.3, "gammart ray tracing\n(exact, 20 min per design)", "#eaf1fb", BLUE)
    box(ax, (4.0, 4.2), 3.2, 1.3, "196,608 sampled\nsource positions, 48 widths\n34 min on the 3080 Ti", "#eaf1fb", BLUE)
    arrow(ax, (3.4, 4.85), (4.0, 4.85), BLUE)
    ax.text(8.0, 6.0, "2. Learn: copy the labels", fontsize=13, color=PURPLE, fontweight="bold")
    box(ax, (8.0, 4.2), 3.4, 1.3, "Neural surrogate\n584,840 parameters\n(trained 1.8 h)", "#efe7fa", PURPLE)
    arrow(ax, (7.2, 4.85), (8.0, 4.85), BLUE)
    ax.text(12.1, 6.0, "3. Use: fast, differentiable", fontsize=13, color=AQUA, fontweight="bold")
    box(ax, (12.0, 4.2), 2.8, 1.3, "~2 s per design\n(about 600 x faster)", "#e3f6ee", AQUA)
    arrow(ax, (11.4, 4.85), (12.0, 4.85), PURPLE)
    box(ax, (1.0, 1.5), 4.4, 1.5, "Gradients: 'if this pinhole\nwere a little wider, the\nresolution would change by ...'", "#fdece4", ORANGE)
    box(ax, (6.3, 1.5), 3.4, 1.5, "Optimiser nudges\npinhole widths and\nhead poses", "#fdece4", ORANGE)
    box(ax, (10.6, 1.5), 4.0, 1.5, "Check: exact ray tracing\nand then full\nreconstruction (scorecard)", "#e3f6ee", AQUA)
    arrow(ax, (5.4, 2.25), (6.3, 2.25), ORANGE)
    arrow(ax, (9.7, 2.25), (10.6, 2.25), ORANGE)
    arrow(ax, (13.4, 4.2), (13.0, 3.0), AQUA)
    ax.text(0.2, 0.6, "Analogy: a chess player who has seen 200,000 positions answers in a second what an engine needs minutes to calculate;\nbecause the answer is a smooth formula, we can also ask 'which move improves it fastest' (the gradient).",
            fontsize=11.5, color=INK2)
    save(fig, "surrogate_concept.png")


# ------------------------------------------------------------------------------------------------ scorecards (anonymised)
SC = PY / "design_scorecard/r100_2026-10-26"
LAB = {"uniform_0.556": ("all A (smallest)", "#86b6ef"), "uniform_0.797": ("all B", "#3987e5"),
       "uniform_1.215": ("all C", "#1c5cab"), "uniform_2.007": ("all D (largest)", "#0d366b"),
       "current": ("current mix (index mod 4)", ORANGE), "rings_mixed": ("rings B/C/D", PURPLE),
       "assignment_best": ("best assignment (C, one B)", AQUA)}


def fig_scorecards():
    """Scorecard curves redrawn from design_scorecard/r100_2026-10-26/*/scorecard.json (ERIS 6138007, 100 realisations);
    same as docs/design_surrogate/img/scorecard_*.png but with the pinhole sizes named A-D (confidentiality)."""
    cards = {n: json.loads((SC / n / "scorecard.json").read_text()) for n in LAB}
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.8), sharey=True)
    for ax, rod in zip(axs, ("6", "7", "8")):
        for n, (lab, c) in LAB.items():
            by = cards[n]["phantoms"]["derenzo"]["by_iteration"]
            its = sorted(by, key=int)
            cov = np.array([by[i][rod]["peak_cov"] for i in its])
            vp = np.array([by[i][rod]["vp_mean"] for i in its])
            ax.plot(100 * cov, vp, ":" if n == "assignment_best" else "-", color=c, marker="o", ms=4.5, mec=SURF, label=lab)
        ax.axvline(2.5, color=INK2, lw=1, ls=(0, (2, 3)))
        ax.set_title(f"{rod} mm rods")
        ax.set_xlabel("rod-peak noise, CoV (%)")
        ax.grid(True, color=GRID, lw=0.6)
        ax.set_xlim(0, 9.5)
    axs[0].set_ylabel("valley / peak (lower = better)")
    axs[0].set_ylim(0, 1.25)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=11, bbox_to_anchor=(0.5, -0.2))
    fig.suptitle("Derenzo in air: resolution against noise, OSEM iterations 1-32 along each curve", fontsize=14)
    save(fig, "scorecard_derenzo.png")

    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    for n, (lab, c) in LAB.items():
        by = cards[n]["phantoms"]["xcat"]["by_iteration"]
        its = sorted(by, key=int)
        cov = np.array([by[i]["noise_cov_100"] for i in its])
        for ax, key in zip(axs, ("crc_920_100", "nrmse_mean")):
            ax.plot(100 * cov, [by[i][key] for i in its], ":" if n == "assignment_best" else "-", color=c, marker="o", ms=4.5, mec=SURF, label=lab)
    for ax, yl in zip(axs, ("contrast recovery 920:100 (higher = better)", "NRMSE in the head (lower = better)")):
        ax.axvline(20, color=INK2, lw=1, ls=(0, (2, 3)))
        ax.set_xscale("log")
        ax.set_xlabel("voxel noise, CoV in the 100 class (%)")
        ax.set_ylabel(yl)
        ax.grid(True, color=GRID, lw=0.6)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=11, bbox_to_anchor=(0.5, -0.2))
    fig.suptitle("XCAT perfusion: contrast and error against noise", fontsize=14)
    save(fig, "scorecard_xcat.png")


def relabel_scorecard_images():
    """Cover the header strip (which carries the pinhole widths) of the existing scorecard_images.png and write A-D labels.
    The image content is the original one (docs/design_surrogate/img/scorecard_images.png)."""
    from PIL import Image, ImageDraw, ImageFont
    im = Image.open(PO / "docs/design_surrogate/img/scorecard_images.png").convert("RGB")
    W, H = im.size
    s = W / 2000.0
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(19 * s))
    cols = [(363, 690, "all A (smallest)\nOSEM it 2"), (693, 1020, "all C\nOSEM it 8"), (1023, 1350, "all D (largest)\nOSEM it 32"),
            (1353, 1680, "current mix\nOSEM it 8"), (1683, 2000, "rings B/C/D\nOSEM it 16")]
    d.rectangle([int(340 * s), int(8 * s), W, int(82 * s)], fill=(252, 252, 251))
    d.rectangle([int(340 * s), int(412 * s), W, int(437 * s)], fill=(252, 252, 251))
    for x0, x1, t in cols:
        for k, line in enumerate(t.split("\n")):
            d.text((int((x0 + x1) / 2 * s), int((48 + 18 * k) * s)), line, fill=(11, 11, 11), font=f, anchor="mm")
    d.text((int(1000 * s), int(22 * s)), "One noisy realisation per design, at the iteration nearest 2.5% rod-peak CoV (8 mm rods)",
           fill=(11, 11, 11), font=f, anchor="mm")
    its = ["it 2", "it 8", "it 32", "it 8", "it 16"]
    for (x0, x1, _), t in zip(cols, its):
        d.text((int((x0 + x1) / 2 * s), int(425 * s)), t, fill=(11, 11, 11), font=f, anchor="mm")
    im.save(OUT / "scorecard_images.png")


# ------------------------------------------------------------------------------------------------ confidence chain
def fig_confidence():
    """Status of each link of the validation chain (text from the project documents; no numbers computed)."""
    links = [
        ("Formula vs unit tests (single pinhole)", "done", "tests/test_multi_pinhole.py: <0.1-0.2 % sens., <0.5 % penetration (on axis)"),
        ("gammart SRM vs 1e14 GATE SRM (columns)", "done", "engine paper: 1,508 columns, head pull rms 1.008"),
        ("gammart vs GATE: image domain", "done", "contrast/FWHM/ROI within 1-4 %; +1.6-1.9 % scale offset"),
        ("Single module, GATE vs gammart MC (WP1)", "done", "window counts 0.999-1.004 in 10 cases; fluorescence not in gammart"),
        ("Spectrum mismatch (WP0)", "done", "room air + Doppler; window within 1 %"),
        ("Converging-pixel SRM (WP2)", "provisional", "~1 % on 5 modules; top module 3.5 % off; no phantoms yet"),
        ("Full-system GATE, 3 phantoms (WP3)", "running", "launching on Expanse; no results"),
        ("Formula -> SRM, brain system (Phase 0)", "not done", "planned, ~1 h"),
        ("Measured LIR in the Derenzo (Phase 1-2)", "not done", "planned; explanation of line vs Derenzo is provisional"),
        ("Surrogate -> exact SRM", "done", "0.20 % per pixel, 0.14 % totals, 0.75 % derivatives"),
        ("Aperture result vs GATE data / scatter", "not done", "scorecard uses one SRM for data and recon (inverse crime)"),
        ("Aperture result on the converging detector", "not done", "re-check pending after WP2"),
    ]
    colr = {"done": AQUA, "provisional": "#e0a800", "running": BLUE, "not done": RED}
    fig, ax = plt.subplots(figsize=(16, 6.6))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, len(links) + 0.5)
    ax.axis("off")
    for k, (n, st, note) in enumerate(links):
        y = len(links) - k - 0.3
        ax.add_patch(FancyBboxPatch((0.1, y - 0.3), 1.9, 0.6, boxstyle="round,pad=0.02,rounding_size=0.1", fc=colr[st], ec="none"))
        ax.text(1.05, y, st, color="white", ha="center", va="center", fontsize=12, fontweight="bold")
        ax.text(2.2, y, n, va="center", fontsize=12.5, fontweight="bold")
        ax.text(8.6, y, note, va="center", fontsize=11, color=INK2)
    save(fig, "confidence.png")


# ------------------------------------------------------------------------------------------------ timeline
def fig_timeline():
    """Work plan from paper2_plan.md (order, revised 2026-10-27) and resolution_consistency_plan.md; no dates beyond the documents."""
    items = [("WP0 spectrum", "final", AQUA, 0), ("WP1 single module", "final", AQUA, 1), ("WP2 converging SRM", "prototype", "#e0a800", 2),
             ("WP2b placement", "provisional", "#e0a800", 3), ("WP3 full-system GATE", "running", BLUE, 4), ("Resolution Phase 0-3", "planned", RED, 5),
             ("WP4 scatter correction", "planned", RED, 6), ("WP5 performance", "planned", RED, 7), ("WP6 comparison", "planned", RED, 8), ("WP7 write", "planned", RED, 9)]
    fig, ax = plt.subplots(figsize=(13, 4.6))
    for n, st, c, k in items:
        ax.barh(0, 1, left=k, color=c, ec=SURF, height=0.5)
        ax.text(k + 0.5, 0.0, n, rotation=90, ha="center", va="center", color="white", fontsize=11.5, fontweight="bold")
        ax.text(k + 0.5, -0.38, st, ha="center", va="top", fontsize=10.5, color=INK2)
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.9, 0.5)
    ax.axis("off")
    ax.set_title("Paper-2 work packages in order (no calendar dates: none are fixed in the plan)")
    save(fig, "timeline.png")


if __name__ == "__main__":
    fig_pipeline()
    fig_helmet()
    r = fig_classic()
    fig_wp0()
    fig_wp2b()
    fig_resolution_measures()
    fig_ideal_lir()
    fig_core_base()
    fig_info_adds()
    fig_surrogate()
    fig_scorecards()
    relabel_scorecard_images()
    fig_confidence()
    fig_timeline()
    print("figures written to", OUT)
