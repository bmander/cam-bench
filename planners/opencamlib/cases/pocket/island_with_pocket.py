"""Everything cleared in 2 mm levels, which fall on the island's top, its pocket's floor and the
outer floor: a raster dropped onto the part, then a waterline round every wall at each level."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=10, stepdown=2, stepover=3, region=(10, 10, 70, 50))
    job.write(out)
