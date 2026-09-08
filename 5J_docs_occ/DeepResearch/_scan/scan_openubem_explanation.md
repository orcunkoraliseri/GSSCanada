# Scan: OpenUBEM docs_EXPLANATION digest

Source root: `C:\Users\o_iseri\Desktop\OpenUBEM\docs\docs_EXPLANATION\`
Purpose: faithful digest for planning the NEXT research paper building on OpenUBEM + an occupancy-generation pipeline.
Method: read-only scan, no edits, no web. Citations are `file:line` against the source files above.

---

## A. What OpenUBEM is (project's own words)

> "OpenUBEM is an **Urban Building Energy Modeling (UBEM)** platform. You give it a
> neighbourhood — an address, a coordinate, a bounding box, or an OpenStreetMap export — and
> it estimates the **annual energy use** and **carbon emissions** of **every building** in
> that neighbourhood." — `OpenUBEM_fundamentals.md:13-16`

> "It does this without per-building audits or metered data: each building is matched to a
> building *archetype*, turned into a physics-based EnergyPlus model, simulated for a full
> year, and rolled up into neighbourhood-level numbers." — `OpenUBEM_fundamentals.md:16-18`

> "each building still gets its **own** EnergyPlus model built from its **true footprint**
> (not a generic box), extruded to its real height, and shaded by its real neighbours. The
> archetype fills in the unknowns; the geometry and location are the building's own." —
> `OpenUBEM_fundamentals.md:29-31`

> "OpenUBEM is a **stock-level / neighbourhood** model. It is deliberately not a
> detailed-design tool: it does not model individual rooms, specific duct/plant networks,
> occupant behaviour per unit, or sub-hourly dynamics." — `OpenUBEM_fundamentals.md:290-292`

Intended users: "urban planners, energy researchers, and policy makers who need
building-level estimates at district scale." `OpenUBEM_fundamentals.md:19-20`

---

## B. Pipeline stages end-to-end

Five-stage spine, each writes a versioned artifact for the next (`OpenUBEM_fundamentals.md:44-53`):

1. **Data Acquisition** — downloads/cleans OSM building footprints → `01_buildings_clean.gpkg`. Module: `acquisition/osm_fetcher.py` (`OpenUBEM_inputs_reference.md:19`).
2. **Semantic Enrichment** — classifies archetype, assigns climate zone + weather file, attaches envelope/loads/schedules → `02b_buildings_enriched.gpkg`. Modules: `semantic/building_classifier.py`, `semantic/construction_sets.py`, `semantic/loads.py`, `semantic/schedules.py`, `semantic/imputation.py`, `semantic/fusion.py` (`OpenUBEM_inputs_reference.md:20-31`; `OpenUBEM_imputation_methods.md:23`).
3. **IDF Generation** — one EnergyPlus `.idf` per building: geometry, zoning, constructions, loads, schedules, HVAC, shading → `idfs/*.idf`. Modules: `geometry/zoning.py`, `geometry/layoutGenerator.py`, `geometry/layout_assigner.py`, `idf/builder.py`, `idf/hvac.py`, `idf/dhw.py`, `idf/cooking.py`, `idf/refrigeration.py` (`OpenUBEM_fundamentals.md:78-100`; `OpenUBEM_inputs_reference.md:33-37`).
4. **EnergyPlus Simulation** — runs EnergyPlus (v23.1) on the fleet in parallel → `04_simulation_manifest.parquet`. Module: `simulation/runner.py` (`OpenUBEM_fundamentals.md:47,61-65`; `OpenUBEM_inputs_reference.md:24`).
5. **Results, Carbon & Validation** — parses outputs to EUI, converts to carbon, aggregates to neighbourhood level, validates against measured data → `05_results.gpkg` + figures + interactive 3D viewer. Modules: `results/carbon.py`, `results/service_loads.py`, `viz/` (`OpenUBEM_fundamentals.md:48,336-363`).

**Stage 6 — Outdoor Microclimate & Thermal Comfort** exists but is explicitly *not* part of the standard-run spine: "invoked explicitly, never as part of a standard run," reads Stages 1-5 outputs read-only, writes its own `06_*` artifacts (`OpenUBEM_fundamentals.md:56-59`). Runner: `scripts/run_step6_microclimate.py` (`OpenUBEM_fundamentals.md:471-472,568-570`).

Two cross-cutting properties: **deterministic/reproducible** (seeded RNG, provenance columns, versioned schemas) and **resume-capable** (Step 4 manifest lets partial fleet runs resume) — `OpenUBEM_fundamentals.md:472-478`.

---

## C. Inputs (every dataset/source named in `OpenUBEM_inputs_reference.md`)

Bundled data ships inside the pip wheel under `openubem/data/` (frozen/versioned, each subfolder has a `PROVENANCE.md`); only two things are fetched live: OSM footprints (via `osmnx`→Overpass) and the EPW weather file (`OpenUBEM_inputs_reference.md:16-22`).

| # | Category | Real-world source | Coverage/notes |
|---|---|---|---|
|1|Building footprints & tags|OpenStreetMap live via `osmnx`→Overpass (`OpenUBEM_inputs_reference.md:26`)|No licence note stated beyond OSM being the source; runtime fetch|
|2|OSM tag→use-class map (~60 tags→6 classes)|Manually curated, DESIGN §3A Module 03 (`:27`)|Audited in `RESULT_I01`: ~24 common tags missing, fall to `unknown` (`:41-45`)|
|3|Archetype vocabulary (30 DOE/OpenStudio archetypes)|OpenStudio *Building Types and Templates* (NREL) (`:28`)|Audited in `RESULT_I02`: 3 of 6 size/level cut-points misclassify DOE's own prototypes (`:46-49`)|
|4|Climate zone polygons|US Census county boundaries + NREL ResStock (ASHRAE 169-2013) (`:29`)|US only|
|5|Weather station catalogue (~2,900 stations)|climate.onebuilding.org TMYx KML index (`:30`)|US-centric|
|6|Weather data (EPW, 8760 h)|climate.onebuilding.org primary / energyplus.net fallback (`:31`)|Runtime download, cached `~/.openubem/epw`|
|7|Envelope/construction (U-values, SHGC, infiltration)|ASHRAE 90.1-2019 via NREL `openstudio-standards` commit `83b1e64` (`:32`)|All 30 archetypes, incl. residential|
|8|Internal loads (LPD/EPD, occupant density, setpoints)|PNNL-20405 DOE Prototype Buildings + `openstudio-standards` (`:33`)| |
|9|Occupancy/lighting/equipment/setpoint schedules|Digitized DOE Commercial Prototype IDFs, ASHRAE 90.1-2013 ed. (energycodes.gov) (`:34`)|Hourly fractional, weekday/Sat/Sun, per archetype|
|10|HVAC system assignment (10 families: VAV/PSZ/PVAV/FCU/WLHP/PTAC…)|ASHRAE 90.1-2019 Appendix G + DOE baselines (`:35`)| |
|11|HVAC efficiency (COP)|DOE Commercial Reference Buildings + AHRI ratings (`:36`)| |
|12|Domestic hot water|PNNL commercial prototypes + ASHRAE 90.1 App. G (`:37`)| |
|13|Cooking loads|PNNL FSR/QSR prototypes + ASHRAE 90.1 §6.5.3.1 (`:38`)| |
|14|Refrigeration|ENERGY STAR Portfolio Manager + ASHRAE 90.1 App. G (`:39`)| |
|15|Service-load end-use fraction splits (legacy overlay)|CBECS 2018 + PNNL prototypes (deep-research Table 4) (`:40`)|Retired production path, kept behind flag (`:126-131`)|
|16|Archetype↔CBECS PBA crosswalk|CBECS 2018 (`:41`)|`RESULT_I03`: correct but coarser than CBECS sub-variables allow (`:50-52`)|
|17|Carbon intensity, electricity|EPA eGRID 2022, state + subregion (`:42`)|US only|
|18|Carbon intensity, natural gas|Iseri et al. (2025), *Energy & Buildings* 337 — fixed 0.181 kg CO2e/kWh (`:43`)| |
|19|EnergyPlus engine|EnergyPlus 23.1, user-installed, not bundled (`:44`)| |

**OSM→attribute mapping** (`OpenUBEM_inputs_reference.md:69-79`): `geometry`, `building=*`→`building_tag`, `amenity/shop/office=*`→`function_tag` (first non-null wins), `building:levels=*`→`levels` (NaN imputed), `height=*`→`height_m` (NaN = `levels×3.5m`), `start_date=*`→`year_built` (NaN KDE/PDE-imputed). Buildings <20 m² dropped as OSM noise. "Occupancy" (people/when/doing-what) is **not an OSM input at all** — comes entirely from the matched archetype's schedules/loads, not from anything observed about the specific building (`:84-87`).

**Validation / ground-truth datasets** (never pipeline inputs, report-only, never tuned to — `OpenUBEM_inputs_reference.md:154-165`):
- NYC Local Law 84 (LL84) disclosure, measured weather-normalized site EUI (EPA Portfolio Manager), CZ 4A.
- LA EBEWE (CA AB 802), measured site EUI, CZ 3B.
- CBECS 2018 West-South-Central region proxy for Austin (CZ 2A, no disclosure law).
- CBECS 2018 national survey — per-archetype distribution gates (NMBE, CV(RMSE), R², KS_D).
- U.S. Building Performance Database (BPD) — national, Level-4 city-scale calibration ground truth.
- Iseri et al. (2025), *Energy & Buildings* 337 — Bahçelievler, Turkey, 24 buildings, per-building heating EUI target ±10%, and the natural-gas carbon factor.

Licence/access: none of the rows state an explicit licence; OSM/CBECS/eGRID/ASHRAE/PNNL are the named upstream authorities, with `PROVENANCE.md` files per bundled folder recording exact commit/URL/date (`OpenUBEM_inputs_reference.md:17-18,175-186`).

---

## D. Imputation methods (`OpenUBEM_imputation_methods.md`)

**Why:** OSM is incomplete — `levels`, `year_built`, `height_m` are frequently missing and block downstream physics (floor area, envelope vintage, massing) (`:14-22`).

**Governing rule — zero fitted parameters:** imputation may copy an observed value, take a group median, sample a distribution fit on observed data, or average neighbours — but never learns/fits a correction coefficient, and imputed output is never fed back to tune thresholds (`:29-33`).

**Four-tier cascade, first hit wins** (`openubem/semantic/imputation.py::impute_missing`, `:39-50`):
1. **`fusion`** — real ground truth from external datasets (Overture Maps height/levels, LiDAR, municipal assessor), joined by location. On by default (no-op if unconfigured). Confidence HIGH/MED. Only tier producing ground truth, not an estimate (`:53-63`).
2. **`spatial`** — distance-weighted donor value from observed neighbours; falls back to group-mode if none in range (`:64-68`).
3. **`statistical`** — KDE (partly observed), PDE (bounded prior, wholly missing group), or group-mode/median; all draws clamped to observed `[min,max]` (`:70-79`).
4. **`ml`** (opt-in, off by default) — 6-method registry (`knn`, `missforest`, `rf`, `histgbm`, `mice`, `linear`) using all features jointly (`:81-85`).

**Arc phases A–E** (`:91-100`): A = base cascade (shipped); B = downstream-EUI validation of A on real cities (shipped, NYC NMBE +0.49%, LA +0.08%); C = `ml` tier (built-but-off, opt-in); D = `fusion` tier (source registry shipped; router completed by E-UTCI-09 sub-plan 2026-07-25); E = "frontier methods (deep-generative, GNN, **LLM**, TabPFN)" — **documented-deferred, none enter the default pipeline** (`:100`).

**No LLM-based imputation is currently implemented** — LLM appears only as a deferred Phase-E frontier-method candidate.

**The known limit — variance collapse** (§6, `:107-190`): imputed values (`year_built`, `levels`) collapse to a flat band vs. the real 1:1 diagonal — any single-best-estimate method (mode/median/donor-average/kNN-mean) mathematically pulls to central tendency; under zero-fitted-parameters there's no mechanism to reinject spread. Measured: `year_built` nyc_centre σ(imputed)/σ(real)=0.44, IQR of imputed = 0.0 (`:120-129`). NMBE is blind to this (unbiased-by-construction); KS statistic and Wasserstein distance do expose it (KS=0.50, W=24y for `year_built`) (`:157-166`). Rule going forward: "never present NMBE as an imputation-accuracy metric" (`:166`).

**Accepted, not fixed** (§7, `:194-213`): variance collapse doesn't bias the aggregate EUI (the platform's actual dependency); the `ml` tier is EUI-neutral so stays opt-in/off. **Condition that would change this:** a future application needing the *per-building distribution itself* (e.g. targeting retrofits, modelling stock variety) should move to a **donor draw** (hot-deck / predictive-mean-matching / PMM) — preserves variance and stays zero-fitted-parameters (`:207-213`). This `pmm` draw tier is **now built** (opt-in/off by default) and illustrated: variance ratio climbs 0.06→0.59 (`year_built`) and 0.31→0.90 (`levels`); point MAE gets slightly worse as the intended trade-off (`:172-190`). Two caveats: a genuine ~1951 mode spike (35% of observed values) legitimately produces a dense draw band there, and `year_built`/`levels` are **not inferable from footprint shape/location** at all — no stratifying columns (`use_class`, `archetype_id`) exist in the Stage-1 schema, so `pmm` degenerates to a global marginal bootstrap (`:181-189`).

No LLM/ML method is validated for per-building accuracy; validation reported is aggregate-EUI-level (NMBE) only, explicitly reframed as "aggregate-EUI unbiased (not per-building accurate)" (`:229`).

---

## E. Simulated vs. reconstructed methodology

**Simulated EUI** (§2): EnergyPlus, via `ZoneHVAC:IdealLoadsAirSystem` (ideal, 100%-efficient), meters only 4 end-uses — heating, cooling, lighting, plug/equipment; fans/pumps/DHW/refrigeration/cooking are **structurally absent**, not rounded to zero — "There is no object in the IDF that could produce them" (`simulated_vs_reconstructed_methodology.md:32-43`).

**Reconstructed EUI** (§3, superseded — see below): a *reporting-layer, no-resimulation* post-process that scales the 4 modeled end-uses up using CBECS-2018/PNNL Table-4 archetype fraction splits to estimate the 5 missing end-uses (`:47-91`). Formula: `E_total_est = (heat+cool+light+equip)/modeled_frac`; missing end-use `j` = `f_j × E_total_est` (`:97-108`). Uplift ranges +19–30% (office/apartment) up to +72% for restaurants/supermarkets.

**Ground truth used:** NYC LL84, LA EBEWE, Austin CBECS proxy (city-level measured EUI); CBECS 2018 national (NMBE/CV(RMSE)/R²/KS_D distribution gates). "Reconstruction is a reporting enhancement, not a calibration" — does not make individual buildings match reference more closely because the modeled-building gap is dominated by errors *inside* the 4 simulated end-uses, not by missing service loads (`:141-148`).

**Phase-E (2026-06-27) retired both IdealLoads and the reconstruction overlay** (§7, `:190-330`): real archetype-appropriate HVAC (central VAV+chiller/boiler for large offices, packaged RTUs, FCU/WLHP for hotels/high-rise, PTAC only for mid-rise residential) plus real EnergyPlus objects for DHW/cooking/refrigeration — all 9 end-uses physically computed, no estimation. This is the **adopted physical baseline** (`:317`).

**Counter-intuitive finding, stated explicitly:** the physically-complete Phase-E model scores **further** from measured city EUI (NYC −24.4%, Austin −25.7%) than the reconstructed overlay did (NYC +2.1%, Austin −8.6%) — but R² (distribution shape/ranking) *improves* sharply (0.895/0.924/0.718 vs ~0.71 flat) (`:213-231`). Root cause: reconstruction's simplified PTAC heating was a large over-count that happened to cancel an unmodeled "Other" loads under-count (elevators, IT/process, misc plug loads) — "right answer, wrong twice" (`:265-280`). Checked against DOE reference prototypes: Phase-E heating is **above**, never below, the reference — so the remaining gap is genuinely the unmodeled "Other" category, "accepted and documented, not calibrated away" per the zero-fitted-parameters rule (`:281-330`).

**Stated uncertainty framing:** "closer to measured ≠ more correct" (`:307`); the −24% city gap is a *lower bound* on the true structural "Other" deficit, not its full size (`:322-324`). One open, non-fitting diagnostic question remains: why Phase-E heating sits ~3–9× the DOE prototype (envelope/infiltration hypothesis, OSM-derived geometry on leakier-than-code envelope) — entangled with the LA hot-bias (`:325-330`).

---

## F. Outdoor / microclimate / heat analysis (Stage 6)

**Status:** built and live-run-verified on real geometry (`nyc_centre`, 738 buildings; all 12 validated cells, 8,160 buildings) — **explicitly not a headline output**, kept out of `05_results.*` because "UTCI is not validated against measured data, and EUI is" (`OpenUBEM_outdoor_analysis_reference.md:73-76`; `OpenUBEM_fundamentals.md:559-561`).

**What it computes** (`OpenUBEM_fundamentals.md:544-556`; `OpenUBEM_outdoor_analysis_reference.md:64-260`):
- **UTCI** (Universal Thermal Climate Index) — equivalent-temperature stress scale, 10 classes, derived from the UTCI-Fiala 187-node thermoregulation model via a COST-730/Bröde 210-term operational polynomial (RMSE 0.11°C vs full model). Reference person: 2.3 MET, self-adaptive clothing 0.3–2.6 clo.
- Four driver fields at pedestrian height (1.1 m): air temperature `Ta`, humidity, wind speed `v`, mean radiant temperature `Tmrt` (dominant driver, ≈+0.31°C UTCI per +1°C Tmrt).
- Radiative geometry: sky-view-factor, 32-azimuth horizon angles, shadow rasters (computed once per site).
- Surface temperatures: ground `T_grd` (empirical, live-verified) and facade `T_wall` — Tier 1 empirical (live-verified) / Tier 2 real EnergyPlus exterior surface temp (built, wired, **not yet exercised on a real run**) (`:380-395`).
- Exposure metrics: **PHEH** (person-hours >46°C) and **CTSI** (cumulative °C·h above 26°C comfort threshold), joined per-building onto energy results. Peak UTCI measured 44.6°C ("very strong heat stress"), mean CTSI 780°C·h, on a hot NYC July week (`OpenUBEM_fundamentals.md:562-565`).
- Five mitigation scenarios: `tree_canopy`, `pv_canopy`, `cool_pavement`, `cool_roof` (alias of cool_pavement), `high_albedo_facade` — domain-layer edits only (albedo/canopy), never physics changes (`OpenUBEM_outdoor_analysis_reference.md:434-465`).

**Cool-pavement paradox** — genuinely cools ground (12–15°C) and air (0.5–1.5°C) but *raises* pedestrian UTCI +0.5 to +2.5°C via reflected shortwave onto the body (view factor ≈0.5 to ground); design directive: deploy high-albedo surfaces only under shade (`:466-479`).

**Coupling:** one-way only, buildings→outdoors; outdoor field never feeds back into building cooling loads. Two-way coupling and CFD wind fields explicitly out of scope (`:398-412`).

**What is stubbed/not built:**
- SHVI (Spatial Heat Vulnerability Index) — **not built**, needs demographic rasters OpenUBEM doesn't have (`:422`).
- `T_wall` Tier 2 (real EnergyPlus surface temps) — built/wired but not yet run (`:385`).
- Future-candidates register, all "nothing specified, planned, or implemented" (`:486-505`): PET, SET*, WBGT (occupational heat-stress), pedestrian wind comfort (needs CFD), UHI intensity, outdoor daylight/glare, air-quality dispersion, outdoor acoustic comfort.
- Deliberately excluded (`:507-521`): CFD wind fields, two-way building↔microclimate coupling, agent-based pedestrian mobility, full 187-node Fiala model at runtime, sub-hourly dynamics, demographic vulnerability indices ("Better absent than fabricated").

**Accuracy framing:** polynomial near-exact; `Tmrt` field is where real error lives (published comparable models RMSE 2.5–4.2°C, R²>0.92 vs field radiometers). "**There is no measured outdoor-comfort data for our validated cities.** Every gate on this arc is internal-consistency or behavioural, never accuracy-vs-measurement" (`:230-236`). The `macdonald` in-canopy wind tier "validated to safely degrade, never validated as accurate" — falls back to `cost730` for 31.6% of cell-hours on real mid/high-rise domains (`:23-33,225`).

---

## G. Every stated limitation, open question, future work / roadmap item

**From `OpenUBEM_fundamentals.md`:**
- `layout_assign` mode **not certified for fleet-level EUI reporting** — floor-area-denominator mismatch: nominal floor area used even where EnergyPlus simulated a different (prototype) floor count; measured verified on only 6 buildings; most of fleet (6,939/7,442) unverified — `:174-190,235-244`.
- Fixed-capacity auxiliary equipment (transformers, DHW tanks, HVAC coils) not scaled with building — clean deterministic failure at storey-multiplier ≥8 — `:150-152`.
- Internal loads modelled as 2022-code construction regardless of real vintage (asymmetry vs. patched envelope) — Register item **OPEN-03** — `:161-169`.
- `zone`/room-level layout generator (`layoutGenerator.py`) — "**parked pending a root-level engine redesign** — the user explicitly excluded it as a direction currently being continued" (2026-08-04) — `:222-224`.
- `layout_assign` storey-matching mechanism: narrow reach by design (`n_proto ∈ {1,3}` only, only when real>prototype) — `:246-255`.
- Section 5.1/§8.5 European district viewers: three of four districts only **partly bound** (ES-MAD 957/1194 buildings, FR-LYO 290/530, GB-LDN 81/1242 residential buildings simulated); Bologna bound on an **imputed** construction period tagged `IMPUTED_CENSUS_SECTION_CONSTRUCTION_PERIOD`, no per-building observed year exists in any open source — `:434-478`.
- Grand Central Terminal / OSM-height-absent buildings render flat, honestly badged "Height: not in OSM — footprint only," never invented — `:398-404`.

**From `OpenUBEM_inputs_reference.md`:** `RESULT_I01`/`I02`/`I03` classification audit findings (§ above, all "not yet acted on, audit pending manager review") — `:38-52`.

**From `OpenUBEM_imputation_methods.md`:** variance collapse (§6, structural, accepted not fixed); `ml`/draw tiers opt-in/off by default; `year_built`/`levels` genuinely not inferable from footprint+location (no stratifying columns exist) — `:107-269`.

**From `simulated_vs_reconstructed_methodology.md` §5 (reconstruction limitations, now largely superseded by Phase-E but recorded):** refrigeration case-credit zone-feedback ignored; static CBECS-2018 operating conditions; CBECS pre-hybrid-work vintage; food-service buildings can reconstruct implausibly high, reported never capped; physics-based Tables 1-3 out of Phase-1 scope, numeric cells never transcribed (image-clipped in source PDF) — `:143-153`. Phase-E's own open item: heating ~3-9× DOE prototype, unresolved, entangled with LA hot-bias — `:325-330`.

**From `OpenUBEM_outdoor_analysis_reference.md`:** rural `height_m` residual gaps (nyc_rural 36.4%, austin_rural 19.2% still `NaN`) — `:230-233` and register `OPEN-12`; no measured outdoor-comfort ground truth exists at all for any validated city; `macdonald` wind tier not accurate outside low-rise regime; 3 of 5 mitigation scenarios undershoot literature magnitude for stated model-scope reasons (Tier-1 model omits transpirational air-cooling pathway; wall-reflection term is a deliberately simplified isotropic approximation) — `:441-448`; static census exposure metrics systematically under-count peak heat risk (real pedestrian movement not modelled) — `:428-430`.

**Debug-reference register (`OpenUBEM_debug_References.md`), open items snapshot 2026-08-20** (`:1682-1705`, 20 tracked items, authoritative list elsewhere in repo):
OPEN-09 thermal-mass warmup non-convergence (~3.66% fleet EUI-projection effect, unresolved); OPEN-10 `ZoneGroup` multiplier narrower than first claimed; OPEN-12 rural height residual (needs source coverage, not more imputation); OPEN-13 draw-tier test-collection abort contained not fixed; OPEN-14 UTCI height backfill not reproducible from clean checkout; OPEN-15/16/17 imputation tiers built but off, draw tier not a simple opt-in; OPEN-19 LA cells run ~+40% hot, no climate-zone/code-year switch exists; OPEN-20 wider validation matrix still needed; OPEN-27 DESIGN doc naming drift; OPEN-28 `05_results` archetype_id not reproducible from frozen input; OPEN-35 two fallbacks disagree on missing storey count; OPEN-38 `layout_assign` SmallHotel thermal runaway; OPEN-42 thermal-mass fix never merged to production; OPEN-48 **the adopted baseline run cannot be reproduced from this repository**; OPEN-51 defect ID reused for two signatures; OPEN-53 874/875 harvest dirs missing files; OPEN-54 `_ssh` never checks remote exit code; OPEN-55 unknown-archetype PDE bounds can draw data-centre loads; OPEN-56 10m³ zone-volume stub, ≈+1.0 kWh/m² understatement fleet-wide; OPEN-58 shared-cwd cross-contamination + wrong EUI formula; OPEN-59 unknown buildings run 1.7× classified after equipment fix; OPEN-60 `total_eui_kwh_m2` undercounts lighting/equipment under zone multipliers.

Section 17 "not-a-bug" list (`:1651-1676`) records accepted behaviours (E+'s 10 m³ volume clamp warning is benign but the underlying clamp is a real ~+1% EUI understatement; Windows/Linux float rounding is expected; imputer scatter "flatness" is inherent variance collapse, not a bug).

Note: most of Ch.1-16 and the EU-numbered findings (X-01–X-05, EU-04…EU-16, FINDING 141-253) in `OpenUBEM_debug_References.md` are **downstream-project-specific debugging log entries** (this GSSCanada 4J European-locations work), not generic OpenUBEM platform limitations — excluded here as out of scope for "what OpenUBEM is," per the task's own file-outline-only instruction for this 1,882-line file.

---

## H. Climate change, retrofit, decarbonisation, grid, DHC, PV, EV, health, equity, policy, digital twins, LLM/agents

Targeted grep across all five fully-read core docs (`fundamentals`, `inputs_reference`, `imputation_methods`, `simulated_vs_reconstructed_methodology`, `outdoor_analysis_reference`):

- **Climate change / future weather scenarios (RCP/SSP):** NOT FOUND. No mention anywhere in the scanned docs.
- **Retrofit:** mentioned twice only as *forward-looking hooks*, not implemented: (1) 3D viewer's result-parameter model names "retrofit delta" as an example of a future addable channel, `OpenUBEM_fundamentals.md:430`; (2) imputation §7 names "targeting retrofits" as the kind of future application that would justify moving to a donor-draw imputer, `OpenUBEM_imputation_methods.md:207-208`. No retrofit-scenario capability exists today.
- **Decarbonisation:** NOT FOUND as a named capability; only carbon *accounting* (eGRID electricity factor, fixed natural-gas factor) is implemented — `OpenUBEM_inputs_reference.md:23-24,42-43`.
- **Grid / district heating / district cooling:** NOT FOUND as modelled infrastructure. "Grid" only appears as the neighbourhood/viewer 2D display grid (`OpenUBEM_fundamentals.md:365`) and in the electricity carbon-intensity sense (eGRID). DHC not mentioned.
- **PV:** only as an **outdoor shading mitigation scenario** ("PV canopy / solid shade sails," modelled purely for its Tmrt-shading effect, ΔUTCI −6…−12°C) — `OpenUBEM_fundamentals.md:559`; `OpenUBEM_outdoor_analysis_reference.md:462`. No PV *generation*/offset modelling.
- **EV:** NOT FOUND.
- **Health:** appears in (a) intended-user framing ("policy makers"), (b) municipal risk-tier table action "Public health warnings; outdoor-labour shade breaks; hydration stations" for the 26-32°C UTCI tier — `OpenUBEM_outdoor_analysis_reference.md:151`. No health-outcome modelling.
- **Equity:** appears only in a cited reference title, Nazarian et al. (2022) "Integrated urban biometeorology for **thermal equity**" — `OpenUBEM_outdoor_analysis_reference.md:587`. Not an implemented metric (SHVI, the closest analogue, is explicitly "not built," `:422`).
- **Policy:** appears as user-audience framing (`OpenUBEM_fundamentals.md:20`) and as a stated blocker/value note for the air-quality-dispersion future candidate ("High policy value") — `OpenUBEM_outdoor_analysis_reference.md:500`. No policy-simulation capability.
- **Digital twins:** NOT FOUND anywhere in the scanned docs.
- **LLM / agents / GNN / deep-generative:** the imputation arc's **Phase E** names "deep-generative, GNN, LLM, TabPFN" as frontier methods, status "⛔ documented-deferred (none enter the default pipeline)" — `OpenUBEM_imputation_methods.md:100,145`. "Agent-based pedestrian mobility" is a named but out-of-scope/unbuilt outdoor-analysis candidate — `OpenUBEM_outdoor_analysis_reference.md:428-430,515`. **No LLM or agent component is implemented anywhere in OpenUBEM today.**

This confirms: an occupancy-generation-pipeline + LLM paper building on OpenUBEM would be extending into genuinely unoccupied territory — OpenUBEM's own occupancy representation is entirely archetype-schedule-based (fixed DOE hourly profiles per archetype, `OpenUBEM_inputs_reference.md:34,84-87`), imputation's only nod to LLMs is a deferred, unbuilt Phase-E candidate, and no generative/agentic component exists in the codebase per this documentation set.

---

## I. Sites/cities named and their status

**U.S. validation matrix — 3 cities × 4 density cells = 12 cells, 8,160 buildings, 100% EnergyPlus success** (`OpenUBEM_fundamentals.md:339-355`):
- **New York City** (centre/urban/suburban/rural) — benchmark NYC LL84. Headline: +2.1% (Phase-D2 reconstructed) / −24.4% (Phase-E physical) vs. measured. Pilot for the 3D viewer (`nyc_centre`, 738 buildings) and for Stage-6 UTCI depth run.
- **Los Angeles** (centre/urban/suburban/rural) — benchmark LA EBEWE. −3.7% (D2) / −5.6% (Phase-E). Noted "long-standing LA hot-bias," OPEN-19 (~+40% hot, no climate-zone/code-year switch).
- **Austin** (centre/urban/suburban/rural) — benchmark CBECS West-South-Central proxy (no disclosure law exists). −8.6% (D2) / −25.7% (Phase-E).
- All three also scored against national CBECS 2018 across mid-Atlantic/Pacific/West-South-Central census regions.

**European district viewers, 4 sites, all Speed-cluster EnergyPlus runs, `openubem/outputs/3D/eu_<neighbourhood>_viewer.html`** (`OpenUBEM_fundamentals.md:434-478`):
- **ES-MAD-BERRUGUETE** (Madrid, Spain) — 957/1194 residential buildings bound, 79.0862 kWh/m² heating over 999,191 m², Catastro years + ERA5 2010 weather.
- **FR-LYO-HAUTCOEURPENTES** (Lyon, France) — 290/530 bound, 70.0619 kWh/m² heating over 394,414 m², IGN BD TOPO years + ERA5 2023 weather. Explicitly flagged **not comparable** to an earlier Windows-engine sample (Speed Linux is a distinct platform/binary, FINDING 187/190).
- **GB-LDN-STDUNSTANS** (London, UK) — 81/1242 bound, 74.7151 kWh/m² heating over 90,790 m², EPC age bands + ERA5 2015 weather.
- **IT-BOL-GALVANI2** (Bologna, Italy) — 1,202/1,220 bound, 55.5346 kWh/m² heating over 2,520,391 m²; construction period is **imputed** (ISTAT 2011 census-section dominant TABULA band), tagged on every row; **no floor-plan pop-ups** (layout side-car script incompatible with the imputed path).

No non-U.S./non-European sites named. No stated coverage outside these 3 U.S. + 4 European locations.

---

## Results/ subfolder (names only, per instruction 7)

`docs_EXPLANATION/Results/`:
- `OpenUBEM_results_Resolution.md`
- `OpenUBEM_results_archetypeClassification.md`
- `OpenUBEM_results_hvacServiceLoads.md`

## Graphic self-description doc (instruction 8)

`OpenUBEM_graphic_summary_prompt_styles.md:1-3` — **NOT** an OpenUBEM-specific self-description; it is an explicitly **project-agnostic** reusable reference for writing image-generation prompts (three styles: Technical Flowchart, 3D Axonometric Realistic, Hybrid Annotated Axonometric), "meant to be handed to a fresh Claude session on any other project." It happens to live in OpenUBEM's docs but "carries no OpenUBEM-specific content." The actual OpenUBEM graphical self-representation is a separate rendered PNG asset, `OpenUBEM_graphical_abstract_2026-07-25.png` (binary, not read), referenced from `OpenUBEM_fundamentals.md` as the source's own summary graphic; no textual content of that image was captured in this scan.

---

*End of digest. All content above is drawn from read-only inspection of the 8 files/paths named in the task; no file was modified.*
