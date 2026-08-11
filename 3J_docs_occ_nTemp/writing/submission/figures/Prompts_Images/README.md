# Image prompts for every figure in the 3J manuscript

> ⚠ **Paste ONLY the fenced code block below into the image tool.** Everything outside the
> fence is authoring notes, corrections and provenance. Pasting the whole file hands the
> generator text it is not supposed to draw.

One `.md` per image, fifteen in total, covering **every one of the fifteen images** in
`3J_manuscript_submission.docx` and `3J_manuscript_submission.md`. Generated `.png` files sit beside
their prompt; the installed copies live in `../` and `../SI/`.

**The standing rule, written into `CLAUDE.md` and `README.md` on 2026-08-09 at the author's
instruction:** the assistant never creates images. It writes the prompt, the author generates the
image, the assistant installs it and reports every defect it can see. The one exception is a plot
computed from data by a script - **plotting is not drawing**.

---

## The two kinds of prompt in this folder, and why they are not interchangeable

| | schematic prompts | data-figure prompts |
|---|---|---|
| which | 1, 2, 3, 4, 5, 6, S2, S3, graphical abstract | **7, 8, 9, 10, 11, S1** |
| what they contain | a scene description in prose | **a scene description AND the full measured series, in tables** |
| what they may show | structure, sequence, mechanism | the paper's results |
| what happens if the tool improvises | a diagram that looks slightly different | **a fabricated result** |

🔴 **A prompt for a figure that carries measured numbers must carry those numbers.** Every value in
the six data prompts was pulled from the frozen deliverable
(`Leg3_4-split/Step9_docs/outputs_step9_deliverable/`, `Step8_docs/outputs_step8/agg_deliverable/`)
by re-implementing the plotting code's own filters, and each prompt names the file, the column and
the source line. **Do not retype them, do not round them, do not let a tool infer them.**

This is not a hypothetical. The generated **Figure S1** installed on 2026-08-09 labels one bar
`4.0.1` and the other `0.37`, has no axis, and carries a footnote reading *"Mechanical, etelorgical
ancr of coherotyl electrical and plumbingnoing"*. Its prompt described the figure in words. The gate
that checks that figure's arithmetic, `f5`'s C6 arm, **still passed** - because it reads the plotting
script, not the shipped PNG.

---

## Contents

**Schematics** - safe to generate from prose

- `Figure_01_pipeline_4split.md` · `Figure_02_three_leg_roadmap.md` · `Figure_03_three_head_transformer.md`
- `Figure_04_exclusivity_projection.md` · `Figure_05_hotel_sidetrack.md` · `Figure_06_tag2_dispatch.md`
- `Figure_S02_scenario_levers.md` · `Figure_S03_leg2_pipeline.md` · `graphicalAbstract.md`

**Data figures** - the prompt carries the series

- `Figure_07_longitudinal_4ch.md` - 32 values, two panels, four eras
- `Figure_08_eui_4ch.md` - four box summaries plus three reference bands. **Three of the paper's four
  failing gates are read off this figure.** Never widen a band to make a box fit.
- `Figure_09_diurnal_4ch.md` - 288 hourly values, six channels, two seasons
- `Figure_10_peakhour_4ch.md` - all 224 per-cell peak hours. **The abstract quotes this figure.**
- `Figure_11_scenario_4ch.md` - 36 values; the **sign** of each is the finding
- `Figure_S01_occupiable_shares.md` - 🔴 **RETIRED as a generation prompt on 2026-08-11. Do not paste
  it into an image tool.** S1 is now plotted by `writing/figures/SI/figS01_shares.py`. The file is kept
  only so the two failures remain reproducible: the generated versions labelled the two bar totals
  `4.0.1` / `0.37` and then `3,610` / `2,071`, and all four are wrong against
  `writing/tables/SI/Appendix_C_corrections.md` C.1 (gross **135,857.6 / 72,623.1 m2**, occupiable
  **107,816.0 / 57,075.4 m2**). The prompt's own text says to keep the numbers out of the image; the
  generator drew invented ones anyway, both times.

---

## 🔴 The convention that never worked: "Annotations to overlay afterward"

Every schematic prompt in this folder has a section headed **"Annotations to overlay afterward (exact
text/numbers -- keep OUT of the AI image)"**. It was written to stop image models garbling digits.
What it actually did was guarantee the digits are missing, because **the overlay step has never been
performed, on any figure, once**. The generator is told not to draw the value; nobody draws it later;
the figure ships with a placeholder.

Three shipped figures are empty in exactly this way:

- **Figure 4** -- the "raw / after projection" panels are two blank rectangles. The ISR values
  (`<= 0.5%` and `0%`) were in the overlay section.
- **Figure 6** -- the Hard Wiring Gate card has a tick beside a blank pill and a cross beside a blank
  pill. The two field names, which are the entire content of that card, were in the overlay section.
- **Figure S2** -- three sliders ticked `low / default / high`. The nine real lever values were in the
  overlay section.

**Rule, 2026-08-11: if a specific string is the reason an element exists, that string goes inside the
fenced block.** The overlay section is for provenance and long-form caption text only -- never for a
value the artwork is built around. The four prompts above were rewritten accordingly.

This is the same failure as the S1 `4.0.1` case one level up: there the tool invented a number it was
not given; here it drew an empty box instead. Both come from a prompt that withholds the content.

---

## Known defects in the images currently installed

| figure | defect | state |
|---|---|---|
| ~~**S1**~~ | ~~`4.0.1` as a share, no axis, garbled footnote~~ | 🟢 **FIXED 2026-08-11.** No longer generated. Re-plotted by `writing/figures/SI/figS01_shares.py` from `writing/tables/SI/Appendix_C_corrections.md` C.1, at 3744 x 3016 px (**535 dpi** at 7 in). All five channel shares now carry their value, including retail and residential-common, which the pre-2026-08-09 matplotlib version left blank because they are too thin to hold a label inside the bar. **This figure is no longer a prompt-and-generate figure -- do not regenerate it.** |
| **4** | the lower "raw / after projection" panel renders as two empty boxes; and the one-hot cluster draws a partly-filled bar, which is the state the projection exists to remove | prompt rewritten 2026-08-11, values moved inside the fence; **regeneration required** |
| **6** | the "Hard Wiring Gate" box has two blank grey label bars | prompt rewritten 2026-08-11, field names moved inside the fence; **regeneration required** |
| **1** | **twelve boxes for nine steps.** STEP 5, STEP 6 and STEP 7 each drawn twice; `End-Use Loads` drawn twice; one box carries a number and an icon and no title; STEP 4 placed after STEP 7; the side-track lane wraps around three main-chain boxes | prompt rewritten 2026-08-11 with an explicit count rule and a no-wrap rule; **regeneration required** |
| **S2** | three sliders ticked `low / default / high` -- none of the nine real lever values appear | prompt rewritten 2026-08-11; **regeneration required** |
| **graphical abstract** | the peak-hour panel is headed "Four different hours" and draws the four peaks evenly spread, residential ~09:00 before office ~12:00. §5.3 and Figure 10 give office/residential/retail between **11.90 and 12.37 h** and hotel at **18.91 h**: three coincide, one does not, and residential peaks fractionally *after* office | prompt rewritten 2026-08-11 with the five peak positions fixed on the axis; **regeneration required** |
| **S3** | 32% of the frame is empty white above the diagram | content is correct; **crop and re-render only** |
| **all nine schematics** | 1376 x 768 px, about **197 dpi** at a 7 in printed width, against Elsevier's **500 dpi** for combination art | unchanged by the 2026-08-11 round; three files declare `300` dpi in `pHYs` while still being 1376 x 768, which adds no pixels. The eleven plotted figures are 3744 to 6597 px |
| **1 to 6, S2** | no vector PDF any more - the stale matplotlib PDFs were archived rather than left to disagree with the new PNGs | `../archive/superseded_matplotlib/` |

---

## Reinstalling, and one trap

The install is scripted and idempotent: copy each `.png` here over its counterpart in **both**
`writing/figures/` and `writing/submission/figures/`, then rebuild.

🔴 **Do not run `f5_figure_check.py` after installing without re-installing afterwards.** Its C2
determinism arm **re-runs every figure script, which writes to the real output path**, and it will
silently put the matplotlib artwork back and regenerate the deleted PDFs. On 2026-08-09 it reported

```
fig01_pipeline.py: md5 changed on re-run (b3eea0a9 -> d09d7b8d) -- NOT deterministic
```

which is not a determinism finding at all: `b3eea0a9` was the generated image and `d09d7b8d` is
matplotlib's. The gate was reporting that it had just overwritten the file. `f6` was checked the same
way and is genuinely read-only.

Always verify against the **installed** `.docx`, never the pandoc output.
