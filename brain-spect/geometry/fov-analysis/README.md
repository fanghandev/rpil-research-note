# Brain SPECT FOV analysis

Which modules see which part of the field of view: coverage slices and the radial profile
of module overlap, with `brain_fov_summary.json`. The interactive 3D overlap check is not
kept; regenerate it with `python dev/python/plot_brain_spect_fov_3d.py [--fov-size-mm 288]`
in qmirt-gate-10-sim. Used
by the 288 mm production study. Scripts in qmirt-gate-10-sim (`brain_spect_max_fov.py`,
`plot_brain_spect_max_fov.py`, `plot_brain_spect_fov_3d.py`); the `.npz` maps stay there.
