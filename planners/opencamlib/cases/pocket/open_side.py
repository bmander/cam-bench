"""The channel cleared in 2 mm levels: a raster from outside the block in along it, then a
waterline that runs along its walls and, where it opens, round the outside of the block."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(8, 20), rpm=16000, feed=1500, plunge=400)
    job.clear(part, top=20, bottom=12, stepdown=2, stepover=4, region=(-5, 15, 40, 45),
              outside=True)
    job.write(out)
