\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5017
Instance GUID: b3aa9190-7d4f-4bdc-a2e4-246ead3eadcf
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
__version__ = "2022.03.16"

import rhinoscriptsyntax as rs
if x > 0:
    a = x
else:
    a = 0