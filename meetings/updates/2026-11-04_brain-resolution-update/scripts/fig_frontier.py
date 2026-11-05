"""Resolution-sensitivity frontier of one module at the helmet centre (classic formulas, square knife edge).

For a pinhole of side w (0.3-3 mm) and a detector option, one module at the helmet centre (b = 149.6 mm, normal
incidence) has
    sensitivity  g = A_eff(w) / (4 pi b^2),  A_eff = w^2 + 2wt/mu + 2t^2/mu^2       (Paix = Metzler & Moore 2020, eq. 25)
    resolution   R = sqrt(R_g^2 + R_i^2),    R_g = (w + ln2 t/mu)(b+f)/f,  R_i = p_eff b / f
Detector options (p_eff b / f):
    2 mm parallel pixels             2 b / 27
    converging pixels                2 b / 35            (pitch 2.0 mm at 35 mm from the pinhole)
    1 mm parallel pixels             1 b / 27            (hypothetical)
    2 mm pixels, f = 54 mm           2 b / 54, and R_g with f = 54 (hypothetical: pinhole-detector distance doubled at the
                                                          same b; ignores the smaller field of view per module and the
                                                          module-radius limit)
    converging / parallel + LIOB decoding (estimate): R_i multiplied by sqrt(1 + 12 var), var = mean per-axis variance
        (pixel^2) of the decoding displacement in the LIOB confusion matrices (shrinkage ML), i.e. the pixel box RMS
        widened by the decoding spread.
Writes ../img/frontier.png and ../img/frontier.json.
"""

import os
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "img"
B, F, MU, T = 149.6, 27.0, 3.63, 1.0
WIDTHS = {"A": 0.556, "B": 0.797, "C": 1.215, "D": 2.007}
DEC = Path(f"{os.path.expanduser('~')}/Work/RPIL/QMIRT/model_LIOB/out/brain_confusion")


def decoding_factor(name):
    P = np.load(DEC / f"{name}.npz")["P_shrink"][:625, :625].astype(float)
    P /= P.sum(1, keepdims=True)
    ix, iy = np.divmod(np.arange(625), 25)
    var = 0.5 * ((P * (ix[None] - ix[:, None]) ** 2).sum(1) + (P * (iy[None] - iy[:, None]) ** 2).sum(1))
    return float(np.sqrt(1 + 12 * var.mean()))


def module(w, ri, f=F):
    a_eff = w * w + 2 * w * T / MU + 2 * T * T / MU ** 2
    rg = (w + np.log(2) * T / MU) * (B + f) / f
    return a_eff, np.hypot(rg, ri)


def main():
    OUT.mkdir(exist_ok=True)
    f_conv, f_par = decoding_factor("P_converging"), decoding_factor("P_parallel")
    opts = [  # label, R_i, colour, style, f
        ("2 mm parallel pixels", 2 * B / 27, "#555555", "-", F),
        ("converging pixels, ideal decoding", 2 * B / 35, "#0072b2", "-", F),
        (f"2 mm parallel + LIOB decoding (est., ×{f_par:.2f})", 2 * B / 27 * f_par, "#555555", "--", F),
        (f"converging + LIOB decoding (est., ×{f_conv:.2f})", 2 * B / 35 * f_conv, "#0072b2", "--", F),
        ("1 mm parallel pixels (hypothetical)", 1 * B / 27, "#009e73", "-", F),
        ("2 mm pixels, pinhole-detector 54 mm (hypothetical)", 2 * B / 54, "#cc79a7", "-", 2 * F),
    ]
    a_ref = module(WIDTHS["A"], 0)[0]
    w = np.linspace(0.3, 3.0, 300)
    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    res = {"decoding_factor": {"converging": f_conv, "parallel": f_par}, "options": {}}
    for lab, ri, col, ls, f in opts:
        a, r = module(w, ri, f)
        ax.plot(a / a_ref, r, ls, color=col, lw=2, label=lab)
        ax.axhline(ri, color=col, ls=ls, lw=0.6, alpha=0.5)
        pts = {}
        for k, wk in WIDTHS.items():
            ak, rk = module(wk, ri, f)
            ax.plot(ak / a_ref, rk, "o", color=col, ms=5)
            pts[k] = {"rel_sensitivity": round(float(ak / a_ref), 3), "R_mm": round(float(rk), 2)}
            if lab == "2 mm parallel pixels":
                ax.annotate(k, (ak / a_ref, rk), textcoords="offset points", xytext=(4, 5), fontsize=10)
        res["options"][lab] = {"R_i_mm": round(float(ri), 2), "apertures": pts}
    ax.set_xscale("log")
    ax.set_xlabel("relative sensitivity of one module (aperture A = 1)")
    ax.set_ylabel("module resolution at the object, FWHM (mm)")
    ax.set_title("One module at the helmet centre (b = 149.6 mm): thin lines = detector floor $R_i$", fontsize=11)
    ax.set_ylim(0, 24)
    ax.grid(True, which="both", color="#e5e5e5")
    ax.legend(fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "frontier.png", dpi=200)
    (OUT / "frontier.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
