# Reference seed list (verification level in bold: full / agent = full text read; abstract / citation / web = not read in full)

Items marked "verify" must be checked (title, authors) before they go into references.bib; drop any that cannot be confirmed.

## 4. Literature on square / rectangular pinholes

Search: Undermind (workspace "GPU Monte Carlo & System Response Matrix", semantic + metadata lookup) and web.
Status: **[full]** = read in full by me from the PDF; **[agent]** = full text read by the Undermind PDF agent on
my questions, with the equations transcribed and, where stated, re-verified here; **[abstract]** = abstract or
citation only.

1. Accorsi R, Metzler SD. Analytic determination of the resolution-equivalent effective diameter of a pinhole
   collimator. *IEEE Trans Med Imaging* 2004;23(6):750–763. doi:10.1109/TMI.2004.826951. **[full]** Source of
   $d_{re}$, eqs. (22), (25), (29); round knife edge only, but §V says the method "can be immediately applied to
   other pinhole edge shapes, provided that the appropriate formula for $\Delta L$ is used", which is what §3 does.
2. Metzler SD, Bowsher JE, Greer KL, Jaszczak RJ. Analytic determination of the pinhole collimator's point-spread
   function and RMS resolution with penetration. *IEEE Trans Med Imaging* 2002;21(8):878–887.
   doi:10.1109/TMI.2002.803129. **[full]** PRF with penetration (eq. 6), RMS definitions (7)–(8), limits (25)–(29).
   Notes (p. 886) that any aperture shape gives a geometric PRF of the same shape, and that the AR is angle dependent.
3. Metzler SD, Accorsi R. Resolution- versus sensitivity-effective diameter in pinhole collimation: experimental
   verification. *Phys Med Biol* 2005;50(21):5005–5017. doi:10.1088/0031-9155/50/21/004. **[full]** Confirms
   $d_{re}$ (eqs. 5–6) against measured FWHM for 57Co and 131I, 1 and 3 mm apertures; Paix overestimates, Anger
   better but $\theta$-independent; appendix A.1–A.3 gives the $\theta$-dependent Paix/Anger forms.
4. Metzler SD, Moore SC. Analytic determination of rectangular-pinhole sensitivity with penetration. *IEEE Trans
   Med Imaging* 2020;39(4):833–843. doi:10.1109/TMI.2019.2936187. **[agent]** The direct reference for our
   geometry: rectangular aperture, eight half-planes (double-sided, no channel), acceptance angles $\alpha_x$,
   $\alpha_y$, source at $h(\tan\theta_x, \tan\theta_y, 1)$. Eq. (12) sensitivity integral, eq. (22) closed form,
   eq. (25) normal incidence $A_{eff} = w_xw_y + \frac{w_x}{\mu}\tan\frac{\alpha_y}{2} + \frac{w_y}{\mu}\tan\frac{\alpha_x}{2}
   + \frac{2}{\mu^2}\tan\frac{\alpha_x}{2}\tan\frac{\alpha_y}{2}$, eqs. (26)–(29) penumbra tapering near the FOV
   edge; validated to 0.16 % (normal) and 0.29 % ($\theta_x = \theta_y = 27°$) against numerical integration for
   $\mu = 4$ mm$^{-1}$, $w = 1$ mm. No resolution formula. Eq. (22) equals §3.3 to machine precision.
5. Metzler SD, Xia D, Moore SC. Analytic determination of rectangular-pinhole sensitivity with penetration.
   *2014 IEEE NSS/MIC Conf. Rec.*, pp. 1–5. doi:10.1109/NSSMIC.2014.7431000. **[abstract]** Conference version of 4
   (aligned-plane paths only).
6. Johnson LC, Moore SC, Metzler SD. Effect of pinhole shape on projection resolution. *Phys Med Biol*
   2016;61(5):2003–2013. doi:10.1088/0031-9155/61/5/2003. **[agent]** Square vs rounded-square vs circular
   apertures, 0.3/0.5/1 mm, $\alpha = 10$–$50°$, tungsten $\mu = 3.64$ mm$^{-1}$; resolution by ray-traced
   projections (geometric mean of LSF FWHM over 0–45°), sensitivity by numerical path sums with penetration.
   Perfect square gives the best FWHM at matched sensitivity and FOV (0.364 vs 0.414 mm, 0.3 mm, 10°); FWTM barely
   changes. No closed-form resolution formula; no side/diagonal statement.
7. Xia D, Moore SC, Park M-A, Cervo M, Metzler SD. Investigation of imaging properties for submillimeter
   rectangular pinholes. *Med Phys* 2015;42(12):6933–6944. doi:10.1118/1.4935200. **[agent]** 18 Pt/Ir inserts
   with 0.33 mm square apertures; sensitivity fitted as $A\sin^q\theta/(4\pi h^2)$ with effective edge
   $w_e = \sqrt A = 0.38 \pm 0.02$ mm and $q = 10.8 \pm 1.8$ (MC: $q = 7.7$); penumbra FOV formula (eqs. 8–10). No
   $\mu$-explicit sensitivity or resolution formula.
8. Xia D, Park M-A, Moore SC, Metzler SD. Preliminary investigation of imaging properties for sub-millimeter
   square pinholes. *2013 IEEE NSS/MIC*. doi:10.1109/NSSMIC.2013.6829173. **[abstract]**
9. Moore SC, Park M-A, Liu Z, Lyon MC, Johnson LC, Lushear VH, Westberg JG, Metzler SD. Design of a dual-resolution
   collimator for preclinical cardiac SPECT with a stationary triple-detector system. *Med Phys*
   2016;43(12):6336–6346. doi:10.1118/1.4966697. **[agent]** 87 Pt/Ir 0.3 mm square pinholes
   ($\mu = 4.56$ mm$^{-1}$, half-angles 17.1°/14.9°). Uses, for the square side, exactly our pair of equations:
   eq. (2) $d_{eff} = d + \ln 2\tan\alpha/\mu$ ($\alpha$ the half-opening angle in the direction considered),
   eq. (1) $res_{pin} = d_{eff}(M+1)/M$, eq. (3) $res_{sys} \approx \sqrt{res_{pin}^2 + (res_{int}/M)^2}$. No
   square/round equivalence stated.
10. Deprez K, Pato LRV, Vandenberghe S, Van Holen R. Characterization of a SPECT pinhole collimator for optimal
    detector usage (the lofthole). *Phys Med Biol* 2013;58(4):859–885. doi:10.1088/0031-9155/58/4/859.
    **[abstract]** (PDF not retrievable.) The lofthole is a *round* aperture with rectangular entrance/exit
    windows, so its projections tile a detector; it is not a square knife edge and its formulas exclude penetration.
    Not applicable here beyond the tiling argument.
11. Van Audenhaege K, Van Holen R, Vandenberghe S, Vanhove C, Metzler SD, Moore SC. Review of SPECT collimator
    selection, optimization, and fabrication for clinical and preclinical imaging. *Med Phys*
    2015;42(8):4796–4813. doi:10.1118/1.4927061. **[agent]** Eqs. (8)–(14) restate Paix (9), AM2004 (12)–(14) and
    the quadrature system resolution (10) with $m = f/h$; $\mu_W = 3.6$ mm$^{-1}$ at 140.5 keV. Nothing specific to
    square pinholes.
12. Metzler SD, Bowsher JE, Smith MF, Jaszczak RJ. Analytic determination of pinhole collimator sensitivity with
    penetration. *IEEE Trans Med Imaging* 2001;20(8):730–741. doi:10.1109/42.938241. **[abstract]** Round
    knife-edge angular sensitivity; its result is reproduced as M&A 2005 eq. (A.1) (read in full) and used in §3.4.
13. Smith MF, Jaszczak RJ. The effect of gamma ray penetration on angle-dependent sensitivity for pinhole
    collimation in nuclear medicine. *Med Phys* 1997;24(11):1701–1709. doi:10.1118/1.597957. **[abstract]**
    Derivation of Anger's $d_e$ from a parallel-beam sensitivity argument (AM2004 §I).
14. Paix D. Pinhole imaging of gamma rays. *Phys Med Biol* 1967;12(4):489–500. doi:10.1088/0031-9155/12/4/004.
    **[abstract]** Eq. (5) of AM2004.
15. Anger HO. Radioisotope cameras. In: Hine GJ (ed.), *Instrumentation in Nuclear Medicine*, vol. 1, Academic
    Press, 1967, pp. 485–552. **[citation]** Eqs. (2)–(3), (6)–(7) of AM2004.
16. Mallard JR, Myers MJ. The performance of a gamma camera for the visualization of radioactive isotopes in
    vivo. *Phys Med Biol* 1963;8:165–182. **[citation]** Eq. (1) of AM2004, the $\sin^3\theta_{AM}/(16h^2)$ law.
17. Tenney CR, Tornai MP, Smith MF, Turkington TG, Jaszczak RJ. Uranium pinhole collimators for 511-keV photon
    SPECT imaging of small volumes. *IEEE Trans Nucl Sci* 2001;48(4):1483–1489. doi:10.1109/23.958384.
    **[abstract]** Round pinholes, high energy; not used.
18. Bal G, Acton PD. Analytical derivation of the point spread function for pinhole collimators. *Phys Med Biol*
    2006;51(19):4923–4950. doi:10.1088/0031-9155/51/19/013. **[abstract]** Round apertures; not used.

No paper gives a closed-form *resolution* (FWHM) formula for a square knife edge with penetration; the Metzler
group applies the AM2004 normal-incidence formula to the side length (ref. 9) and otherwise ray-traces (ref. 6).
§3.2 supplies the oblique-incidence forms and shows the parallel one coincides with AM2004 eq. (22).


## Additional references (from lit_notes_meng_sabet_resolution.md, lit_notes_scatter.md and the 28 Oct work)

19. Zannoni EM, Yang C, Meng LJ. Design study of an ultrahigh resolution brain SPECT system using a synthetic compound-eye camera design with micro-slit and micro-ring apertures. *IEEE Trans Med Imaging* 2021;40(12):3711–3727. doi:10.1109/TMI.2021.3096920. **[full]**
20. Meng LJ, Clinthorne NH. A modified uniform Cramer–Rao bound for multiple pinhole aperture design. *IEEE Trans Med Imaging* 2004;23(7):896–902. doi:10.1109/TMI.2004.828356. **[full]**
21. Meng LJ, Li N. A vector uniform Cramer–Rao bound for SPECT system design. *IEEE Trans Nucl Sci* 2009;56(1):81–90. doi:10.1109/TNS.2008.2006609. **[full]**
22. Lai X, Meng LJ. Simulation study of the second-generation MR-compatible SPECT system based on the inverted compound-eye gamma camera design. *Phys Med Biol* 2018;63(4):045008. doi:10.1088/1361-6560/aaa4fb. **[full]** (verify title)
23. Rentmeester MCM, Beekman FJ. Theoretical analysis of multi-pinhole brain SPECT. 2008 (no DOI found; Semantic Scholar dd7d890e9538749bf752092c05531d64bd17f071). **[abstract]**
24. Feng Y, Worstell WA, Kupinski MA, Furenlid LR, Sabet H. Resolution-recovery-embedded image reconstruction for a high-resolution animal SPECT system / DC-SPECT (check exact title). arXiv:2212.14505, 2022. **[full]**
25. Feng Y, Hashemi M, Soleymani S, Ottensmeyer M, Sabet H. DB-SPECT mixed collimator, IEEE NSS/MIC 2022. doi:10.1109/NSS/MIC44845.2022.10399152. **[abstract]** (verify title)
26. Mandot S et al. Dual-FOV brain SPECT, IEEE NSS/MIC 2025. doi:10.1109/nss/mic/rtsd57106.2025.11286925. **[abstract]** (verify authors and title)
27. Vastenhouw B, Beekman FJ. Submillimeter total-body murine imaging with U-SPECT-I. *J Nucl Med* 2007;48(3):487–493 — or the IEEE TMI 2007 calibration paper; **[web snippet, unverified]**: verify before citing, or omit.
28. Goulet RT, Joy MLG. (pinhole LSF measurement vs Anger prediction). *Med Phys* 1980;7:571. **[citation only]** (verify title)
29. Hutton BF, Buvat I, Beekman FJ. Review and current status of SPECT scatter correction. *Phys Med Biol* 2011;56(14):R85–R112. doi:10.1088/0031-9155/56/14/R01. **[citation]**
30. Ogawa K, Harata Y, Ichihara T, Kubo A, Hashimoto S. A practical method for position-dependent Compton-scatter correction in single photon emission CT. *IEEE Trans Med Imaging* 1991;10(3):408–412. doi:10.1109/42.97591. **[citation]** (TEW original)
31. Dewaraja YK, Ljungberg M, Fessler JA. 3-D Monte Carlo-based scatter compensation in quantitative I-131 SPECT reconstruction. *IEEE Trans Nucl Sci* 2006;53(1):181–188. doi:10.1109/TNS.2005.862956. **[web pdf]**
32. Jan S et al. GATE: a simulation toolkit for PET and SPECT. *Phys Med Biol* 2004;49(19):4543–4561. doi:10.1088/0031-9155/49/19/007. **[citation]** (cite for GATE; GATE 10 / opengate: Sarrut D et al. 2022 Phys Med Biol 67(18):184001 doi:10.1088/1361-6560/ac8c83)
33. Hudson HM, Larkin RS. Accelerated image reconstruction using ordered subsets of projection data. *IEEE Trans Med Imaging* 1994;13(4):601–609. doi:10.1109/42.363108. **[citation]**
34. Barrett HH, Wilson DW, Tsui BMW. Noise properties of the EM algorithm: I. Theory. *Phys Med Biol* 1994;39(5):833–846. doi:10.1088/0031-9155/39/5/004. **[citation]** (LIR context)
35. Fessler JA, Rogers WL. Spatial resolution properties of penalized-likelihood image reconstruction: space-invariant tomographs. *IEEE Trans Image Process* 1996;5(9):1346–1358. doi:10.1109/83.535846. **[citation]**
