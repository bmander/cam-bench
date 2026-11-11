"""The round pocket cleared in 2 mm levels: a raster over it, then a waterline round its wall."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (60, 60, 20))
    job.tool(1, ocl.CylCutter(8, 20), rpm=16000, feed=1500, plunge=400)
    job.clear(part, top=20, bottom=12, stepdown=2, stepover=4, region=(15, 15, 45, 45))
    job.write(out)
