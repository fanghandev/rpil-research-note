# RPIL research notes

Reports, study write-ups, figures, slides and references for Fang Han's SPECT work at
RPIL. Code lives elsewhere (see [Where the code is](#where-the-code-is)); this repository
holds what the code produced and what was concluded from it.

## Layout

| Folder | What is in it |
| --- | --- |
| [`brain-spect/`](brain-spect/) | Stationary 73-module multi-pinhole brain SPECT: geometry, simulation, SRM production, reconstruction, studies |
| [`dc-spect/`](dc-spect/) | Dynamic cardiac SPECT (DC-SPECT): geometry, Gate 10 simulation, SRM analysis, ACR phantom work |
| [`ray-tracing/`](ray-tracing/) | GPU ray tracing for SPECT system modelling (NVIDIA Warp, differentiable calibration) |
| [`meetings/`](meetings/) | Meeting notes and slides, by date |
| [`references/`](references/) | Shared library of papers and phantom data sheets, with an index |
| [`archive/`](archive/) | Older or unrelated work kept for the record |
| [`tools/`](tools/) | Small helpers for reports (e.g. `reencode_images.py`: size-reduced figure copies for PDFs and HTML) |

## Recent studies

| Date | Study | Where |
| --- | --- | --- |
| 2026-10 | Rim streaks in brain SPECT MLEM (truncation, sampling, support, edge overshoot) | [`brain-spect/studies/2026-10_rim-streaks/`](brain-spect/studies/2026-10_rim-streaks/) |
| 2026-10 | SRM production for a 288 mm brain FOV | [`brain-spect/srm-production/2026-10_288mm-production-study/`](brain-spect/srm-production/2026-10_288mm-production-study/) |
| 2026-10 | Brain shield as CSG solids vs STL | [`brain-spect/geometry/2026-10_shield-csg-study/`](brain-spect/geometry/2026-10_shield-csg-study/) |
| 2026-09 | Cardiac and brain SRMs and phantom reconstructions | [`brain-spect/reconstruction/srm-recon-report/`](brain-spect/reconstruction/srm-recon-report/) |
| 2026-09-15 | Expanse campaign progress report | [`brain-spect/srm-production/2026-09-15_campaign-progress-report/`](brain-spect/srm-production/2026-09-15_campaign-progress-report/) |

## Conventions

- **Topic first.** New work goes under its topic folder. A study with a start and an end
  gets a dated folder, `YYYY-MM_short-name` (or `YYYY-MM-DD_…`); a living area gets a
  plain name. A new top-level folder only for work outside the existing topics.
- **Names** are lower-case and hyphenated; dates go first so folders sort in time order.
- **Each study folder has a README:** the question, the answer, the date, where the code
  is (repository and commit) and where the data is.
- **Rendered outputs:** keep the final PDF/HTML next to its source; no Quarto `_output/`
  copies.
- **Bulk plot sets** (hundreds of per-pixel images) go into zip archives under an
  `archives/` folder with a `MANIFEST.md`, split into parts of roughly 25 MB.
- **Figures in PDFs and HTML** are embedded as re-encoded copies
  (`tools/reencode_images.py`); the full-resolution originals sit next to the source.
- **Interactive plots** (plotly, k3d HTML exports) are not kept when the code that makes
  them is in a repository; the README says which script regenerates them.
- **Simulation inputs** (STL meshes, materials) live in the code repository, not here.

## Large files: Git LFS

Images, PDFs, HTML exports, archives, STL/WRL meshes, Keynote and spreadsheet files are
stored with [Git LFS](https://git-lfs.com) (rules in [`.gitattributes`](.gitattributes)).
The git history holds small pointers; the files themselves download on checkout.

```sh
git lfs install                                    # once per machine
git clone git@github.com:<github-user>/rpil-research-note.git
GIT_LFS_SKIP_SMUDGE=1 git clone …                  # text only; then `git lfs pull -I "<path>"`
```

Zip archives under any `archives/` folder (bulk plot sets, ~200 MB) are **not** downloaded
on clone or pull ([`.lfsconfig`](.lfsconfig)); the files appear as small pointer files.
Fetch one set when you need it:

```sh
git lfs pull --include="dc-spect/srm/2026-08_ospool-srm-three-views/archives/*" --exclude=""
```

GitHub Free includes 10 GiB of LFS storage and 10 GiB of download bandwidth a month.
Adding a file of a tracked type needs nothing special: `git add` stores it in LFS.

## Where the code is

| Repository | What |
| --- | --- |
| `qmirt-gate-10-sim` (GitHub `<github-user>`) | Gate 10 SRM production, reconstruction, analysis scripts for brain and cardiac SPECT |
| `pytorch-optix` (`gammart`) | OptiX ray tracer used for the ray-traced brain SRM |

Each study README names the scripts and the commit it used.
