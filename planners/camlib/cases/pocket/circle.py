"""The round pocket as a camlib circle, cleared by Pocket in 2 mm levels from a helix."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Boundary, Component, PlanarRegion

from bench import cutting, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 8, flute=20, length=30, holder=30)
    region = PlanarRegion("pocket", (Component(Boundary.circle((30, 30), 15)),))
    pocket = Pocket("pocket", t1, region, top_z_mm=20, floor_z_mm=12, stepdown_mm=2,
                    stepover_mm=3, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=HelicalEntry(),
                    **cutting(1, rpm=16000, feed=1500, plunge=400))
    write("circle", (0, 0, 0), (60, 60, 20), [t1], {1: 16000}, [pocket], out)
