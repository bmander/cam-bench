"""Three Pockets: the island's top faced down to 16, its outline the region; the outer pocket
down to 10 round the island, kept as a hole; and the island's own pocket from 16 down to 12."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    c1 = cutting(1, rpm=18000, feed=1200, plunge=300)
    island = rounded_rectangle(25, 20, 55, 40, 5)
    at = dict(clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=HelicalEntry(), **c1)
    ops = [Pocket("island-top", t1, PlanarRegion("island", (Component(island),)), top_z_mm=20,
                  floor_z_mm=16, stepdown_mm=2, stepover_mm=2.5, **at),
           Pocket("outer", t1, PlanarRegion("outer", (Component(rounded_rectangle(10, 10, 70, 50, 5),
                                                                holes=(island,)),)),
                  top_z_mm=20, floor_z_mm=10, stepdown_mm=2, stepover_mm=2.5, **at),
           Pocket("inner", t1, PlanarRegion("inner", (Component(rounded_rectangle(33, 25, 47, 35, 3)),)),
                  top_z_mm=16, floor_z_mm=12, stepdown_mm=2, stepover_mm=2.5, **at)]
    write("island-with-pocket", (0, 0, 0), (80, 60, 20), [t1], {1: 18000}, ops, out)
