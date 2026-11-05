I've written `literature_check.md`. Every equation transcription in `square_pinhole.md` and `crosscheck_tables.py` is correct, and no numbers change.

- **M&M 2020 eq. (22) and the code:** I compared it term by term with `area_eff_mm2020`: no transcription error. The comparison is genuinely independent, because the model sums the strip and corner integrals piece by piece. I wrote a literal-form numerical check in `/tmp` but couldn't run it (Python wasn't permitted), so the match rests on the hand comparison.
- **M&M 2020, other claims:** eq. (25), the eight-half-plane geometry, penumbra eqs. (26)–(29) and the 0.16 % / 0.29 % validation are all confirmed. The paper has no resolution formula.
- **AM2004, Metzler 2002, M&A 2005, Moore 2016:** all quoted equations are confirmed.

**Corrections needed:**
1. **§3.3 and the `crosscheck_tables.py` docstring:** τ isn't in eq. (22); it's the tapering function of eq. (29). Eq. (22) is the penetration part only, so the area is w² + g_pen·4πh²/cos³θ. Add the validity limit: outside the penumbra, to leading order in 1/h.
2. **§2, Anger/Paix row:** d_re < Anger only holds when d > 0.216 mm here (AM2004 eq. 43). A–D meet this, but it isn't unconditional.
3. **§4 item 1:** AM2004 §V means other edge *profiles* (its example is the keel edge), not other aperture outlines. Applying it to a square is our extension.
4. **§4 item 3:** add M&A's caveat that the ⁵⁷Co 1 mm data are "less conclusive" (about 0.1 mm systematic offset).
5. **§4 item 6:** Johnson's Fig. 6(c) does show FWHM versus the in-plane profile direction, falling from the flat-to-flat direction to 45°. The widths come from an on-axis point source. Only 0.364 vs 0.414 mm is in the text; "11–12 %" is read off a figure.
6. **§4 item 9:** Moore never states "in the direction considered"; they give the two half-angles (17.1° / 14.9°) and check both directions.
7. **The "no closed-form FWHM" claim:** it holds for these six papers, but not yet for the wider literature. The file lists nine unread candidates from the reference lists. The biggest risk is the slit–slat papers (a slit is a straight knife edge, like one side of our square), which may already contain our side formulas. I cited those from memory, so verify them.
