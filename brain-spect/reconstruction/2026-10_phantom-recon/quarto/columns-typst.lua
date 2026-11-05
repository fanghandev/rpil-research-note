-- Typst output only: turn reveal.js-style column divs into a Typst grid, so one .qmd lays out
-- side by side in both formats:
--   :::: {.columns}
--   ::: {.column width="60%"} ... :::
--   ::: {.column width="40%"} ... :::
--   ::::
-- Column widths become fractions (60% -> 60fr), leaving room for the gutter.
if not quarto.doc.is_format("typst") then
  return {}
end

function Div(el)
  if not el.classes:includes("columns") then
    return nil
  end
  local widths, cells = {}, {}
  for _, c in ipairs(el.content) do
    if c.t == "Div" and c.classes:includes("column") then
      local w = c.attributes["width"] or "1"
      table.insert(widths, (w:gsub("%%$", "")) .. "fr")
      table.insert(cells, c.content)
    end
  end
  local out = pandoc.List()
  out:insert(pandoc.RawBlock("typst", "#grid(columns: (" .. table.concat(widths, ", ") .. "), column-gutter: 1.2em, ["))
  for i, cell in ipairs(cells) do
    if i > 1 then
      out:insert(pandoc.RawBlock("typst", "], ["))
    end
    out:extend(cell)
  end
  out:insert(pandoc.RawBlock("typst", "])"))
  return out
end

-- One slide per level-1 (section) or level-2 heading: an explicit page break before it (weak: no
-- empty pages). On a level-2 slide the body sits between two #v(1fr) spacers, so it is vertically
-- centred under the title (Keynote's body box); a body that fills the page just flows as before.
function Pandoc(doc)
  local out, open = pandoc.List(), false
  local function close()
    if open then out:insert(pandoc.RawBlock("typst", "#v(1fr)")) end
    open = false
  end
  for _, b in ipairs(doc.blocks) do
    if b.t == "Header" and b.level <= 2 then
      close()
      out:insert(pandoc.RawBlock("typst", "#pagebreak(weak: true)"))
      out:insert(b)
      if b.level == 2 then
        out:insert(pandoc.RawBlock("typst", "#v(1fr)"))
        open = true
      end
    else
      out:insert(b)
    end
  end
  close()
  doc.blocks = out
  return doc
end
