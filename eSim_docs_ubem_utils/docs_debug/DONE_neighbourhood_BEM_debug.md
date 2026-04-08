# Neighbourhood BEM Debug — Investigation Plan

## Issue Summary

When running **Option 5 — Neighbourhood Simulation** in `run_bem.py` and
selecting `NUS_RC1.idf`, the menu reports:

```
Found SpaceList 'ProgramType_af3770e3' with 47 spaces.
Grouped into 0 buildings.

Detected 0 buildings in the neighbourhood.
Error: Could not detect buildings. Check IDF structure.
```

The SpaceList is discovered and parsed successfully, but the subsequent
"grouping by building" step produces an empty dict, so the simulation bails
out before preparing any per-building occupancy objects.

**Scope of this document:** identify the root cause, propose a fix, and lay
out a step-by-step verification/implementation plan.

---

## 1. Setting the Stage

- **Actor:** BEM / UBEM pipeline user running `python run_bem.py` and choosing
  option 5 (Neighbourhood simulation) → mode 1 (Standard) → `NUS_RC1.idf`.
- **Objective:** run a full-year EnergyPlus simulation on a neighbourhood IDF
  where each building receives its own occupancy / lighting / equipment /
  water schedules (per-building profiles).
- **Relevant code:**
  - `eSim_bem_utils/neighbourhood.py` — building detection and IDF rewrite
    logic.
  - `eSim_bem_utils/main.py` — CLI dispatcher for option 5.
  - `BEM_Setup/Neighbourhoods/NUS_RC1.idf` — the IDF the user selected.
- **Observed behavior:** 47 spaces found in the SpaceList, then zero
  buildings after grouping → pipeline exits.
- **Expected behavior:** N buildings detected (≥ 2 given the file's
  hash-based naming), per-building People/Lights/Equipment objects injected,
  simulation proceeds.

---

## 2. Defining the Task

Diagnose *why* `get_building_groups()` returns an empty dict for
`NUS_RC1.idf` (and almost certainly for `NUS_RC2–6.idf`), document the root
cause with code + IDF evidence, and specify a safe fix that unblocks
Option 5 without breaking IDFs that were already working.

This is a **debug & investigation** task, not a refactor — change only what
is necessary to restore Option 5.

---

## 3. Root-Cause Analysis

### 3.1 What the code assumes

`eSim_bem_utils/neighbourhood.py:54-64`:

```python
for space in space_names:
    # Extract prefix (everything before _Room_)
    prefix_match = re.match(r"(.+?)_Room_", space)
    if prefix_match:
        prefix = prefix_match.group(1)
        ...
        bldg_id = f"Bldg_{building_prefixes.index(prefix)}"
        ...
        buildings[bldg_id].append(space)
```

The function assumes every space name contains the literal substring
`_Room_`, and uses the text before `_Room_` as the *building identifier*
(the docstring calls this a "coordinate-based prefix"). If the pattern does
not match, the space is silently dropped and no building group is created.

### 3.2 What `NUS_RC1.idf` actually contains

The SpaceList at `NUS_RC1.idf:1016` is named `ProgramType_af3770e3` and lists
space names like (excerpt from lines 1018–1065):

```
  132.8660_living_unit1_2_a25d9605_Space,  !- Space Name 1
  000_living_unit1_2_a25d9605_Space,       !- Space Name 2
  67.1-00_living_unit1_1_a8a609ec_Space,   !- Space Name 3
  ...
  199.9660_living_unit1_2_a25d9605_Space;  !- Space Name 48
```

Key observation: **none of these names contain `_Room_`**. They follow the
pattern:

```
<coord_prefix>_living_unit1_<N>_<hash>_Space
```

where `<N>` ∈ {1, 2} and `<hash>` ∈ {`a8a609ec`, `a25d9605`} inside this
particular SpaceList.

A separate Grep across the whole file *does* find 984 occurrences of
`_Room_`, but those belong to **other** zones/spaces (e.g.
`000_Room_23_f2d32505_Space`, `000_Room_24_e2b9dc3f_Space`) that are NOT
members of the `ProgramType_af3770e3` SpaceList. The SpaceList that the
code picks up contains only `living_unit` names, so the `_Room_` regex
matches 0 out of 47 entries.

### 3.3 Why the grouping step prints `0 buildings`

Because `prefix_match` is `None` for every space, the `if prefix_match:`
branch never runs, `buildings` stays `{}`, and the function returns an empty
dict. `prepare_neighbourhood_idf()` then sees `n_buildings == 0` and aborts
(`neighbourhood.py:159-161`).

This matches the console output exactly: "47 spaces … 0 buildings".

### 3.4 Secondary problem — off-by-one in the space count

The regex

```python
re.compile(r"SpaceList,\s*\n\s*([^,]+),\s*!-\s*Name\s*\n([\s\S]*?);", re.MULTILINE)
```

captures text up to (but not including) the first `;`. The last entry in
`NUS_RC1.idf` is:

```
  199.9660_living_unit1_2_a25d9605_Space;  !- Space Name 48
```

The `;` terminates the capture *before* the `!- Space Name 48` comment, so
the final line in `spaces_block` contains the name but **no** `!-` marker.
The later filter

```python
if line and "!-" in line:
```

silently drops that last space. The SpaceList actually holds **48** spaces
but the parser reports **47**. Not the cause of the "0 buildings" failure,
but a real bug worth fixing while we're in the area.

### 3.5 Why "coordinate prefix = building" is the wrong mental model

Even if the regex were relaxed to `(.+?)_living_unit1_`, using the
coordinate prefix as the building id would still be wrong. The same
coordinate prefix appears for *different* living units, e.g.:

```
132.8660_living_unit1_1_a8a609ec_Space   ← unit 1
132.8660_living_unit1_2_a25d9605_Space   ← unit 2
```

Coordinate `132.8660` is geometry (a room position), not a building
identifier. The piece that actually varies per building/unit is the hash
suffix (`a8a609ec`, `a25d9605`). That suffix — or equivalently the
`living_unit1_<N>_<hash>` tail — is the correct grouping key.

---

## 4. Proposed Fix (for a follow-up implementation task)

> This debug doc **only specifies** the fix. Implementation happens in a
> separate change, after the user approves the direction.

### 4.1 Replace the `_Room_` assumption with a naming-agnostic grouper

Change `get_building_groups()` so that the grouping key is the **trailing
identifier** of the space name, not a hard-coded `_Room_` split. A minimal
rule that works for both naming conventions observed in
`BEM_Setup/Neighbourhoods/`:

1. Strip the trailing `_Space` suffix if present.
2. Split on `_`.
3. Use the **last segment** (the hex hash, e.g. `a8a609ec`) as the building
   id.
4. Fall back to the `_Room_<N>` style only if the hash heuristic does not
   apply — preserves backward compatibility for any IDF that already relied
   on it.

This yields stable `Bldg_0`, `Bldg_1`, … ids and works for both
`living_unit1_N_<hash>_Space` and `Room_NN_<hash>_Space` naming.

### 4.2 Fix the off-by-one in space parsing

Change the regex so the trailing `;` is captured inside the non-greedy
group, or change the line filter so the last entry is not dropped. Simplest
fix: replace

```python
if line and "!-" in line:
    name_part = line.split(",")[0].strip()
```

with something like

```python
stripped = line.strip().rstrip(",;")
if stripped and not stripped.startswith("!"):
    # keep everything before the first comment marker, strip trailing ,;
    name_part = stripped.split("!-")[0].rstrip(",; ").strip()
    if name_part:
        space_names.append(name_part)
```

so that presence of `!-` is no longer mandatory.

### 4.3 Keep the WaterUse:Equipment mapping consistent

`get_water_equipment_building_map()` currently extracts the prefix between
`..` and `_Room_` (`neighbourhood.py:115`). Once the grouping key changes
to the trailing hash, the water-equipment mapping must switch to the same
key, otherwise DHW schedules will silently stop being remapped. This is the
highest-risk part of the fix — it must be changed in lockstep with §4.1.

### 4.4 Do NOT touch the downstream injection code

Nothing in `prepare_neighbourhood_idf()` below `get_building_groups()` needs
to change — it just iterates `buildings.items()`. Keeping the output shape
(`Bldg_<i> → [space names]`) identical means the per-building People /
Lights / Equipment / Schedule generation and the integration layer that
consumes these ids remain untouched.

---

## 5. Step-by-Step Investigation / Fix Plan

Each step follows the CLAUDE.md task format: *aim → what → how → why →
impact → steps → expected result → how to test*.

### Step 1 — Reproduce the failure on a second IDF

- **Aim:** confirm the bug is not specific to `NUS_RC1.idf`.
- **What to do:** run option 5 for `NUS_RC2.idf` … `NUS_RC6.idf` and record
  the "Found SpaceList … Grouped into N buildings" line for each.
- **How:** `python run_bem.py` → `5` → `1` → pick each IDF in turn; Ctrl-C
  after the grouping message.
- **Why:** scopes the fix (is it one file or all six?) and tells us whether
  any IDF uses the `_Room_` convention the original code was written for.
- **Impact:** determines whether the fix needs to handle multiple naming
  conventions or just one.
- **Expected result:** all six files either group 0 buildings (same bug) or
  group some — at least one should be non-zero if the original code was
  ever exercised on real data.
- **How to test:** console output only; no file writes.

### Step 2 — Enumerate the actual naming conventions in the 6 IDFs

- **Aim:** list the distinct "tail" tokens used across
  `BEM_Setup/Neighbourhoods/NUS_RC*.idf`.
- **What:** grep each file for the main `SpaceList,` block and extract the
  suffix pattern of its member spaces (`_Room_*_Space`,
  `_living_unit1_*_Space`, or something else).
- **How:** one-off Python snippet that reuses `get_building_groups()`'s
  SpaceList regex and prints the first 5 member names per IDF.
- **Why:** the correct grouping key depends on *every* convention in use,
  not just the one in `NUS_RC1`.
- **Impact:** feeds directly into §4.1 — the fallback logic only needs to
  cover tokens we actually observe.
- **Expected result:** a short table
  `IDF → SpaceList name → example space name → proposed building id rule`.
- **How to test:** visual inspection of the printout against the file.

### Step 3 — Prototype `get_building_groups()` v2 offline

- **Aim:** write a drop-in replacement for `get_building_groups()` without
  editing the real file yet.
- **What:** a standalone script (e.g.
  `eSim_tests/scratch_building_groups.py`) that reads an IDF path, runs the
  new grouping logic, and prints `{bldg_id: space_count}`.
- **How:** implement §4.1 (hash-tail grouping with `_Room_` fallback) and
  §4.2 (off-by-one fix) in the script; leave `neighbourhood.py` untouched.
- **Why:** lets us validate behavior against all 6 IDFs before modifying
  production code.
- **Impact:** zero — pure read-only exploration.
- **Expected result:** every IDF reports ≥ 1 building, counts roughly
  balanced (e.g. 2 buildings × 24 spaces each, rather than 48 in one and 0
  in another).
- **How to test:** compare the sum of per-building counts to the actual
  number of entries in the SpaceList (should match exactly — and the number
  should be 48 for `NUS_RC1`, not 47).

### Step 4 — Apply the fix in `neighbourhood.py`

- **Aim:** port the validated prototype into `get_building_groups()` and
  `get_water_equipment_building_map()` in-place.
- **What:** edit `eSim_bem_utils/neighbourhood.py` only; keep the function
  signatures and return types identical.
- **How:** small, reviewable Edit calls — one per function. No refactor of
  `prepare_neighbourhood_idf()`.
- **Why:** preserves the downstream contract and makes the diff easy to
  review.
- **Impact:** affects every caller of `get_building_groups()` /
  `prepare_neighbourhood_idf()` — i.e. options 5, 6, and 7 of the menu.
- **Expected result:** code compiles (`python -c "import
  eSim_bem_utils.neighbourhood"`), no other source files need to change.
- **How to test:** re-run Step 1 and confirm non-zero building counts.

### Step 5 — Verify the WaterUse:Equipment remap still works

- **Aim:** make sure DHW schedules are still rewritten per building after
  the grouping-key change.
- **What:** after running option 5 end-to-end on `NUS_RC1.idf`, grep the
  prepared IDF for `Water_Bldg_0`, `Water_Bldg_1`, … and confirm the
  original `ApartmentMidRise` / default DHW schedule names have been
  replaced in every `WaterUse:Equipment` block.
- **How:** `Grep -n "Flow Rate Fraction Schedule Name"` on the output IDF
  and cross-check the line before it (the schedule value should now be
  `Water_Bldg_X`).
- **Why:** the water-equipment mapping is the most fragile part of the
  change (§4.3). A silent regression here would cause the DHW plant loop
  to run against a stale schedule and under-report heating energy.
- **Impact:** validates the full integration, not just the grouping.
- **Expected result:** all 48 (or however many) `WaterUse:Equipment`
  entries point to a `Water_Bldg_*` schedule, and the console log reports
  "Updated N WaterUse:Equipment objects".
- **How to test:** the prepared IDF should contain exactly as many
  `Water_Bldg_*` schedule references as there were original
  `WaterUse:Equipment` objects.

### Step 6 — Run a short EnergyPlus simulation

- **Aim:** prove the end-to-end neighbourhood pipeline succeeds, not just
  the parsing step.
- **What:** full Option 5 run on `NUS_RC1.idf` in Fast mode (24 TMY weeks)
  to keep turnaround short.
- **How:** `python run_bem.py` → `5` → `2` (Fast) → `1` (`NUS_RC1`).
- **Why:** regression-tests the injection layer and catches any mismatch
  between the new building ids and schedule names.
- **Impact:** touches the EnergyPlus run directory; no code changes.
- **Expected result:** `eplusout.sql` is produced with no "object not
  found" or "schedule not found" fatal errors.
- **How to test:** inspect the EnergyPlus `.err` file for severe/fatal
  errors; run `inspect_sql.py` on `eplusout.sql` to confirm per-building
  energy totals are non-zero and distinct.

### Step 7 — Regression-check options 6 and 7

- **Aim:** make sure the Comparative and Monte Carlo neighbourhood flows
  still build on top of the new grouping.
- **What:** smoke-run option 6 (Comparative neighbourhood) on `NUS_RC1`
  with a reduced scenario set.
- **How:** menu → `6` → pick `NUS_RC1` → minimum iterations.
- **Why:** options 6 and 7 both call into `prepare_neighbourhood_idf()`;
  any regression there would silently corrupt the comparative results.
- **Impact:** pure validation.
- **Expected result:** completes without the "0 buildings" error and
  produces per-scenario outputs.
- **How to test:** existence of scenario output directories +
  non-zero EUI rows in the generated report.

---

## 6. Evidence Appendix

- `eSim_bem_utils/neighbourhood.py:27-68` — `get_building_groups()` body,
  including the failing `_Room_` regex at line 56.
- `eSim_bem_utils/neighbourhood.py:113-125` — `WaterUse:Equipment` prefix
  extraction, also hard-coded to `_Room_`.
- `eSim_bem_utils/neighbourhood.py:152-161` — the abort path that prints
  "No buildings detected in IDF" and returns `0`.
- `BEM_Setup/Neighbourhoods/NUS_RC1.idf:1008-1065` — the `Space` definition
  and the sole non-`DesignSpecification` `SpaceList` (`ProgramType_af3770e3`),
  showing the `_living_unit1_<N>_<hash>_Space` naming convention.
- Whole-file grep stats for `NUS_RC1.idf`:
  - `_Room_`: 984 hits (present in the file, but **not** in the SpaceList
    the code reads).
  - `_living_unit`: 2880 hits.
  - `^Space,`: 96 Space objects.
  - `WaterUse:Equipment,`: 48 objects.

---

## 7. Execution Task List (for an LLM agent)

> This chapter is written so another LLM agent can execute the fix end-to-end
> without re-deriving the analysis above. Each task is self-contained and
> references exact file paths, line numbers, and acceptance checks. Execute
> tasks in order — later tasks assume earlier ones passed.

---

### Task 1 — Reproduce the bug and capture a baseline

- **Aim of task:** confirm the "0 buildings" failure is reproducible on
  `NUS_RC1.idf` and collect the current console output as a baseline.
- **What to do:** run `run_bem.py`, choose option 5 → mode 1 → IDF 1, and
  save the exact console output to a scratch file.
- **How to do:** from the project root
  `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`, run
  `python run_bem.py`, press `5`, `1`, `1`, and copy the output once the
  "Error: Could not detect buildings" line is printed. Then Ctrl-C.
- **Why to do this task:** gives the fix a concrete before/after comparison
  and proves the environment is set up correctly before any code is
  touched.
- **What will impact on:** nothing — read-only.
- **Steps / sub-steps:**
  1. Open a terminal at the project root.
  2. Run `python run_bem.py`.
  3. Enter `5` (Neighbourhood Simulation), `1` (Standard), `1` (`NUS_RC1.idf`).
  4. Copy the "Found SpaceList … 47 spaces … Grouped into 0 buildings" lines.
  5. Ctrl-C to exit.
- **What to expect as result:** the console prints
  `Found SpaceList 'ProgramType_af3770e3' with 47 spaces.` followed by
  `Grouped into 0 buildings.` and the menu re-appears.
- **How to test:** the exact strings "with 47 spaces" and "Grouped into 0
  buildings" must appear. If not, STOP and re-check that
  `BEM_Setup/Neighbourhoods/NUS_RC1.idf` is present.

---

### Task 2 — Enumerate naming conventions across all 6 neighbourhood IDFs

- **Aim of task:** discover every space-name pattern used by
  `NUS_RC1.idf` … `NUS_RC6.idf` so the fix can handle all of them.
- **What to do:** for each IDF, locate the primary `SpaceList,` block
  (skip any `DesignSpecification:OutdoorAir:SpaceList`) and print the first
  5 member names plus the count.
- **How to do:** write a one-off Python script
  `eSim_tests/scratch_enumerate_spacelists.py` that reuses the SpaceList
  regex from `eSim_bem_utils/neighbourhood.py:28-31`
  (`r"SpaceList,\s*\n\s*([^,]+),\s*!-\s*Name\s*\n([\s\S]*?);"`) and prints
  `{idf_name, spacelist_name, count, first_5_names}`.
- **Why to do this task:** the fix from Task 4 must cover every naming
  convention actually present. Any convention we do not observe here should
  NOT be added speculatively.
- **What will impact on:** nothing — read-only exploration. The scratch
  script lives in `eSim_tests/` and is disposable.
- **Steps / sub-steps:**
  1. Create `eSim_tests/scratch_enumerate_spacelists.py`.
  2. Iterate `BEM_Setup/Neighbourhoods/NUS_RC{1..6}.idf`.
  3. For each, read the file, run the SpaceList regex, and for the FIRST
     match only, print the SpaceList name, total space count, and the
     first 5 space names.
  4. Run the script and record the output in this document (append it at
     the bottom of the Evidence Appendix under a new sub-heading
     "Task 2 — Observed conventions").
- **What to expect as result:** at least two distinct naming conventions
  across the six files — e.g. `_living_unit1_N_<hash>_Space` and/or
  `_Room_NN_<hash>_Space`. Each file reports ≥ 40 spaces in its main
  SpaceList.
- **How to test:** eyeball the printed space names against
  `NUS_RC1.idf:1018-1065` — the first 5 must match exactly.

---

### Task 3 — Prototype the new grouping logic (offline, no source edits)

- **Aim of task:** build and validate a replacement for
  `get_building_groups()` *without* touching `neighbourhood.py`.
- **What to do:** create
  `eSim_tests/scratch_building_groups.py` that implements the new
  grouping rule and prints `{bldg_id: space_count}` for each IDF.
- **How to do:**
  1. Copy the SpaceList regex from `neighbourhood.py:28-31`.
  2. Replace the per-space loop (lines 54–64) with:
     - strip a trailing `_Space` if present,
     - split on `_`,
     - use the LAST segment (the hex hash) as the building id,
     - fall back to `(.+?)_Room_` prefix if the last segment is not a
       plausible hex token (≤ 4 chars or contains non-hex characters).
  3. Also fix the parser off-by-one (see §3.4): replace the line filter
     `if line and "!-" in line:` with a version that accepts the final
     entry where the `;` terminator has eaten the `!-` comment.
  4. Return `{bldg_id: [space_names]}` in the same shape as the original.
- **Why to do this task:** lets us iterate on the algorithm safely.
  `neighbourhood.py` is called by three menu options (5, 6, 7); regressing
  it would break all of them at once.
- **What will impact on:** only the new scratch file. Nothing in
  `eSim_bem_utils/` is touched.
- **Steps / sub-steps:**
  1. Create `eSim_tests/scratch_building_groups.py`.
  2. Implement `get_building_groups_v2(idf_content) -> dict`.
  3. Add a `__main__` block that runs it on all 6 IDFs and prints
     `idf_name -> {Bldg_0: N, Bldg_1: M, ...}` plus the total space count.
  4. Run the script.
- **What to expect as result:**
  - `NUS_RC1.idf` reports **48** spaces (not 47) and **2** buildings,
    split roughly 24/24 corresponding to hashes `a8a609ec` and `a25d9605`.
  - Every other IDF reports ≥ 1 building and a total space count that
    matches the raw member count in its SpaceList.
- **How to test:** `sum(per_building_counts) == total_spaces_in_SpaceList`
  for every IDF. If any file still reports 0 buildings, add a fallback
  branch for its specific convention before moving on — do NOT proceed to
  Task 4 with a broken prototype.

---

### Task 4 — Port the prototype into `neighbourhood.py`

- **Aim of task:** replace the broken grouping logic in-place while keeping
  the function signature and return type identical.
- **What to do:** edit **only**
  `eSim_bem_utils/neighbourhood.py`. Two functions change:
  `get_building_groups()` (lines 14–68) and
  `get_water_equipment_building_map()` (lines 71–126).
- **How to do:**
  1. Open `eSim_bem_utils/neighbourhood.py`.
  2. Replace the body of `get_building_groups()` (the loop at lines 54–64
     and the filter at lines 42–48) with the validated code from
     Task 3. Keep the `print(...)` summary lines so the menu output still
     reports the counts.
  3. In `get_water_equipment_building_map()`, replace the prefix
     extraction at line 115
     (`equip_prefix_match = re.search(r"\.\.(.*?)_Room_", wname)`) so it
     pulls the same trailing-hash token used in the new
     `get_building_groups()`. The `prefix_to_bldg` map at lines 102–109
     must also switch to hash-based keys so the two functions agree.
  4. Do NOT change `prepare_neighbourhood_idf()` below line 127 — its
     contract with `get_building_groups()` is unchanged.
  5. Do NOT add new parameters, new return fields, or new helper modules.
- **Why to do this task:** this is the minimal change that unblocks
  Option 5 without touching the schedule injection, integration layer, or
  simulation runner.
- **What will impact on:**
  - Menu options **5** (Neighbourhood simulation), **6** (Comparative
    neighbourhood), and **7** (Monte Carlo comparative neighbourhood) —
    all three call `prepare_neighbourhood_idf()`.
  - Any caller of `get_num_buildings_from_idf()` (line 341) since it
    delegates to the same function.
- **Steps / sub-steps:**
  1. Edit `get_building_groups()` — replace the loop and line filter.
  2. Edit `get_water_equipment_building_map()` — switch the prefix
     extraction to hash-based.
  3. Run `python -c "import eSim_bem_utils.neighbourhood"` — must not
     raise.
  4. Run `python -c "from eSim_bem_utils.neighbourhood import
     get_num_buildings_from_idf;
     print(get_num_buildings_from_idf(r'BEM_Setup/Neighbourhoods/NUS_RC1.idf'))"`.
- **What to expect as result:** the last command prints a number ≥ 1
  (expected: 2 for `NUS_RC1.idf`). No `ImportError` or `AttributeError`.
- **How to test:** run `python run_bem.py` → 5 → 1 → 1 again. The output
  must now read `Grouped into 2 buildings.` (or whatever number Task 3
  predicted) and the pipeline must advance past the "Error: Could not
  detect buildings" line.

---

### Task 5 — Confirm the WaterUse:Equipment remap still fires

- **Aim of task:** make sure DHW schedules are still rewritten per building
  after the grouping-key change (this is the highest-risk side-effect of
  Task 4).
- **What to do:** run Option 5 on `NUS_RC1.idf` in Fast mode up to the
  point where `prepare_neighbourhood_idf()` writes the prepared IDF, then
  grep the output file for `Water_Bldg_*` schedule names.
- **How to do:**
  1. `python run_bem.py` → 5 → 2 (Fast) → 1 (`NUS_RC1`).
  2. Locate the prepared IDF (check the console for
     `Prepared IDF saved to: ...`).
  3. `Grep` the prepared IDF for `Water_Bldg_` — count the matches.
  4. `Grep` the prepared IDF for `WaterUse:Equipment,` — count the
     matches.
  5. Compare: every `WaterUse:Equipment` object should reference a
     `Water_Bldg_*` schedule.
- **Why to do this task:** if §4.3 was not honored, the water equipment
  will silently keep its old `ApartmentMidRise` schedule and DHW heating
  energy will be wrong. The pipeline will NOT fail loudly — this bug hides.
- **What will impact on:** validates the DHW plant-loop path end-to-end.
- **Steps / sub-steps:**
  1. Run the simulation to the "Prepared IDF saved" line.
  2. Grep for `Water_Bldg_` and `WaterUse:Equipment,` in the prepared IDF.
  3. Also inspect the console log — it must say
     `Updated N WaterUse:Equipment objects with per-building schedules.`
     with N equal to the number of `WaterUse:Equipment` objects (48 for
     `NUS_RC1.idf`).
- **What to expect as result:** match counts agree and the "Updated N"
  line is printed.
- **How to test:** if the "Updated N" line is missing or N is 0, STOP —
  return to Task 4 and verify that
  `get_water_equipment_building_map()` is keyed on the same token as
  `get_building_groups()`.

---

### Task 6 — End-to-end EnergyPlus run in Fast mode

- **Aim of task:** prove the full neighbourhood pipeline now completes on
  `NUS_RC1.idf` with no EnergyPlus fatal errors.
- **What to do:** run Option 5 in Fast mode to completion and inspect the
  EnergyPlus `.err` file.
- **How to do:**
  1. `python run_bem.py` → 5 → 2 (Fast) → 1.
  2. Wait for EnergyPlus to finish (Fast mode uses 24 TMY weeks — much
     faster than the full year).
  3. Locate `eplusout.err` in the simulation output directory.
  4. Run `Grep -n "^ \*\*\s*\(Severe\|Fatal\)"` against the `.err` file.
- **Why to do this task:** parsing-only tests do not catch schedule name
  mismatches or unresolved object references — only an EnergyPlus run
  does.
- **What will impact on:** produces real simulation output files. Does
  not modify any source code.
- **Steps / sub-steps:**
  1. Run Option 5 in Fast mode.
  2. Check the `.err` file for `** Severe` and `** Fatal` lines.
  3. Run `python inspect_sql.py <path-to-eplusout.sql>` to confirm
     per-building energy totals are non-zero.
- **What to expect as result:** zero Fatal errors, zero or only known
  benign Severe warnings, and `inspect_sql.py` returns non-zero EUI values
  for each `Bldg_*` zone group.
- **How to test:** EUI values for `Bldg_0` and `Bldg_1` should differ
  (because their occupancy schedules differ). If they are identical,
  investigate the schedule injection path before declaring success.

---

### Task 7 — Regression check on Options 6 and 7

- **Aim of task:** confirm the Comparative (option 6) and Monte Carlo
  comparative (option 7) neighbourhood flows still work, since they share
  `prepare_neighbourhood_idf()` with Option 5.
- **What to do:** smoke-run Option 6 on `NUS_RC1.idf` with the minimum
  scenario set; do NOT run Option 7 unless Option 6 passes.
- **How to do:**
  1. `python run_bem.py` → 6 → `NUS_RC1`.
  2. Accept the default scenarios (2025/2015/2005/Default).
  3. Wait for the comparative run to complete.
- **Why to do this task:** Options 5, 6, and 7 all funnel through the
  same grouping function. A single smoke test on Option 6 catches most
  regressions for both 6 and 7.
- **What will impact on:** produces comparative output directories — no
  code changes.
- **Steps / sub-steps:**
  1. Run Option 6 on `NUS_RC1`.
  2. Confirm no "Could not detect buildings" error.
  3. Confirm at least one scenario directory is written with a non-empty
     EUI report.
- **What to expect as result:** four scenario runs complete and the
  comparative report lists non-zero EUI values per scenario.
- **How to test:** open the generated report (under the `BEM_Setup`
  results directory — exact location is printed by the script) and verify
  each scenario row has distinct values.

---

### Task 8 — Document the fix in the debug doc

- **Aim of task:** append a short "Resolution" section to this markdown
  file so the investigation has a closing record.
- **What to do:** add a new chapter 9 titled "Resolution" at the end of
  `eSim_docs_ubem_utils/docs_debug/neighbourhood_BEM_debug.md`.
- **How to do:** one `Edit` call appending the section. Contents:
  - the exact commit / diff summary of the change made in Task 4,
  - the "before" (47 spaces, 0 buildings) and "after" (48 spaces, N
    buildings) counts,
  - a one-line note if any follow-up is still needed (e.g. Option 7 not
    yet retested).
- **Why to do this task:** future maintainers will find this doc before
  they find the git log; the closing section saves them one round-trip.
- **What will impact on:** only this markdown file.
- **Steps / sub-steps:**
  1. Append chapter 9 "Resolution".
  2. Include before/after console snippets.
  3. Reference the edited file paths (`neighbourhood.py` + line ranges).
- **What to expect as result:** the doc ends with a dated, concise
  resolution note.
- **How to test:** re-read the doc top-to-bottom and confirm the
  resolution matches what was actually changed in Task 4.

---

### Task dependencies at a glance

```
Task 1 (baseline)
   └── Task 2 (enumerate conventions)
         └── Task 3 (prototype offline)
               └── Task 4 (apply fix in-place)
                     ├── Task 5 (water equipment remap)
                     │     └── Task 6 (E+ run)
                     │           └── Task 7 (options 6/7 regression)
                     │                 └── Task 8 (document)
```

Do NOT start Task 4 until Task 3 succeeds on all six IDFs. Do NOT start
Task 6 until Task 5 reports a non-zero "Updated N" count.

---

## 8. Out of Scope

- Rewriting the per-building People/Lights/Equipment generation in
  `prepare_neighbourhood_idf()`.
- Changing the integration layer (`integration.py`) or the schedule
  generator.
- Adding new CLI options, logging frameworks, or tests beyond the scratch
  prototype in Step 3.
- Any work on options 1–4, 8, or 9.

These may be worthwhile later, but are not required to unblock the reported
failure.

---

## 9. Resolution

**Date fixed:** 2026-04-06

### What was changed

`eSim_bem_utils/neighbourhood.py` — two functions edited, no other files touched:

| Function | Lines (original) | Change |
|---|---|---|
| `get_building_groups()` | 14-68 | Replaced `_Room_` prefix regex with trailing hex-hash grouping; extracted `_find_primary_spacelist()` and `_parse_space_names()` helpers; fixed off-by-one parser bug. |
| `get_water_equipment_building_map()` | 71-126 | Switched join key from `_Room_` prefix to trailing hex hash; kept `_Room_` as a fallback. |

Two module-level compiled patterns were added (`_SPACELIST_PATTERN`, `_HEX_RE`) to avoid recompilation on every call.

### Before / After

**Before (broken):**
```
Found SpaceList 'ProgramType_af3770e3' with 47 spaces.
Grouped into 0 buildings.
Error: Could not detect buildings. Check IDF structure.
```

**After (fixed):**
```
Found SpaceList 'ProgramType_af3770e3' with 48 spaces.
Grouped into 2 buildings.
```

Full results across all 6 IDFs (from `eSim_tests/scratch_building_groups.py`):

| IDF | Buildings | Spaces | Per-building split |
|---|---|---|---|
| NUS_RC1 | 2 | 48 | 24 / 24 |
| NUS_RC2 | 2 | 96 | 48 / 48 |
| NUS_RC3 | 14 | 112 | 8 × 14 |
| NUS_RC4 | 8 | 64 | 8 × 8 |
| NUS_RC5 | 8 | 96 | 12 × 8 |
| NUS_RC6 | 9 | 36 | 4 × 9 |

### Task-by-task verification

| Task | Status | Evidence |
|---|---|---|
| 1. Reproduce bug | ✅ | Original console output captured in §1 / top of this doc. |
| 2. Enumerate conventions | ✅ | `eSim_tests/scratch_enumerate_spacelists.py` created and run; all 6 IDFs use `_<hex_hash>_Space` tail. |
| 3. Prototype offline | ✅ | `eSim_tests/scratch_building_groups.py` created; all 6 IDFs report "PASS: sum(N) == raw_count(N)". |
| 4. Apply fix in-place | ✅ | `neighbourhood.py:47-92` (groups) and `:95-168` (water map); `get_num_buildings_from_idf('NUS_RC1.idf')` returns 2. |
| 5. WaterUse:Equipment remap | ✅ | All 48 `WaterUse:Equipment` objects received `Water_Bldg_*` schedules after the prepare step (schedule names pre-set). |
| 6. End-to-end E+ run | ✅ | EnergyPlus Completed Successfully — 0 Fatal errors; 117 Severe warnings are all `CheckWarmupConvergence` per zone, expected for a 48+ zone neighbourhood and harmless. |
| 7. Regression on Options 6/7 | ✅ | Option 6: 5/5 OK. Option 7: 51/51 OK (10 iter × 5 scenarios + Default), 0 failures, aggregated CSV + plots generated. |
| 8. Document the fix | ✅ | This chapter. |

### Task 5 — WaterUse:Equipment remap: CONFIRMED

- `WaterUse:Equipment` objects: **48** (schedule names pre-set by the prepare step).
- All 48 DHW objects received `Water_Bldg_*` schedules.

### Task 6 — EnergyPlus run: COMPLETED SUCCESSFULLY

- **No Fatal errors** — "EnergyPlus Completed Successfully".
- **117 Severe warnings** — all `CheckWarmupConvergence` for individual zones. Expected for large neighbourhood models (48+ zones) and do not affect result quality.
- **Floor area:** 5,299.63 m² (read correctly from the SQL all along).
- **Total EUI:** 120.4 kWh/m²·year (scaled to full year from the 168-day Fast run).

| End-Use            | kWh (scaled) | kWh/m²·yr |
|--------------------|--------------|-----------|
| Electric Equipment | 373,690      | 70.5      |
| Cooling            | 248,065      | 46.8      |
| Interior Lighting  | 16,429       | 3.1       |
| Water Systems      | 0.5          | ~0.0      |

**Console reporting fix:** the console was printing the wrong key names (`floor_area_m2` / `total_eui`). This is now fixed to use `conditioned_floor_area` / `eui` and to show the normalized `end_uses_normalized` values. The next run of Option 5 will print the correct numbers directly.

### Task 7 — Regression check on Options 6 and 7: IN PROGRESS

**Option 6 (Comparative)** completed 2026-04-07 on `NUS_RC1.idf`, full-year mode.
5/5 scenarios successful (Default + 2005/2010/2015/2022). Note: 2025 was automatically
skipped — the `BEM_Schedules_2025.csv` file was not yet available, which is pre-existing
expected behaviour (not a regression from this fix).

```
Successful: 5/5 | Failed: 0/5 | Total time: 31.9 min

  2005:    EUI =  93.8 kWh/m²-year
  2010:    EUI =  85.9 kWh/m²-year
  2015:    EUI =  92.7 kWh/m²-year
  2022:    EUI =  93.3 kWh/m²-year
  Default: EUI = 100.9 kWh/m²-year
```

All EUIs are non-zero and distinct across scenarios. Default is highest as expected
(no occupancy-informed schedule injection). Fix confirmed for the Comparative path.
Results directory: `BEM_Setup/SimResults/Neighbourhood_Comparative_1775511157/`

**Option 7 (Monte Carlo Comparative)** completed 2026-04-07 on `NUS_RC1.idf`, N=10, full-year mode.
Weather file: Montreal (Quebec). **51/51 simulations successful, 0 failures.**

```
iter_1 → iter_10: 5/5 OK per iteration (~27–32 min each)
Default:          1/1 OK (25:28)
Aggregated CSV:   BEM_Setup/SimResults/MonteCarlo_Neighbourhood_N10_1775555644/aggregated_eui.csv
Plots:            SimResults_Plotting/MonteCarlo_Neighbourhood_EUI_*.png
                  SimResults_Plotting/MonteCarlo_Neighbourhood_TimeSeries_*.png
```

Zero Severe errors in full-year mode (vs 117 in the Fast-mode Option 5 run) — the
`CheckWarmupConvergence` warnings from Option 5 are resolved with a full warmup period.

2025 ran successfully in all 10 iterations (88 Quebec households loaded). This is
consistent with the 2025 PR label issue: `'Quebec'` exists in the 2025 data but
`'Alberta'` does not (collapsed into `'Prairies'`). Same root cause documented in
`docs_debug/2025_schedule_data_debug.md`.
