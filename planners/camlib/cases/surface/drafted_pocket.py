"""Roughed from the part's mesh by Roughing with adaptive clearing, 2 mm layers, 0.2 left on the
walls; the foot of each wall, where the ball cannot reach, finished by a Waterline of the flat
tool, 0.04 apart; the walls and the floor finished with the ball tool by steep-and-shallow."""
from camlib.operations import AdaptiveClearing, Roughing, Waterline, steep_and_shallow

from bench import cutting, part, tool, write


def make(stl, out):
    mesh = part(stl)
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    t2 = tool(2, "ball", 6, flute=15, length=35, holder=30)
    c1 = cutting(1, rpm=18000, feed=1200, plunge=300)
    c2 = cutting(2, rpm=18000, feed=1500, plunge=400)
    ops = [Roughing("rough", t1, mesh, top_z_mm=20, floor_z_mm=10, stepdown_mm=2,
                    clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                    clearing=AdaptiveClearing(max_radial_engagement_mm=1.5),
                    radial_allowance_mm=0.2, **c1),
           Waterline("foot", t1, mesh, floor_z_mm=0, top_z_mm=12.6, bottom_z_mm=10.04,
                     stepdown_mm=0.04, clearance_z_mm=23, **c1),
           *steep_and_shallow("finish", t2, mesh, floor_z_mm=0, clearance_z_mm=23, top_z_mm=20,
                              bottom_z_mm=10.25, stepdown_mm=0.5, stepover_mm=0.5, **c2)]
    write("drafted-pocket", (0, 0, 0), (80, 60, 20), [t1, t2], {1: 18000, 2: 18000}, ops, out)
