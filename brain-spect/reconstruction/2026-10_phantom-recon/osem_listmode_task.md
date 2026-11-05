# Task: OSEM, list-mode MLEM and list-mode OSEM for the brain SPECT phantom reconstruction

Brief for an unattended Claude Code session (started 2026-10-14 in screen `recon_algorithms`; the
user is offline). Work autonomously; do not wait for answers. When a choice is open, take the
conventional one and record it in the report.

## Read first

- `CLAUDE.md` (repo root) and `dev/reports/2026-10_phantom_recon/NOTES.md` (study context, decisions;
  "Convergence" is the open item this task addresses).
- `dev/python/recon_brain_phantom_projections.py` (driver), `dev/python/compact_gpu_mlem.py`
  (`CompactGpuMLEM`: SRM on the GPU, 2 mm; `StreamingCompactMLEM`: module blocks streamed, 1.5/1 mm),
  `dev/python/merge_phantom_listmode.py` (how the per-job list-mode files become the binned
  projections: energy windows, in/out of FOV, primary vs phantom scatter, TEW windows).
- `dev/python/brain_phantom_recon/doc_2026-10-14/run_all.sh` and `run_unscattered.sh` (how the
  existing runs were made: support threshold 1000 at 2 mm, attenuation factors file).
- `dev/python/make_jaszczak_doc_figures.py` (`Grid`, `run_metrics`, `true_concentration`: the metric
  definitions every result must be scored with).

## Data

- Binned: `/data/<user>/opengate_sim/data/brain_phantom/ospool/full_small_jaszczak_15mCi_20261009T225845Z/merged/projections.npz`
  (73 modules x 625 pixels).
- List mode: `.../full_small_jaszczak_15mCi_20261009T225845Z/jobs/*/listmode.npz` (3,761 jobs, 6.8 GB):
  per event `head` (module), `pixel` (0-624), `energy_kev`, `time_s` (within the job's 0.5 s slice),
  `phantom_scatter`, `event_mm` (decay position). Use exactly the selection rules of
  `merge_phantom_listmode.py`, so that histogramming your selected events reproduces the binned
  `in_fov_primary` / `in_fov_total` / `full_total` main-window data exactly (check this; report the
  check). Job time slices: see the job manifests / meta; order events by absolute time if you need
  time-ordered subsets.

## What to implement

1. **OSEM (binned)**: ordered subsets of modules (rows grouped by module, so it works with both
   engines). Balanced subsets: interleave modules across the 7 rings so each subset sees the whole
   FOV from all directions; document the ordering. Per-subset sensitivity = column sums of that
   subset's rows (attenuated SRM when AC is on). Keep the support mask (air-SRM support, as now).
   OSEM with 1 subset must reproduce MLEM (check to float tolerance).
2. **List-mode MLEM**: lambda_j <- lambda_j / s_j * sum_events H_ej / (sum_k H_ek lambda_k), where the
   event's system row is the SRM row of its (module, pixel); s_j = full sensitivity. On the GPU, with
   the same matrix storage as the binned engine (gather rows by event index; do not duplicate
   rows per event in memory). With unit event weights this is mathematically identical to binned MLEM
   on the same events: verify that numerically on in_fov_primary (2 mm, AC) and report the max relative
   difference.
3. **List-mode OSEM**: events split into S subsets (time-ordered chunks of equal size, the standard
   choice; also try random interleaving if cheap), sensitivity s_j / S per subset (Reader et al. 2002
   convention). Record the choice.
4. Driver integration: `--algorithm {mlem,osem,lm-mlem,lm-osem}`, `--subsets N`, `--listmode-dir`
   in `recon_brain_phantom_projections.py` (default unchanged behaviour = mlem). Output files keep the
   current npz format (`iterations`, `estimates`, ...) plus `algorithm`, `subsets`, and an
   `updates` array (iterations x subsets) so analysis scripts keep working. full_tew is binned-only
   (it is a subtraction); say so in --help. The streaming engine (1.5 / 1 mm) is a stretch goal:
   do OSEM there only if the compact engine work is finished and validated.

## Experiments (2 mm SRM, support 1000, attenuation factors as in run_all.sh)

- Output under `dev/python/brain_phantom_recon/doc_2026-10-14/algorithms/<run>/`; never overwrite
  existing runs or `doc_2026-10-14/metrics.json`; write `algorithms/metrics.json` with
  `run_metrics` instead.
- Data set `in_fov_primary` (unscattered, the cleanest test) for all four algorithms; `full_tew` for
  MLEM vs OSEM (binned).
- OSEM subsets: e.g. 1 (= MLEM), 4, 8, 12 (or divisors that balance 73 modules sensibly); save
  iterations so that the number of sub-updates (iterations x subsets) covers 1-5 iterations and up to
  at least 400 MLEM-equivalent updates; compare at equal updates and at equal wall time.
- LM-OSEM with the same subset counts on in_fov_primary.
- Report contrast (rods 7.9, 6.4, 4.8; spheres 25.4, 12.7, 9.5), accuracy, rim/centre, noise (CoV),
  outside share against MLEM at 400 iterations, and wall time per iteration. Note where OSEM's limit
  cycle / noise growth shows.

## Rules

- Python: `~/.local/share/micromamba/envs/opengate/bin/python` (absolute path; `ma` is
  not available here). Run from `dev/python`.
- One GPU job at a time (RTX 3080 Ti, 12 GB); check `nvidia-smi` first. Runs longer than ~8 min: start
  them in the background with a log file (`nohup ... > log 2>&1 &`) and poll.
- Do not commit or push; do not delete files; do not edit the slides (`dev/reports/2026-10_phantom_recon/quarto`).
  Match the surrounding code style (comment density, naming).
- Small unit tests for the algebra on a tiny random matrix (CPU torch is fine) are welcome; put them
  next to the engine (e.g. `dev/python/test_recon_algorithms.py`).

## Deliverables

- Code: engine changes, driver flags, tests.
- Results: runs + `algorithms/metrics.json`.
- `dev/reports/2026-10_phantom_recon/osem_listmode_report.md`: what was implemented and how (equations,
  subset choices), validation numbers (OSEM S=1 vs MLEM, LM vs binned, histogram check), result tables,
  timings, caveats, next steps. Also update the "Convergence" item in `NOTES.md` with a short summary
  and a pointer to the report.
- Write `dev/reports/2026-10_phantom_recon/osem_listmode_STATUS` with one line ("running: ..." while
  working, "done" or "blocked: <reason>" at the end) and keep it current.
