"""The block around the boss cleared in 2 mm levels: a raster over all of it, riding over the
boss, then a waterline round the boss."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (60, 60, 20))
    job.tool(1, ocl.CylCutter(10, 20), rpm=14000, feed=1800, plunge=400)
    job.clear(part, top=20, bottom=12, stepdown=2, stepover=5)
    job.write(out)
