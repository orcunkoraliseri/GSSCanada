# RESUME - start a 3J session here

**Last updated: 2026-08-09, end of the generated-images round.**

This file is the thirty-second orientation. **The full handoff is the file beside this one**, kept
current every round at a fixed path that never moves:

> ### `3rdJ_employee_N6_figure_renumbering_2026-08-08.md`
>
> Read it. The name is wrong and is deliberately kept wrong - the author pointed at that path, so the
> path is load-bearing. It opens with a twelve-entry table of contents and carries every completed
> round, every standing hazard, and the work that is left.

The previous contents of this file - the Leg-2 two-channel simulation runbook, including the v24.2
`Zone_or_ZoneList_Name` office-WFH bug write-up - are preserved at
`archive/RESUME.2026-08-09_pre_rewrite_leg2_runbook.md`. That campaign is finished and superseded by
Leg-3; nothing in it should be executed.

---

## Where the project is, in five lines

- **The 3J paper is written, built, rendered and gate-clean.** It is not submitted.
- **Target venue: Building and Environment (Elsevier)**, reconfirmed by the authors 2026-08-09, which
  made three commitments binding (uninjected control leads the cover letter · abstract opens on the
  behavioural claim · the §1/§6.1 pass stands).
- **This is a WRITING phase. Zero simulation.** No `sbatch`, no cells, no re-runs.
- **Three open BUILD NOTES block submission.** The build prints them on every run.
- 2J was submitted to Building Simulation on 2026-08-07 and is frozen pending its decision letter.

## The three things that block submission

1. **Table A2 ships unlabelled and uncited** - a build-mechanism defect. The authors choose between
   splitting it into its own SI table or folding it into the model card. `f4`'s C7 is structurally
   blind to it.
2. **Kurin et al. 2022 and Menon et al. 2020 have never been opened.** Needs a `V<NN>` prompt the
   author runs externally. **Do not search from the session.**
3. **The generated-image defects** - see below.

## What happened on 2026-08-09, because it changes how figures work now

The author generated images from prompts and asked for them to replace the matplotlib figures.

- 🔴 **A new hard rule was written into `CLAUDE.md` and `README.md`: the assistant NEVER creates
  images.** It writes the prompt; the author generates; the assistant installs, verifies and audits.
  **Plotting is not drawing** - a matplotlib figure rendered from a frozen aggregate is computation
  and stays with the assistant.
- **Nine schematics and the graphical abstract were swapped in** at 1376 x 768 px, which is about
  184 dpi at page width against Elsevier's 500. Three of them carry visible defects, including a
  **Figure S1 that labels a share `4.0.1`** with a garbled footnote. All of it is in one open BUILD
  NOTE at that figure's caption.
- 🔴 **Three generated results figures were NOT installed, and must not be.** Figures 7, 8 and 9 came
  back with invented numbers. Figure 8 is the worst: it draws office and hotel comfortably inside
  bands the paper reports them **failing**, which reverses three of the paper's four headline gate
  verdicts. They are quarantined at
  `writing/submission/figures/archive/generated_NOT_INSTALLED_data_figures/`. The shipped Figures 7
  to 11 are still the correct 600 dpi plots.
- **Every image in the manuscript now has a prompt** at `writing/submission/figures/Prompts_Images/`,
  fifteen of them, and the six data prompts carry their measured series in tables with the source
  file, column and line named.

## Two traps that cost real time this round

- 🔴 **`f5_figure_check.py` is not read-only.** Its C2 determinism arm re-runs every figure script and
  those scripts **write to the real output paths**, so running it silently reverts a figure install
  and regenerates deleted PDFs. Its `md5 changed on re-run` line was the gate reporting its own write.
  `f6` was checked the same way and is genuinely read-only.
- **A check that validates the generator is blind to a substituted artefact.** `f5`'s C6 certified
  Figure S1's arithmetic - from the plotting script - while the shipped PNG said `4.0.1`.

## The build, and how to rebuild

From `3J_docs_occ_nTemp/`:

```
py -3 writing/fullSet/assemble_3J.py
cd writing/submission
sed 's|\.\./figures/|figures/|g' ../fullSet/readySubmission.md > 3J_manuscript_submission.md
pandoc 3J_manuscript_submission.md -o raw.docx --reference-doc=extra/build_scripts/ref_submit_single.docx --resource-path=.
py -3 extra/build_scripts/post.py raw.docx 3J_manuscript_submission.docx
```

Gates: `f3` 4 PASS / 1 FAIL (**correct, do not modify `f3`**) · `f4` 7/0 · `f5` **5 PASS / 2 FAIL**
(correct since the image swap - the vector PDFs are gone on purpose and the scripts no longer
reproduce the artwork) · `f6` 5/0.

**Always verify the INSTALLED `.docx`, never the pandoc output.** In the 2J round a table column had
silently vanished from the shipped file.

## Hard rules that outlive any round

1. **NEVER** run a blocking `srun`, or any Python, on the Speed login node `speed-submit2`. Always
   `sbatch`. Flagged three times; one more is account suspension. (Irrelevant during the writing
   phase, and that is exactly when it gets forgotten.)
2. **Deep research is external.** Author the prompt; never run the search. Roughly half the citations
   in the returned reports have been fabricated.
3. **The assistant never creates images.** See above.
4. **Archive the predecessor before editing.** Corrections are additive.
5. **Never edit a built artefact by hand.** Changes go into the sources or the build, then get
   verified against the installed file.
6. **No band moves, no gate verdict changes, no measured number changes.** The three failing EUI
   gates stay failing; that is the paper's contribution.
7. **Do NOT tick Gold open access** on the CRKN waiver claim. $3,690 USD, irreversible, same shape as
   the claim that was wrong for 2J.
8. Reply in English; the author writes in French.

## The closure ritual, every round, unprompted

Progress Log in `writing/implementation/3rdJ_paper_TASKS.md` · **the manager prompt edited in place**
at its fixed path, predecessor archived first · the board republished at
<https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213> · memory updated.
