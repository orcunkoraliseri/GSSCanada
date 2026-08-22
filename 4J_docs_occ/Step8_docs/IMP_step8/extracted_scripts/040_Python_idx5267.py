\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5267
Instance GUID: 81b7372c-abae-4c3c-89ba-69858f218fc5
Description: Provides a scripting component.

Inputs:
  - x
  - y

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
__version__ = "2022.03.16"

import rhinoscriptsyntax as rs
if x <1000:
    a = 1
else:
    a = 0