"""Roughed from the part's mesh by Roughing with adaptive clearing, 3 mm layers, 0.3 left on the
bowl; finished with the ball tool by steep-and-shallow: Waterline contours 0.5 apart up the steep
wall, a Spiral 0.5 apart about the bowl's center over the rest."""
from camlib.operations import AdaptiveClearing, Roughing, steep_and_shallow

from bench import cutting, part, tool, write


def make(stl, out):
    mesh = part(stl)
    t1 = tool(1, "flat", 10, flute=20, length=35, holder=30)
    t2 = tool(2, "ball", 6, flute=15, length=35, holder=30)
    c1 = cutting(1, rpm=14000, feed=1800, plunge=400)
    c2 = cutting(2, rpm=18000, feed=1500, plunge=400)
    rough = Roughing("rough", t1, mesh, top_z_mm=20, floor_z_mm=5, stepdown_mm=3,
                     clearance_z_mm=23, retract_z_mm=21, feed_z_mm=20.5,
                     clearing=AdaptiveClearing(max_radial_engagement_mm=2.5),
                     radial_allowance_mm=0.3, bottom_allowance_mm=0.3, **c1)
    steep, shallow = steep_and_shallow("finish", t2, mesh, floor_z_mm=0, clearance_z_mm=23,
                                       top_z_mm=20, bottom_z_mm=5.25, stepdown_mm=0.5,
                                       stepover_mm=0.5, shallow="spiral", center_mm=(35, 35), **c2)
    write("bowl", (0, 0, 0), (70, 70, 20), [t1, t2], {1: 14000, 2: 18000},
          [rough, steep, shallow], out)
