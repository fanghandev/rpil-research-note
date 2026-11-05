"""Figure of the square-pinhole PSF (exact CSG ray trace, variant C, theta = 0 and 30 deg) and the line-spread
(LSF) widths of all four apertures at normal incidence (PSF integrated along the perpendicular direction, as a
rod or line source would see it).  CPU / numpy only.

    micromamba run -n opengate env -u DISPLAY python figures_lsf.py   (writes img/psf_C.png and lsf.json)
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raytrace_pyramid as rt  # noqa: E402
import square_pinhole_model as m  # noqa: E402

OUT = Path(__file__).resolve().parent
INK, INK2, GRID = "#1d1d1f", "#6e6e73", "#e5e5ea"


def lsf_widths(w, t1, t2, mu, step=0.002, margin=3.0):
    """LSF FWHM along a side and along the diagonal, and the (isotropic) RMS, in the knife-edge plane."""
    h = 0.5 * w + margin
    x = np.arange(-h, h + step / 2, step)
    X, Y = np.meshgrid(x, x, indexing="ij")
    T = m.transmission_square(X, Y, w, t1, t2, 0.0, 0.0, mu)
    lsf_side = T.sum(axis=1)
    lsf_diag = diagonal_lsf(T)  # samples spaced step / sqrt(2) along the diagonal
    s = T.sum()
    rms = np.sqrt((T * X * X).sum() / s)
    return {"lsf_fwhm_side": m.full_width(lsf_side, 0.5) * step, "lsf_fwhm_diag": m.full_width(lsf_diag, 0.5) * step / np.sqrt(2),
            "rms": rms, "psf_fwhm_side": m.full_width(T[:, len(x) // 2], 0.5) * step,
            "psf_fwhm_diag": m.full_width(np.diagonal(T), 0.5) * step * np.sqrt(2)}


def diagonal_lsf(T):
    """Exact projection of the map onto the diagonal: sum over the anti-diagonals i + j = k. The samples are
    spaced step / sqrt(2) along the diagonal; the line integral is the sum times step * sqrt(2)."""
    i, j = np.indices(T.shape)
    return np.bincount((i + j).ravel(), weights=T.ravel()) * np.sqrt(2)


def figure():
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.6))
    name, f = "C", m.F_MM
    for row, (th, ph) in enumerate(((0, 0), (30, 0))):
        x, y, T, flux, S, Xc = rt.trace(name, m.B_CENTRE, th, ph)
        b = m.B_CENTRE
        scale = b / (b + f)  # detection plane -> knife-edge plane
        xs, ys = (x - Xc[0]) * scale, (y - Xc[1]) * scale
        step = xs[1] - xs[0]
        ax = axes[row, 0]
        im = ax.imshow(T.T, origin="lower", extent=[xs[0], xs[-1], ys[0], ys[-1]], cmap="viridis", vmin=0, vmax=1)
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_xlabel("x in the knife-edge plane (mm), along a side")
        ax.set_ylabel("y (mm)")
        ax.set_title(f"C (w = 1.215 mm): transmission, theta = {th} deg" + (", tilt along x" if th else ""), fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
        ix, iy = np.argmin(np.abs(xs)), np.argmin(np.abs(ys))
        ax = axes[row, 1]
        d = np.arange(len(np.diagonal(T))) * step * np.sqrt(2)
        d -= d[len(d) // 2]
        for prof, coord, lab, col in ((T[:, iy], xs, "along x (parallel to the tilt)", INK), (T[ix, :], ys, "along y", "#3b82f6"),
                                      (np.diagonal(T), d, "along the diagonal", "#ea580c")):
            ax.plot(coord, prof, color=col, lw=1.6, label=f"{lab}: FWHM {m.full_width(prof, 0.5) * (coord[1] - coord[0]):.3f} mm")
        ax.axhline(0.5, color=INK2, lw=0.8, ls="--")
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("distance from the centre (mm)")
        ax.set_ylabel("transmission")
        ax.set_title("point-profile cuts through the centre (PSF)", fontsize=10)
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(True, color=GRID)
        ax = axes[row, 2]
        lsf_x = T.sum(axis=1) * step
        lsf_d = diagonal_lsf(T) * step
        ud = np.arange(len(lsf_d)) * step / np.sqrt(2)
        ud -= ud[np.argmax(lsf_d)]
        for prof, coord, lab, col in ((lsf_x, xs, "line parallel to a side", INK), (lsf_d, ud, "line along the diagonal", "#ea580c")):
            ax.plot(coord, prof / prof.max(), color=col, lw=1.6, label=f"{lab}: FWHM {m.full_width(prof, 0.5) * (coord[1] - coord[0]):.3f} mm")
        ax.axhline(0.5, color=INK2, lw=0.8, ls="--")
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("distance (mm)")
        ax.set_ylabel("normalised line-spread")
        ax.set_title("line-spread function (PSF integrated along the line)", fontsize=10)
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(True, color=GRID)
    fig.suptitle("Square knife-edge pinhole C, exact CSG ray trace, 140 keV in W (mu = 3.63 /mm), source at b = 149.6 mm; "
                 "widths referred to the knife-edge plane", fontsize=10)
    fig.tight_layout()
    (OUT / "img").mkdir(exist_ok=True)
    fig.savefig(OUT / "img" / "psf_C.png", dpi=140)


def main():
    res = {}
    print("LSF / PSF widths in the knife-edge plane at normal incidence (model, t1/t2 of each variant):")
    print("variant  w     geometric: LSF side = w, LSF diag = w/sqrt2, RMS = w/sqrt12 | with penetration: LSF side, LSF diag, RMS, PSF side, PSF diag")
    for n, w in m.WIDTHS.items():
        t1, t2 = m.slopes(n)
        r = lsf_widths(w, t1, t2, m.MU_W)
        res[n] = {"w": w, "geo_lsf_side": w, "geo_lsf_diag": w / np.sqrt(2), "geo_rms": w / np.sqrt(12), **r}
        print(f"{n}  {w:.3f}   {w:.3f}  {w / np.sqrt(2):.3f}  {w / np.sqrt(12):.3f}  |  {r['lsf_fwhm_side']:.3f}  {r['lsf_fwhm_diag']:.3f}  "
              f"{r['rms']:.3f}  {r['psf_fwhm_side']:.3f}  {r['psf_fwhm_diag']:.3f}")
    (OUT / "lsf.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    figure()


if __name__ == "__main__":
    main()
