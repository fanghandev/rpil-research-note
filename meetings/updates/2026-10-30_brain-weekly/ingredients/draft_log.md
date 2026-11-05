# Draft log: weekly Brain SPECT update, 30 Oct 2026

## What was done
- Read brief, facts, figures, references seed, both lit notes, the precedent report, PLAN
  (`pytorch-optix/docs/paper2_plan.md`), the 28 Oct resolution report (qmd, `_tables/`, phase0, lir, square_pinhole.md),
  the 28 Oct update (`update.md`) and the ACCESS progress report.
- `references.bib`: 14 entries. Authors as initials, as in the seed list; full first names only for DB-SPECT, copied
  from the local bib `qmirt-gate-10-sim/results/brain_spect/references.bib`.
- `scripts/make_figures.py`:
  - 12 new figures: 4 schematics; WP1 and WP3 summaries regenerated from the JSON in house colours; WP4 scatter
    spectra, kernel coverage, ladder, uniform-section profile and two slice panels.
  - 8 verified figures copied from earlier reports.
  - Derived numbers go to `img/figure_numbers.json`. Checked against facts.md: composition 76.32/22.35/1.33 %;
    Derenzo TEW/true 1.054 (+5.4 %); old kernel 104–156 empty rows; new kernel minimum 3036 (≥ 3000);
    box ⊗ box 11.08 mm; quadrature 14.40 mm.
- `report.qmd` rendered with Quarto 1.10 / Typst, using Typst's built-in `ieee` bibliography style (no `ieee.csl` on
  disk). `_header.typ` adds the INTERNAL header, table style, and floating image figures.
- Every page was inspected as PNG and the layout iterated:
  - figure sizes;
  - table alignment and column widths;
  - duplicated block removed;
  - Phase 0, LIR, terms-vs-b and square-pinhole details moved to the appendix to keep the body at 14 pages.
- Result: 18 pages in total. Body pp. 1–14, appendix pp. 15–17, references pp. 17–18.

## Numbers not verified or changed
- facts.md says WP1 window ratio "over 13 cases". `wp1_results.json` and PLAN have **10 cases** (0.9991–1.0035); the
  report uses 10.
- WP3 edge-strip values in facts.md (6.15 % Jaszczak GATE) are fluorescence-on. The WP3 figure shows fluorescence-off
  values (6.24 / 6.22 %) and says so. The text quotes the rounded 6.2 / 7.5 / 0.4 %.
- Removed from the draft because they were not in a source:
  - a "15 % low" reading of the uncorrected profile;
  - the claim that the Phase 0 drop beyond 38° is shield vignetting;
  - a g × 10⁶ = 4.687 worked number at 30°, whose distance basis was unclear.
- The jaszczak reference profile (primary-only gammart) is noisy at 128 iterations. It is shown as computed, and the
  caption says why.
- WP0 Expanse cost is not in any source, so it is left out of the compute table.
- The "cardiac comparison" uses only PLAN statements (one design per collimator length, 40; side leak in the cardiac
  geometry). No cardiac numbers were found.

## Citations
- Dropped as citation-only, per brief rule 6: Ogawa 1991 (TEW), Jan 2004 / Sarrut 2022 (GATE), Hudson & Larkin 1994,
  Barrett 1994, Fessler & Rogers 1996, Paix, Anger, Mallard & Myers, Goulet & Joy, Vastenhouw & Beekman (web snippet),
  Dewaraja 2006 (web PDF).
- Dropped because the title could not be verified (no web access in this session): Lai & Meng 2018 (MRC-SPECT-II),
  Mandot 2025.
- Not used (no claim needed them): Metzler 2001, Smith & Jaszczak 1997, Xia 2013/2015, Metzler 2014,
  Deprez 2013, Tenney 2001, Bal & Acton 2006.
- Kept although marked [citation]: Hutton, Buvat & Beekman 2011. facts.md names it as the general scatter citation.
  It is cited only as background, with no claim attributed to it.
- Verified locally: the Feng arXiv 2212.14505 title (lit notes, local full text) and the DB-SPECT title (local bib).
  Both are cited with their stated verification level ("read in full" / "abstract only").

## Revision 1 (30 Oct 2026): fact, editorial and citation reviews, and the lead's notes

### Result
- `build.sh` runs cleanly: 20 figures built, no warnings, no unresolved citations.
- 21 pages: main text pp. 1–15, appendix pp. 16–19, references pp. 20–21.
- The executive summary fits on page 1.
- Page images in `/tmp/claude-1002/weekly_pages2/p-*.ppm` (60 dpi). Every page was inspected over four render iterations.

### Lead's notes
1. **Slice figures:** done.
   - Same 3D Gaussian post-filter (6 mm FWHM) on every panel; the metrics stay unfiltered.
   - The reference is a 4th column in the gammart rows only; the GATE cell says "no primary-only GATE data".
   - One grey scale, clipped at 0–1.3; scale bar on the first panel of each row; one colour bar.
   - Jaszczak: each panel normalised to the uniform background of its own slice (water > 3 mm from rods and stems, > 6 mm from spheres, as in `wp3_metrics`).
   - **Deviation:** the Derenzo and triple-line backgrounds are cold (zero activity), so a background mean is undefined. They are normalised to the 8 mm rod centres and to the centre-line peak instead, as stated in the caption.
2. **WP4 statements match the corrected plan (lines marked "corrected 2026-10-30"):** done.
   - TEW matches the oracle except GATE cupping (1.032 vs 1.006, split SD 0.022).
   - TEW overestimates the scatter total by 5.4 / 7.7 / 15.3 %.
   - GATE has 12–28× gammart's counts.
   - The reference is reached on 6 mm V/P and the 25.4 mm sphere, not on 7 mm V/P, the 12.7 mm rods or cupping.
3. **Edge strip labelled PROPOSED (decision pending)** in the summary, the section title, the text and the open-issues table: done.
4. **Main text ≤ 15 pages:** done (15). To get there:
   - Kernel coverage, uniform profile, scorecard curves, WP2b maps, terms-vs-b, LIR and Phase 0 moved to the appendix; their numbers stay in the text and tables.
   - Summary tightened.

### Fact-check (review_fact.md)
- **E1** TEW = oracle "in every metric": corrected to "except GATE cupping" in the summary, §4.4, the ladder caption and the parked-scatter paragraph. Done.
- **E2** "per-module kernel": now "pooled over the modules of one aperture size and the 8 symmetries" (text and Fig. 5). Done.
- **I3** "reaches the reference": limited to 6 mm V/P and the sphere, with the three misses listed. Done.
- **I4** Profile caption: now quotes the GATE cupping 0.875; gammart 0.857 is in the ladder text. Done.
- **I5** Edge strip: PROPOSED. Done.
- **I6** Uniform C:
  - "beats every mixed map" → "no mixed design beats".
  - The scorecard table now has all 8 designs, including best assignment and continuous widths (0.38).
  - Best assignment and rings noted as better on 6 mm V/P.
  - Done.
- **I7** "It does not include the detector": moved; the best-module values (7.1 / 6.6 mm) are now said to include the detector. Done.
- **I8** Ratio table: caption explains that the slice z = 25.5 mm ρ = 0 point is not the centre. The summary gives 12.1 (A) to 14.4 (C) and 18.15 (D). Done.
- **I9** A_eff C at 30°: 2.027 mm² at φ = 0 (trace table). Done.
- **I10** Phase 0:
  - Figure redrawn from `phase0.json` with the correct axis label. Checked that `ratio_mc_over_g_paix` uses the corrected form: mean 0.982 above 28°, against 1.18 for the old form.
  - "Flat" qualified: 0.971–1.000 (1st–99th percentile) up to 37°; down to 0.863 at 38–41° (FN `phase0_sens_ratio`).
  - Notation now says θ up to 41°.
  - Done.
- **I11** Compute: 0.16 K core-h non-preempt added; the 509,166 SU (28 Oct) and 514.8 → 514.4 K plan readings both quoted with their dates. Done.
- **I12** WP0: caption reworded (the vacuum excess 1.39 disappears without Doppler; Standard gives the deepest valley); the 12 % deficit at 34–50 keV mentioned. Done.
- **I13** "lose 30 %" → "widens by 30 %". Done.
- **I14** Meng: "at higher sensitivity for the mix", plus CNR and CRC context. Done.
- **S15** ±0.02 vs between-map SD 0.039; the 0.07 gap = 1.8 SD. Done.
- **S16** TEW over-estimates for all three phantoms in the main text. Done.
- **S17** Reference wording (pooled kernel; matrix 0.4–1.1 %, 3.5 % for the top module); quarters 15–28 M; 12–28×. Done.
- **S18** "a ray through the pinhole centre" stays in one pixel; aperture and Compton spread give the 1.8–1.9 mm spot. Done.
- **S19** f = 25 mm + mean depth, rounded (notation table). Done; the 2.55 mm WP1 depth is not repeated in the text.
- **S20** Edge-strip caption: values in row order; point-source rows marked gammart only. Done.
- **S21** Simulated exposure (Jaszczak 51 %, fluorescence off 14–39 %, etc.) added to the WP3 setup. Done.
- **S22** facts.md "13 cases": source-sheet issue, already logged above; the report uses 10. No report change.

### Editorial review (review_format.md)
**MUST**
1. **Summary jargon and pointers:** done.
   - Terms line defines WP0–WP4, paper 2, A–D and gammart.
   - § pointers on every bullet and decision.
   - New opener ("approach the reference", softened from the reviewer's "reach" to match the corrected plan).
   - "Oracle" and "cell 625" are defined in §2.2, §4 and the abbreviations.
2. **Decisions 1 and 5:** done.
   - Inventory wording now matches the System paragraph; decision 5 rephrased.
   - Each decision has a recommended default.
   - **Partly:** no calendar "needed by" dates exist in any source, so each decision names the work it blocks instead.
3. **Resolution bullet:** split into two, with aperture letters. Table 8/9 numbers reconciled in the ratio-table caption. Done.
4. **Symbol clashes:** done.
   - ρ for the image radius; converging pitch $2z/35$ with z defined.
   - Windows renamed $\Delta E$; window counts $N_l$, $N_u$.
   - LIR regulariser λ (times the largest eigenvalue).
   - Attenuation renamed Γ; $\bar y_i$ written with i.
5. **Legibility:** done.
   - All redrawn figures are sized at the printed width with fonts ≥ 7 pt.
   - Fig. 4 (WP3) reduced to two panels; the band ratios moved into Table 4.
   - Pinhole schematic (Fig. 10) redrawn, with the numbers in the caption.
   - **Partly:** the WP0 spectra figure is still the copied original. Rebuilding it needs the OptiX tracer on the GPU (GPU jobs not allowed); it is enlarged to 80 %.
6. **Reconstructed images:** done.
   - Shared 0–1.3 scale, scale bar per row, colour bar, larger row labels, "fluor. on" in the GATE rows.
   - Slice positions and "nearest-neighbour display" stated in the captions; width 80 %.
7. **Float placement:** done.
   - Tables are no longer floated; equation 2 stays with its "where" text.
   - The page budget did not allow a forced page break before §4.2; images still float with Typst `placement: auto`. Inspected: no section is split from its own text by more than one figure.
8. **Ladder table:** split into a gammart and a GATE table (rows = steps, columns = metrics, ↑/↓ in the headers); the figure kept. Done.
9. **Colour consistency:** done.
   - Apertures A–D use yellow / purple / vermilion / green in all redrawn figures (terms, information, Phase 0, scorecard).
   - Scatter classes use vermilion / orange / purple; WP2b map types use non-blue, non-grey colours.
   - WP3 phantoms are now on the x axis rather than colour-coded.
   - Exception: the copied WP0 figure keeps its original colours (see 5).
10. **Duplicates and orphans:** done.
    - §3.2 cost paragraph cut; §7 now holds all compute.
    - §5.3 reduced to one sentence plus a link.
    - The orphan sentence merged into §7.

**SHOULD**
11. **Section order:** not reordered. The § pointers in the summary are the "either/or" fix the reviewer allowed. The notation table stays near the start, as the brief requires.
12. **Title block:**
    - Done: subtitle shortened to one line; INTERNAL banner line added.
    - Not done: author and date on one line (the Quarto Typst template controls that layout).
13. **Fig. 5:** "Γ ∘ H" is now one box; the duplicate equation removed; full width; one symbol per box; H noted as 73 × 626 rows. Done.
14. **Fig. 10:** redrawn with only b, f, $R_g$, $R_i$ (two panels, not to scale). Done.
15. **Acronyms:** an abbreviations list after the notation table (OSEM, CRC, NRMSE, CNR, S/B, LIR, DOI, SU, XCAT, pull rms, split SD, oracle). Done.
16. **Tone:** "What the TEW windows contain"; "It is small" replaced by the value. Done.
17. **Notation table:** value column widened (13/47/40). Done.
18. **Table 12 (compute):** collapsed to one line per WP. Done.
19. **Table 3 colwidths:** [50, 30, 20]. Done.

**COULD**
20. **Footer and header:** "Page n of N" footer and a dated header. Done.
21. **References:**
    - [8] venue fixed (Goorden NSS 2008).
    - "AM2004" written as "Accorsi–Metzler".
    - Article numbers kept with their leading zero (moved to `note`).
    - Partly: IEEE style abbreviates Moore et al. (8 authors) to "et al."; left as the style does it.
22. **Appendix figures:** the PSF figure cropped to its middle column (point-profile cuts, incl. the diagonal); Phase 0 and the others enlarged. Done.
23. **Fig. 2 labels:** "θ …, w = … mm" and an x axis "GATE / gammart". Done.
24. **p.14 white space:** the main text now ends on p.15 with §7–§8 filling most of the page. Done.

### Citation review (review_cite.md)
- **Bib fixes:** done.
  - `feng2024dc` (Biomed. Phys. Eng. Express 2024, preprint noted) replaces `feng2022dc`; the text says it was read as the preprint.
  - `goorden2008` (abstract claim) plus `goorden2009` (full paper, not read) replace `rentmeester2008`.
- **Restored where the text mentions them:** done.
  - `ogawa1991` at TEW; `jan2004` and `sarrut2022` at GATE/opengate; `hudson1994` at OSEM; `dewaraja2006` at MC scatter in OSEM.
  - `lai2018` (MRC-SPECT-II, quote from the full-text notes) and `mandot2025` (abstract only, dual-FOV system) in the Meng-group evidence.
- **Added:** `sabet2012` (LIOB) and `zhang2026` (converging-pixel CsI:Tl decoding; also cited for the plan's 11.8 % energy resolution) in §1 System and §2.1. Done.
- **Not added:** `furenlid2004` was suggested but no sentence in the report concerns FastSPECT II.
- **Softened claims:** done.
  - DC-SPECT is "similar but not identical" (geometry differences listed), and the rule's origin is labelled "our inference"; 4.5 mm is called the reconstructed central resolution from rods.
  - "We found no closed-form FWHM" for the square.
  - Metzler & Moore eq. 22/25 "transcribed via a PDF agent and to be confirmed"; the Paix = A_eff identity is stated as our derivation, with the agent transcription as the cross-check.
  - DB-SPECT wording "as recorded in our literature notes, not re-verified against IEEE Xplore".
  - Zannoni CNR/CRC from bar-chart labels, in the table note only; the prose has no CNR/CRC numbers; "502 modules".
  - Accorsi–Metzler eq. 22 reproduction attributed to our derivation; the RMS ×2 / FWHM ×1.3 figures marked as our calculation, with Metzler 2002 for the definitions only.
- **Quote endings (Zannoni):** not re-checked against the PDF (no access this session). They are as transcribed in `lit_notes_meng_sabet_resolution.md` from the full text.
