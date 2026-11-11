"""Roughed with the flat tool in 3 mm levels (a raster dropped onto the part, then a waterline at
each), which also finishes the plate; the foot of the dome, where the ball cannot reach, finished
by the flat tool's edge in waterlines 0.04 apart; the dome finished with the ball tool, a raster
0.5 apart dropped onto it."""
import opencamlib as ocl
from cam import Job, levels, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 80, 25))
    job.tool(1, ocl.CylCutter(10, 20), rpm=14000, feed=1800, plunge=400)
    job.clear(part, top=25, bottom=10, stepdown=3, stepover=5)
    for z in levels(11.2, 10, 0.04):
        job.waterline(part, z + 0.001)
    job.tool(2, ocl.BallCutter(6, 15), rpm=18000, feed=1500, plunge=400)
    job.raster(part, 10, stepover=0.5, region=(14, 14, 66, 66), sampling=0.2)
    job.write(out)
