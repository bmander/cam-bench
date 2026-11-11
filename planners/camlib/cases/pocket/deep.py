"""Deeper than the flutes, so cleared as two Pockets of the same region, each no deeper than the
flutes: from the top down to 10, then from 10 down to the floor at 2, in 2 mm levels. (One Pocket
the full depth camlib rejects: its depth exceeds the cutting length.)"""
from camlib.operations import HelicalEntry, Pocket
from camlib.planar import Component, PlanarRegion

from bench import cutting, rounded_rectangle, tool, write


def make(stl, out):
    t1 = tool(1, "flat", 6, flute=10, length=30, holder=30)
    c1 = cutting(1, rpm=18000, feed=1200, plunge=300)
    region = PlanarRegion("pocket", (Component(rounded_rectangle(15, 15, 45, 35, 4)),))
    ops = [Pocket("upper", t1, region, top_z_mm=20, floor_z_mm=10, stepdown_mm=2,
                  stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                  entry=HelicalEntry(), **c1),
           Pocket("lower", t1, region, top_z_mm=10, floor_z_mm=2, stepdown_mm=2,
                  stepover_mm=2.5, clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                  entry=HelicalEntry(), **c1)]
    write("deep", (0, 0, 0), (60, 50, 20), [t1], {1: 18000}, ops, out)
