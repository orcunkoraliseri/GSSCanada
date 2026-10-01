# 5J multizone Part A: TABULA dwelling-count column search (Spain rows only). Runs on Speed.
import csv, hashlib, io, sys, re, platform
import openpyxl
R = "/speed-scratch/o_iseri/5J/multizone/tabula/"
print("python", sys.version.split()[0], "openpyxl", openpyxl.__version__, platform.node())
EXP = {"tabula-values.xlsx": "7347b2cae3c4d9f5ce78221e9d5fb832",
       "tabula-calculator.xlsx": "c99ddc9ffcb6dc0ae7391273d9619e37"}
for fn, e in EXP.items():
    h = hashlib.md5(open(R + fn, "rb").read()).hexdigest()
    print("MD5 %s %s expected %s %s" % (fn, h, e, "OK" if h == e else "MISMATCH"))
raw = [r for r in csv.reader(io.open(R + "archetype_parameters_es.csv", encoding="utf-8")) if len(r) > 1]
hdr = raw[0]; rows = [dict(zip(hdr, r)) for r in raw[1:]]
print("ES csv rows", len(rows))
variants = {r["Code_BuildingVariant"]: r for r in rows}
codes = {r["Code_Building"]: r for r in rows}
KEY = re.compile(r"apart|dwell|n_app|n_dw|unit", re.I)
found = []   # (sheet, colname, code, value)
for fn in EXP:
    wb = openpyxl.load_workbook(R + fn, read_only=True, data_only=True)
    print("FILE", fn, "sheets", wb.sheetnames)
    for ws in wb.worksheets:
        head = []
        for i, row in enumerate(ws.iter_rows(min_row=1, max_row=8, values_only=True)):
            head.append(list(row))
        ncol = max((len(h) for h in head), default=0)
        matched = []
        for j in range(ncol):
            cells = [str(h[j]) for h in head if j < len(h) and h[j] is not None]
            if any(KEY.search(c) for c in cells):
                matched.append((j, " | ".join(cells)[:160]))
        print("SHEET %s cols=%d matched_headers=%d" % (ws.title, ncol, len(matched)))
        for j, t in matched:
            print("   HDR col%d: %s" % (j, t))
        # locate code column
        kc = None; kv = None
        for h in head:
            for j, c in enumerate(h):
                if c == "Code_BuildingVariant": kv = j
                if c == "Code_Building": kc = j
        if not matched or (kc is None and kv is None):
            if matched:
                print("   (matched headers but no Code_Building column in first 8 rows)")
            continue
        for row in ws.iter_rows(min_row=1, values_only=True):
            cv = row[kv] if kv is not None and kv < len(row) else None
            cb = row[kc] if kc is not None and kc < len(row) else None
            code = None
            if cv in variants: code = variants[cv]["Code_Building"]
            elif cb in codes: code = cb
            if code is None: continue
            for j, t in matched:
                v = row[j] if j < len(row) else None
                print("   VAL %s | col%d | %r" % (code, j, v))
                found.append((ws.title, t, code, v, fn))
out = R + "dwelling_count_es.csv"
with io.open(out, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["code", "class", "n_storey", "a_c_ref", "n_dwellings_tabula", "sheet", "column"])
    if not found:
        for r in rows:
            w.writerow([r["Code_Building"], r["Code_BuildingSizeClass"], r["n_Storey"], r["A_C_Ref"],
                        "NO_COLUMN_FOUND (no header with apart|dwell|n_App|n_Dw|unit in either workbook)", "", ""])
        print("RESULT: NO matching column found in either workbook")
    else:
        seen = set()
        for sh, col, code, v, fn in found:
            r = codes[code]
            w.writerow([code, r["Code_BuildingSizeClass"], r["n_Storey"], r["A_C_Ref"], v, fn + ":" + sh, col])
        covered = {c for _, _, c, _, _ in found}
        for c in codes:
            if c not in covered:
                r = codes[c]
                w.writerow([c, r["Code_BuildingSizeClass"], r["n_Storey"], r["A_C_Ref"], "ROW_NOT_FOUND_IN_SHEETS_WITH_MATCHED_COLUMN", "", ""])
        print("RESULT: %d value rows, %d/%d codes covered" % (len(found), len(covered), len(codes)))
print("WROTE", out)
