"""Ideal local impulse response of a gammart system matrix, as dev/python/ideal_lir.py does for the GATE SRM:

    R_alpha e_j = H^T (H H^T + alpha I)^-1 H e_j ,   alpha = frac * lambda_max(H H^T)

Cases (--case): current_parallel (iv), current_conv (i), uniform_parallel (ii), uniform_conv (iii)
  current = variant index of the GATE provenance (= index mod 4: 0.556/0.797/1.215/2.007 mm), uniform = 1.215 mm everywhere.
  parallel = 2 mm pixels of the crystal grid (BrainSRM); conv = converging pixels (ConvergingBrainSRM, WP3 scene;
  the CsI outside the outer walls is dropped, "lost" bound).
H: 2 mm voxel grid (144^3, centres at odd mm), voxels within --fov mm of the helmet centre, the BrainSRM QMC rule, no shield;
entries below --rel-threshold of the column maximum dropped.  The LIR voxels are those of ideal_lir.py (1 mm grid, 210^3,
slice z index 130 = z 25.5 mm).  e_j and the response are evaluated at the exact 1 mm voxel centres with the same QMC
columns (H e_j = column at the point; the response at a slice voxel v is column(v) . u), the Gram operator uses the 2 mm voxels.

    python lir_build.py --case current_parallel --out out/current_parallel
"""
import argparse, json, sys, time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
import torch

from gammart import srm
from gammart.compile.compiler import compile_scene
from gammart.design.brain import ENERGY_KEV, BrainSRM, RuleConfig, knife_edge_decay, variant_widths
from gammart.ops import GammaTracer
from gammart.scene.brain_converging import converging_full_scene
from gammart.scene.brain_spect import module_table

GRID = 210
VOXELS = [(104, 104, 130), (130, 120, 130), (156, 134, 130), (174, 144, 130), (187, 152, 130)]
RADII = [0, 30, 60, 80, 95]
FRACS = (1e-2, 1e-3, 1e-4)
N_CELLS = 625
N_MOD = 73


class ConvergingBrainSRM(BrainSRM):
    """BrainSRM rule on the converging-pixel scene (copy of examples/wp3_recon.py, which is left untouched)."""

    def __init__(self, variants, mesh_dir, device="cuda"):
        self.variants = np.asarray(variants, int)
        self.widths = variant_widths(self.variants)
        self.rule = RuleConfig(geometric_filter=False)
        self.scene = compile_scene(converging_full_scene(self.variants, mesh_dir))
        self.tracer = GammaTracer(self.scene)
        self.mu = torch.tensor(self.scene.materials.mu_total(ENERGY_KEV), dtype=torch.float64, device=device)
        table = module_table()
        self.pinhole = np.asarray(table["pinhole"], float)
        self.axes = np.asarray(table["rotation"], float)
        mu_w = float(self.mu[self.scene.materials.names.index("Tungsten")])
        r = self.rule
        k = knife_edge_decay(mu_w, widths=self.widths) * r.decay_scale
        n_max = max(r.n0, r.n_max) if r.near_mm > 0 else r.n0
        ax = self.axes
        self.planes = srm.QmcPlanes(self.pinhole, ax[:, :, 0], ax[:, :, 1], ax[:, :, 2], self.widths / 2, r.margin_mm, k,
                                    srm.sobol_points(n_max, r.seed), r.voxel_mm, r.share, grid=None, n_base=r.n0,
                                    near_mm=r.near_mm, geometric_filter=False)


def make_system(case, meshes):
    cur = np.arange(N_MOD) % 4
    uni = np.full(N_MOD, 2)
    if case == "current_parallel":
        return BrainSRM(variants=cur)
    if case == "uniform_parallel":
        return BrainSRM(variants=uni)
    if case == "current_conv":
        return ConvergingBrainSRM(cur, meshes)
    if case == "uniform_conv":
        return ConvergingBrainSRM(uni, meshes)
    raise ValueError(case)


def columns(system, c, n_rows=N_MOD * N_CELLS, batch=500):
    """(n, 45625) float64 on the GPU, pixel rows only (the outside-wall elements of the converging scene dropped)."""
    out = torch.empty(len(c), n_rows, dtype=torch.float64, device="cuda")
    buf = torch.zeros(min(batch, len(c)), system.scene.n_det_elements, dtype=torch.float64, device="cuda")
    for i in range(0, len(c), batch):
        cc = c[i:i + batch]
        b = buf[:len(cc)].zero_()
        srm.pinhole_columns(system.tracer, cc, None, system.planes, system.mu, out=b)
        out[i:i + len(cc)] = b[:, :n_rows]
    return out


def build_H(system, fov, rel, batch, max_voxels, log):
    a = (np.arange(144) - 143 / 2) * 2.0
    xx, yy, zz = np.meshgrid(a, a, a, indexing="ij")
    cen = np.stack([xx.ravel(), yy.ravel(), zz.ravel()], 1)
    vox = np.flatnonzero(np.linalg.norm(cen, axis=1) <= fov)
    if max_voxels:
        vox = vox[np.random.default_rng(0).choice(len(vox), max_voxels, replace=False)]
        vox.sort()
    cen = cen[vox]
    rows, cols, vals, drop = [], [], [], []
    buf = torch.zeros(batch, system.scene.n_det_elements, dtype=torch.float64, device="cuda")
    t0 = time.time()
    for s in range(0, len(vox), batch):
        b = buf[:min(batch, len(vox) - s)].zero_()
        srm.pinhole_columns(system.tracer, cen[s:s + batch], None, system.planes, system.mu, out=b)
        b = b[:, :N_MOD * N_CELLS]
        keep = (b >= rel * b.max(dim=1, keepdim=True).values) & (b > 0)
        tot = b.sum(1)
        drop.append(((tot - torch.where(keep, b, 0).sum(1)) / tot.clamp_min(1e-300)).cpu().numpy())
        vi, di = torch.nonzero(keep, as_tuple=True)
        rows.append(di.int().cpu().numpy())
        cols.append((vi + s).int().cpu().numpy())
        vals.append(b[vi, di].float().cpu().numpy())
        if (s // batch) % 100 == 0:
            log(f"H {s + len(b):,}/{len(vox):,} voxels, {time.time() - t0:.0f} s")
    H = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(N_MOD * N_CELLS, len(vox)))
    H.sort_indices()
    return H, np.concatenate(drop), len(vox)


F32 = [False]


def to_torch(m):
    return torch.sparse_csr_tensor(torch.from_numpy(m.indptr.astype(np.int32)), torch.from_numpy(m.indices.astype(np.int32)),
                                   torch.from_numpy(m.data.astype(np.float32 if F32[0] else np.float64)), size=m.shape).to("cuda")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--meshes", default="out/wp2/brain_meshes")
    ap.add_argument("--fov", type=float, default=120.0)
    ap.add_argument("--rel-threshold", type=float, default=1e-4)
    ap.add_argument("--tol", type=float, default=1e-6)
    ap.add_argument("--max-iter", type=int, default=3000)
    ap.add_argument("--max-voxels", type=int, default=0, help="test mode: random subset of the voxels")
    ap.add_argument("--noise-c1", type=float, default=0.0, help="emulate the Monte Carlo noise of the GATE SRM: counts = Poisson(c1 * probability) "
                    "per 1 mm voxel (GATE: c1 = 2.5e6, ~1555 counts per voxel in all heads); 2 mm Gram columns use 8 c1 (same counts per volume)")
    ap.add_argument("--f32", action="store_true", help="float32 matrices on the GPU (12 GB card); vectors stay float64")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    F32[0] = a.f32
    out.mkdir(parents=True, exist_ok=True)
    t00 = time.time()

    def log(s):
        print(f"[{time.time() - t00:7.0f} s] {s}", flush=True)

    system = make_system(a.case, a.meshes)
    log(f"scene ready, n_det {system.scene.n_det_elements}")
    H, dropped, nv = build_H(system, a.fov, a.rel_threshold, 512, a.max_voxels, log)
    log(f"H {H.shape}, nnz {H.nnz:,} ({H.nnz / nv:.0f} per voxel), dropped share mean {dropped.mean():.2e}")
    if a.noise_c1 > 0:
        rng = np.random.default_rng(5)
        H.data = rng.poisson(8 * a.noise_c1 * H.data.astype(np.float64)).astype(np.float32)
        H.eliminate_zeros()
        log(f"noise emulation c1={a.noise_c1:g}: nnz {H.nnz:,}")
    Hg = to_torch(H)
    Hc = H.tocsc()
    Htg = to_torch(sp.csr_matrix((Hc.data, Hc.indices, Hc.indptr), shape=(H.shape[1], H.shape[0])))
    del Hc
    alpha = [0.0]
    extra = [None]

    def gram(v):
        if F32[0]:
            o = torch.mv(Hg, torch.mv(Htg, v.float())).double() + alpha[0] * v
        else:
            o = torch.mv(Hg, torch.mv(Htg, v)) + alpha[0] * v
        if extra[0] is not None:   # noise mode: the voxel j itself is part of the sum, as in the GATE SRM
            o = o + extra[0] * torch.dot(extra[0], v)
        return o

    v = torch.rand(H.shape[0], dtype=torch.float64, device="cuda")
    lam = 0.0
    for _ in range(40):
        w = gram(v)
        lam = float(torch.dot(v, w) / torch.dot(v, v))
        v = w / torch.linalg.norm(w)
    log(f"lambda_max {lam:.5g}")

    # LIR voxels (1 mm grid centres)
    pts = np.array([[i - 104.5, j - 104.5, k - 104.5] for i, j, k in VOXELS])
    He = columns(system, pts)  # (5, M)
    if a.noise_c1 > 0:
        He = torch.poisson(a.noise_c1 * He)
    U = np.zeros((len(FRACS), len(VOXELS), H.shape[0]))
    info = []
    for jv, (p, r) in enumerate(zip(pts, RADII)):
        b = He[jv]
        if a.noise_c1 > 0:
            extra[0] = b
        u = torch.zeros_like(b)
        for fi, frac in enumerate(FRACS):  # largest alpha first, warm start
            alpha[0] = frac * lam
            t0 = time.time()
            x = u.clone()
            res = b - gram(x)
            pdir = res.clone()
            rs = torch.dot(res, res)
            bn = float(torch.linalg.norm(b))
            n_it = a.max_iter
            for k in range(1, a.max_iter + 1):
                ap_ = gram(pdir)
                st = rs / torch.dot(pdir, ap_)
                x += st * pdir
                res -= st * ap_
                rsn = torch.dot(res, res)
                if float(torch.sqrt(rsn)) / bn < a.tol:
                    n_it = k
                    break
                pdir = res + (rsn / rs) * pdir
                rs = rsn
            u = x
            U[fi, jv] = u.cpu().numpy()
            info.append({"radius_mm": r, "alpha_fraction": frac, "cg_iterations": n_it, "seconds": time.time() - t0})
            log(f"r={r} alpha={frac:g}: CG {n_it} it, {time.time() - t0:.0f} s")
    del Hg, Htg

    # response on the 1 mm slice z = 25.5 (z index 130): column(v) . u_j for every slice voxel within FOV
    ii, jj = np.meshgrid(np.arange(GRID), np.arange(GRID), indexing="ij")
    sx, sy = (ii.ravel() - 104.5), (jj.ravel() - 104.5)
    sz = np.full_like(sx, 25.5)
    ok = np.flatnonzero(np.sqrt(sx**2 + sy**2 + sz**2) <= 135.0)
    Ug = torch.as_tensor(U.reshape(-1, H.shape[0]).T.copy(), dtype=torch.float64, device="cuda")  # (M, 15)
    resp = np.zeros((GRID * GRID, Ug.shape[1]), dtype=np.float32)
    cs = np.stack([sx, sy, sz], 1)
    for s in range(0, len(ok), 500):
        idx = ok[s:s + 500]
        C = columns(system, cs[idx], batch=500)
        if a.noise_c1 > 0:
            C = torch.poisson(a.noise_c1 * C)
            for jv, (i, j, _) in enumerate(VOXELS):
                w = np.flatnonzero(idx == i * GRID + j)
                if len(w):
                    C[int(w[0])] = He[jv]
        resp[idx] = (C @ Ug).cpu().numpy()
        if (s // 500) % 20 == 0:
            log(f"slice {s}/{len(ok)}")
    resp = resp.reshape(GRID, GRID, len(FRACS), len(VOXELS))
    save = {f"r{r:03d}_a{f:g}": resp[:, :, fi, jv] for fi, f in enumerate(FRACS) for jv, r in enumerate(RADII)}
    np.savez_compressed(out / "lir_slices.npz", **save)
    (out / "lir_info.json").write_text(json.dumps({
        "case": a.case, "lambda_max": lam, "nnz": int(H.nnz), "n_voxels": int(nv), "fov_mm": a.fov, "rel_threshold": a.rel_threshold,
        "dropped_share_mean": float(dropped.mean()), "runs": info, "wall_s": time.time() - t00,
        "He_column_sums": He.sum(1).cpu().tolist()}, indent=1))
    log("done")


if __name__ == "__main__":
    main()
