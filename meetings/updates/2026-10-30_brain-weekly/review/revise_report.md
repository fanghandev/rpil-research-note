I've revised the report and `build.sh` runs cleanly, with no warnings or unresolved citations. It is now 21 pages: main text 1–15 with the summary on page 1, appendix 16–19, references 20–21. I inspected every page as a 60 dpi image (`/tmp/claude-1002/weekly_pages2/p-*.ppm`) over four rounds of layout fixes.

**Lead's notes:**
- **Slice figures:** every panel now has the same 6 mm FWHM post-filter, with one 0–1.3 grey scale, a scale bar on the first panel of each row and one colour bar. The reference is a fourth column in the gammart rows only, and the GATE cell says "no primary-only GATE data".
- **One deviation:** the Derenzo and triple-line backgrounds have no activity, so normalising to a background mean is undefined. I normalised those to the 8 mm rod centres and to the centre-line peak instead, and the caption says so.
- **WP4:** all statements now match the corrected plan. TEW matches the oracle except on GATE cupping, and it reaches the reference only on 6 mm V/P and the 25.4 mm sphere.
- **Edge strip:** labelled PROPOSED everywhere.

**Reviews:** all fact-check items are fixed. All three citation tasks are done: bib replacements, restored references, and softened claims. Every MUST editorial item is done; three only partly:
- **WP0 spectra figure:** it keeps its original colours, because rebuilding it needs the GPU ray tracer.
- **Decision deadlines:** no source gives dates, so each decision names the work it blocks instead.
- **Float placement:** the 15-page limit left no room for a forced page break before §4.2. Tables no longer float, but images still do.

Five figures were redrawn from their data with non-blue colours for the apertures. To fit 15 pages, seven supporting figures moved to the appendix, with their numbers kept in the text.

**Not done:**
- `furenlid2004`: no sentence in the report concerns that system.
- Zannoni quote endings: not re-checked against the PDF.
- Author and date on one line: the Quarto template fixes that layout.

Each review item and its outcome is listed under "Revision 1" in `ingredients/draft_log.md`.
