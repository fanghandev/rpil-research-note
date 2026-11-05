"""Converging vs parallel 2 mm pixels, ideal and LIOB (simulated shrinkage) decoding: reconstructed GATE data (fluorescence
on) of the WP3 Derenzo and small Jaszczak, OSEM 8 subsets 64 iterations, AC + Compton kernel + TEW, each with its own
pixel model (examples/wp4_recon.py --pixels/--decoding).  Display: 3D Gaussian post-filter 6 mm FWHM (metrics unfiltered,
128 iterations, from out/wp4/recon/<phantom>.json).  Writes ../img/convpar_slices.png and ../img/convpar.json.
"""

import os
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.ndimage import gaussian_filter, map_coordinates  # noqa: E402

Q = Path(f"{os.path.expanduser('~')}/Work/RPIL/QMIRT")
REC = Q / "pytorch-optix/out/wp4/recon"
OUT = Path(__file__).resolve().parents[1] / "img"
N, V = 144, 2.0
AX = (np.arange(N) - (N - 1) / 2) * V
CASES = [("", "converging\nideal decoding"), ("_par", "parallel 2 mm\nideal decoding"),
         ("_dec-conv_shrink", "converging\nLIOB decoding"), ("_dec-par_shrink_par", "parallel 2 mm\nLIOB decoding")]
KEYS = {"": "ac_k_tew/gate_on", "_par": "ac_k_tew#par/gate_on", "_dec-conv_shrink": "ac_k_tew@conv_shrink/gate_on",
        "_dec-par_shrink_par": "ac_k_tew@par_shrink#par/gate_on"}


def post(a):
    return gaussian_filter(a, 6.0 / 2.3548 / V)


def ksl(z0, z1):
    return np.flatnonzero((AX >= z0) & (AX <= z1))


def main():
    sys.path.insert(0, str(Q / "qmirt-gate-10-sim/dev/reports/2026-10-30_brain_weekly/scripts"))
    from make_figures import jaszczak_background, jaszczak_cold_parts  # noqa: E402
    phd = np.load(Q / "qmirt-gate-10-sim/dev/python/design_scorecard/phantoms.npz")
    rods8 = phd["derenzo_sector_8_rods"]
    cold = jaszczak_cold_parts()
    k_rod, bg_rod = ksl(27.9, 30.1), jaszczak_background(29.0, cold)

    def der(tag):
        v = post(np.load(REC / f"derenzo_ac_k_tew{tag}_gate_on_it64.npy").astype(float).reshape(N, N, N))[:, :, ksl(-30, 30)].mean(2)
        return v / map_coordinates(v, [(rods8[:, 0] - AX[0]) / V, (rods8[:, 1] - AX[0]) / V], order=1).mean()

    def jr(tag):
        v = post(np.load(REC / f"jaszczak_ac_k_tew{tag}_gate_on_it64.npy").astype(float).reshape(N, N, N))[:, :, k_rod].mean(2)
        return v / v[bg_rod].mean()

    fig, axs = plt.subplots(2, 4, figsize=(12.5, 6.6))
    ext = (AX[0] - 1, AX[-1] + 1, AX[0] - 1, AX[-1] + 1)
    for c, (tag, lab) in enumerate(CASES):
        for r, (get, half, rowlab) in enumerate(((der, 75, "Derenzo (rods 3–8 mm)"), (jr, 70, "Jaszczak rods, z = 29 mm"))):
            ax = axs[r, c]
            im = ax.imshow(np.clip(get(tag), 0, 1.3).T, origin="lower", cmap="gray", vmin=0, vmax=1.3, extent=ext,
                           interpolation="nearest")
            ax.set_xlim(-half, half); ax.set_ylim(-half, half); ax.set_xticks([]); ax.set_yticks([])
            if r == 0:
                ax.set_title(lab, fontsize=11)
            if c == 0:
                ax.set_ylabel(rowlab, fontsize=10)
                ax.plot([-half * 0.75, -half * 0.75 + 20], [-half * 0.88] * 2, color="w", lw=2.5)
                ax.text(-half * 0.75 + 10, -half * 0.82, "20 mm", color="w", ha="center", fontsize=8)
    fig.colorbar(im, ax=axs, fraction=0.02, pad=0.01, label="activity / reference (6 mm post-filter)")
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "convpar_slices.png", dpi=170, bbox_inches="tight")
    res = {}
    for ph, ms in (("derenzo", ["vp_5mm", "vp_6mm", "vp_7mm", "vp_8mm"]), ("jaszczak", ["rod_contrast.7.9", "rod_contrast.9.5", "rod_contrast.12.7", "sphere_contrast.15.9"])):
        d = json.loads((REC / f"{ph}.json").read_text())
        for tag, key in KEYS.items():
            v = d[key]["it128"]
            flat = {}
            for k, x in v.items():
                if isinstance(x, dict):
                    flat.update({f"{k}.{kk}": xx for kk, xx in x.items()})
                else:
                    flat[k] = x
            res.setdefault(ph, {})[key] = {m: round(float(flat[m]), 3) for m in ms if m in flat}
    (OUT / "convpar.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
