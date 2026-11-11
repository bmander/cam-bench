"""Roughed from the part's mesh by Roughing with adaptive clearing, 3 mm layers, 0.3 left on the
ridge; the foot of the ridge, where the ball cannot reach, finished by a Waterline of the flat
tool, 0.05 apart; the ridge finished by Parallel passes of the ball tool across it, along y,
0.8 apart."""
from camlib.operations import AdaptiveClearing, Parallel, Roughing, Waterline

from bench import cutting, part, tool, write


def make(stl, out):
    mesh = part(stl)
    t1 = tool(1, "flat", 10, flute=20, length=35, holder=30)
    t2 = tool(2, "ball", 6, flute=15, length=35, holder=30)
    c1 = cutting(1, rpm=14000, feed=1800, plunge=400)
    c2 = cutting(2, rpm=18000, feed=1500, plunge=400)
    ops = [Roughing("rough", t1, mesh, top_z_mm=25, floor_z_mm=10, stepdown_mm=3,
                    clearance_z_mm=28, retract_z_mm=26, feed_z_mm=25.5, clearing=AdaptiveClearing(max_radial_engagement_mm=2.5),
                    radial_allowance_mm=0.3, **c1),
           Waterline("foot", t1, mesh, floor_z_mm=0, top_z_mm=12.6, bottom_z_mm=10.05,
                     stepdown_mm=0.05, clearance_z_mm=28, **c1),
           Parallel("ridge", t2, mesh, floor_z_mm=0, stepover_mm=0.8, clearance_z_mm=28,
                    axis="y", **c2)]
    write("half-cylinder", (0, 0, 0), (80, 60, 25), [t1, t2], {1: 14000, 2: 18000}, ops, out)
