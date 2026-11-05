# Resolution phantoms: reconstruction slide deck (2026-10-20)

Slide deck (`quarto/slides.qmd`, reveal.js HTML) on the six resolution phantoms simulated on OSPool
(`submit_htcondor/brain_phantom_production_status.md`, "Resolution phantoms"): triple line 75 mm
(NEMA layout) and 50 mm (InSPira HD style), hot-rod Derenzo 3–8 mm, each in water and in air.
Same reconstruction as `../2026-10_unscattered_update`: unscattered main-window data
(`in_fov_primary`), 2 mm Gate SRM, no support threshold, no TEW; OSEM 8, with and without
attenuation correction (gammart factors per phantom).

## Runs and analysis (dev/python)

- `brain_phantom_recon/resolution_2026-10-20/attenuation.sh`: gammart attenuation factors (2 mm).
- `resolution_recon_runs.py` (SRM loaded once, AC by a copy of the values per phantom). Convergence
  test first: OSEM 8 + AC, replicate 0, 28 saved iterations to 1000 (8000 updates); then
  `brain_phantom_recon/resolution_2026-10-20/run.sh`: OSEM 8 without AC, bootstrap copies (Derenzo 20 to 8000 updates, lines 10 to 4000).
- `resolution_analysis.py`: line FWHM (2D voxel-averaged Gaussian fit and NEMA interpolation) per
  10 mm slab and over the line; Derenzo peak P, valley V, V/P, recoveries, row profiles; FOV-edge share.
- `resolution_method_checks.py`: FWHM methods on known lines; the post-filter's real width on the grid.
- `resolution_derenzo_model.py`: V/P of the true Derenzo blurred by a Gaussian (V/P → equivalent FWHM).
- `resolution_chang.py`: Chang's first-order correction of the no-AC images (module-sensitivity-weighted mean
  transmission from the same gammart factors) -> run `osem8_chang` (reference for AC in the model).
- `resolution_bootstrap.py`: bootstrap SDs, voxel noise in the channel cores, CNR (filter choice).
- `resolution_figures.py`: figures in `brain_phantom_recon/resolution_2026-10-20/analysis/figures/`.

## Build

`quarto/slides_data.py` reads every number from the analysis JSON files; figures are symlinked into
`quarto/img/`. From `quarto/`:

    quarto render slides.qmd --to revealjs

Layout: a plot narrower than 2.2:1 sits in a 68 % column with its notes beside it (`.side-notes`); a wider one
fills the slide (`.r-stretch`) with notes below (`.fig-notes`). Figures are rendered at 150 dpi for zooming.
`lightbox-slides.html` turns every plot into one gallery (GLightbox, loaded by the `lightbox:` option): click or
press `z` to open, click to zoom, arrows page through all plots, closing returns the slides to the last one's slide.
Slides 5–10, one per phantom: an interactive 3D scene and exact sections (`dev/python/resolution_phantom_2d.py`,
SVG: axial / coronal / sagittal through the centre, analytic phantom sections, mesh-cut hardware, same ±215 mm
scale on every panel). The interactive 3D scenes of the phantoms in the helmet (`dev/python/resolution_phantom_3d.py` -> .glb, shown
with `<model-viewer>` from `model-viewer.html`, inlined at render); buttons toggle collimators, shield and FOV sphere.

## Running on ERIS (gpu-l40s)

The bootstrap copies were reconstructed on ERIS (user's request, 2026-10-20) with
`dev/python/resolution_recon_eris.py` (needs only `compact_gpu_mlem.py`) and
`submit_slurm/run_resolution_eris.sh` (ROOT $ERIS_SCRATCH/resolution; SRM, support and container of the
error budget). Staging: the measured vectors (`<phantom>_in_fov_primary.npy`, from `measured_sets`) and the
gammart factors (`<phantom>_factors_2mm.npy`) in `ROOT/data`; copy with scp (no rsync on ERIS; quote remote
globs). Check job: ERIS = workstation within 2e-6 of the peak value. Outputs copied back to
`brain_phantom_recon/resolution_2026-10-20/<phantom>/osem8_ac/`; then `resolution_bootstrap.py`.

## Status (2026-10-20)

- Done: all six phantoms, OSEM 8 with and without AC, Chang's correction, bootstrap. `derenzo_brain_air` was
  reconstructed on ERIS (job 6002976, 2026-10-21) and added by `finish_derenzo_air.sh`.
- MLEM was stopped at the user's request (only `triple_line_75_water/mlem_ac` exists; not in the slides).
