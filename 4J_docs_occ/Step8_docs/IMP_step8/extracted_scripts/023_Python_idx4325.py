\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4325
Instance GUID: 9bc98f45-7b7c-407a-a1eb-fba63f7e498b
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
__version__ = "2022.03.04"

import rhinoscriptsyntax as rs
if x == True:
    a = 0
else:
    a = 1