\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 2334
Instance GUID: c0e78354-8350-4534-be56-4b8e8a73ea30
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
__version__ = "2022.01.08"

import rhinoscriptsyntax as rs
if x == True:
    a = 0
else:
    a = 1