"""The pocket as a camlib region with fifteen holes, the pins, kept; cleared by Pocket with the
4 mm tool in 2 mm levels from a helix."""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Boundary, Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 4, flute=12, length=20, holder=25)
    pins = tuple(Boundary.circle((x, y), 2) for x in (20, 30, 40, 50, 60) for y in (20, 30, 40))
    region = PlanarRegion("pocket", (Component(rounded_rectangle(10, 10, 70, 50, 3), holes=pins),))
    pocket = Pocket("pocket", t1, region, top_z_mm=20, floor_z_mm=14, stepdown_mm=2,
                    stepover_mm=1.8, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                    entry=HelicalEntry(), **cutting(1, rpm=20000, feed=900, plunge=200))
    write("pin-field", (0, 0, 0), (80, 60, 20), [t1], {1: 20000}, [pocket], out)
