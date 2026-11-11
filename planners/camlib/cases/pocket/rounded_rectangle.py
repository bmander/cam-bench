"""The pocket's outline drawn as a camlib region and cleared by Pocket in 2.5 mm levels, entering
on a helix; its last pass at each level follows the wall."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    region = PlanarRegion("pocket", (Component(rounded_rectangle(20, 15, 60, 45, 4)),))
    pocket = Pocket("pocket", t1, region, top_z_mm=20, floor_z_mm=10, stepdown_mm=2.5,
                    stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=HelicalEntry(),
                    **cutting(1, rpm=18000, feed=1200, plunge=300))
    write("rounded-rectangle", (0, 0, 0), (80, 60, 20), [t1], {1: 18000}, [pocket], out)
