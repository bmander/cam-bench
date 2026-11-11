"""The channel as a camlib region running out past the block's left face, cleared by Pocket in
2 mm levels, entering from outside the stock."""
from camlib.operations import Pocket, StockEdgeEntry
from camlib.planar import Boundary, Component, PlanarRegion

from bench import QUARTER, cutting, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 8, flute=20, length=30, holder=30)
    channel = Boundary(((-6, 15, 0), (35, 15, QUARTER), (40, 20, 0), (40, 40, QUARTER),
                        (35, 45, 0), (-6, 45, 0)))
    region = PlanarRegion("channel", (Component(channel),))
    pocket = Pocket("channel", t1, region, top_z_mm=20, floor_z_mm=12, stepdown_mm=2,
                    stepover_mm=3.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                    entry=StockEdgeEntry(), **cutting(1, rpm=16000, feed=1500, plunge=400))
    write("open-side", (0, 0, 0), (80, 60, 20), [t1], {1: 16000}, [pocket], out)
