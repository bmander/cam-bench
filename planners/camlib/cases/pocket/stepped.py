"""Two Pockets, each its outline as a camlib region: the outer down to 15, then the inner from
15, the floor the first left, down to 10."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    c1 = cutting(1, rpm=18000, feed=1200, plunge=300)
    outer = PlanarRegion("outer", (Component(rounded_rectangle(15, 10, 65, 50, 5)),))
    inner = PlanarRegion("inner", (Component(rounded_rectangle(28, 22, 52, 38, 4)),))
    ops = [Pocket("outer", t1, outer, top_z_mm=20, floor_z_mm=15, stepdown_mm=2.5,
                  stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=HelicalEntry(), **c1),
           Pocket("inner", t1, inner, top_z_mm=15, floor_z_mm=10, stepdown_mm=2.5,
                  stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=HelicalEntry(), **c1)]
    write("stepped", (0, 0, 0), (80, 60, 20), [t1], {1: 18000}, ops, out)
