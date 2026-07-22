"""
3rdJ Step 1 -- Leg-3 -- ISQ QC PDF transcription helper (Section B, QC source).

One-off transcription step: reads the manually-exported ISQ Power-BI monthly
province tables (`<year>-province-mensuelle.pdf`, tab "Donnees mensuelles,
presentation en tableaux", filter Territoire=Province) and writes a tidy raw
CSV that read_isq_qc() then consumes with the stdlib only.

This mirrors the runbook convention: a manual download is transcribed once into
0_Occupancy/external/hotel_raw/<SOURCE>/ (here: hotel_raw/ISQ_QC/) and the
Section-B reader is re-pointed at it. Keeping the parse here means the pipeline
runtime needs no PDF dependency (pymupdf is used only in this helper).

Requires: pymupdf (fitz). Run once, locally:
    py -3 -X utf8 _transcribe_isq_qc_pdfs.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "pymupdf (fitz) is required for the ISQ transcription helper.\n"
        "Install with: py -3 -m pip install pymupdf\n"
    )
    raise

SCRIPT_DIR = Path(__file__).resolve().parent
# Manually-exported ISQ province PDFs live next to the deep-research prompts.
PDF_DIR = (SCRIPT_DIR / ".." / "deepResearch_v2").resolve()
RAW_DIR = (SCRIPT_DIR / "hotel_raw" / "ISQ_QC").resolve()
RAW_CSV = RAW_DIR / "isq_qc_province_monthly.csv"

# The province PDFs the user exported (one per year). Years present today:
PDF_YEARS = list(range(2019, 2027))


def _section_tokens(text: str, header: str, stop_headers: list[str], kind: str):
    """Return the ordered numeric tokens of the single 'Province' row inside a
    dashboard section (e.g. "Taux d'occupation"). `kind` is 'pct' or 'usd'."""
    i = text.find(header)
    if i < 0:
        return []
    end = len(text)
    for sh in stop_headers:
        k = text.find(sh, i + len(header))
        if k > 0:
            end = min(end, k)
    block = text[i:end]
    p = block.find("Province")
    if p < 0:
        return []
    tail = block[p + len("Province"):]
    if kind == "pct":
        return re.findall(r"(\d+(?:\.\d+)?)\s*%", tail)
    return re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", tail)


def _months_from(tokens: list[str]) -> list[str]:
    """Tokens are Jan..Dec (+ a trailing 'Total' when the year is complete, or a
    trailing period-average for a partial current year). 13 tokens -> 12 months;
    fewer -> leading months with the final 'Total' dropped."""
    if len(tokens) >= 13:
        return tokens[:12]
    if len(tokens) <= 1:
        return []
    return tokens[:-1]  # partial year: drop the trailing period total


def transcribe() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for year in PDF_YEARS:
        pdf = PDF_DIR / f"{year}-province-mensuelle.pdf"
        if not pdf.is_file():
            continue
        doc = fitz.open(pdf)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()

        occ = _months_from(_section_tokens(
            text, "Taux d'occupation", ["Unités louées", "Unites louees"], "pct"))
        adr = _months_from(_section_tokens(
            text, "Prix moyen", ["RMPUD"], "usd"))
        rev = _months_from(_section_tokens(
            text, "RMPUD", ["Données mensuelles", "Donnees mensuelles",
                            "Unités disponibles", "Unites disponibles"], "usd"))

        for m in range(12):
            o = occ[m] if m < len(occ) else ""
            if not o:
                continue  # only emit observed months; gaps stay absent here
            a = adr[m].replace(",", "") if m < len(adr) and adr[m] else ""
            r = rev[m].replace(",", "") if m < len(rev) and rev[m] else ""
            rows.append({
                "YEAR": year,
                "MONTH": m + 1,
                "PR": "QC",
                "occupancy_rate": f"{float(o) / 100:.3f}",
                "ADR_CAD": a,
                "RevPAR_CAD": r,
                "SOURCE": "ISQ",
                "PROVENANCE": (
                    f"ISQ Enquete frequentation, Power-BI dashboard tab "
                    f"'Donnees mensuelles' (Territoire=Province), export "
                    f"{pdf.name}"),
                "STATUS": "OK",
            })

    with open(RAW_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "YEAR", "MONTH", "PR", "occupancy_rate", "ADR_CAD", "RevPAR_CAD",
            "SOURCE", "PROVENANCE", "STATUS"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"[ISQ transcription] {len(rows)} monthly rows -> {RAW_CSV}")
    if rows:
        years = sorted({r["YEAR"] for r in rows})
        print(f"[ISQ transcription] years covered: {years}")
    return len(rows)


if __name__ == "__main__":
    transcribe()
