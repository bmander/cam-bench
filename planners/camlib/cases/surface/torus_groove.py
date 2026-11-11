"""Roughed from the part's mesh by Roughing with adaptive clearing, 1 mm layers, 0.2 left; finished
with the ball tool by steep-and-shallow: Waterline contours 0.3 apart up the groove's steep sides,
a Spiral 0.3 apart about the ring's center along its bottom, from radius 13 to 17 (unbounded,
it runs out to the stock's corners and drops off the part beside them)."""
from camlib.operations import AdaptiveClearing, Roughing, steep_and_shallow

from bench import cutting, part, tool, write


def make(stl, out):
    mesh = part(stl)
    t1 = tool(1, "flat", 6, flute=15, length=25, holder=30)
    t2 = tool(2, "ball", 6, flute=15, length=35, holder=30)
    c1 = cutting(1, rpm=18000, feed=1200, plunge=300)
    c2 = cutting(2, rpm=18000, feed=1500, plunge=400)
    rough = Roughing("rough", t1, mesh, top_z_mm=20, floor_z_mm=16, stepdown_mm=1,
                     clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                     clearing=AdaptiveClearing(max_radial_engagement_mm=1.5),
                     radial_allowance_mm=0.2, bottom_allowance_mm=0.2, **c1)
    steep, shallow = steep_and_shallow("finish", t2, mesh, floor_z_mm=0, clearance_z_mm=23,
                                       top_z_mm=20, bottom_z_mm=16.1, stepdown_mm=0.3,
                                       stepover_mm=0.3, shallow="spiral", center_mm=(40, 40),
                                       inner_radius_mm=13, outer_radius_mm=17, **c2)
    write("torus-groove", (0, 0, 0), (80, 80, 20), [t1, t2], {1: 18000, 2: 18000},
          [rough, steep, shallow], out)
