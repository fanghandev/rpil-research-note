# Scatter correction for Tc-99m pinhole SPECT: literature review

**Caveats.** Everything below comes from search-result abstracts and snippets. I did not read any full text. I did not retrieve DOIs, so I give journal and volume details only. Items marked *(memory)* are from my own recall and not from these searches. The searches found no study of brain or head phantoms in pinhole SPECT, and none that tests a 3% lower or 7% upper TEW window at 12% FWHM.

## 1. Methods and quantitative findings

- **TEW with pinhole Tc-99m (abstract only).** In a U-SPECT-II multi-pinhole study, window-based scatter correction plus Chang attenuation correction (body outline from optical images) cut mean phantom quantification error from −18.7% to −1.7%. In a rat, errors fell from −23.6…−9.3% to −6.3…+4.3% (mean magnitude 2.1%). The search result did not give authors, year or journal.
- **Modified/iterative TEW (Med Phys 2016, dual-isotope small-animal SPECT; abstract only).** Uncorrected data overestimated Tc-99m activity by up to 80%. Standard TEW underestimated it by 13%, because unscattered photons leak into the side windows. Iterative, projection-space TEW correction brought it within 5%. The search did not give the authors.
- **Hutton, Buvat & Beekman, "Review and current status of SPECT scatter correction," Phys Med Biol 56(14):R85–R112, 2011.** The search returned only the citation, not the content. Cite it as the standard review.
- **Monte Carlo scatter as an additive term.**
  - Dewaraja, Ljungberg & Fessler (I-131, 3-D MC scatter in OSEM) found MC superior to TEW in accuracy and noise, but not by a large margin. A suitably scaled TEW closed much of the gap. They started with TEW and updated with MC after a few iterations. Two MC updates matched the true scatter.
  - Beekman et al. used an MC simulator as the projector for Tc-99m. They reported better results than an analytical scatter model.
  - A Tc-99m comparison reported TEW maximum error of −30% in a chest phantom and the worst SNR of the three methods tested. DEW-type methods were most accurate in that study. I did not get its citation.
- **Deep learning.** Xiang et al. (Y-90, a CNN mapping emission and attenuation projections to MC scatter) has the closest architecture, but it is not Tc-99m. The Tc-99m deep-learning work I found is image-domain (sestamibi, MAA). I found no Tc-99m pinhole scatter CNN. Cite DL as future work only.
- **GATE/SIMIND forward modeling.** Saikouk et al. (2022) used GATE to tune TEW sub-windows for Tc-99m.

## 2. TEW windows at about 12% FWHM

- Saikouk et al. (GATE, 2022; 15% main window) found good agreement with true scatter for sub-windows of about 5–7%. They warned that poor width or number choices add noise.
- A 1997 simulation study found the optimal main-window width depends on energy resolution. It gave 20% for a gamma camera and about 9.8% for a semiconductor detector with 7 keV resolution.
- **Known biases.**
  - The lower window contains photopeak tail. At 12% FWHM (about 17 keV) a window just below a 20% main window (about 126–154 keV) sits about 1.5–2σ from the peak. That tail inflates the scatter estimate and causes over-correction.
  - The upper window at 140 keV holds essentially no scatter, only photopeak tail and noise. Many authors therefore use a lower window only (TDW/DEW) or set the upper count to 0.
  - Fixes in the literature:
    - Subtract the primary-leakage fraction using the measured energy response (the modified/iterative TEW above).
    - Apply a scale factor (Dewaraja).
    - Low-pass filter the estimate. An MD Anderson paper (authors/year not retrieved) found filtering reduced error substantially.
- For your system, the cleanest fix is to calibrate the primary-in-side-window fraction from your own MC primary-only energy spectrum.

## 3. Subtract versus additive

- **Recommended: additive term in the Poisson model**, y ~ Poisson(Ax + s). This keeps the data non-negative, preserves Poisson statistics (subtraction does not), and avoids clipping bias. An MD Anderson abstract reported that feeding the TEW estimate directly into OS-ML gave lower error than pre-subtraction. Dewaraja et al. and a CZT cardiac study also used the additive form.
- Smooth the scatter estimate before using it. A noisy additive term still biases the reconstruction.
- I found no direct source on negative counts after subtraction, so that argument rests on the statistical model, not a citation.

## 4. Scatter fractions

- **Inveon pinhole, GATE, IEEE TNS 59(5):1887–1891, 2012 (abstract only).** Tc-99m SF was about 4–10% for MOBY mice and about 10–15% for NEMA rat phantoms. The authors concluded that emission-only energy-window methods suffice for mice and most rats.
- Chen et al., Mol Imaging Biol 2008: in mouse-sized phantoms, attenuation alone gave −18% error and including scatter gave −12% (abstract only).
- A GATE CsI(Tl) camera validation (arXiv physics/0411236): for a point source behind 0, 4 and 10 cm of water, simulated SF was within 2% of measurement. This is a camera, not a pinhole.
- **Gap.** The mouse and rat fractions do not transfer to a head, because scatter grows with phantom size. I found no brain-sized pinhole SF. My rough expectation for a 15–16 cm head phantom is 25–35% in a 20% window for a parallel-hole system. Pinhole and small-FOV geometry will differ, so you should measure SF from your own simulation.

## 5. Likely reviewer expectations *(general judgment, not from search results)*

- State clearly whether scatter is simulated, and in which energy window.
- Show an SF figure or table, with and without a scatter model, for your phantom.
- Show that the conclusions (resolution, sensitivity, contrast) survive realistic scatter.
- Report the quantitative bias of the method you use.
- Reviewers rarely require a new scatter method in a design paper, but they do object to ignoring scatter in a brain-sized object.

## Recommendation for your design paper

Your reconstruction uses a first-interaction matrix with attenuation and a crystal Compton kernel, which models primary photons only. I suggest the following:

1. **Main results.** Score the photopeak window (about 20% at 12% FWHM). Include phantom scatter and crystal scatter in the simulation. Reconstruct with a smoothed additive scatter term, y ~ Poisson(Ax + s).
2. **Estimate for s.** Use a lower-window-only or TEW estimate, with the primary-tail fraction calibrated from your own MC primary-only spectra. Use sub-windows of about 5–7% (Saikouk) and filter the estimate.
3. **Ground truth.** In simulation you can tag scattered photons. Report the true SF, and show the TEW estimate against the true scatter. This validates the method without needing a new technique.
4. **Ablation.** Compare no correction, additive TEW and oracle (true) scatter. Report activity bias and contrast recovery, so reviewers see the residual error.
5. **Deep learning and full MC scatter in OSEM.** Cite as future work (Dewaraja, Beekman, Xiang).

Sources:
- [U-SPECT-II / small-animal attenuation study (PMC3693101)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3693101/)
- [Dewaraja et al., 3-D MC scatter in I-131 SPECT](https://web.eecs.umich.edu/~fessler/papers/lists/files/jour/06/web/dewaraja-06-3dm.pdf)
- [Monte Carlo and experimental evaluation of two scatter correction methods](https://research.utu.fi/converis/portal/detail/Publication/36107548?lang=en_US)
- [Xiang et al., deep scatter estimation (Y-90)](https://web.eecs.umich.edu/~fessler/papers/lists/files/jour/20/xiang-20-adn.pdf)
- [Saikouk et al. GATE TEW sub-window study](https://research.utu.fi/converis/portal/detail/Publication/36276550?lang=en_US)
- [MD Anderson, filtering of TEW estimates](https://mdanderson.elsevierpure.com/en/publications/an-investigation-of-the-filtering-of-tew-scatter-estimates-used-t)
- [GATE CsI(Tl) camera validation](https://arxiv.org/pdf/physics/0411236)
- [Assessment of sources of error in small-animal SPECT (Chen et al.)](https://aemqa.stanfordhealthcare.org/publications/771/771528.html)
- [Evaluation of scatter corrections for bone SPECT/CT (PMC9170091)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9170091/)
