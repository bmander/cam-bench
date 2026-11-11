"""Roughed with the flat tool in 2.5 mm levels (a raster over the pocket, then a waterline at
each), which stops short of the rounded edge; finished with the ball tool, a raster 0.5 apart over
the floor and the rounded edge, then waterlines 0.5 apart up the walls."""
import opencamlib as ocl
from cam import Job, levels, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(10, 20), rpm=14000, feed=1800, plunge=400)
    job.clear(part, top=20, bottom=10, stepdown=2.5, stepover=5, region=(20, 15, 60, 45))
    job.tool(2, ocl.BallCutter(6, 15), rpm=18000, feed=1500, plunge=400)
    job.raster(part, 10, stepover=0.5, region=(20, 15, 60, 45), sampling=0.2)
    for z in levels(20, 10, 0.5):
        job.waterline(part, z + 0.001)
    job.write(out)
