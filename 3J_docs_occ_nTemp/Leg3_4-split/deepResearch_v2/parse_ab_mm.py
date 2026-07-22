import fitz, re, sys, os, json, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DIR = os.path.join(os.path.dirname(__file__), "hotel_raw_AB")

GEO_LABELS = [
    ("Calgary", r"Calgary\s+Occupancy(?:\s+Rate)?"),
    ("Edmonton", r"Edmonton\s+Occupancy(?:\s+Rate)?"),
    ("AlbertaResorts", r"Alberta\s+Resorts\*{0,2}\s+Occupancy(?:\s+Rate)?"),
    ("OtherAlberta", r"Other\s+Alberta\*{0,2}\s+Occupancy(?:\s+Rate)?"),
    ("AlbertaExclResorts", r"Total\s+Alberta\s*\(?excl(?:uding|\.)?\s*Resorts\)?\s+Occupancy(?:\s+Rate)?"),
]
ADR_LABEL = r"Average\s+[Dd]aily\s+[Rr]oom\s+[Rr]ate"
PCT_TOK = re.compile(r"^-?\d{1,3}(?:\.\d+)?%$")
DOL_TOK = re.compile(r"^\$?-?\d[\d,]*(?:\.\d{1,2})?$")

def norm(text):
    return re.sub(r"\s+", " ", text)

def collect_values(s, start, pattern):
    """From position `start` in string s, tokenize following words and collect
    consecutive tokens matching `pattern`. Stop at first non-matching token."""
    rest = s[start:start+400]
    toks = rest.split(" ")
    vals = []
    for t in toks:
        t = t.strip()
        if not t:
            continue
        if pattern.match(t):
            vals.append(t)
            if len(vals) >= 13:
                break
        else:
            break
    return vals

def to_num_pct(tok):
    return float(tok.replace("%", "")) / 100.0

def to_num_dollar(tok):
    return float(tok.replace("$", "").replace(",", ""))

def resolve_months(vals, kind):
    """vals: list of raw string tokens (percent or dollar).
    Returns (num_list_of_12_or_fewer, had_ytd_bool) applying the
    trailing-YTD disambiguation heuristic. Index i -> month i+1 (Jan=0)."""
    if not vals:
        return [], False
    conv = to_num_pct if kind == "pct" else to_num_dollar
    nums = [conv(v) for v in vals]
    c = len(nums)
    if c > 13:
        nums = nums[:13]
        c = 13
    if c == 13:
        return nums[:12], True
    if c <= 1:
        return nums, False
    # ambiguous: check if last ~ mean of the rest (YTD signature)
    mean_rest = sum(nums[:-1]) / (c - 1)
    last = nums[-1]
    tol = 3.0/100.0 if kind == "pct" else 8.0
    if abs(last - mean_rest) <= tol:
        return nums[:-1], True
    return nums, False

YEAR_NEAR = re.compile(r"(?:Point\s+[Cc]hange|Variance)\s+from\s+(20\d\d)")

def local_ref_year(s, pos, window=500):
    m = YEAR_NEAR.search(s[pos:pos+window])
    if m:
        return int(m.group(1)) + 1
    return None

def parse_pdf(path):
    doc = fitz.open(path)
    text = "".join(p.get_text() for p in doc)
    s = norm(text)
    # gather all label match spans (geo-occupancy + adr), in order of appearance
    matches = []
    for geo, pat in GEO_LABELS:
        for m in re.finditer(pat, s):
            matches.append((m.start(), m.end(), "OCC", geo))
    for m in re.finditer(ADR_LABEL, s):
        matches.append((m.start(), m.end(), "ADR", None))
    matches.sort(key=lambda x: x[0])

    results = []  # (geo, metric, values, had_ytd, raw_count, ref_year)
    current_geo = None
    doc_fallback_year = find_ref_year_global(text)
    for start, end, kind, geo in matches:
        if kind == "OCC":
            current_geo = geo
            vals = collect_values(s, end, PCT_TOK)
            months, had_ytd = resolve_months(vals, "pct")
            ry = local_ref_year(s, end) or doc_fallback_year
            results.append((geo, "occupancy_rate", months, had_ytd, len(vals), ry))
        else:  # ADR
            vals = collect_values(s, end, DOL_TOK)
            months, had_ytd = resolve_months(vals, "dollar")
            ry = local_ref_year(s, end) or doc_fallback_year
            if current_geo is not None:
                results.append((current_geo, "ADR_CAD", months, had_ytd, len(vals), ry))
            current_geo = None  # ADR consumes the context; avoid double-attach
    return results

def find_ref_year_global(text):
    """Fallback reference (data) year = majority of 'Point change/Variance from YYYY' + 1
    across the whole doc. Used only if a per-row local match isn't found."""
    yrs = [int(y) for y in re.findall(r"Point\s+[Cc]hange\s+from\s+(20\d\d)", text)]
    yrs += [int(y) for y in re.findall(r"Variance\s+from\s+(20\d\d)", text)]
    if not yrs:
        return None
    from collections import Counter
    common = Counter(yrs).most_common(1)[0][0]
    return common + 1

def main():
    files = sorted(glob.glob(os.path.join(DIR, "AB_MM_*.pdf")))
    all_rows = []
    unparsed_log = []
    for path in files:
        fn = os.path.basename(path)
        try:
            results = parse_pdf(path)
        except Exception as e:
            unparsed_log.append((fn, "EXCEPTION", str(e)))
            continue
        found_geos = set(r[0] for r in results)
        for geo, metric, months, had_ytd, raw_count, ref_year in results:
            if ref_year is None:
                unparsed_log.append((fn, f"NO_REF_YEAR_{geo}_{metric}", ""))
                continue
            if not months:
                unparsed_log.append((fn, f"NO_VALUES_{geo}_{metric}", f"raw_count={raw_count}"))
                continue
            for i, v in enumerate(months):
                month = i + 1
                all_rows.append({
                    "YEAR": ref_year, "MONTH": month, "GEO": geo, "metric": metric,
                    "value": v, "SOURCE": "ABMKTMONITOR", "PROVENANCE": fn,
                    "confident": had_ytd or (len(months) == 12),
                })
        for expected_geo, _ in GEO_LABELS:
            if expected_geo not in found_geos:
                unparsed_log.append((fn, f"MISSING_GEO_{expected_geo}", ""))

    json.dump(all_rows, open(os.path.join(os.path.dirname(__file__), "parsed_rows.json"), "w", encoding="utf-8"), indent=1)
    json.dump(unparsed_log, open(os.path.join(os.path.dirname(__file__), "unparsed_log.json"), "w", encoding="utf-8"), indent=1)
    print("total value-rows:", len(all_rows))
    print("unparsed/log entries:", len(unparsed_log))

if __name__ == "__main__":
    main()
