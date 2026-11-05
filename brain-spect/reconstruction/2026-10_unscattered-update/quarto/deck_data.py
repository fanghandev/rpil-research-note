"""Data helpers for slides.qmd: every number on the slides is read here from the analysis outputs
(dev/python/unscattered_update_analysis.py, osem_reference_*), so re-running an analysis and
re-rendering updates the deck. Missing outputs give empty data, so the deck renders while runs are
still going."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = (HERE / "../../../python").resolve()
RUNS = PY / "brain_phantom_recon/unscattered_update_2026-10-16"
REF = PY / "brain_phantom_recon/osem_reference_2026-10-15"


def _json(path):
    return json.loads(path.read_text()) if path.exists() else {}


UU = _json(RUNS / "analysis/metrics.json")
M = UU.get("metrics", {})
META = UU.get("runs", {})
SUPPORT = _json(RUNS / "analysis/support_check.json")
REF_ENS = _json(REF / "analysis/ensemble.json")
REF_STAB = _json(REF / "analysis/stability.json")


def m(run, it, key, f=0):
    """Metric of a run at a saved iteration (f: post-filter FWHM in mm); None if not there yet."""
    try:
        return M[run][str(f)][str(it)][key]
    except KeyError:
        return None


def n(v): return "…" if v is None else f"{v:,}"
def f1(v): return "…" if v is None else f"{v:.1f}"
def f2(v): return "…" if v is None else f"{v:.2f}"
def f3(v): return "…" if v is None else f"{v:.3f}"
def pct(v, d=1): return "…" if v is None else f"{100 * v:.{d}f} %"


def support_diff(max_it, keys_exclude=("sphere_6.4mm",), f=0):
    """Largest |osem8_ac − reference (support 1000)| over the inserts, recovery, rim / centre and CoV,
    at saved iterations ≤ max_it; the 6.4 mm sphere (bootstrap SD 0.03–0.23) is reported separately."""
    try:
        a, b = M["osem8_ac"][str(f)], M["reference_support1000"][str(f)]
    except KeyError:
        return None
    keys = [k for k in a["1"] if (k.startswith(("rods_", "sphere_")) or k in ("recovery", "rim_over_centre", "cov_voxel"))
            and k not in keys_exclude]
    return max(abs(a[it][k] - b[it][k]) for it in b if int(it) <= max_it for k in keys)


def ref_change(key, f):
    """OSEM reference: change of a metric over 4000 → 8000 updates, and its bootstrap SD at 8000."""
    try:
        s = REF_STAB[str(f)][key]
        return s["change_last_doubling"], s["sd_8000"]
    except KeyError:
        return None, None


def ref_noise(f, it=1000):
    try:
        return REF_ENS["ensemble"][str(f)][str(it)]["ensemble_cov"]
    except KeyError:
        return None


def ref_change_cell(key, f):
    c, s = ref_change(key, f)
    return "…" if c is None else f"{c:+.3f} ({s:.3f})"


def at_updates(run, u, key, f=0):
    """Metric at u updates, interpolated linearly in log(updates) between the run's saved points."""
    import math
    try:
        ups = META[run]["updates"]
        its = META[run]["iterations"]
        vals = [M[run][str(f)][str(i)][key] for i in its]
    except KeyError:
        return None
    if u in ups:
        return vals[ups.index(u)]
    for (u0, v0), (u1, v1) in zip(zip(ups, vals), zip(ups[1:], vals[1:])):
        if u0 < u < u1:
            w = (math.log(u) - math.log(u0)) / (math.log(u1) - math.log(u0))
            return v0 + w * (v1 - v0)
    return None


def osem_minus_mlem(u, key, ac="ac", f=0):
    a, b = at_updates(f"osem8_{ac}", u, key, f), at_updates(f"mlem_{ac}", u, key, f)
    return "…" if a is None or b is None else f"{a - b:+.3f}"


TICK = "✓"


def stab_cell(key, f):
    """Change 4000 → 8000 updates with its bootstrap SD; ✓ when the change is below the SD."""
    c, s = ref_change(key, f)
    if c is None:
        return "…"
    return f"{c:+.3f} ± {s:.3f} {TICK}" if abs(c) < s else f"**{c:+.3f}** ± {s:.3f}"


def ref_sd(key, u, f=0):
    """Bootstrap SD of a metric at u updates (OSEM 8 reference)."""
    try:
        return REF_ENS["ensemble"][str(f)][str(u // 8)]["bootstrap_sd"][key]
    except KeyError:
        return None


def om_cell(u, key, f=0):
    """OSEM − MLEM at u updates (with AC), with the bootstrap SD; ✓ when the difference is below it."""
    a, b = at_updates("osem8_ac", u, key, f), at_updates("mlem_ac", u, key, f)
    s = ref_sd(key, u, f)
    if a is None or b is None:
        return "…"
    d = a - b
    if s is None:
        return f"{d:+.3f}"
    return f"{d:+.3f} ± {s:.3f} {TICK}" if abs(d) < s else f"**{d:+.3f}** ± {s:.3f}"


def stab_table():
    """Markdown table (printed from an output: asis cell, so the bold renders): change 4000 → 8000 updates."""
    rows = [("rods 4.8 mm", "rods_4.8mm"), ("rods 6.4 mm", "rods_6.4mm"), ("rods 7.9 mm", "rods_7.9mm"), ("rods 12.7 mm", "rods_12.7mm"),
            ("sphere 9.5 mm", "sphere_9.5mm"), ("sphere 25.4 mm", "sphere_25.4mm"), ("recovery", "recovery")]
    fs = (0, 6, 8, 10)
    out = ["| metric | no filter | 6 mm filter | 8 mm filter | 10 mm filter |", "|:--|:-:|:-:|:-:|:-:|"]
    out += [f"| {lab} | " + " | ".join(stab_cell(key, f) for f in fs) + " |" for lab, key in rows]
    out.append("| noise (ensemble CoV) at 8000 | " + " | ".join(f2(ref_noise(f)) for f in fs) + " |")
    return "\n".join(out)


def om_table():
    """Markdown table: OSEM − MLEM at equal updates, with AC, no filter."""
    rows = [("rods 4.8 mm", "rods_4.8mm"), ("rods 7.9 mm", "rods_7.9mm"), ("rods 12.7 mm", "rods_12.7mm"), ("sphere 9.5 mm", "sphere_9.5mm"),
            ("sphere 25.4 mm", "sphere_25.4mm"), ("recovery", "recovery"), ("spatial CoV", "cov_voxel")]
    us = (160, 400, 1600, 4000)
    out = ["| metric | " + " | ".join(f"{u} updates" for u in us) + " |", "|:--|" + ":-:|" * len(us)]
    out += [f"| {lab} | " + " | ".join(om_cell(u, key) for u in us) + " |" for lab, key in rows]
    return "\n".join(out)
