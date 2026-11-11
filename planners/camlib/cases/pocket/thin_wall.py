"""Both pockets as one camlib region of two components, cleared by Pocket in 2 mm levels from a
helix in each."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    region = PlanarRegion("pockets", (Component(rounded_rectangle(10, 10, 39.6, 40, 4)),
                                      Component(rounded_rectangle(40.4, 10, 70, 40, 4))))
    pocket = Pocket("pockets", t1, region, top_z_mm=20, floor_z_mm=8, stepdown_mm=2,
                    stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                    entry=HelicalEntry(), **cutting(1, rpm=18000, feed=1200, plunge=300))
    write("thin-wall", (0, 0, 0), (80, 50, 20), [t1], {1: 18000}, [pocket], out)
