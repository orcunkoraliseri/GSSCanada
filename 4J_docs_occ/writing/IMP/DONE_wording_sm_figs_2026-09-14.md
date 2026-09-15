# Wording pass: fail -> limitation, supplement + figure scripts (2026-09-14)

Scope per author ruling (2026-09-14, verbatim): "keep everything as it is, but instead of 'fail' or
'failure' use the word of 'limitation'." Gate verdict tokens (`FAIL`/`PASS`) and code identifiers stay
verbatim. Two targets only: `4J_supplementary_material.md` and `figures/scripts/*.py`.
`4J_manuscript_submission.md` was not opened (another agent owns it).

## Backups
- `previous/4J_supplementary_material.md.bak_pre_wording` (15,059 bytes, matches pre-edit size)
- `figures/previous/scripts_bak_pre_wording_20260914/` (all 8 scripts + `__pycache__`)

## Every hit found in `4J_supplementary_material.md` (grep -n -i, 34 lines)

| Line | Text (pre-edit) | Class | Action |
|---|---|---|---|
| 8 | "three of this study's reported **failures** are **failures** of a band rather than of a model" | PROSE | changed: failures -> limitations (both) |
| 24-27, 28, 32, 38-40, 42-43, 54, 56, 64, 67-69, 71-75, 77, 84, 87 | uppercase `FAIL` verdict tokens in table cells / counts | GATE TOKEN | kept verbatim |
| 88 | `FAIL, 0.0570; also **fails** at 0.0511 on a permuted adapter` | mixed: token `FAIL` kept, prose "fails" changed | changed "also fails" -> "also misses the bar" |
| 91 | "This board ships two registered **failures** and one partial." | PROSE | changed: failures -> limitations |
| 94 | "### S1.6 Three bands that **failed** for reasons that are not about the model" | PROSE (heading) | changed: "that failed" -> "that miss the bar" |
| 96 | "Three of the training-stage **failures** are properties of their own checks" | PROSE | changed: failures -> limitations |
| 109-110 | "The check **fails** against a bar that nothing justifies, and it is reported **failing** with that stated rather than adjusted." | PROSE | changed: "fails" -> "does not clear", "reported failing with that stated" -> "reported as not clearing it, with that stated" |
| 120 | "**One check ships failing without ever having been adjudicated.**" | PROSE (bold lead sentence) | changed: "ships failing" -> "ships short of its bar" |

28 uppercase `FAIL` tokens total; all 28 kept untouched (see count check below).

## Exact substitutions applied (via guarded python patch, `py -3`)

1. `...three of this study's reported failures are failures of a band...` -> `...three of this study's reported limitations are limitations of a band...`
2. `This board ships two registered failures and one partial.` -> `This board ships two registered limitations and one partial.`
3. `### S1.6 Three bands that failed for reasons that are not about the model` -> `### S1.6 Three bands that miss the bar for reasons that are not about the model`
4. `Three of the training-stage failures are properties of their own checks, and this study reports them as` -> `Three of the training-stage limitations are properties of their own checks, and this study reports them as`
5. `The check fails against a bar that nothing\njustifies, and it is reported failing with that stated rather than adjusted.` -> `The check does not clear a bar that nothing\njustifies, and it is reported as not clearing it, with that stated rather than adjusted.`
6. `**One check ships failing without ever having been adjudicated.**` -> `**One check ships short of its bar, without ever having been adjudicated.**`
7. `FAIL, 0.0570; also fails at 0.0511 on a permuted adapter` -> `FAIL, 0.0570; also misses the bar at 0.0511 on a permuted adapter`

All 7 anchors matched exactly once (`s.count(old) == 1` assertion held for every pair, no loosening needed).

Post-edit re-grep for lowercase fail-family words (`grep -n -E "fail(s|ed|ing|ure|ures)?" | grep -v FAIL`)
returned zero hits: no prose "fail" wording remains anywhere in the file.

### Uppercase FAIL count (registered gate tokens)
- Before: 28 (`grep -o "FAIL" 4J_supplementary_material.md | wc -l`)
- After: 28 (identical)

### Line count
- Before: 223 lines
- After: 223 lines (unchanged; no rewrap needed)

## Figure scripts (`figures/scripts/*.py`)

Grepped all 8 scripts (`-n -i -E "fail(s|ed|ing|ure|ures)?"`):

| File | Line | Text | Class | Action |
|---|---|---|---|---|
| generate_fig01_pipeline.py | 5 | docstring: `("ok if possible you create these failed images")`, `"after four generator rounds failed to clear"` | CODE COMMENT / direct quote of author, not reader-facing (build-history docstring, never rendered) | left alone |
| generate_fig01_pipeline.py | 106 | rendered card body string `"three gates ship as declared failures"` | PROSE, reader-facing (drawn on the figure) | changed -> `"three gates ship as declared limitations"` |
| generate_fig02_loco.py | 5 | docstring: `"rounds failed on the one thing the figure exists to prove"` | CODE COMMENT, not reader-facing | left alone |
| generate_fig03.py, fig04, fig06, fig07 | -- | no hits | -- | -- |
| generate_fig05.py | 80 | rendered xlabel string `"...Anything to the right of it fails.)"` | PROSE, reader-facing | changed -> `"...Anything to the right of it does not clear it.)"` |
| generate_graphical_abstract.py | 5 | docstring: `"rounds failed on the one thing the picture must say"` | CODE COMMENT, not reader-facing | left alone |

Left alone, with reason: the three docstring occurrences (fig01 line 5, fig02 line 5, graphical-abstract
line 5) are build-history comments describing prior failed generator attempts, including one verbatim
quotation of the author's own instruction. They are never drawn into the rendered PNG and are not part of
"the document" a reader sees, so they fall outside the scope of "caption / title / label / annotation
strings" the ruling targets. Also flagged: `generate_fig01_pipeline.py`'s own docstring asserts "EVERY
string drawn here is copied verbatim from the frozen TEXT INVENTORY of
`Prompts_Images/4thJ_pipeline_steps_figure.md` Section 11" (and `generate_fig02_loco.py` / graphical
abstract make the equivalent claim about their own frozen TEXT INVENTORY files). Changing the rendered card
text now makes it diverge from those frozen inventory files by one word each; those inventory `.md` files
are outside this task's two named targets and were not touched, so the divergence is unresolved.

### Word-count guard check (`generate_fig01_pipeline.py`)
`WORDCOUNTS[9] = [3, 6]` requires card 9's second body line to be exactly 6 words.
"three gates ship as declared failures" = 6 words; "three gates ship as declared limitations" = 6 words.
Count preserved exactly, no layout change needed.

## Re-run output of every figure script touched

```
=== fig01 run ===
no text overflows its element
written C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\HETUS_LLM_Pipeline_Steps.png 4440 x 1620

=== fig05 run ===
Generated Figure 5: C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\writing\submission\figures\Prompts_Images\Figure_05_joint_structure.png (238771 bytes)
```

Both scripts also passed `py -3 -m py_compile` (syntax check) before running.

### PNG dimensions, before vs after
- `HETUS_LLM_Pipeline_Steps.png`: before 4440 x 1620 -> after 4440 x 1620 (unchanged)
- `Figure_05_joint_structure.png` (all three copies: `figures/`, `figures/Prompts_Images/`,
  `figures/Prompts_Images/4thJ_figure05_joint_structure.png`): before 3600 x 2100 -> after 3600 x 2100
  (unchanged)

fig06, fig03, fig04, fig07, graphical_abstract were not touched (no prose fail-hits in reader-facing
strings) and were not re-run.

## Things left alone, with reason
- Three build-history docstrings (`generate_fig01_pipeline.py:5`, `generate_fig02_loco.py:5`,
  `generate_graphical_abstract.py:5`) - code comments, not rendered to a reader, one contains a verbatim
  quote of the author's own words.
- All 28 uppercase `FAIL` gate-verdict tokens in the supplement - registered definitions, explicitly
  exempted by the ruling.
- The three frozen TEXT INVENTORY `.md` files referenced by the three figure-script docstrings now
  disagree with their scripts by one word each (`failures`/`fails` -> `limitations`/`does not clear`) -
  out of this task's scope (not one of the two named targets), flagged for the author's attention rather
  than fixed.
