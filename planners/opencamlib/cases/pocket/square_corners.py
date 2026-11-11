"""The pocket cleared in 2 mm levels: at each, a raster over the pocket, then a waterline round its
walls, which rounds each corner at the tool's radius."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=10, stepdown=2, stepover=3, region=(20, 15, 60, 45))
    job.write(out)
