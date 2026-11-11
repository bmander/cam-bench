"""Faced in one 2 mm pass of the 12 mm tool, zigzag, entering from outside the stock."""
from camlib.operations import Facing

from bench import cutting, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 12, flute=25, length=40, holder=35)
    face = Facing("face", t1, floor_z_mm=20, stepdown_mm=2, stepover_mm=5, clearance_z_mm=25,
                  **cutting(1, rpm=12000, feed=2000, plunge=500))
    write("block-top", (0, 0, 0), (100, 60, 22), [t1], {1: 12000}, [face], out)
