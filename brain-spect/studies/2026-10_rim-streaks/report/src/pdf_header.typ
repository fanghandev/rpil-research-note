// Extra Typst rules for the PDF (pandoc puts this in the document header).
#show table: set par(justify: false)
#show table: set text(size: 8.5pt)
#show figure.where(kind: image): set figure(placement: auto)
#show figure.caption: set text(size: 9pt)
#show figure.where(kind: table): set block(breakable: true)
