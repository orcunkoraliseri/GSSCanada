import csv, io, json, collections
IMP = "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/5J_docs_occ/Step9_docs/impl"
NEW = "C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/ES-MAD-BERRUGUETE_win_2026-10-05"
w3 = {r["stem"]: r for r in csv.DictReader(open(IMP + "/wp9k/degenerate_win3.csv")) if r["district"] == "ES-MAD-BERRUGUETE"}
it = sum(1 for r in csv.DictReader(open(IMP + "/wp9k/degenerate_win3.csv")) if r["district"] != "ES-MAD-BERRUGUETE")
w5 = {r["stem"]: r for r in csv.DictReader(open("degenerate_win5.csv"))}
ch = dict(l.rstrip("\r\n").split("\t") for l in open(NEW + "/changed_stems.txt"))
R = {r["stem"]: r for r in csv.DictReader(open("win5_check_per_stem.csv"))}
dg = {r["stem"]: r for r in csv.DictReader(open(NEW + "/degenerate_2026-10-05.csv"))}
print("deferred list file rows: ES", len(w3), "IT", it, "(the 95 in the task doc = ES + IT; Bologna is not delivered, so the Madrid deferred list is %d)" % len(w3))
rows = []
cat = collections.Counter()
for s, r in sorted(w3.items()):
    g = ch.get(s, "unchanged")
    n3 = int(r["n_degenerate"]); n5 = int(w5[s]["n_degenerate"]) if s in w5 else 0
    theirs = int(dg[s]["n_deleted"])
    if g == "degenerate":
        status = "fixed_by_deletion" if n5 == 0 else "still_degenerate_after_deletion"
    elif g == "flat_count":
        status = "rebuilt_flat_count_now_clean" if n5 == 0 else "rebuilt_flat_count_still_degenerate"
    else:
        status = "unchanged_still_degenerate" if n5 else "unchanged_but_clean(??)"
    cat[(g, status)] += 1
    rows.append([s, r["split"], r["heldout_tiny"], g, n3, n5, theirs, status, R[s]["flats_old"], R[s]["flats_new"]])
print("category counts (their group, status):")
for k, v in sorted(cat.items()): print("  ", k, v)
unch = [r for r in rows if r[3] == "unchanged"]
print("unchanged stems in the list:", len(unch), "| still degenerate", sum(1 for r in unch if r[5] > 0), "| surfaces old", sum(r[4] for r in unch), "new", sum(r[5] for r in unch))
print("their group of the 75: ", collections.Counter(r[3] for r in rows))
print("their degenerate (58) stems in my 75-list:", sum(1 for s, g in ch.items() if g == "degenerate" and s in w3), "of 58; my-list stems NOT in their degenerate group:", [r[3] for r in rows if r[3] != "degenerate"].__len__(), "= flat_count", sum(1 for r in rows if r[3]=="flat_count"), "unchanged", len(unch))
print("my 10-05 stems with >=1 degenerate:", len(w5), "surfaces", sum(int(r["n_degenerate"]) for r in w5.values()), "; of them in the 75 list:", sum(1 for s in w5 if s in w3), "; NEW stems (not in the 75):", [s for s in w5 if s not in w3])
newst = [s for s in w5 if s not in w3]
for s in newst: print("  new:", s, ch.get(s, "unchanged"), w5[s]["n_degenerate"], w5[s]["boundary_types"])
print("in degenerate-5: by split dev/val/test:", collections.Counter(w3[s]["split"] for s in w5 if s in w3))
print("smoke buildings:", {s: (ch.get(s), w3.get(s, {}).get("n_degenerate"), w5.get(s, {}).get("n_degenerate", 0)) for s in ("394922138a6b5928", "1271cddbf6bd1e8a")})
print("unchanged-and-still-degenerate list (n10-03 -> n10-05, split, heldout):")
for r in unch: print("   ", r[0], r[4], "->", r[5], r[1], "heldout" if r[2]=="1" else "")
with io.open("deferred_win5_status.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["stem", "split", "heldout_tiny_win3", "openubem_group", "n_degenerate_win3", "n_degenerate_win5", "openubem_n_deleted", "status", "flats_win3", "flats_win5"])
    w.writerows(rows)
