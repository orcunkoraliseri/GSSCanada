\"\"\"
Component: Python Script
NickName: Python
Component Index: 1571
Instance GUID: 37691f8e-6cb1-4b5a-a418-0129c48c0f51
Description: GhPython provides a Python script component

Inputs:
  - Toggle

Outputs:

\"\"\"
import Grasshopper as gh

if Toggle:
    
    # Get the Grasshopper document and objects
    ghDoc = ghenv.Component.OnPingDocument()
    ghObjects = ghDoc.Objects
    
    # Iterate the GH objects, check type and reset data recorders
    for obj in ghObjects:
        if type(obj) is gh.Kernel.Special.GH_DataRecorder:
            obj.DestroyRecordedData()
            obj.ExpireSolution(True)