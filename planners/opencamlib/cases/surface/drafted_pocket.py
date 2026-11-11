"""Roughed with the flat tool in 2 mm levels (a raster, then a waterline); the drafted walls
finished by the ball tool's waterlines 0.5 apart, and the foot of each wall, where the ball cannot
reach, by the flat tool's waterlines 0.04 apart."""
import opencamlib as ocl
from cam import Job, levels, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=10, stepdown=2, stepover=3, region=(15, 10, 65, 50))
    for z in levels(12.6, 10, 0.04):
        job.waterline(part, z + 0.001)
    job.tool(2, ocl.BallCutter(6, 15), rpm=18000, feed=1500, plunge=400)
    for z in levels(20, 10, 0.5):
        job.waterline(part, z + 0.001)
    job.write(out)
