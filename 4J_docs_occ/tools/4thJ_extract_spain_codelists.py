#!/usr/bin/env python3
"""
4J Step 1, work item 1.2 -- transcribe Spain's activity and location code lists
from INE's own methodology, so that gate G1.4 has a reference that does not come
from a deep-research report.

Source: "Encuesta de Empleo del Tiempo 2009-2010. Metodologia", INE,
        https://www.ine.es/metodologia/t25/t25304471.pdf
        Annex I "Lista de actividades", compact list, PDF pages 66 to 71.
        Section 7 "Lugar y medio de transporte", PDF pages 124 to 126.

The compact list is used, not the long annotated one, because the compact list
is the enumeration: every code appears exactly once, in order, with its label.

Writes:
    crosswalk_source_spain_activity.csv   code, label, group1, group2, pdf_page
    crosswalk_source_spain_location.csv   code, label, pdf_page
"""

import argparse
import csv
import os
import re

import fitz

ACT_PAGES = range(65, 71)    # 0-based, so PDF pages 66-71
LOC_PAGES = range(123, 126)  # 0-based, so PDF pages 124-126

CODE_RE = re.compile(r"^(\d{1,3})$")


def page_lines(doc, idx):
    return [ln.rstrip() for ln in doc[idx].get_text().splitlines()]


def extract_pairs(doc, pages, widths):
    """A code line, then the first non-empty line after it, is its label."""
    out = []
    for p in pages:
        lines = page_lines(doc, p)
        i = 0
        while i < len(lines):
            m = CODE_RE.match(lines[i].strip())
            if m and len(m.group(1)) in widths:
                label = ""
                j = i + 1
                while j < len(lines):
                    cand = lines[j].strip()
                    if cand and not CODE_RE.match(cand):
                        label = cand
                        break
                    if CODE_RE.match(cand):
                        break
                    j += 1
                out.append((m.group(1), label, p + 1))
                i = j
            else:
                i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    doc = fitz.open(args.pdf)

    # ---- activities -------------------------------------------------------
    raw = extract_pairs(doc, ACT_PAGES, widths={1, 2, 3})
    acts, g1, g2 = [], "", ""
    for code, label, page in raw:
        if len(code) == 1:
            g1, g2 = code, ""
        elif len(code) == 2:
            g2 = code
        else:
            acts.append((code, label, g1, g2, page))

    seen = {}
    dupes = []
    for code, label, a, b, page in acts:
        if code in seen:
            dupes.append(code)
        seen[code] = label

    path_a = os.path.join(args.out, "crosswalk_source_spain_activity.csv")
    with open(path_a, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["code", "label", "group1", "group2", "pdf_page"])
        w.writerows(acts)

    # ---- locations --------------------------------------------------------
    rawl = extract_pairs(doc, LOC_PAGES, widths={2})
    locs, seenl = [], set()
    for code, label, page in rawl:
        if code in seenl:
            continue
        seenl.add(code)
        locs.append((code, label, page))

    path_l = os.path.join(args.out, "crosswalk_source_spain_location.csv")
    with open(path_l, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["code", "label", "pdf_page"])
        w.writerows(locs)

    print(f"activities transcribed : {len(acts)} codes, {len(set(c for c, *_ in acts))} distinct")
    if dupes:
        print(f"  DUPLICATE codes in the source list: {sorted(set(dupes))}")
    print(f"  major groups seen     : {sorted(set(a for _, _, a, _, _ in acts))}")
    print(f"  wrote {path_a}")
    print(f"locations transcribed  : {len(locs)} codes -> {[c for c, _, _ in locs]}")
    print(f"  wrote {path_l}")


if __name__ == "__main__":
    main()
