# Tier C repair: C1 (Figure 4), C2 (Figure 2), C3 (Figure 6) — 2026-09-14

Scope held: `writing/submission/figures/scripts/`, `writing/submission/figures/Prompts_Images/`, this
report. Did not touch `4J_manuscript_submission.md`, `4J_supplementary_material.md`, `tools/`, or the
Speed cluster. No gate, band, verdict or registered definition moved.

Backups made before any edit, all verified non-empty (`[ -s "$BK" ]`):
`writing/submission/figures/previous/scripts_bak_pre_tierC1C2C3_20260914/`
- `generate_fig04.py`, `generate_fig06.py`, `generate_fig02_loco.py`
- `4thJ_figure02_loco_design.md`

All edits made with the mandated guarded find-replace (`py -3`, `count()!=1` aborts).

---

## C1 — Figure 4 (`writing/submission/figures/scripts/generate_fig04.py`)

**Reproduced as reported.** Read the script before editing: title read
`"Figure 4: The Fictional-Country Control: Direction Versus Amplitude"` (line 106, original) while both
drawn panels were amplitude only (response curves; slopes-vs-floor bar chart). The header comment said
explanatory notes "were REMOVED from inside the image ... that text now lives in the manuscript prose" —
so the two load-bearing notes were confirmed absent, not merely hard to find.

**Spec file:** `Prompts_Images/4thJ_figure04_amplitude_slope.md`. The two notes it calls load-bearing
(section "Two qualifiers are load-bearing," lines 16-22, restated as notes (a)/(b) at lines 87-94):

> (a) *"the steering arm was never measured on the model this paper reports. It is inherited from the
> smaller pilot. It may appear only as text, clearly marked inherited, and never as a plotted series."*
>
> (b) *"the plotted slope is the six-channel pre-split figure, while the registered definition of the
> check counts five channels with one excluded by name. The registered definition was never applied to
> the reported model."*

**Verified against source before adding anything** (per the hard rule against inventing numbers):
- `Step6_docs/outputs_step6/g67_leg5_es.json` / `_uk.json` / `_it.json`, `steering` block, lines 122-126:
  `r2` = 0.9896766532040907 (es), 0.9914229425317623 (uk), 0.9940690138212029 (it), all `passes: true`,
  `r2_min: 0.80`.
- Same files, lines 113-116: `pooled_slope` (the five-channel, D-S6-13 definition) = 0.41530107... (es),
  0.532934577... (uk), 0.40486043... (it) — these **are** the values already plotted (0.4153/0.5329/
  0.4049), and `reasons` in each file states it in words: *"amplitude: slope 0.4153 over the 5 active
  aggregates is below 0.80 (the residual bucket AC4-8 is excluded, D-S6-13)."* `pooled_slope_all_six`
  (0.103/0.431/0.192) is a **different**, much lower set, not what is plotted.
- Manuscript §5.4, `4J_manuscript_submission.md:735-741`, already states both facts in prose: direction
  measured on the reported 7 B model (0.9897/0.9914/0.9941), and the plotted amplitude slopes are the
  five-channel definition with the residual bucket excluded.

So **both notes as originally written are now stale** — the facts they warn about no longer hold. I did
not paste the stale text into the figure (that would print a false claim). I added updated notes that
keep the same load-bearing role, sourced from the files above, and said so in the script's own
provenance comment.

**Repair applied:**
- **(a)** Added a third panel (`gs` changed from `1x2` to `1x3`, ratios `[1.7, 1.0, 1.0]`) drawing the
  steering R-squared per fold as horizontal bars against the same 0.80 floor line, titled "Direction vs
  registered floor." This is the layout choice for item (b): a **third panel**, not a second series on
  the existing bar chart, because the existing right panel is already a single-series floor comparison
  on a 0-1 scale — cloning that exact pattern for steering was the smallest change that kept both arms
  visually parallel and readable, versus cramming two differently-scaled series into one panel.
- **(c)** Amplitude panel x-axis relabelled `"Fitted slope (five channels, D-S6-13)"` (was `"Fitted
  slope"`), and panel title changed to `"Amplitude vs registered floor"` (was `"Slopes vs registered
  floor"`) to read as the counterpart to the new direction panel.
- Added the two notes as `fig.text` below the panels, reworded to the verified current facts:
  - Note a: *"Direction (steering) was measured on the reported 7.30 B model, not inherited from the
    pilot: R-squared 0.9897 Spain held out, 0.9914 Britain held out, 0.9941 Italy held out, against the
    registered floor of 0.80."*
  - Note b: *"The amplitude slopes plotted here use the five-channel definition ruled in D-S6-13; the
    residual channel AC4-8 is excluded by name and is not counted toward these values."*
  Note (c) from the spec ("a low slope means under-response, not indifference") was not added — it was
  not one of the two the spec calls load-bearing, and it is not needed to make the title honest.
- Did **not** add the spec's old right-panel verdict line ("Fails 3 of 3...") — the word is banned in
  authored figure prose by the standing house rule; the panel's own bars against the floor line already
  carry that fact wordlessly, same as before.
- No plotted amplitude value changed. Figsize kept at the original `(12, 7.2)` so pixel dimensions stay
  unchanged; only the internal gridspec/margins changed to fit three panels.

**Re-run:** `py -3 generate_fig04.py`, exit 0. Installed to all three configured paths (`figures/`,
`Prompts_Images/Figure_04_amplitude_slope.png`, `Prompts_Images/4thJ_figure04_amplitude_slope.png`),
all three identical.

| | Before | After |
|---|---|---|
| Pixel dimensions | 3600 x 2160 | 3600 x 2160 (unchanged) |
| md5 | `af7dfeb6f414e734d581a7e9645af0f9` | `a78cc584865467ba3b6ebdca538f5aee` (differs, as expected) |

---

## C2 — Figure 2 (`writing/submission/figures/scripts/generate_fig02_loco.py`)

Coordinator corrected the original instruction mid-task: Figure 2 is now built by this matplotlib script
(author ruling *"ok if possible you create these failed images,"* `Prompts/RESUME.md:19-40`, entry
last+271), not hand-generated by the author. The prompt file
`Prompts_Images/4thJ_figure02_loco_design.md` remains the specification; every drawn string is asserted
against its Section 12 TEXT INVENTORY.

**Manuscript caption and body verified** (read-only, did not edit):
- Caption, `4J_manuscript_submission.md:102`: *"**Figure 2.** - Leave-one-country-out design and the
  three nulls."*
- Body, `4J_manuscript_submission.md:650-654`: *"An unexpected property of **the three registered
  nulls** is reported here... The pre-registration named the raked donor pool as the strongest of
  **three nulls**."*
- Body, `4J_manuscript_submission.md:374-378` names them: the primary raked-donor pool (§3.5, the one
  the pre-registered bar is scored against), then *"Two secondary nulls are carried. Single-donor-country
  populations are built for every donor country in every fold... And a discrimination check asks
  whether the generated population is closer to its own country's published table than to any other
  country's..."* — i.e. three total: raked-donor pool, single-donor-country, discrimination check.

**What I found in the prompt file and script before editing:** both said **"two nulls"** — prompt file
H1 title (line 1) and its own installed-caption block (line 444), and the script's docstring (line 2).
None of the 29 entries in Section 12's TEXT INVENTORY (the only strings actually drawn onto the PNG)
contain the word "null" or a null count at all — that word appears drawn only once, inside the sentence
"The null wins 9 of 9," referring to the single primary null the bars are scored against. So the "two"
vs "three" count exists only in non-drawn title/caption/docstring text, never on the face of the image.

**Repair applied**, prompt file then script, in that order:
- Prompt file title (line 1): "two nulls" to "three nulls."
- Prompt file installed-caption block (line 444): "two nulls" to "three nulls."
- Script docstring (line 2) plus a provenance note: "two nulls" to "three nulls," recording that this is
  a wording match to the manuscript caption/body and that the schematic itself is unchanged — it still
  draws only the one primary null (raked donor pool) the LOCO transfer test is scored against; the two
  secondary nulls (single-donor-country, discrimination check) stay prose-only, consistent with this
  figure's own "What must NOT appear" section (no element beyond the transfer-scoring design).
- No assertion in the script counts nulls or asserts a null-related string, so nothing needed loosening.

**Re-run:** `py -3 generate_fig02_loco.py`, exit 0, all six arrowhead-placement assertions and the
text-overflow check passed unchanged (`arrowheads top 2 | bottom 2 | scoring 2 | marginals 0`, `no text
overflows its element`).

| | Before | After |
|---|---|---|
| Pixel dimensions | 3850 x 1277 | 3850 x 1277 (unchanged) |
| md5 | `84d64dafed1c382d68bf7103ab4dff27` | `84d64dafed1c382d68bf7103ab4dff27` (**unchanged**) |

**Declined to change / flagged rather than fixed:** the md5 is identical before and after because no
drawn pixel depends on the "two nulls"/"three nulls" phrase — it lives only in non-drawn title, caption
and code-comment text. I did not redesign the schematic to depict all three nulls graphically (adding
two more boxes/branches): that is a materially different diagram, not a wording fix, is outside "correct
the text inventory," and risks the exact backwards-arrow class of defect this figure has already failed
twice on (`FINDING 276`/`287`/`290`). Recorded here as a finding, not an edit: if the author wants the
picture itself to show three nulls rather than name three in its title, that is a new design task for a
future pass, not a byproduct of this word-count correction.

---

## C3 — Figure 6 (`writing/submission/figures/scripts/generate_fig06.py`)

**Confirmed the reported problem:** the figure carried no scale label anywhere — title, axis and body
text were silent on dwelling count.

**Dwelling count, read from the data file, not this prompt:** the spec
(`Prompts_Images/4thJ_figure06_appliance_peaks.md:11-13`) names the source as
`Step9_docs/outputs_step9/agg_diurnal.csv`, column `elec_w_per_dwelling`, and flags (`FINDING 278`) that
this is the **archetype-scale** run, not stock scale. `agg_diurnal.csv` itself has no dwelling-count
column, so I opened the manifests that produced it:
`Step9_docs/outputs_step9/step9_manifest_es.json`, `step9_manifest_uk.json`, `step9_manifest_it.json`,
field `n_dwellings` — all three agree: **`n_dwellings = 100`**.

**Repair applied:**
- Y-axis label changed from `"Mean appliance electricity, watts per dwelling"` to two lines:
  `"Mean appliance electricity, watts per dwelling\n(100-dwelling archetype run, not stock scale)"`.
- Added an axes subtitle under the figure title: `"Archetype scale: 100 dwellings per fold, not stock
  scale"`.
- Did not touch the plotted data, the axis limits, or any drawn value; only margins (`subplots_adjust`)
  were loosened slightly to fit the added subtitle line.

**Re-run:** `py -3 generate_fig06.py`, exit 0. Visual check: no text clipping, scale legible on both the
title area and the y-axis.

| | Before | After |
|---|---|---|
| Pixel dimensions | 3600 x 2160 | 3600 x 2160 (unchanged) |
| md5 | `0cd0ba3e60e7bbecbc5c44f90c2b7071` | `e520c555ce1e8cd62256fe190f5b8567` (differs, as expected) |

---

## Summary of what was declined

- Figure 4 note (c) from the spec, and the spec's old "Fails 3 of 3" verdict line: not added (banned
  wording / not one of the two load-bearing notes named by the task).
- Figure 2: the schematic was not redrawn to depict all three nulls graphically — only the title/caption
  wording was brought into agreement with the manuscript's "three nulls." This is recorded as a finding
  above, not resolved as an edit, per the no-redesign hard rule.
