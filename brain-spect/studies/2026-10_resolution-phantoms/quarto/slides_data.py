"""Data helpers for slides.qmd: every number on the slides is read here from the analysis outputs
(dev/python/resolution_analysis.py, resolution_bootstrap.py, resolution_method_checks.py,
resolution_derenzo_model.py), so re-running an analysis and re-rendering updates the slide deck. Results whose
data is not there yet are left out of the slides (have_air), never shown as gaps."""

import getpass
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PY = (HERE / "../../../python").resolve()
A = PY / "brain_phantom_recon/resolution_2026-10-20/analysis"
CAMPAIGNS = Path(f"/data/{getpass.getuser()}/opengate_sim/data/brain_phantom/ospool")


def _json(path):
    return json.loads(path.read_text()) if path.exists() else {}


MAIN = _json(A / "main.json").get("phantoms", {})
BOOT = _json(A / "boot_stats.json")
CHECKS = _json(A / "method_checks.json")
MODEL = _json(A / "derenzo_model.json")
UPD = {"osem8_ac": 8, "osem8_noac": 8, "osem8_chang": 8, "mlem_ac": 1}


def n(v): return "…" if v is None else f"{v:,}"
def f1(v): return "…" if v is None or v != v else f"{v:.1f}"
def f2(v): return "…" if v is None or v != v else f"{v:.2f}"
def f3(v): return "…" if v is None or v != v else f"{v:.3f}"
def pct(v, d=0): return "…" if v is None or v != v else f"{100 * v:.{d}f} %"


def counts(phantom):
    """Unscattered main-window counts (in_fov_primary) of a campaign, millions."""
    try:
        [c] = sorted(CAMPAIGNS.glob(f"full_res_{phantom}_15mCi_*"))
        meta = json.loads(str(np.load(c / "merged/projections.npz")["meta"]))
        return meta["window_counts"]["windows_main_in_fov_primary"] / 1e6
    except (ValueError, FileNotFoundError, KeyError):
        return None


def rec(phantom, run, upd, f=0):
    """The analysis record of a run at a number of updates (replicate 0), or None."""
    try:
        return MAIN[phantom]["runs"][run]["replicates"]["00"][str(upd // UPD[run])][str(f)]
    except KeyError:
        return None


def fwhm(phantom, line, upd, f=0, run="osem8_ac", which="mean"):
    """Fitted FWHM of a line ('all' range): radial / tangential (centre line: x / y) or their mean."""
    r = rec(phantom, run, upd, f)
    if r is None:
        return None
    L = r["lines"][line]["all"]
    rad, tan = (L["fwhm_y"], L["fwhm_x"]) if line == 2 else (L["fwhm_x"], L["fwhm_y"])
    return {"radial": rad, "tangential": tan, "mean": (rad + tan) / 2}[which]


def line_recovery(phantom, line, upd, run="osem8_ac"):
    r = rec(phantom, run, upd)
    return None if r is None else r["lines"][line]["all"]["recovery"]


def chang_c_at(phantom, x, y, z0=-30.0, z1=30.0):
    """Chang's c (mean transmission, resolution_chang.py): mean over the 4 voxels around (x, y), z0 ... z1."""
    path = PY / f"brain_phantom_recon/resolution_2026-10-20/chang/{phantom}_chang.npz"
    if not path.exists():
        return None
    centres = np.arange(144) * 2.0 - 143.0
    ix = np.argsort(abs(centres - x))[:2]
    iy = np.argsort(abs(centres - y))[:2]
    iz = np.flatnonzero((centres >= z0) & (centres <= z1))
    with np.load(path) as z:
        return float(z["c"].reshape(144, 144, 144)[np.ix_(ix, iy, iz)].mean())


def chang_c(phantom, line):
    """Chang's c at a line, 10 mm in from its ends."""
    try:
        h = MAIN[phantom]["cyl"][line]
    except (KeyError, IndexError):
        return None
    return chang_c_at(phantom, h["x"], h["y"], h["z0"] + 10, h["z1"] - 10)


def outside(phantom, upd, run="osem8_ac", f=0):
    r = rec(phantom, run, upd, f)
    return None if r is None else r["outside_fraction"]


def vp(phantom, key, upd, f=0, run="osem8_ac"):
    r = rec(phantom, run, upd, f)
    return None if r is None else r["sectors"][key]["vp"]


def sector(phantom, key, upd, what, f=0, run="osem8_ac"):
    r = rec(phantom, run, upd, f)
    return None if r is None else r["sectors"][key][what]


def boot(phantom, upd, f=0):
    try:
        return BOOT[phantom]["stats"][str(f)][str(upd // 8)]
    except KeyError:
        return None


def vp_pm(phantom, key, upd, f=0):
    """'V/P ± SD' from the bootstrap (replicate 0 value)."""
    b = boot(phantom, upd, f)
    if b is None:
        return f2(vp(phantom, key, upd, f))
    return f"{b[key]['vp']:.2f} ± {b[key]['vp_sd']:.3f}"


def fwhm_pm(phantom, line, upd, f=0):
    b = boot(phantom, upd, f)
    if b is None:
        return f1(fwhm(phantom, line, upd, f))
    L = b[line]
    rad, tan = (L["fwhm_y"], L["fwhm_x"]) if line == 2 else (L["fwhm_x"], L["fwhm_y"])
    sr, st = (L["fwhm_y_sd"], L["fwhm_x_sd"]) if line == 2 else (L["fwhm_x_sd"], L["fwhm_y_sd"])
    return f"{rad:.2f} / {tan:.2f}"


def equivalent_fwhm(key, v):
    """Gaussian FWHM giving V/P = v in sector key (resolution_derenzo_model), monotonic part below 0.9."""
    if v is None or not MODEL:
        return None
    w = np.array(MODEL["w_mm"])
    c = np.array(MODEL["vp"][key])
    top = int(np.argmax(c > 0.9)) if np.any(c > 0.9) else len(c)
    if v > c[top - 1] or v < c[0] or top < 2:
        return None
    return float(np.interp(v, c[:top], w[:top]))


def kernel(f):
    try:
        return CHECKS["kernel"][str(f)]["fwhm_moment"]
    except KeyError:
        return None


def nema_floor(offset):
    try:
        return CHECKS["gauss"][offset][0]["nema_x"]
    except KeyError:
        return None


def cnr(phantom, key, upd, f=0, run="osem8_ac"):
    r = rec(phantom, run, upd, f)
    return None if r is None else r["sectors"][key]["cnr_spatial"]


def core_cov(phantom, key, upd, f=0, run="osem8_ac"):
    r = rec(phantom, run, upd, f)
    return None if r is None else r["sectors"][key]["core_cov"]


def best_filter(phantom, key, upd, filters=(0, 3, 4, 5, 6, 8)):
    """The post-filter with the highest CNR of a sector at a number of updates."""
    vals = {f: cnr(phantom, key, upd, f) for f in filters}
    vals = {f: v for f, v in vals.items() if v is not None}
    return max(vals, key=vals.get) if vals else None


def updates_below(phantom, line, width, which="mean", run="osem8_ac"):
    """First saved number of updates at which a line's fitted FWHM is at or below width (mm)."""
    try:
        reps = MAIN[phantom]["runs"][run]["replicates"]["00"]
    except KeyError:
        return None
    for it in sorted(reps, key=int):
        u = int(it) * UPD[run]
        v = fwhm(phantom, line, u, run=run, which=which)
        if v is not None and v <= width:
            return u
    return None


def truth_floor(phantom, line):
    """Fitted FWHM of the true line on the 2 mm grid (mean of the two directions)."""
    try:
        t = MAIN[phantom]["truth_grid"][line]
        return (t["fwhm_x"] + t["fwhm_y"]) / 2
    except (KeyError, IndexError):
        return None


def boot_sector(phantom, key, upd, what, f=0):
    """Bootstrap statistics of a Derenzo sector: vp, vp_sd, peak, peak_sd, voxel_cov, cnr."""
    b = boot(phantom, upd, f)
    return None if b is None else b[key][what]


def best_filter_boot(phantom, key, upd, filters=(0, 3, 4, 5, 6, 8)):
    """The post-filter with the highest bootstrap CNR = (P - V) / voxel SD between the copies."""
    vals = {f: boot_sector(phantom, key, upd, "cnr", f) for f in filters}
    vals = {f: v for f, v in vals.items() if v is not None}
    return max(vals, key=vals.get) if vals else None


def max_fwhm_sd(phantoms, max_upd=4000):
    """Largest bootstrap SD of any fitted line FWHM (x or y) up to max_upd updates."""
    out = 0.0
    for p in phantoms:
        try:
            st = BOOT[p]["stats"]["0"]
        except KeyError:
            continue
        for it, lines in st.items():
            if int(it) * 8 <= max_upd:
                out = max(out, *(max(L["fwhm_x_sd"], L["fwhm_y_sd"]) for L in lines))
    return out or None


def max_vp_sd(phantom, keys=("4", "5", "6", "7", "8"), f=0):
    try:
        st = BOOT[phantom]["stats"][str(f)]
    except KeyError:
        return None
    return max(st[it][k]["vp_sd"] for it in st for k in keys)


def scene_viewer(phantom, caption, height=560):
    """An interactive <model-viewer> of the phantom in the helmet (resolution_phantom_3d.py), the .glb inlined, with a
    label (hotspot) per part and buttons that hide or show the scanner's parts (surfaces, line art and labels)."""
    import base64
    path = A / "figures" / f"scene_{phantom}.glb"
    if not path.exists():
        return f"<p>(scene {phantom} not built)</p>"
    b64 = base64.b64encode(path.read_bytes()).decode()
    lab = path.with_suffix(".labels.json")
    hotspots = "".join(
        f'<button class="hotspot {h.get("side", "right")}" slot="hotspot-{k}" data-part="{h["part"]}" data-position="{" ".join(map(str, h["position"]))}m" '
        f'data-normal="{" ".join(map(str, h["normal"]))}"><span>{h["text"]}</span></button>'
        for k, h in enumerate(json.loads(lab.read_text()) if lab.exists() else []))
    buttons = "".join(f'<button data-part="{p}" class="on">{t}</button>' for p, t in
                      (("collimators", "collimators"), ("shield", "shield"), ("fov", "FOV sphere"), ("labels", "labels")))
    return (f'<figure class="scene3d"><model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls '
            f'auto-rotate auto-rotate-delay="4000" rotation-per-second="12deg" interaction-prompt="none" '
            f'camera-orbit="35deg 72deg 100%" field-of-view="24deg" exposure="1.05" shadow-intensity="0" '
            f'environment-image="neutral" style="width:100%;height:{height}px;background:#fafafa;border-radius:8px">'
            f'{hotspots}<div class="scene-toggles">{buttons}<button data-reset="1">reset view</button></div>'
            f'</model-viewer><figcaption>{caption}</figcaption></figure>')


DA = "derenzo_brain_air"


def water_air_row(key, upd, f):
    """Table row: V/P ± SD in water, in air, the difference in units of the combined SD, and both equivalent FWHMs."""
    bw, ba = boot(DW_, upd, f), boot(DA, upd, f)
    if bw is None or ba is None:
        return f"| {key} mm | {vp_pm(DW_, key, upd, f)} | {vp_pm(DA, key, upd, f)} | … | … |"
    w, a = bw[key], ba[key]
    z = (w["vp"] - a["vp"]) / max(np.hypot(w["vp_sd"], a["vp_sd"]), 1e-9)
    ew, ea = equivalent_fwhm(key, w["vp"]), equivalent_fwhm(key, a["vp"])
    # V/P >= 0.9: the model curve is too flat to convert (model slide): the sector is simply not separated
    fw = "not separated" if ew is None and ea is None else f"{f1(ew)} / {f1(ea)} mm"
    return (f"| {key} mm | {w['vp']:.2f} ± {w['vp_sd']:.3f} | {a['vp']:.2f} ± {a['vp_sd']:.3f} | {z:+.1f} | {fw} |")


def water_air_summary(upd=3200, f=4, keys=("4", "5", "6", "7")):
    """One sentence: in which sectors water and air differ by more than 3 combined SD, and which way."""
    bw, ba = boot(DW_, upd, f), boot(DA, upd, f)
    if bw is None or ba is None:
        return "(air bootstrap not there yet)"
    better, worse, same = [], [], []
    for k in keys:
        w, a = bw[k], ba[k]
        z = (w["vp"] - a["vp"]) / max(np.hypot(w["vp_sd"], a["vp_sd"]), 1e-9)
        (worse if z > 3 else better if z < -3 else same).append(f"{k} mm")
    parts = []
    if same:
        parts.append("the same within 3 SD for " + ", ".join(same))
    if worse:
        parts.append("less separated in water than in air for " + ", ".join(worse))
    if better:
        parts.append("better separated in water than in air for " + ", ".join(better))
    return "; ".join(parts)


DW_ = "derenzo_brain_water"


def have_air():
    """True once the Derenzo in air is reconstructed and analysed (results, bootstrap and figures): until then the
    slides leave its results out instead of showing gaps."""
    return (DA in MAIN and "osem8_ac" in MAIN[DA].get("runs", {}) and DA in BOOT
            and (A / "figures" / f"derenzo_images_{DA}_osem8_ac.png").exists())


def air_slides():
    """Markdown of the three Derenzo-in-air result slides (printed by an asis cell), or nothing before the data."""
    if not have_air():
        return ""
    rows = "\n".join(water_air_row(k, 3200, 4) for k in ("4", "5", "6", "7", "8"))
    return f"""
## Derenzo in air: the images

:::: {{.columns}}
::: {{.column width="68%"}}
![](img/derenzo_images_{DA}_osem8_ac.png){{width=100% group="figs"}}
:::
::: {{.column width="32%" .side-notes}}
- The bare PMMA block in air, OSEM 8 + AC (the block still attenuates), same display as in water
- {f1(counts(DA))} M unscattered counts against {f1(counts(DW_))} M in water: no water absorbs them
- V/P, 4 mm filter, 3200 updates: 5 mm {vp_pm(DA, "5", 3200, 4)}, 6 mm {vp_pm(DA, "6", 3200, 4)} (water: {vp_pm(DW_, "5", 3200, 4)}, {vp_pm(DW_, "6", 3200, 4)})
:::
::::

## Derenzo in air: V/P against updates

![](img/derenzo_vp_{DA}_osem8_ac.png){{.r-stretch group="figs"}}

::: {{.fig-notes}}
- Same quantity and axes as for the Derenzo in water (convergence section)
:::

## Derenzo: water against air {{.smaller}}

V/P ± bootstrap SD, 4 mm filter, 3200 updates; z = (water − air) ÷ combined SD; equivalent Gaussian FWHM from V/P (model slide).

| sector | V/P, water | V/P, air | z | equivalent FWHM, water / air |
|:--|:-:|:-:|:-:|:-:|
{rows}

- **Separation, water vs air:** {water_air_summary(3200, 4)}. Both with AC in the model and unscattered data only, so what differs is the attenuation in the data (and the counts, {counts(DA) / counts(DW_):.1f}× more in air)
- Without a filter at 8000 updates: {water_air_summary(8000, 0)}
"""


def air_compare_note():
    # inline code output is not parsed as Markdown: plain text only
    return "Left, water − air (both with AC): see the water-against-air table. " if have_air() else ""


def air_conclusion():
    return f" Derenzo, water vs air (4 mm, 3200 updates): {water_air_summary(3200, 4)}" if have_air() else ""
