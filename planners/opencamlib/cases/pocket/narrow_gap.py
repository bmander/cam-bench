"""The pocket cleared in 2 mm levels: a raster over it, riding over the island and the gap, then
a waterline round the walls and the island, which meet where the tool cannot pass."""
import opencamlib as ocl
from cam import Job, load


def make(stl, out):
    part = load(stl)
    job = Job((0, 0, 0), (80, 60, 20))
    job.tool(1, ocl.CylCutter(6, 15), rpm=18000, feed=1200, plunge=300)
    job.clear(part, top=20, bottom=12, stepdown=2, stepover=3, region=(10, 10, 70, 50))
    job.write(out)
