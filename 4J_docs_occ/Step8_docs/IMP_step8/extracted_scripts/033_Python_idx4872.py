\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 4872
Instance GUID: 36d0a172-7d91-492d-b735-8d4ea5cf0120
Description: Provides a scripting component.

Inputs:
  - x
  - y

Outputs:
  - out
  - Windowless
  - NoWindowless
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
    Windowless = y
else:
    NoWindowless= y