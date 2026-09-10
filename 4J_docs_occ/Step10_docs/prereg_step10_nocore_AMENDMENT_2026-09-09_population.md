# AMENDMENT 1 to the Step 10 `C2` pre-registration — THE POPULATION RULE

**Date:** 2026-09-09
**Amends:** `Step10_docs/prereg_step10_nocore_DRAFT.md`, md5 `e1f2822a800932ff099c15aed6be7ead`
**Status of the amended document:** UNCHANGED ON DISK AND STILL FROZEN. This amendment is a
separate, append-only record. `R1` still compares the sidecar to `e1f2822a…` and still passes.
Nothing in the frozen text was edited, and no value in it was overwritten — the superseded values
are named here instead.

---

## 1. What is amended, and on whose authority

The author ruled on 2026-09-09, delegating the choice after being shown both candidates and my
recommendation:

> "no need to ask me anything keep goin as you receommend"

Recorded plainly: the author did not pick a number; they delegated the ruling having been given the
two candidates (27,352 and 26,095), the measurement behind them, and the statement that correcting
the count is a basis change. This amendment is that ruling, written down so it can be audited or
reversed.

The eligibility basis is **not** amended. A building still enters `C2` when flats were actually
drawn in it, judged by the payload's own `geometry_outcome`, implemented once in
`4thJ_step10_nocore_preflight.py`. The author's viewer ruling — **the drawn plate IS the
dwelling** — is likewise not amended. What was wrong was how this campaign COUNTED those plates.

## 2. The superseded rule and the rule in force

```
SUPERSEDED  (frozen DRAFT, lines 522 / 525 / 711):
    N_u := sum over floors of len(floor["zones"])
    pre-registered C2 population = 27,352 zones  (es 11,244 / uk 2,316 / it 13,792)

IN FORCE (this amendment):
    N_u := the number of DISTINCT zone names in the payload
        == `dwellings_total`, the emitter's own authoritative field
    corrected C2 population = 26,095 dwellings  (es 10,809 / uk 1,529 / it 13,757)
```

Difference: **1,257 dwellings that do not exist**; London was 34% inflated.

Why the superseded rule was wrong, in one paragraph. A zone that spans n storeys is written out
once per storey ROW, byte-identical, so a viewer can draw every floor
(`scripts/emit_eu11_layout_sidecars.py:364-369` and `:425-431`). Upstream's `FINDING 201` invariant
is one zone per dwelling, extruded over the group's full height, never one zone per physical storey
(`openubem/geometry/european_residential.py:2793-2799`). Summing the rows therefore counted a tall
flat once per floor. Our own `zone_records()` compounded it by falling back to the storey row's
`z_floor_m` when a zone omitted `z_floor`, which made byte-identical repeats look geometrically
distinct — that is the origin of our `FINDING 268` ("defect 8"), **retracted on both sides**.

`dwellings_total` was PROVENANCE under the superseded rule and is the CHECKED basis under this one.
`k` (the census per-building quotient) remains provenance and is still never gated: `FINDING 246` /
`FINDING 266` are about `k` PER STOREY disagreeing with the engine's re-derivation, not about the
building total.

## 3. Evidence this amendment rests on

Measured here, over every payload in all four districts, emitted outcomes only
(`DWELLING_LAYOUT_EMITTED`, `DWELLING_LAYOUT_EMITTED_IMPUTED_COUNT`):

```
ES   buildings= 1100  entries= 11244  distinct= 10809  sum(dwellings_total)= 10809  mismatches=0
LDN  buildings=  685  entries=  2316  distinct=  1529  sum(dwellings_total)=  1529  mismatches=0
IT   buildings= 1036  entries= 13792  distinct= 13757  sum(dwellings_total)= 13757  mismatches=0
LYO  buildings=  105  entries=   617  distinct=   586  sum(dwellings_total)=   586  mismatches=0
TOTAL ES+LDN+IT      entries=27352  distinct=26095  sum(dwellings_total)=26095
```

`missing_dwellings_total = 0` in every district; **2,926 of 2,926 buildings agree, zero
mismatches**. Every repeated name's zone object is byte-identical (md5 of canonical json, 0 of
1,288 repeated names differ). Independently reproduced by `openubem-20` on their side and recorded
under their `FINDING 268`.

## 4. What changed in the instrument

`tools/4thJ_step10_nocore_campaign.py` — all changes additive; **no refusal was relaxed, no pin was
moved, no guard's field names were rewritten**:

1. `zone_records()` returns one record per DWELLING. Repeats of a name are collapsed to the first
   occurrence, which is exact because the repeats are byte-identical.
2. **New refusal `R11`**, two clauses, neither downgradeable:
   - a repeated zone name whose GEOMETRY differs is not a storey repeat — it is the genuine
     two-flats-one-name fault that `DEFECT 8` was looking for, and it refuses instead of being
     collapsed;
   - a building whose distinct dwellings do not equal its declared `dwellings_total` refuses. Under
     the superseded rule those two could disagree by construction, and across the three fold
     districts they disagreed by 1,257.
3. `preflight_report.json` now records `dwellings_registered` and, beside it,
   `payload_zone_entries_superseded_basis`, so the gap is auditable without re-deriving it.
4. `R7`'s "one gain csv per flat" clause is UNCHANGED. It was never wrong; it was refusing correctly
   because `N_u` counted entries. With the population corrected it passes on its own terms.

## 5. Seen passing, and seen still refusing

`--dry-run`, this machine, 2026-09-09:

```
ES-MAD-BERRUGUETE   PREFLIGHT OK   1100 eligible / 75 Arm F / 0 FAIL   11000 cells
                    dwellings registered: 10809  (superseded rule: 11244)
IT-BOL-GALVANI2     PREFLIGHT OK   1036 eligible / 175 Arm F / 0 FAIL  10360 cells
                    dwellings registered: 13757  (superseded rule: 13792)
GB-LDN-STDUNSTANS   REFUSE R5      12 payloads INTERZONE_MISMATCH_REROUTED
FR-LYO-HAUTCOEURPENTES  REFUSE R3  the French baseline, not waivable
```

Geometry smoke, `--limit 45 --dry-run` (builds IDFs, invokes no binary). The exact building that
died `HARNESS_ERROR` yesterday now builds:

```
es__relation-12638102__caseA__f000   ZONE objects 1   gain csvs 1   dwellings_total 1
                                     vertex z 0.0 -> 15.0 m   (all five storeys, nothing lost)
es__relation-12582232__caseA__f000   ZONE objects 18  gain csvs 18  dwellings_total 18
```

The single zone still spans the full 15 m. The correction removes 1,257 duplicate COUNTS; it
removes no floor area, no volume and no building.

## 6. Band change

Any Step 10 or Step 11 quantity expressed **per dwelling** now has a denominator smaller by 1,257
(es −435, uk −787, it −35). This amendment changes no threshold VALUE and no `G10N.x` clause; it
changes what the denominator means. Every per-dwelling band inherited from the frozen DRAFT must be
re-derived against the corrected population before any verdict is quoted. Nothing has been scored
under either basis, so no existing verdict is invalidated — there are none.

## 7. What this amendment deliberately does NOT decide

- **The rerouted buildings.** London is still refused by `R5` over 12 `INTERZONE_MISMATCH_REROUTED`
  payloads. Upstream recommended excluding them; that recommendation is **recorded, not taken**.
  Excluding buildings is a change of population MEMBERSHIP with a selection-bias consequence, which
  is a different act from correcting how dwellings are counted, and it is left open on purpose —
  upstream's `T07` re-emission may re-emit those buildings cleanly, which is the better remedy.
- **Launching the campaign.** See §8.

## 8. Why nothing is launched on this amendment

Madrid and Bologna now pass preflight; London does not, and cannot until either the rerouted
payloads are re-emitted or the author rules them excluded. Running the two that pass today would
mean London runs later against a DIFFERENT emission — and this runner's own `R10` says it plainly:
*"a campaign that spans two emissions is two campaigns."* Upstream's `T07` re-emission of all four
districts is in flight (Madrid 1,175→1,187, Lyon 509→529, London 706→1,240, Bologna 1,211→1,215).
So the campaign holds until that emission lands, is announced (sha, line endings, per-district
counts, row builder), and is re-measured here.

🔴 Consequence for this amendment's numbers: **26,095 is the population of the 2026-09-08 emission,
not a constant.** The RULE is what is pre-registered here. The COUNT is re-derived at preflight and
written into `preflight_report.json` for whichever emission a run is authorised against.

## 9. Provenance

| item | value |
|---|---|
| frozen prereg md5 (unchanged) | `e1f2822a800932ff099c15aed6be7ead` |
| ES payload set sha256 (2026-09-08 emission) | `edd31fd9a79bb2695b1698b9019f1a4c913f5fe299f4d7de3384597db2e687c6` |
| IT payload set sha256 (2026-09-08 emission) | `64d6768f8bdfa88d26d334aa8aa1ceae10408e6f63fabccd07a0d66ff8842d21` |
| engine pin (`european_residential.py`) | `6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3` |
| no-core pin (`european_nocore.py`) | `21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae` |
| runner backup before this amendment | `tools/4thJ_step10_nocore_campaign.py.bak_pre_l53` |
| evidence | impl doc §12, §12.5, §13 |

Stale artefacts warning: `Step10_docs/outputs_step10_nocore/cells/` still holds 1,427 cell records
written on 2026-09-08 under the SUPERSEDED basis. They are kept as prior evidence and are not a
current population; they are overwritten by the next authorised run.
