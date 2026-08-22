\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6595
Instance GUID: b9f8ccfa-a92f-48f2-a865-f5502727606a
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
__version__ = "2022.02.21"

import rhinoscriptsyntax as rs
if x == 1960:
    a = 0.0005
elif x == 1980:
    a = 0.0004
else:
    a = 0.000285