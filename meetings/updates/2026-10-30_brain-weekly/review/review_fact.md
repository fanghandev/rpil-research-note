I found 2 errors, 12 imprecise statements and 8 suggestions. I checked every number against the plan, the JSON outputs and the analysis files. I read the figure-script code behind each data figure. I looked at only 5 of the 21 images (the Derenzo/triple-line slices, WP0 spectra, WP2b maps, the information plot and Phase 0); the rest I checked from the code alone.

**Errors**

1. **Lines 41, 242 and the ladder figure caption (line 236): "TEW equals the true-scatter oracle within 1 split SD in every metric, for GATE and for gammart."** This is wrong for GATE cupping: 1.032 (TEW) against 1.006 (true scatter) is a gap of 0.026, larger than the split SD of 0.022 (`pytorch-optix/out/wp4/wp4_results.json`, jaszczak it128). The plan (line 551) makes the same mistake. — **error**
2. **Line 175: "K is the per-module Compton-centroid kernel."** The kernel is pooled over all modules of one aperture variant and the 8 symmetries of the square (`paper2_plan.md`:424–426). The report's own forward-model figure ("626 × 626 per aperture variant") and the open-issues table ("pooled over modules") say so. — **error**

**Imprecise**

3. **Lines 41 and 243, ladder caption: "with GATE's counts it reaches the reference."** This holds only for 6 mm V/P (0.112 vs 0.108) and the sphere (0.991 vs 0.995). The other metrics miss:
   - 7 mm V/P is 0.033 vs 0.029, about 4 split SD.
   - The 12.7 mm rods are 0.961 vs 0.898.
   - Cupping is 1.032 vs 0.991.
4. **Uniform-profile caption (line 245):** the dotted curve is GATE data (`make_figures.py` `fig_profile`), whose cupping is 0.875 (`air/gate_on`). The 0.86 quoted from the ladder table is gammart's (0.857).
5. **Edge strip:** the section is labelled FINAL and the summary says "For paper 2 it is its own element", but Decision 2 asks for confirmation. The plan (lines 440, 510) calls it a design decision that is still open. It should be labelled as proposed, pending a decision.
6. **Summary line 43: "Uniform C beats every mixed map tested."** The source says only that no mixed design *beats* uniform (`2026-10-28_brain_update/update.md`:295).
   - The "best assignment (C, one B)" row (1.05 / 0.82 / 0.43) matches uniform C within noise and is better on 6 mm V/P, as is "rings of B/C/D" (1.05).
   - Line 366 says "Eight designs" but the table shows six. The omitted continuous-width optimum reaches 8 mm V/P 0.38, better than C.
7. **Line 310:** "It does not include the detector" comes right after the best-module values of 7.1 and 6.6 mm. Those values do include the detector term (`analytic_baseline.qmd`:76, 89).
8. **The ratio table's r = 0 row (10.1 / 14.8) contradicts the centre values in the text (12.1 / 15.5).** The table is on slice z = 25.5 mm, so its r = 0 point is not the centre; this needs saying.
   - Line 42: "a module at the centre is 12.1–14.4 mm" holds for apertures A–C only. D is 18.15 mm (source line 148 says "A–C").
9. **Line 492:** A_eff for C at 30° is given as 2.029 mm², but the trace table (C, 30°, φ = 0) and the closed form both give 2.027. The source (`square_pinhole.md`:77) gives 2.029 without saying which φ it is for. State φ, or use 2.027.
10. **Phase 0 figure and line 330 ("flat in θ"):**
    - The copied figure's y-axis is labelled w_s²cos³θ/4πr², which is the old, wrong form.
    - The plotted ratio falls to 0.86–0.95 at θ ≈ 38–41°. Phase 0 covers θ up to 41° (`analytic_baseline.qmd`:238), while the notation table says "θ ≲ 35° in use".
11. **Line 161 and the compute table: "Only the 19 SU benchmark was charged."**
    - The plan (line 465) also lists 0.16 K core-h run outside the free preempt partition.
    - The 509,166 SU figure (28 Oct) predates the 514.4 K "used" figure in the plan's WP3 cost note.
12. **WP0 caption (line 137): "the remaining valley disappears without Doppler."** In vacuum GATE has an *excess* in the valley (ratio 1.39), and that excess is what disappears. With Standard physics the valley is deepest, matching gammart.
    - Line 130: "all at 60–100 keV" ignores the 12 % deficit at 34–50 keV (plan:288).
13. **Line 97: "parallel pixels lose 30 %."** The spot actually widens by 30 % (2.25 / 1.73).
14. **Line 43: "The Meng group's helmet study found the same."** That holds only for resolution. Their mix had higher CNR (22.5 vs 14.7) and similar CRC on the 4 mm rods (report's Zannoni table).

**Suggestions**

15. **Lines 43 and 377: "±0.02".** The relevant spread for a mixed map is the between-map SD of 0.039 (plan:332). The 0.07 gap between C and the current mix is about 1.8 of those SDs.
16. **Line 207:** +5.4 % is for the Derenzo only. TEW overestimates the true scatter by 15.3 % for the Jaszczak and 7.7 % for the triple line (`figure_numbers.json`, `truth_windows`). Say so in the main text, not only in the appendix.
17. **Line 224:**
    - "The model that matches primary-only data exactly" overclaims: the kernel is pooled, and the deterministic matrix differs from MC by 0.4–1.1 % (3.5 % in the top module).
    - The quarters are 15–28 M counts, not "about 15 M", given 59–114 M in total.
    - "26×" is the top of a 12–28× range.
18. **Line 86:** "stays in one pixel at any depth" is exact only for rays through the pinhole centre. The aperture width and Compton spread give the 1.8–1.9 mm spot.
19. **Line 60:** "25 mm + mean depth" gives 27.55 mm with WP1's measured 2.55 mm depth. The source rounds the depth to 2 mm.
20. **Edge-strip table caption:** the GATE/gammart pairs are listed Jaszczak/Derenzo/triple line, but the rows run Derenzo/Jaszczak/triple line. The point-source rows are gammart only.
21. **Line 143:** say that the simulated exposure differs from the nominal 15 mCi / 15 min: Jaszczak 51 %, fluorescence-off runs 14–39 % (plan:459).
22. **The source sheet, not the report:** `facts.md` says "13 cases" for WP1. The report's 10 is correct (the JSON has 10; the 3 fluorescence-on runs are separate).

**Confirmed correct**
- **WP0, WP1, WP3:** all numbers, the edge-strip shares, and the WP1 spot-width table.
- **WP4 tables:** every ladder value, the composition table, kernel coverage (156/156/120/104 rows empty before; minimum 3036 counts after), and the TEW formula with its 2.5 factor.
- **Classic-formula arithmetic:** the centre table and the sensitivity g = 8.169 × 10⁻⁶.
- **Square-pinhole formulas:** the equations for d_re, sensitivity, side widths and A_eff, including the √2, 1.13w and 1.155w equivalents.
- **Box-vs-Gaussian:** two boxes do give FWHM = the larger width (11.08 mm). The 10.5 mm figure checks out with C's penetration RMS of 0.476 mm.
- **Tables from the literature and other reports:** the LIR, Zannoni, scorecard and WP2b values, and the ACCESS figures.
- **Figures:** the slice z-ranges and normalisations match the script.
