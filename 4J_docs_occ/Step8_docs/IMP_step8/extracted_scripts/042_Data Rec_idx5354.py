\"\"\"
Component: Python Script
NickName: Data Rec
Component Index: 5354
Instance GUID: b625e8c2-4d58-4a81-b92a-6af0cbccf99b
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