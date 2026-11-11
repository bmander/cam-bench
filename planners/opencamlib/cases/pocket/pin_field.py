"""The pocket cleared with the 4 mm tool in 2 mm levels: a raster over it, riding over the
pins, then a waterline round the walls and every pin."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(4, 12), rpm=20000, feed=900, plunge=200)
    job.clear(part, top=20, bottom=14, stepdown=2, stepover=2, region=(10, 10, 70, 50))
    job.write(out)
