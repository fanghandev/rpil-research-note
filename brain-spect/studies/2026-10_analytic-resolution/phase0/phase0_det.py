"""Phase 0 deterministic gammart responses: first-interaction probability per pixel of every module for a point source,
parallel 2 mm pixels (BrainSRM) and converging pixels (WP3 scene), designs mix / A / B / C / D, all evaluation points.

    python phase0_det.py --out out/det.npz
"""
import argparse, sys, time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lir"))
import p0lib as P
from gammart.design.brain import BrainSRM
from lir_build import ConvergingBrainSRM


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meshes", default="out/wp2/brain_meshes")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    names = list(P.POINTS)
    pts = np.array([P.POINTS[n] for n in names])
    out = {"names": np.array(names), "points": pts}
    for d, v in P.DESIGNS.items():
        variants = np.arange(73) % 4 if v is None else np.full(73, v)
        t0 = time.time()
        for kind in ("parallel", "conv"):
            s = BrainSRM(variants=variants) if kind == "parallel" else ConvergingBrainSRM(variants, a.meshes)
            cols = s.columns(pts, batch=len(pts)).cpu().numpy()
            out[f"{d}_{kind}_pix"] = cols[:, :73 * 625].reshape(len(pts), 73, 25, 25)
            if kind == "conv":
                out[f"{d}_conv_outside"] = cols[:, 73 * 625:]
            del s
            torch.cuda.empty_cache()
        print(d, f"{time.time() - t0:.0f} s", flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, **out)


if __name__ == "__main__":
    main()
