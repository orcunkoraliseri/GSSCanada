\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 3675
Instance GUID: f7d204b8-0c51-4aab-9ae9-bd4e3f5fa634
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
if x == 0 : 
    x = x + 0.1
    print(x)
else:
    print(x) 
    