"""Resolved views per voxel, converging vs parallel pixels, from the full-system first-interaction SRMs (gammart, annealed
map, 144^3 x 2 mm, r <= 142 mm; depth of interaction, penetration and the finite aperture included; no shield).

Per voxel j and module m:
    S_m(j)  = sum over the module's resolved pixel rows of H[row, j]   (converging: cells 0..624, edge strip 625 excluded;
                                                                         parallel: all 625 cells)
    E_m(j)  = H[m*626 + 625, j]                                          (converging edge strip)
Per voxel:
    resolved fraction (converging)  f_res = sum_m S_m / sum_m (S_m + E_m)
    effective number of views       N_eff = (sum_m S_m)^2 / sum_m S_m^2    (1 = one module dominates, 73 = all equal)
    resolved sensitivity ratio      sum_m S_m(conv) / sum_m S_m(par)
Writes ../img/views.png and ../img/views.json.
"""

import os
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import scipy.sparse as sp  # noqa: E402

W = Path(f"{os.path.expanduser('~')}/Work/RPIL/QMIRT/pytorch-optix/out/wp4")
OUT = Path(__file__).resolve().parents[1] / "img"
N, V, NM, NC = 144, 2.0, 73, 625


def module_sums(path):
    z = np.load(path)
    H = sp.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    vox = z["voxels"]
    per = H.shape[0] // NM
    rows = np.arange(H.shape[0])
    m, c = rows // per, rows % per
    res = c < NC
    G_res = sp.csr_matrix((np.ones(res.sum(), np.float32), (m[res], rows[res])), shape=(NM, H.shape[0]))
    S = (G_res @ H)[:, vox].toarray()
    E = None
    if per == NC + 1:
        G_e = sp.csr_matrix((np.ones(NM, np.float32), (np.arange(NM), np.flatnonzero(~res))), shape=(NM, H.shape[0]))
        E = (G_e @ H)[:, vox].toarray()
    return S, E, vox


def to_vol(v, vox):
    a = np.full(N ** 3, np.nan, np.float32)
    a[vox] = v
    return a.reshape(N, N, N)


def main():
    Sc, Ec, vox = module_sums(W / "srm_conv.npz")
    Sp, _, voxp = module_sums(W / "srm_par.npz")
    assert np.array_equal(vox, voxp)
    sc, sp_ = Sc.sum(0), Sp.sum(0)
    f_res = sc / np.maximum(sc + Ec.sum(0), 1e-30)
    neff_c = sc ** 2 / np.maximum((Sc ** 2).sum(0), 1e-30)
    neff_p = sp_ ** 2 / np.maximum((Sp ** 2).sum(0), 1e-30)
    ratio = sc / np.maximum(sp_, 1e-30)
    i, j, k = np.unravel_index(vox, (N, N, N))
    ax = (np.arange(N) - (N - 1) / 2) * V
    x, y, zc = ax[i], ax[j], ax[k]
    r3 = np.sqrt(x ** 2 + y ** 2 + zc ** 2)
    res = {"bins_r_mm": [], "f_res_conv": [], "neff_conv": [], "neff_par": [], "resolved_sens_ratio": []}
    edges = np.arange(0, 145, 10)
    for a, b in zip(edges[:-1], edges[1:]):
        s = (r3 >= a) & (r3 < b) & (sp_ > 0)
        if not s.any():
            continue
        res["bins_r_mm"].append(f"{a}-{b}")
        for key, arr in (("f_res_conv", f_res), ("neff_conv", neff_c), ("neff_par", neff_p), ("resolved_sens_ratio", ratio)):
            res[key].append(round(float(np.mean(arr[s])), 3))
    vols = {key: to_vol(arr, vox) for key, arr in (("f", f_res), ("nc", neff_c), ("np", neff_p), ("r", ratio))}
    sl = lambda v: np.nanmean(v[:, 71:73, :], axis=1).T  # coronal x-z plane, y = 0  # noqa: E731
    ext = [ax[0] - 1, ax[-1] + 1, ax[0] - 1, ax[-1] + 1]
    fig, axs = plt.subplots(1, 4, figsize=(17, 4.6))
    panels = [(sl(vols["f"]), "converging: fraction of counts on\nresolved pixels (rest = edge strip)", 0.6, 1.0, "viridis"),
              (sl(vols["nc"]), "converging: effective number of\nresolved views $N_{eff}$", 0, 73, "magma"),
              (sl(vols["np"]), "parallel 2 mm: effective number of\nresolved views $N_{eff}$", 0, 73, "magma"),
              (sl(vols["nc"]) / sl(vols["np"]), "$N_{eff}$ ratio, converging / parallel", 0.4, 1.1, "RdBu")]
    for a_, (img, title, lo, hi, cm) in zip(axs, panels):
        im = a_.imshow(img, origin="lower", extent=ext, vmin=lo, vmax=hi, cmap=cm)
        a_.set_title(title, fontsize=10)
        a_.set_xlabel("x (mm)")
        th = np.linspace(0, 2 * np.pi, 200)
        for rr in (80, 95):
            a_.plot(rr * np.cos(th), rr * np.sin(th), color="w" if cm != "RdBu" else "k", lw=0.6, ls="--")
        plt.colorbar(im, ax=a_, fraction=0.046, pad=0.03)
    axs[0].set_ylabel("z (mm)")
    fig.suptitle("Coronal slice through the helmet centre (y = 0); dashed circles r = 80 and 95 mm; from the full-system SRMs "
                 "(depth of interaction included, no shield)", fontsize=10)
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "views.png", dpi=170)
    (OUT / "views.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
