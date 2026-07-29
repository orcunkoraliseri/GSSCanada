"""3rdJ_08D_campaign_cells.py -- Step 8 (3J Leg-3 4-split): the 56-cell CAMPAIGN table.

Pure data module: builds the 56-cell (2 buildings x 2 cities x 14 scenarios) campaign table
DERIVED PROGRAMMATICALLY (BUILDINGS x CITIES x SCENARIOS, never a hand-typed 56-row literal),
per 3rdJ_08_simulation_4split.md:44 and 3rdJ_08_implementation_improvements.md "the campaign,
as authoritatively defined". Does NOT run anything, does NOT import eppy/pandas at module
scope, does NOT touch commercial_integration.py. Imported by 3rdJ_08D_campaign_driver.py (one
cell) and 3rdJ_08D_campaign_local.py (the orchestrator's --dry-run listing).

2026-07-28 built (employee task: build + dry-run test the campaign driver; do NOT launch the
56-run campaign).

2026-07-28 FIX (manager-verified defect): this file originally built all 56 cells with
office/retail/hotel ONLY -- the residential channel (OD-8R-L3 injector, then unimplemented) was
never wired in, so every cell would have run with the 27 residential apartment Spaces at NECB
baseline, silently omitting the entire subject of the research. The residential injector
(`commercial_integration.py::inject_residential`, dispatched from `inject_mixed_use()` via
`channels["residential"] = {"csv": ..., "seed": 42}`) is now implemented; `_bundle_channels()` /
`_historical_channels()` / `_build_scenarios()` below now wire it into every scenario that has a
residential product, and `validate_campaign_channels()` (defence in depth, see its docstring)
FAILS LOUDLY if any scenario is ever again missing a channel it is supposed to carry.

---------------------------------------------------------------------------------------------
14 scenarios (verified against the docs, not taken on faith -- see each block below):
---------------------------------------------------------------------------------------------
 1. Default (NECB)   -- channels={} (no injection at all, identical to probe cell 0)
 2. 2022              -- office/retail/hotel/residential "observed"-band 2022 products (Step7_docs)
 3. B-cons  (2030)    -- BUNDLE_MAP["cons"]    (3rdJ_07_aug_to_bem_4split.py:149)
 4. B-central (2030)  -- BUNDLE_MAP["central"] (3rdJ_07_aug_to_bem_4split.py:150)
 5. B-opt   (2030)    -- BUNDLE_MAP["opt"]     (3rdJ_07_aug_to_bem_4split.py:151)
 6. 2005              -- historical, office+retail+residential, hotel DELIBERATELY ABSENT (see below)
 7. 2010              -- ditto
 8. 2015              -- ditto
 9. sens_office_cons  -- B-central with office band AND residential BOTH swapped to "conservative"
                         (they share the office/WFH BAND axis -- see "Sensitivity axis" section below)
10. sens_office_opt   -- B-central with office band AND residential BOTH swapped to "fullyhybrid"
                         (== probe cell var_office, plus the now-present residential channel)
11. sens_retail_cons  -- B-central with retail csv swapped to retail_..._2030_cons.csv; residential stays central
12. sens_retail_opt   -- B-central with retail csv swapped to retail_..._2030_opt.csv; residential stays central
                         (== probe cell var_retail, plus the now-present residential channel)
13. sens_hotel_cons   -- B-central with hotel csv swapped to hotel_..._2030_cons.csv; residential stays central
14. sens_hotel_opt    -- B-central with hotel csv swapped to hotel_..._2030_opt.csv; residential stays central
                         (== probe cell var_hotel, plus the now-present residential channel)

---------------------------------------------------------------------------------------------
Sensitivity axis -- residential shares the office/WFH BAND axis (verified against Step-7 code,
not assumed)
---------------------------------------------------------------------------------------------
3rdJ_07_aug_to_bem_4split.py:932 labels the block that builds BOTH products together
"---- Residential + Office (share the office/WFH BAND axis) ----". Concretely:
  - `assemble_2030(office_band, ...)` (3rdJ_07_aug_to_bem_4split.py:358-359, docstring: "ported
    from Leg-2, keyed off the office/WFH BAND axis only") is the ONLY function that produces the
    residential BEM_Schedules_4split_2030_<bundle>.csv product -- its sole free parameter is
    `office_band`, there is no separate residential axis.
  - The `--sens office` build path (3rdJ_07_aug_to_bem_4split.py:917-920) sets
    `chans = {"residential_office"}` and rebuilds BOTH the residential file (for `office_band` in
    {conservative, fullyhybrid}, i.e. the cons/opt states) AND the office multiplier file in the
    SAME branch (:933-954) -- office and residential are REBUILT TOGETHER, never independently,
    for this axis.
  - The `--sens retail` / `--sens hotel` paths (3rdJ_07_aug_to_bem_4split.py:921-928) set
    `chans = {"retail"}` / `{"hotel"}` ONLY -- `"residential_office"` is absent from `chans`, so
    neither residential nor office is rebuilt; both stay at whatever the base (central/hybrid)
    run already produced.
  Conclusion (confirmed, not assumed): sens_office_cons/opt MUST swap residential to the matching
  cons/opt bundle file alongside office, or the cell is internally inconsistent (office at
  cons/opt, residential still reflecting the central-band household draw). sens_retail_*/
  sens_hotel_* MUST keep residential (and office) at central -- exactly what `_build_scenarios()`
  implements below.

Office is a MODULATE product with a SHARED reference peak (Defaut-2 taxonomy, implementation-
improvements doc): a single office_presence_multiplier_2030.csv carries all 3 bundle bands
(BAND column in {"conservative","hybrid","fullyhybrid"}) -- confirmed by reading the CSV
(`py -3 -c "import pandas...` ,2026-07-28). So sensitivities 9/10 do NOT need a new office CSV,
only a different `band` string against the SAME file -- verified against BUNDLE_MAP, not assumed.
Retail and hotel are per-band FILES (retail_..._2030_{cons,central,opt}.csv,
hotel_schedule_multiplier_2030_{cons,central,opt}.csv) -- all 6 already exist on disk (verified
2026-07-28 by `ls`), including the `_cons` variants the probe harness never needed. Residential is
also a per-band FILE (BEM_Schedules_4split_2030_{cons,central,opt}.csv, all 3 already exist on
disk, verified 2026-07-28 by `ls`) -- reused verbatim by sens_office_cons/opt from the same files
B_cons/B_opt already reference, never duplicated.

Office is a MODULATE product with a SHARED reference peak (Defaut-2 taxonomy, implementation-
improvements doc): a single office_presence_multiplier_2030.csv carries all 3 bundle bands
(BAND column in {"conservative","hybrid","fullyhybrid"}) -- confirmed by reading the CSV
(`py -3 -c "import pandas...` ,2026-07-28). So sensitivities 9/10 do NOT need a new CSV, only a
different `band` string against the SAME file -- verified against BUNDLE_MAP, not assumed.
Retail and hotel are per-band FILES (retail_..._2030_{cons,central,opt}.csv,
hotel_schedule_multiplier_2030_{cons,central,opt}.csv) -- all 6 already exist on disk (verified
2026-07-28 by `ls`), including the `_cons` variants the probe harness never needed.

Scenarios 10/12/14 (office/retail/hotel opt) are, by construction, the SAME channel config as
the existing probe cells var_office/var_retail/var_hotel (3rdJ_08P_probe_driver.py:154-168) --
reused verbatim (same csv/band/pr keys), per the task's explicit note that only the cons-side
is new.

---------------------------------------------------------------------------------------------
Hotel absence for 2005/2010/2015 -- EXPLICIT, DOCUMENTED, never an accidental missing file
---------------------------------------------------------------------------------------------
Manager decision (implementation-improvements.md, task brief): hotel source data starts 2011
and QC ground truth starts 2019, so injecting anything into the hotel channel for 2005/2010/2015
would be fabrication. These 3 cells' `channels` dict simply OMITS the "hotel" key entirely (no
csv path is ever pointed at a nonexistent file for this reason -- that pattern is reserved for
probe cell 6's deliberate trip-wire test). This is not silent: `inject_mixed_use()`
(eSim_bem_utils/commercial_integration.py:593-598) treats a channel key ABSENT from `channels`
exactly like a present-but-missing CSV -- both hit `result["fallback"].append("hotel")` and print
the loud `[FALLBACK] hotel channel data missing -- Hotel guest-room Spaces revert to NECB
baseline` banner (verified by reading the source, not assumed). So historical cells get the
SAME loud, auditable FALLBACK_LOUD manifest entry as probe cell 6's fallback_retail cell -- the
absence is structurally impossible to mistake for a bug. Each historical cell additionally
carries a `hotel_deliberately_absent` metadata key (not read by the injector -- pure
documentation/provenance) explaining why, so a reader of the cell table or manifest never has to
re-derive the reason from first principles.

---------------------------------------------------------------------------------------------
Buildings / cities / IDFs / EPWs
---------------------------------------------------------------------------------------------
Buildings: Tall, SuperTall (2). Cities: MTL (CAN_MTL, Z6, EPW 6A, PR=QC), CLG (CAN_CLG, Z7A,
EPW tagged _6B on disk -- see the Calgary climate-zone verdict in the Progress Log; NOT renamed
per instruction, PR=AB). IDF stock verified present locally 2026-07-28 (implementation-
improvements.md Sec. C-bis, md5s recorded there) under
3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/.
Retail/hotel `pr` follows city (MTL->QC, CLG->AB) -- both values verified present in the Step-7
product CSVs' own PR column (2026-07-28: retail and hotel files both carry PR in {'AB','QC')).
Office has NO PR column (confirmed by reading the CSV) -- one national office product, city-
independent; only the office `band` varies by scenario, never the csv path.
"""
from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Axis 1 -- buildings
# ---------------------------------------------------------------------------
BUILDINGS = ["Tall", "SuperTall"]

# ---------------------------------------------------------------------------
# Axis 2 -- cities (city label, CZ, IDF sub-dir, IDF climate-tag token, EPW filename, retail/hotel PR)
# ---------------------------------------------------------------------------
CITIES = [
    {"city": "MTL", "cz": "Z6", "idf_dir": "CAN_MTL", "idf_climate_tag": "Z6",
     "epw_file": "CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw",
     "pr": "QC"},
    {"city": "CLG", "cz": "Z7A", "idf_dir": "CAN_CLG", "idf_climate_tag": "Z7A",
     "epw_file": "CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw",
     "pr": "AB"},
]

# ---------------------------------------------------------------------------
# BUNDLE_MAP mirror (3rdJ_07_aug_to_bem_4split.py:148-152) -- office BAND / retail+hotel band
# labels per 2030 bundle. Kept as a literal copy (not an import: Step-7 doc lives in a sibling
# folder with its own dependency footprint) but every value is cross-checked against the source
# file in the Progress Log entry for this task -- do not edit one without the other.
# ---------------------------------------------------------------------------
BUNDLE_OFFICE_BAND = {"cons": "conservative", "central": "hybrid", "opt": "fullyhybrid"}
BUNDLE_LABEL = {"cons": "cons", "central": "central", "opt": "opt"}  # csv filename suffix, identical to bundle key

OFFICE_ARCHETYPE = "Office_Knowledge"  # verbatim from the probe cell table, unchanged


def _s7(step7_out: str, name: str) -> str:
    return os.path.join(step7_out, name)


def _hist(historical_out: str, name: str) -> str:
    return os.path.join(historical_out, name)


RESIDENTIAL_SEED = 42  # OD-8R-L3 injector default (commercial_integration.py::inject_residential);
                        # pinned explicitly on every cell rather than relying on the injector's
                        # own default, per the task's determinism requirement.


def _bundle_channels(office_csv, office_band, retail_csv, hotel_csv, residential_csv, pr):
    return {
        "office": {"csv": office_csv, "archetype": OFFICE_ARCHETYPE, "band": office_band},
        "retail": {"csv": retail_csv, "pr": pr},
        "hotel": {"csv": hotel_csv, "pr": pr},
        "residential": {"csv": residential_csv, "seed": RESIDENTIAL_SEED},
    }


def _historical_channels(office_csv, retail_csv, residential_csv, pr):
    # Deliberately NO "hotel" key -- see module docstring "Hotel absence" section. Residential
    # IS available for 2005/2010/2015 (Step8_docs/outputs_step8/historical_schedules/
    # BEM_Schedules_4split_{2005,2010,2015}.csv, generated by 3rdJ_08A_gen_historical_products_
    # 4split.py) -- only hotel's source data starts in 2011.
    return {
        "office": {"csv": office_csv, "archetype": OFFICE_ARCHETYPE, "band": "observed"},
        "retail": {"csv": retail_csv, "pr": pr},
        "residential": {"csv": residential_csv, "seed": RESIDENTIAL_SEED},
    }


def _build_scenarios(step7_out: str, historical_out: str, pr: str) -> list:
    """Returns the 14 scenario dicts ({"tag", "channels", "notes", ...}) for ONE city's `pr`.
    Office/residential are city-independent in content (band-driven), retail/hotel filter by
    `pr` internally via load_retail_series/load_hotel_series -- so the returned channel CSV
    *paths* are identical across cities, only the `pr` key value differs.
    """
    office_2022 = _s7(step7_out, "office_presence_multiplier_2022.csv")
    office_2030 = _s7(step7_out, "office_presence_multiplier_2030.csv")
    retail_2022 = _s7(step7_out, "retail_presence_multiplier_2022.csv")
    retail_2030_cons = _s7(step7_out, "retail_presence_multiplier_2030_cons.csv")
    retail_2030_central = _s7(step7_out, "retail_presence_multiplier_2030_central.csv")
    retail_2030_opt = _s7(step7_out, "retail_presence_multiplier_2030_opt.csv")
    hotel_2022 = _s7(step7_out, "hotel_schedule_multiplier_2022.csv")
    hotel_2030_cons = _s7(step7_out, "hotel_schedule_multiplier_2030_cons.csv")
    hotel_2030_central = _s7(step7_out, "hotel_schedule_multiplier_2030_central.csv")
    hotel_2030_opt = _s7(step7_out, "hotel_schedule_multiplier_2030_opt.csv")

    office_2005 = _hist(historical_out, "office_presence_multiplier_2005.csv")
    office_2010 = _hist(historical_out, "office_presence_multiplier_2010.csv")
    office_2015 = _hist(historical_out, "office_presence_multiplier_2015.csv")
    retail_2005 = _hist(historical_out, "retail_presence_multiplier_2005.csv")
    retail_2010 = _hist(historical_out, "retail_presence_multiplier_2010.csv")
    retail_2015 = _hist(historical_out, "retail_presence_multiplier_2015.csv")

    # Residential (OD-8R-L3, REPLACE product; commercial_integration.py::inject_residential).
    # 2022/2030-bundle files live in Step7_docs/outputs_step7; historical files are Step-8A's own
    # output (3rdJ_08A_gen_historical_products_4split.py). Residential and office SHARE the
    # office/WFH BAND axis -- verified against Step-7 source, see module docstring "Sensitivity
    # axis" section and BUNDLE_MAP comment below; residential_2030_{cons,central,opt} is the SAME
    # per-bundle file the B_cons/B_central/B_opt scenarios use, reused (not duplicated) for the
    # sens_office_* cells.
    residential_2022 = _s7(step7_out, "BEM_Schedules_4split_2022.csv")
    residential_2030_cons = _s7(step7_out, "BEM_Schedules_4split_2030_cons.csv")
    residential_2030_central = _s7(step7_out, "BEM_Schedules_4split_2030_central.csv")
    residential_2030_opt = _s7(step7_out, "BEM_Schedules_4split_2030_opt.csv")
    residential_2005 = _hist(historical_out, "BEM_Schedules_4split_2005.csv")
    residential_2010 = _hist(historical_out, "BEM_Schedules_4split_2010.csv")
    residential_2015 = _hist(historical_out, "BEM_Schedules_4split_2015.csv")

    scenarios = [
        {"tag": "Default_NECB", "channels": {}, "notes": "no injection at all -- pure NECB baseline"},
        {"tag": "Y2022", "channels": _bundle_channels(
            office_2022, "observed", retail_2022, hotel_2022, residential_2022, pr),
         "notes": "2022 observed cycle"},
        {"tag": "B_cons", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["cons"], retail_2030_cons, hotel_2030_cons,
            residential_2030_cons, pr),
         "notes": "BUNDLE_MAP['cons']"},
        {"tag": "B_central", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["central"], retail_2030_central, hotel_2030_central,
            residential_2030_central, pr),
         "notes": "BUNDLE_MAP['central']"},
        {"tag": "B_opt", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["opt"], retail_2030_opt, hotel_2030_opt,
            residential_2030_opt, pr),
         "notes": "BUNDLE_MAP['opt']"},
        {"tag": "Y2005", "channels": _historical_channels(office_2005, retail_2005, residential_2005, pr),
         "notes": "historical cycle; hotel DELIBERATELY ABSENT (see module docstring)",
         "hotel_deliberately_absent": "hotel source data starts 2011; injecting a pre-2011 hotel "
                                       "schedule would be fabrication -- manager decision, "
                                       "2026-07-28. Hotel Spaces run at NECB baseline via the "
                                       "injector's own FALLBACK_LOUD path (channel key omitted)."},
        {"tag": "Y2010", "channels": _historical_channels(office_2010, retail_2010, residential_2010, pr),
         "notes": "historical cycle; hotel DELIBERATELY ABSENT (see module docstring)",
         "hotel_deliberately_absent": "same rationale as Y2005"},
        {"tag": "Y2015", "channels": _historical_channels(office_2015, retail_2015, residential_2015, pr),
         "notes": "historical cycle; hotel DELIBERATELY ABSENT (see module docstring)",
         "hotel_deliberately_absent": "same rationale as Y2005"},
        {"tag": "sens_office_cons", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["cons"], retail_2030_central, hotel_2030_central,
            residential_2030_cons, pr),
         "notes": "B_central with office band AND residential swapped to cons (conservative) -- "
                  "residential shares the office/WFH BAND axis (3rdJ_07_aug_to_bem_4split.py:932, "
                  "909-919), so it must move with office or the cell is internally inconsistent -- "
                  "NEW (not a probe cell)"},
        {"tag": "sens_office_opt", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["opt"], retail_2030_central, hotel_2030_central,
            residential_2030_opt, pr),
         "notes": "B_central with office band AND residential swapped to opt (fullyhybrid) -- "
                  "residential shares the office/WFH BAND axis (see sens_office_cons note); "
                  "channel config == probe cell var_office plus the now-present residential channel"},
        {"tag": "sens_retail_cons", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["central"], retail_2030_cons, hotel_2030_central,
            residential_2030_central, pr),
         "notes": "B_central with ONLY retail csv swapped to cons; residential stays at central "
                  "(retail is an independent axis from office/WFH -- Step-7 3rdJ_07_aug_to_bem_"
                  "4split.py:921-924 rebuilds ONLY retail for --sens retail, never residential_office) "
                  "-- NEW (not a probe cell)"},
        {"tag": "sens_retail_opt", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["central"], retail_2030_opt, hotel_2030_central,
            residential_2030_central, pr),
         "notes": "B_central with ONLY retail csv swapped to opt; residential stays at central "
                  "(see sens_retail_cons note) -- == probe cell var_retail plus the now-present "
                  "residential channel"},
        {"tag": "sens_hotel_cons", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["central"], retail_2030_central, hotel_2030_cons,
            residential_2030_central, pr),
         "notes": "B_central with ONLY hotel csv swapped to cons; residential stays at central "
                  "(hotel is an independent axis from office/WFH -- Step-7 3rdJ_07_aug_to_bem_"
                  "4split.py:925-928 rebuilds ONLY hotel for --sens hotel, never residential_office) "
                  "-- NEW (not a probe cell)"},
        {"tag": "sens_hotel_opt", "channels": _bundle_channels(
            office_2030, BUNDLE_OFFICE_BAND["central"], retail_2030_central, hotel_2030_opt,
            residential_2030_central, pr),
         "notes": "B_central with ONLY hotel csv swapped to opt; residential stays at central "
                  "(see sens_hotel_cons note) -- == probe cell var_hotel plus the now-present "
                  "residential channel"},
    ]
    assert len(scenarios) == 14, f"expected 14 scenarios, got {len(scenarios)}"
    return scenarios


def _idf_path(repo_root: str, building: str, city_info: dict) -> str:
    fname = (f"{building}Building_90.1-2019_6A_Buffalo_NECB17_"
             f"{city_info['idf_climate_tag']}_v242.idf")
    return os.path.join(repo_root, "3J_docs_occ_nTemp", "Leg2_2-split", "Step8_docs",
                         "outputs_step8", "office_idfs_v242", city_info["idf_dir"], fname)


def _epw_path(repo_root: str, city_info: dict) -> str:
    return os.path.join(repo_root, "BEM_Setup", "WeatherFile", city_info["epw_file"])


def _missing_inputs(idf, epw, channels: dict) -> list:
    missing = []
    if not os.path.isfile(idf):
        missing.append(f"idf: {idf}")
    if not os.path.isfile(epw):
        missing.append(f"epw: {epw}")
    for ch, cfg in channels.items():
        csv_path = cfg.get("csv", "")
        if not csv_path or not os.path.isfile(csv_path):
            missing.append(f"{ch} csv: {csv_path!r}")
    return missing


# ---------------------------------------------------------------------------
# Channel-completeness GATE (defence in depth) -- 2026-07-28. Added by the same task that fixed
# the residential-channel omission defect (this file previously built all 56 cells with office/
# retail/hotel only, silently missing the entire subject of the research). Guards against that
# EXACT failure shape recurring for any future channel: a scenario is supposed to carry a channel
# but the cell table quietly doesn't wire it, and --dry-run reports "0 missing inputs" because it
# only checks what IS listed, never what's absent.
#
# Runs INSIDE build_campaign_cells() (see the assert at the end of that function) so there is no
# code path that reaches a built cell table without passing through this gate first: both
# 3rdJ_08D_campaign_local.py (--dry-run and a real launch alike, line ~156) and
# 3rdJ_08D_campaign_driver.py (--dry-run and a real single-cell run alike, line ~122) call
# build_campaign_cells() before doing anything else. A gate failure raises AssertionError, which
# aborts the whole process -- "impossible to launch a campaign past it" per the task instruction.
# ---------------------------------------------------------------------------
ALL_CHANNELS = {"office", "retail", "hotel", "residential"}

# Scenarios whose channel set is deliberately SMALLER than ALL_CHANNELS. Every scenario tag not
# listed here must carry exactly ALL_CHANNELS -- any other omission is either this task's fixed
# defect recurring or a new deliberate exception that must be added HERE EXPLICITLY, never
# silently. Only two exceptions exist today, both manager-decided and documented in the module
# docstring / _build_scenarios():
DELIBERATE_CHANNEL_EXCEPTIONS = {
    "Default_NECB": frozenset(),                          # pure NECB baseline -- no injection at all
    "Y2005": frozenset(ALL_CHANNELS - {"hotel"}),          # hotel source data starts 2011
    "Y2010": frozenset(ALL_CHANNELS - {"hotel"}),
    "Y2015": frozenset(ALL_CHANNELS - {"hotel"}),
}


def _expected_channels(scenario_tag: str) -> frozenset:
    return DELIBERATE_CHANNEL_EXCEPTIONS.get(scenario_tag, frozenset(ALL_CHANNELS))


def validate_campaign_channels(cells: list) -> list:
    """Returns a list of human-readable FAIL messages, one per cell missing a channel its
    scenario is supposed to carry (empty list == PASS). Compares each cell's `channels` dict
    keys against `_expected_channels(cell["scenario"])`; any channel present in `expected` but
    absent from the cell's `channels` dict is reported by name. Does NOT flag extra/unexpected
    channels (never happens in practice here, and an extra injected channel is not the failure
    mode this gate defends against)."""
    failures = []
    for c in cells:
        expected = _expected_channels(c["scenario"])
        present = set(c["channels"].keys())
        missing = expected - present
        if missing:
            failures.append(
                f"cell {c['cell_index']} ({c['tag']}): scenario '{c['scenario']}' is missing "
                f"channel(s) {sorted(missing)} -- expected {sorted(expected)}, got {sorted(present)}"
            )
    return failures


def build_campaign_cells(repo_root: str, step7_out: str = None, historical_out: str = None) -> list:
    """Builds the 56-cell campaign table: BUILDINGS (2) x CITIES (2) x SCENARIOS (14),
    derived programmatically -- never a hand-typed 56-row literal. Loop order (building outer,
    city middle, scenario inner) groups the 14 scenarios of a given building/city pair into
    consecutive indices 0-13 / 14-27 / 28-41 / 42-55, convenient for both --dry-run readability
    and a future `--array=0-55` cluster mapping (not launched by this task).

    Every cell carries: cell_index, tag (unique), scenario, building, city, cz, idf, epw,
    channels (dict, exactly what inject_mixed_use() expects), notes, and missing_inputs (list,
    empty when everything resolves -- computed HERE so --dry-run and the driver's own guard
    both read the same precomputed answer instead of re-deriving it twice).
    """
    step7_out = step7_out or os.path.join(
        repo_root, "3J_docs_occ_nTemp", "Leg3_4-split", "Step7_docs", "outputs_step7")
    historical_out = historical_out or os.path.join(
        repo_root, "3J_docs_occ_nTemp", "Leg3_4-split", "Step8_docs", "outputs_step8",
        "historical_schedules")

    cells = []
    idx = 0
    for building in BUILDINGS:
        for city_info in CITIES:
            idf = _idf_path(repo_root, building, city_info)
            epw = _epw_path(repo_root, city_info)
            scenarios = _build_scenarios(step7_out, historical_out, city_info["pr"])
            for scen in scenarios:
                tag = f"{scen['tag']}__{building}__{city_info['city']}"
                channels = scen["channels"]
                cell = {
                    "cell_index": idx,
                    "tag": tag,
                    "scenario": scen["tag"],
                    "building": building,
                    "city": city_info["city"],
                    "cz": city_info["cz"],
                    "idf": idf,
                    "epw": epw,
                    "channels": channels,
                    "notes": scen.get("notes", ""),
                    "missing_inputs": _missing_inputs(idf, epw, channels),
                }
                if "hotel_deliberately_absent" in scen:
                    cell["hotel_deliberately_absent"] = scen["hotel_deliberately_absent"]
                cells.append(cell)
                idx += 1
    assert len(cells) == 56, f"expected 56 cells, got {len(cells)}"

    gate_failures = validate_campaign_channels(cells)
    assert not gate_failures, (
        "CHANNEL-COMPLETENESS GATE FAILED -- refusing to build the campaign table (defence in "
        "depth against a scenario silently missing a channel it is supposed to carry; see "
        "validate_campaign_channels()):\n  " + "\n  ".join(gate_failures)
    )

    return cells


def cell_tags(repo_root: str, step7_out: str = None, historical_out: str = None) -> dict:
    """{cell_index: tag} -- mirrors 3rdJ_08P_probe_driver.py's CELL_TAGS convention for the
    orchestrator's resume-skip / status-csv bookkeeping."""
    return {c["cell_index"]: c["tag"] for c in
            build_campaign_cells(repo_root, step7_out, historical_out)}


if __name__ == "__main__":
    # Minimal self-check: build against this file's own repo checkout and print the count +
    # any missing inputs, without touching eppy/pandas/EnergyPlus. Real --dry-run listing lives
    # in 3rdJ_08D_campaign_local.py.
    HERE = os.path.dirname(os.path.abspath(__file__))
    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    cells = build_campaign_cells(REPO_ROOT)
    print(f"built {len(cells)} cells against repo_root={REPO_ROOT}")
    n_missing = sum(1 for c in cells if c["missing_inputs"])
    print(f"cells with >=1 missing input: {n_missing}/{len(cells)}")
