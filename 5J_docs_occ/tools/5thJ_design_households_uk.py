# -*- coding: utf-8 -*-
"""5J WP1: draw the 60 UK households (same rule as Spain and Italy).  RUN BY THE AUTHOR ONLY.

The assistant has never run this script on UK data (UKDS EUL v16 cl. 5).  It reads the pooled 4J
corpus, keeps only rows with country == "uk", and writes IDs, sizes and split labels (no diary text).

Usage (author, own account):
  5thJ_design_households_uk.py --corpus <pooled 4J_step3_corpus.jsonl> --episodes <episodes parquet> [--seed 5] [--country uk] [--out DIR]

Test on the Spain+Italy copy (allowed):  --corpus ...4J_step3_corpus_es_it.jsonl --episodes <episodes_spain.parquet> --country es --out <scratch>
Output: households_<country>.csv (same columns as households.csv).  Uses the draw and split code of
5thJ_design_tables.py (import), so a Spain test must reproduce the Spain rows of households.csv exactly.
"""
import argparse
import importlib
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
T = importlib.import_module("5thJ_design_tables")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    # 5J change (households v2): episode parquet with hid, pid and the weight column; no default path
    ap.add_argument("--episodes", required=True)
    ap.add_argument("--weight-col", default="weight_ind")
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--country", default="uk")
    ap.add_argument("--out", default=T.OUT_DEFAULT)
    a = ap.parse_args()
    sizes = T.read_household_sizes(a.corpus, a.country)
    if not sizes:
        sys.exit("no households for country %r in %s" % (a.country, a.corpus))
    w = T.read_household_weights(a.episodes, a.weight_col)   # 5J change (households v2)
    hh = T.draw_households(a.seed, a.country, sizes, w)
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, "households_%s.csv" % a.country)
    T.write_csv(path, T.HH_HEADER, T.households_rows(hh))
    print("wrote %s: %d households from %d in the corpus (weighted by %s of the lowest pid, seed %d); "
          "hids without a positive weight: %d" % (path, len(hh), len(sizes), a.weight_col, a.seed,
                                                   T.NO_WEIGHT[a.country]))


if __name__ == "__main__":
    main()
