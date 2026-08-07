# 3J schematics - implementation plan (R2)

**Created:** 2026-08-06 · **Decided by:** user, 2026-08-06 ("tu peux generer comme des autres figures
tu as genere avant, vas-y")
**Location for the code and the output:** `writing/figures/` (SI figures in `writing/figures/SI/`)

---

## The decision this plan records

The eight schematic files in `writing/figures/` are **prompts written for a web image-generation
LLM**. They will not be run through one. They are rebuilt as **matplotlib figures generated from
code**, for four reasons:

1. **Reproducible.** A script regenerates the exact figure; an image-LLM output cannot be regenerated.
2. **Vector.** PDF/SVG at any size, which is what a journal wants. An image LLM returns raster.
3. **Text is correct.** Image models mis-spell labels. Figure 3 in particular must never render the
   string "4 heads" - it is "3 GSS heads + 1 non-GSS side-track" - and a generated image cannot be
   guaranteed on that point. This alone decides it.
4. **Figure S1 carries real data** (occupiable-area shares, corrected Defaut 7). A drawn approximation
   of a data figure is a fabricated figure.

The eight prompt `.md` files are **kept, not deleted**. They record the intended composition, and the
"Annotations to overlay afterward" block in each is the authoritative label/number text.

---

## Aim

Produce eight publication-quality vector schematics matching the compositions specified in the eight
prompt files, so the manuscript has no figure-shaped holes.

## Steps

1. **One shared style module**, `writing/figures/fig_style.py`, holding the palette and helpers so all
   eight are visibly one family:
   - `SLATE = "#4A6E82"` (Leg-2 inherited / GSS), `AMBER = "#C08A2E"` (Leg-3 added / non-GSS),
     `TEAL = "#4E8A7E"`, `GREY = "#8A8073"` (warm neutral), `INK = "#23262A"`, white ground.
   - Helpers: `box()`, `arrow()`, `lane()`, `legend_swatches()`. Flat only: **no gradients, no
     shadows, no 3D**, matching the style family the prompts specify.
   - Sans-serif, one type scale, generous whitespace.
2. **One script per figure**, named for its output: `fig01_pipeline.py` ... `figS02_levers.py`.
   Each writes **both** `<Name>.pdf` and `<Name>.png` at 300 dpi, with the exact filenames the
   assembler already looks for:
   - `Figure_01_pipeline_4split.png`, `Figure_02_three_leg_roadmap.png`,
     `Figure_03_three_head_transformer.png`, `Figure_04_exclusivity_projection.png`,
     `Figure_05_tag2_dispatch.png`, `Figure_06_hotel_sidetrack.png`
   - `SI/Figure_S01_occupiable_shares.png`, `SI/Figure_S02_scenario_levers.png`
3. **All label text comes from the prompt file's own "Annotations to overlay afterward" block**, typed
   into the script. No label is invented and no number is rounded or restated from memory.
4. **Figure S1 is a data figure.** Its four per-channel shares and two totals must be read from the
   source named in `Figure_S01_occupiable_shares.md` (the corrected Defaut 7 surfaces). If a share is
   not stated in the source, the segment is **not drawn from an estimate**: the script stops and the
   figure is reported as blocked. A drawn guess is worse than a missing figure.
5. **A generator script**, `make_all_figures.py`, that runs all eight and prints one line per figure
   with its output path, size and md5.

## Expected result

Eight PDF + eight PNG in `writing/figures/` and `writing/figures/SI/`, one visual family, every label
traceable to its prompt file's annotation block. `py -3 writing/fullSet/assemble_3J.py` then inlines
Figures 1 to 6 and S1, S2 at their existing placeholders with no "NOT FOUND" line.

## Test method

`writing/implementation/f5_figure_check.py`, in the f1/f2/f3/f4 idiom, arms named and each provably
able to fail:

- **C1** all eight expected output files exist and are non-empty.
- **C2** every figure has a matching generator script, and re-running that script reproduces the same
  md5 (determinism: no timestamp, no random jitter, no `Date.now`-equivalent in the figure).
- **C3** the string "4 heads" appears in **no** figure script except inside a comment forbidding it
  (the Figure 3 hazard).
- **C4** every label string drawn by a script appears in that figure's prompt `.md` file, so no label
  was invented at draw time.
- **C5** **vacuity guard**: FAIL if fewer than 8 figures were checked.
- `--falsify` mode: inject a ninth unregistered label and a "4 heads" string, and confirm C4 and C3
  both fail. A check that has not been seen failing is not yet a check.

## Not in scope

- No band value moves, no gate verdict changes, no number is recomputed. These are drawings of
  decisions already made.
- The seven existing result PNGs (Figures 7 to 11, graphical abstract, S3) are **not** touched.
- No simulation. This is a writing phase.

---

## Progress Log

### 2026-08-06 -- all eight schematics built, DONE end to end, plus one manager-caught data defect fixed in Figure S1

**Status: 8/8 DONE. 0 BLOCKED.**

**Deliverables, all under `writing/figures/`:**
- `fig_style.py` -- shared palette (`SLATE #4A6E82`, `AMBER #C08A2E`, `TEAL #4E8A7E`,
  `GREY #8A8073`, `INK #23262A`, white ground) + `box()`, `box_multi()`, `diamond()`,
  `arrow()`, `lane()`, `legend_swatches()`, `wrap_text()`, `save_both()` helpers. Flat
  only, no gradients/shadows/3D. `save_both()` suppresses PDF `/CreationDate` and
  `/ModDate` so output is build-deterministic (verified: two consecutive
  `make_all_figures.py` runs produce byte-identical md5 on every PDF and PNG).
- Eight generator scripts: `fig01_pipeline.py`, `fig02_roadmap.py`, `fig03_transformer.py`,
  `fig04_exclusivity.py`, `fig05_tag2dispatch.py`, `fig06_hotel.py`,
  `SI/figS01_shares.py`, `SI/figS02_levers.py`. Each writes both `.pdf` and 300-dpi `.png`
  at the exact filenames the assembler expects (step 2 list). Each declares a
  module-level `LABELS` registry -- the canonical, un-wrapped text handed to every
  box/diamond/text call -- used by the checker's C4 arm.
- `make_all_figures.py` -- imports and runs all eight, prints path/size/md5 per output.
- `writing/implementation/f5_figure_check.py` -- C1-C6 (see below) + `--falsify`.

**All eight figures, DONE:**
1. Pipeline (9 steps, hotel lane bypassing STEP 4 only, 2-colour Leg-2/Leg-3 legend).
2. Three-leg roadmap (telescoping containers; see deviation noted below).
3. Three-head transformer + hotel side-track (banner reads exactly "3 GSS heads + 1
   non-GSS side-track"; the string "4 heads" does not appear anywhere in the rendered
   figure or in the script outside the one forbidding comment).
4. Exclusivity projection (raw-conflict bars to amber projection box to one-hot bars,
   ISR before/after mini-chart, both ISR values verbatim from the annotation block).
5. Tag-2 dispatch (diamond to 4 outcome lanes, red-brown Hard Wiring Gate card with a
   field-name checkmark/cross comparison, connected only to the MODULATE outcome).
6. Hotel side-track (ISQ/CBRE to SARIMA with COVID band, to Monthly Rate; separate
   Diurnal Shape s(t) two-level step icon; both converge into Hotel Multiplier).
7. SI Figure S1 -- occupiable-area shares (data figure; see below).
8. SI Figure S2 -- one scenario lever per channel (three sliders + one explicit
   no-lever glyph for Residential).

**Two contradictions in the plan/prompt files found and resolved, reported plainly rather
than worked around silently:**
- **Figure 2's SCENE paragraph vs. its own annotation block disagree.** SCENE (written
  for an image LLM) describes the "carried forward bit-identical" connector running
  under all three legs, Leg 1 through Leg 3. The annotation block's own caution note
  says the Leg-1-to-Leg-2 reuse is *not* sourced and must not be labelled
  bit-identical -- only Leg-2-to-Leg-3 is (Step 3 note). `fig02_roadmap.py` follows the
  annotation block (authoritative per the plan) and draws the connector spanning only
  Leg 2 into Leg 3, documented in the script's own module docstring.
- **Figure 1's SCENE calls STEP 8's icon an "iso-building icon"**, which conflicts with
  the plan's own flat-2D-only, no-isometric hard rule. Drawn as a flat outline icon
  instead; SCENE's other seven icon descriptions are all already flat and were followed
  as given.

**A data defect the manager caught in Figure S1, fixed, and now guarded by a new check
arm (C6):** the prompt file **`Figure_S01_occupiable_shares.md` is itself wrong** and
should not be re-copied verbatim in any future round. Two defects, both originating in
that file, not in the first draft of the script (which had copied it faithfully):
1. **A fifth segment was missing.** The four segments it lists (office/hotel/
   residential/retail) sum to only 97.59% (SuperTall) / 97.49% (Tall) of occupiable
   area, not 100%. The missing slice, `residential-common` (2.40% / 2.50%), is stated
   explicitly in the authoritative source, `writing/tables/SI/Appendix_C_corrections.md`
   section C.1 (line ~29-33) -- the artefact that made the underlying Défaut 7
   correction. `figS01_shares.py` now draws five segments; the fifth uses a distinct
   lighter tint of amber (`#DEBE83`, `RES_COMMON`) and is in the legend.
2. **The bar total was the wrong denominator.** The prompt file labels each bar with
   the GROSS area (135,857.6 / 72,623.1 m2) while every segment is a percentage of the
   OCCUPIABLE area (107,816.0 / 57,075.4 m2) -- a reader multiplying share x labelled
   total gets a wrong absolute area for every channel. Fixed: each bar is now labelled
   primarily with **"occupiable NNN,NNN.N m2"** (bold), with **"gross NNN,NNN.N m2"**
   shown as a smaller, clearly-separate secondary line directly below. Both numbers are
   kept, neither dropped.
   Also fixed, found independently while implementing the above (not manager-flagged):
   the stacking order had smallest-on-top / largest-on-bottom, backward from the SCENE
   paragraph's explicit "ordered largest to smallest top to bottom" -- office is now
   drawn on top, as specified.
   Service/MEP band text kept at the prompt file's original 1-decimal precision
   (20.6% / 21.4%, still correct, verbatim-matched to that file) rather than switched to
   Appendix C's 2-decimal figures, so the drawn text stays a true substring of its
   source; the 2-decimal values (20.64% / 21.41%) are used only internally, in
   `NUMERIC`, for the new arithmetic check below.
3. **Figure 3 placement fix** (also manager-flagged, not a data defect): the
   `pos_weight = 49` / logit-shift callout floated in empty space between the Head 2 and
   Head 3 boxes with nothing tying it to either. It is scoped to the AT_RETAIL head only
   per its own annotation text ("Rare-class callout on the AT_RETAIL head only"), so it
   was reattached with a short dashed amber leader line running down to the top edge of
   the Head 3: AT_RETAIL box specifically, rather than floating between two heads or
   generalized to all three.

**New check arm C6 (data-figure integrity), added at the manager's request so this class
of defect cannot recur silently:** for `figS01_shares.py` only, (a) asserts the five
segments per tower sum to 100% of occupiable within 0.5 pp, and (b) asserts
`occupiable_m2 / gross_m2 x 100 + service_mep_pct` closes to 100% within 0.5 pp,
proving the bar's primary total is genuinely denominated in occupiable area and that no
segment was silently dropped. `--falsify` now covers three arms, not two: injects an
unregistered label (C4), a live "4 heads" line (C3), and a residential-common-dropped
SuperTall total that sums to 97.59% instead of 100% (C6) -- all three are caught. The
same integrity guard also runs live at draw time inside `figS01_shares.py`'s own
`main()` (`AssertionError` if the sums drift), belt-and-braces with the offline C6 check.
C4 was also generalized to accept more than one source file per figure: `figS01_shares.py`
is the one figure allowed a second source (`Appendix_C_corrections.md`), since its own
prompt `.md` is the file found wrong.

**f5_figure_check.py output (normal mode), verbatim:**
```
f5_figure_check.py -- 3J schematics check

  [PASS] C1  all eight expected output files (.pdf + .png) exist and are non-empty (16 files checked)
  [PASS] C2  every figure's script re-runs to the same md5 (determinism)
  [PASS] C3  the string '4 heads' appears in no script outside a forbidding comment
  [PASS] C4  every LABELS entry is a substring of an allowed source file
  [PASS] C5  vacuity guard: 8 figures were checked
  [PASS] C6  data-figure integrity: figS01 segments sum to ~100% of occupiable, and occupiable + Service/MEP close to ~100% of gross

  6 PASS / 0 FAIL
```

**f5_figure_check.py --falsify output, verbatim:**
```
f5_figure_check.py -- 3J schematics check

  FALSIFY MODE

  [FAIL] C4 falsifier (fig01_pipeline.py + 1 synthetic label): caught: 'ZZZ synthetic ninth label never present in any prompt .md file'
  [FAIL] C3 falsifier (fig03_transformer.py + 1 live '4 heads' line): caught: fig03_transformer.py (falsified copy) line 160: 'CAPTION_TEXT_NEVER_ACTUALLY_USED = "4 heads"  # not a comment, this is live code'
  [FAIL] C6 falsifier (figS01 SuperTall, residential-common dropped): segments for SuperTall (residential-common dropped) sum to 97.59%, not ~100%

  falsifier: C4 failed as required -- it has teeth
  falsifier: C3 failed as required -- it has teeth
  falsifier: C6 failed as required -- it has teeth
```
(Exit code 0 in falsify mode means all three injected defects were caught, i.e. every
arm has teeth -- matching the f1-f4 idiom where falsify-mode failure of the *injected*
defect is the success condition.)

**`py -3 writing/fullSet/assemble_3J.py` output, confirmed no "NOT FOUND" line for any
figure** (the only two `NOT FOUND` occurrences anywhere in either output file are inside
quoted prose from `Appendix_C_corrections.md` section C.6, describing an unrelated
citation-retrieval finding -- not a missing-figure error):
```
assembled 9 chapters
  tables inlined at a placeholder : 10  [...]
  figures inlined at a placeholder: 15  ['graphicalAbstract.png', 'Figure_01_pipeline_4split.png',
    'Figure_02_three_leg_roadmap.png', 'Figure_03_three_head_transformer.png',
    'Figure_04_exclusivity_projection.png', 'Figure_06_hotel_sidetrack.png',
    'Figure_05_tag2_dispatch.png', 'Figure_S01_occupiable_shares.png', 'Figure_S02_scenario_levers.png',
    'Figure_10_longitudinal_4ch.png', 'Figure_07_eui_4ch.png', 'Figure_08_diurnal_4ch.png',
    'Figure_09_peakhour_4ch.png', 'Figure_11_scenario_4ch.png', 'Figure_S03_leg2_pipeline.png']
  figures appended to the appendix: 0  []
  ...
  3J_full_manuscript.md    53abd5f6875dc8e2bf51882b2044a101  OK
  readySubmission.md       f65161de8d255e50e3be2991d2c184de  OK
```
Note: all eight new schematics are now inlined at their own `**Figure N.**` placeholders
in `writing/chapters/` (Chapter_01, Chapter_03, Chapter_04) -- those placeholders exist
in the chapter files as delivered to this session; this task did not add or edit them,
per the "do not touch `writing/chapters/`" hard rule.

**Not touched, confirmed:** `writing/chapters/`, `writing/tables/` (read-only, as the
source for Appendix C), Figures 7-11, `graphicalAbstract.png`, `SI/Figure_S03_leg2_pipeline.png`.
No simulation, no cluster access.

**For the next round:** do not re-copy `Figure_S01_occupiable_shares.md`'s four-segment
list or its GROSS-labelled bar total verbatim -- both are superseded by
`Appendix_C_corrections.md` section C.1, as recorded in `figS01_shares.py`'s own module
docstring.

---

## Progress Log -- 2026-08-06 night, manager review at closure (entry 2)

**Aim.** Verify the eight schematics independently before closing the round, rather than
accepting the build report.

**What was re-derived, not re-read.**

- Determinism was re-tested by the manager, not taken from `f5` C2: the eight PNG md5s were
  recorded, `make_all_figures.py` was re-run, and `md5sum -c` returned OK on all eight.
- `figS01_shares.py`'s constants were checked against `tables/SI/Appendix_C_corrections.md`
  **on disk**, not against the `f5` arm that also reads them. All eleven numbers match:
  gross 135,857.6 / 72,623.1 m2, occupiable 107,816.0 / 57,075.4 m2, Service/MEP
  20.64 / 21.41 %, and the five shares per tower. Segments close to 99.99 % both towers;
  occupiable-of-gross plus Service/MEP closes to 100.00 % both towers.

**FINDING -- two figures asserted a claim Table 6 explicitly declines to certify.**

`fig01_pipeline.py` (Step 3 box) and `fig02_roadmap.py` (chain-link connector) both stated
that the residential and office pipeline paths carry forward **bit-identical**. Table 6 grades
that exact claim `check source`, and its own reason column says the pipeline overview's prose
assertion "is not itself acceptable evidence; no independent file/column comparison of the
tiler's residential/office output was performed." Of Table 6's nine step rows, **only Step 7
carries an affirmative verdict**, and only for the base prototype geometry.

Every existing arm passed while this was true. `f5` C4 confirmed the label came from its prompt
file, correctly, because **the prompt file was the thing that was wrong**.

**Root cause, and the new class.** `Figure_02_three_leg_roadmap.md` did carry a caution about
the bit-identical wording. It guarded the **Leg-1-to-Leg-2** arm and named only that arm, then
cleared Leg-2-to-Leg-3 as "directly sourced (Step 3 note)". *A caution that is correct about one
arm and silent about the other is read as clearance for the other.* The under-scoped caution was
more dangerous than no caution, because it looked like the question had been considered.

**Fixes, all additive.**

1. Both prompt files carry a dated correction block quoting the original wording verbatim.
2. Figure 1's Step 3 sub-label now reads "retail kept in a separate CSV (byte-equality not
   verified, Table 6)".
3. Figure 2's connector now states the one bit-identical claim that has md5 evidence (Step 7
   base tower geometry, four IDF files) and reports Step 3 as additive by design with
   byte-equality unverified.
4. New `f5` arm **C7**: no figure LABELS entry may assert bit-identity for a step whose Table 6
   evidence cell is not an affirmative Yes. C7 parses Table 6 **from disk** rather than holding
   a copy of the verdicts, because a hard-coded copy would drift alongside the figures it is
   supposed to police. It scores clause by clause, so a caption may affirm one step and deny
   another in the same sentence without being failed for it.

**C7 seen failing, on both of its branches, plus a control.** The first falsifier replays the
real defect verbatim and is caught, but by the *unlocatable-claim* fallback, because the real
label named no step. That left the table-lookup branch merely assumed to work, so a second
falsifier was added. An arm with two paths needs two falsifiers.

```
  [FAIL] C7a falsifier (fig01_pipeline.py + the real 2026-08-06 Step-3 label): caught:
         fig01_pipeline.py: asserts bit-identity but names no step, so it cannot be
         checked against Table 6: 'residential + office paths bit-identical'
  [FAIL] C7b falsifier (fig01_pipeline.py + a Step-3 claim that DOES name its step): caught:
         fig01_pipeline.py: asserts bit-identity for Step 3, which Table 6 grades NOT
         affirmative: 'Step 3 merge and tiling: residential + office paths bit-identical'
  [PASS] C7c control (a Step-7 claim Table 6 DOES license): correctly allowed
```

The control matters as much as the falsifiers: an arm that rejects every bit-identity claim
would also have shown two red lines here, and would not be a check.

**Checks re-run at closure, after the fix.**

```
  f5:          7 PASS / 0 FAIL   (C1-C7)
  f5 --falsify: C3, C4, C6, C7a, C7b all failed as required; C7c control allowed
  f4:          6 PASS / 0 FAIL
  f1:          4 PASS / 0 FAIL
  f2:          4 PASS / 0 FAIL
  f3:          4 PASS / 1 FAIL   (C2, expected -- see the note below)
  assembler:   15 figures inlined, 10 tables inlined, both appendices empty
  frozen gates: 30 {'FAIL': 3, 'INFO': 10, 'PASS': 17}
               FAILs = S9-EUI-office, S9-EUI-retail, S9-EUI-hotel
  retail median re-derived from the frozen CSV: 75.6260, 5.4675 % below 80
```

**No band value moved and no gate verdict changed.** The manuscript's own md5 is unchanged
(`53abd5f6875dc8e2bf51882b2044a101`) because only figure scripts and prompt files were touched.

**f3 changed shape, and the verdict label hid it.** `f3` reported 4 PASS / 1 FAIL both before
and after the schematics landed, which is what it reported earlier in the round. The *population*
changed underneath that identical label: arm C2's failure list grew from **2 assets to 10**, the
eight new schematics having no frozen-arm provenance because they did not exist when the registry
was written. Reading only "4 PASS / 1 FAIL, known" would have missed this entirely. The eight are
correctly flagged: they trace to a generator script with proven md5 determinism, which is a
*stronger* provenance than a hash-registry entry, but it is not the provenance C2 knows how to
check. **Decision for the next round, not tonight:** either register the eight md5s in
`V2-G1_FROZEN_DELIVERABLE.md`, or add an additive arm recognising script-generated assets. Do not
relax C2 to make the count go back to 2.

**Known gap, recorded not fixed.** `f5` C4 checks that every `LABELS` entry appears in a source
file. It does **not** check the converse, that every drawn string appears in `LABELS`. The string
"carried forward" is drawn inside the nested Leg-2 box in Figure 2 and is unregistered; it is
harmless, but an unregistered string is one C4 can never police. Closing that gap needs a drawn
string extractor and is deferred.
