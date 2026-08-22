\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6537
Instance GUID: b3fc9c16-c3b4-49da-9bc4-451319c774a7
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
__version__ = "2022.05.06"

import rhinoscriptsyntax as rs
if x > 4:
    a = 1
else:
    a = 0