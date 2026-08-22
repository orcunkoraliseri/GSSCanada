\"\"\"
Component: Python Script
NickName: Data Rec
Component Index: 3743
Instance GUID: 4504e93a-b4d7-472f-ae10-49a054bf0754
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