# 5J campaign prep, Part D step 3 (Speed): disk parser test on the REAL df capture + timing/disk arithmetic (INFO).
import csv, io, json, os, re, statistics, subprocess, sys, collections
R = "/speed-scratch/o_iseri/5J/campaign_prep/"
T = R + "timing/"
MZ = "/speed-scratch/o_iseri/5J/mz_pilot/"      # read-only (Spanish re-pilot)


def parse_df(text):
    """Return (total, used, avail) bytes from `df -B1 <path>` text; anchors on the LAST data row (handles a wrapped device name)."""
    lines = [l for l in text.strip().splitlines() if l.strip()]
    if len(lines) < 2 or not lines[0].lstrip().startswith("Filesystem"):
        raise ValueError("df header not found")
    m = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%\s+\S+\s*$", " ".join(l.strip() for l in lines[1:]))
    if not m:
        raise ValueError("df data row not parsed")
    tot, used, avail = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if not (tot >= used + 0 and tot >= avail):
        raise ValueError("df numbers inconsistent")
    return tot, used, avail


raw = open(T + "df_raw.txt").read()
print("DF_RAW_LINES_BEGIN")
print(raw.rstrip())
print("DF_RAW_LINES_END")
tot, used, avail = parse_df(raw)
st = open(T + "statfs.txt").read().split()
stat_avail = int(st[0]) * int(st[1])
print("DF_PARSED total=%d used=%d avail=%d | statfs free (blocks_avail x block_size) = %d | rel diff %.2e (other users write; must be < 1e-3)"
      % (tot, used, avail, stat_avail, abs(stat_avail - avail) / avail))
print("DF_CROSSCHECK", "PASS" if abs(stat_avail - avail) / avail < 1e-3 else "FAIL")
used_5j = int(open(T + "du5J.txt").read().split()[0])
print("PREFLIGHT_DISK free_bytes=%d used_5J=%d" % (avail, used_5j))
# seen failing: the parser must refuse garbage / a header-only capture / a truncated row
for label, txt in (("header_only", "Filesystem 1B-blocks Used Available Use% Mounted on\n"),
                   ("truncated_row", "Filesystem 1B-blocks Used Available Use% Mounted on\nfiler:/x 100 50\n"),
                   ("no_header", "filer:/x 100 50 50 50% /mnt\n")):
    try:
        parse_df(txt)
        print("SEENFAIL_DF_PARSER %s NOT REFUSED (problem)" % label)
    except ValueError as e:
        print("SEENFAIL_DF_PARSER %s REFUSED: %s" % (label, e))
# and the wrapped two-line form of the real capture must give the same numbers
hdr, row = [l for l in raw.strip().splitlines() if l.strip()][:2]
wrapped = hdr + "\n" + row.split()[0] + "\n" + " ".join(row.split()[1:]) + "\n"
print("DF_WRAPPED_FORM_SAME_NUMBERS", "PASS" if parse_df(wrapped) == (tot, used, avail) else "FAIL")

# ---------------------------------------------------------------- timing of the two big runs
big = {}
for rid in ("T_es_B40", "T_it_B37"):
    d = dict(l.strip().split("=", 1) for l in open(T + "runs/%s/status.txt" % rid) if "=" in l)
    meta = json.load(io.open(T + "runs/%s/meta.json" % rid))
    nz = len(meta["zones"])
    ext = sum(os.path.getsize(T + "extracted/" + f) for f in os.listdir(T + "extracted") if f.startswith(rid + "."))
    big[rid] = {"sec": float(d["seconds"]), "du_kb": float(d["run_folder_du_sk"]), "rss": d.get("max_rss_kb"), "zones": nz, "ext": ext,
                "ok": d["completed_successfully"], "sev": d["severe_count"]}
    print("BIG_RUN %s zones=%d seconds=%s max_rss_kb=%s du_kb=%s extracted_bytes=%d completed=%s severe=%s"
          % (rid, nz, d["seconds"], d.get("max_rss_kb"), d["run_folder_du_sk"], ext, d["completed_successfully"], d["severe_count"]))

# ---------------------------------------------------------------- re-pilot class medians (Spanish, read-only)
man = list(csv.DictReader(io.open(MZ + "run_manifest.csv", encoding="utf-8")))
cl = collections.defaultdict(lambda: {"sec": [], "du": [], "ext": [], "z": []})
for m in man:
    rid = m["run_id"]
    sd = dict(l.strip().split("=", 1) for l in open(MZ + "runs/%s/status.txt" % rid) if "=" in l)
    e = sum(os.path.getsize(MZ + "extracted/" + f) for f in os.listdir(MZ + "extracted") if f.startswith(rid + "."))
    c = cl[m["class"]]
    c["sec"].append(float(sd["seconds"]))
    c["du"].append(float(sd["run_folder_du_sk"]))
    c["ext"].append(e)
    c["z"].append(int(m["n_zones"]))
med = {k: {"sec": statistics.median(v["sec"]), "du": statistics.median(v["du"]), "ext": statistics.median(v["ext"]), "n": len(v["sec"]),
           "zmax": max(v["z"]), "sec_per_zone": statistics.median([s / z for s, z in zip(v["sec"], v["z"])])} for k, v in cl.items()}
for k, v in sorted(med.items()):
    print("PILOT_CLASS_MEDIAN %s n=%d seconds=%.1f raw_du_kb=%.0f extracted_bytes=%.0f max_zones=%d sec_per_zone=%.2f" %
          (k, v["n"], v["sec"], v["du"], v["ext"], v["zmax"], v["sec_per_zone"]))

# ---------------------------------------------------------------- campaign arithmetic (INFO)
info = json.load(io.open(R + "out/info_es_it.json"))
bigkey = {"es": "T_es_B40", "it": "T_it_B37"}
tot_cpu = 0.0
tot_ext = 0.0
largest_raw = max(b["du_kb"] for b in big.values()) * 1024
allruns = {}
for cc in ("es", "it"):
    rows = list(csv.DictReader(io.open(R + "out/campaign_runs_%s.csv" % cc, encoding="utf-8")))
    b = big[bigkey[cc]]
    sec = 0.0
    ext = 0.0
    raw_tot = 0.0
    n_scaled = 0
    for r in rows:
        nz = int(r["n_dwellings"])
        c = med[r["class"]]
        if r["class"] in ("MFH", "AB") and nz > 18:
            s = b["sec"] / b["zones"] * nz
            e = b["ext"] / b["zones"] * nz
            rw = b["du_kb"] / b["zones"] * nz
            n_scaled += 1
        else:
            s, e, rw = c["sec"], c["ext"], c["du"]
        sec += s
        ext += e
        raw_tot += rw * 1024
    cpu_h = sec / 3600.0
    print("ARITH %s runs=%d (runs with >18 zones scaled per zone from %s: %d) CPU-hours=%.2f wall-hours at 30 CPUs=%.2f extracted_total_GB=%.2f raw_if_all_kept_GB=%.1f"
          % (cc, len(rows), bigkey[cc], n_scaled, cpu_h, cpu_h / 30.0, ext / 1e9, raw_tot / 1e9))
    tot_cpu += cpu_h
    tot_ext += ext
peak = 30 * largest_raw + tot_ext
print("ARITH both countries CPU-hours=%.2f wall-hours at 30 CPUs=%.2f (ideal packing, no queue/overhead)" % (tot_cpu, tot_cpu / 30.0))
print("ARITH peak disk = 30 x largest raw folder (%.1f MB) + all extracted (%.2f GB) = %.2f GB; free now %.2f TB -> %s"
      % (largest_raw / 1e6, tot_ext / 1e9, peak / 1e9, avail / 1e12, "fits" if peak < avail else "DOES NOT FIT"))
print("ARITH_DONE")
