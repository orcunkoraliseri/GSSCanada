\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 3677
Instance GUID: 28c7ff60-4375-4281-a1bd-7c91cc2bbc7f
Description: Provides a scripting component.

Inputs:
  - x
  - y
  - z

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
if x > y:
    z = 0
    print(z)
if z < 0 :
    z = 0 
    print(z)
else:
    print(z)