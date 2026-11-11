"""Roughed with the flat tool in 3 mm levels, which face the boss's top at 22 (a raster, then a
waterline); the boss's foot finished by the flat tool's waterlines 0.04 apart; then the boss's
wall and the fillet, as far as the ball reaches, by the ball tool's waterlines 0.5 apart and a
raster 0.5 apart round it."""
import opencamlib as ocl
from cam import Job, levels, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (60, 60, 25))
    job.tool(1, ocl.CylCutter(10, 20), rpm=14000, feed=1800, plunge=400)
    job.clear(part, top=25, bottom=10, stepdown=3, stepover=5)
    for z in levels(12.2, 10, 0.04):
        job.waterline(part, z + 0.001)
    job.tool(2, ocl.BallCutter(6, 15), rpm=18000, feed=1500, plunge=400)
    for z in levels(22, 10, 0.5):
        job.waterline(part, z + 0.001)
    job.raster(part, 10, stepover=0.5, region=(12, 12, 48, 48), sampling=0.2)
    job.write(out)
