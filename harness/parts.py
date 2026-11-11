#!/usr/bin/env python3
"""Write each case's part as STEP and STL from how the case builds it.

    python3 harness/parts.py            # every case
    python3 harness/parts.py pocket/    # the cases whose ids start so

A case's part is built by `cases/<category>/<name>.py`, whose `part(s)` returns an Open CASCADE
solid made with the helpers of harness/shapes.py (`s`). The solid is written beside the case as
`<name>.step` and, meshed finely, `<name>.stl`. Both are committed: a planner reads either, and
the harness grades against the STL. Prints each part's volume, by Open CASCADE. Needs `pip install
cadquery-ocp`."""
import importlib.util
import os
import sys

from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.Interface import Interface_Static
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shapes  # noqa: E402
from suite import cases  # noqa: E402

# how near the STL is to the solid: its chords stray no more than this from a curved face
DEFLECTION = 0.002
ANGLE = 0.05  # radians


def build(case):
    spec = importlib.util.spec_from_file_location("part", case["part"] + ".py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.part(shapes)


def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def write(shape, base):
    Interface_Static.SetCVal_s("write.step.schema", "AP214")
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    if w.Write(base + ".step") != IFSelect_RetDone:
        raise OSError(f"could not write {base}.step")
    BRepMesh_IncrementalMesh(shape, DEFLECTION, False, ANGLE, True)
    stl = StlAPI_Writer()
    stl.ASCIIMode = False
    if not stl.Write(shape, base + ".stl"):
        raise OSError(f"could not write {base}.stl")


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    for c in cases(prefix):
        shape = build(c)
        write(shape, c["part"])
        stock = [b - a for a, b in zip(c["stock"]["min"], c["stock"]["max"])]
        print(f"{c['id']:40} part {volume(shape):14.6f}  stock {stock[0] * stock[1] * stock[2]:12.3f}"
              f"  stock - part {stock[0] * stock[1] * stock[2] - volume(shape):14.6f}")


if __name__ == "__main__":
    main()
