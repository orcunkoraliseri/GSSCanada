# 5J Model A store, campaign mode (written 2026-10-01 20:44 by a9_store.py campaign, Step 9n)
Same layout as the 9g store (hh_<cc>.npz, weather_<district>.npy, calendar_<district>.npy, flats_<split>, targets_<split>.npy, pairs_<split>, norm.json, static_cols.json, openlog_<tag>.tsv).
Built only from what the campaign keeps: results/<rid>.json (status CLEAN), results/<rid>.npz (hourly heating, cooling, equipment per flat, float32), runs/<rid>/placement.csv + series.tar.gz, b0 files, EPW, zone map, static tables.
Split names: development = dev building x dev households; validation = val building x val households; xdev_hval / xval_hdev = the mixed cases (kept apart); b0_<bs>, default_<bs>. Test runs (pool test or test building) are never opened.
hh_<cc>.npz index = household INSTANCE (one per household x run draw; identical series files share one instance). Instances are append-only; ones whose runs were removed stay as unused rows.
ledger.tsv = stored runs with the md5 of their result json; work/ = raw (un-z-scored) flats tables and hh arrays used for incremental builds; refused_<tag>.tsv = every refused run with its reason.
Row order inside a split = order of insertion (kept rows first, then new runs sorted by run_id); the key of a row is (run_id, zone).
targets_<split>.npy : float32 n_rows x 8760 x 3 (heating, cooling, equipment kWh per hour per flat); total_elec = equipment + (heating + cooling) / 3.0
