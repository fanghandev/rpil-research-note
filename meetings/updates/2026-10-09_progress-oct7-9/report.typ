// Progress report, brain SPECT simulation, Oct 7-9 2026.
// Build: typst compile dev/reports/2026-10-09_progress_oct7-9/report.typ
// Clearance figures: python dev/reports/2026-10-09_progress_oct7-9/make_clearance_figures.py (opengate env)

#set document(title: "Brain SPECT simulation: progress, Oct 7–9, 2026", author: "Fang Han")
#set page(paper: "us-letter", margin: (x: 2.2cm, y: 2.2cm), numbering: "1 / 1",
  header: context if counter(page).get().first() > 1 [
    #set text(8.5pt, fill: luma(110))
    Brain SPECT simulation: progress, Oct 7–9, 2026 #h(1fr) Fang Han
  ])
#set text(font: "Libertinus Serif", size: 10.5pt, lang: "en")
#set par(justify: false, leading: 0.62em, spacing: 0.9em)
#set heading(numbering: "1.1")
#show heading.where(level: 1): it => block(above: 1.4em, below: 0.7em, text(13pt, it))
#show heading.where(level: 2): it => block(above: 1.1em, below: 0.6em, text(11pt, it))
#show heading.where(level: 3): it => block(above: 0.9em, below: 0.5em, text(10.5pt, style: "italic", it.body))
#set list(indent: 0.6em, body-indent: 0.5em, spacing: 0.55em)
#set enum(indent: 0.6em, body-indent: 0.5em, spacing: 0.55em)
#show raw: set text(font: "DejaVu Sans Mono", size: 8.8pt)
#set table(stroke: (x, y) => (top: if y <= 1 { 0.6pt } else { 0.3pt + luma(200) }, bottom: 0.6pt),
  inset: (x: 5pt, y: 4pt))
#show table.cell.where(y: 0): set text(weight: "bold")
#set figure(gap: 0.6em)
#show figure.caption: set text(9pt)
#show figure: set block(above: 1em, below: 1.2em)

#let sci(m, e) = $#m times 10^#e$

// Title block
#align(left)[
  #text(17pt, weight: "bold")[Brain SPECT simulation: progress, Oct 7–9, 2026]
  #v(0.2em)
  #text(10.5pt)[Fang Han · RPIL · October 9, 2026]
]
#v(0.6em)

= Summary

Work from Wednesday Oct 7 to Friday Oct 9 followed the action items from the Oct 7 group meeting:

- Hamid: simulate a phantom acquisition equal to 15 mCi for 10 min, or 30 M counts.
- Arek: check that the ray-traced SRM agrees with the GATE SRM.
- Arek: simulate a realistic phantom, such as the ACR Jaszczak.

Main results:

- *Phantom simulations are running.* All test jobs passed on OSPool and ERIS. The full 15 min acquisitions of the small Jaszczak and the XCAT head (clinical and 10× activity) started on both clusters on Oct 9.
- *Hamid's target is covered.* The small Jaszczak gives about 118,000 counts/s in the main window: about 71 M counts in 10 min, 30 M counts in about 4.2 min. The list-mode data can be cut to either definition.
- *288 mm brain SRM.* Parts 1–9 of 10 are merged: #sci("9.14", 13) primaries, 90 % of the target. Part 10 is running on Expanse.
- *Ray-traced SRM (gammart).* For the same number of samples, the code is about 40 times faster, and about 120–150 times faster when rays that cannot reach a crystal are skipped. The response is a deterministic integral, not a Monte Carlo simulation. With sample points placed analytically (for example aimed at the pinhole openings), the error can be kept small without a very large number of rays. The time for a full SRM will be measured once the sampling scheme is fixed. The comparison with the 288 mm GATE SRM is planned, not done.
- *Jaszczak phantoms.* The models follow the Data Spectrum datasheets. Photo fitting and two AI image-to-3D tools (Hunyuan3D, TRELLIS.2) were used only to check the shape and to measure parts the datasheet does not give.
- *ACR Deluxe does not fit in the helmet.* The small Jaszczak fits when placed upside down, with 11.4 mm of space. It is used instead.
- *XCAT head.* Yuemeng's voxel XCAT was imported and tested first, but its image box overlaps the scanner hardware in GATE. The simulations use the published mesh50_XCAT head of Ben Auer et al.
- *Rim streaks.* The study is closed (separate 24-page report).

Feedback is requested on the questions in Section 4.

= Results

== 288 mm brain SRM on Expanse

- Merged so far: parts 1–9, #sci("9.14", 13) primaries of the #sci("1.016", 14) target.
- Accepted events: #sci("3.30", 10).
- Voxel sizes: 1, 1.5 and 2 mm (grids $288^3$, $192^3$, $144^3$).
- Part 10: 64 jobs running.
- Jobs so far: 894 completed, 59 failed, 1 timed out. Failed loops are left out of the SRM.
- Mean sensitivity over the 288 mm sphere: 0.036 %. The pinhole estimate at the centre is 0.041 %.
- Pipeline changes (Oct 6–7): the merge of parts no longer runs out of memory; a local job database; projection snapshots on the monitoring page.

== Ray-traced SRM (gammart)

=== Earlier check (Oct 5, before the meeting)

- The old ray-traced SRM was compared with the 210 mm GATE SRM using 10 mm spheres.
- Projections: correlation 0.9999 at the centre, 0.9997 off-centre.
- Total counts 3 % higher than GATE. Expected: gammart counts the first interaction in the crystal; GATE counts only events inside the energy window.
- That version placed its sample points at random, so two runs differed by 7–11 % in the main matrix entries. Placing the points by a fixed rule removes this.

=== Changes since then (Oct 7–8)

#figure(
  table(columns: (1fr, auto, auto), align: (left, right, left),
    table.header[Step][Time per voxel][Notes],
    [Before (Oct 5)], [3.16 s], [uniform sampling],
    [Batched sampling on the GPU], [82 ms], [same result (difference $6 times 10^(-12)$)],
    [Skip rays that cannot reach a crystal], [20–27 ms], [response changes by about $10^(-9)$],
    [Aim rays at the pinholes], [2–3.7 ms], [totals within 0.06–0.10 % of a reference],
  ),
  caption: [Time for the response of one source voxel (RTX 3080 Ti, full brain system). Rows 1–3 use the same 1024 sample points in every detector pixel, only to compare code versions; row 4 aims fewer rays at the pinholes. Neither is the number of rays an SRM needs.], kind: table)

- Row 4 aims rays into 3 mm cones around each pinhole, where almost all of the response comes from, plus 2 % in other directions so that no path is missed.
- The response is a deterministic integral over the source voxel and the detector pixels, evaluated along rays. It is not a Monte Carlo simulation: the same sample points always give the same result.
- Its accuracy depends on where the sample points are placed, not only on how many there are. Points can be placed analytically (for example a quadrature rule over the pinhole opening), which keeps the error small with far fewer rays than the 1024 per pixel in rows 1–3.
- The time for a full SRM is therefore not given by this table. It will be measured once the sampling scheme is fixed.
- New finding: much of the signal passes through the tungsten next to the pinhole, not through the hole itself. This must be modelled, not treated as a small correction.

#figure(
  table(columns: (auto, auto, auto, auto), align: (left, right, right, right),
    table.header[Pinhole variant][Width][Through the hole][Through the tungsten edge],
    [0], [0.556 mm], [46 %], [54 %],
    [1], [0.797 mm], [58 %], [42 %],
    [2], [1.215 mm], [70 %], [30 %],
    [3], [2.007 mm], [80 %], [20 %],
  ),
  caption: [Share of the primary response through the open hole and through the tungsten edge (mean of four source positions).], kind: table)

- In progress: an exact calculation of the part through the open hole (`gammart/pinhole.py`, written, not yet validated). Rays would then be needed only for the part through the tungsten.
- Planned (Arek's request): compare the new ray-traced SRM with both GATE SRMs (210 mm and 288 mm). The plan first measures the Monte Carlo noise of the GATE SRMs and the expected differences (energy window, scatter, pixel assignment), so that real errors can be separated from them.

== Rim streaks: study closed

The radial streaks at the edge of the 210 mm FOV come from the system matrix. They start where the object has activity at its own edge. They are not caused by truncation.

Added on Oct 7:

- *Shrunk ACR, fully inside the FOV (E9).* Weaker streaks remain at the edge of the object. This corrected an earlier reading that the streaks disappear once the object is inside the FOV.
- *Removing inserts one at a time (E9b).* The cold rods drive most of the edge streaks (stripe RMS 0.014 without inserts, 0.035 with).
- *Bright ring inside hot edges.* This is the known maximum-likelihood edge overshoot (Snyder et al., 1987): 11–15 %, stops growing with iterations, removed by a 10 mm post-filter.
- *What this means for the 288 mm SRM.* It is still needed, because real heads have activity outside 210 mm. For reconstruction, start the image near zero ($epsilon approx 0.01$) outside the body outline, not uniform over the whole sphere.

The full study is in `dev/reports/2026-10_rim_streaks/report.pdf` (available on request).

#figure(image("figures/rim_streaks_polar_edge.png", width: 80%),
  caption: [Rim streaks in polar view: each row unwraps the edge of the object (x: angle, y: distance from the edge). Rows 1–3: ray-traced SRM; rows 4–5: GATE SRM. Streaks remain at the edge of the shrunk phantom in every case.])

== Jaszczak phantom design: based on the Data Spectrum datasheets

*The final phantom models follow the Data Spectrum datasheets.* Every datasheet value is used as given: diameters, inner heights, wall thickness, rod and sphere sizes, rod length, and water volume. Other methods were used only to check the overall shape and to estimate parts the datasheets do not give (lid and base thickness, lid fittings, sphere stems).

#figure(
  table(columns: (auto, 1fr, 1fr), align: (left, left, left),
    table.header[Method][What it gave][How it was used],
    [Datasheets (both phantoms)], [diameters, inner heights, wall, rods (88 / 40 mm long), spheres, water volume (ACR: about 5.5 L)], [*the design values*],
    [Camera fit to the vendor photo], [outer height 208.5 mm; base + lid 22.5 mm; positions of lid fittings; silhouette match 0.994 (IoU)], [checks the datasheet model; measures parts not in the datasheet],
    [Hunyuan3D-2.1 (AI, one photo → 3D mesh)], [outer height 208.4 mm when scaled by the datasheet diameter; screw positions; silhouette match 0.979], [independent check of height and lid parts; no usable interior (hollow shell)],
    [TRELLIS.2 (AI, one photo → 3D mesh)], [interior: sphere stems start at the rod-plate top, 4.6–5.5 mm wide], [where the stems start; not used for any size],
  ),
  caption: [Sources of the Jaszczak dimensions. AI meshes have no scale of their own and fill hidden parts from learned shapes, so no dimension is taken from them alone.], kind: table)

- *Datasheet checks that changed the model:*
  - Rod insert: rods sit in 2 mm deep holes of two plates; insert 93.5 mm tall. This gives 5.54 L of water with the insert (datasheet: about 5.5 L).
  - *Bug fixed (Oct 9):* the voxel ACR phantom placed the 88 mm rods 12 mm too low, so only 76 mm of each rod was cold. *ACR rod results made before Oct 9 used the wrong rods.*
  - Small phantom: sphere centres 78 mm above the inner floor, on stems standing on the floor (datasheet value and datasheet photo).
- *Still open:* the ACR datasheet sphere height can be read as 127 or 139 mm above the base. The photo suggests 130–134 mm. The model uses 127 mm.

#figure(image("figures/acr_photo_model_hunyuan.png", width: 100%),
  caption: [ACR Deluxe. Left: vendor photo. Middle: datasheet model drawn with the camera fitted to the photo. Right: Hunyuan3D-2.1 mesh made from the same photo, scaled by the datasheet diameter.])

#figure(image("figures/acr_trellis2_views.png", width: 100%),
  caption: [TRELLIS.2 mesh from the same photo. The cut view (right) shows the sphere stems starting at the top of the rod insert. The rod details are not reliable.])

== Which Jaszczak phantom fits in the helmet

*How the check works.* The phantom stands on the helmet axis. It is moved up and down in 1 mm steps. At each height, the program finds the smallest distance between the phantom and the scanner hardware (lead shield and the 73 collimators). This distance is the "gap".

- Gap above 0: the phantom fits, with that much space left.
- Gap below 0: the phantom overlaps the hardware, so it cannot be placed there.
- The phantom includes its lid fittings (caps, screws, knob). They are turned around the axis into full rings, so the result holds for any rotation of the phantom.
- Accuracy: about 1 mm (the hardware surface is sampled every 1.5 mm or less).

*How to read @fig-profile.* The x-axis is the height of the phantom's water centre, relative to the centre of the field of view. Each curve is one phantom in one orientation. The phantom can be placed at every height where its curve is above the black line.

- *ACR Deluxe (blue):* both curves stay below 0 at every height. The best case still overlaps by 5.8 mm (upside down) or 8.9 mm (upright). The ACR phantom does not fit.
- *Small Jaszczak, upright (red):* above 0 only for heights of −16 mm or lower. At −16 mm the gap is 0.3 mm, and the rods are 70 mm below the FOV centre, close to the bottom of the FOV.
- *Small Jaszczak, upside down (orange):* above 0 for all heights up to +39 mm. This leaves room to bring the rods and spheres near the FOV centre.
- *Chosen position (orange dot):* z = −25 mm, gap 11.4 mm. The rods are 29 mm above and the spheres 28 mm below the FOV centre.
- Why the curves are flat on the left: when the phantom is low, the closest point is at the bottom opening of the helmet, and this distance does not change with height.

#figure(image("figures/clearance_profile.png", width: 82%),
  caption: [Smallest gap between the phantom and the shield and collimators, against the height of the phantom. Red area: overlap.]) <fig-profile>

*How to read @fig-sides.* Each panel is a side view at one height. The x-axis is the distance from the helmet axis, so the phantom is shown as a half cross-section. Grey: shield and collimators. The black × marks where the phantom comes closest to the hardware (or overlaps it most).

- ACR upright: the lid screws hit the top of the helmet.
- ACR upside down: the lid fittings hit the lower collimators.
- Small, upright: the lid fittings touch the top of the helmet.
- Small, upside down: the lid and fittings hang out through the bottom opening. The closest point is the side knob near a lower collimator, 11.4 mm away.

#figure(image("figures/clearance_side_views.png", width: 100%),
  caption: [Side views of the four cases at the heights marked in @fig-profile.]) <fig-sides>

#figure(
  table(columns: (auto, auto, 1fr, auto), align: (left, left, left, right),
    table.header[Case][Fits for heights][Insert positions][Gap],
    [ACR, upright], [never], [–], [−8.9 mm (best)],
    [ACR, upside down], [never], [–], [−5.8 mm (best)],
    [Small, upright], [≤ −16 mm], [at −16 mm: rods −70, spheres −13 mm], [+0.3 mm],
    [*Small, upside down (chosen)*], [≤ +39 mm], [at −25 mm: rods +29, spheres −28 mm], [*+11.4 mm*],
  ),
  caption: [Summary of the clearance check.], kind: table)

- The ACR approves the small phantom only for listed cameras (mostly cardiac). Using it for accreditation of this system would need ACR agreement.

== One phantom definition for all tools

Before Oct 9, each tool (voxel phantom, GATE simulation, clearance check, 3D model) had its own copy of the phantoms, and the copies did not agree. For example, the GATE ACR phantom had a 102 mm water radius instead of 104.5 mm.

- Now one file, `phantom_models.py`, defines each phantom.
- The voxel phantom, the GATE geometry, the meshes, the ray-tracer scene and the 3D viewer are all built from it.
- The GATE cardiac simulation now uses it too. Earlier cardiac phantom results used the old copy.

#figure(
  table(columns: (1fr, auto), align: (left, left),
    table.header[Check][Result],
    [3D viewer vs Python model, 40 random positions], [max difference $4 times 10^(-14)$ mm],
    [GATE geometry vs voxel phantom, 4 positions], [no real differences (8–15 voxels exactly on a surface)],
    [Exact path lengths vs ray sampling at 0.01 mm], [≤ 0.018 mm],
    [Ray tracer vs exact transmission, 140.5 keV], [mean $3 times 10^(-4)$, worst ray $4 times 10^(-3)$],
    [Meshes vs exact volumes], [closed surfaces; totals within 0.03 %],
    [Geant4 overlap check, both phantoms], [no overlaps],
  ),
  caption: [Agreement between the outputs built from the single phantom definition.], kind: table)

#figure(image("figures/small_jaszczak_in_helmet.png", width: 88%),
  caption: [Small Jaszczak as simulated: upside down, water centre at z = −25 mm, turned −150° so the largest rods face the face opening (the least-sampled direction). Right: axial, sagittal and coronal cuts; green circle: 288 mm FOV.])

== XCAT head phantom: Yuemeng's voxel XCAT, then Ben Auer's mesh50_XCAT

=== Yuemeng's voxel XCAT (investigated first)

Her brain perfusion XCAT (from her BrainPET GATE example) was imported into the phantom tools and tested in GATE.

- Image: 141 × 134 × 186 voxels of 1.5 mm, with an activity map and an attenuation map.
- Activity levels: grey matter 16, white matter 8, so grey : white = 2 : 1.
- Her GATE material table maps the brain's attenuation value to SpineBone (bone). It was probably written for a different scaling. Our import maps it to soft tissue instead; her table is kept as an option.
- The head itself fits in the helmet (about 6 mm clearance with the brain at the FOV centre).
- *Problem:* in GATE the whole image box (201 × 279 × 212 mm) is one volume. It reaches through the shield and collimators. Overlapping volumes give wrong photon tracking, and the first pilot with it was invalid.
- Fixes that were tried:
  - Hardware in a separate (parallel) world: correct, but the simulation is 3.3 times slower.
  - Splitting the image into boxes that avoid the hardware: 1,052 boxes, not practical.
  - Building surface meshes from the voxels: worked (640,000 triangles), but repeats a published phantom.

=== Ben Auer's mesh50_XCAT head (used in the simulations)

- Published by Auer et al.: XCAT body, skeleton, brain and air cavity as surface meshes (about 24,000 triangles), validated in GATE. MIT licence, redistribution agreed with the XCAT developers.
- Activity: the published brain perfusion map. Grey : white : striatum : background = 9.3 : 2.3 : 10.1 : 1 (grey : white about 4 : 1, closer to clinical perfusion than 2 : 1).
- Small overlaps between the published meshes (7.3 and 1.6 mm³) were removed. Geant4 then reports no overlaps with the full scanner hardware.
- No parallel world is needed.
- Fit: 9.9 mm clearance with the brain centre at the FOV centre and the face toward the face opening.
- Only the head is used. A head-and-torso version exists but is not used yet.

#figure(image("figures/mesh50_head_in_helmet.png", width: 88%),
  caption: [mesh50_XCAT head in the helmet, brain centre at the FOV centre. Right: cuts through the activity map with the mesh outlines.])

== Reference run: Yuemeng's GATE 9 Jaszczak simulation

Her DC-SPECT Jaszczak run is documented as a reference. It cannot be compared directly with ours:

- Each of the 80 heads was simulated alone, without the housing.
- The phantom is a water cylinder with rods only (150 × 100 mm, 66 rods, no spheres, no PMMA).
- Her activity map is mirrored in y relative to the air rods in one of her macros.
- Her brain design (DB-SPECT, 118 modules) has design numbers but no GATE runs to compare with.

= Phantom simulations on OSPool and ERIS

== Test jobs: all passed

#figure(
  table(columns: (auto, auto, auto, 1fr), align: (left, left, right, left),
    table.header[Cluster][Phantom][Jobs][Result],
    [OSPool], [Small Jaszczak], [3 × 50 ms], [all exit 0; 24.7 M primaries and about 12,150 counts per job],
    [OSPool], [mesh50 head, clinical], [3 × 100 ms], [all exit 0; 3.95 M primaries and about 2,270 counts per job],
    [ERIS], [Small Jaszczak], [4 × 50 ms], [all exit 0],
    [ERIS], [mesh50 head, clinical], [4 × 100 ms], [all exit 0],
  ),
  caption: [Test jobs (Oct 9). Counts are all recorded singles before the energy window.], kind: table)

- Every job had the expected number of primaries. The time windows of the jobs join without gaps or overlaps.
- The merge of the jobs worked on the real cluster output.

#figure(
  table(columns: (auto, auto, auto), align: (left, right, right),
    table.header[Cost per primary (one core)][Small Jaszczak][mesh50 head],
    [Workstation (pilot)], [26.5 µs], [163 µs],
    [OSPool (AMD EPYC / Intel Xeon)], [about 23 µs], [about 230 µs (161–314)],
    [ERIS (Xeon Gold 5318Y)], [49 µs], [324 µs],
  ),
  caption: [Measured cost. Memory per process: 0.45 GB (Jaszczak), 1.3 GB (head).], kind: table)

== Count rates (main window, 126–154 keV, after energy blur)

#figure(
  table(columns: (auto, auto, auto, auto), align: (left, right, right, right),
    table.header[Phantom][Counts per second][10 min][15 min],
    [Small Jaszczak, 15 mCi], [about 118,000], [about 71 M], [about 106 M],
    [mesh50 head, clinical: from inside the FOV], [about 7,600], [about 4.6 M], [about 6.9 M],
    [mesh50 head, clinical: from outside the FOV], [about 5,500], [about 3.3 M], [about 5.0 M],
  ),
  caption: [Count rates from the OSPool test jobs (0.15 s of Jaszczak data, 0.2 s of head data). The 10× head run has 10 times these counts.], kind: table)

- Small Jaszczak: 77 % of the counts in the main window did not scatter in the phantom.
- *Hamid's target:* 10 min at 15 mCi gives about 71 M counts; 30 M counts are reached in about 4.2 min. The full run is 15 min of list-mode data, so either definition can be cut from it afterwards.

== Full runs: launched Oct 9, about 7 pm EDT

Each cluster runs the complete target on its own, so each is a backup for the other. Random seeds differ for every job.

#figure(
  table(columns: (auto, 1fr, auto, auto), align: (left, left, left, left),
    table.header[Run (15 min each)][Activity][OSPool][ERIS],
    [Small Jaszczak], [15 mCi (555 MBq) in the water], [1,800 jobs × 0.5 s], [1,200 slices × 0.75 s],
    [mesh50 head, clinical], [27.75 MBq in the brain (5 % of 15 mCi); 44.4 MBq total], [1,800 jobs × 0.5 s], [720 slices × 1.25 s],
    [mesh50 head, 10×], [277.5 MBq in the brain], [9,000 jobs × 0.1 s], [7,200 slices × 0.125 s],
  ),
  caption: [Full runs. OSPool: 12,600 jobs, about 27,000 core-hours, 1.3–2.5 h per job. ERIS: 190 array tasks of 48 cores, about 41,000 core-hours, 4.4–5 h per slice.], kind: table)

Settings shared by all runs:

- Tc-99m emission lines (0.891 photons per decay) and the 6.0 h half-life; acquisition 0–900 s.
- Physics list G4EmStandardPhysics_option4 (the same as the 288 mm SRM).
- Each count keeps its true energy, the decay position, and whether the photon scattered in the phantom.
- At the merge: energy blur (10 % FWHM at 140.5 keV); 1 keV energy bins from 10 to 200 keV; main and scatter (TEW) windows.
- At the merge, counts are also split by where the decay happened: inside or outside the 288 mm FOV.

== Finding: activity in the shoulders reaches the bottom detectors

- In the head runs, 42 % of the counts in the main window come from decays outside the 288 mm FOV.
- These counts land on the three lowest detector heads (heads 0, 9 and 1, at −37° elevation).
- They come from the shoulder tops of the phantom, about 175 mm below the FOV centre. The shoulders hold 30 % of the phantom's activity.
- Almost none of these photons scattered.
- The SRM does not include this region, so these counts would appear as unmodelled background in those three heads.
- Not yet known: whether these photons pass through the pinholes, through the sides of the modules, or below the shield (the shield ends at −47°). This decides whether it is an effect of where the phantom is cut, or a gap in the shielding design.

== Cardiac SRM on OSPool

- About #sci("2.0", 13) primaries have returned from 39,882 jobs. This is 1.5 times the current merged SRM (#sci("1.33", 13)).
- The rest is not merged yet: the script for the combine step is missing from the repository, and the automatic combine has failed since Oct 6.
- 77 held jobs (over the 20 h time limit or the disk limit) were removed. Their data are lost.

= Questions for the group and next steps

== Questions

+ Is the small Jaszczak an acceptable replacement for the ACR Deluxe, given that the Deluxe does not fit? Should we contact the ACR about accreditation use?
+ Phantom position: rods and spheres balanced around the FOV centre (current choice), or one insert at the centre with more than 20 mm gap? Should the largest rods face the face opening (least sampled) or away from it?
+ Which cut of the 15 min data should be the standard: 10 min, or 30 M counts?
+ Is 5 % of 15 mCi in the brain the right clinical activity for the XCAT head?
+ Should the main analysis use only decays inside the FOV, and report the outside part separately? Is the head-and-torso phantom needed?
+ Can someone measure our ACR phantom with calipers? The sphere height and the base/lid thickness are inferred, not measured.

== Next steps

- Follow the full phantom runs; merge each campaign when it finishes; copy the ERIS results from scratch.
- Finish part 10 and merge the full 288 mm SRM.
- Validate the open-hole calculation in gammart, then compare the ray-traced SRM with the 210 mm and 288 mm GATE SRMs.
- Find the path of the shoulder photons to the bottom detectors.
- Reconstruct the small Jaszczak (forward projection with the 288 mm SRM first, then the simulated data).
- Restore the cardiac combine step and merge all three cardiac batches.

= Files and code

Repository `qmirt-gate-10-sim`, branch `brain-288mm-csg-production`. Ray tracer: `pytorch-optix/gammart`.

#table(columns: (auto, 1fr), align: (left, left),
  table.header[Item][Location],
  [288 mm SRM, parts 1–9], [`/data/<user>/opengate_sim/data/brain_spect/`\ `brain_288mm_csg_102t_20261005T211647Z_merged_p01-09/`],
  [Phantom runs: IDs, settings, outputs], [`submit_htcondor/brain_phantom_production_status.md` (commit 9db555c)],
  [Phantom sim code and jobs], [commits a67dfc6, d806a78; `submit_htcondor/wrapper_brain_phantom_sim.sh`, `submit_slurm/run_brain_phantom_eris.sh`],
  [Phantom definition, GATE builder], [`payload/python/phantom_models.py`, `phantom_gate.py`],
  [Phantoms used in the runs], [`dev/python/phantoms/` (not yet committed)],
  [Jaszczak design and clearance], [`dev/python/phantom_fit/`, `dev/python/phantom_3d/`],
  [mesh50_XCAT source and citations], [`dev/python/phantom_sources/mesh50_xcat_head/README.md`],
  [Yuemeng's XCAT and Jaszczak reference], [`dev/python/phantom_sources/xcat_brain_perfusion/`, `dev/python/yuemeng_reference/`],
  [Ray tracer changes], [`pytorch-optix/docs/shield_tracing_study.md`, `gammart/pinhole.py`],
  [Rim streak report], [`dev/reports/2026-10_rim_streaks/`],
  [Cardiac OSPool status], [`submit_htcondor/cardiac_production_status.md`],
)
