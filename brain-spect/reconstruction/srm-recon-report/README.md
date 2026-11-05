# 2026-09-25 · Cardiac and brain SPECT: SRMs and phantom reconstructions

Per-module brain SRM sensitivity maps (73 modules), NEMA triple-line and ACR (Jaszczak)
reconstructions for the brain system, and an ACR reconstruction for the cardiac system.

| Item | What |
| --- | --- |
| `srm_recon_report.pdf` | The report, built by `./build.sh` with re-encoded figures (15 MB) |
| `srm_recon_report.typ` | Typst source; `typst compile srm_recon_report.typ` alone embeds the full-resolution figures (57 MB) |
| `figs/`, `figs/modules/` | Full-resolution originals (5341 px PNGs); per-module maps `SRM_Head_01–73.png` |
| `build.sh` | Re-encodes `figs/` with `tools/reencode_images.py` (1800 px JPEG, q88) into `_build/` and compiles the PDF |
| `brain_srm_stats.json` | SRM statistics read by the source |

**Code.** qmirt-gate-10-sim `dev/python/` (`plot_expanse_brain_srm_202609.py`,
`fp_jaszczak_and_recon.py`, `plot_reconstructed_npz.py`).
