\"\"\"
Component: Python Script
NickName: Python
Component Index: 1314
Instance GUID: 080fbbcd-76f4-404a-a524-dd14760bfe90
Description: GhPython provides a Python script component

Inputs:
  - InList

Outputs:
  - TrueList
  - FalseList
\"\"\"
TrueList = []
FalseList = []
for id,value in enumerate(InList):
    if value == "True":
        TrueList.append(id)
    else:
        FalseList.append(id)