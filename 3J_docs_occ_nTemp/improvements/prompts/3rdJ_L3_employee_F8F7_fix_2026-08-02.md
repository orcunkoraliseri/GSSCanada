# Employee prompt — FINDING 8 + FINDING 7 fix, smoke-tested. 2026-08-02 (evening)

**You are the employee. Execute the task below and append a Progress Log entry on completion.**
Work in `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`. Progress Log =
`3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md` (append only; read its last ~200
lines, which contain the FINDING 8 mechanism correction this task implements).

**Scope: code fix + upload + smoke test. DO NOT launch the campaign.** The cell count is still
being decided by the user. Report the smoke-test result and stop.

## Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node.** ALWAYS
  `sbatch`. Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`,
  `ls`, `scp`, `module load`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. `tar`, `find`,
  `python` are **not** allowed there. Login shell is **tcsh** — no `for` loops, no `2>&1`, one
  short physical line per command.
- **Every job requests `-t 7-00:00:00` minimum**, even one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.**
- **Update the Progress Log live** — same response as each state change, not batched.
- **No file under `Leg2_2-split/` may be modified.**
- All documents in English. Keep replies short and bulleted.

---

## TASK 1 — FINDING 8: the cache-key collision (this is the whole fix)

### The defect, precisely

`eSim_bem_utils/commercial_integration.py:2080-2094`:

```python
def _t9_13_schedule_for(channel, r_wd, r_we, new_wd, new_we):
    key = (channel, round(float(r_wd), 4), round(float(r_we), 4))
    if key in _t9_13_cache:
        return _t9_13_cache[key]          # <-- new_wd / new_we SILENTLY DISCARDED
```

`r_wd`/`r_we` come from `_channel_occ_24(channel)` against the channel reference — **identical for
every object in a channel**. The source schedule is **not in the key**. So every
`WaterUse:Equipment` object in a channel collapses onto ONE schedule, built from whichever object
the loop reached first. That is why `Laundry Service Water Use 30.6gpm 180F` ended up on
`MXU_Hotel_DHWv2_r1000w1000_...` — the guest-room curve — while its `Peak_Flow_Rate` stayed correct
(that is computed per object at `:2146-2148`).

**Do NOT implement "skip objects whose floor/peak are -1.0".** That was the original spec and it is
wrong: `:2151-2155` writes `"floor": None, "peak": None` for **every** T9-13 object and `:2283-2288`
renders `None` as `-1.0`. Nothing takes that branch under T9-13; such a fix would be a no-op.

### 1a. Fix the commercial path — `commercial_integration.py:2080-2094`

Put the source schedule in the key, and in the generated name:

```python
def _t9_13_schedule_for(channel, proto, r_wd, r_we, new_wd, new_we):
    key = (channel, str(proto).strip().upper(),
           round(float(r_wd), 4), round(float(r_we), 4))
    if key in _t9_13_cache:
        return _t9_13_cache[key]
    nm = (f"MXU_{channel.capitalize()}_DHWv2_{_sched_token(proto)}_"
          f"r{int(round(key[2]*1000)):04d}w{int(round(key[3]*1000)):04d}_{tag}")
```

- Add a small `_sched_token(proto)` helper: upper-case, keep `[A-Z0-9]`, collapse the rest to `_`,
  truncate to ~40 chars. **Assert the resulting `nm` is unique per key** (a truncation collision
  would silently recreate the bug it is fixing — if two distinct `proto` values produce the same
  token, append a short deterministic hash of the full `proto`).
- EnergyPlus name length: verify the final names are accepted (the existing `tag` is already long).
  If any name is rejected or truncated by eppy/E+, use the hash suffix form for all of them rather
  than mixing conventions.
- Update the call site at `:2140-2141` to pass `proto`.

### 1b. Fix the residential path — `commercial_integration.py:1577`

```python
key = (hh_id, round(info["r_wd"], 4), round(info["r_we"], 4))
```

Same defect class: `r_wd`/`r_we` are functions of the household occupancy only, **not** of the
object's prototype schedule, so two objects in one apartment Space with different prototype
schedules collide. Add `str(proto).strip().upper()` to the key and the token to the name
(`MXU_Residential_DHWv2_HH{hh_id}_{token}_r####w####`).

**Measure, do not assume:** report how many distinct `(Space, proto)` pairs exist among the 27
residential objects in the smoke IDF. If it is 1:1, say so — that is evidence the residential path
was never actually colliding, and it belongs in the log either way.

### 1c. Add audit check D7 — and read it from the SAVED IDF

In `audit_dhw_shape_preservation` (`:1173`) or a new sibling function called after `idf.saveas`.
**D7 must not be implemented over `result["dhw_applied"]`**: `rec["derived_schedule"]` records the
*cached* name, so a D7 built on it would inherit exactly the blindness it exists to close and would
have passed on arm E.

D7, per `WaterUse:Equipment` object in the re-opened output IDF:

> its `Flow_Rate_Fraction_Schedule_Name` is either **unchanged** from the source IDF, or is the
> T9-13 derivative **of its own original schedule** — never another object's.

Implement by re-reading the saved IDF and asserting the assigned schedule name's embedded source
token matches `_sched_token(rec["prototype_schedule"])` for that object. Wire D7 into the
`counts` dict and the `pass` verdict alongside D1–D6, and into the provenance line.

### 1d. The empty-audit N/A gap (open item 5) — fix it while you are here

The 4 `Default_NECB` control cells report `audit_pass=False, n_audited=0` because they inject
nothing. Report **N/A** (not FAIL) when the cell requested no DHW channels at all
(`_expect == ()`); keep `n_audited == 0` a **FAIL** in every other case. Do not loosen it further.

### 1e. `agg_armE.sh` mis-specified check (open item 4)

It asserts `n_audited == 47` as universal. Actual distribution: 47 (26 cells), 71 (20), 31 (6),
0 (4 controls). Change it to assert **per geometry**. Until then that output line means nothing.

---

## TASK 2 — FINDING 7 option B: rewire 2030 retail to the calibrated pool

User ruling: **option B**. `3rdJ_07_aug_to_bem_4split.py::build_retail_product_2030` (`:684-711`)
reads `RETAIL_LEVER_FILES[...]`, built from `2030_diaries_*_raw.csv`. Every other 2030 channel reads
the calibrated `D2030` = `2030_synthetic_diaries_4split_calibrated_mindwell_C_v2.csv`
(md5 `5aa74f44cd09a7afa9fa5418864956ed`).

**Change exactly one thing — the source. Nothing else.**

- The raw lever files pool **all 111,024 rows (all 3 bands)**; the retail product is band-independent
  and differs between scenarios only by a **uniform scalar** lever (`_derive_retail_lever`, `:169`,
  which already asserts uniformity). Preserve that structure: pool **all** of `_C_v2` the same way.
  Do **not** introduce a band filter — FINDING 7's whole point is that RAW and CAL are the same rows,
  so the difference must be calibration alone.
- Build `ret48` per `(Day_Type3, PR ∈ {2→QC, 4→AB})` as `sub[RET].mean()`, then `np.roll(arr, 8)`
  (+4 h, clock origin — this project has already paid for that offset once), then apply the uniform
  lever and normalise against the **un-levered** pooled base peak, mirroring the existing
  base/levered discipline at `:705-708`.
- Keep `assert_d2030_is_c` / the md5 guard in force on the file you read.
- Keep the predecessor: back up the current retail product as `..._BAK_2026-08-02.csv` before
  overwriting, same discipline as the office product.

**Pre-registered acceptance check, write it before you run it:** after the rewire, QC weekday retail
peak must move from **11:00 → 16:00**, and the Saturday/weekday retail contrast must move from
**0.98 → ~3.38** (observed anchor 2.69). If the peak does not move, the rewire did not take effect —
report that as a FAIL, do not adjust anything to make it look right.

**Flag, do not fix:** T9-12's retail lighting re-spec `k = 0.60` was calibrated against the *current*
shape. Note in the log that it needs re-checking after this change. Do not re-tune it.

---

## TASK 3 — FINDING 6: upload the corrected office product

Built and verified locally, **not yet uploaded** (arm E was reading the old one; overwriting
mid-array would have corrupted it — arm E is now finished, so upload is safe).

- `office_presence_multiplier_2030.csv`, md5 `575d17e55f32f8b5ec493ff590833d94`
- predecessor `office_presence_multiplier_2030_BAK_2026-08-02.csv`, md5 `1536c98c5358ece477290d45f0505e4f` — keep it on disk, do not delete
- `scp` to the cluster, then **verify the md5 on the cluster matches** before reporting done.

---

## TASK 4 — the smoke test. This is the deliverable.

One cell, `sbatch`, `-t 7-00:00:00`: **`Y2022__Tall__MTL`** with the fixed injector, against
`Default_NECB__Tall__MTL`.

`Y2022` is the T9-13 reference, so `r = 1.000` and **a correct T9-13 must be a bit-for-bit no-op on
DHW**. Pre-registered predictions, from the log — do not alter them:

| object | arm E (broken) | required after fix |
|---|---|---|
| `LAUNDRY SERVICE WATER USE` | 2.7598e+12 J (×3.028) | **~9.1147e+11 J (×1.000)** |
| `F30 HOTEL_BOT_LAUNDRY SERVICE WATER USE` | 3.7251e+11 J (×1.399) | **~2.6625e+11 J (×1.000)** |
| `F31-F37 HOTEL_MID_*_GUESTRM` (all 8) | ×1.136 | **×1.000** |
| `F38 HOTEL_TOP_KITCHEN` | ×0.998 | ×1.000 |
| `BOOSTER SERVICE WATER USE` | ×0.995 | ×1.000 |
| D7 | did not exist | **PASS**, 0 violations |

🔴 **The guest rooms are the discriminating case.** Their ×1.136 was recorded in the log as "the
legitimate `r` effect" — but at `r = 1.000` there is no legitimate `r` effect to have. If the guest
rooms do **not** return to ×1.000, the cache collision was not the whole mechanism, the correction is
incomplete, and you must report that rather than proceed. That is the result that makes this test
non-vacuous.

Also report: `t9_13_audit` counts including D7, `n_audited`, and the full list of distinct
`MXU_*_DHWv2_*` schedule names created in the cell (there must now be **more than one per channel**
wherever a channel has objects on different prototype schedules — if there is still exactly one per
channel, the fix did not take).

---

## Deliverable

1. The four tasks above, each with its Progress Log entry appended **live**.
2. The smoke-test table: predicted vs measured, per object, with the verdict stated as PASS/FAIL —
   **a miss is recorded, not repaired.**
3. **Stop there.** Do not launch the 2030-family campaign; the cell count is the user's open call.
   Report the job numbers and the smoke result and hand back.
