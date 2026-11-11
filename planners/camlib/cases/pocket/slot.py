"""The slot's outline (two lines and two half circles) as a camlib region, cleared by Pocket in
2 mm levels from a helix."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Component, PlanarRegion

from bench import cutting, stadium, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    region = PlanarRegion("slot", (Component(stadium(20, 60, 20, 5)),))
    pocket = Pocket("slot", t1, region, top_z_mm=20, floor_z_mm=14, stepdown_mm=2,
                    stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=HelicalEntry(),
                    **cutting(1, rpm=18000, feed=1200, plunge=300))
    write("slot", (0, 0, 0), (80, 40, 20), [t1], {1: 18000}, [pocket], out)
