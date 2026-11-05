I wrote and ran `sympy_check.py` (about 100 s on 16 cores, via the ledger). **62 of 64 checks pass. No formula in §3.1–§3.3 or §3.7 is wrong.** The 2 failures are numbers quoted in `square_pinhole.md`, which I left unchanged.

**Proven symbolically (residual 0):**
- **a. Path length:** built from the 8 half-planes for all nine regions. Zone I (the eight gaps t₁,₂ ± τ all positive) is stated explicitly. Gives κp(U+L) beyond a side and max(pUₓ,qU_y)+max(pLₓ,qL_y) beyond a corner.
- **b. Effective area:** strip and corner integrals done with both orderings as explicit cases. The four-corner sum equals the §3.3 boxed closed form, and `simplify(A_ours − A_paper) == 0`. This last check is weak: the M&M 2020 expression in `crosscheck_tables.py` has the same algebraic shape as ours, and the PDF isn't available, so the transcription is still unchecked.
- **c. Limits:** θ → 0 gives the Paix form, and the θ² series of §3.7 is reproduced for the area and the widths.
- **d. Widths:** W_x, W_y and √2·W are confirmed. I transcribed AM2004 eqs. 22, 25 and 29 from the PDF. Eq. 22 matches term by term, and the only difference to eq. 25 is the −ΔL²sin²θ term.

**e. Numerics:** at 30 points (10 with t₁ ≠ t₂), the closed forms agree with `mpmath.quad` of the raw transmission and a half-maximum search to ≤ 4e-26. Against the ray trace they agree to 8e-4 (area), 1.2e-4 (side widths) and 1.1e-3 (diagonals). The diagonal figure is within the trace's own grid noise.

**Discrepancies (reported in `sympy_check.md`):**
1. "W⊥ − AM25 ≤ 0.003 mm" is wrong: at 30° it is 0.0063 mm for A (0.0085 mm at 35°). The §2 table's own values already show this.
2. The §3.7 area-expansion errors hold only at φ = 0; at φ = 45° A is 3.9 % low, not 3.2 %.
3. Two rounding or wording points: the width-expansion error is 0.0022 mm rather than "≤ 0.002", and "through M³" should include the 3Mm² term.

Files are in `derivation/`:
- sympy_check.py
- sympy_check.md
- sympy_check_output.txt
- sympy_check_results.json
