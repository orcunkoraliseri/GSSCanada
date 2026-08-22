\"\"\"
Component: Python Script
NickName: Python
Component Index: 1228
Instance GUID: c6e92c6d-b01c-46d1-834d-f66f344de036
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