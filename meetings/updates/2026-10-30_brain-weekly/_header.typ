// Page header and footer on every page (internal document), compact tables and captions, floating figures.
#set page(
  header: context [
    #set text(8pt, fill: luma(100))
    Brain SPECT weekly update · 30 Oct 2026 #h(1fr) #text(weight: "bold", fill: rgb("#a33"))[INTERNAL] #h(0.6em) Fang Han
  ],
  footer: context [
    #set text(8pt, fill: luma(100))
    #h(1fr) Page #counter(page).display() of #counter(page).final().first() #h(1fr)
  ],
)
#set par(justify: false)
#show figure.caption: set text(8.6pt)
#show table: set text(8.6pt)
#set table(inset: (x: 4pt, y: 3pt), stroke: (x, y) => (top: if y <= 1 { 0.6pt } else { 0.25pt + luma(200) }, bottom: 0.6pt))
#show table.cell.where(y: 0): set text(weight: "bold")
#show raw: set text(size: 8pt)
#show heading.where(level: 1): set block(above: 1.3em, below: 0.7em)
#show heading.where(level: 2): set block(above: 1.0em, below: 0.55em)
#show table: set par(justify: false)
#show table.cell: set align(left)
#set bibliography(title: [References])
#set figure(placement: auto)
#show figure.where(kind: "quarto-float-tbl"): set figure(placement: none)
