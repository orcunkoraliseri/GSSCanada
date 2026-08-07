# -*- coding: utf-8 -*-
"""FIXTURE -- NOT A WORKING SCRIPT. Do not run it; nothing imports it.

This is the shape `improvements/v4/a4_split_score.py` had when it was first written on
2026-08-06: it read the SUPERSEDED `outputs_step9/` (2026-07-31) instead of the frozen
`outputs_step9_deliverable/` (2026-08-06 00:05). Both report "28 of 56", so every count-based
and band-based check passed; the hotel channel had nevertheless inverted, 28 below the floor
becoming 28 above the ceiling, and a correct master document was "corrected" on that basis.

It is kept as a **static** fixture rather than a pointer into the live tree on purpose: a
falsifier whose fixtures are the working tree stops falsifying the moment the tree is fixed.

Two lines below reproduce the two distinct ways the wrong directory reaches a script -- as a
whole path in one string (caught by C1) and as a join component (caught by C2, which is the one
that actually happened).
"""
import os

ROOT = "."
S9 = os.path.join(ROOT, "Leg3_4-split", "Step9_docs")

# C1 shape: the superseded directory written out inside a path literal
SRC_WHOLE = "Leg3_4-split/Step9_docs/outputs_step9/step9_eui_by_channel.csv"

# C2 shape: the superseded directory assembled from pieces -- what the real script did
SRC = os.path.join(S9, "outputs_step9", "step9_eui_by_channel.csv")
