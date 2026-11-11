"""A slot as wide as the tool is cut by Trace, camlib's operation for a slot along a path: the
tool's center follows the slot's center line from (20, 20) to (60, 20), in 2.5 mm passes.
(Pocket, given the slot's outline, plans no cut: its inward offset by the tool's radius is a
line, not an area.)"""
from camlib.operations import Trace, TraceLine, TracePath

from bench import cutting, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    slot = Trace("slot", t1, (TracePath((20, 20), (TraceLine((60, 20)),)),), top_z_mm=20,
                 depth_z_mm=15, stepdown_mm=2.5, clearance_z_mm=23, retract_z_mm=21,
                 feed_z_mm=20.5, **cutting(1, rpm=18000, feed=1200, plunge=300))
    write("tool-width-slot", (0, 0, 0), (80, 40, 20), [t1], {1: 18000}, [slot], out)
