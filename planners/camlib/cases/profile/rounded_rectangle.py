"""The plate around the part cleared as a Pocket whose region is the stock, grown past its edges
by more than the tool's radius, with the part's outline as an island; entering from outside the
stock, in 2.5 mm levels down to the plate's bottom (camlib cuts no lower than its stock, so not
into the spoilboard). Its last pass round the island is the part's profile."""
from camlib.operations import Pocket, StockEdgeEntry
from camlib.planar import Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    region = PlanarRegion("around", (Component(rounded_rectangle(-4, -4, 84, 64, 0),
                                               holes=(rounded_rectangle(10, 10, 70, 50, 6),)),))
    pocket = Pocket("around", t1, region, top_z_mm=10, floor_z_mm=0, stepdown_mm=2.5,
                    stepover_mm=2.5, clearance_z_mm=13, retract_z_mm=11, feed_z_mm=10.5, entry=StockEdgeEntry(),
                    **cutting(1, rpm=18000, feed=1200, plunge=300))
    write("profile", (0, 0, 0), (80, 60, 10), [t1], {1: 18000}, [pocket], out)
