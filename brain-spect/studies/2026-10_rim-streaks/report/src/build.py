"""Build the rim-streak study report: interactive HTML and PDF from one Markdown source.

Source of truth for the text: the Claude Doc "Rim Streaks in Brain SPECT — Study Report",
exported as Markdown to src/report.md (re-export it and rerun this script after edits).
This script adds what the doc does not hold: the figures (copied from the study outputs
into ../figures/ and placed under their sections), the metrics JSON (../data/), display
equations, and the two renderings:

Figures are embedded as re-encoded JPEGs (tools/reencode_images.py, 1800 px, q88); the
full-resolution PNGs stay in ../figures/.

    ../report.html   self-contained, interactive (sidebar contents, collapsible sections,
                     click-to-zoom figures, sortable tables); opens offline
    ../report.pdf    typeset with pandoc -> Typst

Run from anywhere (opengate env, for pandoc 3.9; typst on PATH). Figures and metrics are
re-copied from the qmirt-gate-10-sim checkout named by QMIRT_REPO (default
~/Work/RPIL/QMIRT/qmirt-gate-10-sim):
    python brain-spect/studies/2026-10_rim-streaks/report/src/build.py
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
QMIRT = Path(os.environ.get("QMIRT_REPO", "~/Work/RPIL/QMIRT/qmirt-gate-10-sim")).expanduser()
PY = QMIRT / "dev" / "python"  # figures and metrics are copied from the code repo's study outputs
FIG = OUT / "figures"
DATA = OUT / "data"
BUILD = SRC / "_build"

META = {"title": "Rim Streaks in Multi-Pinhole Brain SPECT",
        "subtitle": "Study report: truncation, angular sampling and the modelled support",
        "author": "Fang Han", "date": "2026-10-07"}

# (heading the figure goes under, source file, figure name, caption, width)
FIGURES = [
    ("## Background", "report/figs/recon_axial_z130_iterations.png", "01_observation_acr.png",
     "The observation: full ACR phantom, sphere slice, MLEM iterations 10, 50, 100 and 200 (grey 0.6–1.3). Radial streaks start at the FOV edge.", "100%"),
    ("## Background", "report/figs/coverage_z130.png", "02_sensitivity_neff.png",
     "Sensitivity and effective number of modules N_eff in one transverse slice. Sensitivity stays smooth; N_eff falls toward the rim.", "100%"),
    ("### E2:", "report/figs/e2_montage_xy.png", "03_e2_positions.png",
     "E2: cold-sphere phantom at six positions and five iterations, with the difference from P0 at iteration 100. No streaks at any position.", "70%"),
    ("### E5:", "receiver_coupling/coupling_maps.png", "04_e5_coupling_maps.png",
     "Coupling maps c = HᵀHa/s (log scale) for a source at the centre and at the rim. Cyan: coupled receiver; white: control.", "100%"),
    ("### E5:", "receiver_coupling/analysis/e5_centre.png", "05_e5_receivers.png",
     "E5, centre source: reconstructions with and without the source, their difference, and the receiver differences over iterations.", "90%"),
    ("### Ideal local impulse response", "ideal_lir/ideal_vs_mlem_lir.png", "06_ideal_vs_mlem_lir.png",
     "Ideal LIR R_α e_j for three α (columns 1–3; column 3 overlays the voxel-to-pinhole lines) against the MLEM LIR at iteration 200 (column 4).", "90%"),
    ("### E6 and E1b", "extent_series/analysis/e6_montage.png", "07_e6_growing_background.png",
     "E6: cold spheres at P2 inside a hot region growing from 32 to 105 mm; iterations 50, 100, 200. Long streaks only when the hot region fills the support.", "55%"),
    ("### E6 and E1b", "extent_series/analysis/polar_edge_e1b.png", "08_e1b_polar_edge.png",
     "E1b in polar view (distance from the object's own edge against azimuth): the cropped ACR keeps weaker streaks at its own edge.", "100%"),
    ("### E7:", "report/figs/e7_margin_zoom.png", "09_e7_margin.png",
     "E7: zoom on the cold spheres near the rim; hot region to 95 … 105 mm (empty margin 10 → 0 mm); iterations 50 and 200.", "100%"),
    ("### E7:", "extent_series/analysis/polar_edge_grow.png", "10_e7_polar_edge_uniform_balls.png",
     "Uniform balls in polar view at their own edge: an overshoot band with short texture; long stripes only when the ball reaches 105 mm.", "90%"),
    ("### E8:", "gammart_srm/support_test.png", "11_e8_support_test.png",
     "E8 runs A–E (ray-traced SRM): object to 105 mm with support 105 or 142 mm, and the full ACR. Yellow: object edge; blue: support edge.", "80%"),
    ("### E8:", "gammart_srm/support_followup.png", "12_e8_followup.png",
     "E8 runs F–M with the share of activity left beyond 105 mm (right). Run H starts the shell at ε = 0.01.", "60%"),
    ("### E9:", "acr_fit/acr_fit_slices.png", "13_e9_phantom.png",
     "The shrunk ACR phantom: sphere slice, rod slice and XZ section inside the 105 mm FOV (dashed).", "100%"),
    ("### E9:", "acr_fit/e9_polar_slides.png", "14_e9_polar_edge.png",
     "E9 in polar view at each object's own edge (sphere slice, iteration 200): weaker streaks remain for the shrunk ACR with every support and on both SRMs.", "85%"),
    ("### E9:", "acr_fit/e9_slides_differences.png", "15_e9_start_image.png",
     "E9, ray-traced SRM, support to 142 mm: each run minus the contour-support run (rod slice, iterations 20 and 100).", "90%"),
    ("### E9b:", "acr_fit/e9b_polar_spheres.png", "16_e9b_inserts.png",
     "E9b: polar view of the sphere-slice edge as the inserts are added. The rods, 30–60 mm below this slice, add strong stripes.", "90%"),
    ("### E9c:", "acr_fit/e9c_sphere_only.png", "17_e9c_spheres_only.png",
     "E9c: shrunk ACR with the cold spheres only, Gate SRM (top two rows) and ray-traced SRM; transverse and coronal views; iterations 50, 100, 200.", "90%"),
    ("### Linearised MLEM response", "report/figs/lir_pinhole_lines.png", "18_lir_pinhole_lines.png",
     "MLEM LIR at r = 0, 30 and 80 mm; bottom row overlays the lines from the voxel to each pinhole.", "90%"),
]
EMBED_FIGURE = ("extent_series/analysis/edge_overshoot.png", "19_edge_overshoot.png",
                "Edge overshoot of the uniform balls (Gate SRM): radial profile at the 95 mm edge over iterations, overshoot against iteration for each edge position, and profiles at iteration 200.")
DATA_FILES = ["acr_fit/e9_gammart.json", "acr_fit/e9_gate.json", "acr_fit/e9b_edge_energy.json",
              "acr_fit/e9c_sphere_only.json", "extent_series/analysis/edge_overshoot.json",
              "gammart_srm/support_followup.json", "gammart_srm/support_test.json"]


def copy_assets():
    FIG.mkdir(exist_ok=True)
    DATA.mkdir(exist_ok=True)
    for _, src, name, _, _ in FIGURES:
        shutil.copy2(PY / src, FIG / name)
    shutil.copy2(PY / EMBED_FIGURE[0], FIG / EMBED_FIGURE[1])
    for d in DATA_FILES:
        shutil.copy2(PY / d, DATA / Path(d).name)


def figure_md(name, caption, width, prefix):
    # embedded copies are re-encoded JPEGs (see main); figures/ keeps the full-resolution PNGs
    return f"![{caption}]({prefix}/{Path(name).with_suffix('.jpg').name}){{width={width}}}\n"


def prepare(md: str, prefix: str) -> str:
    lines = md.splitlines()
    # title and byline go to the metadata
    lines = [l for i, l in enumerate(lines) if not (i < 4 and (l.startswith("# ") or l.startswith("Oct ")))]
    md = "\n".join(lines)
    # display equations: ```latex blocks -> $$ … $$
    md = re.sub(r"```latex\n(.*?)\n```", lambda m: "$$\n" + m.group(1).strip() + "\n$$", md, flags=re.S)
    # cases: pandoc drops the gap after "&" in Typst; add one (harmless in HTML)
    md = re.sub(r"\\begin\{cases\}.*?\\end\{cases\}", lambda m: m.group(0).replace("& ", "& \\quad "), md, flags=re.S)
    # tables left-aligned
    md = re.sub(r"^(\|(?: --- \|)+)$", lambda m: m.group(0).replace(" --- ", " :--- "), md, flags=re.M)
    # the doc's live chart -> the matplotlib figure of the same data
    md = re.sub(r"^&#91;embedded content:.*$", figure_md(EMBED_FIGURE[1], EMBED_FIGURE[2], "100%", prefix),
                md, flags=re.M)
    # figures at the end of their section (before the next heading of the same or higher level)
    out = md.splitlines()
    for heading, _, name, caption, width in FIGURES:
        start = next(i for i, l in enumerate(out) if l.startswith(heading))
        level = len(heading.split(" ")[0])
        end = next((i for i in range(start + 1, len(out))
                    if out[i].startswith("#") and len(out[i].split(" ")[0]) <= max(level, 3)), len(out))
        out[end:end] = ["", figure_md(name, caption, width, prefix)]
    return "\n".join(out) + "\n"


def pandoc(args):
    subprocess.run(["pandoc", *args], check=True)


def main():
    copy_assets()
    BUILD.mkdir(exist_ok=True)
    # re-encode the figures for embedding (shared tool at the top of the notes repo)
    repo = Path(subprocess.run(["git", "-C", str(SRC), "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True, check=True).stdout.strip())
    sys.path.insert(0, str(repo / "tools"))
    from reencode_images import reencode_tree
    n, before, after = reencode_tree(FIG, BUILD / "web")
    print(f"embedding {n} re-encoded figures: {before / 1e6:.1f} MB -> {after / 1e6:.1f} MB")
    md = (SRC / "report.md").read_text()
    meta = BUILD / "meta.json"
    meta.write_text(json.dumps(META))

    # HTML: self-contained, MathML (renders offline), interactive layer from app.js
    (BUILD / "report_html.md").write_text(prepare(md, "web"))
    (BUILD / "after.html").write_text("<script>\n" + (SRC / "app.js").read_text() + "\n</script>\n")
    pandoc([str(BUILD / "report_html.md"), "-t", "html5", "-s", "--shift-heading-level-by=-1", "--toc", "--toc-depth=3", "--section-divs", "--mathml", "--embed-resources",
            "--metadata-file", str(meta), "--css", str(SRC / "style.css"),
            "--include-after-body", str(BUILD / "after.html"),
            "--resource-path", str(BUILD), "-o", str(OUT / "report.html")])

    # PDF: pandoc -> Typst -> PDF
    (BUILD / "report_pdf.md").write_text(prepare(md, "web"))
    typ = BUILD / "report.typ"
    pdf_meta = BUILD / "meta_pdf.json"
    pdf_meta.write_text(json.dumps({"margin": {"x": "2cm", "y": "2.2cm"}}))
    pandoc([str(BUILD / "report_pdf.md"), "-t", "typst", "-s", "--shift-heading-level-by=-1",
            "--include-in-header", str(SRC / "pdf_header.typ"), "--toc", "--toc-depth=2",
            "--metadata-file", str(meta), "--metadata-file", str(pdf_meta), "-V", "papersize=us-letter", "-V", "fontsize=10pt", "-V", "section-numbering=1.1", "-o", str(typ)])
    # pandoc's TeX -> Typst math glues a one-letter exponent to the next name ("^mP"); split it
    text = typ.read_text().replace(")^mP F", ")^m P F")
    # a table cell starting with "+ " or "- " would become a Typst list item; escape it
    text = re.sub(r"\[([+-]) ", r"[\\\1 ", text)
    typ.write_text(text)
    subprocess.run(["typst", "compile", "--root", str(OUT), str(typ), str(OUT / "report.pdf")], check=True)
    print("wrote", OUT / "report.html", "and", OUT / "report.pdf")


if __name__ == "__main__":
    main()
