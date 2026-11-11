"""Both pockets cleared together in 2 mm levels: a raster over the two, which rides up over the
wall between them, then a waterline round each."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 50, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=8, stepdown=2, stepover=3, region=(10, 10, 70, 40))
    job.write(out)
