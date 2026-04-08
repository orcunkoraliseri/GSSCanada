# Randomized Household Sampling — Options 5 and 7

**File:** `eSim_bem_utils/main.py`  
**Applies to:** Option 5 (Neighbourhood Simulation, `option_neighbourhood_simulation`) and Option 7 (Batch Comparative Neighbourhood Monte Carlo, `option_batch_comparative_neighbourhood_simulation`)

> **Note on menu numbering:** Option 4 (`option_kfold_comparative_simulation`, single-building MC) already uses `random.choice` throughout and is not affected by the greedy-selection bug described here. The fixes in this document apply to Options 5 and 7 only.

---

## Problem Summary

Both options currently select households for injection into the neighbourhood IDF using a **deterministic greedy pattern**: they sort all households by SSE score against a target working-day profile and always pick the top-ranked available household for each required hhsize slot. This means:

- **Option 4**: Every single run produces the exact same neighbourhood — the top-ranked households never change.
- **Option 7**: Every iteration within a run can produce the same neighbourhood if the randomly-sampled `hhsize_profile` repeats (which is common with small `n_buildings` and a narrow hhsize distribution in the pool).

The fix for both is the same idea: **randomly sample from the top-scoring candidate pool** rather than always taking the first-ranked match.

---

## Option 7 Root Causes (Detailed)

### How the data flow works

Trace what happens for one iteration and one scenario year (e.g., `2025`):

1. `base_hhs = random.sample(candidate_pool, n_buildings)` — genuinely random draw from **2005** households (`main.py:1963`)
2. `hhsize_profile` is extracted from `base_hhs` — a short list of integers like `[2, 3, 2]` (`main.py:1967–1969`)
3. For the `2025` scenario, `scored_year_matches = integration.filter_matching_households(year_schedules)` produces `sorted_year_hhs` — **always the same deterministic sorted list**, because `year_schedules` never changes between iterations (`main.py:1994–1996`)
4. For each `target_hhsize` in `hhsize_profile`, the code walks `sorted_year_hhs` in order and grabs the **first available household** with that hhsize (`main.py:2005–2010`)

**The consequence:** The actual household injected for 2025 is always the top-ranked (by SSE) unused household with the matching hhsize, regardless of iteration. The randomness of `base_hhs` only determines which hhsize values appear in `hhsize_profile`. If two iterations produce the same sequence of hhsizes (e.g., both yield `[2, 2, 3]`), they inject exactly the same households into EnergyPlus and produce identical SQL output.

### Cause 1 — Year-scenario selection is deterministic greedy (primary bug)

**Location:** `main.py:1994–2027`

`sorted_year_hhs` is recomputed inside the `for k` loop but is identical every iteration (same input → same SSE scores → same sort). The greedy first-match at line 2005 always picks the same top-ranked household for each hhsize. The random `base_hhs` never reaches the injection step.

### Cause 2 — hhsize profile degeneracy collapses iteration diversity (compounding)

**Location:** `main.py:1955–1969`

With a small `n_buildings` (e.g., 5–8 buildings in the IDF) and a 2005 candidate pool where most households are 2- or 3-person, many random draws of `base_hhs` will produce the same hhsize sequence. When `hhsize_profile` repeats, Cause 1 guarantees identical outputs. This is why iter_1 and iter_5 collide even though `n_buildings` is not 1.

### Cause 3 — `filter_matching_households` called redundantly inside inner loop (minor, wasted CPU)

**Location:** `main.py:1995`

`scored_year_matches = integration.filter_matching_households(year_schedules)` is called on every iteration for every scenario but produces the same result every time. This is wasted work, not a correctness issue.

---

## Option 5 Root Cause

### How the data flow works

**Location:** `main.py:984–988`

```python
hh_ids = sorted_hh_ids
schedules_list = []
for i in range(n_buildings):
    hh_id = hh_ids[i % len(hh_ids)]  # Cycle top matches if not enough unique
    schedules_list.append({**all_schedules[hh_id], 'hh_id': hh_id})
```

Every run selects the same top-`n_buildings` households in the same order. There is no randomness at all. Each time you run Option 4, you simulate an identical neighbourhood.

---

## Fix Plan

---

### Task 1: Randomize year-scenario household selection in Option 7

**Aim:** Make each iteration inject a genuinely different set of households for each scenario year.

**What to do:** Replace the greedy first-match loop (`main.py:2000–2027`) with a random draw from a pool of well-scoring candidates matching each target hhsize.

**Why:** This is the minimal change that makes the random seed matter. The greedy walk currently renders iteration-to-iteration variation impossible when `hhsize_profile` repeats.

**What will it impact:** Every iteration now produces a distinct 2025 (and 2005/2010/2015/2022) household set, making the Monte Carlo uncertainty band meaningful.

**Steps:**

1. Before the `for target_hhsize` loop (after line 1998), build an `hhsize_pools` dict:

```python
from collections import defaultdict
hhsize_pools = defaultdict(list)
for hh in sorted_year_hhs:
    hs = year_schedules[hh].get('metadata', {}).get('hhsize', 0)
    hhsize_pools[hs].append(hh)
# sorted_year_hhs is already sorted by SSE (best first),
# so hhsize_pools[hs] is also best-first within each size.
```

2. Replace `main.py:2002–2014` with:

```python
# Draw randomly from top quarter of SSE-ranked candidates with the right hhsize
size_pool = [h for h in hhsize_pools[target_hhsize] if h not in used_hhs]
top_cut = max(1, len(size_pool) // 4)
if size_pool:
    hh_id = random.choice(size_pool[:top_cut])
    data = year_schedules[hh_id]
    used_hhs.add(hh_id)
    found_hh = hh_id
else:
    found_hh = None
```

3. Keep the existing fallback (lines 2016–2027) unchanged for the `found_hh is None` case.

**Expected result:** `sorted_year_hhs` is still the quality filter, but each iteration picks a different household from within the top-performing candidates. Iter_1 and Iter_5 will no longer be byte-identical.

**How to test:** Run Option 7 with N=5 iterations on a single EPW. Extract monthly heating from each `iter_*/2025/eplusout.sql` using `inspect_sql.py` or `eSim_tests/check_sql_results.py`. Jan heating values should vary across iterations instead of repeating 39.47 GJ.

---

### Task 2: Randomize household selection in Option 5

**Aim:** Make each run of Option 4 simulate a different representative neighbourhood instead of always using the same top-ranked households.

**What to do:** Replace the deterministic sequential assignment at `main.py:984–988` with a random sample drawn from the top-scoring candidate pool.

**Why:** A single deterministic run is not representative — it always picks the best-scoring households rather than a realistic cross-section. Random sampling within the top-scoring pool preserves quality filtering while allowing variability across runs.

**What will it impact:** Each run of Option 4 produces a different neighbourhood, which is more realistic. Repeated runs can be used as an informal sensitivity check.

**Steps:**

1. Locate `main.py:984–988`:

```python
hh_ids = sorted_hh_ids
schedules_list = []
for i in range(n_buildings):
    hh_id = hh_ids[i % len(hh_ids)]
    schedules_list.append({**all_schedules[hh_id], 'hh_id': hh_id})
```

2. Replace with:

```python
import random
# Randomly sample from the top quarter of SSE-ranked candidates
top_cut = max(n_buildings, len(sorted_hh_ids) // 4)
sample_pool = sorted_hh_ids[:top_cut]
if len(sample_pool) >= n_buildings:
    hh_ids = random.sample(sample_pool, n_buildings)
else:
    # Pool too small — sample with replacement (fallback)
    hh_ids = [random.choice(sample_pool) for _ in range(n_buildings)]
schedules_list = [{**all_schedules[hh_id], 'hh_id': hh_id} for hh_id in hh_ids]
```

**Expected result:** Each run of Option 4 selects a different set of households from the top-scoring pool. The run-to-run EUI will no longer be byte-identical.

**How to test:** Run Option 4 twice on the same IDF and EPW. The resulting `eplusout.sql` files should differ. The EUI values should be in a similar range (same quality filter) but not equal.

---

### Task 3: Move `filter_matching_households` outside the iteration loop in Option 7

**Aim:** Eliminate redundant SSE scoring and sorting on every iteration.

**What to do:** Cache `sorted_year_hhs` per scenario before the `for k` loop starts.

**Why:** `filter_matching_households` iterates all households and sorts — currently called `iter_count × len(COMPARATIVE_YEARS)` times when it only needs to run once per scenario. For 10 iterations × 5 years = 50 redundant calls eliminated.

**What will it impact:** Faster run; no behavior change (same sorted list, just cached).

**Steps:**

1. Before `for k in range(iter_count):` (line 1946), add:

```python
# Pre-compute sorted household lists per scenario (identical every iteration)
sorted_year_hhs_cache = {}
for scenario in year_scenarios:
    if scenario not in all_schedules:
        continue
    sorted_year_hhs_cache[scenario] = [
        hh for hh, _ in integration.filter_matching_households(all_schedules[scenario])
    ]
```

2. Inside the `for k`/`for scenario` loop, replace lines 1994–1996 with:

```python
sorted_year_hhs = sorted_year_hhs_cache[scenario]
```

**How to test:** Add a print counter inside `filter_matching_households`; confirm it fires 5 times (once per year) instead of 50 for N=10 iterations.

---

### Task 4: Verify candidate pool is large enough for meaningful diversity

**Aim:** Confirm that the randomized pool in Tasks 1 and 2 actually has more than one candidate per hhsize slot.

**What to do:** Print per-hhsize pool sizes after building `hhsize_pools` (Option 7) and `sample_pool` (Option 4) and check that `top_cut > 1` for all required sizes.

**Why:** If a target hhsize has only 1 candidate, the random draw has no effect for that slot — it will always pick the same household.

**Steps (Option 7):**

After building `hhsize_pools` inside the `for scenario` block, add a one-time diagnostic (iteration 0 only):

```python
if k == 0:
    for hs, pool in sorted(hhsize_pools.items()):
        print(f"      {scenario} hhsize={hs}: {len(pool)} candidates "
              f"(top_cut={max(1, len(pool)//4)})")
```

**Steps (Option 4):**

After computing `sample_pool`, add:

```python
print(f"  Sampling pool: {len(sample_pool)} candidates (top_cut={top_cut}) "
      f"for {n_buildings} buildings.")
```

**If pool is too small:** The underlying issue is `BEM_Schedules_YYYY.csv` for older years having narrow hhsize coverage. Fix: widen the match to allow ±1 hhsize mismatch before falling back, and increase the `top_cut` fraction from top 25% to top 50%.

**Expected result:** Console output like `2025 hhsize=2: 3400 candidates (top_cut=850)` confirms genuine randomness is available. If you see `hhsize=4: 2 candidates (top_cut=1)`, that size slot is still deterministic — note it but accept it as a rare edge case.

---

## Summary Table

| # | Option | Location | Issue | Fix |
|---|---|---|---|---|
| 1 | 7 | `main.py:2000–2027` | Deterministic greedy selection nullifies `random.sample` | Replace first-match walk with `random.choice` from top-N hhsize pool |
| 2 | 5 | `main.py:984–988` | Always picks same top-N households every run | Replace sequential top-N with `random.sample` from top-25% pool |
| 3 | 7 | `main.py:1994–1996` | `filter_matching_households` called redundantly each iteration | Cache per-scenario outside `for k` loop |
| 4 | 5 & 7 | Both options | Pool may be too small for some hhsize values | Add diagnostic; widen ±1 hhsize tolerance if needed |

**Implementation order:** Task 1 and Task 2 are the correctness fixes — do these first. Task 3 is a performance improvement. Task 4 is a diagnostic to run after Tasks 1 and 2 to confirm the fix is effective.

---

## Progress Log

### 2026-04-08 — All tasks implemented in `eSim_bem_utils/main.py`

#### Task 1 — DONE: Randomized year-scenario selection (Option 7)
**Lines affected:** `main.py:2004–2051` (post-edit)  
Replaced the greedy first-match walk with a `defaultdict`-based per-hhsize pool and `random.choice` from the top-25% of SSE-ranked candidates. `found_hh` flag retained to route into the existing hhsize-fallback path unchanged. `from collections import defaultdict` added to the function-level imports at the top of `option_batch_comparative_neighbourhood_simulation`.

#### Task 2 — DONE: Randomized household selection (Option 5)
**Lines affected:** `main.py:984–995` (post-edit)  
Replaced the deterministic sequential top-N assignment with `random.sample` from the top-25% SSE-ranked pool (`top_cut = max(n_buildings, len(sorted_hh_ids) // 4)`). Falls back to `random.choice` with replacement if the pool is smaller than `n_buildings`. `import random` added locally at the point of use (consistent with the existing style in this file).

> **Note:** Menu Option 4 (`option_kfold_comparative_simulation`, single-building MC) was found to already use `random.choice(matching_hhs)` at line 1613 and does not have the greedy-selection bug. No changes were needed there.

#### Task 3 — DONE: Cache `filter_matching_households` outside the iteration loop (Option 7)
**Lines affected:** `main.py:1952–1968` (post-edit)  
Added `sorted_year_hhs_cache` dict built once before `for k in range(iter_count)`, iterating over `year_scenarios`. Also moved `first_schedules`, `first_year_scored`, `pool_size`, and `candidate_pool` out of the loop — all were recomputed identically each iteration. This eliminates `iter_count × len(COMPARATIVE_YEARS)` redundant calls (e.g., 50 calls → 5 for N=10). A status print confirms ranked candidate counts per scenario at startup.

#### Task 4 — DONE: Pool-size diagnostic added to both options (Options 5 & 7)
**Option 7 — Lines affected:** `main.py:2018–2022` (post-edit)  
On iteration `k == 0` only, prints per-hhsize candidate count and effective `top_cut` for each scenario year. Fires once per run before any simulation starts.  
**Option 4 — Lines affected:** `main.py:988` (post-edit)  
Prints `sample_pool` size and `top_cut` value before selection runs. Visible every time Option 4 is launched.

#### Verification — DONE: Randomization confirmed live on Option 7 run
**Run:** `MonteCarlo_Neighbourhood_N10_1775650731`  
**Method:** Compared `Occ_Bldg_0` schedule values in `iter_1/2025/Scenario_2025.idf` vs `iter_2/2025/Scenario_2025.idf` before simulations completed — IDFs are written before EnergyPlus runs so no need to wait for SQL output.

**Result:** Schedules are genuinely different across iterations. Key differences in `Occ_Bldg_0` weekday profile:

| Hour | iter_1 | iter_2 |
|---|---|---|
| 08:00 | 0.500 | 1.000 |
| 09:00 | 0.000 | 0.583 |
| 17:00 | 0.333 | 0.000 |
| Weekend 01:00 | 1.000 | 0.000 |

Different departure times and different weekend presence patterns confirm distinct households are being injected per iteration. The fix is working as intended.
