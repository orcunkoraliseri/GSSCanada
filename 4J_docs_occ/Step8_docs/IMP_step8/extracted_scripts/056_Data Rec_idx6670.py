\"\"\"
Component: Python Script
NickName: Data Rec
Component Index: 6670
Instance GUID: 8bb60f2e-c4a4-4001-b053-0a2aef6ff67f
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