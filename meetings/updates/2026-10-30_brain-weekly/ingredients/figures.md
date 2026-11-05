# Figure plan

Paths are relative to `~/Work/RPIL/QMIRT/`.

## A. Verified existing figures (copy into img/ if they read well; otherwise regenerate from the same data)

| topic | file | notes |
|---|---|---|
| WP0 spectra, ±1σ bands + ratio | pytorch-optix/out/wp0/spectra_t2.png | 4 GATE variants vs gammart |
| WP1 checkpoint | pytorch-optix/out/wp1/wp1_checkpoint.png, wp1_spot_fwhm.png | converging vs parallel FWHM |
| WP3 GATE vs gammart per phantom | pytorch-optix/out/wp3/wp3_{jaszczak,derenzo,triple}.png | recon comparisons |
| Classic terms vs distance b | qmirt-gate-10-sim/dev/reports/2026-10-28_analytic_resolution/img/terms_vs_b.png | |
| Information vs frequency | .../2026-10-28_analytic_resolution/img/information_vs_frequency.png | analytic models only (say so) |
| Phase 0 sensitivity/width | .../2026-10-28_analytic_resolution/img/phase0_sens_width.png | |
| Square pinhole PSF | .../2026-10-28_analytic_resolution/derivation/img/psf_C.png | |
| LIR noise explanation | qmirt-gate-10-sim/dev/reports/2026-10-28_brain_update/img/ideal_lir_profile.png | GATE noisy vs gammart noiseless vs gammart + noise |
| Scorecard XCAT/Derenzo | .../2026-10-28_brain_update/img/scorecard_derenzo.png, scorecard_xcat.png, scorecard_images.png | design comparison |
| WP2b map variation | .../2026-10-28_brain_update/img/wp2b_maps.png | |
| Resolution measures | .../2026-10-28_brain_update/img/resolution_measures.png | "seven ways to say resolution" |

## B. New figures to generate in scripts/make_figures.py (from data)
1. **WP4 reconstructed slices** (key figure), 2-row × 4-column panels per phantom:
   - columns: no correction (`air`), `ac_k`, `ac_k_tew`, reference (`ac_k` on `gammart_primary`);
   - rows: GATE fluorescence on (`gate_on`) and gammart;
   - 64 iterations;
   - Derenzo slice through the rod section (z where the metrics average: see `pytorch-optix/examples/wp3_metrics.py` `derenzo_metrics`, `phantoms.npz` `derenzo_z`); Jaszczak one slice through the rods (z ≈ 30 mm) and one through the spheres (z ≈ −28 mm); triple line, a slice at z = 0;
   - same colour scale per row (normalise each image to its own uniform or background mean); scale bar.
   - Files: `pytorch-optix/out/wp4/recon/<ph>_<step>_<dataset>_it64.npy`, 144³ float32, voxel 2 mm, index (i, j, k) = (x, y, z), centre (71.5, 71.5, 71.5).
2. **Jaszczak uniform-section radial profile:**
   - mean over z −90..−50 mm in 5 mm rings out to r = 60 mm, normalised to the r < 60 mean;
   - steps `air`, `ac`, `ac_k_tew` (gate_on) plus the reference;
   - shows cupping removed.
3. **Ladder bar or dot chart:**
   - Derenzo V/P (5, 6, 7 mm) and Jaszczak sphere/rod contrast per ladder step, at 128 iterations;
   - GATE and gammart, with the split SD as error bars;
   - data `pytorch-optix/out/wp4/wp4_results.json` (keys `<phantom>` → `it128` → `<step>/<dataset>` → metric → value; `<step>/split_sd`).
   - Run `micromamba run -n raytracing python pytorch-optix/examples/wp4_analysis.py --iterations 32 128` first if it128 is missing.
4. **Scatter composition and TEW:**
   - the blurred energy spectra per class from `pytorch-optix/out/wp4/truth/<ph>.npz` (key `spec`, shape (3 classes, 73, 200), 1 keV bins), summed over modules, with the main and TEW windows shaded;
   - this shows why the upper window holds no scatter.
5. **Kernel coverage before and after:**
   - per-pixel first-interaction counts (25 × 25) of the old kernel source (`pytorch-optix/out/wp2/mc_sphere_water.npz`) and the new one (`pytorch-optix/out/wp4/kernel_sphere140.npz`);
   - use `pytorch-optix/examples/wp2_kernel.kernel(d, v)` → (T, N), N[:625].reshape(25, 25); variant 0.

## C. Schematics to draw (matplotlib, clean vector-like style, or Typst cetz)
1. Converging-pixel side view with the edge strip (geometry in `facts.md`; pinhole at the top, entrance 25 mm, exit 35 mm).
2. Forward-model block diagram: x → A (attenuation) → H (first interaction) → K (Compton centroid) → + s (scatter) → ybar; label the files and modules.
3. Pinhole resolution geometry: point at b, pinhole, detector at f; aperture term d(b+f)/f and detector term p b/f; minification f/b = 0.18.
4. Box ⊗ box vs Gaussian quadrature (1-D profiles): aperture box 9.20 mm and pixel box 11.08 mm, their convolution (FWHM 11.1 mm) vs the Gaussian quadrature 14.4 mm.
5. Optional: the "information adds" illustration (the 28 Oct deck has `info_adds.png`, with invented widths; label it so).
