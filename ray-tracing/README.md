# GPU ray tracing for SPECT system modelling

| Folder | What |
| --- | --- |
| [`nv-warp-rtx/`](nv-warp-rtx/) | NVIDIA Warp ray-tracing prototypes (frustum and slab-slit pinhole models), coding plan, per-crystal simulation maps |
| [`differentiable-rtx/`](differentiable-rtx/) | Proposal and implementation memo for differentiable ray-traced SPECT calibration (Quarto sources, PDFs, bibliography) |

The OptiX tracer `gammart` (repository pytorch-optix) built the ray-traced brain SRM used
in [`../brain-spect/studies/2026-10_rim-streaks/`](../brain-spect/studies/2026-10_rim-streaks/).
Reference papers are in [`../references/`](../references/).
