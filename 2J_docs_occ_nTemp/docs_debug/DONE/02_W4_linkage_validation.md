# W4 Linkage Validation Protocol
**SWOT Item:** W4 — Census–GSS linkage is probabilistic, not anchored  
**Task:** TASK 3 in `00_SWOT_pipeline.md`  
**Status:** Protocol defined. Step 5 not yet run.  
**Date written:** 2026-04-09

---

## Purpose

Step 5 of the 25CEN22GSS pipeline assigns each Census record to a GSS activity
archetype using K-means clustering on the GSS side and a Random Forest
classifier trained on shared sociodemographic columns. Because there is no
shared respondent ID between Census and GSS, the linkage cannot be verified
directly. This document defines three independent, ground-truth-free checks
that together confirm whether the linkage is healthy enough to pass to Step 6
(profile selection) and ultimately Step 7 (BEM integration).

**Run order:** Check 1 → Check 2 → Check 3. Check 1 is mandatory; Checks 2
and 3 add confidence. All three must pass before Step 5 is declared done.

---

## Shared Inputs

The checks below refer to the following datasets produced or used by Step 5:

| Symbol | Description |
|--------|-------------|
| `C` | Census PUMF records (2021 or forecast year), weighted by `WEIGHT` |
| `G` | GSS respondent records (2015 + 2022 pooled), with activity episode arrays |
| `K` | Number of K-means archetypes (default sweep: 20, 30, 40, 50) |
| `LINK_COLS` | Shared sociodemographic columns used for linkage: `AGEGRP`, `SEX`, `HHSIZE`, `PR`, `LFTAG`, `NOCS` |
| `archetype[i]` | The archetype ID (0 … K−1) assigned to GSS respondent *i* |
| `pred_archetype[j]` | The archetype ID predicted by RF for Census record *j* |

---

## Check 1 — Marginal Recovery

### Aim
Confirm that the RF-predicted archetype assignment preserves the Census
weighted marginal distributions across all `LINK_COLS`. If the assignment is
good, records in each archetype should collectively reproduce the Census
population shares, because the archetypes were trained on the same columns.

### Pass/fail threshold

| Metric | Pass | Fail |
|--------|------|------|
| Max absolute marginal difference (any column, any category) | ≤ 2 percentage points | > 2 pp |
| Mean absolute marginal difference (averaged across all columns) | ≤ 1 pp | > 1 pp |

Both conditions must be satisfied simultaneously to pass.

### Pseudocode

```python
# Inputs:
#   census_df   — Census records with columns LINK_COLS + 'WEIGHT' + 'pred_archetype'
#   LINK_COLS   — list of columns to check

results = {}

for col in LINK_COLS:
    # Census marginal (weighted)
    census_marginal = (
        census_df.groupby(col)['WEIGHT'].sum()
        / census_df['WEIGHT'].sum()
    )

    # Recovered marginal: weight each archetype by its share of Census records,
    # then sum over all archetypes
    # (Equivalent: just use census_df directly — pred_archetype is a label,
    #  marginal is over LINK_COLS regardless of archetype assignment)
    # The check is: does the RF assign records in a way that distorts the
    # original marginal when we re-aggregate?
    recovered_marginal = (
        census_df.groupby(col)['WEIGHT'].sum()
        / census_df['WEIGHT'].sum()
    )
    # NOTE: if RF rejects records or duplicates them, recovered != census.
    # If every Census record gets exactly one archetype label, this is trivially
    # satisfied. The meaningful check is per-archetype marginal consistency:

    for k in range(K):
        subset = census_df[census_df['pred_archetype'] == k]
        if len(subset) == 0:
            continue
        archetype_marginal = (
            subset.groupby(col)['WEIGHT'].sum()
            / subset['WEIGHT'].sum()
        )
        diff = (archetype_marginal - census_marginal).abs()
        results[(col, k)] = diff

# Aggregate
all_diffs = pd.concat(results.values())
max_diff   = all_diffs.max()    # must be <= 0.02
mean_diff  = all_diffs.mean()   # must be <= 0.01

print(f"Max marginal diff:  {max_diff:.4f}  {'PASS' if max_diff <= 0.02 else 'FAIL'}")
print(f"Mean marginal diff: {mean_diff:.4f}  {'PASS' if mean_diff <= 0.01 else 'FAIL'}")
```

### Interpretation
- **Pass:** The RF does not systematically over- or under-assign any
  sociodemographic group to any archetype. Marginals are preserved.
- **Fail:** One or more groups are concentrated into a narrow subset of
  archetypes, creating a biased linkage. Inspect the failing column and
  archetype pair; likely cause is a missing or coarsely encoded `LINK_COLS`
  category in the RF training data.

---

## Check 2 — K-Stability Sweep (K = 20, 30, 40, 50)

### Aim
Confirm that the archetype structure is stable across K values, meaning that
the K-means clustering reflects real latent structure in the GSS data and is
not an artefact of a particular K choice.

### Pass/fail threshold

| Metric | Pass | Fail |
|--------|------|------|
| Adjusted Rand Index (ARI) between adjacent K solutions (20 vs 30, 30 vs 40, 40 vs 50) | ≥ 0.70 | < 0.70 |
| All three ARI pairs must pass | All ≥ 0.70 | Any < 0.70 |

ARI = 1.0 means identical partitions. ARI ≈ 0.0 means random agreement.
Threshold of 0.70 is a commonly accepted "substantial agreement" level for
clustering stability.

### Pseudocode

```python
from sklearn.metrics import adjusted_rand_score
import numpy as np

K_values = [20, 30, 40, 50]
labels = {}  # dict: K -> array of cluster labels for each GSS respondent

for K in K_values:
    kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
    # gss_features: GSS respondents × LINK_COLS (encoded as numeric)
    labels[K] = kmeans.fit_predict(gss_features)

# Compare adjacent K solutions
# To compare partitions of different K, we compare on the same set of records.
# ARI is symmetric and handles different K sizes correctly.
ari_scores = {}
pairs = [(20, 30), (30, 40), (40, 50)]

for K_a, K_b in pairs:
    ari = adjusted_rand_score(labels[K_a], labels[K_b])
    ari_scores[(K_a, K_b)] = ari
    status = 'PASS' if ari >= 0.70 else 'FAIL'
    print(f"ARI K={K_a} vs K={K_b}: {ari:.4f}  {status}")

overall = 'PASS' if all(v >= 0.70 for v in ari_scores.values()) else 'FAIL'
print(f"K-stability overall: {overall}")
```

### Interpretation
- **Pass:** The same GSS respondents group together regardless of K.
  Archetypes capture real population structure; K is a resolution choice,
  not a distortion.
- **Fail:** Partitions reshuffle substantially as K changes. Likely causes:
  (a) `LINK_COLS` features do not separate the GSS population meaningfully,
  or (b) the GSS sample is too small to support K archetypes stably.
  Remedies: reduce K range, add GSS-side activity features to clustering,
  or inspect whether `LFTAG`/`NOCS` encoding is too coarse.

### Additional diagnostic (optional)
Plot the within-cluster inertia (elbow curve) across K = 10–60 to confirm
there is a natural elbow. If the curve is flat throughout, the data has no
strong cluster structure and K-means is the wrong approach entirely.

---

## Check 3 — Held-Out GSS Test

### Aim
Confirm that the RF classifier, trained on `LINK_COLS` features alone, can
predict the correct archetype for GSS respondents it has never seen. This
directly tests whether the sociodemographic features are informative enough to
drive the linkage.

### Setup
- Hold out a random 10% of GSS respondents **before** fitting K-means.
- Fit K-means on the remaining 90% (training GSS).
- For held-out respondents, determine their "ground-truth" archetype by
  assigning them to the nearest K-means centroid using their full GSS
  feature vector (including activity columns, not just `LINK_COLS`).
- Train RF on the 90% training set using `LINK_COLS` → archetype label.
- Predict archetype for held-out respondents using only their `LINK_COLS`.
- Compare predicted archetype to ground-truth archetype.

### Pass/fail threshold

| Metric | Pass | Fail |
|--------|------|------|
| Held-out classification accuracy | ≥ 60% | < 60% |
| Weighted F1 score (accounts for class imbalance across archetypes) | ≥ 0.55 | < 0.55 |

Both conditions must be satisfied to pass. Use the same K as the production
run (default K = 30 unless Check 2 suggests otherwise).

### Pseudocode

```python
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

# gss_df: all GSS respondents with columns LINK_COLS + activity feature columns
# full_features: all columns (LINK_COLS + activity)
# link_features: LINK_COLS only

np.random.seed(42)
n = len(gss_df)
holdout_idx = np.random.choice(n, size=int(0.10 * n), replace=False)
train_idx   = np.setdiff1d(np.arange(n), holdout_idx)

gss_train   = gss_df.iloc[train_idx]
gss_holdout = gss_df.iloc[holdout_idx]

# Step 1: Fit K-means on training set (full feature vector)
K = 30  # production K
kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
train_labels = kmeans.fit_predict(gss_train[full_features])

# Step 2: Assign ground-truth labels to held-out set via nearest centroid
#         (using full features — this is their "true" archetype)
holdout_gt_labels = kmeans.predict(gss_holdout[full_features])

# Step 3: Train RF on training set using LINK_COLS only
rf = RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
rf.fit(gss_train[link_features], train_labels)

# Step 4: Predict held-out archetypes from LINK_COLS only
holdout_pred_labels = rf.predict(gss_holdout[link_features])

# Step 5: Evaluate
acc = accuracy_score(holdout_gt_labels, holdout_pred_labels)
f1  = f1_score(holdout_gt_labels, holdout_pred_labels, average='weighted')

print(f"Held-out accuracy: {acc:.4f}  {'PASS' if acc >= 0.60 else 'FAIL'}")
print(f"Weighted F1:       {f1:.4f}   {'PASS' if f1 >= 0.55 else 'FAIL'}")
```

### Interpretation
- **Pass:** The sociodemographic features in `LINK_COLS` carry enough
  information to recover the activity-based archetype for unseen respondents.
  The Census-to-GSS bridge is justified.
- **Fail:** `LINK_COLS` alone are not predictive of activity archetype.
  Possible causes: (a) the chosen columns are too coarse (e.g., AGEGRP in
  10-year bands loses too much signal), (b) K is too large (archetypes are
  too fine-grained to recover from demographics alone), or (c) the GSS and
  Census encode the same concept differently (encoding mismatch). Remedies:
  reduce K, refine column encoding, or add a column (e.g., DDAY_STRATA).

---

## Summary Table

| Check | Metric | Pass threshold | Fail action |
|-------|--------|----------------|-------------|
| 1. Marginal recovery | Max marginal diff | ≤ 2 pp | Inspect failing column/archetype pair; fix RF encoding |
| 1. Marginal recovery | Mean marginal diff | ≤ 1 pp | same |
| 2. K-stability (×3 pairs) | ARI adjacent K | ≥ 0.70 each | Reduce K range; inspect LINK_COLS encoding |
| 3. Held-out GSS | Accuracy | ≥ 60% | Reduce K; refine column encoding |
| 3. Held-out GSS | Weighted F1 | ≥ 0.55 | same |

**All five conditions must pass before Step 5 is declared validated.**

---

## Run Order and Reporting

1. Run on a 5 000-record Census subsample and 500-record GSS subsample first,
   to confirm the code runs end-to-end without errors.
2. Run on the full dataset when Step 5 executes.
3. Paste the numeric results (max/mean diff, three ARI values, accuracy, F1)
   into the Progress Log section below.

---

## Progress Log

*(Append results here when Step 5 runs.)*

| Date | Dataset | K | Check 1 max diff | Check 1 mean diff | ARI 20-30 | ARI 30-40 | ARI 40-50 | Acc | F1 | Overall |
|------|---------|---|-----------------|-------------------|-----------|-----------|-----------|-----|----|---------|
| — | — | — | — | — | — | — | — | — | — | pending |
