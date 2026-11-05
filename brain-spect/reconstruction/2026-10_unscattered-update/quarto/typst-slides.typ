// Slide styling for Quarto's typst format (inserted at the start of the body).
// Page size, margins and base font come from the front matter (papersize, margin, fontsize,
// mainfont); columns-typst.lua puts a page break before every level-2 heading (one slide each)
// and turns .columns divs into grids.
#set par(justify: false)
#show heading.where(level: 1): it => block(above: 30%, text(font: "Inter Display", size: 2.6em, weight: "bold", tracking: -0.02em, it.body))
#show heading.where(level: 2): it => block(below: 0.8em, text(font: "Inter Display", size: 1.3em, weight: "semibold", tracking: -0.01em, it.body))
#set text(fill: rgb("#1d1d1f"))
#set list(spacing: 0.7em)
#show table: set text(size: 0.8em)
#show raw: set text(size: 7pt)
#show raw.where(block: true): set par(leading: 0.45em)
#show math.equation: set text(font: "New Computer Modern Math")
