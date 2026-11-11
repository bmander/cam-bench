"""Face the block's top: one raster of the 12 mm tool, dropped onto the part, 8 mm apart."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (100, 60, 22))
    job.tool(1, ocl.CylCutter(12, 25), rpm=12000, feed=2000, plunge=500)
    job.raster(part, 20, stepover=8)
    job.write(out)
