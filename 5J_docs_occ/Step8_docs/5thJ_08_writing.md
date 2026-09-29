# Step 8 — Writing (after the GPU window; no GPU needed)

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 8. Validation: `5thJ_08_writing_val.md`

Written 2026-09-28. November 2026.

---

## STATUS

⬜ NOT STARTED. Needs Steps 6 and 7 closed.

## AIM

Write the paper from the recorded verdicts, with a novelty claim that has a logged search behind it,
figures computed from frozen data, and declarations that fit a sole author and the three licences.

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| Not claimed: first building energy surrogate, first hourly residential stock surrogate, first to score a surrogate on differences | Overview, what makes it new |
| Park and Park 2023 cited as the source of the difference score; He et al. 2015 as the paired-design precedent | `Resources/nearest_work/NEAREST_WORK.md` |
| Manuscript in the 2J AE style; limitations written as limitations; gate verdicts as recorded | Parent Step 8; memory rules |
| No LLM or tool name anywhere except the AI declaration | Memory rule |
| Figures: data plots by script from frozen data only; image prompts for any drawing | CLAUDE.md |

## 8A. NOVELTY, FINISHED (owed from O-2)

* Li, Bae and Im 2021 read in full (ORNL report `10.2172/1817464`): its 107 inputs listed; the
  nearest-work row updated. If still unreachable, the author asks the ORNL library or the authors'
  institution for the file; the row stays "abstract only" and the paper does not lean on it.
* One logged search for P1 (occupancy sequence as surrogate input) and P4 (time-use diaries feeding a
  learned energy model): either a narrow outside round (prompt written under `Prompts/deepResearch/`,
  run by the author, vetted by the manager with the 7 steps), or the author's own Scopus or Web of
  Science search with the queries and hit counts saved. The words "first" or "to our knowledge" appear
  only if this search found nothing closer.
* Unread items from the RT45 vetting: Westermann and Evins 2019 review (reference list followed),
  the Vosoughkhosravi review, CityTFT 2025, Govindarajan 2025 full text.

## 8B. FIGURES (DRAFT list)

1. Design: one building, many households, the pair difference (image prompt; the graphical abstract
   script already exists at `figures/scripts/`).
2. Load accuracy per target and split (from `scores.parquet`).
3. Occupancy effect: surrogate ΔS against EnergyPlus ΔEP, S and C side by side (the key figure).
4. Peaks and lag.
5. District spread from the draws with the EnergyPlus subsample marked.
Each figure cites the file and md5 it was drawn from.

## 8C. DECLARATIONS AND DATA

* Sole author; funding as it applies (none unless one does); AI declaration names the tools used.
* Data sources cited as each licence asks: INE (Spanish credit line, Step 0), ISTAT (source cited,
  changes stated), UKDS (Sullivan and Gershuny 2023 cited and acknowledged, EUL clause 11; paper details
  sent to UKDS after publication, clause 12).
* Data availability: Spain- and Italy-derived campaign outputs and weights may be released under their
  licences; UK-derived outputs and weights are not released (clause 4); code released.

## 8D. VENUE (O-6)

Chosen after RQ1 and RQ2 verdicts exist, by the author; the manager writes one line per candidate on
fit and length, not a ranking.

## OUTPUTS

`writing/` folder (created when this step starts): manuscript, figures, declarations, cover letter.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written as a plan. Next: Steps 6 and 7.
