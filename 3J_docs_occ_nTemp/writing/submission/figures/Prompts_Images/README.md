# Image prompts for every figure in the 3J manuscript

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
- `Figure_S01_occupiable_shares.md` - the prompt as originally written, kept so the failure above is
  reproducible. It needs the shares written into it before it is used again.

---

## Known defects in the images currently installed

| figure | defect | state |
|---|---|---|
| **S1** | `4.0.1` as a share, no axis, garbled footnote | recorded as an open BUILD NOTE at its caption in `Chapter_04_ExperimentalDesign.md` |
| **4** | the lower "raw / after projection" panel renders as two empty boxes | same note |
| **6** | the "Hard Wiring Gate" box has two blank grey label bars | same note |
| **all nine** | 1376 x 768 px, about **184 dpi** at 190 mm page width, against Elsevier's **500 dpi** for combination art | same note; the files they replaced were 5400 to 6600 px |
| **1 to 6, S1, S2** | no vector PDF any more - the stale matplotlib PDFs were archived rather than left to disagree with the new PNGs | `../archive/superseded_matplotlib/` |

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
