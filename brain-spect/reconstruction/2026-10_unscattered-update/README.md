# Unscattered-data reconstruction: update deck (2026-10-16)

Slides (`quarto/slides.qmd`, reveal.js HTML; PDF only after the content is confirmed) on the
reconstruction of the unscattered data (`in_fov_primary`) of the small-Jaszczak campaign: MLEM and
OSEM 8, with and without attenuation correction, no support threshold, no TEW. Linear axes throughout.

## Runs and analysis (dev/python)

- `brain_phantom_recon/unscattered_update_2026-10-16/run.sh`: the four reconstructions (screen,
  ~45 min on the RTX 3080 Ti).
- `unscattered_update_analysis.py`: metrics (osem_reference_analysis definitions + the wall band),
  radial / axial / sphere-line profiles to the FOV edge, slices; and the check of `osem8_ac` against
  the OSEM reference run with the support threshold (`analysis/support_check.json`).
- `unscattered_update_figures.py`: figures in `analysis/figures/`.
- `unscattered_update_line_profiles.py`: the ring-mean illustration (checked against `profiles.npz`),
  the maps of the profile lines, and line profiles along the rod rows and radially through each sphere
  (lines as `make_deck_extras.bare_lines`).
- Convergence, noise and position slides reuse the OSEM reference study
  (`dev/reports/2026-10_phantom_recon/osem_reference.md`; bootstrap error bars). Valid here because
  inside the phantom the runs with and without support agree within the bootstrap SDs (slide "Most of
  the activity ends up at the FOV edge").

## Build

`quarto/deck_data.py` reads every number from the analysis JSON files; figures are symlinked into
`quarto/img/`. From `quarto/`:

    quarto preview slides.qmd --to revealjs --port 4201 --no-browser   # live preview
    quarto render slides.qmd --to revealjs --cache-refresh             # after the analysis changes

## Findings (details on the slides)

- AC removes the broad rise towards the wall; a narrow Gibbs-like band (~16 %) remains, removed by
  an 8 mm post-filter.
- With AC, OSEM 8 = MLEM at equal updates (8× faster); without AC, OSEM is far noisier than MLEM.
- Without a support threshold most activity collects at the FOV surface; the phantom image is unchanged.
- No AC gives higher "contrast" against a background that is too bright near the wall: wrong image,
  not better resolution.
