# 2026-10 · Rim streaks in brain SPECT MLEM

**Question.** Why do MLEM reconstructions of the ACR phantom show radial streaks at the rim
of the 210 mm FOV: truncation, angular sampling, or the edge of the modelled support?

**Answer.** The streak geometry is a property of the system matrix (lines from each voxel
through the pinholes, strongest where few modules see a voxel). Streaks appear when
something in the poorly sampled rim zone excites them: activity at the support edge, a
modelled region that starts full (fixed by starting it near zero), or cold inserts the
system cannot resolve. They are not truncation; all data were consistent. The bright ring
inside hot edges is the maximum-likelihood edge overshoot (Snyder et al. 1987).

| Item | What |
| --- | --- |
| [`report/`](report/) | The study report: `report.pdf`, interactive `report.html`, figures, metrics, build |
| [`lab-notes.md`](lab-notes.md) | Running lab notes: every experiment E1–E9c, predictions, results, corrections |
| [`earlier-writeups/`](earlier-writeups/) | `streak_artifacts_report` (2026-10-01, the problem), `streak_study_report` (2026-10-05; its E1b claim is outdated), `fisher_svd_gram` (theory) — Typst sources, PDFs, figures |

Live versions: report doc https://claude.ai/code/artifact/24ee84fb-af77-46a3-96af-0c23d3f080bc,
slides https://claude.ai/artifact/E9K4grwoWM9xpZctT2eMkP (private until shared).

**Code.** qmirt-gate-10-sim `dev/python/` (scripts listed in the report's Reproducibility
section; branch `brain-288mm-csg-production`). Several study scripts were still
uncommitted there on 2026-10-08. **Data.** Reconstructions and SRMs stay on the
workstation under qmirt-gate-10-sim `dev/python/` and `results/`.
