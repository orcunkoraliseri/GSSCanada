"""5J EPW checker: structure, location, year, sentinels, ranges, monthly means, annual GHI.

Usage:
  5thJ_check_epw.py --registry weather_registry_5J.json --site es_valencia PATH [--site X PATH2 ...]
  5thJ_check_epw.py --registry weather_registry_5J.json --manifest manifest.csv   (columns: site,path)
  optional: --json OUT.json

--site and positional paths pair up in order.

Outcomes per file: PASS / FAIL (failing check named) / NOT_EVALUABLE (file missing or unreadable).
A SUMMARY line prints the three counts.

EXIT CODE: 0 = every file PASS; 1 = at least one FAIL; 2 = at least one NOT_EVALUABLE and no FAIL
(an unreadable file is never counted as a pass, and never silently as a fail).

read_epw / measure / rmse and the column indices (month 1, day 2, dry bulb 6, GHI 13) are copied from
4J_docs_occ/tools/4thJ_step8_weather.py (md5 6fb17cd28b5f5666771eb9599a317d3a); nothing is imported
from 4J.  Extra columns used here: year 0, hour 3, RH 8.

Location rule (decision, see the state file): the converter writes the ERA5 grid-cell centre into the
LOCATION line, not the registry station coordinates, so lat/lon are compared with a tolerance of half an
ERA5 cell (0.125 deg) and the exact offset is printed; elevation to 0.5 m; time zone exact.
"""
import argparse
import csv
import hashlib
import io
import json
import sys

C_YEAR, C_MONTH, C_DAY, C_HOUR, C_DRYBULB, C_RH, C_GHI = 0, 1, 2, 3, 6, 8, 13
LATLON_TOL = 0.125  # half an ERA5 0.25 deg cell


def read_epw(path):  # copied from 4thJ_step8_weather.py, plus raw line list
    txt = io.open(path, encoding="latin-1").read().split("\n")
    loc = txt[0].strip()
    rows = [ln.strip().split(",") for ln in txt[8:]
            if ln.strip() and len(ln.strip().split(",")) >= 16]
    return loc, rows, txt


def measure(rows):  # copied from 4thJ_step8_weather.py (heating-season stats dropped)
    day, ghi = {}, 0.0
    for f in rows:
        t = float(f[C_DRYBULB])
        if t >= 99.0:
            raise ValueError("missing dry bulb sentinel in EPW")
        day.setdefault((int(f[C_MONTH]), int(f[C_DAY])), []).append(t)
        ghi += float(f[C_GHI])
    dmean = {k: sum(v) / len(v) for k, v in day.items()}
    return {
        "n_rows": len(rows),
        "n_days": len(dmean),
        "hours_per_day": sorted(set(len(v) for v in day.values())),
        "theta_month": [sum(v for (m, _), v in dmean.items() if m == mm)
                        / sum(1 for (m, _) in dmean if m == mm)
                        for mm in range(1, 13)],
        "theta_year": sum(dmean.values()) / len(dmean),
        "ghi_year_kwh": ghi / 1000.0,
    }


def rmse(a, b):  # copied from 4thJ_step8_weather.py
    return (sum((x - y) ** 2 for x, y in zip(a, b)) / float(len(a))) ** 0.5


def md5(path):
    h = hashlib.md5()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_file(site, path, entry):
    """Return (outcome, checks[(name, ok, detail)], info)."""
    checks, info = [], {}
    try:
        loc, rows, txt = read_epw(path)
        info["md5"] = md5(path)
    except Exception as exc:  # missing/unreadable
        return "NOT_EVALUABLE", [("readable", None, repr(exc))], info

    def add(name, ok, detail=""):
        checks.append((name, bool(ok), detail))

    try:
        add("header_8_lines", len(txt) > 8 and txt[7].startswith("DATA PERIODS")
            and txt[8][:1].isdigit(), f"line8={txt[7][:12]!r}")
        add("rows_8760", len(rows) == 8760, f"rows={len(rows)}")
        days = {}
        for f in rows:
            days.setdefault((int(f[C_MONTH]), int(f[C_DAY])), []).append(int(f[C_HOUR]))
        ok_days = len(days) == 365 and all(sorted(v) == list(range(1, 25)) for v in days.values())
        add("365_days_x_24_hours", ok_days, f"days={len(days)}")

        p = loc.split(",")
        lat, lon, tz, elev = float(p[6]), float(p[7]), float(p[8]), float(p[9])
        dlat, dlon = lat - entry["latitude"], lon - entry["longitude"]
        add("location_latlon", abs(dlat) <= LATLON_TOL and abs(dlon) <= LATLON_TOL,
            f"epw={lat:.2f},{lon:.2f} registry={entry['latitude']},{entry['longitude']} "
            f"offset={dlat:+.3f},{dlon:+.3f}")
        add("location_elevation", abs(elev - entry["elevation_m"]) <= 0.5,
            f"epw={elev} registry={entry['elevation_m']}")
        add("location_timezone", tz == float(entry["local_standard_utc_offset"]),
            f"epw={tz} registry={entry['local_standard_utc_offset']}")
        year = int(entry["raw_era5_window"][:4])
        bad_year = sum(1 for f in rows if int(f[C_YEAR]) != year)
        add("year_column", bad_year == 0, f"rows_with_other_year={bad_year} expected={year}")

        sent = sum(1 for f in rows if float(f[C_DRYBULB]) >= 99.0 or float(f[C_RH]) >= 999
                   or float(f[C_GHI]) >= 9999)
        add("no_sentinels", sent == 0, f"sentinel_rows={sent}")
        t = [float(f[C_DRYBULB]) for f in rows]
        rh = [float(f[C_RH]) for f in rows]
        g = [float(f[C_GHI]) for f in rows]
        add("dry_bulb_range_-40_50", min(t) >= -40 and max(t) <= 50, f"min={min(t)} max={max(t)}")
        add("rh_range_0_100", min(rh) >= 0 and max(rh) <= 100, f"min={min(rh)} max={max(rh)}")
        night = [float(f[C_GHI]) for f in rows if int(f[C_HOUR]) in (1, 24)]
        add("ghi_nonneg_zero_at_midnight", min(g) >= 0 and all(v == 0 for v in night),
            f"min={min(g)} nonzero_midnight_rows={sum(1 for v in night if v != 0)}")
        m = measure(rows)
        info.update({"theta_month": m["theta_month"], "theta_year": m["theta_year"],
                     "ghi_year_kwh": m["ghi_year_kwh"], "lat": lat, "lon": lon})
    except Exception as exc:
        checks.append(("parse", None, repr(exc)))
        return "NOT_EVALUABLE", checks, info

    failed = [n for n, ok, _ in checks if ok is False]
    return ("FAIL" if failed else "PASS"), checks, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--registry", required=True)
    ap.add_argument("--site", action="append", default=[])
    ap.add_argument("--manifest")
    ap.add_argument("--json")
    a = ap.parse_intermixed_args()
    pairs = list(zip(a.site, a.paths))
    if len(a.site) != len(a.paths):
        print("ERROR --site count must equal path count")
        return 2
    if a.manifest:
        with open(a.manifest, newline="", encoding="utf-8") as fh:
            pairs += [(r["site"], r["path"]) for r in csv.DictReader(fh)]
    try:
        reg = {e["site"]: e for e in json.load(open(a.registry, encoding="utf-8"))["targets"]}
    except Exception as exc:
        print(f"ERROR registry unreadable: {exc!r}")
        return 2
    counts = {"PASS": 0, "FAIL": 0, "NOT_EVALUABLE": 0}
    out = {}
    for site, path in pairs:
        if site not in reg:
            outcome, checks, info = "NOT_EVALUABLE", [("site_in_registry", None, site)], {}
        else:
            outcome, checks, info = check_file(site, path, reg[site])
        for n, ok, d in checks:
            print(f"  {site} {n}: {'PASS' if ok else ('FAIL' if ok is False else 'N/A')} {d}")
        failed = [n for n, ok, _ in checks if ok is False]
        print(f"{outcome} {site} {path}" + (f" failing={failed}" if failed else ""))
        counts[outcome] += 1
        out[site] = {"path": path, "outcome": outcome,
                     "checks": [{"name": n, "ok": ok, "detail": d} for n, ok, d in checks], **info}
    print(f"SUMMARY PASS={counts['PASS']} FAIL={counts['FAIL']} NOT_EVALUABLE={counts['NOT_EVALUABLE']}")
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"), indent=1)
    if counts["FAIL"]:
        return 1
    if counts["NOT_EVALUABLE"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
