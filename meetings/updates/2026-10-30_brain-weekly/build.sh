#!/usr/bin/env bash
# Weekly Brain SPECT update, 30 Oct 2026: figures, then the PDF.
set -euo pipefail
cd "$(dirname "$0")"
CUDA_VISIBLE_DEVICES="" micromamba run -n raytracing env -u DISPLAY python scripts/make_figures.py
CUDA_VISIBLE_DEVICES="" micromamba run -n raytracing env -u DISPLAY python scripts/fig_triple_scale.py
micromamba run -n opengate quarto render report.qmd --to typst
