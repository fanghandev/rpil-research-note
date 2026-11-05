# 2026-10-05 · SRM production for a 288 mm brain FOV

Planning study for producing the brain SPECT system matrix over a 288 mm field of view:
counts and statistics needed, cost, FOV coverage by module, and the CSG shield model.

| Item | What |
| --- | --- |
| `brain_288mm_srm_production_study.pdf` | The study (Typst source alongside; compiles here with `typst compile brain_288mm_srm_production_study.typ`) |
| `figs/` | Figures it uses (pixel-count maps, FOV coverage, shield comparison) |
| `brain_288mm_srm_stats.json`, `brain_288mm_refs.yml` | Numbers and bibliography read by the source |

**Code.** qmirt-gate-10-sim, commit `773b819` (branch `brain-288mm-csg-production`);
the stats come from `dev/python/report/brain_288mm_srm_stats.py` there.
