"""Roughed with the flat tool in 3 mm levels (a raster, then a waterline); finished with the ball
tool, a raster 0.5 apart for the bottom and waterlines 0.5 apart for the steep wall."""
import opencamlib as ocl
from cam import Job, levels, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (70, 70, 20))
    job.tool(1, ocl.CylCutter(10, 20), rpm=14000, feed=1800, plunge=400)
    job.clear(part, top=20, bottom=5, stepdown=3, stepover=5, region=(15, 15, 55, 55))
    job.tool(2, ocl.BallCutter(6, 15), rpm=18000, feed=1500, plunge=400)
    job.raster(part, 5, stepover=0.5, region=(15, 15, 55, 55), sampling=0.2)
    for z in levels(20, 5, 0.5):
        job.waterline(part, z + 0.001)
    job.write(out)
