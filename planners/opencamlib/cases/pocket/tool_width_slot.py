"""The slot cleared in levels by one raster line down its middle, dropped onto the part, and a
waterline round it, where the tool fits."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 40, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=15, stepdown=2.5, stepover=3, region=(20, 20, 60, 20))
    job.write(out)
