# 5J setup check against the 3J and 4J setups (read-only review, 2026-09-30)

Reviewer: read-only agent. Only named .md docs were read (list at the end). No UK file, no data file, no folder-wide search, no code run.
Format: precedent (doc:line) -> 5J (doc:line) -> matters? Short names: D2-8 = `Step2_docs/impl/2026-09-30_d2-8_multizone_design.md`; CD = `outputs_step2/campaign_design.md`;
R = `outputs_step5/step5_rules.md`; GF = `outputs_step4/gates_frozen.md`; S6/S7 = the Step 6 / Step 7 docs; 4J-S8 = `4J Step8 4thJ_08_bemSimulation.md`.

## 1. Simulation setup (EnergyPlus building, HVAC, schedules)

* Zoning. 4J-S8:606-621 (one zone per dwelling, because TABULA has no partition; no claim about WHERE gains land) -> 5J floors x dwellings, interior R 0.35/0.50 ASSUMED, mass spread over all sides (D2-8:3, 5-6; mz_repilot:22-24) -> matters: no for scoring (the surrogate is scored against its own EnergyPlus); yes for Step 8 text: the assumed interior layers need the 4J "assumed value written down" sentence (4J-S8:115-117).
* Heat gains. 4J-S8:551-575: occupancy replaced only the TIME shape of a fixed 3.0 W/m2 gain (annual mean held, so every difference is redistribution in time). 5J: fixed gain zeroed, People + appliance objects with each household's own design level (D2-8:38; multizone_builder:19 shows design levels 1,770 to 6,019 W) -> matters: YES. The 5J occupancy effect between two households mixes a LEVEL difference (size, appliance power) with a TIMING difference. See issue 2.
* HVAC and weather basis. 4J box: heating only, TMYx station chosen by measurement (4J-S8:121-135). 5J: ideal loads, heat 20 C, cool 26 C, no shading, no night ventilation, ERA5 actual diary years, 3 cities per country (CD:96, 126). -> matters: no for the surrogate, yes for realism claims: Madrid cooling 85 kWh/m2 above heating 69 (mz_repilot:56-58). 4J treated such level gaps as DECLARED LIMITATIONS, never corrected (4J-S8:10, FINDING 121-125, 122 timestep, 123 ground default 18 C). 5J wrapper also uses the E+ ground default (wrapper:25 warning). Same treatment recommended; open step 8.
* Calendar and clock. 4J-S8:200-209 and :234-249 (FINDING 131 Sunday-start RunPeriod, FINDING 141 diary day starts 04:00, 13,108 runs redone; Step9:718-725) -> 5J: presence files are rotated to midnight and the run year is 2010 for ES (wrapper:39; households_v2:23); the training calendar uses es 2010, it 2014 (R:35). -> matters: only Italy is not shown. Docs I read do not print the Italian RunPeriod start weekday (Wednesday for 2014) nor a "clock alignment seen failing" gate like 4J G7.19/G8.17. Ask for one printed line.
* Uninjected control first. 4J-S8:52-65 and 3J Overview:137-139 (two probes; byte-identical scenarios = FAIL; stale-output guard) -> 5J: replicate gate and "outputs differ from previous household" check, resume check (Step3:51-53, 88); B0 average-household run plays the control role -> matters: no, covered.
* Noise floor. Overview:145 says 4J saw identical input give different heating. 5J measured spread exactly 0 on the 4 targets; non-target columns differ 1e-15 / 3e-6 between hosts (Step3:88; GF:64) -> matters: low. The floor came from replicates at the end of one array (CD:105-106), so cross-node scatter may not be sampled. Floor 0 turns "above the floor" into "non-zero at 8 digits" (GF:62-64).
* Weights/household draw. 4J chaining `independent`, seed 1 (4J-S8:291-299); 5J households drawn by diary weight, lowest-pid person weight (households_v2:46) -> matters: no. But see issue 6 (are dev/val/test households independent in diary-day content).
* Builder reuse. 3J gave every unit the SAME household (D2-8:14-16); 5J gives every flat its own household (D2-8:64-69, 4J Step 10 precedent) -> matters: no, better than 3J. The price (neighbours differ inside a pair) is already a stated limitation (GF:26-28).

## 2. Training setup (splits, early stopping, seeds, baselines, control)

* Split unit. 4J-Step6:316-349 (respondent split leaked 21 % of records; household split re-labelled and proved) -> 5J splits by household and by building, never both in training and test (CD:40-47; R:94-98 amendment) -> matters: no, good. Small counts: 40/10/10 households, 30/5/5 buildings per country (CD:17, 45-48).
* Frozen before seeing results. 4J-Step6:406-484 (prereg md5, claim-level FAIL criteria, "all folds reported incl. worst", freeze clause :146-160). 5J: rules md5 + amendment log (R:1-8, 104), gates md5 (GF:1-7) -> matters: partly. No CLAIM-level rule yet: how many of the 32 cells (R:70-80) must pass for the paper to say "S works"? 4J wrote this down (Step6:180-185). Open for Step 6/8.
* Baseline strength. 4J-Step6:59-79 (strongest null is the bar). 5J B1 = sklearn HistGB, 20 random configs, tuned on hourly MSE; S has a pair loss and is selected on level + pair term (R:51-57, 63-68) -> matters: yes (frozen). Skill over B1 is a pass condition of G5J.3 (GF:57-59), and B1 never sees a pair-aware objective.
* Control. 4J-Step4:386-422 (permuted-label control, interlocks seen failing both ways). 5J C = winner retrained with household AND neighbour drivers taken from another run (R:82-88; G5J.4 GF:67) -> matters: yes. C removes ALL occupancy, level included, so failing G5J.3 is nearly guaranteed. Also "random other run" may hold the same household (about 1 in 40 for SFH/TH).
* Seeds. 4J: one fixed seed per fold (Step4:62-65, seed 42). 5J: grid at seed 1; winner and C at seeds 1-3, spread INFO (R:68-69, 88-89) -> matters: low. 16 configs on one seed picked by pass counts on a 5-building validation set is noisy; fine because the test is sealed.
* Leave-one-country-out. 4J: 3 folds, each trained on 2 countries, folds not basis-uniform and said so (Step6:615-664). 5J: two trainings, ONE training country each, config pinned from the ES+IT validation (R:90-93) -> matters: yes. The "new country" config was chosen with the other country's validation data in view; say so. Also S6 (:38-39) still says "three folds" and UK; Step 5 doc (5D) says "three extra trainings": stale.
* Hold-out reading rule. R:14-19 says never call load_split on test or loco lists. The loco lists hold test runs and open without the lock. Since the freeze (20:04) the file `gates_frozen.md5` exists, so the Step 3 refusal (Step3:63-64; GF:104) no longer blocks anything. Only the R1 reader and its open log guard Steps 5-6 -> matters: yes for Step 6 ("once" is not enforced by code).

## 3. Sealed test scoring setup

* Pre-registration + manifests. 4J G4.14 recomputes the prereg md5 in every run manifest (Step6:413-420). 5J S6:44-50 checks the scorer md5 and prints it -> matters: add the pinned checkpoint md5s and the split-list md5s to the same line; cheap.
* Scored once, verdicts stay. 4J: all folds reported, worst included, ceiling/Qwen arms labelled single-fold (Step4:255-256). S6:19-26, 52-58 -> same. Matters: no.
* Cluster resampling. 5J two-way bootstrap over buildings and households (GF:92). Test and validation hold ONE building in most class cells (Spain SFH 1, MFH 1, AB 1; Italy SFH 1, MFH 1, AB 1: CD:46-47) -> matters: yes (frozen), see issue 1.
* Noise floor / sign rule. GF:62-64: floor 0, so sign agreement is judged on every pair with |annual effect| above 0.001 kWh, including tiny ones. 4J analogue: effect smaller than between-diary spread was reported, not hidden (4J-S8:225-229) -> matters: medium; the effgood stand-in already fails G5J.3 in 15 of 32 cells (GF:78), kept as a result.
* Cell mix. 8 of the 32 cells are equipment electricity, which equals the input schedule times a design level (D2-8:52-57; R:42-45), and 8 more are total electricity, mostly equipment -> matters: low-medium. Pass counts and the winner rule (R:70-80) are padded by lookup cells; the heating and cooling cells (16) carry the real test.
* New country and district. S7:34-38 and S6:38-40 -> see issues 4 and 5.

## Candidate issues for 5J (ranked)

1. [FROZEN: Step 2 split design + Step 4 bootstrap] Resampling units too few. One test building per class per country in most cells (CD:46-47), and the bootstrap draws "unique building ids of the cell" (GF:92). With one building the draw is always that building, so the skill interval only reflects households and understates uncertainty for new-building splits. Raise: report the number of building units next to every interval, and state the interval is conditional on the building where n = 1.
2. [FROZEN: D2-8 gains + R8 control] Level versus timing is not separated. Two households differ in size and appliance level as well as in hourly timing (multizone_builder:19; 4J held the annual mean fixed, 4J-S8:551-575). A model that learns each household's mean level can pass R2 on hourly differences, and the blind control C is trivially beaten. Raise (cannot change C): add, as a REPORTED non-gated diagnostic in Step 6, a timing-only control (each household's drivers replaced by its own annual mean, same level, no timing) and score S and B1 on it; one extra scorer call, no gate edit.
3. [FROZEN: R5-R7] B1 never sees a pair objective while S does and is selected on it; skill over B1 is a pass condition. Raise: also report B1 refit with a pair-aware objective, or state the asymmetry in Methods. (Strongest-null precedent, 4J-Step6:59-79.)
4. [OPEN: Step 7] 7C compares the surrogate to the 4J Step 10 builder, which has heating only, no windows, no People object, no meters (D2-8:11-13) and a different interior model. Surrogate error would be mixed with builder error, and cooling and equipment cannot be checked at all. Also draws from "all Spanish households" include sizes never seen (Spain dev has no size 5; CD:44) and S7:41-43 mentions "Latin hypercube" ranges. Recommend building the 7C check with `5thJ_idf_mz.py` on the district's mapped dwellings, and reporting in-range / out-of-range household counts as well as dwelling counts.
5. [OPEN: Steps 5 and 6 docs] Stale text: S6:38-40, 50 (three LOCO folds, UK) and Step 5 doc 5D (three trainings) against R9 (two trainings, ES and IT only). Fix the docs before scoring; note that the LOCO config was tuned on both countries' validation (state it).
6. [UNVERIFIED, check first] Household independence. wrapper:38 shows the diary pool has 5,200 days; 4J chains household-years by drawing days from one pool (4J-S8:291-299). If dev, validation and test household-years draw days from the same pool, "new household" means new composition and assembly, not new diary days. Ask: what is the day-level overlap between dev and test households? (4J household-leak precedent, Step6:316-349.)
7. [OPEN: Step 6] Write the claim-level rule and the test-open log before scoring: (a) how many cells must pass; (b) a log listing every test-file open, so "scored once" is checkable; (c) Italian RunPeriod weekday line (section 1).
8. [OPEN: Step 8 writing] Treat Madrid cooling above heating, the E+ ground default, the 26 C setpoint and the assumed interior layers as declared limitations in the 4J style (G8.7 INFO permanently), not as corrections.

## Files opened (all .md; full paths)

* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step2_docs\impl\2026-09-30_d2-8_multizone_design.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step2_docs\outputs_step2\campaign_design.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step5_docs\outputs_step5\step5_rules.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step4_docs\outputs_step4\gates_frozen.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step6_docs\5thJ_06_sealedScoring.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step7_docs\5thJ_07_speedDistrict.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step2_docs\impl\2026-09-29_wp1_wrapper.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step2_docs\impl\2026-09-30_wp1_multizone_builder.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step2_docs\impl\2026-09-30_wp1_mz_repilot.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step2_docs\impl\2026-09-29_wp1_households_v2.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\5thJ_00_Occupancy_Surrogate_Pipeline_Overview.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step3_docs\5thJ_03_fullCampaign.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\Step5_docs\5thJ_05_surrogateTraining.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step8_docs\4thJ_08_bemSimulation.md (lines 1-663 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step9_docs\4thJ_09_enduseLoads.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step4_docs\4thJ_04_finetuneLLM.md
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step6_docs\4thJ_06_transfer.md (lines 1-793 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Step11_docs\4thJ_11_stockEndUseLoads.md (lines 1-180 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Resources\preprocessing_precedents.md (lines 1-120 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\Prompts\RESUME.md (lines 1-150 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\3rdJ_00_4split_Occupancy_Pipeline_Overview.md (lines 1-200 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step7_docs\3rdJ_07_bemIntegration_4split.md (lines 1-200 only)
* C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Prompts\RESUME.md (lines 1-120 only)
* Folder listings only (ls, no file opened): 4J_docs_occ, 4J Resources, Step10_docs, Step11_docs; 3J Leg3_4-split, Step7_docs, Step9_docs, Prompts; 5J_docs_occ and its Step folders.

Not opened: 4J pipeline Overview, any _val.md, 3J Step 9 main doc, 4J Step 10 doc. No UK diary, episode, manifest, schedule, IDF, output or weight file was opened.
