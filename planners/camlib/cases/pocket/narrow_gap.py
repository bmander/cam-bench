"""The pocket as a camlib region whose hole is the island, cleared by Pocket in 2 mm levels; the
gap between island and wall, narrower than the tool, splits what the tool can reach in two."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Boundary, Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    region = PlanarRegion("pocket", (Component(rounded_rectangle(10, 10, 70, 50, 5),
                                               holes=(Boundary.circle((56, 30), 10),)),))
    pocket = Pocket("pocket", t1, region, top_z_mm=20, floor_z_mm=12, stepdown_mm=2,
                    stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                    entry=HelicalEntry(), **cutting(1, rpm=18000, feed=1200, plunge=300))
    write("narrow-gap", (0, 0, 0), (80, 60, 20), [t1], {1: 18000}, [pocket], out)
