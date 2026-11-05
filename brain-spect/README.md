# Brain SPECT

Stationary multi-pinhole brain SPECT: 73 pinhole modules in 7 rings, 45,625 detector
bins, Gate 10 Monte Carlo system matrices (SRMs) produced on SDSC Expanse.

| Folder | What | Date |
| --- | --- | --- |
| [`studies/2026-10_rim-streaks/`](studies/2026-10_rim-streaks/) | Rim streaks in MLEM: truncation vs sampling vs support; edge overshoot. Report (HTML + PDF), lab notes, earlier write-ups | 2026-10 |
| [`srm-production/2026-10_288mm-production-study/`](srm-production/2026-10_288mm-production-study/) | How to produce the SRM for a 288 mm FOV: statistics, cost, CSG shield | 2026-10-05 |
| [`geometry/2026-10_shield-csg-study/`](geometry/2026-10_shield-csg-study/) | Lead shield as analytic CSG solids vs the STL mesh (sharp and rounded edges) | 2026-10 |
| [`geometry/fov-analysis/`](geometry/fov-analysis/) | Which modules see which part of the FOV; coverage maps for the 288 mm decision | 2026-10 |
| [`reconstruction/srm-recon-report/`](reconstruction/srm-recon-report/) | Cardiac and brain SRMs and phantom reconstructions (per-module sensitivity, NEMA triple line, ACR) | 2026-09-25 |
| [`srm-production/2026-09-15_campaign-progress-report/`](srm-production/2026-09-15_campaign-progress-report/) | Expanse allocation progress report (2026-08-14 to 2026-09-15) | 2026-09-15 |
| [`geometry/`](geometry/) | Geometry design diagram (Quarto), point cloud, geometry notebooks. STL meshes: qmirt-gate-10-sim `persistent_data/brain_spect/stl/`; the notebooks regenerate the interactive geometry views | — |
| [`simulation/`](simulation/) | Early simulation checks: per-crystal and per-pixel maps, SDSC Expanse test reconstructions | — |

Code: qmirt-gate-10-sim. Code-facing notes stay there (`dev/python/brain_shield_csg.md`,
`dev/python/srm_plotting_and_analytic_geometry.md`).
