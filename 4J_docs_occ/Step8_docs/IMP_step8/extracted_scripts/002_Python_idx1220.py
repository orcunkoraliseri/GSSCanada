\"\"\"
Component: Python Script
NickName: Python
Component Index: 1220
Instance GUID: bffbb626-16af-4a7a-9941-717a90d46e62
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