# D-S6-1 (b) -- household re-split of `4J_step3_corpus.jsonl`

Ruled by the author 2026-08-18. Unit moved from respondent `(country, hid, pid)` to household `(country, hid)`; seed 42 and fraction 0.10 unchanged; selection procedure unchanged.

## The leak this removed, measured before removal

* households straddling the old respondent split: **4900** of 32205 (15.22 %)
* multi-respondent households: 21031
* records living in a straddling household: **15429** (21.06 % of the corpus)
* straddling households per country: {'es': 1448, 'it': 2883, 'uk': 569}

## The new split

* households: **32205** -> 3220 heldout / 28985 train
* respondents: 65334, none straddling
* diaries: **7328 heldout / 65926 train** of 73254 (heldout record fraction 0.1000, NOT adjusted to 0.10)

| country | diaries train | diaries heldout | households train | households heldout |
|---|---|---|---|---|
| es | 17332 | 1808 | 8640 | 901 |
| it | 34366 | 3894 | 16532 | 1903 |
| uk | 14228 | 1626 | 3813 | 416 |

## Integrity

* records compared against the pre-split backup: 73254
* records whose `text` differs: **0**
* records whose key differs: **0**
* records whose `split` label changed: 13149
* households straddling the new split: **0**; respondents straddling: **0**

The respondent-split corpus is kept at `/speed-scratch/o_iseri/4J_step3_corpus_respondent_split.jsonl`.
