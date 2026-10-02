"""Step 9k item 3: additive patch of tools/speed/a9_store.py (old behaviour reachable: A9_TRUNCATE_TARGETS=0, test_main defaults = 9g test)."""
p = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/tools/speed/a9_store.py"
t = open(p, encoding="utf-8", newline="").read()


def rep(old, new, cnt=1):
    global t
    assert t.count(old) == cnt, (old[:70], t.count(old))
    t = t.replace(old, new)


# ---- (2) truncation of targets in build_store + rows check
rep('''    for s in splits:
        mm[s].flush()
        if off[s] != nfl[s]:
            print("INFO split %s: %d flat rows written of %d announced (failed runs)" % (s, off[s], nfl[s]), flush=True)
''', '''    for s in splits:
        mm[s].flush()
        if off[s] != nfl[s]:
            print("INFO split %s: %d flat rows written of %d announced (failed runs)" % (s, off[s], nfl[s]), flush=True)
    # Step 9k item 3 (2): the memmap was sized from the zone map; a failed run leaves trailing zero rows. Truncate to the rows written
    # (switch A9_TRUNCATE_TARGETS=0 restores the old behaviour, which the rows check below then reports as FAIL).
    if os.environ.get("A9_TRUNCATE_TARGETS", "1") == "1":
        for s in splits:
            if off[s] != nfl[s]:
                tp = os.path.join(out_dir, "targets_%s.npy" % s)
                del mm[s]
                src = np.load(tp, mmap_mode="r")
                tmp = tp + ".tmp.npy"
                dst = np.lib.format.open_memmap(tmp, mode="w+", dtype=np.float32, shape=(off[s], H, 3))
                for a0 in range(0, off[s], 256):
                    dst[a0:a0 + 256] = src[a0:min(a0 + 256, off[s])]
                dst.flush()
                del dst, src
                os.replace(tmp, tp)
                print("INFO split %s: targets_%s.npy truncated from %d to %d rows" % (s, s, nfl[s], off[s]), flush=True)
''')
rep('''        stamp("%s rows %d runs %d" % (os.path.basename(pth), len(flats[s]), flats[s]["run_id"].nunique() if len(flats[s]) else 0))
''', '''        stamp("%s rows %d runs %d" % (os.path.basename(pth), len(flats[s]), flats[s]["run_id"].nunique() if len(flats[s]) else 0))
        chk("targets_rows_equal_flats_rows_%s" % s, targets_rows_match(os.path.join(out_dir, "targets_%s.npy" % s), len(flats[s])),
            "targets shape %s, flats rows %d" % (tuple(np.load(os.path.join(out_dir, "targets_%s.npy" % s), mmap_mode="r").shape), len(flats[s])))
''')
rep('''def read_series(p):''', '''def targets_rows_match(tp, nrows):
    """Step 9k: True when the targets file has exactly nrows rows of shape (8760, 3)."""
    sh = tuple(np.load(tp, mmap_mode="r").shape)
    return sh == (nrows, H, 3)


def read_series(p):''')

# ---- test_main extension
rep('def test_main(base, win="/speed-scratch/o_iseri/5J/step9c/win/", epwd="/speed-scratch/o_iseri/5J/step9c/epw/"):',
    '''def _raw_col_pos(csv_path, pos):
    """Step 9k: one column of an eplusout.csv by header POSITION; returns (header text at that position, values)."""
    with io.open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        return head[pos], np.array([float(r[pos]) for r in rd])


def test_main(base, win="/speed-scratch/o_iseri/5J/step9c/win/", epwd="/speed-scratch/o_iseri/5J/step9c/epw/", runs_dir=None, kinds="D,O", small_stem="7307694dddf93fb6"):
    """Step 9k: runs_dir (read-only run folders <stem>_<run>), kinds (e.g. D,O,DF,OF) and small_stem extend the 9g test; with runs_dir set the 9k checks are added
    (keep_csv present, heating by header position, targets rows = flats rows incl. a planted extra row, triangle refusal, SIZE with and without fast runs).
    Defaults reproduce the 9g test exactly."""
    v3 = runs_dir is not None
    kinds = tuple(kinds.split(","))''')
rep('''    man = [r for r in c.read_csv_rows(W + "manifest.csv") if r["run"] in ("D", "O")]''',
    '''    man = [r for r in c.read_csv_rows(W + "manifest.csv") if r["run"] in kinds]''')
rep('''        rid = "%s_%s" % (r["stem"], r["run"])
        rows.append({"run_id": rid, "split": "development", "district": r["district"], "stem": r["stem"], "mode": r["run"],
                     "run_dir": base + "runs/" + rid, "placement_csv": (W + "%s/placement_%s.csv" % (r["district"], r["stem"])) if r["run"] == "O" else "",
                     "epw": EPWD + r["epw"], "n_flats": r["n_flats"]})''',
    '''        rid = "%s_%s" % (r["stem"], r["run"])
        rows.append({"run_id": rid, "split": "development", "district": r["district"], "stem": r["stem"], "mode": r["run"][0],
                     "run_dir": ((runs_dir.rstrip("/") + "/") if v3 else base + "runs/") + rid,
                     "placement_csv": (W + "%s/placement_%s.csv" % (r["district"], r["stem"])) if r["run"][0] == "O" else "",
                     "epw": EPWD + r["epw"], "n_flats": r["n_flats"], "fast": r["run"] in ("DF", "OF")})
    if v3:
        for r in rows:        # item 3 (4): the hourly csv must still be in the run folder (nothing deleted it before the extraction)
            chk("keep_csv_present_" + r["run_id"], os.path.isfile(r["run_dir"] + "/eplusout.csv") and os.path.getsize(r["run_dir"] + "/eplusout.csv") > 0,
                r["run_dir"] + "/eplusout.csv")''')
rep('''    o_ok = [r for r in rows if r["mode"] == "O" and r["run_id"] in okrun]''',
    '''    o_ok = [r for r in rows if r["mode"] == "O" and not r["fast"] and r["run_id"] in okrun]
    if v3:        # triangle building: refused by the clean-status rule is the RIGHT behaviour; everything else must extract
        tri = [r["run_id"] for r in rows if r["stem"] == "1271cddbf6bd1e8a"]
        other_bad = [rid for rid in bad_run if rid not in tri]
        chk("triangle_runs_refused_by_clean_rule_others_extracted", all(rid in bad_run and "evere" in bad_run[rid] for rid in tri) and not other_bad,
            "triangle runs refused %d of %d (reasons: %s); other runs not extracted: %s" % (sum(1 for rid in tri if rid in bad_run), len(tri), sorted({bad_run[rid][:60] for rid in tri if rid in bad_run}), other_bad))''')
rep('''    allowed = {"development": [r["run_id"] for r in rows if r["mode"] == "O"], "validation": []}''',
    '''    allowed = {"development": [r["run_id"] for r in rows if r["mode"] == "O" and not r["fast"]], "validation": []}''')
rep('''    info = build_store([r for r in rows if r["mode"] == "O"], allowed, zmap_path, static_dir, sdir, "test")''',
    '''    info = build_store([r for r in rows if r["mode"] == "O" and not r["fast"]], allowed, zmap_path, static_dir, sdir, "test")''')
rep('''    raw_h = _raw_col(pick["run_dir"] + "/eplusout.csv", lab) / 3.6e6
''', '''    if v3:        # item 3 (3): by header POSITION found by substring rules (not the built label), then the header at that position must equal the heating name
        with io.open(pick["run_dir"] + "/eplusout.csv", newline="", encoding="utf-8", errors="replace") as fh:
            head0 = next(csv.reader(fh))
        cand = [k for k, h in enumerate(head0) if h.startswith(zone.upper() + " IDEAL LOADS AIR SYSTEM") and "Total Heating Energy" in h and h.endswith("(Hourly)")]
        chk("heating_column_unique_by_position", len(cand) == 1, "candidates at header positions %s" % cand)
        hpos, raw_h = _raw_col_pos(pick["run_dir"] + "/eplusout.csv", cand[0])
        chk("heating_header_at_position_is_the_heating_name", hpos == lab, "position %d header %r expected %r" % (cand[0], hpos, lab))
        raw_h = raw_h / 3.6e6
    else:
        raw_h = _raw_col(pick["run_dir"] + "/eplusout.csv", lab) / 3.6e6
''')
rep('''    small = [r for r in o_ok if r["stem"] == "7307694dddf93fb6"]''', '''    small = [r for r in o_ok if r["stem"] == small_stem]''')
rep('''          % (len(fl), nb, nb / len(fl) / 1e6, tb / len(fl) / 1e6, fb / len(fl) / 1e6, sum(os.path.getsize(sdir + f) for f in os.listdir(sdir) if f.startswith("hh_")) / 1e6), flush=True)
    return summary()''', '''          % (len(fl), nb, nb / len(fl) / 1e6, tb / len(fl) / 1e6, fb / len(fl) / 1e6, sum(os.path.getsize(sdir + f) for f in os.listdir(sdir) if f.startswith("hh_")) / 1e6), flush=True)
    if v3:
        # item 3 (2): rows of targets = rows of flats on the real store, and the check seen failing on a planted extra row
        tp = sdir + "targets_development.npy"
        chk("targets_rows_equal_flats_rows_real", targets_rows_match(tp, len(fl)), "targets shape %s flats %d" % (tuple(np.load(tp, mmap_mode="r").shape), len(fl)))
        pl = base + "planted_extra_row_targets.npy"
        src = np.load(tp, mmap_mode="r")
        dst = np.lib.format.open_memmap(pl, mode="w+", dtype=np.float32, shape=(len(fl) + 1, H, 3))
        dst[:len(fl)] = src[:]
        dst.flush()
        del dst
        chk("targets_rows_check_fails_on_planted_extra_row", not targets_rows_match(pl, len(fl)), "planted file has %d rows, flats %d: the rows check must say False" % (len(fl) + 1, len(fl)))
        os.remove(pl)
        # SIZE with the fast runs: a second store from the O runs and the OF runs
        f_rows = [r for r in rows if r["mode"] == "O"]
        allowed_f = {"development": [r["run_id"] for r in f_rows], "validation": []}
        build_store(f_rows, allowed_f, zmap_path, static_dir, base + "store_fast/", "withfast")
        sf = base + "store_fast/"
        flf = Store(sf).flats("development")
        nbf = dir_bytes(sf)
        print("SIZE_WITH_FAST_RUNS flats=%d store_total_bytes=%d MB_per_flat_year_total=%.4f targets_only_MB_per_flat_year=%.4f (O and OF runs; WITHOUT fast runs see the SIZE line above)"
              % (len(flf), nbf, nbf / len(flf) / 1e6, os.path.getsize(sf + "targets_development.npy") / len(flf) / 1e6), flush=True)
    return summary()''')
rep('''        elif sys.argv[1] == "test":
            code = test_main(*sys.argv[2:5])''', '''        elif sys.argv[1] == "test":
            code = test_main(*sys.argv[2:8])''')
open(p, "w", encoding="utf-8", newline="").write(t)
print("patched")
