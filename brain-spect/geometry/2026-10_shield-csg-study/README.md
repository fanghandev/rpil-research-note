# 2026-10 · Brain shield: CSG solids vs STL mesh

Comparison of the lead shield modelled as analytic Geant4 (CSG) solids against the STL
mesh, in two versions: `sharp-edges/` and `rounded-edges/`. Each holds per-aperture
comparisons (`aperture_*.png`, `apertures.pdf`), whole-shield sections and thickness maps,
and `summary.json`.

The interactive 3D views (`whole_3d.html`, `regions_3d.html`, 18–28 MB each) are not kept;
regenerate them in qmirt-gate-10-sim with
`python dev/python/plot_brain_shield_csg_vs_stl.py` (sharp edges) and `… --rounded`.

Method, benchmark and conclusions: qmirt-gate-10-sim `dev/python/brain_shield_csg.md`
(kept there because it documents the code). Scripts: `brain_shield_csg.py`,
`plot_brain_shield_csg_vs_stl.py`, `benchmark_brain_shield_models.py`. The `.npz` caches
stay in qmirt.
