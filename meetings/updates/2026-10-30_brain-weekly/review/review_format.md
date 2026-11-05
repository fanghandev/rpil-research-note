# Editorial review: Brain SPECT weekly report (18 pp.)

The science is well organised and honest about its status labels. The weaknesses are: undefined project jargon, a dense summary, figures too small to read at print size, floats separated from their text, and symbol clashes.

## MUST (top 10)

1. **p.1, summary opener and bullets.**
   - Problem: "WP0–4", "paper 2", "Phase 0–3", "C", "18/18/18/19", "oracle" and "cell 625" are never defined, and the PI sees them first. The summary also gives no pointers to sections.
   - Fix: add a sentence at the top of the summary: "WP = work package of the paper-2 plan (WP0 spectrum check, WP1 one module, WP2 apertures, WP3 full-system GATE, WP4 reconstruction corrections). Paper 2 = the brain-system design paper."
   - Add "(§2.1)", "(§4.4)" and so on to each bullet and each decision.
   - Replace the opener "This week finished the checks that paper 2 depends on." with "This week we showed that GATE and gammart agree on the full brain system, and that the first corrected reconstructions reach the primary-only reference."

2. **p.1, Decisions 1 and 5.**
   - Problem: "18/18/18/19 inventory" contradicts the System paragraph (current inventory 19/18/18/18, annealed map 18/18/18/19). "The measured point response in the Derenzo" is also unclear, because the point response was withdrawn.
   - Fix for 1: "Aperture build. Is the current 19/18/18/18 inventory (A/B/C/D) already purchased? If not, build uniform C (1.215 mm); if yes, use the annealed placement map."
   - Fix for 5: "Approve Phases 1–3 of the resolution chain (Derenzo-based point response, V/P prediction, triple line on a 1 mm grid; §5)."
   - State a recommended default and a "needed by" date for each decision.

3. **p.1, resolution bullet.**
   - Problem: it is the densest bullet and carries four claims. "12.1–14.4 mm" does not say which modules, and Table 7's caption ("best module 12.1") conflicts with Table 8 (best module at r = 0 is 10.1).
   - Fix: split into two bullets. "Resolution: 'about 7 mm' is the aperture term only. Including the 2 mm detector pixel, a single module at the centre gives 12.1 mm (aperture A) to 14.4 mm (C); the 73-module count-weighted value is 15.5 mm."
   - Reconcile the 12.1/10.1/14.8/15.5 numbers in Tables 7 and 8 with a one-line note on slice z.

4. **Symbol clashes (Notation, Eqs. 1–7).** Each of these needs a fix.
   - $r$ is slant distance and also voxel radius (Tables 8 and 9, "r ≤ 142 mm"); use $\rho$ for radius.
   - $s$ is additive scatter and also the undefined "$2s/35$"; define it as the pinhole-to-pixel distance or rewrite it.
   - $W$ is effective width and also window width ($W_l$, $W_m$); rename the windows $\Delta E$.
   - $C_l$/$C_u$ clash with aperture "C".
   - $\alpha$ is the knife-edge angle and also the LIR regulariser; rename the regulariser $\lambda$.
   - $A$ is aperture A and also attenuation.
   - Eq. 1 says "row $i$" but contains no $i$; write $\bar y_i$.

5. **Figs. 3, 4, 7, 8, 12, 14, 16–20: tick labels and legends are unreadable at print size.**
   - Problem: Fig. 3 legend and axes are about 4 pt, Fig. 12 annotations overlap, and Figs. 14 and 16 have unreadable legends.
   - Fix: set fonts to at least 7 pt at final size and raise figure widths to 85–100 %.
   - Fig. 3: widths 58 % → 85 %, with four labelled lines.
   - Fig. 4: three panels in 96 % width crowd the titles; make it two rows or drop the third panel into Table 4.
   - Fig. 12: remove the overlapping text and put the numbers in the caption.

6. **Reconstructed images (Figs. 10, 11).**
   - Problem: the scale bar and colour bar appear only on the reference panel, and the row labels are tiny.
   - Fix: the caption says "each image normalised to its mean rod peak", which contradicts the brief's "same grey scale". Say "all panels share 0–1 normalised activity", add a 20 mm bar to every panel (or the first of each row), and enlarge the row labels.
   - Raise the widths from 66 % to about 85 %. State the slice position in the figure ("z = 0 ± 29 mm") and "fluorescence on" in the GATE row label.
   - The triple-line crop is blocky at 2 mm; say "no interpolation".

7. **Float placement.**
   - Fig. 6 sits above its section and splits Eq. 2 from its "where…" text (p.5→6).
   - The "Open" bullet breaks across pp.4–5, and Fig. 4 is far from its text.
   - Figs. 10–11 (pp.9–10) are far from §4.4 (pp.6–8); Fig. 12 is far from §5.1.
   - Fix: add `{{< pagebreak >}}` before §4.2, and keep the Eq. 2 "where…" paragraph with its equation.
   - Add `fig-pos="h"` or a caption `keep` for Figs. 5, 12 and 13.
   - Alternatively move Figs. 10–11 to just after the ladder bullets. Page 6 ends with about 25 % white space because Table 6 jumped, so shrink the ladder.

8. **Table 6 (ladder, p.7).**
   - Problem: "a / b / c" triplets in 5 columns wrap badly and are hard to scan, and "cupping" is not capitalised.
   - Fix: make rows = steps (none, AC, AC+K, +TEW, +true scatter, primary-only) and columns = metrics, one table for gammart and one for GATE. Keep Fig. 8 as the visual and put the numbers in the table.
   - Add an arrow (↓/↑) to each header to show which direction is better.

9. **Colour consistency.**
   - Fig. 6 uses blue for "primary" and Figs. 14 and 16 use blues for apertures A–D, but blue means gammart elsewhere.
   - Fig. 4 right uses grey for the phantoms, but grey means GATE.
   - Fig. 3 uses default rainbow colours.
   - Fix: recolour the class and aperture series with a non-blue/grey palette (for example, the Okabe-Ito purple/vermilion/yellow). Use the code colours only for GATE vs gammart.

10. **Duplicated and orphan text.**
    - Problem: §5.3 duplicates the appendix ("The classic papers treat round knife edges…" appears twice). "The constraint this week was the queue, not cost." is an orphan sentence. The §3.2 "Cost" paragraph and §7 repeat each other.
    - Fix: cut the "Cost" paragraph from §3.2 and keep §7.
    - Replace §5.3 with one sentence and a link: "Square-aperture formulas are derived and ray-trace-checked in §9.1; the only change is the corrected sensitivity obliquity, Eq. 5."
    - Merge the orphan sentence into the §7 intro.

## SHOULD

11. **Section order.** Decision 1 (apertures) is the headline decision but sits in §6. Either reorder (§5 aperture, §6 resolution) or add the section pointers from item 1. Consider moving the Notation table to §5, where most symbols appear, with a one-line key on p.1.
12. **Title block (p.1).** The subtitle wraps with a hyphenated "recon-struction". Shorten it to "Converging-pixel detector, validated simulation chain, scatter correction, resolution and aperture questions". Move "Internal" to a banner line and put author and date on one line.
13. **Fig. 5 (block diagram).** The "A ∘" box is truncated and the key equation is repeated inside the figure. Draw "A∘H" as one box and remove the duplicate equation. Enlarge it to 100 % width and add one symbol per box. Note that $H$ is 73 × 626.
14. **Fig. 12 (pinhole terms).** It should be the main schematic for §5.1 but reads as clutter. Redraw it with a larger angle and only $b$, $f$, $R_g$ and $R_i$, so it matches Eq. 3.
15. **Undefined acronyms.** Expand at first use: OSEM, CRC, NRMSE, CNR, S/B, LIR, DOI, SU, XCAT, "pull rms", "split SD". Define "oracle" as "TEW replaced by the true scatter from the truth Monte Carlo".
16. **Tone.** Replace "What TEW really measures" with "What the TEW windows contain". Replace "It is small." (p.4) with the value, "0.2–0.3 %".
17. **Table 1 notation.** The "value here" column wraps badly. Widen it or cut it to five rows (move the rest into the equations' "where" lines).
18. **Table 12.** Half the cells are empty. Collapse it to one line per work package: "WP3: 19 SU charged; 11.1 K core-h preempt (uncharged); 9 K core-h OSPool; 6.2 GPU-h workstation."
19. **Table 3.** Column 1 is too wide for its content; set colwidths to [50, 30, 20].

## COULD

20. **Footer and header.** Use "Page n of 18" instead of the bare number. Date the header ("30 Oct 2026") rather than repeating the range.
21. **References.**
    - [8] lacks a venue (it prints "…brain SPECT. 2008.").
    - [5] and [9] have "[Online]" and double spaces.
    - [11] uses "et al." while the rest list all authors.
    - Make the DOI format uniform (`doi:` vs URL).
    - "AM2004" is never expanded; write "Accorsi–Metzler [2]".
22. **Appendix (pp.15–16).** Fig. 17 is large and dense; its three panels are unreadable, so show only the diagonal cut. Fig. 18 and Fig. 19 are tiny; enlarge them or drop one.
23. **Fig. 2 right panel.** The case labels read "0°, 0.556" with no unit. Write "0°, w = 0.556 mm". Make the x-axis "GATE/gammart".
24. **p.14.** The page is half empty before the appendix. Pull the "Open issues" table onto its own page, or insert the page break before "Compute".
