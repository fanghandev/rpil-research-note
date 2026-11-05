"""Shared helpers for Phase 0: evaluation points, spot statistics (FWHM, RMS) of continuous and pixel-binned positions."""
import numpy as np

POINTS = {"centre": (0.0, 0.0, 0.0)}
for _r in (0, 30, 60, 80, 95):
    POINTS[f"LIR r={_r}"] = (_r * np.cos(np.radians(30)), _r * np.sin(np.radians(30)), 25.5)
POINTS["uniform r=60"] = (60.0, 0.0, -70.0)
DESIGNS = {"mix": None, "A": 0, "B": 1, "C": 2, "D": 3}  # None = variant index mod 4 (the current map)
A_CONV = 2.0 / 35.0  # converging pixel pitch per unit distance from the pinhole (readout.A_CONV)


def _cross(v, k, half, step):
    """Linear-interpolated index of the half-level crossing going outward from the peak bin k."""
    i = k
    while 0 <= i + step < len(v) and v[i] > half:
        i += step
    if not (0 <= i + step < len(v)) and v[i] > half:
        return float(i)
    j = i - step
    return j + step * (v[j] - half) / (v[j] - v[i]) if v[j] != v[i] else float(j)


def fwhm_cont(u, min_n=500):
    """FWHM, trimmed RMS (within +-3 FWHM of the median) and plain RMS of a continuous 1D sample (box or triangle shaped
    profiles: half of the maximum of the 3-bin-smoothed histogram, bin = FWHM/24)."""
    u = np.asarray(u, float)
    if len(u) < min_n:
        return dict(fwhm=np.nan, rms=np.nan, rms_all=np.nan, n=len(u))
    med = np.median(u)
    lo, hi = np.percentile(u, [0.5, 99.5])
    w = None
    for it in range(2):
        if it == 0:
            edges = np.linspace(lo, hi, 151)
        else:
            edges = np.arange(med - 3 * w, med + 3 * w, w / 24.0)
        h, _ = np.histogram(u, bins=edges)
        hs = np.convolve(h, np.ones(3) / 3, mode="same")
        k = int(np.argmax(hs))
        half = hs[k] / 2
        l, r = _cross(hs, k, half, -1), _cross(hs, k, half, 1)
        w = (r - l) * (edges[1] - edges[0])
    keep = np.abs(u - med) < 3 * w
    return dict(fwhm=float(w), rms=float(u[keep].std()), rms_all=float(u.std()), n=len(u))


def fwhm_pixels(profile):
    """FWHM (pixel units) of a binned profile: linear interpolation between pixel centres, outward from the peak pixel."""
    p = np.asarray(profile, float)
    k = int(np.argmax(p))
    half = p[k] / 2
    return float(_cross(p, k, half, 1) - _cross(p, k, half, -1))


def rms_pixels(profile, trim=None):
    """RMS (pixel units) of the pixel-centre distribution, optionally within +-trim pixels of the peak."""
    p = np.asarray(profile, float)
    c = np.arange(len(p))
    if trim is not None:
        k = int(np.argmax(p))
        m = np.abs(c - k) <= trim
        p, c = p[m], c[m]
    mu = (p * c).sum() / p.sum()
    return float(np.sqrt((p * (c - mu) ** 2).sum() / p.sum()))


def directional(x, y):
    """Continuous FWHM/RMS along module axes u (x), v (y), the two diagonals and, for an off-axis spot, radial / tangential."""
    out = {}
    s2 = np.sqrt(0.5)
    dirs = {"u": (1, 0), "v": (0, 1), "d1": (s2, s2), "d2": (s2, -s2)}
    cx, cy = np.median(x), np.median(y)
    if np.hypot(cx, cy) > 3.0:
        ph = np.arctan2(cy, cx)
        dirs["rad"] = (np.cos(ph), np.sin(ph))
        dirs["tan"] = (-np.sin(ph), np.cos(ph))
    for k, (a, b) in dirs.items():
        out[k] = fwhm_cont(a * x + b * y)
    return out


def binned_phase_avg(t, n_phase=8, size=25):
    """Pixel-binned marginal of positions t in pixel units (pixel edges at integers, array centred): FWHM (pixel units)
    and RMS averaged over n_phase sub-pixel shifts of the grid. Returns (fwhm, rms)."""
    fw, rm = [], []
    for ph in np.arange(n_phase) / n_phase:
        i = np.floor(t + ph + size / 2).astype(int)
        i = i[(i >= 0) & (i < size)]
        pr = np.bincount(i, minlength=size).astype(float)
        fw.append(fwhm_pixels(pr))
        rm.append(rms_pixels(pr, trim=8))
    return float(np.mean(fw)), float(np.mean(rm))
