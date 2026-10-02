"""Step 9k: degenerate-surface counter (reads IDF text only; no UK path anywhere)."""
import re, math

def parse_surfaces(path):
    """yield (kind, name, boundary_type, verts[list of (x,y,z)]) for BuildingSurface:Detailed and FenestrationSurface:Detailed."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r"^(BUILDINGSURFACE:DETAILED|FENESTRATIONSURFACE:DETAILED),(.*?);", txt, re.S | re.M | re.I):
        kind = m.group(1).upper()
        body = m.group(2)
        fields = []
        for ln in body.split("\n"):
            ln = ln.split("!")[0].strip()
            if ln == "" :
                if "!" in ln: pass
                continue
            fields.extend([f.strip() for f in ln.split(",")])
        # a field line like ",  !- Space Name" becomes "" after strip -> handle by raw split below
        out.append((kind, body))
    return out

def fields_of(body):
    f = []
    for ln in body.split("\n"):
        code = ln.split("!")[0]
        if code.strip() == "":
            continue
        parts = code.rstrip().rstrip(",").split(",") if code.rstrip().endswith(",") else code.split(",")
        f.append(parts[0].strip() if len(parts) == 1 else parts[0].strip())
    return f

def read_surfaces(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    res = []
    for m in re.finditer(r"^(BUILDINGSURFACE:DETAILED|FENESTRATIONSURFACE:DETAILED),(.*?);", txt, re.S | re.M | re.I):
        kind = m.group(1).upper()
        vals = []
        for ln in m.group(2).split("\n"):
            code = ln.split("!")[0].strip()
            if code == "" and "!-" not in ln:
                continue
            code = code.rstrip(",").strip()
            vals.append(code)
        # first value after "KIND," is on the first line (the name)
        if kind.startswith("BUILDING"):
            name, stype, bc = vals[0], vals[1], vals[5]
            rest = vals[10:]  # Number of Vertices at index 10 -> 11th ... see below
            # fields: 0 name,1 type,2 constr,3 zone,4 space,5 BC,6 BCobj,7 sun,8 wind,9 vf,10 nverts, 11.. coords
            coords = vals[11:]
        else:
            name, stype, bc = vals[0], vals[1], "window"
            # 0 name,1 type,2 constr,3 host,4 BCobj,5 vf,6 frame,7 mult,8 nverts, 9.. coords
            coords = vals[9:]
        nums = [float(c) for c in coords if c != ""]
        v = [tuple(nums[i:i+3]) for i in range(0, len(nums) - 2, 3)]
        res.append((kind, name, stype, bc, v))
    return res

def d(a, b):
    return math.dist(a, b)

def reduce_vertices(v, tol_dist, tol_col):
    """remove coincident (< tol_dist from the previous kept / first) then collinear (middle vertex within tol_col of the line of its neighbours) vertices; loop until stable."""
    v = list(v)
    changed = True
    while changed and len(v) >= 3:
        changed = False
        # coincident
        i = 0
        while i < len(v) and len(v) >= 3:
            j = (i + 1) % len(v)
            if d(v[i], v[j]) < tol_dist:
                del v[j if j != 0 else i]
                changed = True
            else:
                i += 1
        # collinear
        i = 0
        while i < len(v) and len(v) >= 3:
            a, b, c = v[i - 1], v[i], v[(i + 1) % len(v)]
            ac = [c[k] - a[k] for k in range(3)]
            ab = [b[k] - a[k] for k in range(3)]
            L = math.sqrt(sum(x * x for x in ac))
            if L == 0:
                dist = math.sqrt(sum(x * x for x in ab))
            else:
                cr = [ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0]]
                dist = math.sqrt(sum(x * x for x in cr)) / L
            if dist < tol_col:
                del v[i]
                changed = True
            else:
                i += 1
    return v

def degenerate(v, tol_dist, tol_col):
    return len(reduce_vertices(v, tol_dist, tol_col)) < 3
