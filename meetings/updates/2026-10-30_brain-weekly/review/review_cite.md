**Verification of report.qmd and references.bib** (read-only; Crossref API for every DOI, plus web fetches of the Zannoni PMC text and the Feng arXiv PDF). I did not access the DB-SPECT abstract, the Metzler & Moore 2020 full text or the IEEE pages. Those items are marked "unverified" below.

## (a) Entries

| key | verdict |
|---|---|
| accorsi2004, metzler2002, metzler2005, metzler2020, johnson2016, moore2016, vanaudenhaege2015, zannoni2021, meng2004, meng2009, hutton2011 | **ok**: authors, title, journal, volume, pages and DOI all match Crossref |
| feng2022db | **ok**: title and DOI match, and `Hashemi, Amirreza` is right. The seed's "Hashemi M" is wrong. |
| feng2022dc | **fix**: published as Biomed. Phys. Eng. Express 10, 015009 (2024), doi 10.1088/2057-1976/ad0f40, same five authors. Cite the journal version; keep the arXiv ID in a note. |
| rentmeester2008 | **fix**: the real record is Goorden, Rentmeester & Beekman, 2008 IEEE NSS Conf. Rec., pp. 4036–4038, doi 10.1109/NSSMIC.2008.4774170. Goorden is first author. The "no DOI" note is obsolete. The full paper is Goorden, Rentmeester & Beekman, PMB 54(21):6593–6610 (2009), "Theoretical analysis of full-ring multi-pinhole brain SPECT". Prefer it. |

No entry needs dropping. The seed's items 24 (Feng title), 25 (DB-SPECT title) and 22 (Lai & Meng title) are now confirmed.

## (c) Claim-support problems

1. **Zannoni 2021.**
   - Confirmed in the PMC text:
     - 502 modules, 80×80 pixels of 250 µm, MF 1:12, and the 502×1 mm vs 168/167/167 lofthole mix.
     - Centre FWHM 20 mm vs 26 mm.
     - Smallest resolved hot rods 4 mm vs 6 mm.
     - The "specific combination…", "angular sampling… sparser", "lowest spatial resolution in this study" and "DOI capability indispensable" quotes.
   - **CNR 14.7/22.5 and CRC 35.5/36.2 %:** not in the body text, which refers to Figs 8C–D and 9C–D only. The report's table note says they are bar-chart labels. Keep that note, and keep the numbers out of the prose.
   - **"About 500 modules":** the paper says exactly 502.
   - **Uniform 1 mm beats the mix (line 43):** the sentence "The Meng group's helmet study found the same" is supported, but only on resolution, since the paper says the mix improves sensitivity. Add "at higher sensitivity for the mix", otherwise it reads as an equal-sensitivity comparison.
   - **Quote caveat:** my fetch truncated the "specific combination…" and conclusion quotes mid-sentence, so I did not independently confirm their endings. Spot-check the full sentences against the PDF.
2. **Feng 2022 DC-SPECT (line 322).**
   - **Supported:**
     - The PDF has "10 mm FWHM geometrical resolution (without resolution recovery)".
     - The 4.5 mm central resolution is stated.
     - The pinhole is 2.25 mm and the detector pixels are 2×2 mm on a 10 mm CsI:Tl.
     - The theoretical resolution is computed from d_eff, which is Anger-type (tungsten µ ≈ 2.5).
     - The paper states no factor.
   - **Overclaims:**
     - "The rule appears to come from…" is the authors' inference. State it as such.
     - The abstract says "10 mm" is for the *current design*, and the 4.5 mm is for a reconstruction of rods in a test phantom, not a measured point-source FWHM. Label it "reconstructed central resolution".
     - "Same quadrature formula" and "like for like" are asserted. The paper's formula text shows d_eff and 16b², and I did not see the detector term written out. The geometry is asymmetric (collimator length 87 mm, 253 mm to the FOV centre, ~42° acceptance), so say "similar" and not "like for like".
3. **Metzler & Moore 2020.**
   - The seed marks it [agent], not [full]. The equation numbers (22, 25) and "Eq. (22) equals §3.3 to machine precision" rest on an agent transcription. I could not check them.
   - The Paix w_s² = A_eff identity (line 514) holds only if tan(α/2) maps onto t/w as the seed's eq. 25 implies. Check against the PDF before keeping "exactly".
   - The paper gives no resolution formula, so the sentence "no closed-form FWHM… in the literature" is an absence claim. Soften it to "we found none".
4. **Accorsi & Metzler 2004.** Supported, [full], and §V is correctly paraphrased. Line 484, "reproduces eq. (22) identically, with d→w", is the report's own derivation. Attribute only the formula to AM2004, not the square-aperture result.
5. **Metzler 2002 (line 494).** The "RMS changes ×2, FWHM ×1.3" figure is the report's own calculation. The cite supports the RMS definitions and the isotropy remark only. Move it to follow "variance-based figures of merit", or mark the numbers as this report's.
6. **DB-SPECT (feng2022db).**
   - I could not retrieve the abstract. Crossref has none and the web search found nothing.
   - The claims "118 collimators", "four groups 0.5–2.0 mm", "contributed to recovered resolution" and "compared with a dual-head camera" are therefore **unverified**.
   - The seed marks the paper [abstract], so check the quoted phrase against IEEE Xplore.
7. **Rentmeester & Beekman.** "With detectors coarser than 1 mm the optimal geometry magnifies" is abstract-only and I could not check it. After the author fix it is a Goorden et al. claim.
8. **Meng 2004/2009 quotes.** These are [full] in the seed. I did not recheck the quotes.

## (b) BibTeX

```bibtex
@article{feng2024dc,
  author  = {Feng, Yuemeng and Worstell, William and Kupinski, Matthew and Furenlid, Lars R. and Sabet, Hamid},
  title   = {Resolution recovery on list mode {MLEM} reconstruction for dynamic cardiac {SPECT} system},
  journal = {Biomedical Physics \& Engineering Express},
  year    = {2024},
  volume  = {10},
  number  = {1},
  pages   = {015009},
  doi     = {10.1088/2057-1976/ad0f40},
  note    = {Preprint: arXiv:2212.14505}
}

@inproceedings{goorden2008,
  author    = {Goorden, M. C. and Rentmeester, M. C. M. and Beekman, F. J.},
  title     = {Theoretical analysis of multi-pinhole brain {SPECT}},
  booktitle = {2008 IEEE Nuclear Science Symposium Conference Record},
  year      = {2008},
  pages     = {4036--4038},
  doi       = {10.1109/NSSMIC.2008.4774170}
}

@article{goorden2009,
  author  = {Goorden, M. C. and Rentmeester, M. C. M. and Beekman, F. J.},
  title   = {Theoretical analysis of full-ring multi-pinhole brain {SPECT}},
  journal = {Physics in Medicine and Biology},
  year    = {2009},
  volume  = {54},
  number  = {21},
  pages   = {6593--6610},
  doi     = {10.1088/0031-9155/54/21/010}
}

@article{ogawa1991,
  author  = {Ogawa, K. and Harata, Y. and Ichihara, T. and Kubo, A. and Hashimoto, S.},
  title   = {A practical method for position-dependent {Compton}-scatter correction in single photon emission {CT}},
  journal = {IEEE Transactions on Medical Imaging},
  year    = {1991},
  volume  = {10},
  number  = {3},
  pages   = {408--412},
  doi     = {10.1109/42.97591}
}

@article{jan2004,
  author  = {Jan, S. and Santin, G. and Strul, D. and Staelens, S. and Assi{\'e}, K. and others},
  title   = {{GATE}: a simulation toolkit for {PET} and {SPECT}},
  journal = {Physics in Medicine and Biology},
  year    = {2004},
  volume  = {49},
  number  = {19},
  pages   = {4543--4561},
  doi     = {10.1088/0031-9155/49/19/007}
}

@article{sarrut2022,
  author  = {Sarrut, David and Arbor, Nicolas and Baudier, Thomas and Borys, Damian and Etxebeste, Ane and others},
  title   = {The {OpenGATE} ecosystem for {Monte Carlo} simulation in medical physics},
  journal = {Physics in Medicine and Biology},
  year    = {2022},
  volume  = {67},
  number  = {18},
  pages   = {184001},
  doi     = {10.1088/1361-6560/ac8c83}
}

@article{hudson1994,
  author  = {Hudson, H. M. and Larkin, R. S.},
  title   = {Accelerated image reconstruction using ordered subsets of projection data},
  journal = {IEEE Transactions on Medical Imaging},
  year    = {1994},
  volume  = {13},
  number  = {4},
  pages   = {601--609},
  doi     = {10.1109/42.363108}
}

@article{lai2018,
  author  = {Lai, Xiaochun and Meng, Ling-Jian},
  title   = {Simulation study of the second-generation {MR}-compatible {SPECT} system based on the inverted compound-eye gamma camera design},
  journal = {Physics in Medicine and Biology},
  year    = {2018},
  volume  = {63},
  number  = {4},
  pages   = {045008},
  doi     = {10.1088/1361-6560/aaa4fb}
}

@inproceedings{mandot2025,
  author    = {Mandot, S. and Zhu, S. and Metzler, S. D. and Meng, L.-J.},
  title     = {Preliminary Experimental Assessment of Hardware-Implemented Super-Resolution Sampling Strategies for a Dual-{FOV} Clinical Brain-{SPECT} Scanner},
  booktitle = {2025 IEEE Nuclear Science Symposium (NSS), Medical Imaging Conference (MIC) and Room Temperature Semiconductor Detector Conference (RTSD)},
  year      = {2025},
  pages     = {1--1},
  doi       = {10.1109/NSS/MIC/RTSD57106.2025.11286925}
}

@article{dewaraja2006,
  author  = {Dewaraja, Y. K. and Ljungberg, M. and Fessler, J. A.},
  title   = {3-{D} {Monte Carlo}-based scatter compensation in quantitative {I-131} {SPECT} reconstruction},
  journal = {IEEE Transactions on Nuclear Science},
  year    = {2006},
  volume  = {53},
  number  = {1},
  pages   = {181--188},
  doi     = {10.1109/TNS.2005.862956}
}

@inproceedings{sabet2012,
  author    = {Sabet, H. and Kudrolli, H. and Singh, B. and Nagarkar, V. V.},
  title     = {Fabricating high-resolution and high-sensitivity scintillator arrays using Laser Induced Optical Barriers},
  booktitle = {2012 IEEE Nuclear Science Symposium and Medical Imaging Conference Record (NSS/MIC)},
  year      = {2012},
  pages     = {4080--4084},
  doi       = {10.1109/NSSMIC.2012.6551932}
}

@misc{zhang2026,
  author        = {Zhang, Xi and Sitek, Arkadiusz and Blackberg, Lisa and Kupinski, Matthew and Furenlid, Lars and Sabet, Hamid},
  title         = {Maximum-Likelihood-Based Position Decoding of Laser Processed Converging Pixel {CsI:Tl} Detectors for High-Resolution {SPECT}},
  year          = {2026},
  eprint        = {2602.12298},
  archiveprefix = {arXiv}
}

@article{furenlid2004,
  author  = {Furenlid, L. R. and Wilson, D. W. and Chen, Y.-C. and Kim, H. and Pietraski, P. J. and others},
  title   = {{FastSPECT II}: a second-generation high-resolution dynamic {SPECT} imager},
  journal = {IEEE Transactions on Nuclear Science},
  year    = {2004},
  volume  = {51},
  number  = {3},
  pages   = {631--635},
  doi     = {10.1109/TNS.2004.830975}
}
```

Notes on the BibTeX:
- **Crossref abbreviations:** I abbreviated the long author lists with "others" for Jan, Sarrut and Furenlid, because Crossref returned only the first five authors in my printout. Expand them if the style needs full lists.
- **Hutton 2011:** the existing hutton2011 entry is already correct.
- **Dewaraja 2006:** I did not independently verify the I-131 title beyond Crossref, which matches.
- **Lai & Meng 2018:** the Crossref title matches the seed exactly. Per CLAUDE.md, the report only cites it if the text mentions the MR-compatible system.

## Restoring the dropped references
- Cite **ogawa1991** where the report mentions TEW scatter correction.
- Cite **jan2004** and **sarrut2022** at the first mention of GATE and opengate.
- Cite **hudson1994** at OSEM.
- Cite **dewaraja2006** for Monte Carlo scatter compensation.
- Cite **lai2018** and **mandot2025** wherever the Meng group's helmet and dual-FOV work is discussed.
- **Suggested additions:** `sabet2012` (the LIOB method) and `zhang2026` (converging-pixel CsI:Tl) fit where the detector-term floor and converging pixels are discussed. For classic multi-pinhole brain SPECT, use `goorden2009` (brain-specific, replaces rentmeester2008) and `furenlid2004` (FastSPECT II, a fixed dynamic imager).
- **Existence check:** all four exist per Crossref and arXiv. The zhang2026 preprint is dated Feb 2026 and its metadata was visible only through arXiv.
