"""The pocket cleared in 2 mm levels, each a raster and then a waterline that finishes the walls
at that level, so that no pass ever has more than a level of uncut wall beside the flutes."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (60, 50, 20))
    job.tool(1, ocl.CylCutter(6, 30), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=2, stepdown=2, stepover=3, region=(15, 15, 45, 35))
    job.write(out)
