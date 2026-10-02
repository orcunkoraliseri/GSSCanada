import csv, json, os, re, sys
n, stem, rid, rc, wall, idf, run, outp = sys.argv[1:9]
out = {"task": int(n), "stem": stem, "run": rid, "rc": int(rc), "wall_s": float(wall), "idf": idf}
text = open(idf, encoding="utf-8", newline="").read()


def count(kw):
    return len(re.findall(r"^%s," % re.escape(kw), text, flags=re.M | re.I))


for k in ("PEOPLE", "ELECTRICEQUIPMENT", "OTHEREQUIPMENT", "FENESTRATIONSURFACE:DETAILED", "ZONE",
          "HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM"):
    out["n_" + k] = count(k)
errp = run + "/eplusout.err"
err = open(errp, encoding="utf-8", errors="replace").read().splitlines() if os.path.exists(errp) else []
out["completed"] = any("EnergyPlus Completed Successfully" in l for l in err)
out["severe"] = sum(1 for l in err if "** Severe" in l)
# AMENDMENT 3: keep the text of every Severe line and its continuation lines ("**   ~~~   **"), at most 60 lines
sev_text = []
for _i, _l in enumerate(err):
    if "** Severe" in _l:
        sev_text.append(_l.strip()[:220])
        for _l2 in err[_i + 1:_i + 40]:
            if "~~~" in _l2:
                sev_text.append(_l2.strip()[:220])
            else:
                break
out["severe_text"] = sev_text[:60]
out["fatal"] = sum(1 for l in err if "** Fatal" in l)
out["warnings"] = sum(1 for l in err if "** Warning" in l)
bad = [l.strip()[:200] for l in err if re.search(r"invalid|not found", l, re.I)]
out["invalid_or_not_found"] = len(bad)
out["invalid_or_not_found_first"] = bad[:3]
# AMENDMENT 3: SUMM_TABLE_ONLY=1 re-reads only the err file and eplustbl.csv of a KEPT run folder (eplusout.csv was deleted);
# every other field is carried over from the earlier JSON, so no number is lost.
TABLE_ONLY = os.environ.get("SUMM_TABLE_ONLY") == "1"
if TABLE_ONLY:
    prev = json.load(open(outp))
    for k_, v_ in prev.items():
        if k_ not in out and k_ not in ("tbl_error", "csv_error"):
            out[k_] = v_
csvp = run + "/eplusout.csv"
try:
    with open(csvp, newline="", encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        want = {"heat": "Zone Ideal Loads Zone Total Heating Energy", "cool": "Zone Ideal Loads Zone Total Cooling Energy",
                "ee": "Electric Equipment Electricity Energy", "oe": "Zone Other Equipment Electricity Energy"}
        idx = {k: [i for i, h in enumerate(head) if v in h] for k, v in want.items()}
        tot = {k: 0.0 for k in want}
        zpos = {k: [0.0] * len(idx[k]) for k in want}
        ee_hour = []
        for row in rd:
            for k in want:
                for j, i in enumerate(idx[k]):
                    v = float(row[i])
                    tot[k] += v
                    zpos[k][j] += v
            ee_hour.append(sum(float(row[i]) for i in idx["ee"]))
    out["rows"] = len(ee_hour)
    for k in want:
        out[k + "_cols"] = len(idx[k])
        out[k + "_kwh"] = (tot[k] / 3.6e6) if idx[k] else None
    out["cool_zones_positive"] = sum(1 for v in zpos["cool"] if v > 0)
    out["heat_zones_positive"] = sum(1 for v in zpos["heat"] if v > 0)
    if out["n_ELECTRICEQUIPMENT"] > 0:
        lv = 0.0
        for m in re.finditer(r"^ElectricEquipment,(.*?);", text, flags=re.M | re.I | re.S):
            fields = [x.split("!")[0].strip().rstrip(",;") for x in m.group(1).split("\n")]
            fields = [x for x in fields if x != ""]
            lv += float(fields[4])          # name, zone, schedule, method, LEVEL
        sm = re.search(r"Schedule:File,\s*\n\s*HH_[^\n]*_Appliance,[^\n]*\n[^\n]*\n\s*([^,\n]+),", text, flags=re.I)
        series = [float(x) for x in open(sm.group(1)).read().split()[1:]]
        exp = [lv * series[h % len(series)] * 3600.0 for h in range(len(ee_hour))]
        out["ee_design_total_w"] = lv
        out["ee_expected_kwh"] = sum(exp) / 3.6e6
        out["ee_hourly_max_rel_dev"] = max((abs(a - b) / b for a, b in zip(ee_hour, exp) if b > 0), default=None)
except Exception as e:
    out["csv_error"] = repr(e)
if TABLE_ONLY:
    out.pop("csv_error", None)
try:
    # Step 9i: a missing eplustbl.csv is a fault for every writer-built run (R1, D, O, DF, OF, P1, P2); it is allowed only for R0,
    # the delivered file, which has no tabular output. (Table-only re-reads follow the same rule.)
    if not os.path.exists(run + "/eplustbl.csv"):
        if rid == "R0":
            out["tbl_missing_allowed"] = "R0 = delivered file, no tabular output"
            raise FileNotFoundError("R0_ALLOWED")
        raise FileNotFoundError("eplustbl.csv missing; required for every writer-built run (only R0 may lack it)")
    rows = list(csv.reader(open(run + "/eplustbl.csv", newline="", encoding="utf-8", errors="replace")))
    out["tbl_rows"] = len(rows)
    wa = None
    # AMENDMENT 3: the table title is in column 0 (alone on its row), the row label is in column 1, "Total" value in column 2
    for i, r in enumerate(rows):
        if r and r[0] == "Window-Wall Ratio":
            for r2 in rows[i + 1:i + 12]:
                if len(r2) > 2 and r2[1].startswith("Window Opening Area"):
                    wa = float(r2[2])
                    out["tbl_wwr_row"] = r2[:3]
                    break
            break
    out["window_opening_area_m2"] = wa
    # second, independent read: Envelope Summary > Exterior Fenestration, column "Area of Multiplied Openings [m2]", row "Total or Average"
    fa = None
    for i, r in enumerate(rows):
        if r and r[0] == "Exterior Fenestration":
            # AMENDMENT 3: title row, one blank row, then the header; labels are in column 1 (column 0 is empty)
            k = i + 1
            while k < len(rows) and not rows[k]:
                k += 1
            hdr = rows[k]
            col = [j for j, h in enumerate(hdr) if h.startswith("Area of Multiplied Openings")]
            if col:
                obj = 0.0
                n = 0
                for r2 in rows[k + 1:]:
                    if not r2:
                        break
                    lab = r2[1].strip() if len(r2) > 1 else ""
                    if lab == "Total or Average":
                        fa = float(r2[col[0]])
                        out["tbl_fen_total_row"] = r2[:col[0] + 1]
                    elif lab and "Total or Average" not in lab:
                        obj += float(r2[col[0]])
                        n += 1
                out["tbl_fen_sum_objects_m2"] = obj
                out["tbl_fen_n_objects"] = n
            break
    out["fen_total_area_m2"] = fa
    if wa is None and fa is None:
        out["tbl_error"] = "neither window table found in eplustbl.csv"
except FileNotFoundError as e:
    if str(e) != "R0_ALLOWED":
        out["tbl_error"] = repr(e)
except Exception as e:
    out["tbl_error"] = repr(e)
json.dump(out, open(outp, "w"), indent=1)
print(json.dumps(out))
sys.exit(0 if ("csv_error" not in out and "tbl_error" not in out) else 3)
