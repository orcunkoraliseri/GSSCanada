# WP0 Employee A (permits, assessment roll, linkage) - implementation state
Task doc: 5J_docs_occ/impl/2026-09-22_wp0_task.md
Status:   DONE

## Files kept
All in `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\`. Times are download completion, UTC.

- `montreal_permis_construction.csv` — 185,762,564 bytes — sha256
  615b4da960624dee99394c2de6c759f66574365c1ead8ae50e1174fd6212f2ea — URL
  https://donnees.montreal.ca/dataset/d90eaf1b-2de8-43f0-923a-27a620ecdf41/resource/5232a72d-235a-48eb-ae20-bb9d501300ad/download/permis-construction.csv
  — 2026-09-23T00:42:27Z
- `toronto_permits_active.csv` — 69,180,903 bytes — sha256
  b5d806a5c61beeb72b61af074ba5f712736acbcc0e9cc18fb8f99bc05e49afed — URL
  https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/108c2bd1-6945-46f6-af92-02f5658ee7f7/resource/dfce3b7b-4f17-4a9d-9155-5e390a5ffa97/download/building-permits-active-permits.csv
  — 2026-09-23T00:43:27Z
- `toronto_permits_cleared_since2017.csv` — 148,478,326 bytes — sha256
  2b0b435f874fd6ffc448f188a6697b1781aa2408448188e00868dba41f834d2f — URL
  https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9e42a85b-180f-4dc5-b0d7-d46661a6c0ec/resource/b41c3e9e-4d2d-4b09-a789-9569d8da407c/download/cleared-building-permits-since-2017.csv
  — 2026-09-23T00:44:26Z
- `toronto_permits_cleared_2000_2016.csv` — 155,623,064 bytes — sha256
  3abea56690ef095992c3b9be2eecc09c975c81a77ed5109def403ef750ddd5f2 — URL
  https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9e42a85b-180f-4dc5-b0d7-d46661a6c0ec/resource/c647bdae-0127-425e-86e6-2d88ff0e2adf/download/export_202507081211.csv
  — 2026-09-23T00:44:57Z
- `montreal_unites_evaluation_fonciere.csv` — 76,344,621 bytes — sha256
  7e3f834cbba2ff38097fddee45b0a95226af8aaeaded87cf9e4bb753ac7d0845 — URL
  https://donnees.montreal.ca/dataset/4ad6baea-4d2c-460f-a8bf-5d000db498f7/resource/2b9dfc3d-91d3-48de-b32c-a2a6d9417079/download/uniteevaluationfonciere.csv
  — 2026-09-23T00:44:07Z
- `toronto_ckan_active_permits_package_show.json` — CKAN `package_show` for
  https://open.toronto.ca/dataset/building-permits-active-permits/, HTTP 200, fetched 2026-09-23
- `toronto_ckan_cleared_permits_package_show.json` — CKAN `package_show` for
  https://open.toronto.ca/dataset/building-permits-cleared-permits/, HTTP 200, fetched 2026-09-23
- `toronto_open_data_licence_page.html` — https://open.toronto.ca/open-data-licence/, HTTP 200,
  fetched 2026-09-23
- `montreal_licence_page.html` — https://donnees.montreal.ca/pages/licence-d-utilisation, HTTP 200,
  fetched 2026-09-23
- `montreal_ckan_unites_evaluation_fonciere_package_show.json` — CKAN `package_show` for the
  assessment-roll dataset (id `unites-evaluation-fonciere`), HTTP 200, fetched 2026-09-23

All 5 CSV byte counts match the byte counts already recorded in the kickoff note's earlier
"Permit file check" (for the 3 permit files) or the CKAN `package_show` `size` field (for the roll
CSV) exactly, so these are confirmed to be the same current files, freshly downloaded and now
checksummed into `_5J_data`.

## Verified
### 1. Montreal permits CSV
- Rows: 560,309. Columns (16): no_demande, id_permis, date_debut, date_emission, emplacement,
  arrondissement, code_type_base_demande, description_type_demande, description_type_batiment,
  description_categorie_batiment, nature_travaux, nb_logements, longitude, latitude, loc_x, loc_y.
- `date_emission` range: 1990-01-03 to 2026-09-14 (min/max read directly from the column).

### 2. Toronto permits: 3-file dedupe
- Row counts: active 204,592; cleared_since2017 438,965; cleared_2000_2016 448,093. Total rows
  across the 3 files: 1,091,650.
- Dedupe key: (PERMIT_NUM, REVISION_NUM). Unique keys: 1,083,669. Keys present in more than one
  file: 2,803. (Total rows minus unique keys = 7,981 — some keys repeat more than once even within
  a single file, so this is slightly larger than the 2,803 cross-file figure.)
- Residential rule (STRUCTURE_TYPE, per the kickoff note): counted a row as residential if
  STRUCTURE_TYPE contains SFD, "apartment building", "multiple unit building", townhouse, duplex,
  triplex, detached/semi-detached, laneway (suite), "converted house", or "row house", excluding
  values exactly "Multiple Use/Non Residential" or "Mixed Use/Res w Non Res". This rule was checked
  against the active-permits file alone first and reproduced the kickoff note's number exactly:
  137,585 / 204,592 = 67.25%. Applied to the deduplicated set (one representative row per unique
  key, see Decisions for which row is kept when a key appears in more than one file): 729,339
  residential rows out of 1,083,669 unique keys (67.30%).
- DESCRIPTION strings starting with "HVAC -", counted inside the 729,339 deduplicated residential
  rows: 101,611. Median length of DESCRIPTION after stripping the "HVAC -" prefix (and surrounding
  whitespace): 88 characters (min 0, max 924).

### 3. Toronto licence
- CKAN `package_show` for `building-permits-active-permits`: `license_title` = "License not
  specified", `license_id` = "notspecified", `license_url` = null.
- CKAN `package_show` for `building-permits-cleared-permits`: identical — `license_title` =
  "License not specified", `license_id` = "notspecified", `license_url` = null.
- Portal licence page (https://open.toronto.ca/open-data-licence/ — note the task doc's URL used
  the American spelling "open-data-license" and 404s; the live portal page uses the British
  spelling "licence"), quoted verbatim from the fetched HTML body text: "This licence is based on
  version 1.0 of the Open Government Licence – Ontario, which was developed through public
  consultation and a collaborative effort by the provincial and federal government. The only
  substantive changes in this licence are to replace direct references to the Province of Ontario
  with the City of Toronto and the inclusion of a provision for the Ontario Personal Health
  Information Protection Act, 2004. ... The Information Provider grants you a worldwide,
  royalty-free, perpetual, non-exclusive licence to use the Information, including for commercial
  purposes, subject to the terms below. You are free to: Copy, modify, publish, translate, adapt,
  distribute or otherwise use the Information in any medium, mode or format for any lawful
  purpose." So: the two dataset-level CKAN records themselves carry no licence field, but the
  portal-wide page states the general Open Data Licence - City of Toronto applies and is open for
  commercial and any lawful use.

### 4. Montreal assessment roll
- Dataset: https://donnees.montreal.ca/dataset/unites-evaluation-fonciere ("Unités d'évaluation
  foncière"). Three resources listed: CSV "Liste des unités d'évaluation foncière" (downloaded, the
  one used here), GeoJSON and SHP "Extrait géographique des unités d'évaluation foncière" (not
  downloaded — see Decisions).
- Licence: CKAN `package_show` reports `license_title` "Creative Commons Attribution 4.0
  International", `license_id` "cc-by", `license_url` http://creativecommons.org/licenses/by/4.0/.
  The portal's own licence page (donnees.montreal.ca/pages/licence-d-utilisation) also contains the
  text "Creative Commons Attribution 4.0 International".
- Rows: 514,439. Columns (18): ID_UEV, CIVIQUE_DEBUT, CIVIQUE_FIN, NOM_RUE, SUITE_DEBUT,
  MUNICIPALITE, ETAGE_HORS_SOL, NOMBRE_LOGEMENT, ANNEE_CONSTRUCTION, CODE_UTILISATION,
  LETTRE_DEBUT, LETTRE_FIN, LIBELLE_UTILISATION, CATEGORIE_UEF, MATRICULE83, SUPERFICIE_TERRAIN,
  SUPERFICIE_BATIMENT, NO_ARROND_ILE_CUM.
- No coordinate or geometry column exists in this CSV (confirmed from the column list above — the
  geometry lives only in the separate GeoJSON/SHP resources, not downloaded; see Decisions).
- Fill rates (of 514,439 rows): ANNEE_CONSTRUCTION 100.00% (514,439); NOMBRE_LOGEMENT (dwelling
  count) 91.27% (469,507); LIBELLE_UTILISATION (building-use label, used here as "building
  category" — see Decisions) 100.00% (514,439); CATEGORIE_UEF (the other candidate "category"
  field, régulier/condominium) 100.00% (514,439); CIVIQUE_DEBUT 100.00%; NOM_RUE 100.00%.
- Construction-year tabulation (of all 514,439 rows, ANNEE_CONSTRUCTION has 0 missing so bands sum
  to the total): before 1960: 181,646; 1960–1989: 152,229; 1990 and later: 180,564; missing: 0.

### 5. Linkage test (Montreal residential permits to the assessment roll)
- The roll CSV has no coordinate/geometry field (see item 4), so this used the task's stated
  fallback: join by normalised address (civic number + street name).
- Montreal residential permits: same "resident"/"habitation" substring rule on
  description_type_batiment as the kickoff note, re-run here for consistency: 420,572 of 560,309
  rows (75.06%) — matches the kickoff note's figure exactly.
- Address parsing: for every one of the 420,572 residential permits, a leading civic number could
  be extracted from `emplacement` (100%). Street text was normalised (accent-stripped, lower-cased,
  non-alphanumeric collapsed to single spaces) on both sides; the roll's NOM_RUE had its trailing
  borough-code parenthetical, e.g. "(MTL)", stripped before normalising. The roll was indexed by
  normalised street name to lists of (CIVIQUE_DEBUT, CIVIQUE_FIN) ranges; a permit joined if its
  civic number fell within one of those ranges on the same normalised street name (roll rows with
  CIVIQUE_FIN < CIVIQUE_DEBUT were swapped so the range is always ascending).
- Joined: 410,123 of 420,572 residential permits (97.52%).
- Among joined permits, the roll row's ANNEE_CONSTRUCTION vintage-band split: before 1960: 245,059;
  1960–1989: 97,317; 1990 and later: 67,747; missing year among joined: 0.
- Caveat measured directly: 85,376 of the 410,123 joins (20.8%) had more than one roll civic-number
  range on the same normalised street name contain the permit's civic number (streets with several
  roll units in overlapping or adjacent ranges); the script kept the first such candidate
  encountered. See Decisions.

## Decisions
1. **Toronto dedupe: which row to keep for a key seen in more than one file.** Not specified by the
   task. I used file priority cleared_since2017 > cleared_2000_2016 > active (reasoning: a permit
   that has reached a "cleared" file is in a more final state than one still listed as "active";
   between the two cleared files, the newer resource was preferred), keeping the first row seen in
   that priority order for a repeated key. This is an assumption, not a given rule — a different
   priority (e.g. most recent ISSUED_DATE) would change the STRUCTURE_TYPE/DESCRIPTION used for a
   small number of the 2,803 multi-file keys and could shift the residential/HVAC counts slightly.
2. **Toronto residential rule: keyword list was literally reproduced from the kickoff note's stated
   categories** (validated by exactly reproducing its 137,585/204,592 result on the active-permits
   file alone). Full 3-file dedupe surfaced additional STRUCTURE_TYPE values not covered by that
   list and not in the kickoff note's active-only check, which look plausibly residential but were
   NOT counted in the reported 729,339, because the task named a specific rule and I made no new
   design choice: "Residential", "Residential Building", "House", "Group Home",
   "Boarding/Lodging House", "Student Residence", "Live/Work Unit", "Residential
   Carports/Decks/Porches", "Window Replacements (except SFD)". Counted together (any one row, not
   summed per category) these ambiguous values cover 2,394 additional deduplicated rows — open
   question for the manager: should any of these be added to the residential definition for 5J.
3. **Montreal roll "main file" = the CSV, not the GeoJSON/SHP.** The CSV has no coordinate/geometry
   column (18 columns, none of them a lat/lon/geom field), so the 15 m/30 m nearest-unit linkage
   branch of item 5 could not be run from this file. I did not download the 168 MB GeoJSON or 145 MB
   SHP "geographic extract" resources — that decision (whether the 5J pipeline needs point-level
   linkage badly enough to justify parsing one of those instead of the address join) is left open
   for the manager; the task's own wording treats CSV-with-address-join as an acceptable path when
   "the roll" (as downloaded) has no coordinates.
4. **"Building category" field.** The task says "building-category" (singular). The roll has two
   candidate columns: LIBELLE_UTILISATION (a usage label, e.g. residential/commercial/institutional
   use) and CATEGORIE_UEF (régulier vs condominium, a legal/ownership category, not a building-use
   category). I read LIBELLE_UTILISATION as "building category" and reported its fill rate
   (100.00%) as the answer; CATEGORIE_UEF's fill rate (also 100.00%) is reported alongside in
   Verified in case the manager meant that field instead.
5. **Address-normalisation ambiguity (20.8% of joins).** When a permit's civic number fell inside
   more than one roll unit's civic-number range on the same street, the script kept the first
   candidate row encountered in file order (not, e.g., the narrowest range or a MUNICIPALITE-scoped
   choice). No mapping from permit `arrondissement` to roll `MUNICIPALITE` codes was built or used,
   so a same-named street in two different former municipalities could in principle cross-match;
   this was not checked for and is a known limitation of the join as run, not corrected here.

## Next
Nothing outstanding for Employee A's scope. If the manager wants the 15 m/30 m coordinate-based
linkage instead of the address join, the next step is downloading and parsing the roll's GeoJSON or
SHP geographic-extract resource (URLs recorded in Verified item 4) and Montreal permits'
longitude/latitude columns (96.8% filled, per the kickoff note — not re-verified here since the
coordinate branch was not exercised).

## WHAT I DID NOT VERIFY
- Did not download or inspect the Montreal roll's GeoJSON or SHP "geographic extract" resources
  (item 4/5's coordinate branch) — used the CSV-only, no-geometry path and the address-join
  fallback instead, per Decisions #3.
- Did not build a mapping between Montreal permit `arrondissement` values and roll `MUNICIPALITE`
  codes, so the address join could theoretically cross-match identically-named streets in
  different former municipalities; not quantified (Decisions #5).
- Did not exhaustively review all 235 distinct Toronto STRUCTURE_TYPE values against outside
  documentation of Toronto's permit categories — the residential rule is the kickoff note's rule,
  reproduced and reapplied; the additional near-residential category names found in the fuller
  3-file union are listed but not folded into the reported count (Decisions #2).
- Did not verify the Toronto dataset pages themselves (e.g. re-fetching
  open.toronto.ca/dataset/building-permits-active-permits/ HTML) beyond what the manager's earlier
  kickoff-note check already recorded; relied on the CKAN `package_show` JSON and the portal licence
  page fetched fresh in this task for the licence answer.
- Did not check whether the Toronto "cleared" resources' REVISION_NUM values are consistently
  formatted with the "active" resource's (e.g. leading zeros, blank vs "0") in a way that could
  silently split what should be the same key into two different dedupe keys; used the raw
  string values from each file as read.
- Did not re-verify nb_logements (Montreal permits dwelling-count column) or any Montreal permits
  field beyond date_emission and emplacement/description_type_batiment — out of this item's scope.
