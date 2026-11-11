"""The block around the boss cleared as a Pocket whose region is the stock, grown past its edges,
with the boss's circle as an island; entering from outside the stock, in 2 mm levels."""
from camlib.operations import Pocket, StockEdgeEntry
from camlib.planar import Boundary, Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 10, flute=20, length=30, holder=30)
    region = PlanarRegion("around", (Component(rounded_rectangle(-6, -6, 66, 66, 0),
                                               holes=(Boundary.circle((30, 30), 12),)),))
    pocket = Pocket("around", t1, region, top_z_mm=20, floor_z_mm=12, stepdown_mm=2,
                    stepover_mm=4, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5, entry=StockEdgeEntry(),
                    **cutting(1, rpm=14000, feed=1800, plunge=400))
    write("boss", (0, 0, 0), (60, 60, 20), [t1], {1: 14000}, [pocket], out)
