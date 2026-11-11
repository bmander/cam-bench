"""The slot cleared in 2 mm levels: a raster along it, then a waterline round its walls."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 40, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=14, stepdown=2, stepover=3, region=(15, 15, 65, 25))
    job.write(out)
