"""Clearance figures for the Oct 7-9 progress report.

Recomputes the helmet clearance with the functions of
dev/python/phantom_fit_brain_scanner.py (same hardware samples, same phantoms) and draws
two figures for readers new to the check:

- clearance_profile.png: smallest gap between phantom and hardware against the phantom's
  height, one curve per phantom and orientation;
- clearance_side_views.png: each case at one height, as a side view (distance from the
  helmet axis vs height), with the point where the phantom comes closest to the hardware.

Run (opengate env):
    python dev/reports/2026-10-09_progress_oct7-9/make_clearance_figures.py
"""

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEV = HERE.parents[1] / "python"
sys.path.insert(0, str(DEV))
import phantom_fit_brain_scanner as sc  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

CHOSEN_Z = -25.0
BLUE, RED, ORANGE = "#1f77b4", "#d62728", "#e67e00"
CASES = [  # key, orientation, label, colour, line style
    ("acr", "upright", "ACR Deluxe, upright", BLUE, "-"),
    ("acr", "flipped", "ACR Deluxe, upside down", BLUE, "--"),
    ("small", "upright", "Small Jaszczak, upright", RED, "-"),
    ("small", "flipped", "Small Jaszczak, upside down (chosen)", ORANGE, "-"),
]


def profile(z, curves):
    plt.rcParams.update({"font.size": 10})
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    ax.axhspan(-40, 0, color="#f6dede", zorder=0)
    ax.axhline(0, color="k", lw=0.9)
    ax.text(-147, -38, "below 0: the phantom overlaps the hardware (does not fit)", fontsize=8.5,
            color="#8b1a1a", va="bottom")
    ax.text(-147, 28.5, "above 0: the phantom fits, with this much space left", fontsize=8.5,
            color="#2b5d2b", va="top")
    for key, orient, label, colour, ls in CASES:
        ax.plot(z, curves[(key, orient)], color=colour, ls=ls, lw=1.8, label=label)

    c = curves[("small", "flipped")]
    y = float(c[np.argmin(np.abs(z - CHOSEN_Z))])
    ax.plot([CHOSEN_Z], [y], marker="o", ms=7, color=ORANGE, mec="k", zorder=5)
    ax.annotate(f"chosen: z = {CHOSEN_Z:.0f} mm,\ngap {y:.1f} mm", (CHOSEN_Z, y), xytext=(-105, 3),
                fontsize=8.5, arrowprops=dict(arrowstyle="-", lw=0.8))
    a = curves[("acr", "flipped")]
    k = int(np.argmax(a))
    ax.plot([z[k]], [a[k]], marker="v", ms=6, color=BLUE, mec="k", zorder=5)
    ax.annotate("ACR best case:\nstill 5.8 mm overlap", (z[k], a[k]), xytext=(-105, -24), fontsize=8.5,
                arrowprops=dict(arrowstyle="-", lw=0.8))

    ax.set_xlim(z[0], z[-1])
    ax.set_ylim(-40, 30)
    ax.set_xlabel("height of the phantom's water centre above the FOV centre, z (mm)")
    ax.set_ylabel("smallest gap to shield and collimators (mm)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "clearance_profile.png", dpi=200)
    plt.close(fig)


def side_views(points, z, curves, fov_r):
    views = [  # case index, height shown, title
        (0, 6.0, "ACR Deluxe, upright\nbest height z = +6 mm"),
        (1, -3.0, "ACR Deluxe, upside down\nbest height z = −3 mm"),
        (2, -16.0, "Small Jaszczak, upright\nhighest fit z = −16 mm"),
        (3, CHOSEN_Z, "Small Jaszczak, upside down\nchosen z = −25 mm"),
    ]
    rho_hw = np.hypot(points[:, 0], points[:, 1])
    t = np.linspace(-np.pi / 2, np.pi / 2, 200)
    plt.rcParams.update({"font.size": 9})
    fig, axs = plt.subplots(1, 4, figsize=(11, 5.6), sharey=True)
    for ax, (i, zs, title) in zip(axs, views):
        key, orient, _, colour, _ = CASES[i]
        ph, flipped = sc.PHANTOMS[key], sc.ORIENTATIONS[orient]
        ax.scatter(rho_hw, points[:, 2], s=0.15, c="0.62", rasterized=True)
        ax.plot(fov_r * np.cos(t), fov_r * np.sin(t), color="#2e7d32", lw=1.1)
        solids = sc.world_solids(ph, zs, flipped)
        for r_in, r_out, z0, z1 in solids:
            ax.add_patch(Rectangle((r_in, z0), r_out - r_in, z1 - z0, fill=False, ec=colour, lw=1.1))
        (_, r_w, w0, w1), = sc.world_solids(ph, zs, flipped, water_only=True)
        ax.add_patch(Rectangle((0, w0), r_w, w1 - w0, fc=colour, alpha=0.12, ec="none"))
        rod_a, rod_b = (sc.to_world(ph, ph["base_mm"] + h, zs, flipped) for h in ph["rod_z_mm"])
        ax.add_patch(Rectangle((0, min(rod_a, rod_b)), r_w, abs(rod_b - rod_a), fc="none", ec=colour,
                               hatch="||", lw=0, alpha=0.55))
        _, spheres, stems = sc.phantom_layout(key)
        z_s = sc.to_world(ph, ph["base_mm"] + ph["sphere_above_floor_mm"], zs, flipped)
        for x, y, d in spheres:
            ax.add_patch(Circle((np.hypot(x, y), z_s), d / 2, fc="none", ec="#ab47bc", lw=0.9))
        for x, y, s0, s1, d in stems:
            a, b = (sc.to_world(ph, ph["base_mm"] + h, zs, flipped) for h in (s0, s1))
            ax.add_patch(Rectangle((np.hypot(x, y) - d / 2, min(a, b)), d, abs(b - a), fc="#ab47bc",
                                   alpha=0.5, ec="none"))
        # closest hardware point (deepest overlap if negative)
        dist = sc.signed_distance_to_solids(points, solids)
        k = int(np.argmin(dist))
        ax.plot([rho_hw[k]], [points[k, 2]], marker="x", ms=10, mew=2.2, color="k", zorder=6)
        gap = float(curves[(key, orient)][np.argmin(np.abs(z - zs))])
        word = f"overlap {-gap:.1f} mm" if gap < 0 else f"gap {gap:.1f} mm"
        ax.set_title(f"{title}\n{word}", fontsize=9, color="#8b1a1a" if gap < 0 else "#2b5d2b")
        ax.set_xlim(0, 170)
        ax.set_ylim(-200, 170)
        ax.set_aspect("equal")
        ax.set_xlabel("distance from helmet axis (mm)")
        ax.grid(alpha=0.2)
    axs[0].set_ylabel("height z (mm)")
    handles = [plt.Line2D([], [], color="0.62", marker="o", ls="", ms=4, label="shield and collimators"),
               plt.Line2D([], [], color="#2e7d32", label="SRM FOV (r = 144 mm)"),
               plt.Line2D([], [], color="0.3", lw=1.1, label="phantom body and lid fittings"),
               Rectangle((0, 0), 1, 1, fc="none", ec="0.3", hatch="||", lw=0, label="cold rods"),
               plt.Line2D([], [], color="#ab47bc", label="spheres and stems"),
               plt.Line2D([], [], color="k", marker="x", ls="", ms=8, mew=2, label="closest point / worst overlap")]
    fig.legend(handles=handles, loc="lower center", ncol=6, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(HERE / "figures" / "clearance_side_views.png", dpi=200)
    plt.close(fig)


def main():
    provenance = json.loads(sc.DEFAULT_PROVENANCE.read_text())
    _, _, col_p = sc.collimator_geometry(provenance, 1.5)
    _, _, sh_p = sc.shield_geometry(provenance, 1.5, 0.5)
    points = np.vstack([sh_p, col_p])
    z = np.arange(-150.0, 100.0 + 1e-9, 1.0)
    curves = {}
    for key, orient, *_ in CASES:
        curves[(key, orient)] = sc.scan_z(points, sc.PHANTOMS[key], z, sc.ORIENTATIONS[orient])
        c = curves[(key, orient)]
        ok = z[c >= 0]
        print(f"{key} {orient}: best {c.max():+.1f} mm at z {z[np.argmax(c)]:+.0f}; "
              f"fits for z in {[ok.min(), ok.max()] if len(ok) else None}")
    profile(z, curves)
    side_views(points, z, curves, provenance["fov"]["size_mm"] / 2)


if __name__ == "__main__":
    main()
