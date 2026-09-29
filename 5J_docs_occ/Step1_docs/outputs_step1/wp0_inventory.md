# WP0 inventory (5J Step 1)

Written 2026-09-28 by the WP0 employee. Read-only. Every fact carries its source. Machine-readable twin: `wp0_inventory.json` (same keys, same sources).

UK line: **WAITING ON AUTHOR** (UKDS clause 5). No UK data file was opened, hashed, counted or parsed; UK files were listed by name and size only.

## A. HETUS diary files

- **spain_raw_DIARIO2.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/DIARIO2.TXT; bytes = 127810080; md5 = 40d1f7c31f484b962008744ad20fddc2; lines_wc_l = 2778480; 4j_record = DIARIO2: 2778480 records ... MATCH; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_spain.txt (INPUTS READ + record reconciliation)
- **spain_raw_DIARIO1.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/DIARIO1.TXT; bytes = 771800; md5 = ea2d068b2c0a3de692e5196e03a3d581; lines_wc_l = 19295; 4j_record = DIARIO1: 19295 records ... MATCH; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_spain.txt (INPUTS READ + record reconciliation)
- **spain_raw_MHOGAR.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/MHOGAR.TXT; bytes = 1294750; md5 = a5762792d11cfbe3591449b0bdc5c1db; lines_wc_l = 25895; 4j_record = MHOGAR: 25895 records ... MATCH; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_spain.txt (INPUTS READ + record reconciliation)
- **spain_raw_CINDIV.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/CINDIV.TXT; bytes = 1215585; md5 = bfad9a24202a752ddf2845e971e5c7e7; lines_wc_l = 19295; 4j_record = CINDIV: 19295 records ... MATCH; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_spain.txt (INPUTS READ + record reconciliation)
- **spain_raw_DHOGAR.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/DHOGAR.TXT; bytes = 372099; md5 = 427a027432ffcaf26bfc25eefa03aebf; lines_wc_l = 9541; 4j_record = DHOGAR: 9541 records ... MATCH; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_spain.txt (INPUTS READ + record reconciliation)
- **spain_raw_HTR1.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/HTR1.TXT; bytes = 219570; md5 = b64073a490e4ea0d638beebcd4e59493; lines_wc_l = 8445; 4j_record = not among the five files 4J's parse report hashes; equal_to_4j = None
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **spain_raw_HTR2.TXT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/HTR2.TXT; bytes = 7389375; md5 = 6eaa5f27a4a8d00d2eb6de9f6186513e; lines_wc_l = 59115; 4j_record = not among the five files 4J's parse report hashes; equal_to_4j = None
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **spain_raw_SD.txt**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/SD.txt; bytes = 48175; md5 = a376a01f26172c249f6a0c36d3db8488; lines_wc_l = 1025; 4j_record = none found; equal_to_4j = None
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **spain_zip_datos_emptiem0910**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/datos_emptiem0910.zip; bytes = 8623518; md5 = b38d01933e8d2cecec1b652c855fd64d; 4j_record = acquisition_manifest.json:21 md5 b38d0193... (equal)
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); grep -n md5 acquisition_manifest.json
- **spain_zip_disreg_emptiem0910**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/disreg_emptiem0910.zip; bytes = 165012; md5 = 59af0472dae16cd657a289071f9ea20a; 4j_record = acquisition_manifest.json:30 md5 59af0472... (equal)
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **spain_layout_workbook**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/spain/unpacked/DISEnOS DE REGISTRO EET 2009 2010.xlsx; bytes = 266444; md5 = db61ca5f0a745d4bc7dc0b817a697691
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **italy_raw_uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/italy/unpacked/MICRODATI/uso_tempo_Microdati_Anno_2013_DiarioGiornaliero.txt; bytes = 79746805; md5 = f1d70e2d718210b712fe6a677b904997; lines_wc_l = 1077658; 4j_record = 1077657 data rows + 1 header line; 4J: 'DiarioGiornaliero: 1077657 records against ISTAT's stated 1077657 -> MATCH'; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_italy.txt (INPUTS READ + RECORD-COUNT RECONCILIATION)
- **italy_raw_uso_tempo_Microdati_Anno_2013_Individui.txt**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/italy/unpacked/MICRODATI/uso_tempo_Microdati_Anno_2013_Individui.txt; bytes = 27235465; md5 = fd055250d7a04c303a31a52c1c367239; lines_wc_l = 44867; 4j_record = 44866 data rows + 1 header line; 4J: 'Individui: 44866 records ... MATCH'; equal_to_4j = True
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_italy.txt (INPUTS READ + RECORD-COUNT RECONCILIATION)
- **italy_raw_uso_tempo_Microdati_Anno_2013_DiarioSettimanale.txt**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/italy/unpacked/MICRODATI/uso_tempo_Microdati_Anno_2013_DiarioSettimanale.txt; bytes = 11106092; md5 = f0577c0d15c6de864c11b62322eecbaf; lines_wc_l = 105771; 4j_record = not read by the 4J parse report (no record found); equal_to_4j = None
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28); 4J record: 4J_docs_occ/Step1_docs/outputs_step1/parse_report_italy.txt (INPUTS READ + RECORD-COUNT RECONCILIATION)
- **italy_zip_uso_tempo_2013_IT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/italy/uso_tempo_2013_IT.zip; bytes = 18144298; md5 = 58817df9ee59eaf1e5b16f62dbe65798; 4j_record = acquisition_manifest_italy.json:21 md5 58817df9... (equal)
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **italy_zip_UsoTempo_2023_IT**: path = C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/italy/UsoTempo_2023_IT.zip; bytes = 5297692; md5 = 34d50c22128ab5f9c2d940b956083c50; 4j_record = acquisition_manifest_italy.json:58 md5 34d50c22... (equal); a 2023 survey, NOT the 2013-14 wave 5J uses
  - source: md5sum + stat -c %s + wc -l (local, Git Bash, 2026-09-28)
- **spain_episodes_parquet**: path = GSSCanada-main/4J_docs_occ/Step1_docs/outputs_step1/episodes_spain.parquet; bytes = 2421700; md5 = fa1b4c61a33e4553312ed85265799071; rows = 430754; 4j_record = parse_report_spain.txt: 'WROTE ... episodes_spain.parquet (430754 rows, 25 columns)'; equal_to_4j = True
  - source: PYTHONIOENCODING=utf-8 py -c "import pyarrow.parquet as p;print(p.ParquetFile(path).metadata.num_rows)" (file metadata only); md5sum; ls -l
- **italy_episodes_parquet**: path = GSSCanada-main/4J_docs_occ/Step1_docs/outputs_step1/episodes_italy.parquet; bytes = 5573813; md5 = 001d61aefbf923ed39749c0e64f6f177; rows = 1077657; 4j_record = parse_report_italy.txt: 'WROTE ... episodes_italy.parquet (1077657 rows, 27 columns)'; equal_to_4j = True
  - source: PYTHONIOENCODING=utf-8 py -c "import pyarrow.parquet as p;print(p.ParquetFile(path).metadata.num_rows)" (file metadata only); md5sum; ls -l
- **finding_local_vs_speed_parquet_size**: local_spain_bytes = 2421700; speed_spain_bytes = 2561361; local_italy_bytes = 5573813; speed_italy_bytes = 5875778; note = sizes differ; Speed copies dated Aug 17 12:14/12:23 (strata re-run), local Aug 16 21:10. Not md5-compared (ssh is ls only). Step 2 must pick one and hash it.
  - source: ls -l local; ssh ls -l /speed-scratch/o_iseri/4J/outputs_step1
- **uk_raw_and_episodes**: status = WAITING ON AUTHOR; listed_by_name_and_size_only = [_local_runs/4J/raw/uk/UK-TUS-20260815T031737Z-1-001.zip (21465300 bytes); _local_runs/4J/raw/uk/unpacked/UK-TUS/ (directory); 4J_docs_occ/Step1_docs/outputs_step1/episodes_uk.parquet (3392774 bytes)]; md5 = WAITING ON AUTHOR; rows = WAITING ON AUTHOR; author_line = cd "/c/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/uk" ; md5sum *.zip > uk_md5_5J.txt ; ls -l unpacked/UK-TUS >> uk_md5_5J.txt
  - source: ls -l only; no UK file opened, hashed, counted or parsed
- **speed_copies**: root = /speed-scratch/o_iseri/4J/; raw_spain = /speed-scratch/o_iseri/4J/raw/spain/{datos_emptiem0910.zip,disreg_emptiem0910.zip,docs,unpacked,meth_t25304471.pdf}; raw_italy = /speed-scratch/o_iseri/4J/raw/italy/{uso_tempo_2013_IT.zip,UsoTempo_2023_IT.zip,unpacked,Nota_metodologica*.pdf}; outputs_step1 = /speed-scratch/o_iseri/4J/outputs_step1/ (episodes_spain.parquet 2561361 B, episodes_italy.parquet 5875778 B, parse/gate reports, run_20260816-2140, run_20260816-2210, run_20260817-strata); hashes = not computed on Speed (ssh is ls only)
  - source: ssh o_iseri@speed... 'ls -l /speed-scratch/o_iseri/4J/raw/*' and outputs_step1 (2026-09-28)

## B. Diary to schedule (4J Steps 7 and 9)

- **step7_signatures**: rotate_to_midnight = rotate_to_midnight(series, timestep_min, origin_hour=DIARY_ORIGIN_HOUR) :120; year_day_types = year_day_types(year) :153; load_pool = load_pool(path, step2_dir, bitpos, limit=None, outdoor_override=None) :185; draw = draw(pools, prefix, rng, backoff_tally) :245; assemble_person_year = assemble_person_year(prefix, cal, rule, rng, pools, backoff_tally, rho=0.0) :266; to_timestep = to_timestep(minute_values, timestep_min) :307; household_year = household_year(members_days, timestep_min) :321; write_schedule_csv = write_schedule_csv(path, values, column_name) :359; idf_objects = idf_objects(name, csv_name, n_values, timestep_min, n_people, interpolate=None) :398; load_households = load_households(corpus_path, country, n_households, rng, min_size=1) :440; build = build(gen_dir, fold, step2_dir, crosswalk, corpus, out_dir, year, timestep_min, rule, seed, n_households, rho=0.0, arm='constrained', min_size=1, pool_limit=None, interpolate=None, n_hours_override=None, keep_series=False, outdoor_override=None, use_compact=False, presence_offset=0.0, leg='leg4', rotate=True) :484
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step7_schedules.py: grep -n '^def ' ; sed -n 484,490p
- **diary_origin_hour**: value = 4; per_country = single constant DIARY_ORIGIN_HOUR = 4; code comment records native origins es 06:00, uk 04:00, it 04:00, all harmonised to 04:00 by Step 2 (D-S2-5); also_in = 4thJ_step9_trigger.py:68 DIARY_ORIGIN_HOUR = 4
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step7_schedules.py:117 (constant), :106-116 (comment)
- **midnight_rotation**: rule = cyclic over the WHOLE YEAR, k = origin_hour*60//timestep_min places; series[-k:] + series[:-k]; raises ScheduleError if k >= len(series); quote = THE ROTATION IS CYCLIC OVER THE WHOLE YEAR, NOT WITHIN EACH DAY
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step7_schedules.py:120-143 (FINDING 141 comment :114)
- **schedule_time_step**: default_cli = 60; unit = minutes; idf_field = Schedule:File ... Minutes per Item = timestep_min; Interpolate to Timestep = No (constant INTERPOLATE_TO_TIMESTEP, :95); note = only presence (fraction 0..1) per household is written; People object, Fraction Radiant 0.3, Activity_Level schedule name
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step7_schedules.py:614 (add_argument --timestep default=60), :95, :398-437
- **step7_cli_arguments**: [--gen; --fold {es,uk,it}; --arm; --step2; --crosswalk; --corpus; --out; --year (leap years refused); --timestep (60); --rule {independent,static,habit}; --rho; --seed; --leg (leg4); --households (100); --min-size; perturbation-only: --interpolate --hours --drop-outdoor-code --compact --presence-offset --no-rotate]
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step7_schedules.py:603-640
- **chaining_rule**: ruled = decision 14 CLOSED: independent, seed 1 adopted as the standard convention for every published Step 8 and Step 9 dataset; rules_in_code = CHAINING_RULES = ('independent','static','habit') (step7_schedules.py:104); RULE_POINTS in step7_chaining.py:70
  - source: GSSCanada-main/4J_docs_occ/Step8_docs/4thJ_08_bemSimulation.md:10 ('DECISION 14 IS CLOSED -- independent, seed 1'); GSSCanada-main/4J_docs_occ/tools/4thJ_step7_schedules.py:104
- **secondary_activity_in_electricity_schedules**: answer = NO in 4J: the appliance trigger reads only duration_min, act, loc_class; quote = "act2" is absent because `D-S9-1` ruled (d), and for no other reason -- see FINDING 137: the generated record DOES carry `act2`, so its absence here is a policy, not an accident of the format."; mapping_py = 4thJ_step9_mapping.py contains 0 mentions of act2 or secondary (grep -c); size_of_gap = 29.816 % of episodes and 26.308 % of modelled minutes carry a non-empty act2 (Step9 doc :100); consequence = 5J must add secondary activity itself (parent lesson 13)
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step9_trigger.py:159-168 (return ['duration_min','act','loc_class']); GSSCanada-main/4J_docs_occ/Step9_docs/4thJ_09_enduseLoads.md:100-104
- **indoor_rule**: what = presence = (loc_class == 'at_home') AND (act not in OUTDOOR_AT_HOME); functions load_outdoor_at_home, episode_present, presence_minutes, gate_g7_13; needed_by_5J = not decided here
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step7_indoor.py:96-176; Step7_docs/4thJ_07_constrainedGeneration_val.md:75
- **schedules_on_disk**: dir = GSSCanada-main/4J_docs_occ/Step7_docs/outputs_step7/schedules/; subdirs = leg4_{es,it,uk}_independent_seed1; leg5_es_independent_seed1, leg5_es_independent_seed1_cal2010, leg5_it_independent_seed1, leg5_it_independent_seed1_cal2013, leg5_it_independent_seed1_cal2014, leg5_uk_independent_seed1, leg5_uk_independent_seed1_cal2014; perturb_* (9); schedules_bak_prerotation/ (sibling); es_dir_leg5_cal2010 = 103 files: manifest.json, manifest_addendum_9_5.json, 100 presence_HH_es_*.csv (78861 bytes each); uk_dirs = listed by name only
  - source: ls Step7_docs/outputs_step7/schedules; ls -l on the leg5 es and it directories
- **spain_schedule_file_opened**: file = leg5_es_independent_seed1_cal2010/presence_HH_es_00035.csv; header = HH_es_00035_Presence; columns = 1; lines_wc_l = 8761; values = 8760; md5 = 279be545089b56cc8d8708278f932dd7; first_values = [0.916667; 1.0]; manifest = timestep_min = 60; year = 2010; rule = independent; diary_origin_hour = 4; n_households = 100; leg = leg5
  - source: head -3; wc -l; md5sum; py json.load(manifest.json) keys
- **other_4J_schedule_type**: note = 4thJ_step9_trigger.py idf_objects(hid, fold, elec_csv, dhw_csv, n_values, timestep_min, ...) :1063 writes appliance electricity and DHW series; step9 uses to_timestep/rotate_to_midnight :749/:757
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step9_trigger.py:749,757,1063

## C. Buildings (4J Step 8)

- **idf_builder_signature**: build_idf = build_idf(d) :447 -> (idf_text, meta); derive = derive(row) :258 (TABULA row -> dict d); main = main(): positional base (outputs_step8), --out
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step8_idf.py: grep -n '^def '
- **variable_parameters_from_tabula_row**: keys_of_d_read_by_build_idf = width, depth, height (from A_C_Ref, n_Storey, h_room, aspect), u_wall, u_roof, u_floor (area-weighted from U_/A_ Wall_1-3, Roof_1-2, Floor_1-2), dub (delta_U_ThermalBridging_Original), win_face / win_total (A_Window_1,2 + compass A_Window_*), u_win (U_Window_1,2), mass_rho, code, country, cls, period, bc, phi_int, q_w_nd; note = there is NO per-parameter function argument: the only argument is the TABULA-derived dict d, so a Latin hypercube must vary dict entries or use a different builder
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step8_idf.py:258-377 (row keys), :447-460 (d keys)
- **hard_coded_parameters**: ASPECT = 1.5; WWR_CAP = 0.94; C_M_WH_M2K = 45.0; N_FACADES = 4; R_SI = wall = 0.13; roof = 0.1; floor = 0.17; R_SE = wall = 0.04; roof = 0.04; floor = 0.0; MASS_D_m = 0.05; MASS_K = 5.0; MASS_CP = 1000.0; SHGC = 0.7; infiltration_ach = 0.5; heating_setpoint_C = 20.0; cooling = none (heating-only ThermostatSetpoint:SingleHeating); ground_temp = E+ default (no Site:GroundTemperature); window_frame = none; zones = ONE thermal zone, no partition; Building = Building,name,0.0,City,0.04,0.4,FullExterior,25,6; ShadowCalculation = PolygonClipping, Periodic, 20; SimulationControl = No,No,No,No,Yes,No,1
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step8_idf.py:86-152, :481-487
- **step8_outputs_requested**: Output:Meter = NONE written by 4thJ_step8_idf.py; Output:Variable = [* Zone Ideal Loads Supply Air Total Heating Energy, Hourly; * Zone Mean Air Temperature, Hourly; * Zone Ideal Loads Zone Total Heating Energy, Monthly]; other = [OutputControl:Table:Style CommaAndHTML; Output:Table:SummaryReports AllSummary]; timestep = Timestep, 6 (10 min); RunPeriod ANNUAL 1 Jan to 31 Dec, Sunday start; version_string = Version, 24.2 (EPLUS_VERSION :145); note = heating only; NO electricity or cooling meters; lesson 9 needs meters that Step 2 must add
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step8_idf.py:481-487,644-659
- **step10_openubem_output_request**: Output:Variable = OUTPUT:VARIABLE * 'Zone Ideal Loads Zone Total Heating Energy' Hourly (only one); meters = none added by 4thJ_step10_nocore_campaign.py
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py:1403-1405
- **tabula_archetype_counts**: archetype_idf_manifest_rows = 88; by_fold = es = 24; uk = 32; it = 32; by_class_es = AB = 6; MFH = 6; SFH = 6; TH = 6; by_class_uk = AB = 8; MFH = 8; SFH = 8; TH = 8; by_class_it = AB = 8; MFH = 8; SFH = 8; TH = 8; parameter_tables_rows = 24 / 36 / 42 archetypes (es / uk / it); manifest_columns = [a_ref; n_storey; h_room; width; depth; height; aspect; win_total; win_face; u_wall; u_roof; u_floor; u_win; dub; a_*_tabula; c_total_j; mass_rho; h_transmission_*; phi_int; q_w_nd]
  - source: py csv.DictReader on Step8_docs/outputs_step8/archetype_idf_manifest.csv (TABULA rows, no diaries); Step8_docs/4thJ_08_bemSimulation.md:10
- **tabula_parameters_held**: files = [Step8_docs/outputs_step8/archetype_parameters_es.csv (6806 B); ..._uk.csv (11406 B); ..._it.csv (12115 B); tabula_reference.csv (26410 B); archetype_parameter_provenance.md]; columns = 44 TABULA columns incl. U_/A_ Wall/Roof/Floor/Window, A_C_Ref, n_Storey, h_room, phi_int, q_w_nd, delta_U_ThermalBridging_Original; NOT held: g-value, n_air_use, frame fraction; source_files = tabula-values.xlsx, tabula-calculator.xlsx (episcope.eu)
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step8_tabula.py:140-170; Step8_docs/4thJ_08_bemSimulation.md:10; step8_idf.py:122-143
- **idfs_built_record**: claim = 88 IDFs, 0 severe; source_line = Step8_docs/4thJ_08_bemSimulation.md:106 ('DONE ... REBUILT 2026-08-25 under D-S8-3(a). 88 IDFs, 26 of 26 selftest checks pass'); :1047 ('B1 every IDF runs, 0 severe errors'); :142 ('Zero severe errors'); archetype_idf_files_on_disk = 88
  - source: sed -n 106p, 142p; ls Step8_docs/outputs_step8/archetypes | wc -l -> 88
- **step10_stock_buildings**: districts = ES-MAD-BERRUGUETE = fold es, Madrid; GB-LDN-STDUNSTANS = fold uk, London; IT-BOL-GALVANI2 = fold it, Bologna; archetype_files = openubem/data/construction/tabula_archetypes_{es,gb,it}.json; note = Step 10 uses OpenUBEM multi-zone real stock, a DIFFERENT builder from step8_idf.py (single-zone box)
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py:209-219

## D. Weather

- **openubem_epw_es_madrid_2009_2010_y2009**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/es_madrid_2009_2010_y2009.epw; bytes = 881450; md5 = 38c46d2880919816e667d892711734c1; header_line1 = LOCATION,Madrid,Madrid,ESP,ERA5,000000,40.50,-3.50,1.0,609.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **openubem_epw_es_madrid_2009_2010_y2010**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/es_madrid_2009_2010_y2010.epw; bytes = 882333; md5 = 110b364912226ee4d2a5b5411eab81da; header_line1 = LOCATION,Madrid,Madrid,ESP,ERA5,000000,40.50,-3.50,1.0,609.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **openubem_epw_it_bologna_2013_2014_y2013**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/it_bologna_2013_2014_y2013.epw; bytes = 890868; md5 = 4a3f274d9a1fbe9bbaafdb586e3cbe92; header_line1 = LOCATION,Bologna,Bologna,ITA,ERA5,000000,44.50,11.25,1.0,37.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **openubem_epw_it_bologna_2013_2014_y2014**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/it_bologna_2013_2014_y2014.epw; bytes = 890973; md5 = 9a5e25091e7a9585f662e1efdc113629; header_line1 = LOCATION,Bologna,Bologna,ITA,ERA5,000000,44.50,11.25,1.0,37.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **openubem_epw_uk_london_2014_2015_y2014**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/uk_london_2014_2015_y2014.epw; bytes = 893653; md5 = bd27616134fd3d4094b1553ac22fe7e8; header_line1 = LOCATION,London,London,GBR,ERA5,000000,51.50,-0.50,0.0,25.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **openubem_epw_uk_london_2014_2015_y2015**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/uk_london_2014_2015_y2015.epw; bytes = 893938; md5 = 9d63b8de70f6b70cbdf4a63bdb91fe8c; header_line1 = LOCATION,London,London,GBR,ERA5,000000,51.50,-0.50,0.0,25.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **openubem_epw_fr_lyon_bron_2023_era5**: path = C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/fr_lyon_bron_2023_era5.epw; bytes = 888427; md5 = e0d1ff457f7668535292d92b262e8cea; header_line1 = LOCATION,Lyon-Bron,Auvergne-Rhone-Alpes,FRA,ERA5,074800,45.75,5.00,1.0,198.0; source = ERA5 (Copernicus) via cdsapi -> pvlib; actual_year = ERA5 actual calendar year in filename yNNNN (France: 2023; France is NOT a 5J fold)
  - source: md5sum; sed -n 1p; ls -l (local); weather_registry.json source field
- **diary_year_weather_used_in_4J_step10**: es = es_madrid_2009_2010_y2010.epw; uk = uk_london_2014_2015_y2014.epw; it = it_bologna_2013_2014_y2014.epw; ruling = D-S10-1 option A: majority calendar year per fold es 2010, uk 2014, it 2014
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py:200-205; tools/4thJ_step10_weather_year.py:2-7
- **step8_tmyx_epws**: dir = GSSCanada-main/4J_docs_occ/Step8_docs/outputs_step8/weather/; files = [ESP_VC_Valencia.Viveros.082850_TMYx.2009-2023.epw (es, 1603009 B); GBR_ENG_Birmingham.AP.035340_TMYx.2009-2023.epw (uk, 1587716 B); ITA_PM_Torino.Venaria.160600_TMYx.2009-2023.epw (it, 1575476 B)]; source = climate.onebuilding.org TMYx.2009-2023, station chosen by RMSE against TABULA monthly temperatures (D-S8-4); note = typical-year files, NOT ERA5 actual years; different city from the Step 10 EPWs (Valencia/Birmingham/Torino vs Madrid/London/Bologna); Step 8 numbers are on this basis
  - source: ls -l Step8_docs/outputs_step8/weather; cut -c1-300 weather_manifest.csv; tools/4thJ_step8_weather.py:86-95
- **speed_epw**: finding = /speed-scratch/o_iseri/openubem/openubem/data/weather does not exist (ssh ls: No such file or directory); the Speed OpenUBEM copy (dated Jul 26) predates the ERA5 EPWs (Aug 26). Where Step 10 jobs read EPWs on Speed was NOT located.
  - source: ssh ls -l /speed-scratch/o_iseri/openubem/openubem/data/weather
- **epw_tools_note**: note = 4thJ_step10_weather_year.py hard-codes the raw UK tab path (UK_TAB, line ~39-40) and reads it; it must not be run by an AI tool in 5J. Not run here.
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step10_weather_year.py:36-40 (code read only)

## E. Campaign runner (4J Step 10, OpenUBEM)

- **entry_point**: campaign = GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py (argparse :1649-1664: --district {ES-MAD-BERRUGUETE,GB-LDN-STDUNSTANS,IT-BOL-GALVANI2,FR-LYO-HAUTCOEURPENTES(refused)} --dry-run --shakedown --scored --expect-payload-digest --energyplus --out --run-root --workers(4) --timeout(3600) --limit --resume); eu08_driver = GSSCanada-main/4J_docs_occ/tools/4thJ_step10_eu08_driver.py (--run-root --dry-run --workers 8 --limit --cells --energyplus-timeout 900 --progress-every 10); madrid_wrapper = GSSCanada-main/4J_docs_occ/tools/4thJ_run_madrid_stock_campaign.sh (WORKERS=4, MEM_THRESHOLD=75, python 3.13 at C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe); paired = GSSCanada-main/4J_docs_occ/tools/4thJ_step10_paired.py (build_pairs :198, emit_paired :253, --table --out --country --seed-base --decimals --bundles --production-table --label --perturb); preflight = GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_preflight.py (check_manifest :218)
  - source: grep -n 'add_argument\|^def ' on each file
- **energyplus_binary_and_version**: local_exe = C:/EnergyPlusV23-1-0/energyplus.exe; measured_now = EnergyPlus, Version 23.1.0-87ed9199d4, YMD=2026.09.28 20:43; idd = C:/EnergyPlusV23-1-0/Energy+.idd (4458147 B); invocation = energyplus.exe -w <epw> -d . -x -r <idf>, cwd=run_dir; recorded_in_manifest = energyplus_version, energyplus_build_hash, openubem_version, openubem_git_commit, platform (:339-340); step8_archetype_idf_declares = Version, 24.2 (EPLUS_VERSION in step8_idf.py:145); Step 8 injected campaign engine: EnergyPlus 24.2.0 build 94a887817b (Step8_docs/docs/2026-08-25_items-8.5-8.6_injected-campaign-and-aggregate.md:43); conflict = Step 8 (single-zone) = 24.2; Step 10 (OpenUBEM) = 23.1.0. The 5J scope table says 23.1 via OpenUBEM.
  - source: /c/EnergyPlusV23-1-0/energyplus.exe --version; ls -l; GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py:197,1562-1565,339-340
- **one_working_directory_per_run**: answer = YES; quote = `cwd=run_dir` with `-d .` is NOT cosmetic. `-r` runs ReadVarsESO, which writes `readvars.audit` into the PROCESS working directory ... With a shared cwd, parallel workers delete each other's audit file; line_setting_cwd = cwd=str(run_dir), capture_output=True, text=True, timeout=args.timeout; run_dir = Path(args.run_root) / cell['cell_slug'] (:1539)
  - source: GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py:1539,1554-1565
- **openubem_repo**: path = C:/Users/o_iseri/Desktop/OpenUBEM (env OPENUBEM_ROOT); git_head_now = 4c023cc66d46d4befffe36a9e520339608124979; pins_in_4J = engine european_residential.py sha256 6a14f428a6d8c26745af3e1483080bf31e3026ebb94702f90ac7eadc4ad2afd3 (PIN 2, 2026-09-08); european_nocore.py sha256 21d723d5479076d0a57416ff92fd67a98fca8a33ff19343132415c144ff6b8ae (commit 4431f2fe); PIN 1 superseded (8e1dcda1..., commit 4431f2fe); speed_copy = /speed-scratch/o_iseri/openubem (dir dated Jul 26; commit not read); note = 4J pins by file digest, not by repo commit; repo HEAD today may differ from the engine used in the 2026-09 campaigns
  - source: cd OpenUBEM; git rev-parse HEAD; GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_preflight.py:83-108
- **cache_key**: file = GSSCanada-main/4J_docs_occ/tools/4thJ_step8_scenario.py; functions = cache_key(parts) :189; naive_cache_key(cell) :200; inject(...) :146; md5 :56; sha256 :64; note = lesson 8 (F8 cache-key collision) concerns naive_cache_key; not assessed here
  - source: grep -n '^def ' 4thJ_step8_scenario.py
- **time_per_annual_run**: ES_Madrid_OpenUBEM = about 79 s per cell per worker (Madrid) on the local Windows box, 4 workers; UK_London_OpenUBEM = about 53 s per cell per worker; 12,070 cells in ~44.2 h = ~273 cells/h; IT_Bologna_OpenUBEM = 11,681 cells in ~30.5 h = ~383 cells/h (per-worker seconds not stated); smoke = 16 cells, 91 s wall on 16 workers, EnergyPlus ~28-30 s each (building 27410, 16 zones); 410_cell_real_stock_local = 410 of 410, 4163.7 s (L5); step8_single_zone_box = 4,048 runs in 659 s; 9,000 runs in 1,530 s (12 workers default); about 2 s of core time per run (510 cells, 14 workers, wall_s 71.9); note = elapsed columns include resume gaps: an upper bound on wall-clock
  - source: Prompts/RESUME.md:1474-1485 (table + 'about 79 s against about 53 s'); Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:568-569; Step10_docs/impl/2026-08-28_realstock-campaign-two-platform.md:20; Step8_docs/4thJ_08_bemSimulation.md:191,278; Prompts/RESUME.md:11621
- **output_size_per_run**: one_ES_run_dir = _local_runs/4J_ES_local/runs/ES-MAD-BERRUGUETE/es__relation-12582232__caseA__f000: ls total 4144 KB; eplusout.csv 2195598 B, epluszsz.csv 1105596 B, in.idf 380297 B, eplusout.err 14231 B, eplusout.dbg 23937 B, gain CSVs 26280 B each; cell_manifest_json = 13590 B (out/ES-MAD-BERRUGUETE/cells/...f000.json); Madrid cell files 17.6 KB vs London 4-10 KB; retained_per_cell_step10_eu08 = eplusout.csv (8,760 hourly rows), .eso, .sql, .err, manifest
  - source: ls -l on the ES run dir (one dir); Prompts/RESUME.md:1485; Step10_docs/impl/2026-08-28_EU-08-accounting-over-the-certified-191.md:99

## F. Cluster facts (Speed, listing only)

- **speed_4J_assets**: /speed-scratch/o_iseri/4J = outputs_step1, outputs_step2, raw/{spain,italy,uk}, tools; /speed-scratch/o_iseri/4J_step10_nocore = opt/, out/{ES-MAD-BERRUGUETE,ES-MAD-BERRUGUETE_v2,IT-BOL-GALVANI2}, sbatch scripts 4J_s10_*.sh, C2 logs; /speed-scratch/o_iseri/4J_madrid = engine/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu18.04-x86_64, install_ep231.sh; other = 4J_step4, 4J_P3_docs_occ, 4J_P5_docs_occ, 4J_step3_corpus*.jsonl (54-58 MB)
  - source: ssh ls -l /speed-scratch/o_iseri and subdirs, 2026-09-28
- **speed_energyplus_install**: used_by_Step10_C2 = /speed-scratch/o_iseri/4J_step10_nocore/opt/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu20.04-x86_64; second_copy = /speed-scratch/o_iseri/4J_madrid/engine/EnergyPlus-23.1.0-87ed9199d4-Linux-Ubuntu18.04-x86_64; containers = /speed-scratch/o_iseri/energyplus_23.1.0.sif (93405184 B), energyplus_22.1.0.sif (89505792 B); older = /speed-scratch/o_iseri/EnergyPlus (dir, Apr 16); doc = no EnergyPlus in /encs/pkg or modules; installed into scratch from inside sbatch (Step10 impl 2026-09-08 :726-729); ENERGYPLUS_PATH set to the staged install (:920)
  - source: ssh ls; Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:726-729,920
- **speed_python_env**: step10_openubem_jobs = /speed-scratch/o_iseri/4J_step10_nocore/opt/venv312 (python from /encs/pkg/python-3.12.0/root/bin/python3; default python3 is 3.9 and fails); step7_generation = /speed-scratch/o_iseri/envs/step7 (base /speed-scratch/o_iseri/envs/step4/bin/python); step3_tokenizer = /speed-scratch/o_iseri/envs/4j_tok; step4_training = /speed-scratch/o_iseri/envs/step4
  - source: ssh ls -ld envs/*; Step10_docs/impl/2026-09-08_...:764-766; tools/4thJ_step7_env_build.sh:28-29; tools/4thJ_step3_build_setup_and_run.sh:16
- **scratch_fill**: value = 9.3 T of 10 T (2026-09-25); a later line in the same doc says 9.7 T used of 10 T; re_measured = False
  - source: 1J_docs_occ/Prompts/1J_manager_prompt_RESUME.md:30 (9.3T/10T), :49 (9.7T used of 10T); NOT re-measured (no quota/du in this task)
- **speed_cpu_cap_and_rules**: note = 1J holds a 64-CPU cap (per 1J doc); 4J used 31 cpu, not 32, because the association cap is cpu=32 across running jobs; partition ps; -t 7-00:00:00; --exclude=antenna1 (1J truncated outputs there)
  - source: Step10_docs/impl/2026-09-08_...:923-926; 5J parent lesson 11; 1J RESUME
- **ssh_access**: value = key login worked non-interactively (BatchMode); login shell is tcsh (2>&1 inside a remote command fails: 'Ambiguous output redirect')
  - source: ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca 'ls ...'

## Open 4J findings touching reused tools (listed, not assessed)

- FINDING 141: schedule rotated 4 h early before 2026-08-26; rotate_to_midnight added. `Step7_docs/4thJ_07_constrainedGeneration_val.md:19,80; tools/4thJ_step7_schedules.py:114`
- FINDING 42: presence rule LOC==11 always False (step7_indoor). `Step7_docs/4thJ_07_constrainedGeneration.md:102,392; _val.md:75`
- FINDING 137: generated record carries act2 but trigger ignores it (policy D-S9-1). `tools/4thJ_step9_trigger.py:164-165`
- FINDING 147: step8_chaining.py bypassed the emitter. `Step8_docs/4thJ_08_bemSimulation.md:1599; _val.md:32,613`
- FINDING 109: all 36 UK archetypes have zero South and North glazing. `Step8_docs/4thJ_08_bemSimulation.md:10,724`
- FINDING 110 / 117: box does not conserve envelope area; D-S8-3(a) reproduces TABULA wall area; it/AB 0.656, uk/AB 1.137 limitation. `Step8_docs/4thJ_08_bemSimulation.md:110,312 / :109`
- FINDING 120: weather station worth 5-11 % of heating demand; no cross-fold absolute comparison safe to +-10 %. `Step8_docs/4thJ_08_bemSimulation.md:10`
- FINDING 121 / 122 / 123: control vs TABULA sign flips by country; timestep worth -4.1/+5.6/-3.7 %; ground temperature default worth +33.5/+1.7/+15.7 %. `Step8_docs/4thJ_08_bemSimulation.md:10,1304,1307`
- FINDING 126: G8.13 parser missed Interpolate to Timestep = Yes on a 9-field Schedule:File (step8_scenario). `Step8_docs/4thJ_08_bemSimulation.md:171`
- FINDING 131: schedules emitted on survey years into a Sunday-start RunPeriod. `Step8_docs/4thJ_08_bemSimulation.md:204`
- FINDING 143-145: after rotation no occupancy claim survives at f=1.00; annual medians negative. `Step8_docs/4thJ_08_bemSimulation.md:10`
- FINDING 181 / 189: EU-08 replicate divergence; IT continuum not bistability. `Step10_docs/impl/2026-08-28_EU-08-accounting-over-the-certified-191.md:84,90; Step10_docs/docs/2026-08-28_FINDING181_arms-1-2-3_implementation.md:47`
- FINDING 210/221, 254, 246/266, 201: geometry/vertex-snap, pairing snapshot, k-per-storey, one zone per dwelling (nocore_campaign). `tools/4thJ_step10_nocore_campaign.py:57,68,983-1006,1158,1195; Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:3499 (221)`

## Discrepancies and flags for Step 2 (recorded, nothing fixed)

1. Two EnergyPlus versions: Step 8 archetype IDFs declare 24.2 (`step8_idf.py:145`); Step 10 OpenUBEM runs 23.1.0-87ed9199d4. The 5J scope says 23.1.
2. Two weather bases: Step 8 uses TMYx typical-year EPWs (Valencia, Birmingham, Torino); Step 10 uses ERA5 actual-year EPWs (Madrid 2010, London 2014, Bologna 2014).
3. `step8_idf.py` has no per-parameter arguments (only a TABULA-derived dict) and writes no Output:Meter; only heating variables.
4. Local and Speed copies of the Spain and Italy episode parquets differ in size (not hashed on Speed).
5. 4J pins OpenUBEM by file digest, not by repo commit; local HEAD is 4c023cc6.
6. 4J timing per country exists only for Madrid (~79 s) and London (~53 s) per cell per worker; Bologna has a cells-per-hour rate only.
7. `4thJ_step10_weather_year.py` hard-codes the raw UK tab path; never run it through an AI tool.
8. 4J step9 mapping/trigger ignore secondary activity (act2); 5J lesson 13 requires it.
9. Speed weather EPW location for OpenUBEM jobs not located (`/speed-scratch/o_iseri/openubem/openubem/data/weather` absent).
