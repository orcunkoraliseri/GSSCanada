# AMENDMENT 2 to the Step 10 `C2` pre-registration — WHAT A RUN LEAVES BEHIND

**Date:** 2026-09-09
**Amends:** `Step10_docs/prereg_step10_nocore_DRAFT.md`, md5 `e1f2822a800932ff099c15aed6be7ead`
**Sits beside:** Amendment 1 (population), md5 `86afe2043657f0bccf679c0781fd3d42`
**Status of the amended document:** UNCHANGED ON DISK AND STILL FROZEN — md5 re-verified
`e1f2822a800932ff099c15aed6be7ead` after this amendment was written, `R1` still passes. This is a
separate, append-only record; no value in the frozen text was overwritten.

---

## 1. What is amended, and on whose authority

The author's standing delegation of 2026-09-09 — *"no need to ask me anything keep goin as you
receommend"* — and this project's own written rule that the runner's reporting defect **"belongs in
the next re-pre-registration, not a hurried edit"**. This is that re-pre-registration. It is made
BEFORE the campaign runs, not after a run went wrong, which is the only time such a change can be
made honestly.

Nothing about the population, the eligibility basis, the bands or the refusals is amended here.
Amendment 1 stands unchanged.

## 2. The defect being closed

Recorded on 2026-09-08 and deliberately not hurried:

```
(a) a cell that FAILS writes no file at all.  Its status lives in the returned
    dict, in RAM, for the whole run.
(b) `campaign_results.json` is written only after the LAST cell finishes.
```

Consequence at the size now authorised — **35,290 cells across three fold districts** — is that a
campaign is unreadable until it ends. This is not hypothetical: `DEFECT 8` had to be **reproduced on
a second machine** to be read at all, because the machine that hit it had nothing on disk to show.

## 3. What changed in the instrument — all of it additive

`tools/4thJ_step10_nocore_campaign.py` (backup before the change:
`4thJ_step10_nocore_campaign.py.bak_pre_l56`, md5 `25b16567f2f94d0bc24637d57fbbca8f`, LF-only
verified before and after):

1. **`write_failure_record()`** — a cell that does not complete now writes
   `cells_failed/<cell_slug>.json` carrying its identity (`cell_id`, `cell_slug`, `building_id`,
   case, arm, fold, `f`, `n_u`, `zone_count_emitted`), the pins it ran under (from `base_manifest`),
   the failure dict including the traceback tail, wall seconds and a timestamp.
   🔴 **`"record_kind": "FAILURE_NOT_A_RESULT"`, and it is written to `cells_failed/`, NEVER to
   `cells/`.** `cells/` is the manifest population that `G10N.14` counts blank fields in; a failure
   record landing there could be read as a result. The separation is the point.
2. **`run_cell()` is now a wrapper**; the 2026-09-08 body is `run_cell_inner()`, unchanged in what it
   does on the success path — same manifest, same fields, same destination, same return dict. The
   wrapper cannot rescue a failing cell or soften its status; it only makes the failure legible while
   the run is still going. A failure while WRITING the record is caught and reported beside the
   original failure (`failure_record_written: false` plus the error), never allowed to mask it.
3. **`campaign_progress.jsonl`** — one line per finished cell, written and **flushed immediately**,
   preceded by a `RUN_HEADER` line carrying district, planned cell count, `payload_set_sha256`,
   `prereg_md5`, `engine_sha256` and worker count. Opened in APPEND mode: a second run adds its own
   header and cells rather than erasing the first run's evidence.
4. **`campaign_status.json`** — rewritten every `PROGRESS_EVERY = 25` cells (and once at the end)
   with counts by completion status and an explicit note that it is in flight.
5. **Closing print** names how many cells did not complete and where their records are.
6. Module docstring gained a `--- reporting ---` block stating all of the above.

🔴 **No refusal was relaxed, added or renamed. No manifest field changed. `R7` and `R11` are
untouched. `campaign_results.json` is still written at the end and is still the complete record.**
The population path is provably undisturbed: ES preflight before and after gives the same 1,151
eligible, 11,510 cells, 11,976 dwellings and the same `payload_set_sha256`
`575960f547ce462a3754eaa8d1f84090f721b5fb7ca135324bb46b6769929486`.

## 4. Seen failing, and seen working

**A cell that dies leaves a file** — the shipped runner imported unmodified, `run_cell` called with
geometry deliberately missing:

```
returned completion_status: HARNESS_ERROR
failure_record_written    : True
record_kind               : FAILURE_NOT_A_RESULT
identity kept             : es__relation/12582234__caseA__f000 | relation/12582234 | fold es
pins carried              : e1f2822a800932ff099c15aed6be7ead
traceback captured        : True
cells/ untouched          : True
```

**A real two-cell shakedown** (`--shakedown --limit 2`, real EnergyPlus 23.1.0, scratch `--out`):
both cells completed, `campaign_progress.jsonl` carried the `RUN_HEADER` and one `CELL` line each
written as they finished, `campaign_status.json` showed `cells_finished 2 / completed 2`, and
`campaign_results.json` still landed at the end. Manifests: 18 zones, `cf` 1.0,
`unstable_markers: ["Temperature out of range"]` → `COMPLETED_WITH_UNSTABLE_MARKERS` (recorded by
the runner as before; this amendment does not change how markers are treated).

**A dry run writes no failure records:** `--dry-run --limit 3` produced progress, status, results and
preflight files and **no `cells_failed/` directory** — `DRY_RUN` is excluded by name, so a smoke
cannot manufacture failure evidence.

## 5. What this amendment deliberately does NOT do

- It does not rescue, retry or reclassify a single failing cell.
- It does not score anything. `G10N.x` verdicts are still computed nowhere in this tool.
- It does not touch the population, the bands, or the reroute question.
- It does not make a partial run a campaign. A run that ends with cells in `cells_failed/` is a
  failed campaign that can now be READ, not a campaign that passed.

## 6. Provenance

| item | value |
|---|---|
| frozen prereg md5 (unchanged, re-verified) | `e1f2822a800932ff099c15aed6be7ead` |
| Amendment 1 (population) md5 | `86afe2043657f0bccf679c0781fd3d42` |
| runner md5 after this amendment | `ad8a586d0a681057cb3552e082165669` (77,239 bytes, LF-only) |
| runner backup before it | `tools/4thJ_step10_nocore_campaign.py.bak_pre_l56`, md5 `25b16567f2f94d0bc24637d57fbbca8f` |
| emission this is aimed at | `T07`, 2026-09-08 recut, verified 2026-09-09 (impl §15) |
| per-district payload digests to pin | ES `575960f5…`, IT `2cc6ba95…`, UK `1d575d0f…` |

## 7. The launch this makes possible

With this amendment in force, the conditions for launching `C2` are:

1. one emission all three fold districts pass — **met** by `T07` (ES 1,151 / IT 1,171 / LDN 1,207
   eligible, 0 FAIL, zero reroutes);
2. the population rule pre-registered and the count re-derived at preflight — **met** (Amendment 1;
   31,591 dwellings on this emission);
3. a run that can be read while it runs — **met by this amendment**;
4. `--expect-payload-digest` given per district so `R10` refuses if the stock moves under the run —
   **to be done at launch**, and it is not optional: the stock moved twice in two days.

Per-dwelling bands must be re-derived on 31,591 before any verdict is quoted. Nothing has been
scored under any basis; there are no verdicts to invalidate.
