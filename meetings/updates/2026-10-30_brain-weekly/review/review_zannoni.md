Both papers were read in full. Of the 12 items below, 7 are ok, 4 need a fix and 1 is an optional addition. The main problem is the Goorden claim (item 11); items 8–10 are small corrections.

**Zannoni 2021**

1. **Report line 463, §II-B.3 quote: ok.** It is verbatim. The paper (p. 3714) reads: "The specific combination of the three lofthole diameters is chosen to allow the system to sample the object at high spatial frequencies, while maintaining a relatively high sensitivity."

2. **Report line 463, design numbers: ok.** I confirmed all of these:
   - 502 modules, with 80×80 pixels at 250 µm pitch (§II-C).
   - MF 1:12 (§II-B).
   - 1 mm uniform loftholes, and the mix of 168×0.5 mm, 167×1.5 mm and 167×3 mm (§II-B.3).
   - All three types are used in every ring.

3. **Report line 469, FIM FWHM: ok.** The paper gives 20 mm for the 1 mm lofthole and 26 mm for the mix (§III-A, p. 3718, Fig. 5).

4. **Report line 470, rods resolved at S/B 20:1: ok.** The 1 mm lofthole resolves the 4 mm group and the mix resolves 6 mm (§III-D.2, Fig. 8A).

5. **Report line 471 and its footnote, CNR/CRC: ok.** The 4 mm labels in Fig. 8C and 8D match the report.

   | Aperture | CNR | CRC |
   |:---|:---|:---|
   | 1 mm lofthole | 14.7 | 35.5 |
   | Mix | 22.5 | 36.2 |

   The values are not in the text, so "read from bar-chart labels" is right. Suggested footnote text: "…bar-chart labels of Fig. 8C–D".

6. **S/B 5:1, optional addition to the table.** At 5:1 (Fig. 9, §III-D.2) the 1 mm lofthole and the mix both resolve only the 6 mm group; only the micro-ring resolves 4 mm. The 4 mm rods give CNR 5.5 vs 7.2 and CRC 31.3 vs 30.9 %. The report has no 5:1 row, so nothing there is wrong.

7. **Report line 479, §IV quote: ok.** The wording is verbatim and the section is right. It is item (c) of the list "we can conclude that…" in the Discussion (p. 3725), not in §V Conclusion. The sentence is: "(c) The combination of 3 types of loftholes having different diameters improves the system sensitivity but offers the lowest spatial resolution in this study."

8. **Report line 475, "Their explanation (§III-D.1)": fix.** This passage explains the Defrise-phantom (axial disks) result, not the hot-rod result. Replace with: "Their explanation for the axial (Defrise-phantom) result (§III-D.1):".

9. **Report line 477, quote: ok.** It is verbatim. The text is split across pp. 3719–3720, and the report's join is faithful: "…at the center of the FOV." continues "The reduction of the number…".

10. **Report line 479, §II-C quote: fix (minor).** It is verbatim but cut mid-sentence. The paper continues "…to achieve a high spatial resolution needed in brain imaging applications." Either add the closing words or end the quote with "…high spatial resolution" and no full stop inside the quotation marks.

**Goorden 2009**

11. **Report line 487: fix.**
   - **The 1 mm threshold is not in the 2009 paper.** It puts the crossover near 0.2 mm, not 1 mm.
   - **Quote 1, §4 (p. 6602):** "For detector intrinsic resolutions μR_i > 0.7 (typically R_i > 0.2 mm), the optimal detector radius is large, resulting in a magnified object projection onto the detector, thus reducing the image degrading effect of detector blurring."
   - **Quote 2, abstract:** "for detectors with intrinsic resolutions < 0.2 mm, it is beneficial to place the detectors close to the collimator, resulting in a high number of de-magnified projections."
   - **Table 3** shows magnifying optima for R_i = 1 mm (r_c 167 mm, r_d 343 mm), but there is no statement about "coarser than 1 mm".
   - **The 2008 abstract:** I can't confirm whether it says 1 mm. It is not in the references folder, and `review/review_cite.md` also says it was "abstract-only … could not check".
   - **The right citation is the 2009 PMB paper (@goorden2009).** It is the full brain-specific analysis, and `review_cite.md` already says to prefer it. Suggested replacement for line 487:

   > "**Goorden, Rentmeester and Beekman** [@goorden2009] show analytically that for conventional detectors (intrinsic resolution above about 0.2 mm) the optimal full-ring multi-pinhole brain geometry magnifies ("the optimal detector radius is large, resulting in a magnified object projection onto the detector", §4), while for detectors below 0.2 mm de-magnified projections with the detector close to the collimator are better (abstract)."

   If `@goorden2008` is no longer cited anywhere, drop it from `references.bib`; it is cited only on line 487. Also update the source comment on line 461, which says "Goorden 2008 [abstract]".

**Section references**

12. **§II-B.3, §II-C, §III-D.1 and §IV: ok.** These are the section labels used in the report, and all are correct. The only caveat is the one in item 7: the §IV item (c) sits in the Discussion, and the report is right to call it §IV.
