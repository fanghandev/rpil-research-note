"""Numbers and tables for error_budget.qmd, read from the error budget analysis
(dev/python/error_budget_analysis.py -> brain_phantom_recon/error_budget_2026-10-16/analysis/metrics.json),
so re-running the analysis and re-rendering updates the deck."""

import getpass
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AN = (HERE / "../../../python/brain_phantom_recon/error_budget_2026-10-16/analysis").resolve()
M = json.loads((AN / "metrics.json").read_text())
S, ENS, A, CHI = M["single"], M["ensemble"], M["A"], M["chi2"]
UMAX_MLEM = M["updates"]["B_mlem"][-1]

RODS = ["rods_4.8mm", "rods_6.4mm", "rods_7.9mm", "rods_9.5mm", "rods_11.1mm", "rods_12.7mm"]
SPHERES = ["sphere_6.4mm", "sphere_9.5mm", "sphere_12.7mm", "sphere_15.9mm", "sphere_19.1mm", "sphere_25.4mm"]


def name(key):
    return ("rods " if key.startswith("rods") else "sphere ") + key.split("_")[1].replace("mm", " mm")


def f2(x):
    return f"{x:.2f}"


def f3(x):
    return f"{x:.3f}"


def pct(x, d=1):
    return f"{100 * x:.{d}f} %"


def s(step, key, u=8000, f=8):
    """Value of a metric: single runs, D = mean over the 20 draws, B_mlem = its last iteration."""
    if step == "D":
        return ENS["D"][str(u)][str(f)]["mean_of"][key]
    if step == "B_mlem":
        u = UMAX_MLEM
    return S[step][str(u)][str(f)][key]


def sd(step, key, u=8000, f=8):
    return ENS["D" if step == "D" else "E_boot"][str(u)][str(f)]["sd_of"][key]


def a(key, f=0, kind="pv"):
    return A[kind][str(f)][key]


def ens(step, key, u=8000, f=8):
    return ENS[step][str(u)][str(f)][key]


def ladder_table(u=8000, f=8):
    """Contrast at every step and the change each step adds."""
    filt = f > 0
    head = ["insert", "truth (PV)"] + ([f"+ {f} mm filter"] if filt else []) + \
        ["B", "C", "C′", "D̄ ± SD", "E ± SD"]
    rows = []
    for k in RODS + SPHERES:
        r = [name(k), f2(a(k))] + ([f2(a(k, f))] if filt else []) + \
            [f2(s("B", k, u, f)), f2(s("C", k, u, f)), f2(s("Cp", k, u, f)),
             f"{f2(s('D', k, u, f))} ± {f2(sd('D', k, u, f))}", f"{f2(s('E', k, u, f))} ± {f2(sd('E', k, u, f))}"]
        rows.append(r)
    return md(head, rows)


def budget_table(u=8000, f=8):
    """Change of contrast per factor (later step − earlier step)."""
    filt = f > 0
    head = ["insert", "2 mm grid (PV)"] + (["filter"] if filt else []) + \
        ["system + algorithm", "discretisation", "noise bias", "mismatch", "noise SD"]
    rows = []
    for k in RODS + SPHERES:
        t = a(k, f) if filt else a(k)
        r = [name(k), f"{a(k) - 1:+.2f}"] + ([f"{a(k, f) - a(k):+.2f}"] if filt else []) + \
            [f"{s('B', k, u, f) - t:+.2f}", f"{s('C', k, u, f) - s('B', k, u, f):+.2f}",
             f"{s('D', k, u, f) - s('C', k, u, f):+.2f}", f"{s('E', k, u, f) - s('D', k, u, f):+.2f}",
             f"{sd('D', k, u, f):.2f}"]
        rows.append(r)
    return md(head, rows)


def nrmse_table():
    head = ["setting", "truth nearest", "B", f"B∞ (MLEM {UMAX_MLEM:,})", "C", "C′", "D̄", "D bias", "D noise", "E"]
    rows = []
    for u, f in [(400, 0), (1600, 0), (8000, 0), (400, 8), (8000, 8)]:
        nk, bk = ("nrmse_phantom", "bias_phantom") if f == 0 else ("nrmse_f_phantom", "bias_f_phantom")
        rows.append([f"{u} upd., {'no filter' if f == 0 else f'{f} mm'}", f3(a(nk, f, "nearest")),
                     f3(s("B", nk, u, f)), f3(S["B_mlem"][str(UMAX_MLEM)][str(f)][nk]), f3(s("C", nk, u, f)),
                     f3(s("Cp", nk, u, f)), f3(s("D", nk, u, f)), f3(ens("D", bk, u, f)),
                     f3(ens("D", "sd_phantom", u, f)), f3(s("E", nk, u, f))])
    return md(head, rows)


def noise_table():
    head = ["setting", "ensemble CoV, D (20 draws)", "bootstrap CoV, E (20 copies)", "E / D",
            "inserts with SD ratio within ±20 %"]
    rows = []
    keys = RODS + SPHERES
    for u, f in [(400, 0), (1600, 0), (8000, 0), (400, 8), (1600, 8), (8000, 8)]:
        d, e = ens("D", "ensemble_cov", u, f), ENS["E_boot"][str(u)][str(f)]["ensemble_cov"]
        r = np.array([sd("E", k, u, f) / sd("D", k, u, f) for k in keys])
        rows.append([f"{u} upd., {'no filter' if f == 0 else f'{f} mm'}", f3(d), f3(e), f2(e / d),
                     f"{int((abs(r - 1) <= 0.2).sum())} / {len(keys)}"])
    return md(head, rows)


def md(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def mlem(key, u, f=0):
    return S["B_mlem"][str(u)][str(f)][key]


def best_updates(step, key="nrmse_phantom", f=0):
    us = M["updates"][step]
    v = [ENS["D"][str(u)][str(f)]["mean_of"][key] if step == "D" else S[step][str(u)][str(f)][key] for u in us]
    i = int(np.argmin(v))
    return us[i], v[i]


CHI2 = CHI["chi2_per_pixel_all"]
CHI2_MOD = np.array(CHI["chi2_per_module"])
RATIO_MOD = np.array(CHI["count_ratio_per_module"]) - 1
LEVELS = M["levels"]


def z_mismatch(key, u, f):
    """(E − D̄) in units of the combined SD of one E and one D reconstruction."""
    return (s("E", key, u, f) - s("D", key, u, f)) / np.hypot(sd("E", key, u, f), sd("D", key, u, f))


PROVENANCE = Path(f"/data/{getpass.getuser()}/opengate_sim/data/brain_spect/brain_288mm_csg_102t_20261005T211647Z_05/geometry_provenance.json")
RING = np.array(json.loads(PROVENANCE.read_text())["analytic_geometry"]["modules"]["ring_index"])
RING_RATIO = {int(r): float(RATIO_MOD[RING == r].mean()) for r in np.unique(RING)}


def chi2_plotly():
    """Interactive version of img/error_budget/chi2_modules.png: χ² per pixel and module total vs the model,
    per module, with alternating ring bands and the ring means; hover shows module, ring and values."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    blue, ink, muted, grid = "#2a78d6", "#0b0b0b", "#52514e", "#e4e3df"
    m = np.arange(1, RING.size + 1)
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08,
                        subplot_titles=("χ² per pixel: Gate data vs C's expected counts",
                                        "Module total: Gate / expected − 1"))
    panels = [(np.round(CHI2_MOD, 3), 1.0, "χ² %{y:.3f}"), (np.round(100 * RATIO_MOD, 2), 0.0, "Gate / expected − 1: %{y:.2f} %")]
    for col, (y, ref, fmt) in enumerate(panels, start=1):
        for r in np.unique(RING):  # alternating ring bands
            sel = m[RING == r]
            if r % 2 == 0:
                fig.add_vrect(x0=sel[0] - 0.5, x1=sel[-1] + 0.5, fillcolor=grid, opacity=0.45, line_width=0,
                              layer="below", row=1, col=col)
        fig.add_trace(go.Bar(x=m, y=y, marker_color=blue, marker_line_width=0, name="module",
                             customdata=RING, showlegend=False,
                             hovertemplate=f"module %{{x}} · ring %{{customdata}}<br>{fmt}<extra></extra>"),
                      row=1, col=col)
        for r in np.unique(RING):  # ring mean as a step
            sel = RING == r
            mean = round(float(y[sel].mean()), 3)
            fig.add_trace(go.Scatter(x=[m[sel][0] - 0.5, m[sel][-1] + 0.5], y=[mean, mean], mode="lines",
                                     line=dict(color=ink, width=2.5), showlegend=bool(col == 1 and r == 0),
                                     name="ring mean", legendgroup="ring",
                                     hovertemplate=f"ring {r} mean ({int(sel.sum())} modules)<br>{fmt}<extra></extra>"),
                          row=1, col=col)
        fig.add_hline(y=ref, line=dict(color=muted, width=1.5, dash="dash"), row=1, col=col)
        fig.update_xaxes(title_text="module (grey bands: even rings 0, 2, 4, 6)", range=[0.3, m[-1] + 0.7],
                         row=1, col=col)
    fig.update_yaxes(title_text="χ² per pixel (expected > 10)", rangemode="tozero", row=1, col=1)
    fig.update_yaxes(title_text="Gate / expected − 1 (%)", ticksuffix=" %", row=1, col=2)
    fig.update_xaxes(showgrid=False, linecolor=muted, tickcolor=muted, ticks="outside")
    fig.update_yaxes(gridcolor=grid, zeroline=False, linecolor=muted)
    fig.update_layout(height=430, margin=dict(l=70, r=20, t=50, b=60), plot_bgcolor="white", paper_bgcolor="white",
                      font=dict(size=16, color=ink), bargap=0.15, hoverlabel=dict(font_size=16),
                      legend=dict(orientation="h", x=1, xanchor="right", y=1.16))
    for ann, ax in zip(fig.layout.annotations, ("xaxis", "xaxis2")):  # titles left-aligned over each panel
        ann.update(x=fig.layout[ax].domain[0], xanchor="left", font_size=18)
    return fig


def chi2_html():
    """chi2_plotly() as a raw-HTML fence for an `output: asis` cell. plotly.js is inlined and Plotly's MathJax
    hook is left out: the hook that Quarto's default Plotly output adds stops the deck's MathJax from rendering
    the formulas. The fence keeps pandoc from reading the HTML as Markdown (blank lines inside the inlined
    script would end the HTML block and push the plot out of its slide)."""
    html = chi2_plotly().to_html(full_html=False, include_plotlyjs=True, include_mathjax=False,
                                 config={"displayModeBar": False, "responsive": True})
    return "\n```{=html}\n" + html + "\n```\n"
