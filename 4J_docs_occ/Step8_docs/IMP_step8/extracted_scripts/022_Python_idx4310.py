\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4310
Instance GUID: ac46cc96-5aba-465c-a636-5da22847eae7
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