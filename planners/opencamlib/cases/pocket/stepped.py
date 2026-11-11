"""The outer pocket cleared in levels, then the inner one below it: at each level a raster over
the pocket being cut, then a waterline round its walls."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=15, stepdown=2, stepover=3, region=(15, 10, 65, 50))
    job.clear(part, top=15, bottom=10, stepdown=2, stepover=3, region=(28, 22, 52, 38))
    job.write(out)
