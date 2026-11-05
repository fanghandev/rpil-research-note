"""Measured triple-line data (Mar23, cardiac converging-pixel prototype, 20 heads, Xi decoding) reconstructed with three
system matrices: GATE (parallel pixels), gammart parallel pixels, gammart converging pixels.  MLEM 50 iterations, 1 mm
voxels, 150 mm crop (model_LIOB/studies/cardiac_recon.py; metrics as model_LIOB/studies/recon_lines.py).
Writes img/triple_scale.png and adds the numbers to img/figure_numbers.json under "triple_scale".
"""

import os
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, f"{os.path.expanduser('~')}/Work/RPIL/QMIRT/model_LIOB/studies")
from recon_lines import lines  # noqa: E402

REC = Path(f"{os.path.expanduser('~')}/Work/RPIL/QMIRT/model_LIOB/out/recon")
OUT = Path(__file__).resolve().parents[1] / "img"
TRUE = np.array([75.0, 75.0, 106.1])
CASES = [("Mar23_xi_gate", "GATE matrix\n(parallel 2 mm pixels)"),
         ("Mar23_xi_parallel_1mm", "gammart matrix\n(parallel 2 mm pixels)"),
         ("Mar23_xi_converging_1mm", "gammart matrix\n(converging pixels)")]


def main():
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.9))
    nums = {}
    for ax, (f, title) in zip(axes, CASES):
        img, L = lines(np.load(REC / f"{f}.npz")["it50"])
        P = np.array([(x, y) for x, y, _, _ in L])
        sides = np.array(sorted(np.hypot(*(P[i] - P[j])) for i, j in ((0, 1), (0, 2), (1, 2))))
        scale = sides.sum() / TRUE.sum()
        n = img.shape[0]
        ext = [-n / 2, n / 2, -n / 2, n / 2]
        ax.imshow(np.clip(img.T / img.max(), 0, None) ** 0.5, origin="lower", cmap="gray_r", extent=ext, vmin=0, vmax=0.9)
        c = P.mean(0)
        tri = c + (P - c) / scale  # the reconstructed triangle shrunk to the true size, same centre and orientation
        for Q, style, lab in ((P, "-", "reconstructed"), (tri, "--", "true size")):
            Qc = np.vstack([Q, Q[:1]])
            ax.plot(Qc[:, 0], Qc[:, 1], style, color="#d55e00" if style == "-" else "#0072b2", lw=1.3, label=lab)
        fw = np.array([(fx, fy) for _, _, fx, fy in L])
        ax.set_title(title, fontsize=10)
        fwtxt = ("line FWHM: not comparable\n(Monte Carlo noise in the matrix)" if "gate" in f
                 else f"line FWHM {fw.min():.1f}–{fw.max():.1f} mm")
        ax.text(0.97, 0.97, f"sides {sides[0]:.1f} / {sides[1]:.1f} / {sides[2]:.1f} mm\nscale ×{scale:.3f}\n" + fwtxt,
                transform=ax.transAxes, fontsize=8.5, va="top", ha="right", bbox=dict(fc="white", ec="0.7", lw=0.6))
        ax.set_xlim(-75, 75); ax.set_ylim(-75, 75)
        ax.set_aspect("equal")
        ax.set_xlabel("x (mm)")
        nums[f] = {"sides_mm": sides.round(1).tolist(), "scale": round(float(scale), 4),
                   "fwhm_mm": [round(float(fw.min()), 1), round(float(fw.max()), 1)]}
    axes[0].set_ylabel("y (mm)")
    axes[0].legend(loc="lower left", fontsize=8, frameon=True)
    fig.suptitle("Measured triple line (true sides 75 / 75 / 106.1 mm), MLEM 50 iterations, axial sum over 40 mm",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "triple_scale.png", dpi=200)
    fn = OUT / "figure_numbers.json"
    d = json.loads(fn.read_text()) if fn.exists() else {}
    d["triple_scale"] = nums
    fn.write_text(json.dumps(d, indent=1))
    print(json.dumps(nums, indent=1))


if __name__ == "__main__":
    main()
