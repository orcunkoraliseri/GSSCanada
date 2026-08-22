\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4188
Instance GUID: d8e43239-2d17-4896-9bdd-f870ba104b79
Description: Provides a scripting component.

Inputs:
  - x

Outputs:
  - out
  - a
\"\"\"
"""Provides a scripting component.
    Inputs:
        x: The x script variable
        y: The y script variable
    Output:
        a: The a output variable"""

__author__ = "orcun"
__version__ = "2021.11.17"

import rhinoscriptsyntax as rs
if x == 1:
    a=1,1
elif x ==2:
    a=2,1
elif x == 3 or x == 4:
    a=2,2
elif x==5 or x ==6:
    a=3,2
else:
    a=4,2