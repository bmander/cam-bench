"""The plate around the part cleared in levels, the last 0.2 into the spoilboard: at each, a
raster over the whole plate, which rides over the part, then a waterline round the part (no
lower than its bottom, where there is nothing for a waterline to meet)."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 10))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=10, bottom=-0.2, stepdown=2.5, stepover=3, floor=0)
    job.write(out)
