\"\"\"
Component: Python Script
NickName: Data Rec
Component Index: 6787
Instance GUID: b00f9134-9be4-41c4-bda3-673be8b010e3
Description: GhPython provides a Python script component

Inputs:
  - x
  - enable
  - reset
  - limit

Outputs:
  - x
\"\"\"
from Grasshopper import DataTree
if reset or 'rec' not in globals(): rec = DataTree[object]()
if enable and not reset: rec.MergeTree(x)
if limit > 0:
  for branch in rec.Branches:
    if branch.Count > limit:
      branch.RemoveRange(0, branch.Count - limit)
x = rec