\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 1246
Instance GUID: 263a858a-a0d6-4b91-b0f1-b0ae5cd59332
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

__author__ = "jhorikawa"
__version__ = "2020.07.27"

import rhinoscriptsyntax as rs
import math

a = math.atan2(x, y)