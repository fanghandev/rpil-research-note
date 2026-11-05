"""Phase 0 gammart MC: point source, one design, one point; per module (a) first-interaction (primary photon, Rayleigh counted)
probability and the continuous spot of the first-interaction positions, (b) the pixel-binned spot (parallel 2 mm, converging)
of the first interactions (phase-averaged over 8 grid shifts) and of the in-window readout events (block centroid, 11.8 % blur,
126-154 keV) with the real pixel grids, (c) mean depth.  Scene: the brain scene with STL shield, world in vacuum, no phantom.

    python phase0_mc.py --design mix --point centre --photons 4e9 --out out/mc_mix_centre.json
"""
import argparse, json, sys, time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p0lib as P
from gammart import readout as R
from gammart.compile.compiler import compile_scene
from gammart.ops import GammaTracer, isotropic_directions
from gammart.scene.brain_spect import build_brain_spect_scene, module_table

N_MOD, NPIX = 73, 25
MIN_N = 1500


def run(design, point, photons, seed, batch=1 << 24):
    v = P.DESIGNS[design]
    variants = np.arange(N_MOD) % 4 if v is None else np.full(N_MOD, v)
    tab = module_table()
    sc = build_brain_spect_scene(variants=variants)
    sc.world_material = "Vacuum"
    tracer = GammaTracer(compile_scene(sc))
    rot, pin = tab["rotation"], tab["pinhole"]
    n_cells = NPIX * NPIX
    gen = torch.Generator(device="cuda").manual_seed(seed)
    rng = np.random.default_rng(seed + 1000)
    cen = torch.as_tensor(point, dtype=torch.float32, device="cuda")
    fi = [[] for _ in range(N_MOD)]   # first-interaction local positions of primary photons
    ce = [[] for _ in range(N_MOD)]   # in-window primary events: centroid (continuous)
    cv_all = np.zeros((N_MOD, NPIX, NPIX)); pa_all = np.zeros((N_MOD, NPIX, NPIX))
    cv_pr = np.zeros((N_MOD, NPIX, NPIX)); pa_pr = np.zeros((N_MOD, NPIX, NPIX))
    n_fi = np.zeros(N_MOD); n_win_prim = np.zeros(N_MOD); n_win = np.zeros(N_MOD)
    t0 = time.time()
    n_total = int(photons)
    for k, s in enumerate(range(0, n_total, batch)):
        m = min(batch, n_total - s)
        d = isotropic_directions(m, generator=gen)
        o = cen.expand(m, 3).contiguous()
        h, _ = tracer.transport(o, d, R.E0_KEV, seed=seed * 100000 + k, hits_per_photon=0.02, record_all=True)
        sel = h.det >= 0
        det = h.det[sel].long().cpu().numpy()
        mod = det // n_cells
        ph = h.photon[sel].long().cpu().numpy() + s
        pos = h.pos[sel].double().cpu().numpy()
        ed = h.edep[sel].double().cpu().numpy()
        order = h.order[sel].long().cpu().numpy()
        local = np.einsum("nji,nj->ni", rot[mod], pos - pin[mod])
        key = ph * N_MOD + mod
        ev = R.block_events(key, local, ed)
        emod = (ev["event"] % N_MOD).astype(int)
        eb = R.blur_energy(ev["energy"], rng)
        win = (eb > R.WINDOW_KEV[0]) & (eb < R.WINDOW_KEV[1])
        np.add.at(n_win, emod, win)
        cix, ciy = R.converging_pixel(ev["x"], ev["y"], ev["z"])
        pix, piy = R.parallel_pixel(ev["x"], ev["y"])
        o2 = np.lexsort((order, key))
        ks = key[o2]
        first_all = o2[np.r_[True, ks[1:] != ks[:-1]]]
        k_all = key[first_all]
        prim_all = order[first_all] == 0
        loc = np.searchsorted(k_all, ev["event"])
        assert np.array_equal(k_all[loc], ev["event"])
        wp = win & prim_all[loc]
        for arr, arr_p, ix, iy in ((cv_all, cv_pr, cix, ciy), (pa_all, pa_pr, pix, piy)):
            ok = win & (ix >= 0)
            np.add.at(arr, (emod[ok], ix[ok], iy[ok]), 1)
            ok = wp & (ix >= 0)
            np.add.at(arr_p, (emod[ok], ix[ok], iy[ok]), 1)
        np.add.at(n_win_prim, emod[wp], 1)
        # first-interaction positions of primaries
        fp = first_all[prim_all]
        fm = (k_all[prim_all] % N_MOD).astype(int)
        np.add.at(n_fi, fm, 1)
        for mm in np.unique(fm):
            fi[mm].append(local[fp[fm == mm]].astype(np.float32))
        # centroids of in-window primary events
        for mm in np.unique(emod[wp]):
            q = wp & (emod == mm)
            ce[mm].append(np.stack([ev["x"][q], ev["y"][q], ev["z"][q]], 1).astype(np.float32))
        if k % 20 == 0:
            print(f"batch {k}: {time.time() - t0:.0f} s, first interactions {int(n_fi.sum())}", flush=True)
    res = {"design": design, "point": list(point), "photons": n_total, "seed": seed, "wall_s": time.time() - t0, "modules": {}}
    for mm in range(N_MOD):
        if n_fi[mm] < MIN_N:
            if n_fi[mm] > 0:
                res["modules"][str(mm)] = {"n_fi": int(n_fi[mm]), "p_fi": float(n_fi[mm] / n_total), "n_win_prim": float(n_win_prim[mm]),
                                           "p_win_prim": float(n_win_prim[mm] / n_total), "p_win": float(n_win[mm] / n_total)}
            continue
        q = np.concatenate(fi[mm]).astype(np.float64)
        x, y, z = q[:, 0], q[:, 1], q[:, 2]
        sdep = -z
        sbar = float(sdep.mean())
        xn, yn = x * sbar / sdep, y * sbar / sdep   # positions carried along the ray to the mean-depth plane
        r = {"n_fi": int(n_fi[mm]), "p_fi": float(n_fi[mm] / n_total), "p_win_prim": float(n_win_prim[mm] / n_total),
             "p_win": float(n_win[mm] / n_total), "mean_s": sbar, "depth_sd": float(sdep.std()),
             "centre_xy": [float(np.median(x)), float(np.median(y))],
             "raw": P.directional(x, y), "norm": P.directional(xn, yn)}
        # pixel-binned first interactions, phase-averaged (parallel: 2 mm pixels; converging: coordinate x / (a s))
        bp, bc = {}, {}
        for ax, (c, cn) in {"u": (x, xn), "v": (y, yn)}.items():
            f, rm = P.binned_phase_avg(c / 2.0)
            bp[ax] = {"fwhm": f * 2.0, "rms": rm * 2.0}
            f, rm = P.binned_phase_avg(c / (P.A_CONV * sdep))
            bc[ax] = {"fwhm": f * P.A_CONV * sbar, "rms": rm * P.A_CONV * sbar}   # mm at the mean-depth plane
        r["bin_fi_parallel"], r["bin_fi_conv"] = bp, bc
        # readout-binned (real grids): marginals of the in-window maps, all events and primaries only
        for nm, mp, tag in (("cv", cv_all, "all"), ("pa", pa_all, "all"), ("cv", cv_pr, "prim"), ("pa", pa_pr, "prim")):
            m2 = mp[mm]
            unit = (P.A_CONV * sbar) if nm == "cv" else 2.0
            r[f"readout_{nm}_{tag}"] = {ax: {"fwhm": P_f * unit, "rms": P_r * unit} for ax, (P_f, P_r) in
                                        {"u": (P.fwhm_pixels(m2.sum(1)), P.rms_pixels(m2.sum(1), 8)),
                                         "v": (P.fwhm_pixels(m2.sum(0)), P.rms_pixels(m2.sum(0), 8))}.items()}
        if ce[mm]:
            c3 = np.concatenate(ce[mm]).astype(np.float64)
            sd = -c3[:, 2]
            r["readout_centroid"] = {"n": len(c3), "u": P.fwhm_cont(c3[:, 0]), "v": P.fwhm_cont(c3[:, 1]), "mean_s": float(sd.mean())}
        res["modules"][str(mm)] = r
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--point", nargs="+", required=True, help="names from p0lib.POINTS")
    ap.add_argument("--photons", type=float, default=4e9)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--outdir", required=True)
    a = ap.parse_args()
    Path(a.outdir).mkdir(parents=True, exist_ok=True)
    for name in a.point:
        res = run(a.design, P.POINTS[name], a.photons, a.seed)
        res["point_name"] = name
        f = Path(a.outdir) / f"mc_{a.design}_{name.replace(' ', '_').replace('=', '')}.json"
        f.write_text(json.dumps(res))
        print("wrote", f, f"{res['wall_s']:.0f} s", flush=True)


if __name__ == "__main__":
    main()
