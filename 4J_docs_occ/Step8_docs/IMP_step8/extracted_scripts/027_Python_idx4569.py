\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4569
Instance GUID: 878666a2-b3fe-488a-96d0-36b267bb113b
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

__author__ = "Siser"
__version__ = "2022.03.17"

import rhinoscriptsyntax as rs
if x < 1980:
    a = 1960
elif x < 2000 and x >= 1980:
    a = 1980
else:
    a = 2000