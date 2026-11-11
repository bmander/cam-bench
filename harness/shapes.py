"""A few solids, built with Open CASCADE (the OCP bindings), from which each case's part is made
(`cases/<category>/<name>.py`). Only harness/parts.py uses this, to write a case's part as STEP and
STL; grading reads the STL alone. Needs `pip install cadquery-ocp`."""
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.BRepPrimAPI import (BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder,
                             BRepPrimAPI_MakeSphere)
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt


def _unify(shape):
    u = ShapeUpgrade_UnifySameDomain(shape, True, True, True)
    u.Build()
    return u.Shape()


def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def cylinder(cx, cy, z0, z1, r):
    """A cylinder of radius r on a vertical axis through (cx, cy), from z0 to z1."""
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(cx, cy, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()


def cylinder_along(p, d, r, length):
    """A cylinder of radius r whose axis starts at point p and runs `length` along direction d."""
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*p), gp_Dir(*d)), r, length).Shape()


def sphere(c, r):
    return BRepPrimAPI_MakeSphere(gp_Pnt(*c), r).Shape()


def union(*shapes):
    out = shapes[0]
    for s in shapes[1:]:
        out = BRepAlgoAPI_Fuse(out, s).Shape()
    return _unify(out)


def cut(a, *bs):
    for b in bs:
        a = BRepAlgoAPI_Cut(a, b).Shape()
    return _unify(a)


def common(a, b):
    return _unify(BRepAlgoAPI_Common(a, b).Shape())


def rounded_box(x0, y0, x1, y1, z0, z1, r):
    """A box from (x0, y0, z0) to (x1, y1, z1) whose four vertical edges are rounded to radius r
    (sharp where r is 0)."""
    if r == 0:
        return box(x0, y0, z0, x1, y1, z1)
    return union(box(x0 + r, y0, z0, x1 - r, y1, z1), box(x0, y0 + r, z0, x1, y1 - r, z1),
                 *(cylinder(x, y, z0, z1, r) for x in (x0 + r, x1 - r) for y in (y0 + r, y1 - r)))


def stadium(x0, x1, y, z0, z1, r):
    """A slot's shape: the points within r of the segment from (x0, y) to (x1, y), from z0 to z1."""
    return union(box(x0, y - r, z0, x1, y + r, z1), cylinder(x0, y, z0, z1, r),
                 cylinder(x1, y, z0, z1, r))


def edges(shape):
    ex = TopExp_Explorer(shape, TopAbs_EDGE)
    while ex.More():
        yield (getattr(TopoDS, "Edge_s", None) or TopoDS.Edge)(ex.Current())
        ex.Next()


def bounds(shape):
    b = Bnd_Box()
    BRepBndLib.Add_s(shape, b)
    b.SetGap(0.0)
    lo, hi = b.CornerMin(), b.CornerMax()
    return lo.X(), lo.Y(), lo.Z(), hi.X(), hi.Y(), hi.Z()


def fillet(shape, r, keep):
    """`shape` with every edge for which keep(xmin, ymin, zmin, xmax, ymax, zmax) holds, of its
    bounding box, rounded to radius r."""
    f = BRepFilletAPI_MakeFillet(shape)
    n = 0
    for e in edges(shape):
        if keep(*bounds(e)):
            f.Add(r, e)
            n += 1
    if not n:
        raise ValueError("no edge to round")
    return f.Shape()
