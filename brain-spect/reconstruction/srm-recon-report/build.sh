#!/usr/bin/env bash
# Build srm_recon_report.pdf with re-encoded figures (full-resolution originals stay in figs/).
# Needs typst and Pillow (e.g. `ma opengate`). Run from anywhere.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(git -C "$here" rev-parse --show-toplevel)"
python "$repo/tools/reencode_images.py" "$here/figs" "$here/_build/figs"
typst compile --root "$here" --input figdir=_build/figs --input ext=.jpg \
  "$here/srm_recon_report.typ" "$here/srm_recon_report.pdf"
ls -la "$here/srm_recon_report.pdf"
