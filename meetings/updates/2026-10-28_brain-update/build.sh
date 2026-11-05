#!/bin/bash
# Build the 2026-10-28 brain SPECT update: figures -> article.qmd (from update.md) -> HTML article + reveal.js slides.
# Quarto runs in the opengate env (as docs/design_surrogate/build.sh and the other report folders); figures in raytracing, DISPLAY unset.
#   build.sh [--no-figures]
set -euo pipefail
cd "$(dirname "$0")"
[[ "${1:-}" == "--no-figures" ]] || micromamba run -n raytracing env -u DISPLAY python make_figures.py
# article.qmd = front matter + the body of update.md (the master source), figure paths unchanged (quarto/img -> ../img)
{
cat <<'H'
---
title: "Brain SPECT study: where we stand"
subtitle: "73-module knife-edge pinhole helmet, Tc-99m 140 keV, CsI(Tl) 25 x 25 pixel detectors. Research-group update, 28 October 2026"
author: "Fang Han"
date: 2026-10-28
date-format: "D MMMM YYYY"
lightbox: true
execute:
  echo: false
format:
  html:
    toc: true
    toc-depth: 3
    number-sections: false
    html-math-method: mathjax
    embed-resources: true
    code-fold: false
    fig-cap-location: bottom
    theme: cosmo
    css: article.css
---
H
awk 'BEGIN{n=0} /^---$/ && n<2 {n++; next} n>=2 {print}' update.md
} > quarto/article.qmd
# every figure used on the slides must exist; every figure of the article too
for f in $(grep -ohE 'img/[A-Za-z0-9_.-]+\.png' quarto/article.qmd quarto/slides.qmd | sort -u); do
  [[ -e "$f" ]] || { echo "MISSING FIGURE $f"; exit 1; }
done
cd quarto
micromamba run -n opengate quarto render article.qmd 2>&1 | tail -3
micromamba run -n opengate quarto render slides.qmd 2>&1 | tail -3
ls -la article.html slides.html
