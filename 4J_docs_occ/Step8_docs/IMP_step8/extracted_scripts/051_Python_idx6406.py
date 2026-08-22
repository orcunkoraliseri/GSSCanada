\"\"\"
Component: GhPython Script
NickName: Python
Component Index: 6406
Instance GUID: 2d5f9fdd-b93d-4503-af18-60c0764b61c3
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

__author__ = "orcun"
__version__ = "2022.05.06"

import rhinoscriptsyntax as rs
if x == 0:
    a = 0
else:
    a = 1