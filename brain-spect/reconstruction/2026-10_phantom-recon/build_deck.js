// Slides: brain SPECT phantom reconstruction (small Jaszczak), corrections and SRM voxel size.
// Plain format: white slides, title + content. node build_deck.js -> brain_spect_phantom_reconstruction.pptx
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const sizeOf = require("image-size");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "../../python/brain_phantom_recon/doc_2026-10-14");
const FIG = path.join(ROOT, "figures");
const EXT = path.join(__dirname, "extras");
const M = JSON.parse(fs.readFileSync(path.join(ROOT, "metrics.json"), "utf8"));
const CONV = JSON.parse(fs.readFileSync(path.join(ROOT, "convergence", "metrics.json"), "utf8"));
const X = JSON.parse(fs.readFileSync(path.join(EXT, "extras.json"), "utf8"));
const OUT = path.join(__dirname, "brain_spect_phantom_reconstruction.pptx");

const THEME = {
  name: "Plain", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "1A1A1A", lt1: "FFFFFF", dk2: "1A1A1A", lt2: "F2F2F2", accent1: "1F77B4", accent2: "FF7F0E", accent3: "2CA02C",
            accent4: "7F7F7F", accent5: "D62728", accent6: "9467BD", hlink: "1F77B4", folHlink: "7F7F7F" },
};
const HEX = THEME.colors;
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "Brain SPECT phantom reconstruction";
pres.author = "Fang Han";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "TITLE",
  background: { color: HEX.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.3, w: 11.7, h: 1.6, fontSize: 36, bold: true, color: C.text1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.1, w: 11.7, h: 1.4, fontSize: 18, color: C.accent4, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.5, 0.5, 0.5, 0.5],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 12.3, h: 0.8, fontSize: 28, bold: true, color: C.text1, valign: "middle", align: "left" }, text: "" } },
  ],
  slideNumber: { x: 12.4, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: HEX.accent4 },
});

// ---------- helpers ----------
const f2 = v => v.toFixed(2), f1 = v => v.toFixed(1);
const pct = v => (v < 0.01 ? (v * 100).toFixed(1) : Math.round(v * 100)) + " %";
const newSlide = () => pres.addSlide({ masterName: "CONTENT" });
function text(slide, runs, opts) {
  const bullet = opts.bullet !== false;
  const items = Array.isArray(runs) ? runs : [runs];
  const o = { ...opts }; delete o.bullet;
  slide.addText(items.map((t, i) => (typeof t === "string" ? { text: t, options: { bullet, breakLine: i < items.length - 1 } }
    : { text: t.text, options: { bullet, breakLine: i < items.length - 1, ...t.options } })),
    { isTextBox: true, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0.05, ...o });
}
function caption(slide, t, opts) { slide.addText(t, { isTextBox: true, fontSize: 11, color: C.accent4, margin: 0, ...opts }); }
function pic(slide, file, x, y, { w, h } = {}, name) {
  const d = sizeOf(fs.readFileSync(file)), a = d.width / d.height;
  if (w && !h) h = w / a; else if (h && !w) w = h * a;
  slide.addImage({ path: file, x, y, w, h, objectName: name || path.basename(file) });
  return { w, h };
}
const eq = (slide, name, x, y, h) => pic(slide, path.join(EXT, `${name}.png`), x, y, { h }, name);
const HEAD = { bold: true, color: HEX.dk1, fill: { color: HEX.lt2 }, fontSize: 13, valign: "middle" };
const cell = (t, o = {}) => ({ text: String(t), options: { fontSize: 13, color: HEX.dk1, valign: "middle", ...o } });
const table = (slide, rows, opts) => slide.addTable(rows, { border: { type: "solid", pt: 0.5, color: "BFBFBF" }, fill: { color: HEX.lt1 }, align: "center", ...opts });
const fwhm = (grp, lab, it, d) => X.sphere_fits[grp][lab][String(it)][d].fwhm_mm;

const s0 = M["2mm_step0_raw"].in_fov_total["400"], s1 = M["2mm_steps1-2_support_tew"].in_fov_total["400"];
const s2 = M["2mm_steps1-2_support_tew"].full_tew["400"], s3 = M["2mm_step3_ac"].full_tew["400"], si = M["2mm_step3_ac"].in_fov_primary["400"];

// 1. title
let s = pres.addSlide({ masterName: "TITLE" });
s.addText("Brain SPECT phantom reconstruction: corrections and SRM voxel size", { placeholder: "title" });
s.addText("Small Jaszczak, 15 mCi Tc-99m, 15 min, GATE 10 simulation · MLEM with the Gate system matrix (SRM) · October 2026", { placeholder: "body" });

// 2. summary
s = newSlide();
s.addText("Summary", { placeholder: "title" });
text(s, [
  { text: `With support restriction, TEW scatter correction and attenuation correction, the reconstructed activity is ${f2(s3.activity_over_truth)}× the true activity`, options: { bold: true } },
  `(${f2(s3.activity_over_truth)}× = mean reconstructed activity concentration in a uniform water region divided by the true concentration; 1.00 is perfect. Without attenuation correction it is ${f2(s2.activity_over_truth)}×.)`,
  `Without corrections, ${pct(s0.outside_fraction)} of the reconstructed activity ends up outside the phantom; with all corrections ${pct(s3.outside_fraction)}`,
  { text: "2, 1.5 and 1 mm SRMs give the same contrast and resolution at every iteration (1 to 2,000), even on data generated with the 1 mm SRM", options: { bold: true } },
  `Fitted image resolution (FWHM, 25.4 mm sphere, iteration 400): ${f1(fwhm("resolution", "2 mm", 400, "25.4"))} mm with the 2 mm SRM, ${f1(fwhm("resolution", "1 mm", 400, "25.4"))} mm with the 1 mm SRM`,
  "Recommendation: keep the 2 mm SRM (5.5× faster than 1 mm); spend effort on convergence instead",
], { x: 0.5, y: 1.3, w: 12.3, h: 5.6 });

// 3. setup
s = newSlide();
s.addText("Setup: one acquisition, SRMs at three voxel sizes", { placeholder: "title" });
pic(s, path.join(__dirname, "phantom_truth.png"), 0.5, 1.2, { w: 7.0 }, "phantom truth");
text(s, [
  "Scanner: 73 pinhole modules on 7 rings, 288 mm spherical FOV, 25 × 25 pixels of 2 mm per module",
  "Phantom: small Jaszczak, upside down, 25 mm below the FOV centre, 15 mCi Tc-99m in the water, 15 min",
  "Rods (cold PMMA): 4.8, 6.4, 7.9, 9.5, 11.1 and 12.7 mm",
  "Spheres (cold PMMA): 6.4, 9.5, 12.7, 15.9, 19.1 and 25.4 mm",
  "Counts 126.5–154.6 keV: 104 M recorded, 79 M after TEW, 80 M unscattered (simulation-only reference)",
], { x: 7.8, y: 1.2, w: 5.0, h: 3.4, fontSize: 14 });
table(s, [
  ["SRM grid", "Non-zero entries", "Files on disk (73 .npz)", "In memory (int32 + float16)", "Time per MLEM iteration"].map(h => cell(h, HEAD)),
  [cell("2 mm (144³ voxels)"), cell("1.43 × 10⁹"), cell("3.2 GB"), cell("8.6 GB, on the GPU"), cell("0.2 s")],
  [cell("1.5 mm (192³ voxels)"), cell("2.24 × 10⁹"), cell("5.0 GB"), cell("13 GB, streamed"), cell("0.43 s")],
  [cell("1 mm (288³ voxels)"), cell("4.61 × 10⁹"), cell("10 GB"), cell("28 GB, streamed"), cell("1.1 s")],
], { x: 0.5, y: 4.9, w: 12.3, colW: [2.6, 2.2, 2.4, 2.8, 2.3], rowH: 0.42 });
caption(s, "All three SRMs are binned from the same 1.0 × 10¹⁴ simulated 140 keV photons; one RTX 3080 Ti (12 GB)", { x: 0.5, y: 6.75, w: 12.3, h: 0.3 });

// 3b. insert map: exact and voxelised
s = newSlide();
s.addText("Insert sizes: exact geometry and on each reconstruction grid", { placeholder: "title" });
pic(s, path.join(EXT, "insert_map.png"), 0.5, 1.15, { h: 5.55 }, "insert map");
caption(s, "Cross-sections through the rod plane (z = 29 mm) and the sphere plane (z = \u221228 mm, through the sphere centres). A voxel is cold when its centre lies inside an insert; on the 2 mm grid the 4.8 mm rods are only a few voxels each", { x: 0.5, y: 6.75, w: 11.8, h: 0.5 });

// 4. sensitivity
const sp = X.sensitivity_profile;
const at = (key, r) => sp[key].reduce((best, q) => (Math.abs(q.r_mm - r) < Math.abs(best.r_mm - r) ? q : best));
s = newSlide();
s.addText("Sensitivity falls from the FOV centre to its edge, the same for all three grids", { placeholder: "title" });
pic(s, path.join(EXT, "sensitivity.png"), 0.5, 1.2, { w: 8.6 }, "sensitivity");
text(s, [
  "Sensitivity = SRM column sum: counts detected from each voxel, per mm³ of source (so the grids can be compared)",
  `2 mm SRM: ${Math.round(at("2mm", 2.5).mean)} counts/mm³ at the centre, ${Math.round(at("2mm", 67.5).mean)} at 70 mm (phantom edge), ${Math.round(at("2mm", 142.5).mean)} at the FOV edge`,
  "The three curves coincide: they come from the same photons, only binned differently",
  "Voxels below 1,000 counts (2 mm grid) are frozen in MLEM (support restriction)",
], { x: 9.3, y: 1.3, w: 3.6, h: 5.5, fontSize: 14 });

// 5. MLEM and the measures
s = newSlide();
s.addText("Reconstruction: MLEM with the SRM, and how the images are scored", { placeholder: "title" });
text(s, ["MLEM update (y = measured counts per detector pixel, H = SRM, λ = image):"], { x: 0.5, y: 1.2, w: 6.0, h: 0.5, bullet: false, fontSize: 15 });
eq(s, "eq_mlem", 0.7, 1.75, 1.0);
text(s, ["Cold contrast of an insert (1 = perfect, 0 = invisible):"], { x: 0.5, y: 3.0, w: 6.0, h: 0.5, bullet: false, fontSize: 15 });
eq(s, "eq_contrast", 0.7, 3.5, 0.85);
text(s, ["Quantitative accuracy (the “1.01×”):"], { x: 0.5, y: 4.6, w: 6.0, h: 0.5, bullet: false, fontSize: 15 });
eq(s, "eq_accuracy", 0.7, 5.1, 0.8);
text(s, [
  "Insert mask: voxels whose centre lies inside the rod or sphere (phantom model on the reconstruction grid)",
  "Background, sphere: water in a shell 4–12 mm outside the sphere surface, > 4 mm from any other insert",
  "Background, rods: water between the rods of that sector, > 2 mm from any rod, away from the plates",
  "Accuracy: mean in a uniform water region (z −80 to −60 mm, r < 50 mm); N = simulated decays (phantom) or photons (SRM), V = volumes; MLEM's λ is in units of SRM photons per voxel",
  "Noise: coefficient of variation (CoV) in that same uniform region",
], { x: 7.0, y: 1.2, w: 5.9, h: 5.7, fontSize: 14 });

// 6. TEW
s = newSlide();
s.addText("Scatter correction (TEW): estimate scatter from two side windows", { placeholder: "title" });
text(s, [
  "Photons that scatter in the phantom lose energy, and many still land in the 20 % main window, from the wrong direction",
  "Just below and above the main window there are mostly scattered photons; TEW counts them in two narrow windows (5.6 keV each) per detector pixel",
  "It assumes the scattered spectrum is a straight line under the main window: the trapezoid between the two side-window levels",
  "That estimate is subtracted from the main-window counts, pixel by pixel, and negative values are set to zero",
], { x: 0.5, y: 1.3, w: 12.3, h: 2.8 });
eq(s, "eq_tew", 0.8, 4.3, 0.95);
caption(s, "C = counts in a window, w = window width (keV): main 126.5–154.6, lower 120.8–126.5, upper 154.6–160.2; P = primary (unscattered) estimate used for the reconstruction", { x: 0.8, y: 5.45, w: 11.8, h: 0.5 });
text(s, ["Here TEW removes 24 % of the main-window counts (104 M → 79 M); the simulation-only count of unscattered photons is 80 M"], { x: 0.5, y: 6.1, w: 12.3, h: 0.6, fontSize: 15 });

// 7. AC
s = newSlide();
s.addText("Attenuation correction: the phantom's attenuation in the system matrix", { placeholder: "title" });
text(s, [
  "The SRM was simulated in air; in the phantom, photons from deep inside are absorbed or scattered away more than those near the surface",
  "For each voxel j and module m: the fraction of photons that survive the straight path from the voxel to the module's pinhole",
  "Every SRM row of that module is multiplied by it, so MLEM expects fewer counts from deep voxels and raises them accordingly",
  "The path integral uses the phantom's own geometry and materials (water, and the PMMA/nylon of walls, rods and spheres), traced with the gammart OptiX ray tracer: 73 × 1.6 M rays in 8 s",
], { x: 0.5, y: 1.3, w: 12.3, h: 2.9 });
eq(s, "eq_att", 0.8, 4.25, 0.95);
caption(s, "μ = linear attenuation at 140.5 keV (water 0.154 /cm, PMMA 0.177 /cm); r_j = voxel centre, p_m = pinhole centre, m(i) = module of detector pixel i", { x: 0.8, y: 5.3, w: 11.8, h: 0.4 });
text(s, ["Checks: transmissions agree with exact analytic path lengths to 0.0013; the attenuated SRM predicts the unscattered projections with correlation 0.9996 and per-module totals 0.995–1.020 (air SRM 0.79–1.10)"], { x: 0.5, y: 5.85, w: 12.3, h: 0.9, fontSize: 15 });

// 8. AC map and inserts
const cm = X.correction;
s = newSlide();
s.addText("The correction grows with depth; the PMMA inserts add about " + Math.round(cm.inserts_share_median_pct) + " %", { placeholder: "title" });
pic(s, path.join(EXT, "attenuation_correction_map.png"), 0.5, 1.2, { w: 12.3 }, "attenuation correction map");
text(s, [
  `Correction factor = air sensitivity / attenuated sensitivity: how much MLEM scales a voxel up. In the water: ${f1(cm.correction_water_min)}× at the wall, ${f1(cm.correction_centre)}× at the FOV centre, up to ${f1(cm.correction_water_max)}× at the lower centre of the phantom (furthest from the pinholes)`,
  `Yes, the cold inserts are in the attenuation model, as PMMA (μ 0.177 /cm vs 0.154 for water). Their share of the correction (vs an all-water phantom): up to ${f1(cm.inserts_share_max_pct)} %, median ${f1(cm.inserts_share_median_pct)} %`,
  "Attenuation depends only on the material along the path, not on activity: a cold insert attenuates like any other plastic; it is not treated as “empty”",
], { x: 0.5, y: 5.0, w: 12.3, h: 2.0, fontSize: 14 });

// 9-10. steps images
for (const [plane, title] of [["rods", "Rod plane: inserts appear by iteration 20; AC removes the bright rim"],
                              ["spheres", "Sphere plane: the four largest spheres are clear by iteration 100"]]) {
  s = newSlide();
  s.addText(title, { placeholder: "title" });
  pic(s, path.join(FIG, `steps_${plane}.png`), 0.5, 1.15, { h: 5.5 }, `steps ${plane}`);
  text(s, [
    "Rows: 0 no corrections; 1 + support; 2 + TEW; 3 + attenuation correction; ideal = unscattered data + AC",
    "Iterations 1–5: a smooth blob in every row (MLEM recovers coarse structure first); no insert above 0.2 contrast",
    `With AC the level is right early: ${f2(M["2mm_step3_ac"].full_tew["5"].activity_over_truth)}× the truth at iteration 5`,
  ], { x: 8.4, y: 1.2, w: 4.5, h: 5.4, fontSize: 14 });
  caption(s, `${plane === "rods" ? "Rod" : "Sphere"} plane, 6 mm slab average, 2 mm SRM; each panel scaled to its own water level`, { x: 0.5, y: 6.75, w: 7.8, h: 0.3 });
}

// 11. steps profiles
s = newSlide();
s.addText("Line profiles: AC flattens the profile; the inserts' dips keep their depth", { placeholder: "title" });
pic(s, path.join(EXT, "profiles_steps_it400.png"), 0.5, 1.15, { w: 9.2 }, "profiles steps");
text(s, [
  `Without AC the profile rises towards the wall (rim / centre ${f2(s2.rim_over_centre)}); with AC it is flat (${f2(s3.rim_over_centre)})`,
  "Each curve is normalised to its own median water value; grey = truth",
], { x: 9.9, y: 1.3, w: 3.0, h: 5.3, fontSize: 14 });
caption(s, "Iteration 400, 2 mm SRM; 6 mm slab average (rods: ±10 mm along the rods)", { x: 0.5, y: 6.1, w: 9.0, h: 0.3 });

// 12. steps table
s = newSlide();
s.addText("All three corrections together give a quantitative, uniform image", { placeholder: "title" });
const stepRows = [["0: no corrections", s0], ["1: + support", s1], ["2: + TEW", s2], ["3: + attenuation correction", s3], ["ideal: unscattered + AC", si]];
const fw = ["0: no corrections", "1: + support", "2: + TEW", "3: + AC", "ideal"];
table(s, [["Step (iteration 400)", "Activity outside phantom", "Accuracy", "Rim / centre", "Noise (CoV)", "Sphere 25.4 mm", "Sphere 12.7 mm", "Rods 9.5 mm", "Rods 7.9 mm", "FWHM (25.4 mm sphere)"].map(h => cell(h, HEAD)),
  ...stepRows.map(([lab, r], i) => [cell(lab, i === 3 ? { bold: true } : {}), cell(pct(r.outside_fraction)), cell(f2(r.activity_over_truth) + "×"), cell(f2(r.rim_over_centre)),
    cell(f2(r.cov_voxel)), cell(f2(r["sphere_25.4mm"])), cell(f2(r["sphere_12.7mm"])), cell(f2(r["rods_9.5mm"])), cell(f2(r["rods_7.9mm"])),
    cell(f1(X.sphere_fits.steps[fw[i]]["400"]["25.4"].fwhm_mm) + " mm")])],
  { x: 0.5, y: 1.3, w: 12.3, colW: [2.4, 1.2, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.1, 1.3], rowH: 0.5 });
text(s, [
  "Contrast columns: cold contrast (slide 6); activity outside phantom = share of the reconstructed total > 6 mm outside it",
  "Contrast without AC is higher at the same iteration: a model-mismatch effect. On identical noise-free data the air SRM gives the 25.4 mm sphere 0.89 and the attenuated SRM 0.79; the attenuated model converges more slowly",
], { x: 0.5, y: 4.8, w: 12.3, h: 2.0, fontSize: 14 });

// 13. MIP
s = newSlide();
s.addText("Activity outside the phantom: maximum-intensity projections", { placeholder: "title" });
pic(s, path.join(FIG, "outside_mip.png"), 0.5, 1.15, { h: 5.5 }, "outside mip");
text(s, [
  "Maximum-intensity projection (MIP): for each (x, y), the largest value along z through the whole 288 mm FOV, so a hot voxel anywhere shows up",
  "Grey scale stops at 1.4× the water level: the phantom saturates to white, and any bright spot outside it is spurious",
  `No corrections: isolated hot voxels at the FOV edge; ${pct(s0.outside_fraction)} of the activity outside the phantom at iteration 400`,
  `Support restriction removes them (${pct(s1.outside_fraction)} left)`,
  `Cones pointing at each pinhole persist until AC (${pct(s3.outside_fraction)} left): where the air model puts counts it cannot explain`,
], { x: 6.0, y: 1.2, w: 6.9, h: 5.6, fontSize: 14 });

// 14. resolution images
s = newSlide();
s.addText("SRM voxel size: 2, 1.5 and 1 mm give the same image at every iteration", { placeholder: "title" });
pic(s, path.join(FIG, "resolution_rods.png"), 0.5, 1.15, { w: 12.3 }, "resolution rods");
caption(s, "All corrections (TEW + AC), rod plane, 6 mm slab average; the 1 mm images look smoother, not sharper", { x: 0.5, y: 6.75, w: 12.3, h: 0.3 });

// 15. resolution profiles + FWHM
s = newSlide();
s.addText("Line profiles and fitted FWHM: no gain from finer voxels", { placeholder: "title" });
pic(s, path.join(EXT, "profiles_resolution_it400.png"), 0.5, 1.15, { w: 9.6 }, "profiles resolution");
caption(s, "FWHM, 25.4 mm sphere (fit below)", { x: 10.3, y: 1.25, w: 2.6, h: 0.3 });
table(s, [["Iteration", "2 mm", "1.5 mm", "1 mm"].map(h => cell(h, { ...HEAD, fontSize: 11 })),
  ...[100, 400].map(it => [cell(String(it), { fontSize: 11 }), ...["2 mm", "1.5 mm", "1 mm"].map(l => cell(f1(fwhm("resolution", l, it, "25.4")), { fontSize: 11 }))])],
  { x: 10.3, y: 1.6, w: 2.6, colW: [0.8, 0.6, 0.6, 0.6], rowH: 0.4 });
text(s, ["The rod dips and the sphere edges overlap for all three grids; the 6.4 mm rods give only shallow ripples with any grid",
  "FWHM from the 25.4 mm sphere; smaller spheres fit wider because their contrast has not converged yet"], { x: 10.3, y: 3.0, w: 2.6, h: 3.1, fontSize: 12, bullet: false });
eq(s, "eq_fit", 0.5, 6.2, 0.42);
caption(s, "Fit: sphere = ball of its true radius R, blurred by a 3D Gaussian of width σ; b = background, c = inside level; fitted to all voxels within R + 14 mm (lower half, water only)", { x: 0.5, y: 6.68, w: 9.6, h: 0.35 });

// 16. contrast chart (native)
s = newSlide();
s.addText("The 7.9 mm rods reach the same contrast with every SRM grid", { placeholder: "title" });
const ITS = ["1", "2", "3", "4", "5", "10", "20", "50", "100", "200", "400"];
const RES = [["2 mm", "2mm"], ["1.5 mm", "1p5mm"], ["1 mm", "1mm"]];
const chartOpts = title => ({
  showTitle: true, title, titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
  chartColors: [HEX.accent1, HEX.accent2, HEX.accent3], lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 5,
  showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
  catAxisTitle: "MLEM iteration", showCatAxisTitle: true, catAxisTitleFontSize: 12, catAxisTitleColor: HEX.accent4,
  valAxisTitle: "cold contrast (true 1)", showValAxisTitle: true, valAxisTitleFontSize: 12, valAxisTitleColor: HEX.accent4,
  valAxisMinVal: 0, valAxisMaxVal: 0.5, valAxisMajorUnit: 0.1, valAxisLabelFormatCode: "0.0",
  catAxisLabelColor: HEX.accent4, valAxisLabelColor: HEX.accent4, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
  catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", valGridLine: { color: "D9D9D9", size: 0.5 }, catGridLine: { style: "none" },
});
const series = (prefix, ds) => RES.map(([lab, tag]) => ({ name: `${lab} SRM`, labels: ITS, values: ITS.map(it => M[prefix ? prefix + tag : `${tag}_step3_ac`][ds][it]["rods_7.9mm"]) }));
s.addChart(pres.charts.LINE, series("", "full_tew"), { x: 0.5, y: 1.2, w: 6.0, h: 4.8, ...chartOpts("Simulated acquisition, TEW + AC"), objectName: "contrast measured" });
s.addChart(pres.charts.LINE, series("synthetic_noisefree_", "in_fov_primary"), { x: 6.8, y: 1.2, w: 6.0, h: 4.8, ...chartOpts("Noise-free data made with the 1 mm SRM"), objectName: "contrast noisefree" });
text(s, ["The three lines lie on top of each other, even when the data come from the 1 mm SRM itself (an “inverse crime” that favours 1 mm). Iterations on a category axis, not to scale"], { x: 0.5, y: 6.15, w: 12.3, h: 0.8, fontSize: 14, bullet: false });

// 17. is 1 mm needed table
s = newSlide();
s.addText("Even close to convergence, the 1 mm SRM does not pull ahead", { placeholder: "title" });
const nf = (lab, it) => X.sphere_fits.noisefree_2000[lab][String(it)]["25.4"].fwhm_mm;
const t1 = (r, fwhmVal) => [f2(r["rods_7.9mm"]), f2(r["rods_6.4mm"]), f2(r["rods_4.8mm"]), f2(r["sphere_9.5mm"]), f1(fwhmVal) + " mm"];
const rowsNeed = [
  ["Simulated acquisition, iteration 400", "2 mm", t1(M["2mm_step3_ac"].full_tew["400"], fwhm("resolution", "2 mm", 400, "25.4"))],
  ["", "1 mm", t1(M["1mm_step3_ac"].full_tew["400"], fwhm("resolution", "1 mm", 400, "25.4"))],
  ["Noise-free, made with 1 mm SRM, iteration 400", "2 mm", t1(M["synthetic_noisefree_2mm"].in_fov_primary["400"], fwhm("noisefree", "2 mm", 400, "25.4"))],
  ["", "1 mm", t1(M["synthetic_noisefree_1mm"].in_fov_primary["400"], fwhm("noisefree", "1 mm", 400, "25.4"))],
  ["Noise-free, made with 1 mm SRM, iteration 2,000", "2 mm", t1(CONV["2mm"]["2000"], nf("2 mm", 2000))],
  ["", "1 mm", t1(CONV["1mm"]["2000"], nf("1 mm", 2000))],
];
table(s, [["Data", "SRM", "Rods 7.9 mm", "Rods 6.4 mm", "Rods 4.8 mm", "Sphere 9.5 mm", "FWHM (25.4 mm sphere)"].map(h => cell(h, HEAD)),
  ...rowsNeed.map(([d, r, v]) => [cell(d, { bold: true, align: "left" }), cell(r), ...v.map(x => cell(x))])],
  { x: 0.5, y: 1.3, w: 12.3, colW: [4.3, 0.9, 1.35, 1.35, 1.35, 1.35, 1.7], rowH: 0.45 });
text(s, [
  "Noise-free data from the 1 mm SRM favour the 1 mm reconstruction (its model is exact by construction); a 10×-count Poisson version gives the same result",
  "At 2,000 iterations the 2 mm SRM is slightly ahead: the 1 mm problem has 8× more unknowns and converges more slowly",
], { x: 0.5, y: 4.7, w: 12.3, h: 2.0, fontSize: 14 });

// 18. why
s = newSlide();
s.addText("Why the grid does not matter for this scanner", { placeholder: "title" });
text(s, [
  `The system blurs more than the grid: fitted FWHM ${f1(fwhm("resolution", "2 mm", 400, "25.4"))}–${f1(fwhm("resolution", "1 mm", 400, "25.4"))} mm at iteration 400 (${f1(nf("2 mm", 2000))}–${f1(nf("1 mm", 2000))} mm at 2,000, noise-free) with every grid; a 2 mm grid already represents detail down to about 4 mm`,
  "MLEM is not converged: contrast still rises at iteration 400, and the noise-free and measured curves almost coincide, so iterations, not counts or voxels, limit the image",
  "A finer grid costs more and is noisier: 1 mm takes 5.5× the time per iteration and 28 GB instead of 8.6 GB, and each SRM entry comes from 8× fewer simulated photons",
  "Would change the answer: sharper system resolution (smaller pinholes, finer detector pixels) or tasks on structures of 4 mm or less",
], { x: 0.5, y: 1.3, w: 12.3, h: 5.5 });

// 19. caveats & next steps
s = newSlide();
s.addText("Caveats and next steps", { placeholder: "title" });
text(s, [
  { text: "Caveats", options: { bold: true, bullet: false } },
  "Simulation only: the SRM and the data share geometry and physics",
  "The μ map is the exact phantom; real data need a CT or a fitted outline",
  "One ray per voxel and module (pinhole centre); plain MLEM, no regularisation; cold inserts only",
  { text: "Next steps", options: { bold: true, bullet: false } },
  "Same pipeline on the corrected XCAT head data (running on Expanse); 42 % of its counts come from outside the FOV",
  "OSEM or another accelerated algorithm; a hot-sphere phantom for recovery coefficients",
], { x: 0.5, y: 1.3, w: 12.3, h: 5.5 });

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})();
