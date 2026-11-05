# Rim streaks in multi-pinhole brain SPECT — study report (October 2026)

Why the brain SPECT MLEM reconstructions show radial streaks at the FOV rim, what sets
them off, the edge-overshoot ring, and what this means for the 288 mm SRM.

## Open these

| File | What it is |
| --- | --- |
| `report.html` | Interactive report: contents sidebar, fold/unfold sections, click a figure to zoom, click a table header to sort. Self-contained (figures embedded); opens offline in any browser. |
| `report.pdf` | The same report typeset for print and review (US letter, 24 pages). |
| `figures/` | The 19 figures in the report at full resolution, numbered in reading order. The HTML and PDF embed re-encoded copies (1800 px JPEG) made by `tools/reencode_images.py` at build time. |
| `data/` | Metrics behind the numbers in the report (JSON from the analysis scripts). |

Live versions (Claude artifacts, private until shared from their Share menu):

- Report (editable, commentable): https://claude.ai/code/artifact/24ee84fb-af77-46a3-96af-0c23d3f080bc
- Slide deck for the group meeting: https://claude.ai/artifact/E9K4grwoWM9xpZctT2eMkP

## Where things come from

- **Text:** the Claude Doc above, exported to `src/report.md` on 2026-10-08 (doc revision 19).
  The doc is the source of truth; this folder is a snapshot of it.
- **Figures and metrics:** copied from the study outputs in qmirt-gate-10-sim `dev/python/`
  (see `src/build.py`, lists `FIGURES` and `DATA_FILES`). The analysis scripts live there too.
- **Running lab notes:** `../lab-notes.md` (every experiment, the predictions written
  before running, and the corrections).
- **Papers read in full:** `references/` at the top of this repo (Barrett et al. 1994;
  Snyder et al. 1987).
- **Earlier write-ups:** `../earlier-writeups/` (`streak_study_report.pdf` predates the E9
  correction; `fisher_svd_gram.pdf` has the theory, with the Barrett derivation).

## Rebuild after editing the doc

1. Export the doc as Markdown into `src/report.md` (Claude Docs export, or ask a Claude
   agent with the Docs connector to do it).
2. Run, in the `opengate` environment (pandoc 3.9; typst on PATH), with a checkout of
   qmirt-gate-10-sim at `$QMIRT_REPO` (default `~/Work/RPIL/QMIRT/qmirt-gate-10-sim`):

   ```sh
   ma opengate && python brain-spect/studies/2026-10_rim-streaks/report/src/build.py
   ```

`src/` holds the build: `build.py` (figure placement, equation fixes, both renderings),
`style.css` and `app.js` (the HTML's look and interactivity), `pdf_header.typ` (PDF layout
rules). `src/_build/` is scratch and ignored.

## For agents picking this up

- Start with the report's last section, **Handoff for research planning**: claim registry
  (C1–C11, with status and evidence), candidate experiments (X1–X10), literature queries
  and working rules.
- Claims are cited by ID; update their status in the doc rather than here.
- Rules that came out of this study: write predictions before running a test; judge
  streaks at the object's own edge (polar view), not at a fixed radius; trust images over
  scalar metrics until a metric is validated; read a paper before citing it.
