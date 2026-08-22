\"\"\"
Component: Python Script
NickName: Python
Component Index: 1253
Instance GUID: 8e387507-53f3-46e1-af00-547eaa55b093
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