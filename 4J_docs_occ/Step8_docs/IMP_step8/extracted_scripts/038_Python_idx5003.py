\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 5003
Instance GUID: 49b71e4c-13d0-4d25-b263-510d45bd0aeb
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
if x >0:
    a = 1
else:
    a = 0