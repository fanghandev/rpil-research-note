"""Data and table helpers for slides.qmd: every number on the slides is read here from the
analysis outputs, so re-running an analysis and re-rendering updates the deck."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT = HERE.parent
DOC = (REPORT / "../../python/brain_phantom_recon/doc_2026-10-14").resolve()
FIG = DOC / "figures"
EXT = REPORT / "extras"

M = json.loads((DOC / "metrics.json").read_text())
CONV = json.loads((DOC / "convergence" / "metrics.json").read_text())
X = json.loads((EXT / "extras.json").read_text())
# attenuated-SRM check: true phantom forward-projected vs the unscattered data (dev/python/ac_pixel_residuals.py)
AR = {r: json.loads((DOC / "ac_residuals" / f"ac_pixel_residuals_{r}.json").read_text()) for r in ("2mm", "1mm")}


def ar_bins(res, lo=0.0, hi=1.0, key="ac"):
    """(min ratio, max ratio, share of the counts) over transmission bins with > 1e4 counts in [lo, hi)."""
    s = AR[res][key]
    e = s["transmission_bins"]
    sel = [(r, c) for a, r, c in zip(e, s["ratio_by_transmission"], s["counts_by_transmission"])
           if c > 1e4 and lo - 1e-9 <= a < hi - 1e-9]
    return min(r for r, _ in sel), max(r for r, _ in sel), sum(c for _, c in sel) / AR[res]["counts"]

RES = [("2 mm", "2mm"), ("1.5 mm", "1p5mm"), ("1 mm", "1mm")]

# corrections step by step, 2 mm SRM, by row label
STEPS = {
    "0: none": M["2mm_step0_raw"]["in_fov_total"],
    "1: + support": M["2mm_steps1-2_support_tew"]["in_fov_total"],
    "2: + TEW": M["2mm_steps1-2_support_tew"]["full_tew"],
    "3: + AC": M["2mm_step3_ac"]["full_tew"],
    "ideal": M["2mm_step3_ac"]["in_fov_primary"],
}
FIT_KEY = {"0: none": "0: no corrections", "1: + support": "1: + support", "2: + TEW": "2: + TEW",
           "3: + AC": "3: + AC", "ideal": "ideal"}
S0, S1, S2, S3 = (STEPS[k]["400"] for k in list(STEPS)[:4])

# section 2: the unscattered data (in_fov_primary), 2 mm SRM, step by step
USTEPS = {
    "0: none": M["2mm_unscattered_u0_raw"]["in_fov_primary"],
    "1: + support": M["2mm_unscattered_u1_support"]["in_fov_primary"],
    "2: + support + AC": M["2mm_step3_ac"]["in_fov_primary"],
}
UFIT = dict(zip(USTEPS, X["unscattered_fits"]))  # row label -> fit label
U0, U1, U2 = (USTEPS[k]["400"] for k in USTEPS)
B0 = USTEPS["0: none"]  # the bare reconstruction, every saved iteration
BH = X["bare_histogram"]  # its voxel-value histograms by region (make_deck_extras.bare_histogram)
CM = X["correction"]
TW = X["tew_spectrum"]
PP = TW["per_pixel"]


def n(v): return f"{v:,}"
def mc(v): return f"{v / 1e6:.1f} M"  # counts in millions
def f1(v): return f"{v:.1f}"
def f2(v): return f"{v:.2f}"
def pct(v): return f"{v * 100:.1f} %" if v < 0.01 else f"{round(v * 100)} %"


def fwhm(group, label, it, sphere="25.4"):
    return X["sphere_fits"][group][label][str(it)][sphere]["fwhm_mm"]


def sens(key, r):
    rows = X["sensitivity_profile"][key]
    return min(rows, key=lambda q: abs(q["r_mm"] - r))["mean"]


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join([":--"] + [":-:"] * (len(header) - 1)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def steps_table():
    hdr = ["Step (it. 400)", "Outside", "Accuracy", "Rim / centre", "Noise (CoV)",
           "Sphere 25.4", "Sphere 12.7", "Rods 9.5", "Rods 7.9", "FWHM"]
    rows = []
    for lab, d in STEPS.items():
        r = d["400"]
        rows.append([lab, pct(r["outside_fraction"]), f2(r["activity_over_truth"]) + "×", f2(r["rim_over_centre"]),
                     f2(r["cov_voxel"]), f2(r["sphere_25.4mm"]), f2(r["sphere_12.7mm"]), f2(r["rods_9.5mm"]),
                     f2(r["rods_7.9mm"]), f1(fwhm("steps", FIT_KEY[lab], 400)) + " mm"])
    return md_table(hdr, rows)


def u_table(it=400):
    """Section 2 summary: one row per step at one iteration. The sphere FWHM is given for the AC
    row only: without AC the background slopes up towards the wall and the flat-background
    ball-blur fit does not apply."""
    hdr = [f"Step (it. {it})", "Accuracy", "Rim / centre", "Outside", "Noise (CoV)",
           "Sphere 25.4", "Sphere 12.7", "Rods 9.5", "Rods 7.9", "Rods 6.4", "FWHM 25.4"]
    rows = []
    for lab, d in USTEPS.items():
        r = d[str(it)]
        fw = f1(X["unscattered_fits"][UFIT[lab]][str(it)]["25.4"]["fwhm_mm"]) + " mm" if "AC" in lab else "–"
        rows.append([lab, f2(r["activity_over_truth"]) + "×", f2(r["rim_over_centre"]), pct(r["outside_fraction"]),
                     f2(r["cov_voxel"]), f2(r["sphere_25.4mm"]), f2(r["sphere_12.7mm"]), f2(r["rods_9.5mm"]),
                     f2(r["rods_7.9mm"]), f2(r["rods_6.4mm"]), fw])
    return md_table(hdr, rows)


def need_table():
    def row(r, f):
        return [f2(r["rods_7.9mm"]), f2(r["rods_6.4mm"]), f2(r["rods_4.8mm"]), f2(r["sphere_9.5mm"]), f1(f) + " mm"]
    nf2000 = lambda lab: X["sphere_fits"]["noisefree_2000"][lab]["2000"]["25.4"]["fwhm_mm"]
    rows = [
        ["Measured, it. 400", "2 mm", *row(M["2mm_step3_ac"]["full_tew"]["400"], fwhm("resolution", "2 mm", 400))],
        ["", "1 mm", *row(M["1mm_step3_ac"]["full_tew"]["400"], fwhm("resolution", "1 mm", 400))],
        ["Noise-free, it. 400", "2 mm", *row(M["synthetic_noisefree_2mm"]["in_fov_primary"]["400"], fwhm("noisefree", "2 mm", 400))],
        ["", "1 mm", *row(M["synthetic_noisefree_1mm"]["in_fov_primary"]["400"], fwhm("noisefree", "1 mm", 400))],
        ["Noise-free, it. 2,000", "2 mm", *row(CONV["2mm"]["2000"], nf2000("2 mm"))],
        ["", "1 mm", *row(CONV["1mm"]["2000"], nf2000("1 mm"))],
    ]
    return md_table(["Data", "SRM", "Rods 7.9", "Rods 6.4", "Rods 4.8", "Sphere 9.5", "FWHM 25.4"], rows)


def fwhm_table():
    return md_table(["Iteration", "2 mm", "1.5 mm", "1 mm"],
                    [[it, *[f1(fwhm("resolution", lab, it)) for lab, _ in RES]] for it in (100, 400)])


def code_excerpt(path, func, start=None, end=None):
    """Exact source of function `func` in the file `path` (whole, or from the first line containing
    `start` to the first line after it containing `end`), read as text (no import), as a markdown
    code block with its file name and line numbers."""
    import ast
    path = Path(path)
    text = path.read_text()
    node = next(n for n in ast.walk(ast.parse(text)) if isinstance(n, ast.FunctionDef) and n.name == func)
    lines = text.splitlines(keepends=True)[node.lineno - 1:node.end_lineno]
    i0 = 0 if start is None else next(i for i, l in enumerate(lines) if start in l)
    i1 = len(lines) - 1 if end is None else next(i for i, l in enumerate(lines) if i >= i0 and end in l)
    chunk = lines[i0:i1 + 1]
    indent = min(len(l) - len(l.lstrip()) for l in chunk if l.strip())
    body = "".join(l[indent:] if l.strip() else l for l in chunk)
    return f"`{path.name}`, lines {node.lineno + i0}–{node.lineno + i1}:\n\n```python\n{body}```\n"


PYDIR = (REPORT / "../../python").resolve()


def outside_table(its=(5, 20, 100, 400)):
    """Share of the reconstructed activity > 6 mm outside the phantom, per correction step and iteration."""
    rows = [[lab, *[pct(STEPS[lab][str(it)]["outside_fraction"]) for it in its]] for lab in list(STEPS)[:4]]
    return md_table(["Step", *[f"it. {it}" for it in its]], rows)


SUB = json.loads((EXT / "subset_stats.json").read_text())


def subset_table(mode="footprint", it="400"):
    """Per insert: subset mean +- SE (full counts) per grid, paired 2 mm - 1 mm difference +- SE, p."""
    pg, pd = SUB["per_grid"][mode], SUB["paired_2mm_minus_1mm"][mode][it]
    key = lambda n: (0 if n.startswith("sphere") else 1, float(n.split("_")[1][:-2]))
    rows = []
    for name in sorted(pg["2mm"][it], key=key):
        a, b, d = pg["2mm"][it][name], pg["1mm"][it][name], pd[name]
        label = ("Sphere " if name.startswith("sphere") else "Rods ") + name.split("_")[1].replace("mm", " mm")
        rows.append([label, f"{a['mean']:.3f} ± {a['se_full']:.3f}", f"{b['mean']:.3f} ± {b['se_full']:.3f}",
                     f"{d['mean']:+.3f} ± {d['se_full']:.3f}", "< 0.01" if d["p"] < 0.01 else f"{d['p']:.2f}"])
    return md_table(["Insert", "2 mm SRM", "1 mm SRM", "Difference 2 − 1 mm", "p"], rows)


def subset_range(mode="footprint", it="400", kind=None, min_mm=0.0):
    """(min, max) of se_full over the selected inserts (both grids) and max |paired difference|;
    kind = "sphere" / "rods" / None (all), min_mm = smallest diameter included."""
    pg, pd = SUB["per_grid"][mode], SUB["paired_2mm_minus_1mm"][mode][it]
    names = [n for n in pg["2mm"][it] if (kind is None or n.startswith(kind)) and float(n.split("_")[1][:-2]) >= min_mm]
    se = [pg[g][it][n]["se_full"] for g in ("2mm", "1mm") for n in names]
    return min(se), max(se), max(abs(pd[n]["mean"]) for n in names)


def se_text(kind, min_mm=0.0, max_mm=None, mode="footprint"):
    pg = SUB["per_grid"][mode]
    names = [n for n in pg["2mm"]["400"] if n.startswith(kind) and float(n.split("_")[1][:-2]) >= min_mm
             and (max_mm is None or float(n.split("_")[1][:-2]) <= max_mm)]
    se = [pg[g]["400"][n]["se_full"] for g in ("2mm", "1mm") for n in names]
    return f"±{min(se):.3f}–{max(se):.3f}"


def diff_exceeding_se(mode="footprint", it="400"):
    """Inserts whose |paired difference| exceeds the larger of the two grids' standard errors."""
    pg, pd = SUB["per_grid"][mode], SUB["paired_2mm_minus_1mm"][mode][it]
    out = []
    for n, d in pd.items():
        se = max(pg["2mm"][it][n]["se_full"], pg["1mm"][it][n]["se_full"])
        if abs(d["mean"]) > se:
            label = ("sphere " if n.startswith("sphere") else "rods ") + n.split("_")[1].replace("mm", " mm")
            out.append(f"{label} ({d['mean']:+.3f} vs ±{se:.3f})")
    return out
