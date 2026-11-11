"""Roughed from the part's mesh by Roughing with adaptive clearing, 3 mm layers that face the
boss's top at 22, 0.3 left on the boss's wall; the boss's foot by a Waterline of the flat tool,
0.04 apart; the wall and as much of the fillet as the ball reaches by steep-and-shallow."""
from camlib.operations import AdaptiveClearing, Roughing, Waterline, steep_and_shallow

from bench import cutting, part, tool, write


def make(stl, out):
    mesh = part(stl)
    t1 = tool(1, "flat", 10, flute=20, length=35, holder=30)
    t2 = tool(2, "ball", 6, flute=15, length=35, holder=30)
    c1 = cutting(1, rpm=14000, feed=1800, plunge=400)
    c2 = cutting(2, rpm=18000, feed=1500, plunge=400)
    ops = [Roughing("rough", t1, mesh, top_z_mm=25, floor_z_mm=10, stepdown_mm=3,
                    clearance_z_mm=28, retract_z_mm=26, feed_z_mm=25.5,
                    clearing=AdaptiveClearing(max_radial_engagement_mm=2.5),
                    radial_allowance_mm=0.3, **c1),
           Waterline("foot", t1, mesh, floor_z_mm=0, top_z_mm=12.2, bottom_z_mm=10.04,
                     stepdown_mm=0.04, clearance_z_mm=28, **c1),
           *steep_and_shallow("finish", t2, mesh, floor_z_mm=0, clearance_z_mm=28, top_z_mm=22,
                              bottom_z_mm=10.25, stepdown_mm=0.5, stepover_mm=0.5, **c2)]
    write("small-fillet", (0, 0, 0), (60, 60, 25), [t1, t2], {1: 14000, 2: 18000}, ops, out)
