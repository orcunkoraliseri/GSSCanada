\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 3669
Instance GUID: b934dfc1-0675-4327-be72-2a3ba3724d62
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

__author__ = "ipg"
__version__ = "2022.01.28"

import rhinoscriptsyntax as rs
if x>=90:
    x = x-90
    print(x)
else:
    pass
    