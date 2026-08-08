#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_all_figures.py -- run all eight 3J schematic generators and report the result.

Run:  py -3 writing/figures/make_all_figures.py     (from 3J_docs_occ_nTemp/,
                                                       or from writing/figures/)

Prints one line per figure: output path, file size, md5 -- for both the .pdf and
the .png. Imports each generator module directly (rather than shelling out) and
calls its main(), so a failure in any one script raises immediately with a full
traceback instead of a silently-skipped figure.
"""
import hashlib
import importlib.util
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # .../writing/figures
SI = os.path.join(HERE, "SI")

MODULES = [
    ("fig01_pipeline", HERE, "Figure_01_pipeline_4split"),
    ("fig02_roadmap", HERE, "Figure_02_three_leg_roadmap"),
    ("fig03_transformer", HERE, "Figure_03_three_head_transformer"),
    ("fig04_exclusivity", HERE, "Figure_04_exclusivity_projection"),
    ("fig05_hotel", HERE, "Figure_05_hotel_sidetrack"),
    ("fig06_tag2dispatch", HERE, "Figure_06_tag2_dispatch"),
    ("figS01_shares", SI, "Figure_S01_occupiable_shares"),
    ("figS02_levers", SI, "Figure_S02_scenario_levers"),
]


def md5_of(path):
    h = hashlib.md5()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(mod_name, mod_dir):
    path = os.path.join(mod_dir, mod_name + ".py")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    print("make_all_figures.py -- building all eight 3J schematics\n")
    n_ok = 0
    for mod_name, mod_dir, out_base in MODULES:
        mod = load_module(mod_name, mod_dir)
        mod.main()
        base_path = os.path.join(mod_dir, out_base)
        for ext in (".pdf", ".png"):
            p = base_path + ext
            if not os.path.exists(p):
                print("  [MISSING] %s" % p)
                continue
            size = os.path.getsize(p)
            print("  %-70s %8d bytes  md5=%s" % (os.path.relpath(p, HERE), size, md5_of(p)))
        n_ok += 1
    print("\n%d / %d figures built." % (n_ok, len(MODULES)))
    return 0 if n_ok == len(MODULES) else 1


if __name__ == "__main__":
    sys.exit(main())
