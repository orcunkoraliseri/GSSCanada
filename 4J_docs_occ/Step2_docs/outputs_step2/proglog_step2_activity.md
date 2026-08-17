# Progress log fragment -- Step 2 activity crosswalk (work item 2.1, D-S2-11, D-S2-7, D-S2-10)

This is a fragment for the manager to merge into `4thJ_02_harmonisation.md`'s Progress Log. It is not
appended to that file directly.

## What was built

Four files were produced under `outputs_step2/`, all UTF-8, all cited to the delivered codebooks.

`activity_target_list.csv` holds **158 target codes**, built by the D-S2-11 rule: a code enters the
list if it appears in the Spanish 116-code list, the Italian 146-code list, or both, with Spanish and
Italian judged for agreeing meaning code by code. Of the 158 targets, **86 are two_source** (Spain and
Italy agree), **17 are conflict_resolved** (Spain and Italy both carry the code but disagree, resolved
explicitly and recorded), and **55 are single_source** (13 from Spain only, 42 from Italy only). Every
target code is a 3-character, all-digit string; `level1` and `level2` are read off the first one and
two characters of `target_code`, never authored separately.

`crosswalk_activity.csv` holds **531 rows**: 114 of Spain's 116 codes, 144 of Italy's 146, and 273 of
the UK's 277. The remaining 8 source codes (2 Spanish, 2 Italian, 4 British) are listed in
`crosswalk_unmapped_activity.md` with a named reason each, never silently dropped. Sixteen rows are
flagged `ambiguous=1` with a written rule: two Spanish rows and fourteen British rows. The UK column is
not vacuous -- most of its 277 codes are ordinary many-to-one granularity mappings (not ambiguous by
the task's own definition), but a genuine minority, chiefly the UK's own top-level "unspecified X"
catch-alls and its dependent/non-dependent adult-help split, spanned more than one candidate target and
needed a picked-by-rule choice.

`crosswalk_activity_secondary.csv` holds **421 rows**: 114 Spanish rows (mirroring the 114 mapped
primary Spanish rows, truncated to 2 digits, `source_list=Lista EET`), 273 British rows (mirroring the
273 mapped primary British rows, truncated, `source_list=NATCEN Appendix H`), and 34 Italian rows built
independently from `crosswalk_source_italy_activity2.csv` (`CLS-var13`), mapped to a target level-2
group by meaning, never by number, per F-IT-3's warning that `catcon` is not a truncation of `catpri`.

`crosswalk_unmapped_activity.md` carries all six required headings, none empty: 8 unmapped source
codes, 17 Spain-Italy conflicts with both labels, both citations and a resolution, one group-header row
(Italy's code 90), the 55 single-source target codes listed out, the 16 ambiguous rows with their
rules, and a COUNTS table printed per country before any verdict.

All seven self-checks specified in the task were run with `py` and the stdlib `csv` module, none by
hand-counting, and re-run after the correction described below. Results: (1) mapped+unmapped equals the
source count exactly for all three countries (114+2=116, 144+2=146, 273+4=277); (2) 0 rows with an
empty `source_citation`; (3) 0 `target_code` values in the crosswalk missing from the target list; (4) 0
target codes that are not exactly three digits; (5) 0 `ambiguous=1` rows with an empty `rule`; (6) the
G2.15 pre-check (Spain and UK secondary rows must agree with the primary crosswalk on the same code,
truncated) found 0 disagreements across 387 checked rows; (7) the G2.13 pre-check (no Italian secondary
code resolvable through the primary crosswalk) found 0 overlaps. All seven numbers were zero.

## A correction made after manager review: Spain's lunch break was not treated like the UK's

The manager's review caught a real inconsistency before this fragment was first written, and it is
recorded here rather than folded in silently. My first pass mapped the UK's code `1310` ("Activities
related to employment: Lunch break") to target `139` with `ambiguous=1`, on the reasoning that no target
denotes a lunch break specifically. In the same pass I left Spain's code `121` ("Pausa para la comida",
the same concept) **unmapped**, on the reasoning that no agreed target denotes a lunch break either --
both statements were individually true, but they licensed opposite outcomes for the same real-world
activity: the UK kept its lunch-break episodes under `139` while Spain would have lost them entirely.
That is exactly the kind of country-shaped artefact a leave-one-country-out design cannot tolerate,
since it would read as a genuine difference between Spanish and British time use when it is only a
difference in how this crosswalk treated the same gap.

The fix: Spain's `121` now maps to target `139` as well, `ambiguous=1`, with a rule stating explicitly
that it is given the same treatment as the UK's `1310` for the same reason, and each row's rule text
cross-references the other. I also checked Italy for the same concept: Italy's *primary* activity list
(`catpri`) has no standalone "lunch break" code (its nearest primary code, `112`, is a coffee break
during the main job, already correctly mapped to its own single-source target and left untouched).
Italy's *secondary* list (`CLS-var13`) does carry a `Pausa pranzo` (lunch break) modality at code `11`,
which was already mapped in `crosswalk_activity_secondary.csv` to level2 `13` for the same underlying
reason; its rule text was updated to cross-reference the same Spain/UK decision so a reader does not
have to infer the connection. This changed Spain's counts from 113 mapped / 3 unmapped to 114 mapped /
2 unmapped, the crosswalk total from 530 to 531 rows, the secondary-crosswalk total from 420 to 421
rows, and the ambiguous-row count from 15 to 16. `activity_target_list.csv` itself did not change --
target `139` already existed as an Italian single-source code before this fix and needed no new row.

Two smaller review corrections went with it. The `crosswalk_unmapped_activity.md` heading that reads
"the UK column is not vacuous" originally said `### WHY NO UK ROW IS AMBIGUOUS`, a leftover from the
task's conditional instruction that only applies if the UK column comes out all-zero; since it did not
(14 UK rows are genuinely ambiguous), the heading contradicted its own body and was retitled to match
what the section actually says. Several unmapped-code reasons cited `crosswalk_unmapped_activity.csv`,
a file that does not exist -- the file is the `.md` -- and every such reference was corrected to point
at the actual filename.

## Judgement calls, and what was decided

The Spain-Italy agreement pass on the 103 codes both lists share needed 17 individual judgements. Some
were straightforward mismatches at the same code number (Spain's 121 "lunch break" against Italy's 121
"second job"; Spain's 812 "reading books" against Italy's 812 "reading periodicals", where Italy's own
813 turned out to be the exact match for Spain's meaning). Others were structural: the whole 42-subgroup
("help to another household") is internally reordered between the two lists, so five Spanish codes
(421, 422, 424, 425, and their neighbours) needed redirecting to a different Italian code number that
actually matched their content, rather than being forced to agree at the shared number. In every one of
these cases the resolution favoured whichever country's meaning was independently corroborated (usually
by the UK's own list, or by the losing country's own numbering being internally inconsistent with its
neighbours), and the losing country's real content was either redirected to a better-fitting target or,
where nothing fit, sent to the unmapped list rather than forced. Two Spanish codes (399, 900) and two
Italian codes (997, and code 90 itself) had no honest home anywhere in the shared vocabulary and are
unmapped for that reason, not for lack of effort; a third Spanish code (121) initially looked the same
but was reclassified once the UK's parallel case made clear that a shared "no target exists" gap should
get the same crosswalk treatment in every country it affects, not silence in one and a mapped catch-all
in another. Italy's code 90 needed a separate judgement distinct from a true conflict: it is a genuine
2-digit leaf activity code per `codebook_facts_italy.md` finding F-IT-5 ("a real, usable code, not a
header"), not a header, but the task specification named a 2-digit Italian row as its own illustrative
example of what to set aside from the target list. Both facts are recorded together in the GROUP HEADER
ROWS section, with the correction spelled out, rather than silently mislabelling a documented leaf code
as a header.

The UK judgement calls were the larger body of work, since D-S2-11 makes the UK's crosswalk the one
piece of real label-matching work in this file rather than a near-identity check. Two recurring patterns
account for most of the 277 rows. First, wherever the UK fields its own "unspecified X" catch-all at a
coarser level than the target vocabulary offers (personal care, employment, study, volunteer work,
social life, sport, hobbies, mass media), that UK code was judged to span every target underneath it and
was mapped to the closest single residual target with a rule recorded, rather than picked arbitrarily
without documentation. Second, wherever the UK gives a finer split than Spain or Italy (its
dependent/non-dependent adult-help codes, mirroring Spain's own 391/392/399 split before that split was
lost in the Spain-Italy conflict resolution), the UK's "unspecified kind of help" codes were mapped to
the residual target 399 with a rule, while its specific physical-care/company/other-help codes were
mapped directly and cleanly. UK's "video watching" codes were read as offline/recorded video (matching
the sense Spain's own 822 originally carried) and mapped to target 821, whose Italian label already
explicitly spans television and recorded video, rather than to target 822, which was resolved to
Italy's distinct online/PC-viewing meaning.

## What could not be done

No target could be built for a small number of real activities that only one of the two agreeing
deliveries records in a form distinguishable from something else: a general "unspecified-purpose"
travel residual (Spain's own 900, the UK's own 9000) and "help to a non-dependent adult household
member" as its own category (Spain's own 399, and the UK's mirrored non-dependent-help codes). These
are not oversights; per D-S2-11 the target vocabulary is built only from Spain-Italy agreement, so a
real activity that only one country's list isolates as its own code, or that both record under a
colliding but disagreeing number, cannot enter the target list without either fabricating a citation or
overriding the conflict resolution silently. Both are excluded by the hard rules governing this task.
These gaps are recorded in `crosswalk_unmapped_activity.md`, not silently absorbed into a neighbouring
code. The one gap that initially looked like this (the lunch break) turned out to have an honest
fallback -- an adjacent employment catch-all, 139 -- once the same standard was applied to every
country that has the concept; it is flagged `ambiguous=1` in every country rather than left unmapped in
one.

## What I did not verify

I matched activity labels by meaning as I understand the English, Spanish and Italian text; I did not
verify, and cannot verify from this delivery alone, that a UK respondent's "3811 Feeding the child" and
a Spanish respondent's "381 Cuidados físicos y vigilancia de niños" denote the same real-world behaviour
duration-for-duration, only that the words describe the same category of activity. The same caveat
applies to every one of the 531 crosswalk rows: this is a codebook-label match, not a validated
behavioural equivalence, and the task's own validation document says as much (G2.10, the only gate that
could check this against a real reference, is not yet checkable). I did not verify my own translations
of the Spanish and Italian labels against a professional translator or a second source; they are my own
reading of the source text, kept deliberately short and literal per the task's instruction not to
editorialise, but a translation error in any one of the roughly 150 hand-written `target_label_en`
values is possible and would not be caught by any of the seven self-checks, which test structure and
citation completeness, not translation accuracy. I did not verify that my choice of which country's
meaning wins in each of the 17 conflicts is the choice a native speaker of both languages, or INE/ISTAT
themselves, would make; each resolution is documented with its reason so a reviewer can disagree with a
specific, visible judgement rather than an invisible one. I also did not re-audit every one of the other
15 codes for the same country-asymmetry defect the manager caught in the lunch-break case beyond the
specific check requested (Italy's own work-break code); a systematic sweep for "is this gap treated the
same way in every country that has it" was not run end to end, and a similar asymmetry could exist
elsewhere in the 531 rows without having been caught. I did not attempt to verify the UK's own
"group1"/"group2" columns against anything, since D-S2-11 explicitly forbids treating them as the
harmonised level1 and this crosswalk does not read them at all. Finally, I did not check whether the
158-code target vocabulary, once used to compute Level-1 time budgets in a later step, will actually
satisfy G2.9 (the cross-country divergence floor) or G2.10 (agreement with published national tables);
both are downstream gates this file's construction cannot pre-empt.

## Scratch files

`_es_it_cw_rows.json`, `_helper_sets.json` and `_uk_cw_rows.json` were intermediate scratch used only
to pass data between my own build scripts; I had already deleted them from `outputs_step2/` before this
review (they were never part of the deliverable list and nothing downstream reads them -- the four
shipped files are self-contained CSV/Markdown). There is nothing left for the manager to remove.
