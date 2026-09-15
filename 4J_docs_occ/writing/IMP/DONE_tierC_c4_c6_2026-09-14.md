# Tier C figure repair - C4 (Figure 7) and C6 (graphical abstract) - 2026-09-14

Scope: `4J_docs_occ/writing/submission/figures/` only. Two scripts touched:
`scripts/generate_fig07.py` (one substitution applied) and
`scripts/generate_graphical_abstract.py` (read only, zero edits - defect does not reproduce).
`4J_manuscript_submission.md` / `4J_supplementary_material.md` were opened only with `sed -n`, never written.

## Backup

`figures/previous/scripts_bak_pre_tierC_20260914/` created before any edit, holding byte-identical
copies of both scripts, verified non-empty (`generate_fig07.py` 8140 bytes, `generate_graphical_abstract.py`
18371 bytes - same sizes as the live files at that moment).

## C4 - Figure 7 (`scripts/generate_fig07.py`)

### Part 1 of the recorded defect: "four labels rounded against a specification that forbids rounding"

**Does not reproduce.** The live script already prints every Table-10-sourced value at full frozen
precision:

- Panel A peak effect: `f"{pe:+.4f} %"` -> `+2.7145 %`, `+0.0393 %`, `-0.6332 %`
- Panel A between-diary spread: `f"{sp:.4f}"` -> `4.9837`, `2.3797`, `1.5959`
- Panel B1 annual median: `f"{val:.4f} %"` -> `-1.5100 %`, `-0.3605 %`, `-0.4178 %`
- Panel A ratio (`f"{rat:.2f}"`, 2 dp) and Panel B2 apartment-building effect (`f"+{val:.2f} %"`, 2 dp)
  are printed at exactly the precision the spec itself gives for those two quantities
  (`Prompts_Images/4thJ_figure07_heating_null.md:47` - "Print the ratio beside each pair: **0.54**,
  **0.02**, **0.40**"; `:69-70` - "**+3.46 %**, **+1.04 %**, **+0.50 %**"), so 2 dp there is not rounding
  away from the source, it *is* the source.

A comparison against `figures/previous/scripts_pre_recolour_2026-09-14/generate_fig07.py` (an older,
already-superseded copy, not part of this task's scope) shows the rounding this defect description refers
to: that older script printed Spain/Italy peak effect and all three spreads at 2 dp (`{pe:+.2f}`,
`{sp:.2f}`). A prior pass ("second pass, author request", see the live script's own header comment)
already replaced those with the 4 dp forms above before this task started. Verified by re-running the
script (see stdout below): the overflow check that this fix required (longer 4 dp strings could collide)
passes clean. No change made; recorded as non-reproducing.

Specification clause relied on: `Prompts_Images/4thJ_figure07_heating_null.md:11-13` -
"**No value in this prompt may be altered.** ... No value may be rounded, re-signed, re-scaled or
averaged," sourced from `4J_manuscript_submission.md:872-879` (Table 10, read with `sed -n` only).

### Part 2 of the recorded defect: "Panel B2 says 'Peak' where the text does not"

**Reproduces - fixed.** Table 10 (`4J_manuscript_submission.md:872-879`) only labels the row "Peak
effect" for Panel A's per-country peak-vs-spread comparison. The apartment-building numbers Panel B2
draws are never called "peak" anywhere they are defined:

- Spec: `Prompts_Images/4thJ_figure07_heating_null.md:69` - "B2, the surviving ordering. Three bars, one
  per fold, giving the **apartment-building effect**, which is the largest dwelling class everywhere."
- Manuscript prose: `4J_manuscript_submission.md:925-926` - "Panel B2 gives **the effect on apartment
  buildings**, the largest of the three dwelling classes in every fold."

Only the script's y-axis label used the word "Peak": `ax_b2.set_ylabel("Peak heating effect (%)", ...)`.
The panel title ("Panel B2: The surviving ordering (apartment buildings)") already matched the spec and
was left untouched.

**Substitution applied** (guarded `s.count(old) == 1` pattern, `py -3`):

```
old: ax_b2.set_ylabel("Peak heating effect (%)", fontsize=9, labelpad=6)
new: ax_b2.set_ylabel("Apartment-building effect (%)", fontsize=9, labelpad=6)
```

No plotted value, colour, size, or any other string was touched.

### Verification

```
py -3 -m py_compile generate_fig07.py   -> exit 0, no output (compiles)
py -3 generate_fig07.py                 -> stdout:
    no text overflows its element
    Generated Figure 7: C:\Users\o_iseri\...\Prompts_Images\Figure_07_heating_null.png (270785 bytes)
```

PNG dimensions (`Figure_07_heating_null.png`, PIL `Image.size`):
- Before: `(3600, 2550)`
- After:  `(3600, 2550)` - unchanged.

All three output copies regenerated together in one run: `figures/Figure_07_heating_null.png`,
`figures/Prompts_Images/Figure_07_heating_null.png`, `figures/Prompts_Images/4thJ_figure07_heating_null.png`
(all 270785 bytes, same run).

## C6 - Graphical abstract (`scripts/generate_graphical_abstract.py`)

**Does not reproduce. No edit made.**

Repo-wide grep inside `4J_docs_occ` for `"One Recipe, Many Countries"` returns only: the current
`Prompts/RESUME.md` and its `previous/*.bak_*` history, two `writing/IMP/*.md` planning docs, and the
`Prompts_Images/4thJ_graphical_abstract.md` text-inventory spec (plus its own backups). It does not
appear in the manuscript or the supplementary material (`grep` against both returned no match).

Critically, it also does not appear in the live generator script or the live PNG. `generate_graphical_abstract.py`
is a from-scratch matplotlib rebuild, dated 2026-09-14, whose own docstring says it was "built in code
... after four generator rounds failed" (referring to an earlier, now-abandoned external-image-generation
workflow that *did* follow the `4thJ_graphical_abstract.md` prompt, including its "One Recipe, Many
Countries" subtitle line). The code script never uses that phrase anywhere (`grep -in "recipe\|countries"`
checked). Its actual title block (`generate_graphical_abstract.py:65-70`) is:

```
line 65-66: "Cross-National Occupancy Generation with a Fine-Tuned Open-Weight LLM"   (main title, 22pt bold)
line 67-70: "Beaten by Real Diaries: A Pre-Registered Leave-One-Country-Out Test of a Fine-Tuned
             Language Model for Cross-National Occupancy Generation (HETUS; Spain, Italy, United Kingdom)"
             (subtitle, 14pt)
```

Both strings are quoted verbatim from the manuscript's own title
(`4J_manuscript_submission.md:1`, read with `sed -n` only). This already satisfies the task's own
preferred fix ("prefer a phrase that already appears in the manuscript's title or abstract") and makes
no claim about country count, so nothing about a three-country corpus is misstated. Visually confirmed
by opening the live PNG (`figures/HETUS_LLM_CrossNational_Pipeline.png`, 3937x1525): the subtitle reads
"Beaten by Real Diaries: ..." with no occurrence of "One Recipe, Many Countries" or "Many Countries"
anywhere in the image.

Because no edit was made, the script was not re-run; the live PNG on disk (last generated 2026-09-14
16:37, same run that produced the current script) is left as-is per the "never re-run a script you did
not edit" implication of the task's own guarded-edit workflow.

Stale reference not touched (out of scope, flagged only): the `4thJ_graphical_abstract.md` text-inventory
spec still names "One Recipe, Many Countries" as its mandated subtitle (its own Section 6, e.g. line 437),
and `Prompts/RESUME.md` / the two `writing/IMP/*.md` planning docs still refer to that same old string.
None of these are figure scripts and are outside this task's edit scope (only the two named `.py` files
were authorised); they are left for whoever owns the spec/planning docs to reconcile with the now-live
code-built abstract.

## Summary of what was NOT changed, and why

- Fig 7 Panel A / B1 numeric labels (peak effect, spread, ratio, annual median): already correct
  precision, matching the spec's own stated precision for each quantity. No rounding defect present.
- Fig 7 Panel B2 numeric labels (`+3.46 %`, `+1.04 %`, `+0.50 %`): 2 dp is the spec's own literal
  precision for this quantity, not a rounding of a more precise frozen value. Left unchanged.
- Fig 7 Panel B2 title ("The surviving ordering (apartment buildings)"): already matches the spec's own
  naming. Left unchanged.
- Graphical abstract script: contains no "One Recipe, Many Countries" text anywhere; already uses the
  manuscript's own title/subtitle. Left unchanged, script not re-run.
- `Prompts_Images/4thJ_graphical_abstract.md` and the various `Prompts/RESUME.md` / `writing/IMP/*.md`
  references to "One Recipe, Many Countries": out of scope (not a `.py` figure script), left untouched.
- `4J_manuscript_submission.md`, `4J_supplementary_material.md`: opened only with `sed -n` to read Table
  10 and the manuscript title/abstract; never written, per hard rule.
- House palette: not touched in either script (no colour lines were part of either recorded defect).
