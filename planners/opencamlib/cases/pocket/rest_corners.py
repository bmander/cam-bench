"""The 12 mm tool clears the pocket in 2.5 mm levels (a raster, then a waterline); the 4 mm tool
follows with a waterline at each level, which reaches into the corners and runs up and down the
slot. opencamlib keeps no model of the stock, so the small tool's work is chosen by hand: the
waterline is where the big tool could not go."""
import opencamlib as ocl
from cam import Job, levels, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (90, 60, 20))
    job.tool(1, ocl.CylCutter(12, 25), rpm=12000, feed=2000, plunge=500)
    job.clear(part, top=20, bottom=10, stepdown=2.5, stepover=6, region=(10, 10, 70, 50))
    job.tool(2, ocl.CylCutter(4, 12), rpm=20000, feed=900, plunge=200)
    for z in levels(20, 10, 2.5):
        job.waterline(part, z + 0.001)
    job.write(out)
