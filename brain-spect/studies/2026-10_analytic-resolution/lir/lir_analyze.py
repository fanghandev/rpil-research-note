"""Half-max width (12 directions, min/mean/max, as analytic.py lir_half_max) and energy share beyond 15 mm of the four gammart LIRs
and of the GATE-SRM LIR (dev/python/ideal_lir), alpha = 1e-3 lambda_max.  Writes lir.json, lir.md, lir_profiles.png."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import map_coordinates

HERE = Path(__file__).resolve().parent
CASES = {"(i) current mix, converging": "current_conv", "(ii) uniform 1.215, parallel": "uniform_parallel",
         "(iii) uniform 1.215, converging": "uniform_conv", "(iv) current mix, parallel": "current_parallel"}
RADII = (0, 30, 60, 80, 95)
VOX = {0: (104, 104), 30: (130, 120), 60: (156, 134), 80: (174, 144), 95: (187, 152)}


def hm(a, t=np.arange(-30, 30.01, 0.25)):
    c = len(t) // 2
    iy, ix = np.unravel_index(np.argmax(a), a.shape)
    ws = []
    for ang in np.radians(np.arange(0, 180, 15)):
        v = map_coordinates(a, [iy + t * np.sin(ang), ix + t * np.cos(ang)], order=1)
        v = v / v[c]
        w = 0.0
        for st in (1, -1):
            i = c
            while v[i] >= 0.5:
                i += st
            j = i - st
            w += (abs(j - c) + (v[j] - 0.5) / (v[j] - v[i])) * 0.25
        ws.append(w)
    return ws, (iy, ix), t


def far(a, v, near=15.0):
    g = np.arange(a.shape[0])
    dx, dy = np.meshgrid(g - v[0], g - v[1], indexing="ij")
    return float(np.sum(a[dx**2 + dy**2 > near**2] ** 2) / np.sum(a**2))


def main():
    src = {"GATE SRM (ideal_lir.py)": np.load(HERE.parents[2] / "python/ideal_lir/ideal_lir_slices.npz")}
    for k, c in CASES.items():
        src[k] = np.load(HERE / "out" / c / "lir_slices.npz")
    nz = HERE / "out_noise"
    for k, c in CASES.items():
        if (nz / c / "lir_slices.npz").exists():
            src[k + " + GATE-like MC noise"] = np.load(nz / c / "lir_slices.npz")
    res, prof = {}, {}
    for name, z in src.items():
        res[name] = {}
        for r in RADII:
            for al in ("0.001", "0.01", "0.0001"):
                a = z[f"r{r:03d}_a{al}"].astype(float)
                ws, pk, t = hm(a)
                d = {"min": min(ws), "mean": float(np.mean(ws)), "max": max(ws), "far15": far(a, VOX[r]), "peak_at_voxel": bool(pk == VOX[r][::-1] or pk == VOX[r]),
                     "peak": float(a[VOX[r]])}
                res[name].setdefault(f"r={r}", {})[f"alpha={al}"] = d
                if al == "0.001":
                    prof[(name, r)] = (a, VOX[r])
    (HERE / "lir.json").write_text(json.dumps(res, indent=1))
    L = ["Half-max width (mm), mean (min-max over 12 directions), alpha = 1e-3 lambda_max; energy share beyond 15 mm in %.", "",
         "| case | " + " | ".join(f"r={r}" for r in RADII) + " |", "|---" * 6 + "|"]
    for n in src:
        L.append(f"| {n} | " + " | ".join(f"**{res[n][f'r={r}']['alpha=0.001']['mean']:.1f}** ({res[n][f'r={r}']['alpha=0.001']['min']:.1f}-{res[n][f'r={r}']['alpha=0.001']['max']:.1f})" for r in RADII) + " |")
    L += ["", "| case (far-field share, %) | " + " | ".join(f"r={r}" for r in RADII) + " |", "|---" * 6 + "|"]
    for n in src:
        L.append(f"| {n} | " + " | ".join(f"{100 * res[n][f'r={r}']['alpha=0.001']['far15']:.1f}" for r in RADII) + " |")
    (HERE / "lir.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    fig, axes = plt.subplots(1, 5, figsize=(17, 3.6), sharey=True)
    for ax, r in zip(axes, RADII):
        for n in src:
            a, v = prof[(n, r)]
            t = np.arange(-30, 30.01, 0.5)
            p = np.mean([map_coordinates(a / a[v], [v[0] + t * np.sin(g), v[1] + t * np.cos(g)], order=1) for g in np.radians(np.arange(0, 180, 15))], 0)
            ax.plot(t, p, label=n, lw=1.5)
        ax.axhline(0.5, color="#aaa", lw=0.6); ax.set_title(f"r = {r} mm"); ax.set_xlabel("distance (mm)"); ax.grid(alpha=0.3)
    axes[0].set_ylabel("LIR / peak (mean of 12 directions)"); axes[0].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(HERE / "lir_profiles.png", dpi=130)


main()
