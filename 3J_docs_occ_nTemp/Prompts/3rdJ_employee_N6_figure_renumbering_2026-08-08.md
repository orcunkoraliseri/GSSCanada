# Employee task N6 - renumber the figures into reading order

**You are the employee. Execute the task below and append a Progress Log entry on completion.**
Model: Sonnet. Working root: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\`.
Read `CLAUDE.md` at the repo root first. Reply in English. This task touches **only** figure
numbering. Do not fix anything else you notice - write it at the bottom of the Progress Log instead.

---

## Aim

All 15 figures are placed in the text, but two pairs were numbered before their placements were
known, so the assembled document runs `1 2 3 4 6 5 S1 S2 10 7 8 9 11 S3`. Renumber so caption order
equals numeric order. **Nothing else in this round may edit a chapter until this lands**, because
this rewrites captions and prose references across Chapters 3 and 5.

## The permutation

| current | becomes | figure | placed at |
|---|---|---|---|
| 6 | **5** | hotel side-track | `Chapter_03_Methods.md:175` |
| 5 | **6** | tag-2 dispatch | `Chapter_03_Methods.md:224` |
| 10 | **7** | longitudinal | `Chapter_05_Results.md:51` |
| 7 | **8** | per-channel EUI | `Chapter_05_Results.md:99` |
| 8 | **9** | diurnal | `Chapter_05_Results.md:134` |
| 9 | **10** | peak hour | `Chapter_05_Results.md:137` |

Figures 1, 2, 3, 4, 11, S1, S2, S3 and the graphical abstract **do not move**.

🔴 **This is a permutation, not a shift. Rename through temporary names** (`Figure_05_*` ->
`__tmp_05_*` -> `Figure_06_*`) or you will overwrite a file you still need.

## Asset inventory, measured on disk 2026-08-08 - do not assume symmetry

- `writing/figures/`: figures **1-6** each have `.png`, `.pdf` **and** a prompt `.md`.
- `writing/figures/`: figures **7-11** have **`.png` only** - no `.pdf`, no prompt `.md`.
- Generator scripts are named by topic, not by number: `fig05_tag2dispatch.py`,
  `fig06_hotel.py`. **Their filenames encode the old numbers and must be renamed too**
  (`fig05_tag2dispatch.py` -> `fig06_tag2dispatch.py`, `fig06_hotel.py` -> `fig05_hotel.py`),
  along with every reference to them inside `make_all_figures.py` and the output paths written
  inside each script.
- `writing/figures/SI/` is untouched by this task.

## Steps

1. **Archive first.** Copy every file you are about to modify to its sibling `archive/`
   (chapters and tables already have one; create `writing/figures/archive/` if absent) with the
   suffix `.2026-08-08_pre_figure_renumber`. Corrections in this project are additive.
2. **Enumerate the ground truth yourself before editing.** Run, from `3J_docs_occ_nTemp/writing`:
   `grep -rn "Figure S\?[0-9]\+" chapters/Chapter_0[1-8]*.md`
   You should get **16** hits: 15 caption placeholders and **exactly 2 in-prose references**
   (`Chapter_01_Introduction.md:43` -> Figure 1, unchanged; `Chapter_05_Results.md:49` ->
   "Section 5.2 (Figure 7)"). If you get a different count, **stop and report** - the manuscript
   moved under this prompt. Do **not** search `chapters/archive/` or `tables/archive/`; those are
   frozen and must keep their old numbers.
3. 🔴 **`Chapter_05_Results.md:49` is the one prose reference that changes.** It reads
   "verdicts in Section 5.2 (Figure 7)." Section 5.2's figure is the per-channel EUI figure, which
   becomes Figure **8**. So this line becomes "(Figure 8)". Getting this wrong by applying the
   mapping backwards is the single most likely failure of this task - the sentence names a
   *section*, and the section does not move.
4. Rename the assets (png, pdf, prompt md, generator py) via temporary names.
5. Update, in this order: generator scripts' internal output paths -> `make_all_figures.py` ->
   the prompt `.md` files -> the caption placeholder lines in the chapters -> the one prose
   reference in step 3.
6. **Regenerate the moved figures** with `PYTHONIOENCODING=utf-8 py -3 writing/figures/make_all_figures.py`
   and confirm each renamed `.png`/`.pdf` is rewritten by its renamed script (mtime changes).
   `py -3` is the only working Python invocation here.
7. **Rebuild:** `PYTHONIOENCODING=utf-8 py -3 writing/fullSet/assemble_3J.py`.
   Note the output layout changed on 2026-08-08: `fullSet/` holds **one final document**,
   `readySubmission.md`; the working draft is now written to `fullSet/previous/3J_full_manuscript.md`.

## Expected result

- Assembled figure order is `1 2 3 4 5 6 S1 S2 7 8 9 10 11 S3`.
- `figures inlined at a placeholder: 15`, `figures appended to the appendix: 0` in the build output.
- The leftovers appendix is still empty.
- No file named with an old number survives outside `archive/`.

## Test method - all four, at closure, not at authoring

1. `grep -o "Figure S\?[0-9]\+" writing/fullSet/readySubmission.md | uniq` in file order must print
   the expected sequence above. **A grep whose exit code you did not read is not a check** - in an
   earlier round three readers reported "zero em dashes" from a `grep -P` that had exited 2 while
   96 dashes were present. Print the exit code.
2. `PYTHONIOENCODING=utf-8 py -3 writing/implementation/f5_figure_check.py` and
   `f4_prose_rules_check.py`. Record every arm's verdict, before and after, in the Progress Log.
   **`f5` arm C7 reads `Table_06_leg2_leg3_delta.md` from disk and will fail any figure asserting
   bit-identity for a non-affirmative step - if it fires, stop and report; do not edit Table 6.**
3. Confirm every renamed `.png` referenced by a caption actually exists on disk (a caption
   pointing at a missing file assembles fine and fails silently at the placeholder).
4. **Loss check:** the build prints a caption count before and after the strip. Confirm all ten
   `**Table N.**` captions and all fifteen `**Figure N.**` captions survive. A residue check and a
   loss check are different checks; this project has already lost a caption to that distinction.

## Progress Log

Append to `writing/implementation/3rdJ_paper_TASKS.md` under a new `## N6 - figure renumbering`
heading: what you renamed, the before/after grep sequences with exit codes, the f4/f5 arm verdicts
before and after, and anything you noticed but deliberately did not fix.
